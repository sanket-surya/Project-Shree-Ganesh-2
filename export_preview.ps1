param(
    [string]$pptxPath = "C:\Users\Asus\Desktop\AeroTwin_SIH2026_ProtonShift_FINAL.pptx",
    [string]$outDir = "C:\Users\Asus\AppData\Local\Temp\preview_slides_final"
)

try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $presentation = $ppt.Presentations.Open($pptxPath, [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
    
    if (!(Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
    $presentation.SaveAs($outDir, 18)
    $presentation.Close()
    $ppt.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($presentation) | Out-Null
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
    Write-Output "Done: $outDir"
} catch {
    Write-Output "Error: $_"
}
