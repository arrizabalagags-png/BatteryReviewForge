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
foreach ($skillFolder in $skillFolders) {
    Copy-Item -LiteralPath $skillFolder.FullName -Destination $targetRoot -Recurse -Force
}
Write-Host "Copied $($skillFolders.Count) BatteryReviewForge skills for $Agent to $targetRoot. Start a new agent task and check that the skills appear."
