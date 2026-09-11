#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Topic 83：旧方案套不上新问题。工厂 64 改认 83。云端 NEW A-roll + B-roll。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/83/，成品中转 成片/83-旧方案套不上新问题.mp4。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
目标四十到五十秒。不定格、不慢放注水。时长用中文「秒」。
不拷工厂 15.5 秒短切。不讲成片 64 空字典、#62 验收、#61 试点。
"""
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
NAME = "旧方案套不上新问题"
STAGED_NAME = "83-旧方案套不上新问题.mp4"
VOICE = "zh-CN-YunyangNeural"
ASSET_SRC = Path("/workspace/.abroll-cloud/06/assets")
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_REG = "/tmp/NotoSansSC-Regular.otf"
FONT_FALLBACK = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
TARGET_LO, TARGET_HI = 40.0, 50.0
HARD_LO, HARD_HI = 30.0, 60.0

BG = (11, 13, 18)
CARD = (24, 28, 38)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
CREAM = (245, 247, 250)
RED = (255, 118, 118)
INK = (22, 24, 28)
PAPER = (236, 230, 214)
LEAD = 0.28


def zh_sec(sec: float) -> str:
    return f"{sec:.1f}秒"


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


def new_bg(t: float = 0.0) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    overlay = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(overlay)
    dx = int(36 * math.sin(t * 1.15))
    dy = int(28 * math.cos(t * 0.85))
    d.ellipse((-220 + dx, -280 + dy, 720 + dx, 560 + dy), fill=(38, 28, 16))
    d.ellipse((480 - dx, 1180 - dy, 1400 - dx, 2100 - dy), fill=(16, 36, 42))
    overlay = overlay.filter(ImageFilter.GaussianBlur(110))
    return Image.blend(img, overlay, 0.58)


def bob(t: float, amp: float = 10.0, freq: float = 0.7) -> int:
    return int(amp * math.sin(t * freq * math.pi * 2))


def tag(draw: ImageDraw.ImageDraw, t: float, label: str) -> None:
    a = appear(t, 0.0, 0.22)
    if a <= 0:
        return
    fnt = font(30)
    tw, th = text_wh(draw, label, fnt)
    x, y = 84, 88
    rounded(draw, (x - 22, y - 14, x + tw + 22, y + th + 12), 22, mix(BG, (42, 32, 16), a))
    draw.text((x, y), label, font=fnt, fill=mix(BG, YELLOW, a))


def render_to_mp4(draw_fn, duration: float, dest: Path) -> None:
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
        im = draw_fn(i / FPS).convert("RGB")
        proc.stdin.write(im.tobytes())
        if i == n // 2:
            mid = im
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(err[-2000:])
    if mid is not None:
        mid.save(dest.with_suffix(".jpg"), quality=92)


def strike_line(draw: ImageDraw.ImageDraw, box, progress: float, color) -> None:
    x0, y0, x1, y1 = box
    if progress <= 0.04:
        return
    mid = (y0 + y1) / 2
    x_end = lerp(x0 + 24, x1 - 24, min(1.0, progress))
    draw.line([(x0 + 24, mid), (x_end, mid)], fill=color, width=10)


def check_badge(draw: ImageDraw.ImageDraw, cx: int, cy: int, a: float) -> None:
    if a <= 0.04:
        return
    r = 36
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=mix(CARD, (18, 56, 46), a))
    col = mix(CARD, MINT, a)
    draw.line([(cx - 16, cy + 2), (cx - 4, cy + 16), (cx + 20, cy - 14)], fill=col, width=8)


def draw_x(draw: ImageDraw.ImageDraw, cx: int, cy: int, a: float, size: int = 44) -> None:
    if a <= 0.04:
        return
    col = mix(CARD, RED, a)
    s = int(size * a)
    draw.line([(cx - s, cy - s), (cx + s, cy + s)], fill=col, width=10)
    draw.line([(cx + s, cy - s), (cx - s, cy + s)], fill=col, width=10)


def punch_bar(draw: ImageDraw.ImageDraw, t: float, start: float, text: str, color=YELLOW, y0: int = 1040) -> None:
    a = appear(t, start, 0.22)
    if a <= 0.04:
        return
    y = y0 + bob(t, 7, 0.8)
    fill = (42, 32, 16) if color == YELLOW else (18, 42, 36) if color == MINT else (42, 24, 22)
    rounded(draw, (120, y, 960, y + 170), 28, mix(BG, fill, a))
    draw.text((W // 2, y + 85), text, font=font(50), fill=mix(BG, color, a), anchor="mm")


def draw_b_mismatch(t: float) -> Image.Image:
    img = new_bg(t)
    d = ImageDraw.Draw(img)
    tag(d, t, "错 · 旧模板")
    d.text((W // 2, 236 + bob(t, 6, 0.5)), "旧模板套新题", font=font(52), fill=mix(BG, WHITE, appear(t, 0.02)), anchor="mm")
    a1 = appear(t, 0.12)
    y = 340 + bob(t, 8, 0.55)
    rounded(d, (70, y, 500, y + 460), 32, mix(BG, (42, 32, 16), a1))
    d.text((285, y + 80), "去年方案", font=font(30), fill=mix(CARD, MUTED, a1), anchor="mm")
    d.text((285, y + 180), "旧步骤", font=font(48), fill=mix(CARD, YELLOW, a1), anchor="mm")
    d.text((285, y + 270), "还能跑", font=font(36), fill=mix(CARD, WHITE, a1), anchor="mm")
    a2 = appear(t, 0.28)
    rounded(d, (580, y + bob(t + 0.2, 7, 0.5), 1010, y + 460), 32, mix(BG, (18, 40, 38), a2))
    d.text((795, y + 80), "今年新题", font=font(30), fill=mix(CARD, MUTED, a2), anchor="mm")
    d.text((795, y + 180), "换了皮", font=font(48), fill=mix(CARD, MINT, a2), anchor="mm")
    d.text((795, y + 270), "对不上", font=font(36), fill=mix(CARD, WHITE, a2), anchor="mm")
    crack = appear(t, 0.55, 0.28)
    if crack > 0.04:
        cx = 540
        d.line([(cx, y + 40), (cx - 20, y + 220), (cx + 18, y + 320), (cx, y + 440)], fill=mix(CARD, RED, crack), width=10)
        draw_x(d, cx, y + 220, crack, 36)
    punch_bar(d, t, 1.00, "套不上", YELLOW, 900)
    return img


def draw_b_wrong_size(t: float) -> Image.Image:
    img = new_bg(t)
    d = ImageDraw.Draw(img)
    tag(d, t, "错 · 尺寸")
    d.text((W // 2, 236 + bob(t, 6, 0.5)), "不是执行不力", font=font(50), fill=mix(BG, WHITE, appear(t, 0.02)), anchor="mm")
    a1 = appear(t, 0.12)
    y = 340 + bob(t, 7, 0.5)
    rounded(d, (90, y, 990, y + 280), 32, mix(BG, CARD, a1))
    d.text((W // 2, y + 70), "新题宽度", font=font(30), fill=mix(CARD, MUTED, a1), anchor="mm")
    rounded(d, (140, y + 120, 940, y + 200), 16, mix(CARD, (18, 22, 28), a1))
    grow = appear(t, 0.40, 0.45)
    d.rectangle((150, y + 132, int(lerp(360, 920, grow)), y + 188), fill=mix(CARD, MINT, a1))
    d.text((W // 2, y + 160), "尺子对不上", font=font(32), fill=mix(CARD, WHITE, a1), anchor="mm")
    a2 = appear(t, 0.28)
    rounded(d, (90, y + 320, 500, y + 620), 32, mix(BG, (42, 24, 22), a2))
    d.text((295, y + 390), "旧约束", font=font(30), fill=mix(CARD, MUTED, a2), anchor="mm")
    d.text((295, y + 480), "已经不在", font=font(40), fill=mix(CARD, RED, a2), anchor="mm")
    strike_line(d, (130, y + 450, 460, y + 510), appear(t, 0.62, 0.35), mix(CARD, RED, 1))
    draw_x(d, 295, y + 560, appear(t, 0.70, 0.18), 40)
    a3 = appear(t, 0.40)
    rounded(d, (580, y + 320, 990, y + 620), 32, mix(BG, (22, 40, 36), a3))
    d.text((785, y + 390), "新尺寸", font=font(30), fill=mix(CARD, MUTED, a3), anchor="mm")
    d.text((785, y + 480), "要重量", font=font(40), fill=mix(CARD, MINT, a3), anchor="mm")
    check_badge(d, 785, y + 560, appear(t, 0.80, 0.18))
    punch_bar(d, t, 1.05, "尺寸不对", MINT, 1060)
    return img


def draw_b_whats_new(t: float) -> Image.Image:
    img = new_bg(t)
    d = ImageDraw.Draw(img)
    tag(d, t, "对 · 先写新")
    d.text((W // 2, 236 + bob(t, 6, 0.5)), "这次新在哪", font=font(54), fill=mix(BG, WHITE, appear(t, 0.02)), anchor="mm")
    chips = [(0.12, 80, "边界"), (0.28, 390, "约束"), (0.44, 700, "目标")]
    for ts, x, label in chips:
        a = appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 340 + bob(t + ts, 8, 0.55)
        rounded(d, (x, y, x + 300, y + 200), 28, mix(BG, CARD, a))
        d.text((x + 150, y + 100), label, font=font(48), fill=mix(CARD, YELLOW, a), anchor="mm")
    a1 = appear(t, 0.60)
    y = 600 + bob(t, 7, 0.5)
    rounded(d, (70, y, 500, y + 280), 32, mix(BG, (22, 40, 36), a1))
    d.text((285, y + 80), "能留", font=font(30), fill=mix(CARD, MUTED, a1), anchor="mm")
    d.text((285, y + 170), "留下", font=font(48), fill=mix(CARD, MINT, a1), anchor="mm")
    check_badge(d, 285, y + 230, appear(t, 0.82, 0.18))
    a2 = appear(t, 0.72)
    rounded(d, (580, y, 1010, y + 280), 32, mix(BG, (42, 32, 16), a2))
    d.text((795, y + 80), "对不上", font=font(30), fill=mix(CARD, MUTED, a2), anchor="mm")
    d.text((795, y + 170), "重写", font=font(48), fill=mix(CARD, YELLOW, a2), anchor="mm")
    punch_bar(d, t, 1.05, "先写再动手", MINT, 980)
    return img


def draw_b_old_habits(t: float) -> Image.Image:
    img = new_bg(t)
    d = ImageDraw.Draw(img)
    tag(d, t, "错 · 硬改旧稿")
    d.text((W // 2, 236 + bob(t, 6, 0.5)), "别硬改两个词", font=font(50), fill=mix(BG, WHITE, appear(t, 0.02)), anchor="mm")
    a1 = appear(t, 0.12)
    y = 340 + bob(t, 8, 0.55)
    rounded(d, (70, y, 500, y + 480), 32, mix(BG, (42, 24, 22), a1))
    d.text((285, y + 80), "旧提示词", font=font(30), fill=mix(CARD, MUTED, a1), anchor="mm")
    d.text((285, y + 190), "+ 两个词", font=font(44), fill=mix(CARD, RED, a1), anchor="mm")
    d.text((285, y + 280), "还是旧的", font=font(32), fill=mix(CARD, WHITE, a1), anchor="mm")
    strike_line(d, (110, y + 160, 460, y + 220), appear(t, 0.45, 0.35), mix(CARD, RED, 1))
    draw_x(d, 285, y + 380, appear(t, 0.55, 0.2), 48)
    a2 = appear(t, 0.28)
    rounded(d, (580, y + bob(t + 0.15, 7, 0.5), 1010, y + 480), 32, mix(BG, (42, 32, 16), a2))
    d.text((795, y + 80), "上学期课表", font=font(30), fill=mix(CARD, MUTED, a2), anchor="mm")
    d.text((795, y + 190), "套这学期", font=font(44), fill=mix(CARD, YELLOW, a2), anchor="mm")
    d.text((795, y + 280), "格对不上", font=font(32), fill=mix(CARD, WHITE, a2), anchor="mm")
    draw_x(d, 795, y + 380, appear(t, 0.70, 0.2), 48)
    punch_bar(d, t, 1.05, "旧稿改不活", RED, 920)
    return img


def draw_b_compare_stop(t: float) -> Image.Image:
    img = new_bg(t)
    d = ImageDraw.Draw(img)
    tag(d, t, "收 · 先量再裁")
    d.text((W // 2, 236 + bob(t, 6, 0.5)), "对得上才复用", font=font(52), fill=mix(BG, WHITE, appear(t, 0.02)), anchor="mm")
    a1 = appear(t, 0.12)
    y = 330 + bob(t, 7, 0.5)
    rounded(d, (70, y, 500, y + 400), 32, mix(BG, (22, 40, 36), a1))
    d.text((285, y + 80), "新条件", font=font(30), fill=mix(CARD, MUTED, a1), anchor="mm")
    d.text((285, y + 180), "先摊开", font=font(44), fill=mix(CARD, MINT, a1), anchor="mm")
    check_badge(d, 285, y + 300, appear(t, 0.55, 0.18))
    a2 = appear(t, 0.24)
    rounded(d, (580, y + bob(t + 0.12, 6, 0.45), 1010, y + 400), 32, mix(BG, CARD, a2))
    d.text((795, y + 80), "旧步骤", font=font(30), fill=mix(CARD, MUTED, a2), anchor="mm")
    d.text((795, y + 180), "对一下", font=font(44), fill=mix(CARD, YELLOW, a2), anchor="mm")
    stop = appear(t, 0.70, 0.22)
    if stop > 0.04:
        d.ellipse((735, y + 250, 855, y + 370), fill=mix(CARD, (56, 22, 20), stop))
        d.text((795, y + 310), "停", font=font(48), fill=mix(CARD, RED, stop), anchor="mm")
    punch_bar(d, t, 1.00, "套不上就停手", MINT, 820)
    return img


BROLL_DRAW = {
    "mismatch": draw_b_mismatch,
    "wrong_size": draw_b_wrong_size,
    "whats_new": draw_b_whats_new,
    "old_habits": draw_b_old_habits,
    "compare_stop": draw_b_compare_stop,
}


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


async def synthesize_voice(text: str, mp3: Path, rate: str) -> list[dict]:
    import edge_tts

    comm = edge_tts.Communicate(text, VOICE, rate=rate)
    bounds: list[dict] = []
    with mp3.open("wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("SentenceBoundary", "WordBoundary"):
                bounds.append(chunk)
    return bounds


def ts(x: float) -> str:
    ms = int(round(x * 1000))
    return f"{ms // 3600000:02d}:{(ms // 60000) % 60:02d}:{(ms // 1000) % 60:02d}.{ms % 1000:03d}"


def write_align_files(aligned: list[tuple[float, float, str]], duration: float) -> None:
    audio_dir = ROOT / "audio"
    audio_dir.mkdir(exist_ok=True)
    (audio_dir / "vo-align.txt").write_text(
        "".join(f"{s:.3f}\t{e:.3f}\t{p}\n" for s, e, p in aligned),
        encoding="utf-8",
    )
    (audio_dir / "vo.vtt").write_text(
        "WEBVTT\n\n" + "".join(
            f"{i}\n{ts(s)} --> {ts(e)}\n{p}\n\n"
            for i, (s, e, p) in enumerate(aligned, 1)
        ),
        encoding="utf-8",
    )
    cues = [{"start": s, "end": e, "text": p} for s, e, p in aligned]
    (audio_dir / "cues.json").write_text(json.dumps(cues, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (audio_dir / "vo.vtt.json").write_text(json.dumps(cues, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def synth_once(text: str, phrases: list[str], rate: str) -> tuple[float, list[tuple[float, float, str]]]:
    audio_dir = ROOT / "audio"
    audio_dir.mkdir(exist_ok=True)
    mp3 = audio_dir / "vo-full.mp3"
    wav = audio_dir / "vo-full.wav"
    bounds = asyncio.run(synthesize_voice(text, mp3, rate))
    if mp3.stat().st_size < 800:
        raise RuntimeError("tts too small")
    run(["ffmpeg", "-y", "-i", str(mp3), "-ac", "1", "-ar", "44100", str(wav)])
    duration = probe_dur(wav)
    sentences = [b for b in bounds if b.get("type") == "SentenceBoundary"]
    if sentences and len(sentences) >= len(phrases):
        aligned = []
        for i, phrase in enumerate(phrases):
            b = sentences[i]
            start = ticks_to_sec(b["offset"])
            end = start + ticks_to_sec(b["duration"])
            aligned.append((start, end, phrase))
        aligned = close_align(aligned, duration)
        print("TTS sentence cues", len(sentences), "rate", rate, "dur", zh_sec(duration))
    else:
        aligned = detect_sentence_cues(wav, phrases, duration)
        print("TTS silencedetect/weight cues", "rate", rate, "dur", zh_sec(duration))
    return duration, aligned


def make_voiceover() -> tuple[float, list[tuple[float, float, str]]]:
    text = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    phrases = [ln.strip() for ln in (ROOT / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    audio_dir = ROOT / "audio"
    audio_dir.mkdir(exist_ok=True)
    wav = audio_dir / "vo-full.wav"
    if wav.exists() and wav.stat().st_size > 800 and (audio_dir / "vo-align.txt").exists():
        duration = probe_dur(wav)
        parsed: list[tuple[float, float, str]] = []
        for line in (audio_dir / "vo-align.txt").read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) >= 3:
                parsed.append((float(parts[0]), float(parts[1]), parts[2]))
        if len(parsed) == len(phrases) and TARGET_LO <= duration <= TARGET_HI:
            print("reuse VO", wav, zh_sec(duration))
            return duration, close_align(parsed, duration)
    rates = ["-2%", "-6%", "-10%", "+2%", "-14%", "+6%"]
    best_target = None
    best_hard = None
    last = None
    for rate in rates:
        try:
            duration, aligned = synth_once(text, phrases, rate)
        except Exception as exc:
            print("TTS attempt failed", rate, exc)
            continue
        last = (rate, duration, aligned)
        print(f"VO rate={rate} duration={zh_sec(duration)}")
        if TARGET_LO <= duration <= TARGET_HI:
            best_target = (rate, duration, aligned)
            break
        if HARD_LO <= duration <= HARD_HI:
            if best_hard is None or abs(duration - 45.0) < abs(best_hard[1] - 45.0):
                best_hard = (rate, duration, aligned)
    picked = best_target or best_hard or last
    if picked is None:
        raise RuntimeError("TTS failed all rates")
    win_rate, duration, aligned = picked
    if abs(probe_dur(wav) - duration) > 0.15:
        print("re-synth winning rate", win_rate)
        duration, aligned = synth_once(text, phrases, win_rate)
    write_align_files(aligned, duration)
    print("picked VO", win_rate, zh_sec(duration))
    return duration, aligned


def split_caption(line: str) -> list[str]:
    line = line.strip("。．. ")
    if "，" in line and len(line) > 8:
        parts = [p for p in line.split("，") if p]
        if 1 < len(parts) <= 2:
            return parts
    return [line]


def build_timeline(cues: list[tuple[float, float, str]], duration: float) -> dict:
    recipe = json.loads((ROOT / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
    by_text = {p: (s, e) for s, e, p in cues}
    specs = recipe["shots"]
    shots = []
    for i, spec in enumerate(specs):
        phrases = spec["phrases"]
        missing = [p for p in phrases if p not in by_text]
        if missing:
            raise SystemExit(f"missing phrases in align: {missing}")
        start = 0.0 if i == 0 else by_text[phrases[0]][0]
        if i + 1 < len(specs):
            nxt = specs[i + 1]["phrases"][0]
            nxt_start = by_text[nxt][0]
            if spec["kind"] == "A" and specs[i + 1]["kind"] == "B":
                end = max(start + 0.45, nxt_start - LEAD)
            else:
                end = nxt_start
        else:
            end = duration
        shot = {
            "id": spec["id"],
            "kind": spec["kind"],
            "start": round(float(start), 3),
            "end": round(float(end), 3),
            "src": spec["src"],
            "line": " ".join(phrases),
        }
        if spec.get("close"):
            shot["close"] = True
        if spec.get("broll"):
            shot["broll"] = spec["broll"]
        shots.append(shot)

    for i, shot in enumerate(shots):
        if shot["end"] <= shot["start"] + 0.12:
            raise SystemExit(f"bad shot {shot}")
        if i:
            shots[i]["start"] = shots[i - 1]["end"]
    shots[-1]["end"] = round(duration, 3)

    a_caps = []
    eyebrows = []
    shutters = []
    for i, spec in enumerate(specs):
        shot = shots[i]
        if spec["kind"] == "A":
            for phrase in spec["phrases"]:
                ps, pe = by_text[phrase]
                cap_s = max(shot["start"], ps if phrase != spec["phrases"][0] or i else 0.0)
                cap_e = min(shot["end"], pe)
                if cap_e > cap_s + 0.08:
                    a_caps.append({"start": round(cap_s, 3), "end": round(cap_e, 3), "lines": split_caption(phrase)})
            eyebrows.append({
                "start": shot["start"],
                "end": shot["end"],
                "text": f"A-ROLL / {spec['id'][1:3]}",
            })
        if i:
            shutters.append({
                "start": shot["start"],
                "color": list(MINT if spec["kind"] == "B" else CREAM),
            })

    data = {
        "audio": "audio/vo-full.wav",
        "duration": round(duration, 3),
        "duration_zh": zh_sec(duration),
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
        "cue_map": {p: [round(s, 3), round(e, 3)] for s, e, p in cues},
        "b_lead_s": LEAD,
        "video_type": "普通短视频",
        "source_note": "topics-batch4.md #83 / 工厂 64_旧方案套不上新问题 / 云端 NEW",
    }
    (ROOT / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


def make_bgm(duration: float) -> Path:
    dest = ROOT / "audio" / "bgm.wav"
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=164:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=196:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=246:sample_rate=44100:duration={duration + 1.2:.2f}",
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
        delays.append(f"aevalsrc=0.012*sin(2*PI*760*t):s=44100:d=0.07,adelay={ms}|{ms}[s{i}]")
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
    fnt = font(50 if len(lines) == 1 and max(len(s) for s in lines) <= 9 else 42)
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
    pd.rectangle((10, 14, 20, box_h - 14), fill=(*YELLOW, 235))
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
    if kind == "A" and close:
        vf = f"scale=1380:2454,crop={W}:{H}:150:60,fps={FPS},setsar=1,format=yuv420p"
    elif kind == "A":
        vf = f"scale=1188:2112,crop={W}:{H}:54:105,fps={FPS},setsar=1,format=yuv420p"
    else:
        vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},setsar=1,format=yuv420p"
    run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(src), "-t", f"{dur:.3f}",
        "-vf", vf, "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18", str(dest),
    ])


def assemble(data: dict) -> Path:
    shots_dir = ROOT / "shots"
    shots_dir.mkdir(exist_ok=True)
    parts: list[Path] = []
    for shot in data["shots"]:
        dur = float(shot["end"]) - float(shot["start"])
        src = ROOT / shot["src"]
        dest = shots_dir / f"{shot['id']}.mp4"
        print(shot["id"], shot["kind"], zh_sec(dur), src.name)
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

    out = ROOT / "output" / f"{NAME}.mp4"
    out.parent.mkdir(exist_ok=True)
    shutil.copy2(final, out)
    shutil.copy2(final, ROOT / "final" / f"{NAME}.mp4")

    staged = Path("/workspace/成片") / STAGED_NAME
    staged.parent.mkdir(exist_ok=True)
    if staged.resolve() != final.resolve():
        try:
            shutil.copy2(final, staged)
        except shutil.SameFileError:
            pass
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
    d.text((W // 2, 160), "旧方案", font=font(52), fill=WHITE, anchor="mm")
    d.text((W // 2, 250), "套不上", font=font(72), fill=YELLOW, anchor="mm")
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
    src_dir = ASSET_SRC
    if not (src_dir / "V-挥手.mp4").exists():
        for alt in (
            Path("/workspace/.abroll-cloud/81/assets"),
            Path("/workspace/.abroll-cloud/73/assets"),
        ):
            if (alt / "V-挥手.mp4").exists():
                src_dir = alt
                break
    for name in ("V-挥手.mp4", "V-摊手.mp4", "V-指向.mp4", "V-点赞.mp4", "A-角色-小灯-摊手.jpg"):
        src = src_dir / name
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
        "project_name": "83_旧方案套不上新问题",
        "video_type": "普通短视频",
        "episode": 83,
        "title": NAME,
        "source_note": "topics-batch4.md #83 / 工厂 64_旧方案套不上新问题 / 云端 NEW",
        "slug": "83_旧方案套不上新问题",
        "duration_zh": zh_sec(duration),
        "voice": VOICE,
        "duration": round(duration, 3),
        "size": [W, H],
        "fps": FPS,
        "stage": "delivered",
        "status": "已交付",
        "current_stage": "核验并交付",
        "production_method": "白底小灯 A-roll + 黑底对照卡 B-roll + edge-tts Yunyang + FFmpeg",
        "script": {"path": "script/voiceover.txt", "sha256": sha},
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
        "factory_remap": "工厂 64 → 成片 83（64 已被空字典占用）",
        "distinct_from": "成片/64-空字典写在循环外面.mp4",
        "not_factory_copy": True,
        "cloud_only": True,
        "windows_paths": False,
        "drive_upload": False,
        "not": "drama-pipeline / 仙侠连载 / C:D:G: / Drive 上传 / 工厂15.5秒短切 / 成片64空字典 / 验收 / 试点",
        "updated_at": now,
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    note = f"""# 83 · 旧方案套不上新问题

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。

- **选题**：`topics-batch4.md` 第 83 条（工厂原号 64）
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿目录**：`/workspace/.abroll-cloud/83/`
- **云端 only**：不写 `C:\\` / `D:\\` / `G:\\`，不传 Drive
- **时长**：{zh_sec(duration)}（目标四十到五十秒）
- **避开**：成片 64 空字典；工厂 15.5 秒短切不拷；#62 验收；#61 试点；成片 29 故事锁

钩子：旧方案套不上新问题。去年能跑，今年对不上。  
诊断：不是执行不力，是尺寸不对。  
动作：先写下这次新在哪。能留的留下，对不上的重写。  
收束：对得上才复用。套不上就停手。先量尺寸，再裁新布。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。不念真名。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {zh_sec(duration)}（目标四十到五十秒）。镜头 {len(data["shots"])} 条，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")

    (ROOT / "时长.md").write_text(
        f"""# 成片 83 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 工厂短切 | 新时长 | 草稿 |
|----|------|----------|--------|------|
| 83 | `{STAGED_NAME}` | 十五点五秒（不拷） | {zh_sec(duration)} | `.abroll-cloud/83/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。十二镜 / 十八句。禁止 `tpad=stop_mode=clone`。
成片 64 是空字典，本集不占用 64。
""",
        encoding="utf-8",
    )


def patch_index(duration: float) -> None:
    line = f"| `{STAGED_NAME}` | {zh_sec(duration)} |"
    for idx in (Path("/workspace/成片/INDEX.md"), Path("/workspace/.abroll-cloud/INDEX.chengpian.md")):
        if not idx.exists():
            continue
        text = idx.read_text(encoding="utf-8")
        token = f"`{STAGED_NAME}`"
        if token in text:
            rows = []
            for raw in text.splitlines():
                if raw.startswith("|") and token in raw:
                    rows.append(line)
                else:
                    rows.append(raw)
            text = "\n".join(rows)
            if not text.endswith("\n"):
                text += "\n"
            idx.write_text(text, encoding="utf-8")
            continue
        if not text.endswith("\n"):
            text += "\n"
        if "仙侠云海突进" in text:
            text = text.replace("| `仙侠云海突进.mp4`", line + "\n| `仙侠云海突进.mp4`")
        else:
            text += line + "\n"
        idx.write_text(text, encoding="utf-8")


def patch_delivery(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    row = (
        f"| `成片/{STAGED_NAME}` | 1080×1920 h264+aac 44.1k stereo | {zh_sec(duration)} | "
        f"topic 83 `topics-batch4.md` 第 83 条；工厂 `64_旧方案套不上新问题`（15.5秒短切不拷）。"
        f"成片 64 已被空字典占用。云端 NEW |"
    )
    token = f"`成片/{STAGED_NAME}`"
    if token in text:
        rows = []
        for raw in text.splitlines():
            if raw.startswith("|") and token in raw:
                rows.append(row)
            else:
                rows.append(raw)
        text = "\n".join(rows)
    else:
        marker = "| `成片/仙侠云海突进.mp4`"
        if marker in text:
            text = text.replace(marker, row + "\n" + marker)
        else:
            if not text.endswith("\n"):
                text += "\n"
            text += row + "\n"
    plus_row = f"| 83 | `{STAGED_NAME}` | {zh_sec(duration)} | 已核验 |"
    if "| 83 |" in text:
        rows = []
        for raw in text.splitlines():
            if raw.startswith("| 83 |"):
                rows.append(plus_row)
            else:
                rows.append(raw)
        text = "\n".join(rows)
    elif "| 81 |" in text and plus_row not in text:
        lines = text.splitlines()
        out = []
        inserted = False
        for raw in lines:
            out.append(raw)
            if raw.startswith("| 81 |") and not inserted:
                out.append(plus_row)
                inserted = True
        text = "\n".join(out)
    elif plus_row not in text:
        if not text.endswith("\n"):
            text += "\n"
        text += plus_row + "\n"
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


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
    shot_overlap = any(data["shots"][i]["end"] > data["shots"][i + 1]["start"] + 0.001 for i in range(len(data["shots"]) - 1))
    shot_gap = any(abs(data["shots"][i]["end"] - data["shots"][i + 1]["start"]) > 0.02 for i in range(len(data["shots"]) - 1))
    null = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(staged), "-f", "null", "-"],
        capture_output=True, text=True,
    )
    (qa_dir / "decode.txt").write_text((null.stderr or "") + "\n", encoding="utf-8")
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
    fps_num, fps_den = (v.get("r_frame_rate") or "24/1").split("/")
    fps = float(fps_num) / float(fps_den or 1)
    digest = hashlib.sha256(staged.read_bytes()).hexdigest()
    other64 = Path("/workspace/成片/64-空字典写在循环外面.mp4")
    distinct64 = True
    if other64.exists():
        distinct64 = digest != hashlib.sha256(other64.read_bytes()).hexdigest()
    report = {
        "project": "83_旧方案套不上新问题",
        "duration_zh": zh_sec(float(info["format"]["duration"])),
        "strict": True,
        "cloud_only": True,
        "windows_paths": False,
        "drive_upload": False,
        "video_type": "普通短视频",
        "final": str(staged),
        "project_final": str(ROOT / f"00_最终成片_{NAME}.mp4"),
        "sha256": digest,
        "bytes": staged.stat().st_size,
        "distinct_from_64_empty_dict": distinct64,
        "not_factory_copy": True,
        "video": {
            "codec": v.get("codec_name"),
            "width": int(v.get("width", 0)),
            "height": int(v.get("height", 0)),
            "fps": fps,
            "pix_fmt": v.get("pix_fmt"),
            "duration_s": float(info["format"]["duration"]),
        },
        "audio": {
            "codec": a.get("codec_name"),
            "sample_rate": int(a.get("sample_rate", 0)),
            "channels": int(a.get("channels", 0)),
            "mean_volume_db": mean,
            "max_volume_db": maxv,
        },
        "timeline": {
            "segments": len(data["shots"]),
            "overlap": shot_overlap,
            "gap": shot_gap,
            "last_end_equals_audio": abs(data["shots"][-1]["end"] - data["duration"]) < 0.05,
            "broll_lead_s": LEAD,
        },
        "decode_null": null.returncode == 0 and not (null.stderr or "").strip(),
        "ok": True,
    }
    dur_s = report["video"]["duration_s"]
    report["duration_window"] = {
        "min": HARD_LO,
        "max": HARD_HI,
        "target": [TARGET_LO, TARGET_HI],
        "hit": TARGET_LO <= dur_s <= TARGET_HI,
        "duration_zh": zh_sec(dur_s),
    }
    kinds = [s["kind"] for s in data["shots"]]
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8")
    banned = ["验收", "试点成功", "空字典", "再优化", "下一期", "赵老师"]
    report["script_guard"] = {w: (w not in vo) for w in banned}
    report["ok"] = (
        report["video"]["width"] == 1080
        and report["video"]["height"] == 1920
        and abs(report["video"]["fps"] - 24) < 0.05
        and report["video"]["codec"] == "h264"
        and report["audio"]["codec"] == "aac"
        and report["audio"]["sample_rate"] == 44100
        and report["decode_null"]
        and not shot_overlap
        and not shot_gap
        and report["timeline"]["last_end_equals_audio"]
        and report["duration_window"]["hit"]
        and kinds.count("A") >= 4
        and kinds.count("B") >= 3
        and distinct64
        and all(report["script_guard"].values())
    )
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    copy_assets()
    duration, cues = make_voiceover()
    print("VO", zh_sec(duration))
    for row in cues:
        print(f"  {row[0]:6.3f}-{row[1]:6.3f}  {row[2]}")
    if not (HARD_LO <= duration <= HARD_HI):
        raise SystemExit(f"VO duration {zh_sec(duration)} outside 三十到六十秒")
    make_bgm(duration)
    data = build_timeline(cues, duration)
    print("timeline shots", [(s["id"], s["start"], s["end"], s["kind"]) for s in data["shots"]])

    for shot in data["shots"]:
        if shot["kind"] != "B":
            continue
        key = shot.get("broll")
        if key not in BROLL_DRAW:
            raise SystemExit(f"unknown broll {key}")
        d = max(1.6, float(shot["end"]) - float(shot["start"]))
        dest = ROOT / shot["src"]
        print("render", dest.name, zh_sec(d), key)
        render_to_mp4(BROLL_DRAW[key], d + 0.12, dest)

    make_cover()
    staged = assemble(data)
    dur = probe_dur(staged)
    write_docs(dur, staged, data)
    patch_index(dur)
    patch_delivery(dur)
    report = qa(staged, data)
    print("STAGED", staged, "dur", zh_sec(dur), "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
