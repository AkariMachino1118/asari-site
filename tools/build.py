#!/usr/bin/env python3
"""キャラ個別ページ（chara/<id>/index.html）を data/characters.json から作る。

使い方:  python3 tools/build.py
- サンプル画像は img/gallery/<id>/ に .webp / .jpg / .png を置くと、ファイル名順に自動で載る
- main に push すると GitHub Actions でもこのスクリプトが動くので、実行し忘れても反映される
- 個別ページは全年齢。成人向けの画像は置かないこと
- 成人向けの r18/index.html と r18/chara/<id>/index.html もここで作る（画像はサーバーに直接。tools/upload_r18.py）
"""
import html
import json
from urllib.parse import quote
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "characters.json"
CSS_VERSION = "12"  # style.css を変えたら上げる
# pixiv の「タイトル・キャプション」検索。作品タイトルにキャラ名（スペースなし）が入っている前提
PIXIV_SEARCH = "https://www.pixiv.net/tags/{q}/artworks?s_mode=s_tc"
IMG_EXT = {".webp", ".jpg", ".jpeg", ".png"}

FONTS = "https://fonts.googleapis.com/css2?family=Zen+Antique&display=swap"


def e(s: str) -> str:
    return html.escape(s, quote=True)


def gallery_files(cid: str):
    d = ROOT / "img" / "gallery" / cid
    if not d.is_dir():
        return []
    return sorted(p for p in d.iterdir() if p.suffix.lower() in IMG_EXT)


# ----- サンプルボイス -----
AUDIO_EXT = (".mp3", ".m4a", ".ogg")

VOICE_JS = """<script>
  // サンプルボイス：ボタンで再生／停止（同時に鳴るのは1つだけ）
  (function () {
    var list = document.querySelector(".voice-list");
    if (!list) return;
    var audio = new Audio(), current = null;
    function stop() { audio.pause(); if (current) { current.classList.remove("is-playing"); current.setAttribute("aria-pressed", "false"); } current = null; }
    audio.addEventListener("ended", stop);
    function bind(btn) {
      btn.addEventListener("click", function () {
        if (current === btn) { stop(); return; }
        stop(); audio.src = btn.dataset.src; audio.play();
        current = btn; btn.classList.add("is-playing"); btn.setAttribute("aria-pressed", "true");
      });
    }
    var manifest = list.dataset.manifest;
    if (!manifest) { list.querySelectorAll(".voice-play").forEach(bind); return; }
    // 成人向け：サーバーの list.json にある音声だけ表示
    fetch(manifest, { cache: "no-cache" })
      .then(function (r) { return r.ok ? r.json() : []; })
      .catch(function () { return []; })
      .then(function (files) {
        var shown = 0;
        list.querySelectorAll("li").forEach(function (li) {
          var btn = li.querySelector(".voice-play");
          var name = btn.dataset.src.split("/").pop();
          if (files.indexOf(name) >= 0) { li.hidden = false; bind(btn); shown++; }
        });
        if (shown) document.getElementById("voice-empty").hidden = true;
      });
  })();
</script>"""


def voice_audio_file(cid: str, vid: str):
    for ext in AUDIO_EXT:
        f = ROOT / "audio" / cid / f"{vid}{ext}"
        if f.exists():
            return f
    return None


def voice_items(voices, src_of, hidden=False) -> str:
    rows = []
    for v in voices:
        src = src_of(v)
        if not src:
            continue
        hid = " hidden" if hidden else ""
        rows.append(
            f'      <li{hid}><button type="button" class="voice-play" data-src="{e(src)}" aria-pressed="false">'
            f'<span class="voice-icon" aria-hidden="true"></span><span class="voice-label">再生</span></button>'
            f'<p class="voice-line">「{e(v["line"])}」</p></li>')
    return "\n".join(rows)


def voice_section(c) -> str:
    cid = c["id"]

    def src_of(v):
        f = voice_audio_file(cid, v["id"])
        return f"../../audio/{cid}/{f.name}" if f else None

    items = voice_items(c.get("voices", []), src_of)
    credit = f'\n    <p class="voice-credit">音声：{e(c["voice_credit"])}</p>' if c.get("voice_credit") else ""
    body = f'    <ul class="voice-list">\n{items}\n    </ul>' if items else '    <p class="gallery-empty">ボイスは準備中です。</p>'
    return f"""  <section class="voice-sec">
    <h2 class="feature-title">サンプルボイス</h2>
{body}{credit}
  </section>

"""


def r18_voice_section(c) -> str:
    cid = c["id"]
    items = voice_items(c.get("r18_voices", []), lambda v: f"../../audio/{cid}/{v['id']}.mp3", hidden=True)
    credit = f'\n      <p class="voice-credit">音声：{e(c["voice_credit"])}</p>' if c.get("voice_credit") else ""
    return f"""    <section class="voice-sec">
      <h2 class="feature-title">成人向けサンプルボイス</h2>
      <ul class="voice-list" data-manifest="../../audio/{cid}/list.json">
{items}
      </ul>
      <p class="gallery-empty" id="voice-empty">ボイスは準備中です。</p>{credit}
    </section>

"""


def page(c, prev_c, next_c) -> str:
    cid = c["id"]
    files = gallery_files(cid)
    intro = "\n".join(f"        <p>{e(p)}</p>" for p in c["intro"])
    profile = "\n".join(
        f"        <div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in c["profile"])
    q = c["name"].replace(" ", "")
    if c.get("pixiv"):  # 個別にURLを指定したときはそちらを優先
        pixiv_url = c["pixiv"]
    else:
        pixiv_url = PIXIV_SEARCH.format(q=quote(q))
    pixiv_label = f"pixivで「{q}」のイラストを見る"

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

{voice_section(c)}  <section class="gallery-sec">
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

{VOICE_JS}
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


# ======================================================================
# 成人向け（r18/）のページ
#   - r18/index.html            … 年齢確認 → キャラ一覧
#   - r18/chara/<id>/index.html … 年齢確認 → キャラ紹介＋成人向けサンプル
# 成人向けの画像は GitHub に置かない（公開リポジトリのため）。
# サーバーの r18/img/<id>/ に tools/upload_r18.py で直接アップロードし、
# 同じ場所の list.json をページが読み込んで並べる。
# ======================================================================

GATE_HEAD = """<script>
  // 前回「はい」を押していれば、描画前にロックを外す（ゲートが一瞬出るのを防ぐ）
  (function () {
    try {
      var until = Number(localStorage.getItem("ageOkUntil") || 0);
      if (until > Date.now()) document.documentElement.classList.remove("gate-locked");
    } catch (e) { /* 保存できない環境では毎回確認 */ }
  })();
</script>"""

GATE_BODY = """<!-- ===== 年齢確認ゲート ===== -->
<section id="age-gate" role="dialog" aria-labelledby="gate-title">
  <div class="gate-card">
    <div class="gate-badge">R-18</div>
    <h1 id="gate-title">年齢確認</h1>
    <p>この先には、18歳未満の方の閲覧に適さない内容が含まれています。</p>
    <p>あなたは18歳以上ですか？</p>
    <p class="note">登場人物はすべて18歳以上です。</p>
    <div class="gate-buttons">
      <button id="gate-yes" type="button">はい（18歳以上）</button>
      <a id="gate-no" href="{top}">いいえ（トップに戻る）</a>
    </div>
    <label class="gate-remember">
      <input type="checkbox" id="gate-remember" checked>
      30日間この確認を表示しない
    </label>
    <noscript><p class="note">このページの閲覧にはJavaScriptを有効にしてください。</p></noscript>
  </div>
</section>"""

GATE_SCRIPT = """<script>
  document.getElementById("gate-yes").addEventListener("click", function () {
    if (document.getElementById("gate-remember").checked) {
      try { localStorage.setItem("ageOkUntil", String(Date.now() + 30 * 864e5)); } catch (e) {}
    }
    document.documentElement.classList.remove("gate-locked");
    window.scrollTo(0, 0);
  });
</script>"""


def r18_head(title: str, css: str) -> str:
    return f"""<!doctype html>
<html lang="ja" class="gate-locked">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- このファイルは tools/build.py が自動で作っています。直接編集せず data/characters.json を直してください -->
<title>{e(title)}</title>
<meta name="robots" content="noindex, nofollow, noimageindex">
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{css}style.css?v={CSS_VERSION}">
{GATE_HEAD}
</head>
<body>
"""


def r18_index(chars) -> str:
    items = []
    for c in chars:
        items.append(f"""    <article class="profile">
      <img src="img/top/{c['id']}.webp" onerror="this.onerror=null;this.src='../img/{c['id']}.webp'" alt="{e(c['name'])}の立ち絵" loading="lazy">
      <div class="profile-text">
        <h3 class="name"><a href="chara/{c['id']}/">{e(c['name'])}</a></h3>
        <p class="roman">{e(c['roman'])}</p>
        <p class="catch">{e(c['catch'])}</p>
        <p class="desc">{e(c.get('r18_desc') or c['desc'])}</p>
        <a class="more" href="chara/{c['id']}/">成人向けサンプルを見る</a>
      </div>
    </article>""")
    body = "\n".join(items)
    return r18_head("成人向けコンテンツ | あさりちゃんの部屋", "../") + GATE_BODY.format(top="../") + f"""

<div id="site">
  <header class="site-header">
    <div class="wrap">
      <p class="site-title"><a href="./">あさりちゃんの部屋 <span class="r18-mark">R-18</span></a></p>
      <nav class="site-nav"><a href="../">全年齢のトップへ</a></nav>
    </div>
  </header>

  <main class="wrap">
    <section id="chara">
      <h2 class="feature-title">キャラクター大図鑑 R-18</h2>
      <p class="feature-lead">各キャラクターの成人向けサンプルを載せています。</p>
      <a class="pickup-link" href="pickup/"><span class="c-name">ランダムピックアップ</span><span class="c-note">pixivのイラストを1枚ずつ表示。タップで作品ページへ</span></a>
{body}
    </section>
  </main>

  <footer class="site-footer">
    <div class="wrap"><p><a class="adult-link" href="../">全年齢のトップへ戻る</a></p><p>&copy; あさりちゃんの部屋</p></div>
  </footer>
</div>

{GATE_SCRIPT}
</body>
</html>
"""


def r18_page(c, prev_c, next_c) -> str:
    cid = c["id"]
    intro_src = c.get("r18_intro") or c["intro"]
    intro = "\n".join(f"        <p>{e(p)}</p>" for p in intro_src)
    profile = "\n".join(
        f"        <div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in c["profile"])
    q = c["name"].replace(" ", "")
    pixiv_url = c.get("pixiv") or PIXIV_SEARCH.format(q=quote(q))
    pager = []
    if prev_c:
        pager.append(f'<a class="pager-prev" href="../{prev_c["id"]}/"><span>前のキャラクター</span>{e(prev_c["name"])}</a>')
    if next_c:
        pager.append(f'<a class="pager-next" href="../{next_c["id"]}/"><span>次のキャラクター</span>{e(next_c["name"])}</a>')

    return r18_head(f"{c['name']}（R-18） | あさりちゃんの部屋", "../../../") + GATE_BODY.format(top="../../../") + f"""

<div id="site">
  <header class="site-header">
    <div class="wrap">
      <p class="site-title"><a href="../../">あさりちゃんの部屋 <span class="r18-mark">R-18</span></a></p>
      <nav class="site-nav"><a href="../../">キャラクター一覧</a></nav>
    </div>
  </header>

  <main class="wrap chara-page">
    <section class="chara-hero">
      <img class="chara-main" src="../../img/top/{cid}.webp" onerror="this.onerror=null;this.src='../../../img/{cid}.webp'" alt="{e(c["name"])}の立ち絵">
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
        <a class="pixiv-button" href="{e(pixiv_url)}" target="_blank" rel="noopener">pixivで「{e(q)}」のイラストを見る</a>
      </div>
    </section>

{r18_voice_section(c)}    <section class="gallery-sec">
      <h2 class="feature-title">成人向けサンプル</h2>
      <ul class="gallery" id="r18-gallery" data-dir="../../img/{cid}/"></ul>
      <p class="gallery-empty" id="r18-empty">サンプル画像は準備中です。</p>
    </section>

    <nav class="chara-pager" aria-label="ほかのキャラクター">
      {"".join(pager)}
    </nav>
  </main>

  <footer class="site-footer">
    <div class="wrap"><p><a class="adult-link" href="../../../">全年齢のトップへ戻る</a></p><p>&copy; あさりちゃんの部屋</p></div>
  </footer>
</div>

<dialog class="viewer" aria-label="拡大表示">
  <img alt="">
  <button type="button" class="viewer-close">閉じる</button>
</dialog>

{GATE_SCRIPT}
{VOICE_JS}
<script>
  // サーバーの r18/img/<id>/list.json を読み込んで、サンプル画像を並べる
  (function () {{
    var ul = document.getElementById("r18-gallery");
    var empty = document.getElementById("r18-empty");
    var dir = ul.dataset.dir;
    var dlg = document.querySelector(".viewer");
    var big = dlg.querySelector("img");
    fetch(dir + "list.json", {{ cache: "no-cache" }})
      .then(function (r) {{ return r.ok ? r.json() : []; }})
      .catch(function () {{ return []; }})
      .then(function (files) {{
        if (!files.length) return;
        empty.hidden = true;
        files.forEach(function (name, i) {{
          var li = document.createElement("li");
          var b = document.createElement("button");
          b.type = "button"; b.className = "g-item";
          var img = document.createElement("img");
          img.src = dir + name; img.loading = "lazy";
          img.alt = {json.dumps(c["name"])} + "の成人向けイラスト " + (i + 1);
          b.appendChild(img); li.appendChild(b); ul.appendChild(li);
          b.addEventListener("click", function () {{
            big.src = img.src; big.alt = img.alt;
            if (dlg.showModal) dlg.showModal();
          }});
        }});
      }});
    dlg.addEventListener("click", function (ev) {{ if (ev.target !== big) dlg.close(); }});
  }})();
</script>
</body>
</html>
"""


# ======================================================================
# ランダムピックアップ（成人向け側：r18/pickup/index.html）
#   サーバーの r18/img/pickup/<pixiv作品ID>.webp から1枚をランダムに表示し、
#   タップで https://www.pixiv.net/artworks/<作品ID> を開く。
#   画像は GitHub に入れず tools/upload_r18.py で送る（list.json を読み込んで並べる）。
# ======================================================================

def r18_pickup_page() -> str:
    return r18_head("ランダムピックアップ（R-18） | あさりちゃんの部屋", "../../") + GATE_BODY.format(top="../../") + """

<div id="site">
  <header class="site-header">
    <div class="wrap">
      <p class="site-title"><a href="../">あさりちゃんの部屋 <span class="r18-mark">R-18</span></a></p>
      <nav class="site-nav"><a href="../">キャラクター一覧</a></nav>
    </div>
  </header>

  <main class="wrap pickup">
    <h1 class="feature-title">ランダムピックアップ</h1>
    <p class="feature-lead">pixivに投稿したイラストから、1枚をランダムに表示しています。絵をタップするとpixivで開きます。</p>

    <a class="pickup-card" id="pick" href="https://www.pixiv.net/users/7204909" target="_blank" rel="noopener" hidden>
      <img id="pick-img" alt="">
    </a>
    <p class="pickup-hint" id="pick-hint" hidden>タップでpixivの作品ページへ</p>
    <button type="button" class="pickup-next" id="pick-next" hidden>ほかの絵を見る</button>
    <p class="gallery-empty" id="pick-empty">イラストは準備中です。</p>
  </main>

  <footer class="site-footer">
    <div class="wrap"><p><a class="adult-link" href="../../">全年齢のトップへ戻る</a></p><p>&copy; あさりちゃんの部屋</p></div>
  </footer>
</div>

""" + GATE_SCRIPT + """
<script>
  (function () {
    var dir = "../img/pickup/";
    fetch(dir + "list.json", { cache: "no-cache" })
      .then(function (r) { return r.ok ? r.json() : []; })
      .catch(function () { return []; })
      .then(function (files) {
        // ファイル名（<作品ID>.webp）から作品IDを取り出す
        var items = files.map(function (f) { return { id: String(f).split(".")[0], src: dir + f }; })
                         .filter(function (it) { return /^\\d+$/.test(it.id); });
        if (!items.length) return;
        // シャッフルして順に見せる（一巡するまで同じ絵は出ない）
        for (var i = items.length - 1; i > 0; i--) {
          var j = Math.floor(Math.random() * (i + 1)); var t = items[i]; items[i] = items[j]; items[j] = t;
        }
        var pos = 0;
        var a = document.getElementById("pick"), img = document.getElementById("pick-img");
        var next = document.getElementById("pick-next");
        function show() {
          var it = items[pos % items.length];
          img.src = it.src; img.alt = "pixiv作品 " + it.id;
          a.href = "https://www.pixiv.net/artworks/" + it.id;
          var pre = new Image(); pre.src = items[(pos + 1) % items.length].src;  // 次の絵を先読み
        }
        document.getElementById("pick-empty").hidden = true;
        a.hidden = false; document.getElementById("pick-hint").hidden = false;
        next.hidden = items.length < 2;
        next.addEventListener("click", function () { pos++; show(); });
        show();
      });
  })();
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

        r18_out = ROOT / "r18" / "chara" / c["id"] / "index.html"
        r18_out.parent.mkdir(parents=True, exist_ok=True)
        r18_out.write_text(r18_page(c, prev_c, next_c), encoding="utf-8")

    (ROOT / "r18" / "index.html").write_text(r18_index(chars), encoding="utf-8")
    print("built r18/index.html と r18/chara/*/index.html")

    out = ROOT / "r18" / "pickup" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(r18_pickup_page(), encoding="utf-8")
    print("built r18/pickup/index.html")


if __name__ == "__main__":
    main()
