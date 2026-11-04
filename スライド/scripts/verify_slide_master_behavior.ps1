param(
    [Parameter(Mandatory=$true)][string]$Source,
    [Parameter(Mandatory=$true)][string]$TestCopy,
    [Parameter(Mandatory=$true)][string]$Report
)
# Check on a test copy that page numbers follow the slide order and new slides inherit the master.
$ErrorActionPreference = 'Stop'
$sourcePath = (Resolve-Path -LiteralPath $Source).Path
$testPath = [IO.Path]::GetFullPath($TestCopy)
if ($sourcePath -eq $testPath) { throw 'Keep the source unchanged.' }
$before = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash
$app = $null; $deck = $null; $initialCount = 0
function Page-Number($slide) {
    foreach ($shape in $slide.Shapes) {
        if ($shape.Type -eq 14 -and $shape.PlaceholderFormat.Type -eq 13) { return $shape.TextFrame.TextRange.Text }
    }
    return $null
}
try {
    $app = New-Object -ComObject PowerPoint.Application
    $initialCount = $app.Presentations.Count
    $deck = $app.Presentations.Open($sourcePath, -1, 0, 0)
    $count = $deck.Slides.Count
    $original = Page-Number $deck.Slides.Item(5)
    $masterNames = @($deck.SlideMaster.Shapes | ForEach-Object { $_.Name })
    $layoutNames = @($deck.SlideMaster.CustomLayouts | ForEach-Object { $_.Name })
    $deck.Slides.Item(2).Delete()
    $afterDelete = Page-Number $deck.Slides.Item(4)
    $layout = $deck.Slides.Item(4).CustomLayout
    $added = $deck.Slides.AddSlide(5, $layout)
    $addedNumber = Page-Number $added
    $addedLayout = $added.CustomLayout.Name
    $deck.SaveAs($testPath, 24)
    $deck.Close(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($deck); $deck = $null
    $deck = $app.Presentations.Open($testPath, -1, 0, 0)
    $reopened = Page-Number $deck.Slides.Item(6)
    $unchanged = $before -eq (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash
    $passed = ($original -eq '5') -and ($afterDelete -eq '4') -and ($reopened -eq '6') -and $unchanged -and ($layoutNames.Count -eq 8)
    @{ passed = $passed; slide_count = $count; page_before_delete = $original; page_after_delete = $afterDelete;
       added_slide_layout = $addedLayout; added_slide_number = $addedNumber; page_after_reopen = $reopened;
       master_shapes = $masterNames; layouts = $layoutNames; original_unchanged = $unchanged } |
        ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $Report -Encoding utf8
    if (-not $passed) { throw "Slide master behavior check failed: $original, $afterDelete, $reopened, $unchanged" }
    Write-Output "Behavior check passed: 5 -> $afterDelete after delete, added slide on '$addedLayout' page '$addedNumber', reopened $reopened; original unchanged."
} finally {
    if ($null -ne $deck) { $deck.Close(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($deck) }
    if ($null -ne $app) { if ($initialCount -eq 0 -and $app.Presentations.Count -eq 0) { $app.Quit() }; [void][Runtime.InteropServices.Marshal]::ReleaseComObject($app) }
}
