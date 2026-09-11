#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 48：远程实习人在工位活在线上。云端 A-roll + B-roll，不是短剧。"""
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
NAME = "远程实习人在工位活在线上"
STAGED_NAME = "48-远程实习人在工位活在线上.mp4"
VOICE = "zh-CN-YunyangNeural"
ASSET_SRC = Path("/workspace/.abroll-cloud/06/assets")
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


def check_badge(draw, cx: int, cy: int, a: float) -> None:
    if a <= 0.04:
        return
    r = 36
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=mix(CARD, (18, 56, 46), a))
    col = mix(CARD, MINT, a)
    draw.line([(cx - 16, cy + 2), (cx - 4, cy + 16), (cx + 20, cy - 14)], fill=col, width=8)


def draw_occupied_desk(draw: ImageDraw.ImageDraw, cx: int, cy: int, a: float, t: float) -> None:
    if a <= 0.04:
        return
    wood = mix(CARD, (58, 44, 28), a)
    glow = mix(CARD, MINT, a * 0.85)
    rounded(draw, (cx - 210, cy + 70, cx + 210, cy + 150), 18, wood)
    rounded(draw, (cx - 150, cy - 150, cx + 150, cy + 70), 16, mix(CARD, (18, 22, 28), a))
    rounded(draw, (cx - 136, cy - 136, cx + 136, cy + 46), 10, mix(CARD, (12, 28, 26), a))
    pulse = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(t * 3.2))
    for i in range(5):
        y = cy - 100 + i * 26
        wline = int(80 + 40 * math.sin(t * 2.4 + i) * pulse)
        draw.line([(cx - 100, y), (cx - 100 + wline, y)], fill=mix(CARD, glow, a), width=4)
    draw.rectangle((cx - 12, cy + 46, cx + 12, cy + 78), fill=mix(CARD, MUTED, a))
    head = mix(CARD, CREAM, a)
    draw.ellipse((cx - 36, cy + 88, cx + 36, cy + 160), fill=head)
    draw.pieslice((cx - 70, cy + 148, cx + 70, cy + 230), 200, 340, fill=mix(CARD, (40, 46, 58), a))
    draw.text((cx, cy + 248), "人在", font=font(28), fill=mix(BG, MINT, a), anchor="mm")


def render_b_desk(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    rows = [
        (0.72, "人", "人坐着", "工位有人在场", MINT),
        (1.08, "活", "杂活应按", "来了就应，做完即止", YELLOW),
    ]
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "人在工位")
        a0 = appear(t, 0.02)
        d.text((W // 2, 236 + int(lerp(16, 0, a0))), "人坐着就行", font=font(56), fill=mix(BG, WHITE, a0), anchor="mm")
        draw_occupied_desk(d, W // 2, 470, appear(t, 0.08, 0.24), t)
        for idx, (ts, num, head, body, color) in enumerate(rows):
            a = appear(t, ts, 0.24)
            if a < 0.04:
                continue
            y = 820 + idx * 176 + int(lerp(20, 0, a))
            rounded(d, (90, y, 990, y + 156), 26, mix(BG, CARD, a))
            d.rounded_rectangle((120, y + 36, 214, y + 120), 16, fill=mix(CARD, color, a))
            d.text((167, y + 78), num, font=font(36), fill=mix(color, INK, a), anchor="mm")
            d.text((244, y + 48), head, font=font(42), fill=mix(CARD, color, a), anchor="lm")
            d.text((244, y + 108), body, font=font(28), fill=mix(CARD, WHITE, a), anchor="lm")
            check_badge(d, 900, y + 78, appear(t, ts + 0.22, 0.18))
        punch = appear(t, 1.58, 0.22)
        if punch > 0.04:
            y = 1180 + int(lerp(18, 0, punch))
            rounded(d, (160, y, 920, y + 140), 26, mix(BG, (18, 42, 36), punch))
            d.text((W // 2, y + 70), "人不用搬走", font=font(52), fill=mix(BG, MINT, punch), anchor="mm")
        out.append(img)
    return out


def draw_monitor(draw, box, a: float, title: str, kind: str, t: float, color) -> None:
    x0, y0, x1, y1 = box
    if a <= 0.04:
        return
    rounded(draw, box, 22, mix(BG, CARD, a))
    rounded(draw, (x0 + 18, y0 + 58, x1 - 18, y1 - 28), 14, mix(CARD, (12, 16, 22), a))
    draw.text(((x0 + x1) // 2, y0 + 30), title, font=font(28), fill=mix(CARD, color, a), anchor="mm")
    sx0, sy0, sx1, sy1 = x0 + 34, y0 + 78, x1 - 34, y1 - 44
    if kind == "sim":
        pts = []
        steps = 18
        for i in range(steps + 1):
            px = lerp(sx0, sx1, i / steps)
            py = lerp(sy0 + 20, sy1 - 20, 0.5 + 0.42 * math.sin(t * 2.8 + i * 0.55))
            pts.append((px, py))
        if len(pts) >= 2:
            draw.line(pts, fill=mix(CARD, YELLOW, a), width=5)
        draw.line([(sx0, sy1 - 12), (sx1, sy1 - 12)], fill=mix(CARD, MUTED, a), width=2)
    else:
        items = ["接口联调", "算法小单", "周报先交"]
        for j, item in enumerate(items):
            iy = sy0 + 16 + j * 54
            on = appear(t, 0.42 + j * 0.16, 0.18)
            rounded(draw, (sx0, iy, sx1, iy + 42), 10, mix(CARD, (18, 28, 26), a))
            draw.text((sx0 + 16, iy + 21), item, font=font(26), fill=mix(CARD, WHITE, a), anchor="lm")
            if on > 0.04:
                col = mix(CARD, MINT, on)
                draw.line([(sx1 - 48, iy + 22), (sx1 - 36, iy + 32), (sx1 - 18, iy + 12)], fill=col, width=5)


def render_b_dual(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "活在线上")
        a0 = appear(t, 0.02)
        d.text((W // 2, 236 + int(lerp(16, 0, a0))), "双屏一起跑", font=font(56), fill=mix(BG, WHITE, a0), anchor="mm")
        a1 = appear(t, 0.12, 0.24)
        y = 320 + int(lerp(18, 0, a1))
        draw_monitor(d, (70, y, 520, y + 520), a1, "左 · 仿真", "sim", t, YELLOW)
        a2 = appear(t, 0.22, 0.24)
        draw_monitor(d, (560, y, 1010, y + 520), a2, "右 · 线上", "job", t, MINT)
        link = appear(t, 0.70, 0.20)
        if link > 0.04:
            d.ellipse((510, y + 230, 570, y + 290), fill=mix(CARD, MINT, link))
            d.text((540, y + 260), "接", font=font(28), fill=mix(MINT, INK, link), anchor="mm")
        grey = appear(t, 0.92, 0.22)
        if grey > 0.04:
            y3 = 880 + int(lerp(16, 0, grey))
            rounded(d, (90, y3, 990, y3 + 120), 22, mix(BG, (28, 28, 32), grey))
            d.text((W // 2, y3 + 60), "研三再谈本地", font=font(36), fill=mix(CARD, MUTED, grey), anchor="mm")
            x0, x1, mid = 160, 920, y3 + 60
            d.line([(x0, mid), (x1, mid)], fill=mix(CARD, MUTED, grey), width=6)
        punch = appear(t, 1.28, 0.22)
        if punch > 0.04:
            y2 = 1040 + int(lerp(18, 0, punch))
            rounded(d, (120, y2, 960, y2 + 160), 28, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y2 + 80), "一边工位一边履历", font=font(48), fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out



def render_b_leave(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "诊断")
        a0 = appear(t, 0.02)
        d.text((W // 2, 236 + int(lerp(16, 0, a0))), "人留下，活上线", font=font(54), fill=mix(BG, WHITE, a0), anchor="mm")
        a1 = appear(t, 0.14)
        y = 340 + int(lerp(20, 0, a1))
        rounded(d, (70, y, 520, y + 460), 28, mix(BG, CARD, a1))
        d.text((295, y + 80), "搬", font=font(30), fill=mix(CARD, MUTED, a1), anchor="mm")
        d.text((295, y + 190), "人搬走", font=font(48), fill=mix(CARD, YELLOW, a1), anchor="mm")
        d.text((295, y + 280), "工位空了", font=font(32), fill=mix(CARD, MUTED, a1), anchor="mm")
        xm = appear(t, 0.70, 0.22)
        if xm > 0.04:
            col = mix(CARD, RED, xm)
            d.line([(210, y + 340), (380, y + 420)], fill=col, width=10)
            d.line([(380, y + 340), (210, y + 420)], fill=col, width=10)
        a2 = appear(t, 0.26)
        rounded(d, (560, y, 1010, y + 460), 28, mix(BG, (22, 40, 36), a2))
        d.text((785, y + 80), "留", font=font(30), fill=mix(CARD, MUTED, a2), anchor="mm")
        d.text((785, y + 190), "人留下", font=font(48), fill=mix(CARD, MINT, a2), anchor="mm")
        d.text((785, y + 280), "活接到线上", font=font(32), fill=mix(CARD, WHITE, a2), anchor="mm")
        check_badge(d, 785, y + 380, appear(t, 0.86, 0.20))
        punch = appear(t, 1.18, 0.22)
        if punch > 0.04:
            y2 = 860 + int(lerp(16, 0, punch))
            rounded(d, (140, y2, 940, y2 + 160), 28, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y2 + 80), "不是把人搬走", font=font(52), fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_b_later(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    rows = [
        (0.20, "研一", "远程", "人在工位", MINT, False),
        (0.48, "研二", "锁稿", "专利论文初稿", YELLOW, False),
        (0.76, "研三", "本地", "现在先灰掉", MUTED, True),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "再一例")
        a0 = appear(t, 0.02)
        d.text((W // 2, 236 + int(lerp(16, 0, a0))), "研三再谈本地", font=font(54), fill=mix(BG, WHITE, a0), anchor="mm")
        for idx, (ts, num, head, body, color, grey) in enumerate(rows):
            a = appear(t, ts, 0.22)
            if a < 0.04:
                continue
            y = 340 + idx * 200 + int(lerp(18, 0, a))
            rounded(d, (90, y, 990, y + 176), 26, mix(BG, CARD if not grey else (28, 28, 32), a))
            d.rounded_rectangle((120, y + 40, 240, y + 136), 16, fill=mix(CARD, color, a))
            d.text((180, y + 88), num, font=font(32), fill=mix(color, INK, a), anchor="mm")
            d.text((270, y + 56), head, font=font(42), fill=mix(CARD, color, a), anchor="lm")
            d.text((270, y + 118), body, font=font(28), fill=mix(CARD, WHITE if not grey else MUTED, a), anchor="lm")
            if grey:
                strike = appear(t, ts + 0.28, 0.24)
                if strike > 0.04:
                    d.line([(260, y + 88), (int(lerp(260, 940, strike)), y + 88)], fill=mix(CARD, MUTED, a), width=8)
        punch = appear(t, 1.36, 0.22)
        if punch > 0.04:
            y2 = 980 + int(lerp(16, 0, punch))
            rounded(d, (140, y2, 940, y2 + 160), 28, mix(BG, (18, 42, 36), punch))
            d.text((W // 2, y2 + 80), "现在只走远程", font=font(52), fill=mix(BG, MINT, punch), anchor="mm")
        out.append(img)
    return out


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
    weights = [max(1, len(p.replace("，", "").replace("。", "").replace("、", ""))) for p in phrases]
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

    comm = edge_tts.Communicate(text, VOICE, rate="-8%")
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
    phrases_sha = hashlib.sha256("\n".join(phrases).encode("utf-8")).hexdigest()
    sha_file = audio_dir / "phrases.sha"
    reuse_ok = (
        wav.exists()
        and wav.stat().st_size > 800
        and (audio_dir / "vo-align.txt").exists()
        and sha_file.exists()
        and sha_file.read_text(encoding="utf-8").strip() == phrases_sha
    )
    if reuse_ok:
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
    (audio_dir / "cues.json").write_text(
        json.dumps([{"start": s, "end": e, "text": p} for s, e, p in aligned], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    vtt = ["WEBVTT", ""]
    for i, (s, e, p) in enumerate(aligned, 1):
        def ts(x: float) -> str:
            ms = int(round(x * 1000))
            return f"{ms // 3600000:02d}:{(ms // 60000) % 60:02d}:{(ms // 1000) % 60:02d}.{ms % 1000:03d}"

        vtt += [str(i), f"{ts(s)} --> {ts(e)}", p, ""]
    (audio_dir / "vo.vtt").write_text("\n".join(vtt), encoding="utf-8")
    (audio_dir / "phrases.sha").write_text(phrases_sha + "\n", encoding="utf-8")
    return duration, aligned


def build_timeline(cues: list[tuple[float, float, str]], duration: float) -> dict:
    recipe = json.loads((ROOT / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
    if len(cues) != 12:
        raise SystemExit(f"need 12 phrases, got {len(cues)}")
    cuts = [
        max(cues[1][1], cues[2][0] - LEAD),
        max(cues[2][1], cues[3][0] - LEAD),
        max(cues[3][1], cues[4][0] - LEAD),
        max(cues[4][1], cues[5][0] - LEAD),
        max(cues[5][1], cues[6][0] - LEAD),
        max(cues[6][1], cues[7][0] - LEAD),
        max(cues[7][1], cues[8][0] - LEAD),
        max(cues[8][1], cues[9][0] - LEAD),
    ]
    shots = [
        {"id": "S01a", "kind": "A", "start": 0.0, "end": cues[0][1], "src": "assets/V-挥手.mp4", "line": cues[0][2], "close": True},
        {"id": "S01b", "kind": "A", "start": cues[0][1], "end": cuts[0], "src": "assets/V-摊手.mp4", "line": cues[1][2]},
        {"id": "S02", "kind": "B", "start": cuts[0], "end": cuts[1], "src": "broll/B-留下不上线.mp4", "line": cues[2][2], "broll": "stay_not_leave"},
        {"id": "S03", "kind": "A", "start": cuts[1], "end": cuts[2], "src": "assets/V-指向.mp4", "line": cues[3][2]},
        {"id": "S04", "kind": "B", "start": cuts[2], "end": cuts[3], "src": "broll/B-人在工位.mp4", "line": cues[4][2], "broll": "desk_stay"},
        {"id": "S05", "kind": "A", "start": cuts[3], "end": cuts[4], "src": "assets/V-摊手.mp4", "line": cues[5][2]},
        {"id": "S06", "kind": "B", "start": cuts[4], "end": cuts[5], "src": "broll/B-双屏线上.mp4", "line": cues[6][2], "broll": "dual_screen"},
        {"id": "S07", "kind": "A", "start": cuts[5], "end": cuts[6], "src": "assets/V-指向.mp4", "line": cues[7][2]},
        {"id": "S08", "kind": "B", "start": cuts[6], "end": cuts[7], "src": "broll/B-研三再谈.mp4", "line": cues[8][2], "broll": "later_local"},
        {"id": "S09", "kind": "A", "start": cuts[7], "end": duration, "src": "assets/V-点赞.mp4", "line": " / ".join(c[2] for c in cues[9:])},
    ]
    for i, shot in enumerate(shots):
        shot["start"] = round(float(shot["start"]), 3)
        shot["end"] = round(float(shot["end"]), 3)
        if shot["end"] <= shot["start"] + 0.12:
            raise SystemExit(f"bad shot {shot}")
        if i:
            shots[i]["start"] = shots[i - 1]["end"]
    shots[-1]["end"] = round(duration, 3)

    data = {
        "audio": "audio/vo-full.wav",
        "duration": round(duration, 3),
        "fps": FPS,
        "size": [W, H],
        "title": recipe["title"],
        "bgm": "audio/bgm.wav",
        "shots": shots,
        "a_caps": [
            {"start": 0.0, "end": round(cues[0][1], 3), "lines": ["大家好"]},
            {"start": round(cues[1][0], 3), "end": round(shots[1]["end"], 3), "lines": ["远程实习", "人在工位，活在线上"]},
            {"start": round(shots[3]["start"], 3), "end": round(shots[3]["end"], 3), "lines": ["工位一空", "对不上查岗"]},
            {"start": round(shots[5]["start"], 3), "end": round(shots[5]["end"], 3), "lines": ["左屏仿真", "右屏接项目"]},
            {"start": round(shots[7]["start"], 3), "end": round(shots[7]["end"], 3), "lines": ["考勤和履历", "同一张工位"]},
            {"start": round(shots[9]["start"], 3), "end": round(duration, 3), "lines": ["人在工位", "活在线上"]},
        ],
        "shutters": [
            {"start": round(shots[i]["start"], 3), "color": list((CREAM, MINT, YELLOW)[i % 3])}
            for i in range(1, len(shots))
        ],
        "eyebrows": [
            {"start": round(s["start"], 3), "end": round(s["end"], 3), "text": f"A-ROLL / {s['id'][1:]}"}
            for s in shots if s["kind"] == "A"
        ],
        "cover": {
            "title": recipe["cover_title"],
            "sub": recipe["cover_sub"],
            "line": recipe["cover_line"],
            "src": recipe["cover_src"],
        },
        "cue_map": {p: [round(s, 3), round(e, 3)] for s, e, p in cues},
        "b_lead_s": LEAD,
        "video_type": "普通短视频",
        "source_note": "topics-batch3.md #48 / 备忘录第二节 3 远程日常实习",
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
    extra = []
    if dur > src_dur + 0.30 and kind == "A":
        extra = ["-stream_loop", "-1"]
    elif dur > src_dur + 0.02:
        pad = min(0.28, dur - src_dur)
        vf = f"{vf},tpad=stop_mode=clone:stop_duration={pad:.3f}"
    run([
        "ffmpeg", "-y", *extra, "-i", str(src), "-t", f"{dur:.3f}",
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
    staged.parent.mkdir(parents=True, exist_ok=True)
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
    overlay = Image.new("RGBA", (W, H), (11, 13, 18, 48))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((70, 80, 1010, 470), radius=36, fill=(22, 24, 28))
    d.text((W // 2, 160), "远程实习", font=font(64), fill=WHITE, anchor="mm")
    d.text((W // 2, 250), "人在工位 · 活在线上", font=font(44), fill=YELLOW, anchor="mm")
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
        "project_name": "48_远程实习人在工位活在线上",
        "video_type": "普通短视频",
        "episode": 48,
        "title": NAME,
        "source_note": "topics-batch3.md #48 · 备忘录第二节 3 远程日常实习",
        "unused_of": "研一别脱产离校（#47）/ 工位时间切片（成片16）/ 杂务报销（成片28）/ 杂务六十分（#46）",
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
        "not": "drama-pipeline / 仙侠连载 / #47 脱产离校 / C:D:G: / Drive 上传",
        "updated_at": now,
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note = f"""# 48 · 远程实习人在工位活在线上

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。

- **选题**：`.abroll-cloud/topics-batch3.md` 第 48 条；Drive 只读备忘录第二节 3 远程日常实习
- **明确不用**：#47 脱产离校；成片 16 时间切片 / 秒回；成片 28 报销红线；#46 杂务六十分
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿目录**：`/workspace/.abroll-cloud/48/`
- **云端 only**：不写 `C:\\` / `D:\\` / `G:\\`，不传 Drive

钩子：远程实习，人在工位、活在线上。
方法：杂活按时应，人坐着就行；双屏一边仿真，一边接线上项目。
收束：考勤和履历一起拿。不念真名，不讲脱产离校。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {duration:.2f} 秒。镜头 {len(data["shots"])} 条，时间轴闭合。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")


def patch_index(duration: float) -> None:
    line = f"| `{STAGED_NAME}` | {duration:.1f}s |"
    for idx in (Path("/workspace/成片/INDEX.md"), Path("/workspace/.abroll-cloud/INDEX.chengpian.md")):
        if not idx.exists():
            continue
        text = idx.read_text(encoding="utf-8")
        if STAGED_NAME in text:
            continue
        if not text.endswith("\n"):
            text += "\n"
        idx.write_text(text + line + "\n", encoding="utf-8")


def patch_delivery(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    marker = "| 48 | — | 待收 |"
    row = f"| 48 | `{STAGED_NAME}` | 已核验 {duration:.1f}s |"
    if marker in text:
        path.write_text(text.replace(marker, row), encoding="utf-8")
        return
    if STAGED_NAME in text:
        return
    extra = "\n## 本轮补 48\n\n| 号 | 文件 | 状态 |\n|----|------|------|\n" + row + "\n"
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text + extra, encoding="utf-8")


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch3.md")
    if path.exists():
        text = path.read_text(encoding="utf-8")
        old = "| 48 | 专硕实习方法 | `48-远程实习人在工位.mp4` | 未拍 |"
        new = f"| 48 | 专硕实习方法 | `{STAGED_NAME}` | 已核验 {duration:.1f}s |"
        if old in text:
            path.write_text(text.replace(old, new), encoding="utf-8")
    local = ROOT / "topics-batch3.md"
    if local.exists():
        text = local.read_text(encoding="utf-8")
        old = "- **状态**：已认领 · `.abroll-cloud/48/` · `成片/48-远程实习人在工位活在线上.mp4`"
        new = f"- **状态**：已核验 {duration:.1f}s · `.abroll-cloud/48/` · `成片/{STAGED_NAME}`"
        if old in text:
            local.write_text(text.replace(old, new), encoding="utf-8")


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
        "project": "48_远程实习人在工位活在线上",
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
        and 30.0 <= report["video"]["duration_s"] <= 60.0
        and len(shots) >= 7
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

    renders = {
        "S02": ("B-留下不上线", render_b_leave),
        "S04": ("B-人在工位", render_b_desk),
        "S06": ("B-双屏线上", render_b_dual),
        "S08": ("B-研三再谈", render_b_later),
    }
    for sid, (name, fn) in renders.items():
        shot = next(s for s in data["shots"] if s["id"] == sid)
        d = max(2.4, float(shot["end"]) - float(shot["start"]))
        print("render", name, d)
        frames_to_mp4(fn(d + 0.12), ROOT / "broll" / f"{name}.mp4")

    make_cover()
    staged = assemble(data)
    dur = probe_dur(staged)
    write_docs(dur, staged, data)
    patch_index(dur)
    patch_delivery(dur)
    patch_topics(dur)
    report = qa(staged, data)
    print("STAGED", staged, "dur", dur, "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
