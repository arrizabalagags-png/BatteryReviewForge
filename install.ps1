# Install standalone skills from an extracted release ZIP into a supported host.
param(
    [ValidateSet('Codex', 'KimiCode', 'DeepSeekHarness')]
    [string]$Agent = 'Codex',
    [switch]$Overwrite,
    [string]$TargetRoot
)

$ErrorActionPreference = 'Stop'
$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceRoot = Join-Path $packageRoot 'skills'
if ([string]::IsNullOrWhiteSpace($TargetRoot)) {
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
        if ($sharedConflicts.Count -gt 0) { throw 'BRF skills also exist under .agents/skills. Check the host discovery path before choosing -TargetRoot; do not install duplicates.' }
    }
} else {
    $targetRoot = $TargetRoot
}

if (-not (Test-Path -LiteralPath $sourceRoot -PathType Container)) {
    throw 'The skills folder is missing. Extract the complete release ZIP first.'
}

$skillFolders = @(Get-ChildItem -LiteralPath $sourceRoot -Directory)
if ($skillFolders.Count -eq 0) { throw 'No skill folders were found in this package.' }

$conflicts = @($skillFolders | Where-Object {
    Test-Path -LiteralPath (Join-Path $targetRoot $_.Name)
})
if ($conflicts.Count -gt 0 -and -not $Overwrite) {
    $names = ($conflicts | ForEach-Object Name) -join ', '
    throw "These skills already exist: $names. Review them first, then rerun with -Overwrite to update."
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
Write-Host "Copied $($skillFolders.Count) BatteryReviewForge skills for $Agent to $targetRoot. Start a new agent task and check that the skills appear."
if (Test-Path -LiteralPath $backupRoot) { Write-Host "Previous skills preserved at $backupRoot. Do not delete until the new version is checked." }
Write-Host 'Only copied is checked here. Discovery, Python dependencies and a PNG/SVG export still need checking.'
