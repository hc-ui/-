# -*- coding: utf-8 -*-
"""Topic 04: 咖啡自己滑向桌边 — cloud A-roll + B-roll assemble."""
from __future__ import annotations

import asyncio
import json
import math
import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 24
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
VOICE = "zh-CN-YunyangNeural"
NAME = "咖啡自己滑向桌边"

BG = (11, 13, 18)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
CARD = (24, 28, 38)
RED = (255, 118, 118)
CREAM = (236, 241, 239)
INK = (28, 32, 36)
A_BG = (244, 241, 234)
A_WARM = (255, 248, 232)

PHRASES = [
    "大家好。",
    "咖啡自己滑向桌边。",
    "不是飘。",
    "是摩擦力归零。",
    "停着的车开始溜。",
    "堆好的东西塌成一摊。",
    "绳结自己松开。",
    "三分钟到，整条街冻在滑完的样子。",
]

# kind, src relative, close, caption lines (A only)
SHOT_META = [
    ("A", "assets/A-挥手.mp4", True, ["大家好"]),
    ("B", "broll/B-咖啡滑.mp4", False, None),
    ("A", "assets/A-摊手.mp4", False, ["不是飘"]),
    ("B", "broll/B-定律.mp4", False, None),
    ("B", "broll/B-车溜.mp4", False, None),
    ("A", "assets/A-指向.mp4", False, ["堆好的东西塌成一摊"]),
    ("B", "broll/B-塌摊.mp4", False, None),
    ("B", "broll/B-冻住.mp4", False, None),
]


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout)[-2500:])


def probe(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True,
    )
    return float(out.strip())


def font(size: int) -> ImageFont.FreeTypeFont:
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


def new_b_bg() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    overlay = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(overlay)
    d.ellipse((-220, -280, 720, 560), fill=(16, 42, 38))
    d.ellipse((480, 1180, 1400, 2100), fill=(42, 32, 16))
    overlay = overlay.filter(ImageFilter.GaussianBlur(110))
    return Image.blend(img, overlay, 0.58)


def tag(draw, t: float, label: str) -> None:
    a = appear(t, 0.0, 0.24)
    if a <= 0:
        return
    fnt = font(32)
    tw, th = text_wh(draw, label, fnt)
    x, y = 84, 88
    rounded(draw, (x - 22, y - 14, x + tw + 22, y + th + 12), 22, mix(BG, (20, 42, 38), a))
    draw.text((x, y), label, font=fnt, fill=mix(BG, MINT, a))


def frames_to_mp4(frames: list[Image.Image], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18",
        str(dest),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    for im in frames:
        proc.stdin.write(im.convert("RGB").tobytes())
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(err[-2000:])
    mid = frames[min(len(frames) // 2, len(frames) - 1)]
    mid.save(dest.with_suffix(".jpg"), quality=92)


# ---------- TTS ----------
async def synth_one(text: str, dest: Path) -> None:
    import edge_tts

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".mp3")
    await edge_tts.Communicate(text, VOICE).save(str(tmp))
    run(["ffmpeg", "-y", "-i", str(tmp), "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", str(dest)])
    tmp.unlink(missing_ok=True)


async def make_voice() -> list[tuple[float, float]]:
    audio = ROOT / "audio"
    audio.mkdir(exist_ok=True)
    parts = []
    for i, phrase in enumerate(PHRASES):
        wav = audio / f"p{i:02d}.wav"
        if not wav.exists() or wav.stat().st_size < 1000:
            print("tts", phrase)
            await synth_one(phrase, wav)
        parts.append(wav)

    # 80 ms gap between phrases
    gap = audio / "gap.wav"
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.08", "-c:a", "pcm_s16le", str(gap)])
    lst = audio / "concat.txt"
    lines = []
    for i, p in enumerate(parts):
        lines.append(f"file '{p.as_posix()}'")
        if i < len(parts) - 1:
            lines.append(f"file '{gap.as_posix()}'")
    lst.write_text("\n".join(lines) + "\n", encoding="utf-8")
    vo = audio / "vo-full.wav"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(vo)])

    spans = []
    t = 0.0
    for i, p in enumerate(parts):
        d = probe(p)
        spans.append((t, t + d))
        t += d
        if i < len(parts) - 1:
            t += 0.08
    (audio / "vo-align.txt").write_text(
        "\n".join(f"{s:.3f}\t{e:.3f}\t{PHRASES[i].rstrip('。')}" for i, (s, e) in enumerate(spans)) + "\n",
        encoding="utf-8",
    )
    print("vo", vo, "dur", probe(vo))
    return spans


# ---------- A-roll: 白底小灯 ----------
def draw_xiaodeng(img: Image.Image, pose: str, t: float) -> None:
    d = ImageDraw.Draw(img)
    bob = int(6 * math.sin(t * 2.4))
    cx, cy = W // 2, 980 + bob
    # floor shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse((cx - 220, 1480, cx + 220, 1560), fill=(40, 36, 28, 50))
    img.alpha_composite(sh)

    # glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((cx - 260, cy - 320, cx + 260, cy + 200), fill=(255, 220, 140, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(36))
    img.alpha_composite(glow)

    # body
    d.rounded_rectangle((cx - 92, cy - 40, cx + 92, cy + 210), 70, fill=(255, 252, 246), outline=(210, 200, 180), width=4)
    # head / lamp glass
    d.ellipse((cx - 150, cy - 250, cx + 150, cy + 40), fill=(255, 244, 200), outline=(230, 200, 120), width=5)
    d.ellipse((cx - 70, cy - 210, cx + 10, cy - 130), fill=(255, 255, 240))
    # face
    eye_y = cy - 90
    d.ellipse((cx - 48, eye_y, cx - 22, eye_y + 28), fill=(40, 36, 32))
    d.ellipse((cx + 22, eye_y, cx + 48, eye_y + 28), fill=(40, 36, 32))
    d.arc((cx - 28, eye_y + 20, cx + 28, eye_y + 58), 20, 160, fill=(80, 60, 40), width=4)
    # mint badge
    d.rounded_rectangle((cx - 36, cy + 70, cx + 36, cy + 132), 16, fill=MINT)
    d.text((cx, cy + 101), "灯", font=font(36), fill=INK, anchor="mm")

    # arms
    if pose == "wave":
        ang = 0.35 + 0.25 * math.sin(t * 8)
        x2, y2 = cx + 170, cy - 40 - int(80 * math.sin(ang + 0.4))
        d.line([(cx + 90, cy + 40), (x2, y2)], fill=(255, 248, 230), width=22)
        d.ellipse((x2 - 28, y2 - 28, x2 + 28, y2 + 28), fill=YELLOW)
        d.line([(cx - 90, cy + 50), (cx - 170, cy + 160)], fill=(255, 248, 230), width=22)
        d.ellipse((cx - 198, cy + 138, cx - 142, cy + 194), fill=YELLOW)
    elif pose == "shrug":
        d.line([(cx - 90, cy + 30), (cx - 210, cy + 10)], fill=(255, 248, 230), width=22)
        d.line([(cx + 90, cy + 30), (cx + 210, cy + 10)], fill=(255, 248, 230), width=22)
        d.ellipse((cx - 238, cy - 18, cx - 182, cy + 38), fill=YELLOW)
        d.ellipse((cx + 182, cy - 18, cx + 238, cy + 38), fill=YELLOW)
    elif pose == "point":
        d.line([(cx + 90, cy + 20), (cx + 250, cy - 80)], fill=(255, 248, 230), width=22)
        d.ellipse((cx + 228, cy - 108, cx + 284, cy - 52), fill=YELLOW)
        d.line([(cx - 90, cy + 50), (cx - 150, cy + 180)], fill=(255, 248, 230), width=22)
        d.ellipse((cx - 178, cy + 158, cx - 122, cy + 214), fill=YELLOW)
    else:
        d.line([(cx - 90, cy + 50), (cx - 150, cy + 180)], fill=(255, 248, 230), width=22)
        d.line([(cx + 90, cy + 50), (cx + 150, cy + 180)], fill=(255, 248, 230), width=22)
        d.ellipse((cx - 178, cy + 158, cx - 122, cy + 214), fill=YELLOW)
        d.ellipse((cx + 122, cy + 158, cx + 178, cy + 214), fill=YELLOW)


def render_aroll(pose: str, dest: Path, seconds: float = 3.2) -> None:
    n = max(8, round(seconds * FPS))
    frames = []
    for i in range(n):
        t = i / FPS
        img = Image.new("RGBA", (W, H), A_BG + (255,))
        # studio wash
        wash = Image.new("RGB", (W, H), A_BG)
        wd = ImageDraw.Draw(wash)
        wd.ellipse((80, 220, 1000, 1100), fill=A_WARM)
        wash = wash.filter(ImageFilter.GaussianBlur(80))
        img = Image.alpha_composite(img, wash.convert("RGBA"))
        draw_xiaodeng(img, pose, t)
        d = ImageDraw.Draw(img)
        d.text((W // 2, 220), "小灯", font=font(28), fill=(170, 162, 148), anchor="mm")
        frames.append(img.convert("RGB"))
    frames_to_mp4(frames, dest)


# ---------- B-roll ----------
def b_coffee(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, sub_f = font(64), font(38)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "01 钩子")
        a0 = appear(t, 0.02)
        d.text((W // 2, 260 + int(lerp(22, 0, a0))), "咖啡自己走", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        # table
        a1 = appear(t, 0.18)
        if a1 > 0.04:
            y = 980
            rounded(d, (80, y, 1000, y + 220), 28, mix(BG, (62, 48, 34), a1))
            rounded(d, (80, y - 28, 1000, y + 18), 18, mix(BG, (92, 72, 50), a1))
            p = ease_out(min(1.0, t / max(0.01, duration - 0.25)))
            cx = int(lerp(280, 860, p))
            cy = y - 70
            d.ellipse((cx - 70, cy + 70, cx + 70, cy + 92), fill=mix(BG, (30, 22, 16), a1))
            d.rectangle((cx - 48, cy - 20, cx + 48, cy + 78), fill=mix(BG, (245, 244, 240), a1))
            d.ellipse((cx - 48, cy - 48, cx + 48, cy - 8), fill=mix(BG, (90, 52, 28), a1))
            d.arc((cx + 44, cy - 8, cx + 92, cy + 44), 270, 90, fill=mix(BG, (245, 244, 240), a1), width=10)
            # steam
            if t > 0.3:
                for k in range(3):
                    sx = cx - 16 + k * 16
                    sy = cy - 70 - int(18 * math.sin(t * 3 + k))
                    d.arc((sx, sy, sx + 18, sy + 36), 200, 340, fill=mix(BG, MUTED, a1), width=3)
            if p > 0.82:
                d.text((cx, cy - 110), "桌边", font=sub_f, fill=mix(BG, YELLOW, appear(t, duration * 0.7)), anchor="mm")
        d.text((W // 2, 1680), "贴着桌面滑，不是飘", font=sub_f, fill=mix(BG, MUTED, appear(t, 0.4)), anchor="mm")
        out.append(img)
    return out


def b_law(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, sub_f = font(68), font(52), font(36)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "02 定律")
        a0 = appear(t, 0.02)
        d.text((W // 2, 280 + int(lerp(22, 0, a0))), "摩擦力归零", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        a1 = appear(t, 0.28)
        if a1 > 0.04:
            rounded(d, (120, 460, 500, 780), 32, mix(BG, CARD, a1))
            d.text((310, 580), "飘", font=card_f, fill=mix(CARD, WHITE, a1), anchor="mm")
            st = appear(t, 0.7, 0.26)
            if st > 0.04:
                d.line([(180, 580), (int(lerp(180, 440, st)), 580)], fill=mix(CARD, RED, st), width=12)
                d.text((310, 700), "离地 ✕", font=sub_f, fill=mix(CARD, RED, st), anchor="mm")
            rounded(d, (580, 460, 960, 780), 32, mix(BG, CARD, a1))
            d.text((770, 580), "滑", font=card_f, fill=mix(CARD, MINT, a1), anchor="mm")
            if t >= 1.05:
                d.text((770, 700), "贴地 ✓", font=sub_f, fill=mix(CARD, YELLOW, appear(t, 1.05)), anchor="mm")
        if t >= 1.4:
            a = appear(t, 1.4)
            d.text((W // 2, 980), "只改这一条", font=title_f, fill=mix(BG, YELLOW, a), anchor="mm")
            d.text((W // 2, 1100), "东西必须贴着地走", font=sub_f, fill=mix(BG, MUTED, a), anchor="mm")
        out.append(img)
    return out


def b_car(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, sub_f = font(58), font(36)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "03 后果一")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(20, 0, a0))), "停着的车开始溜", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        # road
        rounded(d, (60, 1180, 1020, 1380), 20, mix(BG, (28, 30, 36), appear(t, 0.15)))
        d.line([(80, 1280), (1000, 1280)], fill=mix(BG, (90, 92, 98), appear(t, 0.2)), width=6)
        p = ease_out(min(1.0, t / max(0.01, duration - 0.2)))
        cx = int(lerp(220, 820, p))
        cy = 1120
        # car body sliding, wheels not rotating much — it's sliding
        rounded(d, (cx - 150, cy - 70, cx + 150, cy + 50), 28, mix(BG, (230, 232, 236), appear(t, 0.2)))
        rounded(d, (cx - 70, cy - 130, cx + 110, cy - 60), 18, mix(BG, (180, 200, 210), appear(t, 0.2)))
        d.ellipse((cx - 110, cy + 20, cx - 50, cy + 80), fill=mix(BG, (40, 40, 44), appear(t, 0.2)))
        d.ellipse((cx + 50, cy + 20, cx + 110, cy + 80), fill=mix(BG, (40, 40, 44), appear(t, 0.2)))
        # motion streaks on ground, not in air
        if p > 0.15:
            for k in range(4):
                x0 = cx - 180 - k * 36
                d.line([(x0, cy + 70), (x0 + 24, cy + 70)], fill=mix(BG, YELLOW, 0.5), width=4)
        d.text((W // 2, 1560), "没人开，贴地滑走", font=sub_f, fill=mix(BG, MUTED, appear(t, 0.45)), anchor="mm")
        out.append(img)
    return out


def b_collapse(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, sub_f = font(56), font(44), font(34)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "04 后果二三")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(18, 0, a0))), "堆好的，自己塌", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        # stack -> pile
        fall = ease_out(min(1.0, max(0.0, (t - 0.35) / 1.1)))
        boxes = [(0, (200, 90, 40)), (1, (90, 160, 200)), (2, (200, 70, 70))]
        for idx, col in boxes:
            x = 220 + idx * 40
            y_stack = 720 - idx * 110
            y = int(lerp(y_stack, 980 + idx * 28, fall))
            x2 = int(lerp(x, 180 + idx * 160, fall))
            rot_shift = int(lerp(0, 30 * (idx - 1), fall))
            rounded(d, (x2 + rot_shift, y, x2 + 240 + rot_shift, y + 100), 16, mix(BG, col, appear(t, 0.15)))
        a1 = appear(t, 1.35)
        if a1 > 0.04:
            rounded(d, (140, 1280, 940, 1580), 32, mix(BG, CARD, a1))
            d.text((W // 2, 1380), "绳结", font=sub_f, fill=mix(CARD, MUTED, a1), anchor="mm")
            # knot untying
            open_p = ease_out(min(1.0, max(0.0, (t - 1.5) / 0.8)))
            cy = 1480
            d.arc((360, cy - 50, 520, cy + 50), 0, 360, fill=mix(CARD, YELLOW, a1), width=10)
            d.arc((560, cy - 50, 720, cy + 50), 0, 360, fill=mix(CARD, YELLOW, a1), width=10)
            if open_p > 0.2:
                d.line([(400, cy), (int(lerp(400, 280, open_p)), cy + int(40 * open_p))], fill=mix(CARD, MINT, a1), width=10)
                d.line([(680, cy), (int(lerp(680, 800, open_p)), cy + int(40 * open_p))], fill=mix(CARD, MINT, a1), width=10)
                d.text((W // 2, 1548), "自己松开", font=card_f, fill=mix(CARD, WHITE, open_p), anchor="mm")
        out.append(img)
    return out


def b_freeze(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, sub_f, big = font(58), font(36), font(96)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "05 回报")
        remain = max(0.0, 1.0 - t / max(0.2, duration * 0.45))
        a0 = appear(t, 0.02)
        if remain > 0.05 and t < duration * 0.48:
            d.text((W // 2, 320), "倒计时", font=sub_f, fill=mix(BG, MUTED, a0), anchor="mm")
            d.text((W // 2, 480), f"0:{int(remain * 3):02d}", font=big, fill=mix(BG, YELLOW, a0), anchor="mm")
        else:
            a = appear(t, duration * 0.45)
            d.text((W // 2, 280 + int(lerp(20, 0, a))), "三分钟到", font=title_f, fill=mix(BG, WHITE, a), anchor="mm")
            d.text((W // 2, 400), "摩擦力回来了", font=sub_f, fill=mix(BG, MUTED, a), anchor="mm")
            # frozen street silhouettes
            rounded(d, (90, 560, 990, 1500), 36, mix(BG, CARD, a))
            d.rectangle((90, 1280, 990, 1500), fill=mix(CARD, (18, 20, 26), a))
            # tilted car, spilled boxes, cup at edge
            cx, cy = 280, 1100
            d.polygon([(cx, cy), (cx + 180, cy - 40), (cx + 210, cy + 70), (cx - 20, cy + 90)], fill=mix(CARD, (200, 204, 210), a))
            d.ellipse((cx + 10, cy + 70, cx + 70, cy + 130), fill=mix(CARD, (50, 50, 54), a))
            d.ellipse((cx + 130, cy + 50, cx + 190, cy + 110), fill=mix(CARD, (50, 50, 54), a))
            for k, col in enumerate([(200, 90, 40), (90, 160, 200), (200, 70, 70)]):
                rounded(d, (560 + k * 30, 980 + k * 40, 760 + k * 40, 1080 + k * 36), 12, mix(CARD, col, a))
            d.ellipse((820, 1180, 900, 1260), fill=mix(CARD, (90, 52, 28), a))
            d.text((W // 2, 1400), "冻在滑完的样子", font=title_f, fill=mix(CARD, YELLOW, a), anchor="mm")
        out.append(img)
    return out


def render_brolls(spans: list[tuple[float, float]]) -> None:
    # map phrase index -> broll duration
    jobs = [
        (1, "B-咖啡滑.mp4", b_coffee),
        (3, "B-定律.mp4", b_law),
        (4, "B-车溜.mp4", b_car),
        (6, "B-塌摊.mp4", b_collapse),
        (7, "B-冻住.mp4", b_freeze),
    ]
    out = ROOT / "broll"
    out.mkdir(exist_ok=True)
    for idx, name, fn in jobs:
        dur = max(1.2, spans[idx][1] - spans[idx][0] + 0.06)
        print("broll", name, f"{dur:.2f}s")
        frames_to_mp4(fn(dur), out / name)


def render_arolls() -> None:
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    for pose, name in (("wave", "A-挥手.mp4"), ("shrug", "A-摊手.mp4"), ("point", "A-指向.mp4")):
        dest = assets / name
        if dest.exists() and dest.stat().st_size > 8000:
            print("reuse", dest)
            continue
        print("aroll", name)
        render_aroll(pose, dest, 3.4)


# ---------- captions ----------
def render_caps(spans: list[tuple[float, float]], duration: float) -> None:
    cues = []
    for i, (kind, _src, _close, lines) in enumerate(SHOT_META):
        if kind == "A" and lines:
            cues.append((spans[i][0], spans[i][1], lines))
    shutters = []
    colors = [MINT, WHITE, YELLOW, MINT, YELLOW, MINT, YELLOW]
    prev = None
    for i, (kind, *_rest) in enumerate(SHOT_META):
        if prev is not None and prev != kind:
            shutters.append((spans[i][0], colors[i % len(colors)]))
        prev = kind
    eyebrows = []
    a_i = 0
    for i, (kind, *_rest) in enumerate(SHOT_META):
        if kind == "A":
            a_i += 1
            eyebrows.append((spans[i][0], spans[i][1], f"A-ROLL / {a_i:02d}"))

    n = max(1, round(duration * FPS))
    dest = ROOT / "shots" / "caption_layer.mov"
    dest.parent.mkdir(parents=True, exist_ok=True)

    def frame_at(t: float) -> Image.Image:
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        label = next((text for s, e, text in eyebrows if s <= t < e), None)
        if label:
            d.rectangle((76, 88, 120, 92), fill=(126, 224, 197, 230))
            d.text((136, 78), label, font=font(22), fill=(90, 98, 108, 220))
        lines = next((ln for s, e, ln in cues if s <= t < e), None)
        if lines:
            fnt = font(56 if len(lines) == 1 else 50)
            dummy = ImageDraw.Draw(img)
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
            y = 168
            pill = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
            pd = ImageDraw.Draw(pill)
            pd.rounded_rectangle((0, 0, box_w - 1, box_h - 1), radius=28, fill=(22, 24, 28, 214))
            pd.rectangle((10, 14, 20, box_h - 14), fill=(126, 224, 197, 235))
            for j, line in enumerate(lines):
                pd.text((box_w / 2 + 4, pad_y + line_h * j), line, font=fnt, fill=(245, 247, 250, 255), anchor="mt")
            shadow = pill.filter(ImageFilter.GaussianBlur(8))
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sh.alpha_composite(shadow, (x0, y + 4))
            img.alpha_composite(sh)
            img.alpha_composite(pill, (x0, y))
        for start, color in shutters:
            dt = t - start
            if 0 <= dt <= 0.16:
                p = dt / 0.16
                if p < 0.5:
                    ww = max(2, int(W * p * 2))
                    xx = 0
                else:
                    ww = max(2, int(W * (1 - (p - 0.5) * 2)))
                    xx = W - ww
                layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(layer).rectangle((xx, 0, xx + ww, H), fill=(*color, 235))
                img = Image.alpha_composite(img, layer)
        return img

    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "qtrle", "-pix_fmt", "argb", str(dest),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    for i in range(n):
        proc.stdin.write(frame_at(i / FPS).tobytes())
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(err[-2500:])
    print("caps", dest, n)


def cut_shot(src: Path, dur: float, dest: Path, kind: str, close: bool = False) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    src_dur = max(0.01, probe(src))
    if kind == "A" and close:
        vf = f"scale=1380:2454,crop={W}:{H}:150:60,fps={FPS},setsar=1,format=yuv420p"
    elif kind == "A":
        vf = f"scale=1188:2112,crop={W}:{H}:54:105,fps={FPS},setsar=1,format=yuv420p"
    else:
        vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},setsar=1,format=yuv420p"
    if kind == "A" and dur > src_dur + 0.05:
        vf = f"setpts=PTS*{dur / src_dur:.6f},{vf}"
    elif dur > src_dur + 0.02:
        vf = f"{vf},tpad=stop_mode=clone:stop_duration={dur - src_dur:.3f}"
    run(["ffmpeg", "-y", "-i", str(src), "-t", f"{dur:.3f}", "-vf", vf, "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18", str(dest)])


def assemble(spans: list[tuple[float, float]]) -> Path:
    duration = spans[-1][1]
    shots = []
    for i, (kind, src, close, _lines) in enumerate(SHOT_META):
        s, e = spans[i]
        shots.append({"id": f"S{i+1:02d}", "kind": kind, "start": s, "end": e, "src": src, "close": close, "line": PHRASES[i]})
    data = {
        "audio": "audio/vo-full.wav",
        "duration": duration,
        "fps": FPS,
        "size": [W, H],
        "shots": shots,
    }
    (ROOT / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    shots_dir = ROOT / "shots"
    shots_dir.mkdir(exist_ok=True)
    parts = []
    for shot in shots:
        dest = shots_dir / f"{shot['id']}.mp4"
        print(shot["id"], shot["kind"], f"{shot['end']-shot['start']:.2f}s")
        cut_shot(ROOT / shot["src"], shot["end"] - shot["start"], dest, shot["kind"], bool(shot.get("close")))
        parts.append(dest)

    lst = shots_dir / "concat.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    concat = shots_dir / "video_only.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), str(concat)])

    caps = shots_dir / "caption_layer.mov"
    burned = shots_dir / "video_subs.mp4"
    if caps.exists():
        run([
            "ffmpeg", "-y", "-i", str(concat), "-i", str(caps),
            "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an", str(burned),
        ])
    else:
        burned = concat

    # quiet pad
    bgm = ROOT / "audio" / "bgm.wav"
    if not bgm.exists():
        run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=196:sample_rate=44100",
            "-t", f"{duration + 1:.2f}",
            "-af", "volume=0.04,lowpass=f=380,alimiter=limit=0.2",
            "-ac", "2", "-c:a", "pcm_s16le", str(bgm),
        ])
    audio = ROOT / "audio" / "vo-full.wav"
    final = ROOT / "final" / f"{NAME}.mp4"
    final.parent.mkdir(exist_ok=True)
    # VO + quiet pad only. Cut SFX omitted: chained aevalsrc+adelay fails on this ffmpeg.
    run([
        "ffmpeg", "-y", "-i", str(burned), "-i", str(audio), "-i", str(bgm),
        "-filter_complex",
        "[1:a]loudnorm=I=-16:LRA=11:TP=-1.5,aformat=sample_rates=44100:channel_layouts=stereo[vo];"
        "[2:a]adelay=800|800,volume=0.16,highpass=f=140[bg];"
        "[vo][bg]amix=inputs=2:duration=first:dropout_transition=2,alimiter=limit=0.95[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        str(final),
    ])
    out_dir = ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    dest = out_dir / f"{NAME}.mp4"
    run(["ffmpeg", "-y", "-i", str(final), "-c", "copy", str(dest)])
    run(["ffmpeg", "-y", "-i", str(final), "-c", "copy", str(ROOT / f"00_最终成片_{NAME}.mp4")])
    staging = Path("/workspace/成片") / f"04-{NAME}.mp4"
    staging.parent.mkdir(exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(final), "-c", "copy", str(staging)])
    print("FINAL", staging, "dur", probe(staging))
    return staging


def make_cover(spans: list[tuple[float, float]]) -> None:
    img = new_b_bg()
    d = ImageDraw.Draw(img)
    rounded(d, (90, 160, 990, 620), 36, CARD)
    d.text((W // 2, 280), "咖啡自己滑向桌边", font=font(58), fill=WHITE, anchor="mm")
    d.text((W // 2, 400), "摩擦力归零 · 只给三分钟", font=font(36), fill=YELLOW, anchor="mm")
    d.text((W // 2, 500), "贴地滑，不是飘", font=font(40), fill=MINT, anchor="mm")
    # cup
    d.rectangle((470, 980, 610, 1180), fill=CREAM)
    d.ellipse((470, 930, 610, 1010), fill=(90, 52, 28))
    d.arc((600, 1020, 700, 1120), 270, 90, fill=CREAM, width=14)
    dest = ROOT / "00_封面_咖啡自己滑向桌边.jpg"
    img.save(dest, quality=92)
    Path("/workspace/成片").mkdir(exist_ok=True)
    img.save(Path("/workspace/成片") / "04-封面-咖啡自己滑向桌边.jpg", quality=92)
    print("cover", dest)


def write_status(duration: float) -> None:
    data = {
        "schema_version": 1,
        "project_name": "04_咖啡自己滑向桌边",
        "video_type": "普通短视频",
        "status": "已交付",
        "current_stage": "核验并交付",
        "topic": 4,
        "source": "选题库.md 第002号 / topics.md #4",
        "duration_s": round(duration, 3),
        "size": [W, H],
        "fps": FPS,
        "deliverables": {
            "final_video": f"/workspace/成片/04-{NAME}.mp4",
            "project_video": f"00_最终成片_{NAME}.mp4",
        },
        "updated_at": "2026-09-11",
    }
    (ROOT / "项目状态.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    os.chdir(ROOT)
    spans = asyncio.run(make_voice())
    duration = spans[-1][1]
    render_arolls()
    render_brolls(spans)
    render_caps(spans, duration)
    assemble(spans)
    make_cover(spans)
    write_status(duration)
    print("done", duration)


if __name__ == "__main__":
    main()
