param(
    [Parameter(Mandatory=$true)][string]$Source,
    [Parameter(Mandatory=$true)][string]$OutputDir
)
# Render every page with PowerPoint and list each slide's layout. The source is opened read-only.
$ErrorActionPreference = 'Stop'
$sourcePath = (Resolve-Path -LiteralPath $Source).Path
$outputPath = [IO.Path]::GetFullPath($OutputDir)
[IO.Directory]::CreateDirectory($outputPath) | Out-Null
$app = $null; $deck = $null; $initialCount = 0
try {
    $app = New-Object -ComObject PowerPoint.Application
    $initialCount = $app.Presentations.Count
    $deck = $app.Presentations.Open($sourcePath, -1, 0, 0)
    $records = [Collections.Generic.List[object]]::new()
    foreach ($slide in $deck.Slides) {
        $number = $slide.SlideIndex
        $slide.Export((Join-Path $outputPath ('slide-{0:d3}.png' -f $number)), 'PNG', 1200, 900)
        $records.Add(@{ slide = $number; layout = $slide.CustomLayout.Name; follow_master_shapes = $slide.DisplayMasterShapes -eq -1 })
    }
    @{ source = $sourcePath; slides = $records; master_shapes = $deck.SlideMaster.Shapes.Count; layouts = $deck.SlideMaster.CustomLayouts.Count } |
        ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $outputPath 'render.json') -Encoding utf8
    Write-Output "Rendered $($deck.Slides.Count) slides; master shapes $($deck.SlideMaster.Shapes.Count); layouts $($deck.SlideMaster.CustomLayouts.Count)."
} finally {
    if ($null -ne $deck) { $deck.Close(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($deck) }
    if ($null -ne $app) { if ($initialCount -eq 0 -and $app.Presentations.Count -eq 0) { $app.Quit() }; [void][Runtime.InteropServices.Marshal]::ReleaseComObject($app) }
}
