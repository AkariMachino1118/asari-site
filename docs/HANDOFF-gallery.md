# キャラ個別ページのサンプル画像 引き継ぎメモ（Claude Code向け）

各キャラの個別ページ `https://aiasar.com/chara/<id>/` に「ギャラリー」がある。
`img/gallery/<id>/` に画像を置いて main に push するだけで、自動でページに載る（ファイル名順）。

## 絶対に守ること

- 個別ページは**全年齢**（pixiv・Xのプロフからリンクされるトップページの一部）
- 服を着た、性的でない画像だけ。露出・胸の強調・下着・水着・透け・スカートめくれはNG
- 迷ったら載せない。成人向けの画像は `r18/` 側の別企画で扱う

## 置き方

| 項目 | 値 |
|---|---|
| 置き場所 | `img/gallery/<id>/`（id は下表） |
| ファイル名 | `01.webp`, `02.webp` …（この順に並ぶ） |
| サイズ | 長辺 1200px 以内（縦長推奨。一覧では 3:4 に切り抜いて表示、タップで全体表示） |
| 形式 | WebP、品質 80 前後、1枚 250KB 以下が目安 |
| 枚数 | 1キャラ 6〜12 枚くらい |

| キャラ | id |
|---|---|
| 真城 美羽 | `mashiro-miu` |
| 綾瀬 奈津 | `ayase-natsu` |
| 相沢 志乃 | `aizawa-shino` |
| 水嶋 ケイ | `mizushima-kei` |
| 三浦 ひとみ | `miura-hitomi` |
| 如月 紗夜 | `kisaragi-sayo` |

```python
# 変換の例（Pillow）
from PIL import Image
im = Image.open(src).convert("RGB")
im.thumbnail((1200, 1200), Image.LANCZOS)
im.save(dst, "WEBP", quality=80, method=6)
```

## 生成する場合

立ち絵用のプロンプト（`docs/HANDOFF-tachie.md`）をベースに、構図・服装・背景・表情を変えてバリエーションを出す。
ネガティブプロンプトの nsfw 系は必ず残す。生成したら本人（あかり）に選んでもらってから置く。

## 文章やpixivリンクを変えるとき

- `data/characters.json` を編集する（紹介文・プロフィール・`pixiv` に作品やまとめのURL）
- `python3 tools/build.py` で `chara/<id>/index.html` が作り直される（push 時にも自動で実行される）
- `chara/` の HTML は直接編集しない
