# -*- coding: utf-8 -*-
"""黑底 B-roll：先给场景再给方法。中文全部代码绘制。"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
W, H, FPS = 720, 1280, 24
BG = (11, 13, 18)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
CARD = (24, 28, 38)
RED = (255, 118, 118)
INK = (28, 32, 36)
FONT_REG = "/tmp/NotoSansSC-Regular.otf"
FONT_BD = "/tmp/NotoSansSC-Bold.otf"


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BD if bold else FONT_REG, size)


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


def new_bg() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    overlay = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(overlay)
    d.ellipse((-180, -220, 500, 400), fill=(16, 42, 38))
    d.ellipse((340, 820, 980, 1500), fill=(42, 32, 16))
    overlay = overlay.filter(ImageFilter.GaussianBlur(90))
    return Image.blend(img, overlay, 0.58)


def tag(draw, t: float, label: str) -> None:
    a = appear(t, 0.0, 0.24)
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


def strike_line(draw, box, t: float, start: float) -> None:
    st = appear(t, start, 0.28)
    if st <= 0.04:
        return
    cy = (box[1] + box[3]) // 2
    x0, x1 = box[0] + 48, box[2] - 48
    draw.line([(x0, cy), (int(lerp(x0, x1, st)), cy)], fill=mix(CARD, RED, st), width=10)


def b_method_first(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(44)
    card_f = font(34)
    sub_f = font(26)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "对照 方法在前")
        a0 = appear(t, 0.02)
        d.text((W // 2, 188 + int(lerp(18, 0, a0))), "方法甩在前面", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        a1 = appear(t, 0.28)
        if a1 > 0.04:
            y = 250 + int(lerp(22, 0, a1))
            box = (56, y, 664, y + 200)
            rounded(d, box, 28, mix(BG, CARD, a1))
            d.text((90, y + 70), "先甩方法", font=card_f, fill=mix(CARD, YELLOW, a1), anchor="lm")
            d.text((90, y + 140), "没有场景", font=sub_f, fill=mix(CARD, MUTED, a1), anchor="lm")
            strike_line(d, box, t, 0.85)

        a2 = appear(t, 1.15)
        if a2 > 0.04:
            y = 490 + int(lerp(22, 0, a2))
            rounded(d, (56, y, 664, y + 220), 28, mix(BG, CARD, a2))
            d.text((W // 2, y + 78), "听众对不上自己", font=title_f, fill=mix(CARD, RED, a2), anchor="mm")
            d.text((W // 2, y + 150), "这句话不是给我的", font=sub_f, fill=mix(CARD, MUTED, a2), anchor="mm")

        punch = appear(t, 2.05, 0.28)
        if punch > 0.04:
            y = 780 + int(lerp(24, 0, punch))
            rounded(d, (80, y, 640, y + 180), 26, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y + 90), "对不上自己", font=title_f, fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def b_scene_front(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(42)
    card_f = font(34)
    sub_f = font(26)
    out = []
    rows = [
        (0.12, "01", "场景先落地", "让人认出自己", MINT),
        (0.95, "02", "方法再跟上", "这下才接得住", YELLOW),
    ]
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "改法 场景前移")
        d.text(
            (W // 2, 188 + int(lerp(18, 0, appear(t, 0.02)))),
            "写完开场",
            font=title_f,
            fill=mix(BG, WHITE, appear(t, 0.02)),
            anchor="mm",
        )
        y0 = 250
        for idx, (ts, num, head, body, color) in enumerate(rows):
            a = appear(t, ts, 0.28)
            if a < 0.04:
                continue
            y = y0 + idx * 220 + int(lerp(22, 0, a))
            rounded(d, (56, y, 664, y + 196), 28, mix(BG, CARD, a))
            d.ellipse((86, y + 72, 138, y + 124), fill=mix(CARD, color, a))
            d.text((112, y + 98), num, font=sub_f, fill=mix(color, INK, a), anchor="mm")
            d.text((168, y + 74), head, font=title_f, fill=mix(CARD, color, a), anchor="lm")
            d.text((168, y + 132), body, font=card_f, fill=mix(CARD, WHITE, a), anchor="lm")

        punch = appear(t, 2.05, 0.28)
        if punch > 0.04:
            y = 780 + int(lerp(24, 0, punch))
            rounded(d, (70, y, 650, y + 190), 26, mix(BG, (18, 42, 36), punch))
            d.text((W // 2, y + 95), "把场景挪到前面", font=title_f, fill=mix(BG, MINT, punch), anchor="mm")
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
        ("broll/B-方法在前.mp4", b_method_first),
        ("broll/B-场景前移.mp4", b_scene_front),
    ]
    for rel, fn in jobs:
        dur = durs.get(rel)
        if not dur:
            raise SystemExit(f"no duration for {rel}")
        print("render", rel, dur)
        frames = fn(max(dur, 2.4))
        frames_to_mp4(frames, ROOT / rel)
        print(" wrote", ROOT / rel)


if __name__ == "__main__":
    main()
