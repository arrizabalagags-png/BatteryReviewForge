# Install VoltPeer Skills; existing trees are never silently overwritten.
param(
    [ValidateSet('Codex','KimiCode','DeepSeekHarness')][string]$Agent='DeepSeekHarness',
    [switch]$Overwrite, [switch]$MigrateLegacy, [switch]$CheckOnly,
    [string]$TargetRoot, [string]$Workspace
)
$ErrorActionPreference='Stop'
$packageRoot=Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceRoot=Join-Path $packageRoot 'skills'
if(-not(Test-Path -LiteralPath $sourceRoot -PathType Container)){throw 'Extract the complete VoltPeer package first.'}
$skillFolders=@(Get-ChildItem -LiteralPath $sourceRoot -Directory)
if($skillFolders.Count -eq 0){throw 'No Skill folders were found.'}
$aliases=@{}
$mapping=Join-Path $packageRoot 'docs\SKILL_MIGRATION.json'
if(-not(Test-Path -LiteralPath $mapping -PathType Leaf)){throw 'The migration map is missing. Extract the complete VoltPeer package; no installation was changed.'}
foreach($row in (Get-Content -LiteralPath $mapping -Raw|ConvertFrom-Json).aliases){$aliases[$row.canonical_id]=$row.legacy_id}
function Assert-RealAncestors([string]$Path){
    $cursor=[IO.Path]::GetFullPath($Path)
    while($cursor){
        if((Test-Path -LiteralPath $cursor) -and ((Get-Item -LiteralPath $cursor).Attributes -band [IO.FileAttributes]::ReparsePoint)){throw "A path uses a link/junction: $cursor"}
        $parent=Split-Path -Parent $cursor
        if($parent -eq $cursor){break}
        $cursor=$parent
    }
}
function Assert-Child([string]$Base,[string]$Child){
    $basePath=[IO.Path]::GetFullPath($Base).TrimEnd('\','/')
    $childPath=[IO.Path]::GetFullPath($Child)
    if((Split-Path -Parent $childPath).TrimEnd('\','/') -ne $basePath){throw 'A move/copy target is outside its verified directory.'}
}
foreach($skill in $skillFolders){
    if(-not $aliases.ContainsKey($skill.Name)){throw "Skill is missing from the migration map: $($skill.Name)"}
    if($skill.Name -notmatch '^voltpeer-[a-z0-9]+(?:-[a-z0-9]+)*$' -or -not(Test-Path -LiteralPath (Join-Path $skill.FullName 'SKILL.md') -PathType Leaf)){throw "Invalid canonical Skill: $($skill.Name)"}
    Assert-RealAncestors $skill.FullName
    if(@(Get-ChildItem -LiteralPath $skill.FullName -Recurse -Force|Where-Object{$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count){throw "Source Skill contains a link: $($skill.Name)"}
    if($aliases.ContainsKey($skill.Name) -and $aliases[$skill.Name] -notmatch '^battery-[a-z0-9]+(?:-[a-z0-9]+)*$'){throw 'Invalid migration alias.'}
}
if($Workspace){
    if($TargetRoot){throw 'Choose -Workspace or -TargetRoot, not both.'}
    if($Agent -ne 'DeepSeekHarness'){throw '-Workspace requires DeepSeekHarness.'}
    if(-not(Test-Path -LiteralPath $Workspace -PathType Container)){throw 'Choose an existing research workspace.'}
    Assert-RealAncestors $Workspace
    $resolvedWorkspace=(Resolve-Path -LiteralPath $Workspace).Path
    $TargetRoot=Join-Path $resolvedWorkspace '.dsh\skills'
}elseif(-not $TargetRoot){
    if($Agent -eq 'DeepSeekHarness'){throw 'For desktop discovery use -Workspace "your research folder"; an explicit CLI profile does not prove discovery.'}
    $hostRoot=if($Agent -eq 'Codex'){$env:CODEX_HOME}else{$env:KIMI_CODE_HOME}
    if(-not $hostRoot){$hostRoot=Join-Path $env:USERPROFILE $(if($Agent -eq 'Codex'){'.codex'}else{'.kimi-code'})}
    $TargetRoot=Join-Path $hostRoot 'skills'
}
$TargetRoot=[IO.Path]::GetFullPath($TargetRoot).TrimEnd('\','/')
Assert-RealAncestors $TargetRoot
if((Test-Path -LiteralPath $TargetRoot) -and -not(Test-Path -LiteralPath $TargetRoot -PathType Container)){throw 'The target must be a directory.'}
if($Agent -eq 'Codex'){
    $codexRoot=if($env:CODEX_HOME){Join-Path $env:CODEX_HOME 'skills'}else{Join-Path $env:USERPROFILE '.codex\skills'}
    foreach($other in @((Join-Path $env:USERPROFILE '.agents\skills'),$codexRoot)){
        if([IO.Path]::GetFullPath($other).TrimEnd('\','/') -eq $TargetRoot){continue}
        foreach($skill in $skillFolders){
            foreach($name in @($skill.Name,$aliases[$skill.Name])){
                if($name -and (Test-Path -LiteralPath (Join-Path $other $name))){throw "VoltPeer or legacy Skill exists in another discovery root: $(Join-Path $other $name). Review and migrate that root first."}
            }
        }
    }
}
$existing=@()
$legacy=@()
foreach($skill in $skillFolders){
    $destination=Join-Path $TargetRoot $skill.Name
    Assert-Child $TargetRoot $destination
    $oldName=$aliases[$skill.Name]
    $oldPath=if($oldName){Join-Path $TargetRoot $oldName}else{$null}
    if(Test-Path -LiteralPath $destination){Assert-RealAncestors $destination;$existing+=$skill.Name}
    if($oldPath -and (Test-Path -LiteralPath $oldPath)){Assert-Child $TargetRoot $oldPath;Assert-RealAncestors $oldPath;$legacy+=$oldName}
    if((Test-Path -LiteralPath $destination) -and $oldPath -and (Test-Path -LiteralPath $oldPath)){throw "Both legacy $oldName and canonical $($skill.Name) exist. Resolve the two installations before migrating; neither was changed."}
}
if($CheckOnly){
    [ordered]@{brand='VoltPeer';canonical_skills=$skillFolders.Count;legacy_found=$legacy;canonical_existing=$existing;would_require_migration=($legacy.Count -gt 0);would_require_overwrite=($existing.Count -gt 0);written=$false;host_discovery='NOT_TESTED'}|ConvertTo-Json
    return
}
if($legacy.Count -and -not $MigrateLegacy){throw "Legacy Skills detected: $($legacy -join ', '). Run -CheckOnly, review docs/NAMING_MIGRATION.md, then explicitly choose -MigrateLegacy. No duplicate Skills were installed."}
if($existing.Count -and -not $Overwrite){throw "Canonical Skills already exist: $($existing -join ', '). Review first, then explicitly choose -Overwrite; existing trees will be backed up."}
New-Item -ItemType Directory -Force -Path $TargetRoot|Out-Null
$resolvedTarget=(Resolve-Path -LiteralPath $TargetRoot).Path.TrimEnd('\','/')
Assert-RealAncestors $resolvedTarget
$stamp=(Get-Date -Format 'yyyyMMdd-HHmmss-ffff')+'-'+$PID
$stageBase=Join-Path (Split-Path -Parent $resolvedTarget) '.voltpeer-install-staging'
$stageRoot=Join-Path $stageBase $stamp
$backupBase=Join-Path (Split-Path -Parent $resolvedTarget) '.voltpeer-install-backups'
$backupRoot=Join-Path $backupBase $stamp
Assert-RealAncestors $stageRoot
Assert-RealAncestors $backupRoot
New-Item -ItemType Directory -Force -Path $stageBase|Out-Null
New-Item -ItemType Directory -Path $stageRoot|Out-Null
$installed=@()
$moved=@()
try{
    foreach($skill in $skillFolders){Copy-Item -LiteralPath $skill.FullName -Destination $stageRoot -Recurse}
    foreach($skill in $skillFolders){
        foreach($oldName in @($skill.Name,$aliases[$skill.Name])){
            if(-not $oldName){continue}
            $oldPath=Join-Path $resolvedTarget $oldName
            if(Test-Path -LiteralPath $oldPath){
                $kind=if($oldName -eq $skill.Name){'canonical'}else{'legacy'}
                $backupFolder=Join-Path $backupRoot $kind
                New-Item -ItemType Directory -Force -Path $backupFolder|Out-Null
                $saved=Join-Path $backupFolder $oldName
                Assert-Child $resolvedTarget $oldPath
                Assert-Child $backupFolder $saved
                Move-Item -LiteralPath $oldPath -Destination $saved
                $moved+=@{Original=$oldPath;Saved=$saved;Base=$backupFolder}
            }
        }
        $destination=Join-Path $resolvedTarget $skill.Name
        $staged=Join-Path $stageRoot $skill.Name
        Assert-Child $resolvedTarget $destination
        Assert-Child $stageRoot $staged
        Move-Item -LiteralPath $staged -Destination $destination
        $installed+=$destination
    }
    Remove-Item -LiteralPath $stageRoot
}catch{
    foreach($destination in $installed){Assert-Child $resolvedTarget $destination;Remove-Item -LiteralPath $destination -Recurse -Force}
    foreach($row in $moved){Assert-Child $resolvedTarget $row.Original;Assert-Child $row.Base $row.Saved;Move-Item -LiteralPath $row.Saved -Destination $row.Original}
    Assert-Child $stageBase $stageRoot
    if(Test-Path -LiteralPath $stageRoot){Remove-Item -LiteralPath $stageRoot -Recurse -Force}
    throw
}
Write-Host "Installed $($skillFolders.Count) canonical VoltPeer Skills in $resolvedTarget."
if(Test-Path -LiteralPath $backupRoot){Write-Host "Old trees and customisations are preserved outside discovery at $backupRoot. Review and merge wanted customisations manually; keep backups until checked."}
if($Workspace){Write-Host 'Open that workspace in a new desktop conversation and locate voltpeer-plot and voltpeer-assemble.'}
Write-Host 'File installation only. Host discovery, dependencies and an actual export remain to be checked.'
