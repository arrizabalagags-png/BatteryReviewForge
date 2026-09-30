# Install standalone skills from an extracted release ZIP into a supported host.
param(
    [ValidateSet('Codex', 'KimiCode', 'DeepSeekHarness')]
    [string]$Agent = 'DeepSeekHarness',
    [switch]$Overwrite,
    [string]$TargetRoot,
    [string]$Workspace
)

$ErrorActionPreference = 'Stop'
$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceRoot = Join-Path $packageRoot 'skills'
if (-not (Test-Path -LiteralPath $sourceRoot -PathType Container)) {
    throw 'The skills folder is missing. Extract the complete release ZIP first.'
}

$skillFolders = @(Get-ChildItem -LiteralPath $sourceRoot -Directory)
if ($skillFolders.Count -eq 0) { throw 'No skill folders were found in this package.' }

foreach ($skillFolder in $skillFolders) {
    if (-not $skillFolder.Name.StartsWith('battery-') -or -not (Test-Path -LiteralPath (Join-Path $skillFolder.FullName 'SKILL.md') -PathType Leaf)) { throw "Invalid skill folder: $($skillFolder.FullName)" }
    if ($skillFolder.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Source skill is a link: $($skillFolder.FullName)" }
}

if (-not [string]::IsNullOrWhiteSpace($Workspace)) {
    if (-not [string]::IsNullOrWhiteSpace($TargetRoot)) { throw 'Choose -Workspace or -TargetRoot, not both.' }
    if ($Agent -ne 'DeepSeekHarness') { throw '-Workspace is the DeepSeek Harness desktop project installation. Choose -Agent DeepSeekHarness.' }
    if (-not (Test-Path -LiteralPath $Workspace -PathType Container)) { throw 'Open/create your research workspace first, then pass its existing folder to -Workspace.' }
    $resolvedWorkspace = (Resolve-Path -LiteralPath $Workspace).Path
    if ((Get-Item -LiteralPath $resolvedWorkspace).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Choose the real workspace folder, not a link/junction.' }
    $targetRoot = Join-Path $resolvedWorkspace '.dsh\skills'
} elseif ([string]::IsNullOrWhiteSpace($TargetRoot)) {
    if ($Agent -eq 'DeepSeekHarness') { throw 'For DeepSeek Harness desktop, pass -Workspace "your research project folder". Global DSH_HOME belongs to the CLI profile and does not prove desktop discovery. Advanced users can choose -TargetRoot explicitly.' }
    $relativeRoots = @{
        Codex = '.codex\skills'
        KimiCode = '.kimi-code\skills'
        DeepSeekHarness = '.dsh\skills'
    }
    $hostHomes = @{
        Codex = $env:CODEX_HOME
        KimiCode = $env:KIMI_CODE_HOME
        DeepSeekHarness = $env:DSH_HOME
    }
    if (-not [string]::IsNullOrWhiteSpace($hostHomes[$Agent])) {
        $targetRoot = Join-Path $hostHomes[$Agent] 'skills'
    } else {
        $targetRoot = Join-Path $env:USERPROFILE $relativeRoots[$Agent]
    }
    if ($Agent -eq 'Codex') {
        $sharedSkills = Join-Path $env:USERPROFILE '.agents\skills'
        $sharedConflicts = @(Get-ChildItem -LiteralPath $sourceRoot -Directory | Where-Object {
            Test-Path -LiteralPath (Join-Path $sharedSkills $_.Name)
        })
        if ($sharedConflicts.Count -gt 0) { throw ("Same-name skills exist: " + (($sharedConflicts | ForEach-Object { Join-Path $sharedSkills $_.Name }) -join ', ') + '. Review discovery before adding duplicates.') }
    }
} else {
    $targetRoot = $TargetRoot
}

$conflicts = @($skillFolders | Where-Object {
    Test-Path -LiteralPath (Join-Path $targetRoot $_.Name)
})
if ($conflicts.Count -gt 0 -and -not $Overwrite) {
    $names = ($conflicts | ForEach-Object { Join-Path $targetRoot $_.Name }) -join ', '
    throw "These skills already exist: $names. Review them first, then rerun with -Overwrite to update."
}

foreach ($existingSkill in $conflicts) {
    $existingPath = Join-Path $targetRoot $existingSkill.Name
    if ((Get-Item -LiteralPath $existingPath).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Existing skill is a link: $existingPath" }
}
$ancestorPath = [IO.Path]::GetFullPath($targetRoot)
while (-not [string]::IsNullOrWhiteSpace($ancestorPath)) {
    if ((Test-Path -LiteralPath $ancestorPath) -and ((Get-Item -LiteralPath $ancestorPath).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "The target passes through a link/junction: $ancestorPath. Choose a real project folder." }
    $parentPath = Split-Path -Parent $ancestorPath
    if ($parentPath -eq $ancestorPath) { break }
    $ancestorPath = $parentPath
}
New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null
$resolvedTarget = (Resolve-Path -LiteralPath $targetRoot).Path
if ((Get-Item -LiteralPath $resolvedTarget).Attributes -band [IO.FileAttributes]::ReparsePoint) {
    throw 'The target is a link/junction. Choose a real skills directory explicitly.'
}
$backupRoot = Join-Path (Split-Path -Parent $resolvedTarget) ('.brf-install-backups\' + (Get-Date -Format 'yyyyMMdd-HHmmss-ffff'))
foreach ($skillFolder in $skillFolders) {
    $destination = [IO.Path]::GetFullPath((Join-Path $resolvedTarget $skillFolder.Name))
    if ((Split-Path -Parent $destination) -ne $resolvedTarget -or -not $skillFolder.Name.StartsWith('battery-')) {
        throw 'A skill destination is outside the verified target directory.'
    }
    if (Test-Path -LiteralPath $destination) {
        if ((Get-Item -LiteralPath $destination).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Existing skill is a link. Review it manually.' }
        New-Item -ItemType Directory -Force -Path $backupRoot | Out-Null
        Move-Item -LiteralPath $destination -Destination (Join-Path $backupRoot $skillFolder.Name)
    }
    Copy-Item -LiteralPath $skillFolder.FullName -Destination $resolvedTarget -Recurse
}
Write-Host "Installed $($skillFolders.Count) VoltPeer skills in $resolvedTarget."
if (-not [string]::IsNullOrWhiteSpace($Workspace)) { Write-Host "In DeepSeek Harness desktop, open workspace $resolvedWorkspace, start a new conversation, and ask it to locate battery-review-figure and battery-figure-assemble." }
if (Test-Path -LiteralPath $backupRoot) { Write-Host "Previous skills preserved at $backupRoot. Do not delete until the new version is checked." }
Write-Host 'Only copied is checked here. Discovery, Python dependencies and a PNG/SVG export still need checking.'
