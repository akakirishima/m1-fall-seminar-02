param(
    [Parameter(Mandatory=$true)][string]$Source,
    [Parameter(Mandatory=$true)][string]$TableData,
    [Parameter(Mandatory=$true)][string]$Output,
    [Parameter(Mandatory=$true)][string]$Report
)
$ErrorActionPreference = 'Stop'
$sourcePath = (Resolve-Path -LiteralPath $Source).Path
$outputPath = [IO.Path]::GetFullPath($Output)
if ($sourcePath -eq $outputPath) { throw 'Keep the source export unchanged.' }
$data = Get-Content -LiteralPath $TableData -Raw -Encoding utf8 | ConvertFrom-Json
[IO.Directory]::CreateDirectory((Split-Path -Parent $outputPath)) | Out-Null
function Color-Value([string]$css) {
    $channels = [regex]::Matches($css, '[\d.]+')
    if ($channels.Count -lt 3) { throw "Unsupported color: $css" }
    return [int]$channels[0].Value + 256 * [int]$channels[1].Value + 65536 * [int]$channels[2].Value
}
function Set-Line($line, [string]$color, [double]$width) {
    $line.Visible = -1
    $line.ForeColor.RGB = Color-Value $color
    $line.Weight = [Math]::Max(0.1, $width)
    $line.DashStyle = 1
}
$app = $null
$deck = $null
$initialCount = 0
$records = [Collections.Generic.List[object]]::new()
try {
    $app = New-Object -ComObject PowerPoint.Application
    $initialCount = $app.Presentations.Count
    $deck = $app.Presentations.Open($sourcePath, -1, 0, 0)
    $scale = $deck.PageSetup.SlideWidth / $data.canvas.width
    foreach ($page in $data.slides) {
        $slide = $deck.Slides.Item([int]$page.number)
        foreach ($spec in $page.tables) {
            $left = [double]$spec.x * $scale; $top = [double]$spec.y * $scale
            $width = [double]$spec.width * $scale; $height = [double]$spec.height * $scale
            $removed = 0
            # Remove only shapes contained in the table, including exporter text-box slack.
            for ($index = $slide.Shapes.Count; $index -ge 1; $index--) {
                $shape = $slide.Shapes.Item($index)
                $tolerance = 14 * $scale
                if ($shape.Left -ge $left - $tolerance -and $shape.Top -ge $top - $tolerance -and
                    $shape.Left + $shape.Width -le $left + $width + $tolerance -and
                    $shape.Top + $shape.Height -le $top + $height + $tolerance) {
                    $shape.Delete(); $removed++
                }
                [void][Runtime.InteropServices.Marshal]::ReleaseComObject($shape)
            }
            $native = $slide.Shapes.AddTable($spec.rows.Count, $spec.columns.Count, $left, $top, $width, $height)
            $native.Name = "NativeTable_slide$($page.number)"
            $table = $native.Table
            $table.FirstRow = 0; $table.FirstCol = 0
            $table.HorizBanding = 0; $table.VertBanding = 0
            for ($column = 1; $column -le $spec.columns.Count; $column++) {
                $table.Columns.Item($column).Width = [double]$spec.columns[$column - 1] * $scale
            }
            for ($row = 1; $row -le $spec.rows.Count; $row++) {
                for ($column = 1; $column -le $spec.columns.Count; $column++) {
                    $cellSpec = $spec.rows[$row - 1].cells[$column - 1]
                    $cell = $table.Cell($row, $column)
                    $shape = $cell.Shape
                    $shape.Fill.Solid(); $shape.Fill.ForeColor.RGB = Color-Value $cellSpec.fill
                    $frame = $shape.TextFrame
                    $frame.VerticalAnchor = 3
                    $frame.MarginTop = [double]$cellSpec.margins[0] * $scale
                    $frame.MarginRight = [double]$cellSpec.margins[1] * $scale
                    $frame.MarginBottom = [double]$cellSpec.margins[2] * $scale
                    $frame.MarginLeft = [double]$cellSpec.margins[3] * $scale
                    # Soft line breaks keep one paragraph and match HTML <br>.
                    $frame.TextRange.Text = $cellSpec.text.Replace("`n", [string][char]11)
                    $frame.TextRange.Font.Name = $cellSpec.font
                    $frame.TextRange.Font.NameFarEast = $cellSpec.font
                    $frame.TextRange.Font.Size = [double]$cellSpec.size * $scale
                    $frame.TextRange.Font.Color.RGB = Color-Value $cellSpec.color
                    $frame.TextRange.Font.Bold = $(if ($cellSpec.bold) { -1 } else { 0 })
                    $frame.TextRange.ParagraphFormat.Alignment = $(if ($cellSpec.align -eq 'left') { 1 } elseif ($cellSpec.align -eq 'right') { 3 } else { 2 })
                    $frame.TextRange.ParagraphFormat.SpaceBefore = 0
                    $frame.TextRange.ParagraphFormat.SpaceAfter = 0
                    $frame.TextRange.ParagraphFormat.Bullet.Visible = 0
                    $position = 1
                    foreach ($run in $cellSpec.runs) {
                        if ($run.text.Length -gt 0) {
                            $range = $frame.TextRange.Characters($position, $run.text.Length)
                            $range.Font.Name = $run.font; $range.Font.NameFarEast = $run.font
                            $range.Font.Size = [double]$run.size * $scale
                            $range.Font.Bold = $(if ($run.bold) { -1 } else { 0 })
                            $range.Font.Italic = $(if ($run.italic) { -1 } else { 0 })
                            $range.Font.Color.RGB = Color-Value $run.color
                            $position += $run.text.Length
                        }
                    }
                    for ($side = 1; $side -le 4; $side++) {
                        $border = $cellSpec.borders[$side - 1]
                        Set-Line $cell.Borders.Item($side) $border.color ([double]$border.width * $scale)
                    }
                    $cell.Borders.Item(5).Visible = 0; $cell.Borders.Item(6).Visible = 0
                    if ($spec.emphasisColumn -eq $column) {
                        Set-Line $cell.Borders.Item(2) 'rgb(237,125,49)' (4 * $scale)
                        Set-Line $cell.Borders.Item(4) 'rgb(237,125,49)' (4 * $scale)
                        if ($row -eq 1) { Set-Line $cell.Borders.Item(1) 'rgb(237,125,49)' (4 * $scale) }
                        if ($row -eq $spec.rows.Count) { Set-Line $cell.Borders.Item(3) 'rgb(237,125,49)' (4 * $scale) }
                    }
                }
            }
            for ($row = 1; $row -le $spec.rows.Count; $row++) {
                $table.Rows.Item($row).Height = [double]$spec.rows[$row - 1].height * $scale
            }
            $records.Add(@{ slide = $page.number; rows = $table.Rows.Count; columns = $table.Columns.Count;
                removed_shapes = $removed; native_table = ($native.HasTable -eq -1);
                expected_height = $height; actual_height = $native.Height })
        }
    }
    $deck.SaveAs($outputPath, 24)
    @{ output = $outputPath; slide_count = $deck.Slides.Count; tables = $records } |
        ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $Report -Encoding utf8
    Write-Output "Saved $($records.Count) native tables in $($deck.Slides.Count) slides."
} finally {
    if ($null -ne $deck) { $deck.Close(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($deck) }
    if ($null -ne $app) {
        if ($initialCount -eq 0 -and $app.Presentations.Count -eq 0) { $app.Quit() }
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($app)
    }
}
