# -*- coding: utf-8 -*-
"""A-roll rounded captions + color shutters. B-roll is not re-captioned."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 24
FONT_PATH = str(ROOT / "fonts" / "NotoSansSC-Bold.otf")
FALLBACK = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
DATA = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
DUR = float(DATA["duration"])
CUES = [(c["start"], c["end"], c["lines"]) for c in DATA["a_caps"]]
SHUTTERS = [(s["start"], tuple(s["color"])) for s in DATA["shutters"]]
EYEBROWS = [(e["start"], e["end"], e["text"]) for e in DATA["eyebrows"]]


def font(size: int):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        return ImageFont.truetype(FALLBACK, size)


def active_cue(t: float):
    for s, e, lines in CUES:
        if s <= t < e:
            return s, e, lines
    return None


def draw_eyebrow(base: Image.Image, t: float) -> None:
    label = None
    for s, e, text in EYEBROWS:
        if s <= t < e:
            label = text
            break
    if not label:
        return
    d = ImageDraw.Draw(base)
    d.rectangle((76, 88, 120, 92), fill=(126, 224, 197, 230))
    d.text((136, 78), label, font=font(22), fill=(90, 98, 108, 220))


def draw_pill(base: Image.Image, lines: list[str], y: int = 168) -> None:
    fnt = font(56 if len(lines) == 1 else 50)
    dummy = ImageDraw.Draw(base)
    widths, heights = [], []
    for line in lines:
        x0, y0, x1, y1 = dummy.textbbox((0, 0), line, font=fnt)
        widths.append(x1 - x0)
        heights.append(y1 - y0)
    tw = max(widths)
    line_h = max(heights) + 10
    pad_x, pad_y = 40, 22
    box_w = tw + pad_x * 2
    box_h = pad_y * 2 + line_h * len(lines) - 8
    x0 = (W - box_w) // 2
    pill = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle((0, 0, box_w - 1, box_h - 1), radius=28, fill=(22, 24, 28, 214))
    pd.rectangle((10, 14, 20, box_h - 14), fill=(126, 224, 197, 235))
    for i, line in enumerate(lines):
        pd.text((box_w / 2 + 4, pad_y + line_h * i), line, font=fnt, fill=(245, 247, 250, 255), anchor="mt")
    shadow = pill.filter(ImageFilter.GaussianBlur(8))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.alpha_composite(shadow, (x0, y + 4))
    base.alpha_composite(sh)
    base.alpha_composite(pill, (x0, y))


def draw_shutter(base: Image.Image, t: float) -> Image.Image:
    for start, color in SHUTTERS:
        dt = t - start
        if 0 <= dt <= 0.16:
            p = dt / 0.16
            if p < 0.5:
                w = max(2, int(W * p * 2))
                x0 = 0
            else:
                w = max(2, int(W * (1 - (p - 0.5) * 2)))
                x0 = W - w
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(layer).rectangle((x0, 0, x0 + w, H), fill=(*color, 235))
            base = Image.alpha_composite(base, layer)
    return base


def frame_at(t: float) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_eyebrow(img, t)
    cue = active_cue(t)
    if cue:
        draw_pill(img, cue[2])
    return draw_shutter(img, t)


def main() -> None:
    n = max(1, round(DUR * FPS))
    dest = ROOT / "shots" / "caption_layer.mov"
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "qtrle", "-pix_fmt", "argb",
        str(dest),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    for i in range(n):
        proc.stdin.write(frame_at(i / FPS).tobytes())
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(err[-2500:])
    print("wrote", dest, "frames", n)


if __name__ == "__main__":
    main()
