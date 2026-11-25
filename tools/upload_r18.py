#!/usr/bin/env python3
"""成人向けサンプル画像を、GitHub を通さずに mixhost の r18/img/<id>/ へ直接アップロードする。

なぜ直接か：asari-site は公開リポジトリで、GitHub の規約上も成人向け画像は置けないため。
画像はリポジトリの外のフォルダ（例: E:\\r18_gallery）で管理する。

フォルダの形：
  E:\\r18_gallery\\
    mashiro-miu\\  01.png 02.png ...
    mizushima-kei\\ ...
  （フォルダ名はキャラの id。ファイル名順に並ぶ）

使い方（PowerShell）：
  $env:FTP_SERVER="ik10016.mixhost.jp"; $env:FTP_USERNAME="deploy@aiasar.com"; $env:FTP_PASSWORD="..."
  python tools/upload_r18.py E:\\r18_gallery            # 全キャラ
  python tools/upload_r18.py E:\\r18_gallery mashiro-miu # 1人だけ
  python tools/upload_r18.py E:\\r18_gallery --sync      # ローカルに無い画像はサーバーからも消す

- png / jpg は長辺1200px・WebP品質80に変換してから送る（Pillow が必要: pip install pillow）
- 送ったあと、同じ場所に list.json（ファイル名の一覧）を書き込む。ページはこれを読んで画像を並べる
"""
import io
import json
import os
import sys
from ftplib import FTP_TLS, error_perm
from pathlib import Path

IMG_EXT = {".webp", ".jpg", ".jpeg", ".png"}
REMOTE_BASE = "r18/img"  # FTPアカウントのルート = public_html
LONG_EDGE = 1200


def to_webp(path: Path) -> bytes:
    if path.suffix.lower() == ".webp":
        return path.read_bytes()
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.thumbnail((LONG_EDGE, LONG_EDGE), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=80, method=6)
    return buf.getvalue()


def ensure_dir(ftp: FTP_TLS, path: str):
    cur = ""
    for part in path.split("/"):
        cur = f"{cur}/{part}" if cur else part
        try:
            ftp.mkd(cur)
        except error_perm:
            pass  # 既にある


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sync = "--sync" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(1)
    src = Path(args[0])
    only = set(args[1:])
    env = {k: os.environ.get(k) for k in ("FTP_SERVER", "FTP_USERNAME", "FTP_PASSWORD")}
    if not all(env.values()):
        sys.exit("FTP_SERVER / FTP_USERNAME / FTP_PASSWORD を環境変数に入れてください")

    ftp = FTP_TLS(env["FTP_SERVER"], timeout=60)
    ftp.login(env["FTP_USERNAME"], env["FTP_PASSWORD"])
    ftp.prot_p()

    for cdir in sorted(p for p in src.iterdir() if p.is_dir()):
        cid = cdir.name
        if only and cid not in only:
            continue
        files = sorted(p for p in cdir.iterdir() if p.suffix.lower() in IMG_EXT)
        remote = f"{REMOTE_BASE}/{cid}"
        ensure_dir(ftp, remote)
        names = []
        for f in files:
            name = f.stem + ".webp"
            ftp.storbinary(f"STOR {remote}/{name}", io.BytesIO(to_webp(f)))
            names.append(name)
            print(f"  {cid}/{name}")
        if sync:
            try:
                existing = [n.rsplit("/", 1)[-1] for n in ftp.nlst(remote)]
            except error_perm:
                existing = []
            for n in existing:
                if n.endswith(".webp") and n not in names:
                    ftp.delete(f"{remote}/{n}")
                    print(f"  削除 {cid}/{n}")
        ftp.storbinary(f"STOR {remote}/list.json",
                       io.BytesIO(json.dumps(names, ensure_ascii=False).encode("utf-8")))
        print(f"{cid}: {len(names)}枚 → list.json 更新")

    ftp.quit()


if __name__ == "__main__":
    main()
