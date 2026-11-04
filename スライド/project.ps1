param([ValidateSet('dev','build','export','export:pdf','export:png')][string]$Task='dev')
$ErrorActionPreference='Stop'
$node='C:\Users\tokei\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
$npm='C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js'
if (-not (Test-Path -LiteralPath $node)) { throw 'Codex Node.js 24.22 runtime was not found.' }
$root=$PSScriptRoot
$originalNodePath=$env:PATH
$env:PATH=(Split-Path -Parent $node)+';'+$originalNodePath
Push-Location -LiteralPath $root
try {
  & $node $npm run $Task
  if ($LASTEXITCODE -ne 0) { throw "Slidev task failed: $Task" }
} finally { Pop-Location; $env:PATH=$originalNodePath }
