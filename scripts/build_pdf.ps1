$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$PaperDir = Join-Path $Root "paper"
$DownloadsPdf = "C:\Users\wangz\Downloads\54.pdf"
$LocalPdf = Join-Path $PaperDir "main.pdf"
$BuildStatus = Join-Path $Root "data\build_status.json"

Push-Location $PaperDir
try {
    pdflatex -interaction=nonstopmode -halt-on-error main.tex | Out-Null
    pdflatex -interaction=nonstopmode -halt-on-error main.tex | Out-Null
    pdflatex -interaction=nonstopmode -halt-on-error main.tex | Out-Null
}
finally {
    Pop-Location
}

Copy-Item -LiteralPath $LocalPdf -Destination $DownloadsPdf -Force
Remove-Item -LiteralPath $LocalPdf -Force
$Hash = (Get-FileHash -LiteralPath $DownloadsPdf -Algorithm SHA256).Hash
$PdfInfo = pdfinfo $DownloadsPdf
$Pages = (($PdfInfo | Select-String -Pattern '^Pages:\s+(\d+)$').Matches.Groups[1].Value)

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $BuildStatus) | Out-Null
$Status = [ordered]@{
    paper = 54
    decision = "final_v3_full_scale"
    canonical_pdf = $DownloadsPdf
    pages = [int]$Pages
    sha256 = $Hash
    local_pdf_removed = -not (Test-Path -LiteralPath $LocalPdf)
    built_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz")
}
$Status | ConvertTo-Json | Set-Content -Path $BuildStatus -Encoding UTF8

Get-Item -LiteralPath $DownloadsPdf | Select-Object FullName,Length,LastWriteTime
Write-Host "Pages:" $Pages
Write-Host "SHA256:" $Hash
Write-Host "Local paper/main.pdf exists:" (Test-Path -LiteralPath $LocalPdf)
