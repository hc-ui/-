# -*- coding: utf-8 -*-
"""B-roll: slow leaf + syrup street. Chinese drawn in code only."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
W, H, FPS = 720, 1280, 24
BG = (11, 13, 18)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
CARD = (24, 28, 38)
INK = (28, 32, 36)
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
NOTO = "/tmp/NotoSansSC-Bold.otf"


def font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(NOTO, size)
    except OSError:
        return ImageFont.truetype(FONT_PATH, size)


def ease_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def appear(t: float, start: float, dur: float = 0.38) -> float:
    return ease_out((t - start) / dur)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def mix(c0, c1, a: float):
    a = max(0.0, min(1.0, a))
    return tuple(int(c1[i] * a + c0[i] * (1 - a)) for i in range(3))


def rounded(draw: ImageDraw.ImageDraw, xy, r: int, fill) -> None:
    draw.rounded_rectangle(xy, radius=r, fill=fill)


def text_wh(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=fnt)
    return x1 - x0, y1 - y0


def kenburns(src: Path, t: float, duration: float, y_bias: float = 0.28) -> Image.Image:
    im = Image.open(src).convert("RGB")
    p = min(1.0, t / max(0.01, duration))
    s = lerp(1.10, 1.22, p)
    nw, nh = int(W * s), int(H * s)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = int((nw - W) * (0.40 + 0.18 * p))
    y = int((nh - H) * (y_bias + 0.12 * p))
    crop = im.crop((x, y, x + W, y + H))
    crop = ImageEnhance.Brightness(crop).enhance(0.48)
    crop = ImageEnhance.Color(crop).enhance(0.78)
    veil = Image.new("RGB", (W, H), BG)
    return Image.blend(crop, veil, 0.30)


def tag(draw, t: float, label: str) -> None:
    a = appear(t, 0.0, 0.22)
    if a <= 0:
        return
    fnt = font(22)
    tw, th = text_wh(draw, label, fnt)
    x, y = 56, 58
    rounded(draw, (x - 16, y - 10, x + tw + 16, y + th + 8), 16, mix(BG, (20, 42, 38), a))
    draw.text((x, y), label, font=fnt, fill=mix(BG, MINT, a))


def frames_to_mp4(frames: list[Image.Image], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    out_w, out_h = 1080, 1920
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{out_w}x{out_h}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18",
        str(dest),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    for im in frames:
        rgb = im.convert("RGB").resize((out_w, out_h), Image.Resampling.LANCZOS)
        proc.stdin.write(rgb.tobytes())
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(err[-2000:])
    frames[min(len(frames) // 2, len(frames) - 1)].save(dest.with_suffix(".jpg"), quality=92)


def b_leaf(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(44)
    card_f = font(34)
    huge = font(40)
    src = ROOT / "assets" / "b-slow-leaf.png"
    out = []
    for i in range(n):
        t = i / FPS
        img = kenburns(src, t, duration, 0.22) if src.exists() else Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        tag(d, t, "现象 超慢坠落")
        a0 = appear(t, 0.02)
        d.text((W // 2, 198 + int(lerp(18, 0, a0))), "叶子掉了二十秒", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        d.text((W // 2, 268), "还没落地", font=huge, fill=mix(BG, YELLOW, appear(t, 0.12)), anchor="mm")

        left_t = min(0.32, duration * 0.16)
        left = appear(t, left_t, 0.24)
        if left > 0.04:
            y = 430 + int(lerp(22, 0, left))
            rounded(d, (48, y, 348, y + 220), 28, mix(BG, CARD, left))
            d.text((198, y + 70), "不是慢镜头", font=card_f, fill=mix(CARD, MUTED, left), anchor="mm")
            d.text((198, y + 140), "空气太稠", font=huge, fill=mix(CARD, WHITE, left), anchor="mm")

        right_t = min(0.50, duration * 0.28)
        right = appear(t, right_t, 0.24)
        if right > 0.04:
            y = 430 + int(lerp(22, 0, right))
            rounded(d, (372, y, 672, y + 220), 28, mix(BG, CARD, right))
            d.text((522, y + 70), "灰尘永不落", font=card_f, fill=mix(CARD, MUTED, right), anchor="mm")
            d.text((522, y + 140), "黏在空气里", font=huge, fill=mix(CARD, YELLOW, right), anchor="mm")

        punch = appear(t, max(0.85, duration - 0.85), 0.22)
        if punch > 0.04:
            y = 760 + int(lerp(20, 0, punch))
            rounded(d, (70, y, 650, y + 170), 26, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y + 85), "黏度 ×10000", font=title_f, fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def b_syrup(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(42)
    card_f = font(32)
    sub_f = font(26)
    src = ROOT / "assets" / "b-syrup-street.png"
    rows = [
        (0.08, "01", "旗子不飘", "只慢慢弯", YELLOW),
        (min(0.55, duration * 0.30), "02", "声音变闷", "空气太稠", MINT),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = kenburns(src, t, duration, 0.38) if src.exists() else Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        tag(d, t, "后果 糖浆空气")
        d.text(
            (W // 2, 188 + int(lerp(16, 0, appear(t, 0.02)))),
            "像浸在糖浆里",
            font=title_f,
            fill=mix(BG, WHITE, appear(t, 0.02)),
            anchor="mm",
        )
        y0 = 270
        for idx, (ts, num, head, body, color) in enumerate(rows):
            a = appear(t, ts, 0.26)
            if a < 0.04:
                continue
            y = y0 + idx * 210 + int(lerp(20, 0, a))
            rounded(d, (56, y, 664, y + 186), 28, mix(BG, CARD, a))
            d.ellipse((86, y + 68, 138, y + 120), fill=mix(CARD, color, a))
            d.text((112, y + 94), num, font=sub_f, fill=mix(color, INK, a), anchor="mm")
            d.text((168, y + 70), head, font=title_f, fill=mix(CARD, color, a), anchor="lm")
            d.text((168, y + 128), body, font=card_f, fill=mix(CARD, WHITE, a), anchor="lm")

        punch = appear(t, max(1.05, duration - 0.80), 0.22)
        if punch > 0.04:
            y = 750 + int(lerp(18, 0, punch))
            rounded(d, (70, y, 650, y + 180), 26, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y + 58), "雨、灰、鸟", font=sub_f, fill=mix(BG, MUTED, punch), anchor="mm")
            d.text((W // 2, y + 118), "都悬着慢移", font=title_f, fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def shot_durs() -> dict[str, float]:
    data = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
    out = {}
    for shot in data["shots"]:
        if shot.get("kind") == "B":
            out[shot["src"]] = float(shot["end"]) - float(shot["start"])
    return out


def main() -> None:
    durs = shot_durs()
    jobs = [
        ("broll/B-叶子还没落地.mp4", b_leaf),
        ("broll/B-旗子慢慢弯.mp4", b_syrup),
    ]
    for rel, fn in jobs:
        dur = durs.get(rel)
        if not dur:
            raise SystemExit(f"no duration for {rel}")
        print("render", rel, dur)
        frames_to_mp4(fn(dur), ROOT / rel)
        print(" wrote", ROOT / rel)


if __name__ == "__main__":
    main()
