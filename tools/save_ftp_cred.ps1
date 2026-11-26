# FTPの接続情報を、このPC・このWindowsユーザーだけが復号できる形で保存する（1回だけ実行）
# 保存先: %APPDATA%\asari-site\ftp_cred.xml（リポジトリの外。DPAPIで暗号化）
# 使い方: powershell -ExecutionPolicy Bypass -File tools\save_ftp_cred.ps1
$dir = Join-Path $env:APPDATA "asari-site"
New-Item -ItemType Directory -Force $dir | Out-Null
$cred = Get-Credential -UserName "deploy@aiasar.com" -Message "aiasar.com のFTPパスワードを入力してください"
if (-not $cred) { Write-Host "キャンセルしました"; exit 1 }
$cred | Export-Clixml (Join-Path $dir "ftp_cred.xml")
Write-Host "保存しました: $dir\ftp_cred.xml"
