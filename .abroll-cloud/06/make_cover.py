# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
W, H = 1080, 1920
FONT_PATH = "/tmp/NotoSansSC-Bold.otf"


def main() -> None:
    data = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
    cover = data["cover"]
    char = Image.open(ROOT / cover["src"]).convert("RGB")
    scale = max(W / char.width, H / char.height)
    nw, nh = int(char.width * scale), int(char.height * scale)
    char = char.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - W) // 2
    y = int((nh - H) * 0.62)
    canvas = char.crop((x, y, x + W, y + H))
    overlay = Image.new("RGBA", (W, H), (11, 13, 18, 36))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((90, 90, 990, 430), radius=36, fill=(22, 24, 28))
    d.text((W // 2, 168), cover["title"], font=ImageFont.truetype(FONT_PATH, 58), fill=(245, 247, 250), anchor="mm")
    d.text((W // 2, 258), cover["sub"], font=ImageFont.truetype(FONT_PATH, 44), fill=(126, 224, 197), anchor="mm")
    d.text((W // 2, 348), cover["line"], font=ImageFont.truetype(FONT_PATH, 30), fill=(154, 162, 176), anchor="mm")
    out = ROOT / "final" / "cover.jpg"
    out.parent.mkdir(exist_ok=True)
    canvas.save(out, quality=92)
    print("cover", out)


if __name__ == "__main__":
    main()
