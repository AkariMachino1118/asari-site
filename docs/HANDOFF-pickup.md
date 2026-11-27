# ランダムピックアップ 引き継ぎメモ（Claude Code向け）

ページ：`https://aiasar.com/r18/pickup/`（**成人向け側**。年齢確認あり）。
pixivに投稿した作品から1枚をランダムに表示し、タップでその作品ページ（`https://www.pixiv.net/artworks/<作品ID>`）を開く。
入口は `r18/` のキャラ一覧の上にある「ランダムピックアップ」。全年齢のトップからはリンクしない。

## 画像は GitHub に入れない

R-18 の作品も載せるため、他の成人向け画像と同じく**リポジトリの外**で管理し、`tools/upload_r18.py` でサーバーに直接送る。

```
E:\r18_pickup\
  pickup\
    149364155.png   ← ファイル名 = pixivの作品ID（数字だけ）
    150012345.jpg
```

```powershell
python tools/upload_r18.py E:\r18_pickup pickup          # 追加・差し替え
python tools/upload_r18.py E:\r18_pickup pickup --sync   # ローカルから消した作品はサーバーからも消す
```

- 送り先はサーバーの `r18/img/pickup/`。WebP（長辺1200px）に変換され、`list.json` が更新されるとページに反映される
- ファイル名の数字がそのままリンク先の作品IDになる。数字以外のファイル名は表示されない
- 複数枚の作品は1枚目だけでよい
- 何を載せるかは本人（あかり）に確認する

## 作品の取り込み方（本人の作品なので転載ではない）

1. `https://www.pixiv.net/ajax/user/7204909/profile/all` で作品ID一覧を取る
2. `https://www.pixiv.net/ajax/illust/<ID>` で各作品の情報（タイトル、`xRestrict`、`urls`）を取る
3. 画像を、ヘッダー `Referer: https://www.pixiv.net/` 付きでダウンロード（Refererが無いと403）
   - R-18 作品は、ログインしていないと情報や画像が取れないことがある。その場合は本人に PHPSESSID（Cookie）を一時的に入力してもらう。保存しない
4. `E:\r18_pickup\pickup\<ID>.png` などで保存して、上のコマンドで送る
5. アクセスは1秒に1回程度に抑える

※ pixiv の ajax は非公式。取れなくなったら、本人に作品の画像とIDをもらって手で置く。
※ pixiv に投稿済みの作品なので修正は入っているはずだが、無修正のものが混ざっていないか念のため確認する。
