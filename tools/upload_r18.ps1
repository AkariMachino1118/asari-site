# 保存済みのFTP接続情報（tools\save_ftp_cred.ps1 で作成）を使って upload_r18.py を実行する
# 使い方: powershell -ExecutionPolicy Bypass -File tools\upload_r18.ps1 E:\r18_gallery [キャラid ...] [--sync]
$credPath = Join-Path $env:APPDATA "asari-site\ftp_cred.xml"
if (-not (Test-Path $credPath)) {
    Write-Host "接続情報がありません。先に tools\save_ftp_cred.ps1 を実行してください"
    exit 1
}
$cred = Import-Clixml $credPath
$env:FTP_SERVER = "ik10016.mixhost.jp"
$env:FTP_USERNAME = $cred.UserName
$env:FTP_PASSWORD = $cred.GetNetworkCredential().Password
try {
    python (Join-Path $PSScriptRoot "upload_r18.py") @args
} finally {
    Remove-Item Env:FTP_PASSWORD -ErrorAction SilentlyContinue
}
