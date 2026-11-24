# 立ち絵生成 引き継ぎメモ（Claude Code向け）

「あさりちゃんの部屋」（https://aiasar.com/）のトップページに載せる、キャラ紹介用の立ち絵を6人分作る。
生成はローカルの SD Forge（RTX 4070）で行う。

## 前提

- トップページは**全年齢向け**。pixiv・Xのプロフィールから直接リンクされる
- 立ち絵は**服を着た、性的でない絵**にする（露出・胸の強調・下着・透けはNG）。迷ったら控えめにする
- 登場人物は全員成人

## 仕上がりの仕様

| 項目 | 値 |
|---|---|
| 生成サイズ | 832x1216（縦長） |
| 最終サイズ | **600x800（3:4）**。上寄せで切り抜く（頭が切れないように） |
| 形式 | **WebP**、品質80前後、1枚150KB以下が目安 |
| ファイル名 | 下の表の `id` を使い `img/<id>.webp` |
| 置き場所 | リポジトリ `asari-site` の `img/` フォルダ |

| キャラ | id |
|---|---|
| 真城 美羽 | `mashiro-miu` |
| 綾瀬 奈津 | `ayase-natsu` |
| 相沢 志乃 | `aizawa-shino` |
| 水嶋 ケイ | `mizushima-kei` |
| 三浦 ひとみ | `miura-hitomi` |
| 如月 紗夜 | `kisaragi-sayo` |

推奨設定：DPM++ 2M Karras／Steps 28／CFG 6／ADetailer（顔）ON。
各キャラ4〜8枚出して、本人（あかり）に選んでもらう。

## 共通

全員の構図をそろえる（カードを並べたときに統一感が出るように）。

```
共通positive（各キャラの末尾に足す）:
cowboy shot,standing,facing viewer,looking at viewer,gentle smile,
simple background,soft pastel background,soft lighting,
fully clothed,sfw

共通negative:
(low quality),(worst quality),bad anatomy,extra fingers,missing fingers,
blurry,watermark,text,logo,cropped head,deformed,mutated hands,
nsfw,nude,nipples,cleavage,underwear,see-through,lingerie,swimsuit,
skirt lift,panties,sexually suggestive
```

## キャラ別 positive

### 真城 美羽 `mashiro-miu`
```
(masterpiece),(best quality),8k,
gyaru girl,japanese woman,
long wavy blonde hair,thick wavy hair,tareme eyes,natural makeup,
oversized pastel hoodie,denim skirt,cheerful,peace sign,
mashiro_miu,
<lora:Mashiro_Miu_v1-000002:0.9>
```

### 綾瀬 奈津 `ayase-natsu`
```
(masterpiece),(best quality),(soft realistic),ultra-detailed,8k,
japanese mature woman,elegant,
black medium bob hair,natural straight with slight inward curl,see-through bangs,
warm brown eyes,soft lips,natural makeup,warm expression,
white blouse,long flared skirt,hands clasped in front,
soft sunlight,
<lora:Ayase_Natsu_v1-000002:0.9>
```

### 相沢 志乃 `aizawa-shino`
```
(masterpiece),(best quality),(soft realistic),ultra-detailed,8k,
plump japanese woman,soft body,
dark brown medium messy hair,tareme eyes,expressionless,calm,
oversized knit sweater,long skirt,holding a mug,
<lora:Aizawa_Shino_v1-000002:0.9>
```
※ 志乃は無表情キャラなので、共通の `gentle smile` は外して `expressionless` を優先する。

### 水嶋 ケイ `mizushima-kei`
```
(masterpiece),(best quality),(soft realistic),ultra-detailed,8k,
japanese woman,mature,glamorous,
slightly tsurime eyes,long eyelashes,faint makeup,
long glossy hair,
beige trench coat,black turtleneck,hand on hip,confident smile,
```
※ LoRAなし。顔が安定しなければ seed を固定して選ぶ。

### 三浦 ひとみ `miura-hitomi`
```
(masterpiece),(best quality),(soft realistic),ultra-detailed,8k,
japanese woman,mature,kind older sister,
short hair,glasses,gentle eyes,
white lab coat over a pastel blouse,knee-length skirt,holding a clipboard,
school infirmary background,
```
※ LoRAなし。保健室の先生。白衣・メガネ・ショートカットが目印。体型は控えめな表現にとどめる。

### 如月 紗夜 `kisaragi-sayo`
```
(masterpiece),(best quality),ultra-detailed,8k,
mature japanese woman,elegant and dignified,
black silky hair in a traditional bun,
refined traditional ryokan hostess,
formal kimono,obi,hands folded,graceful bow,
japanese ryokan entrance background,
kisaragi sayo,
<lora:Sayo_Kisaragi_v1-000002:0.9>
```

## 仕上げ（ページへの組み込み）

1. 選ばれた画像を 600x800 に上寄せで切り抜き、WebPで `img/<id>.webp` に保存
   ```
   # 例（Pillow）
   from PIL import Image
   im = Image.open(src).convert("RGB")
   w, h = im.size; th = int(w * 4 / 3)
   im = im.crop((0, 0, w, min(th, h))).resize((600, 800), Image.LANCZOS)
   im.save(f"img/{cid}.webp", "WEBP", quality=80, method=6)
   ```
2. `index.html` の各キャラカードで、コメントアウトしてある `<img ...>` を有効にし、「画像準備中」の文字を消す
3. コミットして push
4. `index.html`・`style.css`・`img/` をzipにまとめ、mixhostの cPanel → ファイルマネージャー → `public_html` で展開（あかりが手作業で行う）
5. 反映されなければ cPanel の LiteSpeed Web Cache Manager で Flush All
