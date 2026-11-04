param([string]$Source, [string]$TestCopy, [string]$Report)
$ErrorActionPreference = 'Stop'
$sourcePath = (Resolve-Path -LiteralPath $Source).Path
$testPath = [IO.Path]::GetFullPath($TestCopy)
$before = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash
$app = $null; $deck = $null; $initialCount = 0
try {
    $app = New-Object -ComObject PowerPoint.Application
    $initialCount = $app.Presentations.Count
    $deck = $app.Presentations.Open($sourcePath, -1, 0, 0)
    $tableShape = $null
    foreach ($shape in $deck.Slides.Item(11).Shapes) { if ($shape.HasTable -eq -1) { $tableShape = $shape; break } }
    if ($null -eq $tableShape) { throw 'Slide 11 has no native table.' }
    $expected = $tableShape.Table.Cell(2, 2).Shape.TextFrame.TextRange.Text + ' [edit-check]'
    $tableShape.Table.Cell(2, 2).Shape.TextFrame.TextRange.Text = $expected
    $deck.SaveAs($testPath, 24)
    $deck.Close(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($deck); $deck = $null
    $deck = $app.Presentations.Open($testPath, -1, 0, 0)
    $actual = $null
    foreach ($shape in $deck.Slides.Item(11).Shapes) { if ($shape.HasTable -eq -1) { $actual = $shape.Table.Cell(2, 2).Shape.TextFrame.TextRange.Text; break } }
    $unchanged = $before -eq (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash
    $passed = ($actual -eq $expected) -and $unchanged
    @{ passed = $passed; slide = 11; cell = @(2, 2); original_unchanged = $unchanged;
       operation = 'Edit cell in a test copy, save, reopen and compare' } | ConvertTo-Json | Set-Content -LiteralPath $Report -Encoding utf8
    if (-not $passed) { throw 'Native cell edit round trip failed.' }
    Write-Output 'Native cell edit/save/reopen passed; original unchanged.'
} finally {
    if ($null -ne $deck) { $deck.Close(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($deck) }
    if ($null -ne $app) { if ($initialCount -eq 0 -and $app.Presentations.Count -eq 0) { $app.Quit() }; [void][Runtime.InteropServices.Marshal]::ReleaseComObject($app) }
}
