# Connect DVC to a Google Drive folder (one-time setup).
#
# Prerequisites:
#   1. Create a folder in Google Drive.
#   2. Open it; copy the ID from the URL:
#      https://drive.google.com/drive/folders/THIS_IS_THE_FOLDER_ID
#
# Usage (from repo root):
#   .\scripts\setup_dvc_gdrive.ps1 -FolderId "YOUR_FOLDER_ID"
#
# Then authenticate and upload:
#   dvc push
#   (A browser window opens for Google login the first time.)
#
param(
    [Parameter(Mandatory = $true, HelpMessage = "Google Drive folder ID from the URL")]
    [string] $FolderId
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $repoRoot

if (-not (Test-Path (Join-Path $repoRoot ".dvc"))) {
    Write-Error "No .dvc folder found. Run: dvc init"
}

$dvc = Get-Command dvc -ErrorAction SilentlyContinue
if (-not $dvc) {
    Write-Error "DVC not found. Run: pip install dvc dvc-gdrive"
}

# Normalize ID (strip trailing slashes / query junk if user pasted a full URL by mistake)
$FolderId = $FolderId.Trim()
if ($FolderId -match "drive\.google\.com") {
    if ($FolderId -match "/folders/([^/?]+)") {
        $FolderId = $Matches[1]
    }
    else {
        Write-Error "Could not parse folder ID from URL. Paste only the ID or the full folder URL."
    }
}

Write-Host "Configuring default DVC remote: gdrive://$FolderId"
dvc remote add -f -d gdrive_remote "gdrive://$FolderId"
dvc remote modify gdrive_remote gdrive_use_service_account false

Write-Host ""
Write-Host "Done. Next steps:"
Write-Host "  1. Track data (after CSVs exist):  dvc add data/raw/*.csv data/processed/*.csv"
Write-Host "  2. Upload to Drive:               dvc push"
Write-Host "  3. Commit pointers:               git add data/*.dvc .gitignore && git commit -m \"Track data with DVC\""
Write-Host ""
