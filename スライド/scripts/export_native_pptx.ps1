param([string]$Output = '')
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object Text.UTF8Encoding($false)
$OutputEncoding = [Console]::OutputEncoding
$slideRoot = Split-Path -Parent $PSScriptRoot
$projectRoot = Split-Path -Parent $slideRoot
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$work = Join-Path $projectRoot "local_data/pptx_export_$($stamp)_native_tables"
if (-not $Output) { $Output = Join-Path $slideRoot "exports/seminar-02-native-tables-$stamp.pptx" }
$node = 'C:\Users\tokei\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
$python = 'C:\Users\tokei\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$npxCli = 'C:\Program Files\nodejs\node_modules\npm\bin\npx-cli.js'
$cli = Join-Path $slideRoot 'node_modules/@slidev/cli/bin/slidev.mjs'
$session = "native-$stamp"
$devProcess = $null
[IO.Directory]::CreateDirectory($work) | Out-Null
Push-Location -LiteralPath $slideRoot
try {
    try { $null = Invoke-WebRequest 'http://localhost:3032/1' -UseBasicParsing -TimeoutSec 3 }
    catch {
        $devProcess = Start-Process -FilePath $node -ArgumentList @($cli, 'seminar.md', '--port', '3032') -WorkingDirectory $slideRoot -WindowStyle Hidden -PassThru
        $ready = $false
        for ($attempt = 0; $attempt -lt 60; $attempt++) {
            try { $null = Invoke-WebRequest 'http://localhost:3032/1' -UseBasicParsing -TimeoutSec 1; $ready = $true; break }
            catch { Start-Sleep -Milliseconds 500 }
        }
        if (-not $ready) { throw 'Web slide server did not become ready.' }
    }
    & $node $cli export seminar.md --format pptx-editable --output (Join-Path $work 'raw-export.pptx')
    if ($LASTEXITCODE -ne 0) { throw 'Slidev export failed.' }
    & $node $npxCli --yes --package '@playwright/cli' playwright-cli "-s=$session" open 'http://localhost:3032/1'
    if ($LASTEXITCODE -ne 0) { throw 'Could not open table capture session.' }
    & $node $npxCli --yes --package '@playwright/cli' playwright-cli "-s=$session" resize 1200 900
    & $node $npxCli --yes --package '@playwright/cli' playwright-cli "-s=$session" run-code --filename (Join-Path $PSScriptRoot 'capture_native_tables.js') --raw |
        Set-Content -LiteralPath (Join-Path $work 'tables.json') -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw 'Web table capture failed.' }
    & $python (Join-Path $PSScriptRoot 'finalize_seminar_pptx.py') (Join-Path $work 'raw-export.pptx') (Join-Path $work 'corrected-export.pptx') (Join-Path $work 'finalization.json')
    if ($LASTEXITCODE -ne 0) { throw 'Export correction failed.' }
    & (Join-Path $PSScriptRoot 'replace_with_native_tables.ps1') -Source (Join-Path $work 'corrected-export.pptx') -TableData (Join-Path $work 'tables.json') -Output $Output -Report (Join-Path $work 'native-tables.json')
    & $python (Join-Path $PSScriptRoot 'verify_native_tables.py') $Output (Join-Path $work 'tables.json') (Join-Path $work 'verification.json')
    if ($LASTEXITCODE -ne 0) { throw 'Native table validation failed.' }
    Write-Output "PowerPoint with native tables: $Output"
} finally {
    & $node $npxCli --yes --package '@playwright/cli' playwright-cli "-s=$session" close
    if ($null -ne $devProcess -and -not $devProcess.HasExited) { Stop-Process -Id $devProcess.Id }
    Pop-Location
}
