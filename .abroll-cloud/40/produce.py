#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 40：对齐为什么对齐到半夜。云端 A-roll + B-roll，不是短剧。"""
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
NAME = "对齐为什么对齐到半夜"
STAGED_NAME = "40-对齐为什么对齐到半夜.mp4"
VOICE = "zh-CN-YunyangNeural"
ASSET_SRC = Path("/workspace/.abroll-cloud/06/assets")
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_REG = "/tmp/NotoSansSC-Regular.otf"
FONT_FALLBACK = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

BG = (8, 10, 22)
CARD = (22, 26, 40)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
CREAM = (245, 247, 250)
RED = (255, 118, 118)
INK = (22, 24, 28)
AMBER = (255, 168, 76)
NAVY = (18, 28, 58)
LEAD = 0.28


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
    d.ellipse((-260, -320, 640, 520), fill=(16, 22, 48))
    d.ellipse((420, 980, 1380, 1980), fill=(48, 28, 12))
    overlay = overlay.filter(ImageFilter.GaussianBlur(120))
    return Image.blend(img, overlay, 0.62)


def tag(draw: ImageDraw.ImageDraw, t: float, label: str) -> None:
    a = appear(t, 0.0, 0.22)
    if a <= 0:
        return
    fnt = font(30)
    tw, th = text_wh(draw, label, fnt)
    x, y = 84, 88
    rounded(draw, (x - 22, y - 14, x + tw + 22, y + th + 12), 22, mix(BG, (20, 32, 56), a))
    draw.text((x, y), label, font=fnt, fill=mix(BG, AMBER, a))


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


def split_caption(line: str) -> list[str]:
    line = line.strip("。．. ")
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
    return aligned


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
    log = proc.stderr
    starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", log)]
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

    lines = [f"{s:.3f}\t{e:.3f}\t{p}" for s, e, p in aligned]
    (audio_dir / "vo-align.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    vtt = ["WEBVTT", ""]
    for i, (s, e, p) in enumerate(aligned, 1):
        def ts(x: float) -> str:
            ms = int(round(x * 1000))
            return f"{ms // 3600000:02d}:{(ms // 60000) % 60:02d}:{(ms // 1000) % 60:02d}.{ms % 1000:03d}"

        vtt += [str(i), f"{ts(s)} --> {ts(e)}", p, ""]
    (audio_dir / "vo.vtt").write_text("\n".join(vtt), encoding="utf-8")
    return duration, aligned


def make_bgm(duration: float) -> Path:
    dest = ROOT / "audio" / "bgm.wav"
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=147:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=185:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=220:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-filter_complex",
        "[0:a]volume=0.10[a];[1:a]volume=0.07[b];[2:a]volume=0.05[c];"
        "[a][b][c]amix=inputs=3:duration=longest,lowpass=f=460,alimiter=limit=0.30",
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
        delays.append(f"aevalsrc=0.011*sin(2*PI*740*t):s=44100:d=0.07,adelay={ms}|{ms}[s{i}]")
        parts.append(f"[s{i}]")
    fc = ";".join(delays) + f";{''.join(parts)}amix=inputs={len(parts)}:duration=longest,aformat=sample_rates=44100:channel_layouts=stereo"
    run(["ffmpeg", "-y", "-filter_complex", fc, "-t", f"{duration:.2f}", str(dest)])
    return dest


def draw_clock(draw, cx: int, cy: int, scale: float, a: float, t: float) -> None:
    if a <= 0.04:
        return
    r = int(118 * scale)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=mix(BG, CARD, a), outline=mix(CARD, AMBER, a), width=8)
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        x0 = cx + int((r - 18) * math.cos(ang))
        y0 = cy + int((r - 18) * math.sin(ang))
        x1 = cx + int((r - 6) * math.cos(ang))
        y1 = cy + int((r - 6) * math.sin(ang))
        draw.line([(x0, y0), (x1, y1)], fill=mix(CARD, MUTED, a), width=3)
    sweep = min(1.0, t / 1.8)
    hour = math.radians(-90 + 8)
    minute = math.radians(-90 + lerp(240, 358, sweep))
    draw.line([(cx, cy), (cx + int(r * 0.48 * math.cos(hour)), cy + int(r * 0.48 * math.sin(hour)))], fill=mix(CARD, WHITE, a), width=8)
    draw.line([(cx, cy), (cx + int(r * 0.78 * math.cos(minute)), cy + int(r * 0.78 * math.sin(minute)))], fill=mix(CARD, AMBER, a), width=6)
    draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=mix(CARD, YELLOW, a))
    draw.text((cx, cy + r + 36), "半夜", font=font(max(22, int(26 * scale))), fill=mix(BG, AMBER, a), anchor="mm")


def draw_knot(draw, cx: int, cy: int, a: float, t: float) -> None:
    if a <= 0.04:
        return
    for i, label in enumerate(("议题", "工期", "接口", "预算", "风险")):
        ang = math.radians(-90 + i * 72 + t * 18)
        r = 86
        x = cx + int(r * math.cos(ang))
        y = cy + int(r * math.sin(ang))
        draw.line([(cx, cy), (x, y)], fill=mix(CARD, RED, a), width=6)
        draw.ellipse((x - 28, y - 28, x + 28, y + 28), fill=mix(CARD, (48, 24, 24), a))
        draw.text((x, y), label, font=font(20), fill=mix(CARD, WHITE, a), anchor="mm")
    draw.ellipse((cx - 36, cy - 36, cx + 36, cy + 36), fill=mix(CARD, RED, a))
    draw.text((cx, cy), "捆", font=font(28), fill=mix(RED, INK, a), anchor="mm")


def strike_line(draw: ImageDraw.ImageDraw, box, progress: float, color) -> None:
    x0, y0, x1, y1 = box
    if progress <= 0.04:
        return
    mid = (y0 + y1) / 2
    x_end = lerp(x0 + 24, x1 - 24, min(1.0, progress))
    draw.line([(x0 + 24, mid), (x_end, mid)], fill=color, width=10)


def check_badge(draw, cx: int, cy: int, a: float) -> None:
    if a <= 0.04:
        return
    r = 36
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=mix(CARD, (18, 56, 46), a))
    col = mix(CARD, MINT, a)
    draw.line([(cx - 16, cy + 2), (cx - 4, cy + 16), (cx + 20, cy - 14)], fill=col, width=8)


def render_b_one_line(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(52)
    card_f = font(40)
    sub_f = font(30)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "01 一句议题")
        a0 = appear(t, 0.02)
        d.text((W // 2, 220 + int(lerp(16, 0, a0))), "先写必须对齐的那一句", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        draw_clock(d, 270, 460, 1.0, appear(t, 0.08, 0.24), t)
        draw_knot(d, 800, 460, appear(t, 0.16, 0.24), t)

        a1 = appear(t, 0.55)
        if a1 > 0.04:
            y = 680 + int(lerp(20, 0, a1))
            rounded(d, (80, y, 1000, y + 200), 28, mix(BG, CARD, a1))
            d.text((W // 2, y + 62), "不要捆", font=sub_f, fill=mix(CARD, RED, a1), anchor="mm")
            d.text((W // 2, y + 128), "十个问题一起聊", font=card_f, fill=mix(CARD, WHITE, a1), anchor="mm")
            strike_line(d, (160, y + 90, 920, y + 170), appear(t, 1.15, 0.28), mix(CARD, RED, a1))

        a2 = appear(t, 1.05)
        if a2 > 0.04:
            y = 920 + int(lerp(20, 0, a2))
            rounded(d, (80, y, 1000, y + 240), 28, mix(BG, (22, 40, 36), a2))
            d.text((W // 2, y + 70), "只要这句", font=sub_f, fill=mix(CARD, MINT, a2), anchor="mm")
            d.text((W // 2, y + 150), "一个议题 · 一次一句", font=card_f, fill=mix(CARD, YELLOW, a2), anchor="mm")

        punch = appear(t, 1.70, 0.22)
        if punch > 0.04:
            y = 1220 + int(lerp(18, 0, punch))
            rounded(d, (160, y, 920, y + 150), 26, mix(BG, (42, 28, 14), punch))
            d.text((W // 2, y + 75), "只要这一句", font=title_f, fill=mix(BG, AMBER, punch), anchor="mm")
        out.append(img)
    return out


def render_b_one_dissent(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(50)
    card_f = font(40)
    sub_f = font(28)
    out = []
    bubbles = [
        (0.10, 160, 360, "方案 A", RED),
        (0.22, 560, 320, "方案 B", YELLOW),
        (0.34, 360, 520, "方案 C", MUTED),
    ]
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "02 一个分歧")
        a0 = appear(t, 0.02)
        d.text((W // 2, 220 + int(lerp(16, 0, a0))), "每人只带一个分歧", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        pile = appear(t, 0.70, 0.35)
        for ts, x, y, label, color in bubbles:
            a = appear(t, ts, 0.20)
            if a < 0.04:
                continue
            yy = y + int(lerp(18, 0, a)) + int(pile * 40)
            rounded(d, (x, yy, x + 360, yy + 120), 24, mix(BG, CARD, a))
            d.text((x + 180, yy + 60), label, font=card_f, fill=mix(CARD, color, a), anchor="mm")
            if pile > 0.2:
                strike_line(d, (x + 20, yy + 20, x + 340, yy + 100), pile, mix(CARD, RED, a))

        warn = appear(t, 0.95)
        if warn > 0.04:
            y = 700 + int(lerp(16, 0, warn))
            rounded(d, (80, y, 1000, y + 200), 28, mix(BG, CARD, warn))
            d.text((W // 2, y + 64), "分歧堆一起", font=sub_f, fill=mix(CARD, MUTED, warn), anchor="mm")
            d.text((W // 2, y + 130), "变成聊天 · 对齐到半夜", font=card_f, fill=mix(CARD, RED, warn), anchor="mm")

        good = appear(t, 1.40)
        if good > 0.04:
            y = 960 + int(lerp(16, 0, good))
            rounded(d, (80, y, 1000, y + 200), 28, mix(BG, (22, 40, 36), good))
            d.text((200, y + 100), "只留一个分歧", font=card_f, fill=mix(CARD, MINT, good), anchor="lm")
            check_badge(d, 860, y + 100, appear(t, 1.55, 0.18))

        punch = appear(t, 1.85, 0.22)
        if punch > 0.04:
            y = 1220 + int(lerp(16, 0, punch))
            rounded(d, (120, y, 960, y + 150), 26, mix(BG, (42, 28, 14), punch))
            d.text((W // 2, y + 75), "一个分歧，才拍得了板", font=font(44), fill=mix(BG, AMBER, punch), anchor="mm")
        out.append(img)
    return out


def render_b_seven_days(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(50)
    card_f = font(40)
    sub_f = font(28)
    num_f = font(30)
    rows = [
        (0.10, "记", "有共识", "当场记下", MINT),
        (0.32, "定", "没共识", "负责人先定", YELLOW),
        (0.54, "七", "先定七天", "也能再改", AMBER),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "03 到点拍板")
        a0 = appear(t, 0.02)
        d.text((W // 2, 220 + int(lerp(16, 0, a0))), "到点必须带走决定", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        tick = appear(t, 0.08, 0.22)
        if tick > 0.04:
            rounded(d, (360, 300, 720, 420), 22, mix(BG, CARD, tick))
            d.text((W // 2, 360), "到点", font=font(48), fill=mix(CARD, AMBER, tick), anchor="mm")

        for idx, (ts, num, head, body, color) in enumerate(rows):
            a = appear(t, ts, 0.22)
            if a < 0.04:
                continue
            y = 470 + idx * 176 + int(lerp(18, 0, a))
            rounded(d, (90, y, 990, y + 156), 26, mix(BG, CARD, a))
            d.rounded_rectangle((120, y + 36, 220, y + 120), 16, fill=mix(CARD, color, a))
            d.text((170, y + 78), num, font=num_f, fill=mix(color, INK, a), anchor="mm")
            d.text((250, y + 48), head, font=card_f, fill=mix(CARD, color, a), anchor="lm")
            d.text((250, y + 110), body, font=sub_f, fill=mix(CARD, WHITE, a), anchor="lm")

        punch = appear(t, 1.55, 0.22)
        if punch > 0.04:
            y = 1040 + int(lerp(16, 0, punch))
            rounded(d, (140, y, 940, y + 160), 26, mix(BG, (42, 28, 14), punch))
            d.text((W // 2, y + 80), "不定，就散不了", font=title_f, fill=mix(BG, AMBER, punch), anchor="mm")
        out.append(img)
    return out


def build_timeline(cues: list[tuple[float, float, str]], duration: float) -> dict:
    recipe = json.loads((ROOT / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
    p = cues
    if len(p) != 14:
        raise SystemExit(f"need 14 phrases, got {len(p)}")

    def edge(i: int) -> float:
        return float(p[i][1])

    b1 = max(edge(4) + 0.04, p[5][0] - LEAD)
    b1e = edge(7)
    a3 = edge(8)
    b2 = max(a3 + 0.04, p[9][0] - LEAD)
    b2e = edge(9)
    a5 = edge(10)
    b3 = max(a5 + 0.04, p[11][0] - LEAD)
    b3e = edge(11)

    shots = [
        {"id": "S01a", "kind": "A", "start": 0.0, "end": round(edge(0), 3), "src": "assets/V-挥手.mp4", "line": p[0][2], "close": True},
        {"id": "S01b", "kind": "A", "start": round(edge(0), 3), "end": round(edge(2), 3), "src": "assets/V-摊手.mp4", "line": p[1][2]},
        {"id": "S01c", "kind": "A", "start": round(edge(2), 3), "end": round(b1, 3), "src": "assets/V-指向.mp4", "line": p[3][2]},
        {"id": "S02", "kind": "B", "start": round(b1, 3), "end": round(b1e, 3), "src": "broll/B-一句议题.mp4", "line": p[5][2], "broll": "one_line"},
        {"id": "S03", "kind": "A", "start": round(b1e, 3), "end": round(b2, 3), "src": "assets/V-摊手.mp4", "line": p[8][2]},
        {"id": "S04", "kind": "B", "start": round(b2, 3), "end": round(b2e, 3), "src": "broll/B-一个分歧.mp4", "line": p[9][2], "broll": "one_dissent"},
        {"id": "S05", "kind": "A", "start": round(b2e, 3), "end": round(b3, 3), "src": "assets/V-指向.mp4", "line": p[10][2]},
        {"id": "S06", "kind": "B", "start": round(b3, 3), "end": round(b3e, 3), "src": "broll/B-先定七天.mp4", "line": p[11][2], "broll": "seven_days"},
        {"id": "S07", "kind": "A", "start": round(b3e, 3), "end": round(duration, 3), "src": "assets/V-点赞.mp4", "line": p[12][2]},
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

    a_caps = [
        {"start": 0.0, "end": round(p[0][1], 3), "lines": ["大家好"]},
        {"start": round(p[1][0], 3), "end": round(min(p[1][1], shots[2]["start"]), 3), "lines": ["对齐对齐到半夜"]},
        {"start": round(p[2][0], 3), "end": round(min(p[2][1], shots[2]["start"]), 3), "lines": ["不是人不够认真"]},
        {"start": round(max(p[3][0], shots[2]["start"]), 3), "end": round(min(p[4][1], shots[3]["start"]), 3), "lines": split_caption(p[3][2])},
        {"start": round(max(p[8][0], shots[4]["start"]), 3), "end": round(shots[4]["end"], 3), "lines": ["每人只带一个分歧"]},
        {"start": round(max(p[10][0], shots[6]["start"]), 3), "end": round(shots[6]["end"], 3), "lines": ["到点没有共识"]},
        {"start": round(shots[8]["start"], 3), "end": round(min(p[12][1], duration), 3), "lines": ["按这三步对齐"]},
        {"start": round(max(p[13][0], shots[8]["start"]), 3), "end": round(duration, 3), "lines": ["人才回得了家"]},
    ]
    a_caps = [c for c in a_caps if c["end"] > c["start"] + 0.08]

    shutters = [
        {"start": shots[1]["start"], "color": list(CREAM)},
        {"start": shots[2]["start"], "color": list(CREAM)},
        {"start": shots[3]["start"], "color": list(AMBER)},
        {"start": shots[4]["start"], "color": list(CREAM)},
        {"start": shots[5]["start"], "color": list(MINT)},
        {"start": shots[6]["start"], "color": list(CREAM)},
        {"start": shots[7]["start"], "color": list(YELLOW)},
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
        "cue_map": {p3: [round(s, 3), round(e, 3)] for s, e, p3 in cues},
        "b_lead_s": LEAD,
        "video_type": "普通短视频",
    }
    (ROOT / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


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
    d.rectangle((76, 88, 120, 92), fill=(*AMBER, 230))
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
    pd.rectangle((10, 14, 20, box_h - 14), fill=(*AMBER, 235))
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
    if kind == "A" and dur > src_dur + 0.05:
        vf = f"setpts=PTS*{dur / src_dur:.6f},{vf}"
    elif dur > src_dur + 0.02:
        vf = f"{vf},tpad=stop_mode=clone:stop_duration={dur - src_dur:.3f}"
    run([
        "ffmpeg", "-y", "-i", str(src), "-t", f"{dur:.3f}",
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
        filters.append(f"[{idx}:a]adelay=800|800,volume=0.15,highpass=f=140[bg]")
        mix_ins.append("[bg]")
        idx += 1
    if sfx.exists():
        inputs += ["-i", str(sfx)]
        filters.append(f"[{idx}:a]volume=0.26[sfx]")
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
    shutil.copy2(final, staged)
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
    overlay = Image.new("RGBA", (W, H), (8, 10, 22, 56))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((70, 80, 1010, 470), radius=36, fill=(22, 24, 28))
    d.text((W // 2, 160), "对齐为什么", font=font(48), fill=WHITE, anchor="mm")
    d.text((W // 2, 250), "对齐到半夜", font=font(64), fill=AMBER, anchor="mm")
    d.text((W // 2, 340), cover["sub"], font=font(32), fill=MINT, anchor="mm")
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
        "project_name": "40_对齐为什么对齐到半夜",
        "video_type": "普通短视频",
        "episode": 40,
        "title": NAME,
        "source_note": "topics-batch3.md #40 文件不在云端；Drive 只读 40_对齐为什么对齐到半夜",
        "unused_of": "成片00-37 / 39对照卡 / 42比较 / 16切片 / 28报销 / 37撞课",
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
        "not": "drama-pipeline / 仙侠连载 / C:D:G: / Drive 上传",
        "updated_at": now,
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    note = f"""# 40 · 对齐为什么对齐到半夜

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。

- **选题**：`topics-batch3.md` #40（文件不在仓库）；Drive 只读 `40_对齐为什么对齐到半夜`
- **方法**：一句议题、一个分歧、到点没共识由负责人先定七天
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿目录**：`/workspace/.abroll-cloud/40/`
- **云端 only**：不写盘符路径，不传 Drive

钩子：对齐对齐到半夜，不是人不够认真。  
诊断：没有人能拍板，就散不了。  
收束：按这三步对齐，人才回得了家。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {duration:.2f} 秒。镜头 {len(data["shots"])} 条，时间轴闭合。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")


def patch_index(duration: float) -> None:
    idx = Path("/workspace/成片/INDEX.md")
    line = f"| `{STAGED_NAME}` | {duration:.1f}s |"
    if idx.exists():
        text = idx.read_text(encoding="utf-8")
        if STAGED_NAME not in text:
            if not text.endswith("\n"):
                text += "\n"
            text += line + "\n"
            idx.write_text(text, encoding="utf-8")
    else:
        idx.write_text(
            "# 成片（可直接看）\n\n竖屏口播 1080×1920，H.264 + AAC。\n\n| 文件 | 时长 |\n|------|------|\n"
            + line + "\n",
            encoding="utf-8",
        )


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
    shots = data["shots"]
    overlap = any(shots[i]["end"] > shots[i + 1]["start"] + 0.001 for i in range(len(shots) - 1))
    gap = any(abs(shots[i]["end"] - shots[i + 1]["start"]) > 0.02 for i in range(len(shots) - 1))
    fps_num, fps_den = (v.get("r_frame_rate") or "24/1").split("/")
    fps = float(fps_num) / float(fps_den or 1)
    digest = hashlib.sha256(staged.read_bytes()).hexdigest()
    report = {
        "project": "40_对齐为什么对齐到半夜",
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
            "segments": len(shots),
            "overlap": overlap,
            "gap": gap,
            "last_end_equals_audio": abs(shots[-1]["end"] - data["duration"]) < 0.05,
            "broll_lead_s": LEAD,
        },
        "decode_null": null.returncode == 0 and not (null.stderr or "").strip(),
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
    )
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    copy_assets()
    duration, cues = make_voiceover()
    print("VO", duration)
    for row in cues:
        print(f"  {row[0]:6.3f}-{row[1]:6.3f}  {row[2]}")
    make_bgm(duration)
    data = build_timeline(cues, duration)
    print("timeline shots", [(s["id"], s["start"], s["end"], s["kind"]) for s in data["shots"]])

    mapping = {
        "S02": ("B-一句议题.mp4", render_b_one_line),
        "S04": ("B-一个分歧.mp4", render_b_one_dissent),
        "S06": ("B-先定七天.mp4", render_b_seven_days),
    }
    for sid, (fname, renderer) in mapping.items():
        shot = next(s for s in data["shots"] if s["id"] == sid)
        d = max(2.2, float(shot["end"]) - float(shot["start"]))
        print("render", fname, d)
        frames_to_mp4(renderer(d + 0.12), ROOT / "broll" / fname)

    make_cover()
    staged = assemble(data)
    dur = probe_dur(staged)
    write_docs(dur, staged, data)
    patch_index(dur)
    report = qa(staged, data)
    print("STAGED", staged, "dur", dur, "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
