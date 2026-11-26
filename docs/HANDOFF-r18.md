# 成人向けサンプル（r18）引き継ぎメモ（Claude Code向け）

成人向けページ：`https://aiasar.com/r18/`（年齢確認 → キャラ一覧）、`/r18/chara/<id>/`（キャラ紹介＋成人向けサンプル）。
ページの HTML は `tools/build.py` が `data/characters.json` から自動で作る（全年齢ページと同じ紹介文・プロフィール）。

## 最重要：成人向けの画像は GitHub に入れない

- `asari-site` は**公開リポジトリ**。誰でも年齢確認なしで見られるうえ、GitHub の規約でも性的な画像は禁止
- 画像はリポジトリの**外**のフォルダで管理する（例：`E:\r18_gallery\<id>\01.png`）
- `.gitignore` に `r18/img/` を入れてあるが、そもそもリポジトリ内に置かないこと
- サーバーへは `tools/upload_r18.py` で**直接** FTPS アップロードする（自動反映の対象外になっている）

## アップロード手順

おすすめ：接続情報をこのPCに暗号化して保存しておけば、以後はパスワードの入力なしで送れる（Claude Code からも実行できる。パスワードはClaudeに見えない）。

```powershell
# 1回だけ：Windowsのダイアログにパスワードを入力（%APPDATA%\asari-site\ftp_cred.xml にDPAPIで暗号化して保存。リポジトリの外）
powershell -ExecutionPolicy Bypass -File tools\save_ftp_cred.ps1

# 以後
powershell -ExecutionPolicy Bypass -File tools\upload_r18.ps1 E:\r18_gallery              # 全キャラ
powershell -ExecutionPolicy Bypass -File tools\upload_r18.ps1 E:\r18_gallery miura-hitomi # 1人だけ
powershell -ExecutionPolicy Bypass -File tools\upload_r18.ps1 E:\r18_voice --audio        # 成人向けボイス
```

接続情報を消したいときは `%APPDATA%\asari-site\ftp_cred.xml` を削除する。

保存せずに、その都度入力する場合：

```powershell
# FTPの接続情報（GitHub Secrets と同じもの。本人に入力してもらう。ファイルに保存しない）
$env:FTP_SERVER="ik10016.mixhost.jp"
$env:FTP_USERNAME="deploy@aiasar.com"   # 実際のFTPアカウント名
$env:FTP_PASSWORD="（本人が入力）"

pip install pillow
python tools/upload_r18.py E:\r18_gallery                # 全キャラ
python tools/upload_r18.py E:\r18_gallery mashiro-miu    # 1人だけ
python tools/upload_r18.py E:\r18_gallery --sync         # ローカルから消した画像はサーバーからも消す
```

- png / jpg は長辺1200px・WebP品質80に変換して送られる
- 送ったあとに `r18/img/<id>/list.json` が更新され、ページがそれを読んで並べる（HTMLの再生成は不要）
- 並び順はファイル名順。`01.png`, `02.png` … と付ける
- 成人向けページのキャラ紹介の立ち絵（水着）は `E:\r18_gallery\top\<id>.png` に置いて同じく送る（`python tools/upload_r18.py E:\r18_gallery top`）。サーバーに無いあいだは全年齢の立ち絵が出る

| キャラ | id |
|---|---|
| 真城 美羽 | `mashiro-miu` |
| 綾瀬 奈津 | `ayase-natsu` |
| 相沢 志乃 | `aizawa-shino` |
| 水嶋 ケイ | `mizushima-kei` |
| 三浦 ひとみ | `miura-hitomi` |
| 如月 紗夜 | `kisaragi-sayo` |

## 画像のルール

- 登場人物はすべて成人として描く（幼く見える体型・顔立ち・服装・小道具は避ける）
- **性器や結合部は必ず修正（モザイク等）を入れる**。日本の法律上、無修正は公開できない
- 実在の人物に似せない
- 生成したら本人（あかり）に選んでもらってから送る

## 紹介文を成人向けページだけ変えたいとき

`data/characters.json` の各キャラに次を足せる（無ければ全年齢版と同じ文章が出る）。
- `r18_desc`：一覧ページの短い紹介
- `r18_intro`：個別ページの紹介文（段落ごとの配列）

編集して push すれば、HTML は自動で作り直される。

## 補足

- r18 以下は `robots.txt` と `r18/.htaccess`（X-Robots-Tag）で検索・画像検索に載らないようにしてある
- 年齢確認はブラウザ側の自己申告方式。画像のURLを直接知っていれば見られる点は、業界で一般的な水準と同じ
