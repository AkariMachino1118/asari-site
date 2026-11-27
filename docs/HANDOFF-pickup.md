# ランダムピックアップ 引き継ぎメモ（Claude Code向け）

ページ：`https://aiasar.com/pickup/`。pixivに投稿した作品から1枚をランダムに表示し、タップでその作品ページを開く。

## 置き方

- `img/pickup/<pixiv作品ID>.webp` に置くだけ（例：`img/pickup/149364155.webp`）。ファイル名の数字がそのままリンク先になる
- push すれば `tools/build.py` が `pickup/index.html` を作り直して、自動で反映される
- 長辺1200px以内、WebP品質80前後
- **全年齢の作品だけ**（pixivで R-18 / R-18G 指定のもの＝`xRestrict` が 0 以外は置かない）。トップから直接リンクされるページのため

## 作品の取り込み方（本人の作品なので転載ではない）

1. `https://www.pixiv.net/ajax/user/7204909/profile/all` で作品ID一覧を取る
2. `https://www.pixiv.net/ajax/illust/<ID>` で各作品の情報を取り、`body.xRestrict == 0` のものだけ残す
3. `body.urls.regular` の画像を、ヘッダー `Referer: https://www.pixiv.net/` 付きでダウンロード（Refererが無いと403）
4. WebPに変換して `img/pickup/<ID>.webp` に保存
5. 何枚載せるかは本人に確認（全部でも、選んだものだけでもよい）。アクセスは1秒に1回程度に抑える

※ pixiv の ajax は非公式。取れなくなったら、本人に作品の画像とIDをもらって手で置く。
※ 複数枚の作品は1枚目だけでよい。
