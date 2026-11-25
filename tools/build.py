#!/usr/bin/env python3
"""キャラ個別ページ（chara/<id>/index.html）を data/characters.json から作る。

使い方:  python3 tools/build.py
- サンプル画像は img/gallery/<id>/ に .webp / .jpg / .png を置くと、ファイル名順に自動で載る
- main に push すると GitHub Actions でもこのスクリプトが動くので、実行し忘れても反映される
- 個別ページは全年齢。成人向けの画像は置かないこと
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "characters.json"
CSS_VERSION = "8"  # style.css を変えたら上げる
PIXIV_PROFILE = "https://www.pixiv.net/users/7204909"
IMG_EXT = {".webp", ".jpg", ".jpeg", ".png"}

FONTS = ("https://fonts.googleapis.com/css2?family=Zen+Old+Mincho:wght@600;700"
         "&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap")


def e(s: str) -> str:
    return html.escape(s, quote=True)


def gallery_files(cid: str):
    d = ROOT / "img" / "gallery" / cid
    if not d.is_dir():
        return []
    return sorted(p for p in d.iterdir() if p.suffix.lower() in IMG_EXT)


def page(c, prev_c, next_c) -> str:
    cid = c["id"]
    files = gallery_files(cid)
    intro = "\n".join(f"        <p>{e(p)}</p>" for p in c["intro"])
    profile = "\n".join(
        f"        <div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in c["profile"])
    if c.get("pixiv"):
        pixiv_url, pixiv_label = c["pixiv"], f"pixivで{c['name'].split()[-1]}のイラストを見る"
    else:
        pixiv_url, pixiv_label = PIXIV_PROFILE, "pixivでイラスト一覧を見る"

    if files:
        items = "\n".join(
            f'      <li><button type="button" class="g-item" data-src="../../img/gallery/{cid}/{e(p.name)}">'
            f'<img src="../../img/gallery/{cid}/{e(p.name)}" alt="{e(c["name"])}のイラスト {i}" loading="lazy"></button></li>'
            for i, p in enumerate(files, 1))
        gallery = f'    <ul class="gallery">\n{items}\n    </ul>'
    else:
        gallery = '    <p class="gallery-empty">サンプル画像は準備中です。</p>'

    pager = []
    if prev_c:
        pager.append(f'<a class="pager-prev" href="../{prev_c["id"]}/"><span>前のキャラクター</span>{e(prev_c["name"])}</a>')
    if next_c:
        pager.append(f'<a class="pager-next" href="../{next_c["id"]}/"><span>次のキャラクター</span>{e(next_c["name"])}</a>')

    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- このファイルは tools/build.py が自動で作っています。直接編集せず data/characters.json を直してください -->
<title>{e(c["name"])} | あさりちゃんの部屋</title>
<meta name="description" content="{e(c["desc"])}">
<meta property="og:title" content="{e(c["name"])} | あさりちゃんの部屋">
<meta property="og:description" content="{e(c["desc"])}">
<meta property="og:image" content="https://aiasar.com/img/{cid}.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://aiasar.com/chara/{cid}/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="../../style.css?v={CSS_VERSION}">
</head>
<body>

<header class="site-header">
  <div class="wrap">
    <p class="site-title"><a href="../../">あさりちゃんの部屋</a></p>
    <nav class="site-nav"><a href="../../#chara">キャラクター大図鑑</a></nav>
  </div>
</header>

<main class="wrap chara-page">

  <section class="chara-hero">
    <img class="chara-main" src="../../img/{cid}.webp" alt="{e(c["name"])}の立ち絵">
    <div class="chara-info">
      <p class="kana">{e(c["kana"])}</p>
      <h1 class="name">{e(c["name"])}</h1>
      <p class="roman">{e(c["roman"])}</p>
      <p class="catch">{e(c["catch"])}</p>
      <div class="intro">
{intro}
      </div>
      <dl class="profile-list">
{profile}
      </dl>
      <a class="pixiv-button" href="{e(pixiv_url)}" target="_blank" rel="noopener">{e(pixiv_label)}</a>
    </div>
  </section>

  <section class="gallery-sec">
    <h2 class="feature-title">ギャラリー</h2>
{gallery}
  </section>

  <nav class="chara-pager" aria-label="ほかのキャラクター">
    {"".join(pager)}
  </nav>

</main>

<dialog class="viewer" aria-label="拡大表示">
  <img alt="">
  <button type="button" class="viewer-close">閉じる</button>
</dialog>

<footer class="site-footer">
  <div class="wrap">
    <p><a class="adult-link" href="../../r18/">成人向けコンテンツ（18歳以上）</a></p>
    <p>&copy; あさりちゃんの部屋</p>
  </div>
</footer>

<script>
  // サンプル画像をタップすると拡大表示（背景タップ・閉じる・Escで閉じる）
  (function () {{
    var dlg = document.querySelector(".viewer");
    if (!dlg || !dlg.showModal) return;
    var img = dlg.querySelector("img");
    document.querySelectorAll(".g-item").forEach(function (b) {{
      b.addEventListener("click", function () {{
        img.src = b.dataset.src; img.alt = b.querySelector("img").alt;
        dlg.showModal();
      }});
    }});
    dlg.addEventListener("click", function (ev) {{ if (ev.target !== img) dlg.close(); }});
  }})();
</script>
</body>
</html>
"""


def main():
    chars = json.loads(DATA.read_text(encoding="utf-8"))["characters"]
    for i, c in enumerate(chars):
        prev_c = chars[i - 1] if i > 0 else None
        next_c = chars[i + 1] if i + 1 < len(chars) else None
        out = ROOT / "chara" / c["id"] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(c, prev_c, next_c), encoding="utf-8")
        print(f"built {out.relative_to(ROOT)}  (gallery: {len(gallery_files(c['id']))}枚)")


if __name__ == "__main__":
    main()
