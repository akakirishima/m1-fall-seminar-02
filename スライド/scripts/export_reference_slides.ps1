param(
    [Parameter(Mandatory=$true)][string]$Source,
    [Parameter(Mandatory=$true)][string]$OutputDir,
    [int[]]$SlideNumbers = @(7,12,15,16,18,46,47)
)

$ErrorActionPreference = 'Stop'
$sourcePath = (Resolve-Path -LiteralPath $Source).Path
$outputPath = [IO.Path]::GetFullPath($OutputDir)
[IO.Directory]::CreateDirectory($outputPath) | Out-Null
$powerPoint = $null
$presentation = $null
$initialCount = $null
try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $initialCount = $powerPoint.Presentations.Count
    # ReadOnly=true, Untitled=false, WithWindow=false; never save the source.
    $presentation = $powerPoint.Presentations.Open($sourcePath, -1, 0, 0)
    $width = 1200
    $height = [int][Math]::Round($width * $presentation.PageSetup.SlideHeight / $presentation.PageSetup.SlideWidth)
    foreach ($number in $SlideNumbers) {
        $slide = $null
        try {
            $slide = $presentation.Slides.Item($number)
            $imagePath = Join-Path $outputPath ('slide_{0:D3}.png' -f $number)
            $slide.Export($imagePath, 'PNG', $width, $height)
            Write-Output ('Exported slide {0}' -f $number)
        } finally {
            if ($null -ne $slide) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($slide) }
        }
    }
} finally {
    if ($null -ne $presentation) {
        $presentation.Close()
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($presentation)
    }
    if ($null -ne $powerPoint) {
        if ($initialCount -eq 0 -and $powerPoint.Presentations.Count -eq 0) { $powerPoint.Quit() }
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($powerPoint)
    }
}
