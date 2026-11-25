# 公開の仕組み（Claude Code向け）

- `main` に push すると、GitHub Actions（`.github/workflows/deploy.yml`）が mixhost の `public_html` に FTPS で自動アップロードする
- つまり **main への push = 本番サイト https://aiasar.com/ に即反映**。試したいだけの変更は別ブランチで
- アップロード前に `python3 tools/build.py` が動き、`data/characters.json` からキャラ個別ページ `chara/<id>/` を作る
- アップロード対象外：`.github/`、`docs/`、`data/`、`tools/`、`.git*`、`README.md`
- サンプル画像の置き方は `docs/HANDOFF-gallery.md`
- 成人向け（r18）のページも build.py が作る。**成人向けの画像はリポジトリに入れず** `tools/upload_r18.py` でサーバーに直接送る（`docs/HANDOFF-r18.md`）。`r18/img/` は自動反映の対象外
- 接続情報は GitHub の Secrets（`FTP_SERVER` / `FTP_USERNAME` / `FTP_PASSWORD`）。FTPアカウントのディレクトリは `public_html`
- 手動で再実行したいときは GitHub の Actions → Deploy to mixhost → Run workflow
- トップ（`index.html`）は全年齢。pixiv・Xから直接リンクされるので、性的な画像や文言は置かない。成人向けは `r18/` のみ
- 反映されないときは cPanel の LiteSpeed Web Cache Manager で Flush All
