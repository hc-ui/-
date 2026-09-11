#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 46 加长：杂务按六十分及格。云端 A-roll + B-roll，不是短剧。覆盖 10.5s 短切。"""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 24
NAME = "杂务按六十分及格"
FULL_TITLE = "杂务按六十分及格交付"
STAGED_NAME = "46-杂务按六十分及格.mp4"
VOICE = "zh-CN-YunyangNeural"
_LOCAL_ASSETS = ROOT.parent / "06" / "assets"
_WS_ASSETS = Path("/workspace/.abroll-cloud/06/assets")
ASSET_SRC = _LOCAL_ASSETS if (_LOCAL_ASSETS / "V-挥手.mp4").exists() else _WS_ASSETS
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_REG = "/tmp/NotoSansSC-Regular.otf"
FONT_FALLBACK = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

BG = (11, 13, 18)
CARD = (24, 28, 38)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
CREAM = (245, 247, 250)
RED = (255, 118, 118)
INK = (22, 24, 28)
LEAD = 0.28
N_PHRASES = 18
DUR_MIN, DUR_MAX, DUR_LO, DUR_HI = 30.0, 60.0, 40.0, 50.0


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout)[-2500:])


def probe_dur(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True,
    ).strip()
    return float(out)


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    for path in ((FONT_BD if bold else FONT_REG), FONT_FALLBACK):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def ease_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def appear(t: float, start: float, dur: float = 0.32) -> float:
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
    d.ellipse((-220, -280, 720, 560), fill=(16, 42, 38))
    d.ellipse((480, 1180, 1400, 2100), fill=(42, 32, 16))
    overlay = overlay.filter(ImageFilter.GaussianBlur(110))
    return Image.blend(img, overlay, 0.58)


def tag(draw: ImageDraw.ImageDraw, t: float, label: str) -> None:
    a = appear(t, 0.0, 0.22)
    if a <= 0:
        return
    fnt = font(30)
    tw, th = text_wh(draw, label, fnt)
    x, y = 84, 88
    rounded(draw, (x - 22, y - 14, x + tw + 22, y + th + 12), 22, mix(BG, (20, 42, 38), a))
    draw.text((x, y), label, font=fnt, fill=mix(BG, MINT, a))


def kt(duration: float, t_ref: float) -> float:
    """Stretch keyframes designed for ~3.2s onto the real B-roll length, cap 2.1x."""
    scale = min(2.1, max(1.0, duration / 3.2))
    return t_ref * scale


def strike_line(draw: ImageDraw.ImageDraw, box, progress: float, color) -> None:
    x0, y0, x1, y1 = box
    if progress <= 0.04:
        return
    mid = (y0 + y1) / 2
    x_end = lerp(x0 + 24, x1 - 24, min(1.0, progress))
    draw.line([(x0 + 24, mid), (x_end, mid)], fill=color, width=10)


def jagged_tear(draw: ImageDraw.ImageDraw, x: int, y0: int, y1: int, phase: float, color) -> None:
    pts = []
    steps = 14
    for i in range(steps + 1):
        yy = lerp(y0, y1, i / steps)
        wobble = 10 * math.sin(i * 1.7 + phase * 6.0) + (8 if i % 2 else -8)
        pts.append((x + wobble, yy))
    if len(pts) >= 2:
        draw.line(pts, fill=color, width=6)


def render_to_mp4(frame_fn, duration: float, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    n = max(1, round(duration * FPS))
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18",
        str(dest),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    mid = None
    for i in range(n):
        im = frame_fn(i / FPS)
        if i == n // 2:
            mid = im.copy()
        proc.stdin.write(im.convert("RGB").tobytes())
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(err[-2000:])
    if mid is not None:
        mid.save(dest.with_suffix(".jpg"), quality=92)


def frame_b_rent(t: float, duration: float) -> Image.Image:
    img = new_bg()
    d = ImageDraw.Draw(img)
    tag(d, t, "对 · 租金")
    a0 = appear(t, kt(duration, 0.02))
    d.text((W // 2, 236 + int(lerp(16, 0, a0))), "当成换工位的租金", font=font(54), fill=mix(BG, WHITE, a0), anchor="mm")

    a1 = appear(t, kt(duration, 0.18))
    if a1 > 0.04:
        y = 330 + int(lerp(22, 0, a1))
        rounded(d, (80, y, 500, y + 520), 32, mix(BG, (22, 40, 36), a1))
        d.text((290, y + 80), "租", font=font(30), fill=mix(CARD, MUTED, a1), anchor="mm")
        d.text((290, y + 200), "租金", font=font(72), fill=mix(CARD, MINT, a1), anchor="mm")
        d.text((290, y + 320), "交完就行", font=font(40), fill=mix(CARD, WHITE, a1), anchor="mm")
        d.text((290, y + 420), "换工位自由", font=font(32), fill=mix(CARD, YELLOW, a1), anchor="mm")

        rounded(d, (580, y, 1000, y + 520), 32, mix(BG, CARD, a1))
        d.text((790, y + 80), "主", font=font(30), fill=mix(CARD, MUTED, a1), anchor="mm")
        d.text((790, y + 200), "主业", font=font(72), fill=mix(CARD, RED, a1), anchor="mm")
        d.text((790, y + 320), "别把杂务做成", font=font(36), fill=mix(CARD, WHITE, a1), anchor="mm")
        strike_line(d, (640, y + 250, 940, y + 390), appear(t, kt(duration, 0.95), 0.28), mix(CARD, RED, a1))

        tear = appear(t, kt(duration, 0.55), 0.30)
        if tear > 0.04:
            jagged_tear(d, 540, y + 20, y + 500, t, mix(BG, YELLOW, tear))

    punch = appear(t, kt(duration, 1.45), 0.24)
    if punch > 0.04:
        y = 920 + int(lerp(22, 0, punch))
        rounded(d, (120, y, 960, y + 200), 28, mix(BG, (18, 42, 36), punch))
        d.text((W // 2, y + 100), "别交成主业", font=font(56), fill=mix(BG, MINT, punch), anchor="mm")
    return img


def frame_b_sixty(t: float, duration: float) -> Image.Image:
    img = new_bg()
    d = ImageDraw.Draw(img)
    tag(d, t, "对 · 六十分")
    a0 = appear(t, kt(duration, 0.02))
    d.text((W // 2, 228 + int(lerp(16, 0, a0))), "六十分就过", font=font(58), fill=mix(BG, WHITE, a0), anchor="mm")

    a1 = appear(t, kt(duration, 0.16))
    if a1 > 0.04:
        y = 300 + int(lerp(20, 0, a1))
        rounded(d, (80, y, 1000, y + 560), 36, mix(BG, CARD, a1))
        d.text((W // 2, y + 64), "行政杂务", font=font(34), fill=mix(CARD, MUTED, a1), anchor="mm")
        score_a = appear(t, kt(duration, 0.40), 0.40)
        score = int(lerp(12, 60, score_a))
        d.text((340, y + 230), f"{score}", font=font(150), fill=mix(CARD, MINT if score >= 60 else YELLOW, a1), anchor="mm")
        d.text((340, y + 360), "分 · 及格", font=font(36), fill=mix(CARD, MUTED, a1), anchor="mm")

        ninety = appear(t, kt(duration, 0.70), 0.24)
        if ninety > 0.04:
            rounded(d, (620, y + 120, 940, y + 300), 22, mix(CARD, (42, 24, 22), ninety))
            d.text((780, y + 180), "90", font=font(64), fill=mix(CARD, RED, ninety), anchor="mm")
            d.text((780, y + 250), "别追求", font=font(30), fill=mix(CARD, MUTED, ninety), anchor="mm")
            strike_line(d, (640, y + 140, 920, y + 280), appear(t, kt(duration, 1.05), 0.26), mix(CARD, RED, ninety))

        stamp = appear(t, kt(duration, 1.15), 0.28)
        if stamp > 0.04:
            cx, cy = 820, y + 430
            col = mix(CARD, MINT, stamp)
            d.ellipse((cx - 80, cy - 80, cx + 80, cy + 80), outline=col, width=10)
            d.text((cx, cy), "过", font=font(68), fill=col, anchor="mm")

        d.text((340, y + 470), "不出差错即可", font=font(34), fill=mix(CARD, YELLOW, a1), anchor="mm")

    a2 = appear(t, kt(duration, 1.35))
    if a2 > 0.04:
        y = 900 + int(lerp(18, 0, a2))
        rounded(d, (80, y, 1000, y + 280), 28, mix(BG, (22, 40, 36), a2))
        d.text((200, y + 50), "卫生清单", font=font(30), fill=mix(CARD, MUTED, a2), anchor="lm")
        items = ["工位卫生", "收发快递", "盖章跑腿"]
        for j, item in enumerate(items):
            iy = y + 100 + j * 52
            rounded(d, (160, iy, 700, iy + 44), 10, mix(CARD, (18, 28, 26), a2))
            d.text((190, iy + 22), item, font=font(30), fill=mix(CARD, WHITE, a2), anchor="lm")
            chk = appear(t, kt(duration, 1.50 + j * 0.12), 0.18)
            if chk > 0.04:
                col = mix(CARD, MINT, chk)
                d.line([(720, iy + 24), (736, iy + 36), (768, iy + 10)], fill=col, width=6)
        faded = appear(t, kt(duration, 1.40), 0.20)
        if faded > 0.04:
            rounded(d, (800, y + 90, 970, y + 230), 16, mix(CARD, (36, 28, 26), faded))
            d.text((885, y + 140), "票据墙", font=font(28), fill=mix(CARD, MUTED, faded), anchor="mm")
            d.text((885, y + 190), "本条不拍", font=font(24), fill=mix(CARD, RED, faded), anchor="mm")

    punch = appear(t, kt(duration, 1.85), 0.22)
    if punch > 0.04:
        y = 1220 + int(lerp(16, 0, punch))
        rounded(d, (120, y, 960, y + 160), 26, mix(BG, (18, 42, 36), punch))
        d.text((W // 2, y + 80), "做完即止", font=font(52), fill=mix(BG, MINT, punch), anchor="mm")
    return img


def frame_b_honor(t: float, duration: float) -> Image.Image:
    img = new_bg()
    d = ImageDraw.Draw(img)
    tag(d, t, "错 · 评优")
    a0 = appear(t, kt(duration, 0.02))
    d.text((W // 2, 236 + int(lerp(16, 0, a0))), "别在杂务上评优", font=font(54), fill=mix(BG, WHITE, a0), anchor="mm")

    a1 = appear(t, kt(duration, 0.16))
    if a1 > 0.04:
        y = 330 + int(lerp(20, 0, a1))
        rounded(d, (80, y, 520, y + 440), 32, mix(BG, CARD, a1))
        d.text((300, y + 80), "评", font=font(30), fill=mix(CARD, MUTED, a1), anchor="mm")
        d.text((300, y + 180), "评优争先", font=font(44), fill=mix(CARD, YELLOW, a1), anchor="mm")
        d.text((300, y + 270), "情绪成本白投", font=font(32), fill=mix(CARD, MUTED, a1), anchor="mm")
        strike_line(d, (140, y + 140, 460, y + 220), appear(t, kt(duration, 0.80), 0.28), mix(CARD, RED, a1))
        xmark = appear(t, kt(duration, 1.00), 0.22)
        if xmark > 0.04:
            col = mix(CARD, RED, xmark)
            d.line([(230, y + 320), (370, y + 400)], fill=col, width=10)
            d.line([(370, y + 320), (230, y + 400)], fill=col, width=10)

    a2 = appear(t, kt(duration, 0.28))
    if a2 > 0.04:
        y = 330 + int(lerp(20, 0, a2))
        rounded(d, (560, y, 1000, y + 440), 32, mix(BG, (22, 40, 36), a2))
        d.text((780, y + 80), "走", font=font(30), fill=mix(CARD, MUTED, a2), anchor="mm")
        d.text((780, y + 180), "过了就走", font=font(44), fill=mix(CARD, MINT, a2), anchor="mm")
        d.text((780, y + 270), "不是你的战场", font=font(32), fill=mix(CARD, WHITE, a2), anchor="mm")
        emo = appear(t, kt(duration, 0.90), 0.30)
        bar_w = int(lerp(280, 40, emo))
        rounded(d, (620, y + 330, 940, y + 380), 12, mix(CARD, (36, 28, 26), a2))
        if bar_w > 4:
            rounded(d, (628, y + 338, 628 + bar_w, y + 372), 8, mix(CARD, YELLOW, a2))
        d.text((780, y + 410), "情绪撤走", font=font(28), fill=mix(CARD, MUTED, a2), anchor="mm")

    punch = appear(t, kt(duration, 1.50), 0.24)
    if punch > 0.04:
        y = 850 + int(lerp(20, 0, punch))
        rounded(d, (120, y, 960, y + 200), 28, mix(BG, (42, 24, 22), punch))
        d.text((W // 2, y + 100), "评优那分别投", font=font(52), fill=mix(BG, YELLOW, punch), anchor="mm")
    return img


def split_caption(line: str) -> list[str]:
    line = line.strip("。．. ")
    specials = {
        "杂务按六十分及格交付": ["杂务按六十分", "及格交付"],
        "行政杂务，当成换工位的租金": ["行政杂务", "当成换工位的租金"],
        "工位卫生，收发快递，盖章跑腿": ["工位卫生，收发快递", "盖章跑腿"],
        "标准只有一条，不出差错": ["标准只有一条", "不出差错"],
        "六十分就过，别追求九十分": ["六十分就过", "别追求九十分"],
        "多一分，就少一分给课题": ["多一分", "就少一分给课题"],
        "做完即止，清单勾上就停": ["做完即止", "清单勾上就停"],
        "评优那分别投，情绪也别跟进去": ["评优那分别投", "情绪也别跟进去"],
        "过了就走，把满分留给该满分的事": ["过了就走", "满分留给正事"],
        "是把力气留给正事": ["力气留给正事"],
    }
    if line in specials:
        return specials[line]
    if "，" in line and len(line) > 8:
        parts = [p for p in line.split("，") if p]
        if 1 < len(parts) <= 2:
            return parts
    return [line]


def ticks_to_sec(v: float) -> float:
    return float(v) / 10_000_000.0


def close_align(aligned: list[tuple[float, float, str]], duration: float) -> list[tuple[float, float, str]]:
    aligned[0] = (0.0, aligned[0][1], aligned[0][2])
    for i in range(1, len(aligned)):
        aligned[i] = (aligned[i - 1][1], aligned[i][1], aligned[i][2])
    last_s, _, last_p = aligned[-1]
    aligned[-1] = (last_s, duration, last_p)
    return [(round(s, 3), round(e, 3), p) for s, e, p in aligned]


def weight_align(phrases: list[str], duration: float) -> list[tuple[float, float, str]]:
    weights = [max(1, len(p.replace("，", "").replace("。", ""))) for p in phrases]
    total = sum(weights)
    t = 0.0
    aligned = []
    for phrase, w in zip(phrases, weights):
        span = duration * (w / total)
        aligned.append((t, t + span, phrase))
        t += span
    return close_align(aligned, duration)


def detect_sentence_cues(wav: Path, phrases: list[str], duration: float) -> list[tuple[float, float, str]]:
    proc = subprocess.run(
        ["ffmpeg", "-i", str(wav), "-af", "silencedetect=noise=-32dB:d=0.12", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", proc.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", proc.stderr)]
    silences: list[tuple[float, float]] = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else duration
        silences.append((s, min(e, duration)))
    speech: list[tuple[float, float]] = []
    cursor = 0.0
    for s, e in silences:
        if s - cursor >= 0.18:
            speech.append((cursor, s))
        cursor = max(cursor, e)
    if duration - cursor >= 0.18:
        speech.append((cursor, duration))
    speech = [(max(0.0, a), min(duration, b)) for a, b in speech if b - a >= 0.15]
    merged: list[tuple[float, float]] = []
    for a, b in speech:
        if merged and a - merged[-1][1] < 0.45:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    if len(merged) == len(phrases):
        cues = []
        for i, phrase in enumerate(phrases):
            start = 0.0 if i == 0 else merged[i][0]
            end = merged[i][1]
            cues.append((start, end, phrase))
        return close_align(cues, duration)
    return weight_align(phrases, duration)


async def synthesize_voice(text: str, mp3: Path) -> list[dict]:
    import edge_tts

    comm = edge_tts.Communicate(text, VOICE, rate="-4%")
    bounds: list[dict] = []
    with mp3.open("wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("SentenceBoundary", "WordBoundary"):
                bounds.append(chunk)
    return bounds


def make_voiceover() -> tuple[float, list[tuple[float, float, str]]]:
    text = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    phrases = [ln.strip() for ln in (ROOT / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(phrases) != N_PHRASES:
        raise SystemExit(f"need {N_PHRASES} phrases, got {len(phrases)}")
    audio_dir = ROOT / "audio"
    audio_dir.mkdir(exist_ok=True)
    mp3 = audio_dir / "vo-full.mp3"
    wav = audio_dir / "vo-full.wav"
    aligned: list[tuple[float, float, str]] | None = None
    if wav.exists() and wav.stat().st_size > 800 and (audio_dir / "vo-align.txt").exists():
        duration = probe_dur(wav)
        parsed: list[tuple[float, float, str]] = []
        for line in (audio_dir / "vo-align.txt").read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) >= 3:
                parsed.append((float(parts[0]), float(parts[1]), parts[2]))
        if len(parsed) == len(phrases):
            print("reuse VO", wav, duration)
            return duration, close_align(parsed, duration)
    try:
        bounds = asyncio.run(synthesize_voice(text, mp3))
        if mp3.stat().st_size < 800:
            raise RuntimeError("tts too small")
        run(["ffmpeg", "-y", "-i", str(mp3), "-ac", "1", "-ar", "44100", str(wav)])
        sentences = [b for b in bounds if b.get("type") == "SentenceBoundary"]
        if sentences and len(sentences) >= len(phrases):
            aligned = []
            for i, phrase in enumerate(phrases):
                b = sentences[i]
                start = ticks_to_sec(b["offset"])
                end = start + ticks_to_sec(b["duration"])
                aligned.append((start, end, phrase))
        print("TTS ok", wav, "cues", len(sentences))
    except Exception as exc:
        print("TTS failed, silencedetect fallback after retry:", exc)
        if not wav.exists() or wav.stat().st_size < 800:
            raise

    duration = probe_dur(wav)
    if aligned is None:
        aligned = detect_sentence_cues(wav, phrases, duration)
    else:
        aligned = close_align(aligned, duration)

    (audio_dir / "vo-align.txt").write_text(
        "".join(f"{s:.3f}\t{e:.3f}\t{p}\n" for s, e, p in aligned),
        encoding="utf-8",
    )
    vtt = ["WEBVTT", ""]
    for i, (s, e, p) in enumerate(aligned, 1):
        def ts(x: float) -> str:
            ms = int(round(x * 1000))
            return f"{ms // 3600000:02d}:{(ms // 60000) % 60:02d}:{(ms // 1000) % 60:02d}.{ms % 1000:03d}"

        vtt += [str(i), f"{ts(s)} --> {ts(e)}", p, ""]
    (audio_dir / "vo.vtt").write_text("\n".join(vtt), encoding="utf-8")
    (audio_dir / "cues.json").write_text(
        json.dumps([{"start": s, "end": e, "text": p} for s, e, p in aligned], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if duration < DUR_MIN or duration > DUR_MAX:
        raise SystemExit(f"VO duration {duration:.2f}s outside {DUR_MIN:.0f}–{DUR_MAX:.0f}s; rewrite phrases, do not pad")
    return duration, aligned


def build_timeline(cues: list[tuple[float, float, str]], duration: float) -> dict:
    recipe = json.loads((ROOT / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
    p = cues
    if len(p) != N_PHRASES:
        raise SystemExit(f"need {N_PHRASES} phrases, got {len(p)}")

    def edge(i: int) -> float:
        return float(p[i][1])

    b1 = max(edge(3) + 0.04, p[4][0] - LEAD)
    b1e = edge(6)
    a3 = edge(8)
    b2 = max(a3 + 0.04, p[9][0] - LEAD)
    b2e = edge(12)
    a5 = edge(13)
    b3 = max(a5 + 0.04, p[14][0] - LEAD)
    b3e = edge(16)

    shots = [
        {"id": "S01a", "kind": "A", "start": 0.0, "end": round(edge(0), 3), "src": "assets/V-挥手.mp4", "line": p[0][2], "close": True},
        {"id": "S01b", "kind": "A", "start": round(edge(0), 3), "end": round(edge(1), 3), "src": "assets/V-摊手.mp4", "line": p[1][2]},
        {"id": "S01c", "kind": "A", "start": round(edge(1), 3), "end": round(b1, 3), "src": "assets/V-指向.mp4", "line": p[2][2]},
        {"id": "S02", "kind": "B", "start": round(b1, 3), "end": round(b1e, 3), "src": "broll/B-租金不是主业.mp4", "line": p[4][2], "broll": "rent"},
        {"id": "S03", "kind": "A", "start": round(b1e, 3), "end": round(b2, 3), "src": "assets/V-摊手.mp4", "line": p[7][2]},
        {"id": "S04", "kind": "B", "start": round(b2, 3), "end": round(b2e, 3), "src": "broll/B-六十分就过.mp4", "line": p[9][2], "broll": "sixty"},
        {"id": "S05", "kind": "A", "start": round(b2e, 3), "end": round(b3, 3), "src": "assets/V-指向.mp4", "line": p[13][2]},
        {"id": "S06", "kind": "B", "start": round(b3, 3), "end": round(b3e, 3), "src": "broll/B-别评优.mp4", "line": p[14][2], "broll": "no_honor"},
        {"id": "S07", "kind": "A", "start": round(b3e, 3), "end": round(duration, 3), "src": "assets/V-点赞.mp4", "line": p[17][2]},
    ]
    for i, shot in enumerate(shots):
        if shot["end"] <= shot["start"] + 0.14:
            shot["end"] = min(duration, shot["start"] + 0.18)
            if i + 1 < len(shots):
                shots[i + 1]["start"] = shot["end"]
    for i in range(1, len(shots)):
        shots[i]["start"] = shots[i - 1]["end"]
    shots[-1]["end"] = round(duration, 3)
    for shot in shots:
        shot["start"] = round(float(shot["start"]), 3)
        shot["end"] = round(float(shot["end"]), 3)
        if shot["end"] <= shot["start"] + 0.12:
            raise SystemExit(f"bad shot {shot}")

    a_caps = [
        {"start": 0.0, "end": round(p[0][1], 3), "lines": ["大家好"]},
        {"start": round(p[1][0], 3), "end": round(min(p[1][1], shots[2]["start"]), 3), "lines": split_caption(p[1][2])},
        {"start": round(max(p[2][0], shots[2]["start"]), 3), "end": round(min(p[2][1], shots[3]["start"]), 3), "lines": ["不是偷懒"]},
        {"start": round(max(p[3][0], shots[2]["start"]), 3), "end": round(min(p[3][1], shots[3]["start"]), 3), "lines": ["力气留给正事"]},
        {"start": round(max(p[7][0], shots[4]["start"]), 3), "end": round(min(p[7][1], shots[5]["start"]), 3), "lines": split_caption(p[7][2])},
        {"start": round(max(p[8][0], shots[4]["start"]), 3), "end": round(shots[4]["end"], 3), "lines": ["这些都按六十分做"]},
        {"start": round(max(p[13][0], shots[6]["start"]), 3), "end": round(shots[6]["end"], 3), "lines": ["别把卫生做成作品集"]},
        {"start": round(shots[8]["start"], 3), "end": round(duration, 3), "lines": split_caption(p[17][2])},
    ]
    a_caps = [c for c in a_caps if c["end"] > c["start"] + 0.08]

    shutters = [
        {"start": shots[1]["start"], "color": list(CREAM)},
        {"start": shots[2]["start"], "color": list(CREAM)},
        {"start": shots[3]["start"], "color": list(MINT)},
        {"start": shots[4]["start"], "color": list(CREAM)},
        {"start": shots[5]["start"], "color": list(YELLOW)},
        {"start": shots[6]["start"], "color": list(CREAM)},
        {"start": shots[7]["start"], "color": list(RED)},
        {"start": shots[8]["start"], "color": list(MINT)},
    ]
    eyebrows = [
        {"start": shots[0]["start"], "end": shots[0]["end"], "text": "A-ROLL / 1a"},
        {"start": shots[1]["start"], "end": shots[1]["end"], "text": "A-ROLL / 1b"},
        {"start": shots[2]["start"], "end": shots[2]["end"], "text": "A-ROLL / 1c"},
        {"start": shots[4]["start"], "end": shots[4]["end"], "text": "A-ROLL / 03"},
        {"start": shots[6]["start"], "end": shots[6]["end"], "text": "A-ROLL / 05"},
        {"start": shots[8]["start"], "end": shots[8]["end"], "text": "A-ROLL / 07"},
    ]
    data = {
        "audio": "audio/vo-full.wav",
        "duration": round(duration, 3),
        "fps": FPS,
        "size": [W, H],
        "title": recipe["title"],
        "bgm": "audio/bgm.wav",
        "shots": shots,
        "a_caps": a_caps,
        "shutters": shutters,
        "eyebrows": eyebrows,
        "cover": {
            "title": recipe["cover_title"],
            "sub": recipe["cover_sub"],
            "line": recipe["cover_line"],
            "src": recipe["cover_src"],
        },
        "cue_map": {phrase: [round(s, 3), round(e, 3)] for s, e, phrase in cues},
        "b_lead_s": LEAD,
        "video_type": "普通短视频",
        "cut": "long-40s",
    }
    (ROOT / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


def make_bgm(duration: float) -> Path:
    dest = ROOT / "audio" / "bgm.wav"
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=174:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=220:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=261:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-filter_complex",
        "[0:a]volume=0.11[a];[1:a]volume=0.07[b];[2:a]volume=0.05[c];"
        "[a][b][c]amix=inputs=3:duration=longest,lowpass=f=480,alimiter=limit=0.32",
        "-ac", "2", "-ar", "44100", str(dest),
    ])
    return dest


def make_sfx(cuts: list[float], duration: float) -> Path:
    dest = ROOT / "audio" / "sfx.wav"
    if not cuts:
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={duration:.2f}", str(dest)])
        return dest
    delays = []
    parts = []
    for i, t in enumerate(cuts):
        ms = int(max(0.0, t) * 1000)
        delays.append(f"aevalsrc=0.012*sin(2*PI*880*t):s=44100:d=0.07,adelay={ms}|{ms}[s{i}]")
        parts.append(f"[s{i}]")
    fc = ";".join(delays) + f";{''.join(parts)}amix=inputs={len(parts)}:duration=longest,aformat=sample_rates=44100:channel_layouts=stereo"
    run(["ffmpeg", "-y", "-filter_complex", fc, "-t", f"{duration:.2f}", str(dest)])
    return dest


def draw_eyebrow(base: Image.Image, t: float, eyebrows) -> None:
    label = None
    for item in eyebrows:
        if item["start"] <= t < item["end"]:
            label = item["text"]
            break
    if not label:
        return
    d = ImageDraw.Draw(base)
    fnt = font(22)
    d.rectangle((76, 88, 120, 92), fill=(*MINT, 230))
    d.text((136, 78), label, font=fnt, fill=(90, 98, 108, 220))


def draw_pill(base: Image.Image, lines: list[str], y: int = 168) -> None:
    fnt = font(56 if len(lines) == 1 and max(len(s) for s in lines) <= 8 else 44)
    dummy = ImageDraw.Draw(base)
    widths, heights = [], []
    for line in lines:
        x0, y0, x1, y1 = dummy.textbbox((0, 0), line, font=fnt)
        widths.append(x1 - x0)
        heights.append(y1 - y0)
    tw = max(widths)
    line_h = max(heights) + 10
    pad_x, pad_y = 40, 22
    box_w = min(W - 80, tw + pad_x * 2)
    box_h = pad_y * 2 + line_h * len(lines) - 8
    x0 = (W - box_w) // 2
    pill = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle((0, 0, box_w - 1, box_h - 1), radius=28, fill=(22, 24, 28, 214))
    pd.rectangle((10, 14, 20, box_h - 14), fill=(*MINT, 235))
    for i, line in enumerate(lines):
        pd.text((box_w / 2 + 4, pad_y + line_h * i), line, font=fnt, fill=(*WHITE, 255), anchor="mt")
    shadow = pill.filter(ImageFilter.GaussianBlur(8))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.alpha_composite(shadow, (x0, y + 4))
    base.alpha_composite(sh)
    base.alpha_composite(pill, (x0, y))


def draw_shutter(base: Image.Image, t: float, shutters) -> Image.Image:
    for item in shutters:
        start, color = item["start"], tuple(item["color"])
        dt = t - start
        if 0 <= dt <= 0.16:
            p = dt / 0.16
            if p < 0.5:
                wdt = max(2, int(W * p * 2))
                x0 = 0
            else:
                wdt = max(2, int(W * (1 - (p - 0.5) * 2)))
                x0 = W - wdt
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(layer).rectangle((x0, 0, x0 + wdt, H), fill=(*color, 235))
            base = Image.alpha_composite(base, layer)
    return base


def render_captions(data: dict) -> Path:
    dest = ROOT / "shots" / "caption_layer.mov"
    dest.parent.mkdir(parents=True, exist_ok=True)
    duration = float(data["duration"])
    n = max(1, round(duration * FPS))
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "qtrle", "-pix_fmt", "argb", str(dest),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    for i in range(n):
        t = i / FPS
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_eyebrow(img, t, data["eyebrows"])
        for cue in data["a_caps"]:
            if cue["start"] <= t < cue["end"]:
                draw_pill(img, cue["lines"])
                break
        img = draw_shutter(img, t, data["shutters"])
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(err[-2500:])
    return dest


def cut_shot(src: Path, dur: float, dest: Path, kind: str, close: bool = False) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    src_dur = max(0.01, probe_dur(src))
    if kind == "A" and close:
        vf = f"scale=1380:2454,crop={W}:{H}:150:60,fps={FPS},setsar=1,format=yuv420p"
    elif kind == "A":
        vf = f"scale=1188:2112,crop={W}:{H}:54:105,fps={FPS},setsar=1,format=yuv420p"
    else:
        vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},setsar=1,format=yuv420p"
    cmd = ["ffmpeg", "-y"]
    if kind == "A" and dur > src_dur + 0.08:
        loops = max(0, int(math.ceil(dur / src_dur)) - 1)
        cmd += ["-stream_loop", str(loops)]
    cmd += [
        "-i", str(src), "-t", f"{dur:.3f}",
        "-vf", vf, "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18", str(dest),
    ]
    run(cmd)


def assemble(data: dict) -> Path:
    shots_dir = ROOT / "shots"
    shots_dir.mkdir(exist_ok=True)
    parts: list[Path] = []
    for shot in data["shots"]:
        dur = float(shot["end"]) - float(shot["start"])
        src = ROOT / shot["src"]
        dest = shots_dir / f"{shot['id']}.mp4"
        print(shot["id"], shot["kind"], f"{dur:.2f}s", src.name)
        cut_shot(src, dur, dest, shot["kind"], bool(shot.get("close")))
        parts.append(dest)

    lst = shots_dir / "concat.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    concat = shots_dir / "video_only.mp4"
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
        str(concat),
    ])

    caps = render_captions(data)
    burned = shots_dir / "video_subs.mp4"
    run([
        "ffmpeg", "-y", "-i", str(concat), "-i", str(caps),
        "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an", str(burned),
    ])

    audio = ROOT / data["audio"]
    bgm = ROOT / "audio" / "bgm.wav"
    sfx = ROOT / "audio" / "sfx.wav"
    cuts = [float(s["start"]) for s in data["shutters"]]
    make_sfx(cuts, float(data["duration"]))

    final = ROOT / f"00_最终成片_{NAME}.mp4"
    (ROOT / "final").mkdir(exist_ok=True)
    inputs = ["ffmpeg", "-y", "-i", str(burned), "-i", str(audio)]
    filters = ["[1:a]loudnorm=I=-16:LRA=11:TP=-1.5,aformat=sample_rates=44100:channel_layouts=stereo[vo]"]
    mix_ins = ["[vo]"]
    idx = 2
    if bgm.exists():
        inputs += ["-i", str(bgm)]
        filters.append(f"[{idx}:a]adelay=800|800,volume=0.16,highpass=f=140[bg]")
        mix_ins.append("[bg]")
        idx += 1
    if sfx.exists():
        inputs += ["-i", str(sfx)]
        filters.append(f"[{idx}:a]volume=0.28[sfx]")
        mix_ins.append("[sfx]")
        idx += 1
    filters.append(f"{''.join(mix_ins)}amix=inputs={len(mix_ins)}:duration=first:dropout_transition=2,alimiter=limit=0.95[a]")
    inputs += [
        "-filter_complex", ";".join(filters),
        "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        str(final),
    ]
    run(inputs)

    def safe_copy(src: Path, dest: Path) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.resolve() == src.resolve():
            return
        try:
            if dest.exists() and dest.samefile(src):
                return
        except OSError:
            pass
        shutil.copy2(src, dest)

    out = ROOT / "output" / f"{NAME}.mp4"
    safe_copy(final, out)
    safe_copy(final, ROOT / "final" / f"{NAME}.mp4")

    staged = Path("/workspace/成片") / STAGED_NAME
    safe_copy(final, staged)
    return staged


def make_cover() -> Path:
    data = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
    cover = data["cover"]
    char = Image.open(ROOT / cover["src"]).convert("RGB")
    scale = max(W / char.width, H / char.height)
    nw, nh = int(char.width * scale), int(char.height * scale)
    char = char.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - W) // 2
    y = int((nh - H) * 0.62)
    canvas = char.crop((x, y, x + W, y + H))
    overlay = Image.new("RGBA", (W, H), (11, 13, 18, 48))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((70, 80, 1010, 470), radius=36, fill=(22, 24, 28))
    d.text((W // 2, 160), "杂务按", font=font(48), fill=WHITE, anchor="mm")
    d.text((W // 2, 250), "六十分及格", font=font(64), fill=YELLOW, anchor="mm")
    d.text((W // 2, 340), cover["sub"], font=font(36), fill=MINT, anchor="mm")
    d.text((W // 2, 410), cover["line"], font=font(30), fill=MUTED, anchor="mm")
    dest = ROOT / f"00_封面_{NAME}.jpg"
    canvas.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    canvas.save(ROOT / "final" / "cover.jpg", quality=92)
    return dest


def copy_assets() -> None:
    dest = ROOT / "assets"
    dest.mkdir(exist_ok=True)
    for name in ("V-挥手.mp4", "V-摊手.mp4", "V-指向.mp4", "V-点赞.mp4", "A-角色-小灯-摊手.jpg"):
        src = ASSET_SRC / name
        if not src.exists():
            raise FileNotFoundError(src)
        target = dest / name
        if not target.exists() or target.stat().st_size != src.stat().st_size:
            shutil.copy2(src, target)


def write_docs(duration: float, staged: Path, data: dict) -> None:
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    sha = hashlib.sha256(vo.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    status = {
        "schema_version": 1,
        "project_name": "46_杂务按六十分及格_long",
        "video_type": "普通短视频",
        "episode": 46,
        "cut": "long-40s",
        "title": NAME,
        "full_title": FULL_TITLE,
        "source_note": "topics-batch3.md #46 · 备忘录第二节 2 钝感策略 · 加长覆盖 10.5s",
        "slug": "杂务按六十分及格交付",
        "voice": VOICE,
        "duration": round(duration, 3),
        "size": [W, H],
        "fps": FPS,
        "stage": "delivered",
        "status": "已交付",
        "current_stage": "核验并交付",
        "production_method": "白底小灯 A-roll + 黑底对照卡 B-roll + edge-tts Yunyang + FFmpeg",
        "script": {"path": "script/voiceover.txt", "sha256": sha, "phrases": N_PHRASES},
        "audio": {
            "path": "audio/vo-full.wav",
            "alignment_path": "audio/vo-align.txt",
            "voice_id": VOICE,
            "sample_rate": 44100,
            "channels": 1,
            "duration_ms": int(duration * 1000),
        },
        "deliverables": {
            "final_video": str(staged),
            "project_final": f"00_最终成片_{NAME}.mp4",
            "cover": f"00_封面_{NAME}.jpg",
        },
        "staged": f"成片/{STAGED_NAME}",
        "cloud_only": True,
        "windows_paths": False,
        "drive_upload": False,
        "not": "drama-pipeline / 仙侠连载 / C:D:G: / Drive 上传",
        "updated_at": now,
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    note = f"""# 46 · 杂务按六十分及格交付（加长）

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。

- **选题**：`topics-batch3.md` 第 46 条；备忘录第二节 2「钝感策略与情绪脱敏」
- **成片中转**：`成片/{STAGED_NAME}`（覆盖原 10.5s 短切）
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿目录**：`/workspace/.abroll-cloud/46-long/`
- **云端 only**：不写 `C:\\` / `D:\\` / `G:\\`，不传 Drive
- **避开**：成片 28 报销红线；成片 16 时间切片 / 秒回

钩子：杂务按六十分及格交付。  
诊断：不是偷懒，是把力气留给正事。  
例子：租金对主业；考卷 60 对 90；评优红叉对做完即止。  
收束：过了就走，满分留给正事。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {duration:.2f} 秒。镜头 {len(data["shots"])} 条，时间轴闭合。目标 40–50s，硬限 30–60s。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")


def _patch_md_duration(path: Path, duration: float) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    new_lines = []
    found = False
    for ln in text.splitlines():
        if STAGED_NAME in ln and ln.strip().startswith("|"):
            if re.search(r"\|\s*[\d.]+s\s*\|", ln):
                ln = re.sub(r"\|\s*[\d.]+s\s*\|", f"| {duration:.1f}s |", ln, count=1)
            if re.search(r"\|\s*[\d.]+s\s*\|", ln) is None and "10.5" in ln:
                ln = ln.replace("10.5s", f"{duration:.1f}s").replace("10.54s", f"{duration:.2f}s")
            found = True
        new_lines.append(ln)
    if found:
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def patch_index(duration: float) -> None:
    idx = Path("/workspace/成片/INDEX.md")
    line = f"| `{STAGED_NAME}` | {duration:.1f}s |"
    if idx.exists():
        text = idx.read_text(encoding="utf-8")
        new = []
        found = False
        for ln in text.splitlines():
            if STAGED_NAME in ln and ln.strip().startswith("|"):
                new.append(line)
                found = True
            else:
                new.append(ln)
        if not found:
            new.append(line)
        idx.write_text("\n".join(new) + "\n", encoding="utf-8")
    else:
        idx.write_text(
            "# 成片（可直接看）\n\n竖屏口播 1080×1920，H.264 + AAC。\n\n| 文件 | 时长 |\n|------|------|\n"
            + line + "\n",
            encoding="utf-8",
        )
    _patch_md_duration(Path("/workspace/.abroll-cloud/INDEX.chengpian.md"), duration)
    delivery = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if delivery.exists():
        text = delivery.read_text(encoding="utf-8")
        text = re.sub(
            rf"(\| `成片/{re.escape(STAGED_NAME)}` \| 1080×1920 h264\+aac 44\.1k stereo \| )[\d.]+s",
            rf"\g<1>{duration:.2f}s",
            text,
            count=1,
        )
        text = re.sub(
            rf"(\| 46 \| `{re.escape(STAGED_NAME)}` \| 已核验 )[\d.]+s",
            rf"\g<1>{duration:.1f}s",
            text,
            count=1,
        )
        delivery.write_text(text, encoding="utf-8")


def qa(staged: Path, data: dict) -> dict:
    qa_dir = ROOT / "qa"
    qa_dir.mkdir(exist_ok=True)
    probe = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(staged)],
        text=True,
    )
    (qa_dir / "ffprobe.json").write_text(probe, encoding="utf-8")
    (qa_dir / "ffprobe.txt").write_text(probe, encoding="utf-8")
    info = json.loads(probe)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next(s for s in info["streams"] if s["codec_type"] == "audio")
    null = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(staged), "-f", "null", "-"],
        capture_output=True, text=True,
    )
    decode_err = null.stderr or ""
    (qa_dir / "decode.txt").write_text(decode_err + "\n", encoding="utf-8")
    decode_clean = "\n".join(
        ln for ln in decode_err.splitlines()
        if "no version information available" not in ln
    ).strip()
    vol = subprocess.run(
        ["ffmpeg", "-i", str(staged), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    mean = maxv = None
    for line in (vol.stderr or "").splitlines():
        if "mean_volume" in line:
            mean = float(line.split(":")[-1].strip().split()[0])
        if "max_volume" in line:
            maxv = float(line.split(":")[-1].strip().split()[0])
    shots = data["shots"]
    overlap = any(shots[i]["end"] > shots[i + 1]["start"] + 0.001 for i in range(len(shots) - 1))
    gap = any(abs(shots[i]["end"] - shots[i + 1]["start"]) > 0.02 for i in range(len(shots) - 1))
    fps_num, fps_den = (v.get("r_frame_rate") or "24/1").split("/")
    fps = float(fps_num) / float(fps_den or 1)
    digest = hashlib.sha256(staged.read_bytes()).hexdigest()
    dur_s = float(info["format"]["duration"])
    report = {
        "project": "46_杂务按六十分及格_long",
        "strict": True,
        "cloud_only": True,
        "windows_paths": False,
        "drive_upload": False,
        "video_type": "普通短视频",
        "cut": "long-40s",
        "final": str(staged),
        "project_final": str(ROOT / f"00_最终成片_{NAME}.mp4"),
        "sha256": digest,
        "bytes": staged.stat().st_size,
        "video": {
            "codec": v.get("codec_name"),
            "width": int(v.get("width", 0)),
            "height": int(v.get("height", 0)),
            "fps": fps,
            "pix_fmt": v.get("pix_fmt"),
            "duration_s": dur_s,
        },
        "audio": {
            "codec": a.get("codec_name"),
            "sample_rate": int(a.get("sample_rate", 0)),
            "channels": int(a.get("channels", 0)),
            "mean_volume_db": mean,
            "max_volume_db": maxv,
        },
        "timeline": {
            "segments": len(shots),
            "overlap": overlap,
            "gap": gap,
            "last_end_equals_audio": abs(shots[-1]["end"] - data["duration"]) < 0.05,
            "broll_lead_s": LEAD,
        },
        "duration_ok": DUR_MIN <= dur_s <= DUR_MAX,
        "duration_target": DUR_LO <= dur_s <= DUR_HI,
        "decode_null": null.returncode == 0 and not decode_clean,
        "ok": True,
    }
    report["ok"] = (
        report["video"]["width"] == 1080
        and report["video"]["height"] == 1920
        and abs(report["video"]["fps"] - 24) < 0.05
        and report["video"]["codec"] == "h264"
        and report["audio"]["codec"] == "aac"
        and report["audio"]["sample_rate"] == 44100
        and report["decode_null"]
        and not overlap
        and not gap
        and report["timeline"]["last_end_equals_audio"]
        and report["duration_ok"]
    )
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    copy_assets()
    duration, cues = make_voiceover()
    print("VO", duration)
    for row in cues:
        print(f"  {row[0]:6.3f}-{row[1]:6.3f}  {row[2]}")
    if not (DUR_MIN <= duration <= DUR_MAX):
        raise SystemExit(f"VO {duration:.2f}s not in {DUR_MIN:.0f}–{DUR_MAX:.0f}")
    make_bgm(duration)
    data = build_timeline(cues, duration)
    print("timeline shots", [(s["id"], s["start"], s["end"], s["kind"]) for s in data["shots"]])

    mapping = {
        "S02": ("B-租金不是主业.mp4", frame_b_rent),
        "S04": ("B-六十分就过.mp4", frame_b_sixty),
        "S06": ("B-别评优.mp4", frame_b_honor),
    }
    for sid, (fname, renderer) in mapping.items():
        shot = next(s for s in data["shots"] if s["id"] == sid)
        d = max(2.4, float(shot["end"]) - float(shot["start"]))
        print("render", fname, d)
        dur_b = d + 0.12
        render_to_mp4(lambda t, fn=renderer, dur=dur_b: fn(t, dur), dur_b, ROOT / "broll" / fname)

    make_cover()
    staged = assemble(data)
    dur = probe_dur(staged)
    write_docs(dur, staged, data)
    patch_index(dur)
    report = qa(staged, data)
    print("STAGED", staged, "dur", dur, "ok", report["ok"], "target", report.get("duration_target"))
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
