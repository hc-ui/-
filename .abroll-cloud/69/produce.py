#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Topic 69：值班手册是空的。工厂 69_值班手册是空的。云端 NEW A-roll + B-roll。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/69/，成品中转 成片/69-值班手册是空的.mp4。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
目标四十到五十秒。不定格、不慢放注水。时长用中文「秒」。
不讲备机号（成片 09）。
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
NAME = "值班手册是空的"
STAGED_NAME = "69-值班手册是空的.mp4"
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
    d.ellipse((-220 + dx, -280 + dy, 720 + dx, 560 + dy), fill=(16, 42, 38))
    d.ellipse((480 - dx, 1180 - dy, 1400 - dx, 2100 - dy), fill=(42, 32, 16))
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
    rounded(draw, (x - 22, y - 14, x + tw + 22, y + th + 12), 22, mix(BG, (20, 42, 38), a))
    draw.text((x, y), label, font=fnt, fill=mix(BG, MINT, a))


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


def draw_book(draw: ImageDraw.ImageDraw, x0: int, y0: int, w: int, h: int, a: float, title: str, blank: bool) -> None:
    if a <= 0.04:
        return
    cover = mix(BG, (42, 28, 22) if blank else (22, 40, 36), a)
    rounded(draw, (x0, y0, x0 + w, y0 + h), 28, cover)
    draw.rectangle((x0 + 18, y0 + 24, x0 + 30, y0 + h - 24), fill=mix(cover, YELLOW if blank else MINT, a))
    draw.text((x0 + w // 2, y0 + 70), title, font=font(28), fill=mix(cover, MUTED, a), anchor="mm")
    page = mix(cover, (236, 232, 220) if not blank else (48, 50, 56), a)
    rounded(draw, (x0 + 54, y0 + 110, x0 + w - 36, y0 + h - 36), 16, page)
    if blank:
        draw.text((x0 + w // 2 + 8, y0 + h // 2 + 20), "空白", font=font(48), fill=mix(page, RED, a), anchor="mm")
    else:
        for i, line in enumerate(("谁接", "怎么停", "打给谁")):
            yy = y0 + 170 + i * 70
            draw.rectangle((x0 + 80, yy, x0 + w - 70, yy + 14), fill=mix(page, INK, a))
            draw.text((x0 + 80, yy - 28), line, font=font(24), fill=mix(page, INK, a), anchor="lm")


def draw_b_empty_book(t: float) -> Image.Image:
    img = new_bg(t)
    d = ImageDraw.Draw(img)
    tag(d, t, "错 · 空本子")
    d.text((W // 2, 236 + bob(t, 7, 0.5)), "本子在，字不在", font=font(52), fill=mix(BG, WHITE, appear(t, 0.02)), anchor="mm")
    a1 = appear(t, 0.12)
    draw_book(d, 90, 330 + bob(t, 8, 0.55), 420, 520, a1, "封面写值班", True)
    reveal = appear(t, 0.40, 0.4)
    draw_book(d, 560, 330 + bob(t + 0.2, 8, 0.5), 430, 520, max(a1, reveal), "翻开全空", True)
    punch = appear(t, 1.00, 0.22)
    if punch > 0.04:
        y = 920 + bob(t, 7, 0.8)
        rounded(d, (120, y, 960, y + 180), 28, mix(BG, (42, 24, 22), punch))
        d.text((W // 2, y + 90), "不是没本子", font=font(50), fill=mix(BG, YELLOW, punch), anchor="mm")
    return img


def draw_b_night_guess(t: float) -> Image.Image:
    img = new_bg(t)
    d = ImageDraw.Draw(img)
    tag(d, t, "错 · 夜里猜")
    d.text((W // 2, 236 + bob(t, 6, 0.5)), "夜里出事只能猜", font=font(50), fill=mix(BG, WHITE, appear(t, 0.02)), anchor="mm")
    a1 = appear(t, 0.14)
    y = 330 + bob(t, 8, 0.55)
    rounded(d, (80, y, 1000, y + 280), 32, mix(BG, CARD, a1))
    d.text((W // 2, y + 80), "口头传说", font=font(36), fill=mix(CARD, MUTED, a1), anchor="mm")
    d.text((W // 2, y + 170), "他说过一次", font=font(48), fill=mix(CARD, YELLOW, a1), anchor="mm")
    fade = appear(t, 0.48)
    y2 = 660 + bob(t + 0.2, 9, 0.6)
    rounded(d, (80, y2, 1000, y2 + 240), 32, mix(BG, (42, 24, 22), fade))
    d.text((W // 2, y2 + 80), "第一晚", font=font(32), fill=mix(CARD, MUTED, fade), anchor="mm")
    d.text((W // 2, y2 + 160), "踩坑", font=font(64), fill=mix(CARD, RED, fade), anchor="mm")
    q = 0.4 + 0.6 * abs(math.sin(t * 2.6))
    d.text((860, 420), "？", font=font(72), fill=mix(CARD, YELLOW, q), anchor="mm")
    punch = appear(t, 1.00, 0.22)
    if punch > 0.04:
        y = 980 + bob(t, 7, 0.8)
        rounded(d, (120, y, 960, y + 170), 28, mix(BG, (42, 24, 22), punch))
        d.text((W // 2, y + 85), "只能猜", font=font(52), fill=mix(BG, YELLOW, punch), anchor="mm")
    return img


def draw_b_one_head(t: float) -> Image.Image:
    img = new_bg(t)
    d = ImageDraw.Draw(img)
    tag(d, t, "错 · 一人脑子")
    d.text((W // 2, 236 + bob(t, 6, 0.5)), "步骤只在一个人脑子里", font=font(44), fill=mix(BG, WHITE, appear(t, 0.02)), anchor="mm")
    a1 = appear(t, 0.14)
    y = 340 + bob(t, 8, 0.55)
    rounded(d, (80, y, 520, y + 400), 32, mix(BG, CARD, a1))
    d.text((300, y + 90), "停机步骤", font=font(30), fill=mix(CARD, MUTED, a1), anchor="mm")
    d.text((300, y + 190), "在他脑子里", font=font(40), fill=mix(CARD, YELLOW, a1), anchor="mm")
    d.text((300, y + 290), "没写下来", font=font(32), fill=mix(CARD, RED, a1), anchor="mm")
    gone = appear(t, 0.36)
    gx = 560 + int(40 * math.sin(t * 1.4))
    rounded(d, (gx, y + bob(t + 0.3, 7, 0.5), gx + 440, y + 400), 32, mix(BG, (36, 28, 24), gone))
    d.text((gx + 220, y + 90), "人一不在", font=font(30), fill=mix(CARD, MUTED, gone), anchor="mm")
    d.text((gx + 220, y + 190), "整晚悬着", font=font(44), fill=mix(CARD, RED, gone), anchor="mm")
    d.text((gx + 220, y + 290), "没人接得住", font=font(32), fill=mix(CARD, MUTED, gone), anchor="mm")
    punch = appear(t, 1.00, 0.22)
    if punch > 0.04:
        y = 840 + bob(t, 7, 0.8)
        rounded(d, (120, y, 960, y + 180), 28, mix(BG, (42, 24, 22), punch))
        d.text((W // 2, y + 90), "整晚悬着", font=font(52), fill=mix(BG, YELLOW, punch), anchor="mm")
    return img


def draw_b_three_pages(t: float) -> Image.Image:
    img = new_bg(t)
    d = ImageDraw.Draw(img)
    tag(d, t, "对 · 三页")
    d.text((W // 2, 236 + bob(t, 6, 0.5)), "接班先补三页", font=font(54), fill=mix(BG, WHITE, appear(t, 0.02)), anchor="mm")
    rows = [
        (0.12, "1", "谁接", "第一页写清班次", YELLOW),
        (0.32, "2", "怎么停", "第二页写停机", MINT),
        (0.52, "3", "打给谁", "第三页写报警", (92, 176, 214)),
    ]
    for idx, (ts, num, head, body, color) in enumerate(rows):
        a = appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 330 + idx * 180 + bob(t + idx * 0.15, 7, 0.6)
        rounded(d, (90, y, 990, y + 160), 26, mix(BG, CARD, a))
        d.ellipse((128, y + 36, 220, y + 128), fill=mix(CARD, color, a))
        d.text((174, y + 82), num, font=font(36), fill=mix(color, INK, a), anchor="mm")
        d.text((248, y + 56), head, font=font(48), fill=mix(CARD, color, a), anchor="lm")
        d.text((248, y + 116), body, font=font(28), fill=mix(CARD, WHITE, a), anchor="lm")
        check_badge(d, 900, y + 80, appear(t, ts + 0.35, 0.16))
    punch = appear(t, 1.15, 0.20)
    if punch > 0.04:
        y = 920 + bob(t, 7, 0.8)
        rounded(d, (140, y, 940, y + 160), 26, mix(BG, (18, 42, 36), punch))
        d.text((W // 2, y + 80), "照着做", font=font(52), fill=mix(BG, MINT, punch), anchor="mm")
    return img


def draw_b_empty_duty(t: float) -> Image.Image:
    img = new_bg(t)
    d = ImageDraw.Draw(img)
    tag(d, t, "收 · 当没值")
    d.text((W // 2, 236 + bob(t, 6, 0.5)), "空手册请当成没值", font=font(48), fill=mix(BG, WHITE, appear(t, 0.02)), anchor="mm")
    a1 = appear(t, 0.14)
    y = 330 + bob(t, 8, 0.55)
    rounded(d, (80, y, 520, y + 400), 32, mix(BG, (42, 24, 22), a1))
    d.text((300, y + 90), "空页", font=font(30), fill=mix(CARD, MUTED, a1), anchor="mm")
    d.text((300, y + 190), "翻开没有字", font=font(40), fill=mix(CARD, RED, a1), anchor="mm")
    strike_line(d, (120, y + 160, 480, y + 220), appear(t, 0.40, 0.4), mix(CARD, RED, 1))
    fill = appear(t, 0.36, 0.7)
    rounded(d, (560, y + bob(t + 0.2, 7, 0.5), 1000, y + 400), 32, mix(BG, (22, 40, 36), a1))
    d.text((780, y + 90), "补上", font=font(30), fill=mix(CARD, MUTED, a1), anchor="mm")
    d.text((780, y + 190), "写完交接", font=font(40), fill=mix(CARD, MINT, a1), anchor="mm")
    bar_w = int(lerp(40, 320, fill))
    rounded(d, (620, y + 270, 620 + bar_w, y + 330), 14, mix(CARD, MINT, a1))
    check_badge(d, 780, y + 360, appear(t, 0.80, 0.18))
    punch = appear(t, 1.05, 0.22)
    if punch > 0.04:
        y = 820 + bob(t, 7, 0.8)
        rounded(d, (120, y, 960, y + 180), 28, mix(BG, (18, 42, 36), punch))
        d.text((W // 2, y + 90), "请当成没值", font=font(50), fill=mix(BG, MINT, punch), anchor="mm")
    return img


BROLL_DRAW = {
    "empty_book": draw_b_empty_book,
    "night_guess": draw_b_night_guess,
    "one_head": draw_b_one_head,
    "three_pages": draw_b_three_pages,
    "empty_duty": draw_b_empty_duty,
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
    rates = ["+4%", "+2%", "-2%", "-4%", "-8%", "+8%"]
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
        "source_note": "工厂 69_值班手册是空的 / 云端 NEW",
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
    if kind == "A" and close:
        vf = f"scale=1380:2454,crop={W}:{H}:150:60,fps={FPS},setsar=1,format=yuv420p"
    elif kind == "A":
        vf = f"scale=1188:2112,crop={W}:{H}:54:105,fps={FPS},setsar=1,format=yuv420p"
    else:
        vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},setsar=1,format=yuv420p"
    # Loop the clip. Do not freeze-frame or slow-mo pad.
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
    d.text((W // 2, 160), "值班手册", font=font(52), fill=WHITE, anchor="mm")
    d.text((W // 2, 250), "是空的", font=font(72), fill=YELLOW, anchor="mm")
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
        "project_name": "69_值班手册是空的",
        "video_type": "普通短视频",
        "episode": 69,
        "title": NAME,
        "source_note": "工厂 69_值班手册是空的 / 云端 NEW",
        "slug": "69_值班手册是空的",
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
        "cloud_only": True,
        "windows_paths": False,
        "drive_upload": False,
        "not": "drama-pipeline / 仙侠连载 / C:D:G: / Drive 上传 / 成片09备机号",
        "updated_at": now,
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    note = f"""# 69 · 值班手册是空的

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。

- **选题**：工厂 `69_值班手册是空的`（`成片/69-*.mp4` 原未占用）
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿目录**：`/workspace/.abroll-cloud/69/`
- **云端 only**：不写 `C:\\` / `D:\\` / `G:\\`，不传 Drive
- **时长**：{zh_sec(duration)}（目标四十到五十秒）
- **避开**：成片 09 备机号；成片 08 工单时限；成片 07 中止口令；成片 01 截止日

钩子：值班手册是空的。  
后果：本子在、字不在；夜里出事只能猜。  
做法：接班先补三页——谁接、怎么停、打给谁。  
收束：空手册的值班，请当成没值。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {zh_sec(duration)}（目标四十到五十秒）。镜头 {len(data["shots"])} 条，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")

    (ROOT / "69-DURATION.md").write_text(
        f"""# 成片 69 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 工厂短切 | 新时长 | 草稿 |
|----|------|----------|--------|------|
| 69 | `{STAGED_NAME}` | 十六点九六秒 | {zh_sec(duration)} | `.abroll-cloud/69/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。十一镜 / 十七句。禁止 `tpad=stop_mode=clone`。
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
    report = {
        "project": "69_值班手册是空的",
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
    report = qa(staged, data)
    print("STAGED", staged, "dur", zh_sec(dur), "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
