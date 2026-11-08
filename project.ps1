param(
    [ValidateSet('dev', 'build', 'export', 'export:pdf', 'export:png')]
    [string]$Task = 'dev'
)

$ErrorActionPreference = 'Stop'
$slideProject = Join-Path $PSScriptRoot 'スライド/project.ps1'
& $slideProject $Task
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
    throw "Slide project failed: $Task"
}
