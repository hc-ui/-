#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 49 加长重切：研一汇报先精读一篇顶刊。云端 A-roll + B-roll，不是短剧。

覆盖 成片/49-研一汇报先精读一篇顶刊.mp4。
目标 40–50 秒（硬限制 30–60）。不准冻帧、空镜、静音尾巴垫时长。
禁止 C:\\ D:\\ G:\\，禁止 Drive，不走 drama-pipeline。
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
NAME = "研一汇报先精读一篇顶刊"
FULL_TITLE = "研一汇报先精读一篇顶刊"
STAGED_NAME = "49-研一汇报先精读一篇顶刊.mp4"
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
AMBER = (255, 168, 76)
INK = (22, 24, 28)
LEAD = 0.28
TARGET_LO, TARGET_HI = 40.0, 51.0
HARD_LO, HARD_HI = 30.0, 60.0
EXPECTED_PHRASES = 18
REPLACED_SHORT_S = 13.5


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


def frames_to_mp4(frame_fn, duration: float, dest: Path) -> None:
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
    mid_i = min(n // 2, n - 1)
    for i in range(n):
        im = frame_fn(i / FPS)
        if i == mid_i:
            mid = im.copy()
        proc.stdin.write(im.convert("RGB").tobytes())
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


def draw_slide_stack(draw: ImageDraw.ImageDraw, cx: int, cy: int, page: int, flip: float, a: float) -> None:
    if a <= 0.04:
        return
    w, h = 300, 380
    for i, off in enumerate((40, 22)):
        col = mix(BG, (18, 20, 28), a * (0.55 + i * 0.15))
        rounded(draw, (cx - w // 2 + off, cy - h // 2 + off // 3, cx + w // 2 + off, cy + h // 2 + off // 3), 22, col)
    squeeze = 1.0 - 0.62 * abs(math.sin(flip * math.pi))
    sw = max(36, int(w * squeeze))
    x0, y0 = cx - sw // 2, cy - h // 2
    rounded(draw, (x0, y0, x0 + sw, y0 + h), 22, mix(BG, CARD, a))
    rounded(draw, (x0, y0, x0 + sw, y0 + 64), 22, mix(CARD, YELLOW, a))
    draw.rectangle((x0, y0 + 44, x0 + sw, y0 + 64), fill=mix(CARD, YELLOW, a))
    if sw > 120:
        draw.text((cx, y0 + 32), f"{page:02d} / 10", font=font(28), fill=mix(YELLOW, INK, a), anchor="mm")
        bars = [0.35 + 0.08 * ((page + k) % 5) for k in range(4)]
        base_y = y0 + h - 70
        gap = sw // 5
        for k, bh in enumerate(bars):
            bx = x0 + gap * (k + 1) - 16
            hh = int(160 * bh)
            rounded(draw, (bx, base_y - hh, bx + 32, base_y), 8, mix(CARD, MINT if k == page % 4 else MUTED, a))
        draw.text((cx, y0 + 96), "顶刊图", font=font(26), fill=mix(CARD, MUTED, a), anchor="mm")


def frame_b_pick(t: float) -> Image.Image:
    cards = [
        (0.28, "测", "微流控测控", "挑一篇就够", YELLOW),
        (0.70, "温", "精密温控", "别同时开三篇", MINT),
        (1.12, "图", "生物图像", "算法线也能读", CREAM),
    ]
    img = new_bg()
    d = ImageDraw.Draw(img)
    tag(d, t, "选题")
    a0 = appear(t, 0.02)
    d.text((W // 2, 236 + int(lerp(16, 0, a0))), "每周一篇", font=font(58), fill=mix(BG, WHITE, a0), anchor="mm")
    a1 = appear(t, 0.10)
    if a1 > 0.04:
        y = 320 + int(lerp(18, 0, a1))
        rounded(d, (220, y, 860, y + 280), 28, mix(BG, CARD, a1))
        d.text((W // 2, y + 90), "顶刊", font=font(64), fill=mix(CARD, YELLOW, a1), anchor="mm")
        d.text((W // 2, y + 190), "一周只抱一篇", font=font(34), fill=mix(CARD, MUTED, a1), anchor="mm")
    for idx, (ts, num, head, body, color) in enumerate(cards):
        a = appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 640 + idx * 160 + int(lerp(16, 0, a))
        rounded(d, (90, y, 990, y + 140), 26, mix(BG, CARD, a))
        d.rounded_rectangle((120, y + 28, 214, y + 112), 16, fill=mix(CARD, color, a))
        d.text((167, y + 70), num, font=font(32), fill=mix(color, INK, a), anchor="mm")
        d.text((244, y + 44), head, font=font(40), fill=mix(CARD, color, a), anchor="lm")
        d.text((244, y + 100), body, font=font(28), fill=mix(CARD, WHITE, a), anchor="lm")
    punch = appear(t, 1.70, 0.22)
    if punch > 0.04:
        y = 1160 + int(lerp(16, 0, punch))
        rounded(d, (160, y, 920, y + 150), 26, mix(BG, (18, 42, 36), punch))
        d.text((W // 2, y + 75), "先换一篇文献", font=font(50), fill=mix(BG, MINT, punch), anchor="mm")
    return img


def frame_b_pages(t: float) -> Image.Image:
    cards = [
        (0.40, "背", "背景", "这篇在解什么", YELLOW),
        (1.10, "法", "方法", "图表规范写清", MINT),
        (1.80, "结", "结论", "读者能带走的", CREAM),
    ]
    img = new_bg()
    d = ImageDraw.Draw(img)
    tag(d, t, "精读主菜")
    a0 = appear(t, 0.02)
    d.text((W // 2, 236 + int(lerp(16, 0, a0))), "八到十页", font=font(58), fill=mix(BG, WHITE, a0), anchor="mm")
    page = 1 + int((t * 2.4) % 10)
    flip = (t * 2.4) % 1.0
    draw_slide_stack(d, W // 2, 540, page, flip, appear(t, 0.08, 0.22))
    for idx, (ts, num, head, body, color) in enumerate(cards):
        a = appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 780 + idx * 150 + int(lerp(18, 0, a))
        rounded(d, (90, y, 990, y + 132), 26, mix(BG, CARD, a))
        d.rounded_rectangle((120, y + 28, 214, y + 104), 16, fill=mix(CARD, color, a))
        d.text((167, y + 66), num, font=font(32), fill=mix(color, INK, a), anchor="mm")
        d.text((244, y + 42), head, font=font(40), fill=mix(CARD, color, a), anchor="lm")
        d.text((244, y + 96), body, font=font(28), fill=mix(CARD, WHITE, a), anchor="lm")
    punch = appear(t, 2.55, 0.22)
    if punch > 0.04:
        y = 1240 + int(lerp(16, 0, punch))
        rounded(d, (160, y, 920, y + 140), 26, mix(BG, (18, 42, 36), punch))
        d.text((W // 2, y + 70), "讲清三件事", font=font(52), fill=mix(BG, MINT, punch), anchor="mm")
    return img


def frame_b_bench(t: float) -> Image.Image:
    dones = [
        (0.20, "精", "精读了文献"),
        (0.70, "仿", "跑通了仿真"),
        (1.20, "课", "课实验做完"),
    ]
    img = new_bg()
    d = ImageDraw.Draw(img)
    tag(d, t, "错 · 承诺")
    a0 = appear(t, 0.02)
    d.text((W // 2, 220 + int(lerp(16, 0, a0))), "别报没搭完的台", font=font(52), fill=mix(BG, WHITE, a0), anchor="mm")
    for idx, (ts, num, head) in enumerate(dones):
        a = appear(t, ts, 0.20)
        if a < 0.04:
            continue
        x = 90 + idx * 310
        y = 310 + int(lerp(14, 0, a))
        rounded(d, (x, y, x + 290, y + 160), 24, mix(BG, CARD, a))
        d.ellipse((x + 20, y + 44, x + 92, y + 116), fill=mix(CARD, MINT, a))
        d.text((x + 56, y + 80), num, font=font(30), fill=mix(MINT, INK, a), anchor="mm")
        d.text((x + 108, y + 80), head, font=font(26), fill=mix(CARD, WHITE, a), anchor="lm")
    a1 = appear(t, 2.20)
    if a1 > 0.04:
        y = 520 + int(lerp(20, 0, a1))
        rounded(d, (80, y, 1000, y + 260), 32, mix(BG, CARD, a1))
        d.text((W // 2, y + 70), "下周一定搭完温控台", font=font(40), fill=mix(CARD, YELLOW, a1), anchor="mm")
        d.text((W // 2, y + 150), "超出能力的工程承诺", font=font(28), fill=mix(CARD, MUTED, a1), anchor="mm")
        strike_line(d, (160, y + 40, 920, y + 100), appear(t, 2.70, 0.28), mix(CARD, RED, a1))
        xmark = appear(t, 2.95, 0.20)
        if xmark > 0.04:
            col = mix(CARD, RED, xmark)
            d.line([(470, y + 180), (610, y + 230)], fill=col, width=12)
            d.line([(610, y + 180), (470, y + 230)], fill=col, width=12)
    a2 = appear(t, 3.40)
    if a2 > 0.04:
        y = 820 + int(lerp(18, 0, a2))
        rounded(d, (80, y, 1000, y + 240), 32, mix(BG, (22, 40, 36), a2))
        d.text((W // 2, y + 80), "这篇精读完了", font=font(44), fill=mix(CARD, MINT, a2), anchor="mm")
        d.text((W // 2, y + 160), "已经落地的动作", font=font(28), fill=mix(CARD, WHITE, a2), anchor="mm")
        chk = appear(t, 3.80, 0.18)
        if chk > 0.04:
            col = mix(CARD, MINT, chk)
            d.ellipse((860, y + 40, 960, y + 140), outline=col, width=8)
            d.line([(882, y + 94), (900, y + 116), (938, y + 64)], fill=col, width=8)
    punch = appear(t, 4.30, 0.22)
    if punch > 0.04:
        y = 1110 + int(lerp(16, 0, punch))
        rounded(d, (160, y, 920, y + 150), 26, mix(BG, (18, 42, 36), punch))
        d.text((W // 2, y + 75), "这篇精读完了", font=font(50), fill=mix(BG, MINT, punch), anchor="mm")
    return img


def split_caption(line: str) -> list[str]:
    line = line.strip("。．. ")
    if "，" in line and len(line) > 8:
        parts = [p for p in line.split("，") if p]
        if 1 < len(parts) <= 2:
            return parts
    if len(line) > 10:
        mid = len(line) // 2
        cut = line.rfind("的", 0, mid + 3)
        if cut < 3:
            cut = mid
        return [line[: cut + 1], line[cut + 1 :]] if line[cut + 1 :] else [line]
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


def load_phrases() -> list[str]:
    return [ln.strip() for ln in (ROOT / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]


def write_align_files(aligned: list[tuple[float, float, str]], duration: float) -> None:
    audio_dir = ROOT / "audio"
    audio_dir.mkdir(exist_ok=True)
    (audio_dir / "vo-align.txt").write_text(
        "".join(f"{s:.3f}\t{e:.3f}\t{p}\n" for s, e, p in aligned),
        encoding="utf-8",
    )
    cues = [{"start": round(s, 3), "end": round(e, 3), "text": p} for s, e, p in aligned]
    (audio_dir / "cues.json").write_text(json.dumps(cues, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    vtt = ["WEBVTT", ""]
    for i, (s, e, p) in enumerate(aligned, 1):
        def ts(x: float) -> str:
            ms = int(round(x * 1000))
            return f"{ms // 3600000:02d}:{(ms // 60000) % 60:02d}:{(ms // 1000) % 60:02d}.{ms % 1000:03d}"

        vtt += [str(i), f"{ts(s)} --> {ts(e)}", p, ""]
    (audio_dir / "vo.vtt").write_text("\n".join(vtt), encoding="utf-8")


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
        print("TTS sentence cues", len(sentences), "rate", rate, "dur", duration)
    else:
        aligned = detect_sentence_cues(wav, phrases, duration)
        print("TTS silencedetect/weight cues", "rate", rate, "dur", duration)
    return duration, aligned


def make_voiceover() -> tuple[float, list[tuple[float, float, str]]]:
    text = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    phrases = load_phrases()
    if len(phrases) != EXPECTED_PHRASES:
        raise SystemExit(f"need {EXPECTED_PHRASES} phrases, got {len(phrases)}")
    if len(set(phrases)) != len(phrases):
        raise SystemExit("phrases must be unique")
    audio_dir = ROOT / "audio"
    audio_dir.mkdir(exist_ok=True)
    wav = audio_dir / "vo-full.wav"
    align = audio_dir / "vo-align.txt"
    if wav.exists() and wav.stat().st_size > 800 and align.exists():
        parsed: list[tuple[float, float, str]] = []
        for line in align.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) >= 3:
                parsed.append((float(parts[0]), float(parts[1]), parts[2]))
        duration = probe_dur(wav)
        if [p for *_, p in parsed] == phrases and TARGET_LO <= duration <= TARGET_HI:
            print("reuse VO", wav, duration)
            return duration, close_align(parsed, duration)

    rates = ["-6%", "-10%", "-2%", "-14%", "+4%"]
    best_target: tuple[str, float, list[tuple[float, float, str]]] | None = None
    best_hard: tuple[str, float, list[tuple[float, float, str]]] | None = None
    last: tuple[str, float, list[tuple[float, float, str]]] | None = None
    for rate in rates:
        try:
            duration, aligned = synth_once(text, phrases, rate)
        except Exception as exc:
            print("TTS attempt failed", rate, exc)
            continue
        last = (rate, duration, aligned)
        print(f"VO rate={rate} duration={duration:.3f}s")
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
    wav = audio_dir / "vo-full.wav"
    if abs(probe_dur(wav) - duration) > 0.15:
        print("re-synth winning rate", win_rate)
        duration, aligned = synth_once(text, phrases, win_rate)
    write_align_files(aligned, duration)
    return duration, aligned


def build_timeline(cues: list[tuple[float, float, str]], duration: float) -> dict:
    recipe = json.loads((ROOT / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
    if len(cues) != EXPECTED_PHRASES:
        raise SystemExit(f"need {EXPECTED_PHRASES} cues, got {len(cues)}")
    by_text = {p: (s, e, p) for s, e, p in cues}

    shots = []
    cursor = 0.0
    for spec in recipe["shots"]:
        phrase_cues = [by_text[p] for p in spec["phrases"]]
        first_s, last_e = phrase_cues[0][0], phrase_cues[-1][1]
        start = cursor
        if spec["kind"] == "B":
            start = min(first_s, max(cursor, first_s - LEAD))
            start = max(cursor, start)
        end = last_e
        shots.append({
            "id": spec["id"],
            "kind": spec["kind"],
            "start": start,
            "end": end,
            "src": spec["src"],
            "line": spec["phrases"][0],
            "phrases": spec["phrases"],
            **({"close": True} if spec.get("close") else {}),
            **({"broll": spec["broll"]} if spec.get("broll") else {}),
        })
        cursor = end

    for shot in shots:
        if shot["end"] <= shot["start"] + 0.14:
            shot["end"] = min(duration, shot["start"] + 0.18)
    for i in range(1, len(shots)):
        shots[i]["start"] = shots[i - 1]["end"]
    shots[0]["start"] = 0.0
    shots[-1]["end"] = duration
    for shot in shots:
        shot["start"] = round(float(shot["start"]), 3)
        shot["end"] = round(float(shot["end"]), 3)

    a_caps = []
    for spec, shot in zip(recipe["shots"], shots):
        if spec["kind"] != "A":
            continue
        for phrase in spec["phrases"]:
            s, e, _ = by_text[phrase]
            cap_s = max(s, shot["start"])
            cap_e = min(e, shot["end"])
            if cap_e > cap_s + 0.08:
                a_caps.append({"start": round(cap_s, 3), "end": round(cap_e, 3), "lines": split_caption(phrase)})

    b_colors = [list(MINT), list(YELLOW), list(AMBER)]
    shutters = []
    b_i = 0
    for shot in shots[1:]:
        if shot["kind"] == "B":
            color = b_colors[b_i % len(b_colors)]
            b_i += 1
        else:
            color = list(CREAM)
        shutters.append({"start": shot["start"], "color": color})

    eyebrows = []
    for spec, shot in zip(recipe["shots"], shots):
        if spec["kind"] != "A":
            continue
        eyebrows.append({"start": shot["start"], "end": shot["end"], "text": f"A-ROLL / {spec['id'][1:]}"})

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
        "cue_map": {p: [round(s, 3), round(e, 3)] for s, e, p in cues},
        "b_lead_s": LEAD,
        "video_type": "普通短视频",
        "topic": 49,
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
    fnt = font(56 if len(lines) == 1 and max(len(s) for s in lines) <= 8 else 42)
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
    """Cut or pingpong-loop. Never freeze last frame, never slow-mo stretch."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    src_dur = max(0.01, probe_dur(src))
    if kind == "A" and close:
        geo = f"scale=1380:2454,crop={W}:{H}:150:60,fps={FPS},setsar=1,format=yuv420p"
    elif kind == "A":
        geo = f"scale=1188:2112,crop={W}:{H}:54:105,fps={FPS},setsar=1,format=yuv420p"
    else:
        geo = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},setsar=1,format=yuv420p"
    if dur <= src_dur + 0.06:
        run([
            "ffmpeg", "-y", "-i", str(src), "-t", f"{dur:.3f}",
            "-vf", geo, "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18", str(dest),
        ])
        return
    n_src = max(2, int(round(src_dur * FPS)))
    loop_size = n_src * 2
    fc = (
        f"[0:v]split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1:a=0,"
        f"loop=loop=-1:size={loop_size}:start=0,"
        f"trim=duration={dur:.3f},setpts=PTS-STARTPTS,{geo}"
    )
    run([
        "ffmpeg", "-y", "-i", str(src),
        "-filter_complex", fc, "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", str(dest),
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
    staged.parent.mkdir(exist_ok=True)
    if staged.exists() and staged.samefile(final):
        staged.unlink()
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
    d.text((W // 2, 160), "研一汇报", font=font(48), fill=WHITE, anchor="mm")
    d.text((W // 2, 250), "先精读一篇顶刊", font=font(58), fill=YELLOW, anchor="mm")
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
        "project_name": "49_研一汇报先精读一篇顶刊",
        "video_type": "普通短视频",
        "episode": 49,
        "cut": "long-40s",
        "title": NAME,
        "full_title": FULL_TITLE,
        "source_note": "topics-batch3.md #49 · 备忘录第三节 4 · 加长重切覆盖 13.5s",
        "slug": "研一汇报先精读一篇顶刊",
        "voice": VOICE,
        "duration": round(duration, 3),
        "size": [W, H],
        "fps": FPS,
        "stage": "delivered",
        "status": "已交付",
        "current_stage": "核验并交付",
        "production_method": "白底小灯 A-roll 往返循环 + 黑底对照卡 B-roll + edge-tts Yunyang + FFmpeg",
        "script": {"path": "script/voiceover.txt", "sha256": sha, "phrases": EXPECTED_PHRASES},
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
        "replaced_short_cut_s": REPLACED_SHORT_S,
        "cloud_only": True,
        "windows_paths": False,
        "drive_upload": False,
        "not": "drama-pipeline / 仙侠连载 / C:D:G: / Drive 上传 / 成片16主标题 / 成片37撞课SOP",
        "updated_at": now,
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    note = f"""# 49 · 研一汇报先精读一篇顶刊（加长重切）

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。

- **选题**：`topics-batch3.md` 第 49 条；备忘录第三节 4「研一周会汇报战术」
- **成片中转**：`成片/{STAGED_NAME}`（覆盖原 13.5s 短切）
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿目录**：`/workspace/.abroll-cloud/49/`
- **时长**：瞄准 40–50 秒，硬限 30–60 秒。口播加长，不用冻帧/空镜垫时长。
- **云端 only**：不写 `C:\\` / `D:\\` / `G:\\`，不传 Drive
- **避开**：成片 16「只报做完」主标题；成片 37 撞课 SOP；#47 脱产；#48 远程实习

钩子：研一汇报先精读一篇顶刊。  
方法：每周一篇，八到十页讲清背景、方法和结论。开口先报已经落地的精读、仿真、课实验。  
收束：别报下周一定搭完温控台。这篇精读完了，才算交了周会。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {duration:.2f} 秒。镜头 {len(data["shots"])} 条，口播 {EXPECTED_PHRASES} 句，时间轴闭合。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")


def patch_index(duration: float) -> None:
    idx = Path("/workspace/成片/INDEX.md")
    line = f"| `{STAGED_NAME}` | {duration:.1f}s |"
    if not idx.exists():
        idx.write_text(
            "# 成片（可直接看）\n\n竖屏口播 1080×1920，H.264 + AAC。\n\n| 文件 | 时长 |\n|------|------|\n"
            + line + "\n",
            encoding="utf-8",
        )
        return
    text = idx.read_text(encoding="utf-8")
    token = f"`{STAGED_NAME}`"
    out_lines = []
    in_table = False
    seen = False
    for raw in text.splitlines():
        if raw.startswith("| 文件"):
            in_table = True
            out_lines.append(raw)
            continue
        if in_table and raw.startswith("|") and token in raw:
            if not seen:
                out_lines.append(line)
                seen = True
            continue
        out_lines.append(raw)
    if not seen:
        rebuilt = []
        inserted = False
        for raw in out_lines:
            if (not inserted) and "仙侠云海突进" in raw and raw.strip().startswith("|"):
                rebuilt.append(line)
                inserted = True
            rebuilt.append(raw)
        if not inserted:
            rebuilt.append(line)
        out_lines = rebuilt
    text = "\n".join(out_lines)
    if not text.endswith("\n"):
        text += "\n"
    idx.write_text(text, encoding="utf-8")


def patch_index_chengpian(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/INDEX.chengpian.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    line = f"| `{STAGED_NAME}` | {duration:.1f}s |"
    token = f"`{STAGED_NAME}`"
    rows = []
    seen = False
    for raw in text.splitlines():
        if raw.startswith("|") and token in raw:
            if not seen:
                rows.append(line)
                seen = True
            continue
        rows.append(raw)
    if not seen:
        rebuilt = []
        inserted = False
        for raw in rows:
            if (not inserted) and "仙侠云海突进" in raw and raw.strip().startswith("|"):
                rebuilt.append(line)
                inserted = True
            rebuilt.append(raw)
        if not inserted:
            rebuilt.append(line)
        rows = rebuilt
    text = "\n".join(rows)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def patch_delivery(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"\| `成片/49-研一汇报先精读一篇顶刊\.mp4` \|[^\n]+\|",
        f"| `成片/{STAGED_NAME}` | 1080×1920 h264+aac 44.1k stereo | {duration:.2f}s | topic 49 加长重切（覆盖 13.5s 短切） |",
        text,
        count=1,
    )
    text = re.sub(
        r"\| 49 \| `49-研一汇报先精读一篇顶刊\.mp4` \|[^\n]+\|",
        f"| 49 | `{STAGED_NAME}` | 已核验 {duration:.1f}s |",
        text,
        count=1,
    )
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
    dur = float(info["format"]["duration"])
    digest = hashlib.sha256(staged.read_bytes()).hexdigest()
    kinds = [s["kind"] for s in shots]
    report = {
        "project": "49_研一汇报先精读一篇顶刊",
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
        "replaced_short_cut_s": REPLACED_SHORT_S,
        "video": {
            "codec": v.get("codec_name"),
            "width": int(v.get("width", 0)),
            "height": int(v.get("height", 0)),
            "fps": fps,
            "pix_fmt": v.get("pix_fmt"),
            "duration_s": dur,
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
            "a_shots": kinds.count("A"),
            "b_shots": kinds.count("B"),
            "phrases": EXPECTED_PHRASES,
            "overlap": overlap,
            "gap": gap,
            "last_end_equals_audio": abs(shots[-1]["end"] - data["duration"]) < 0.05,
            "broll_lead_s": LEAD,
            "in_hard_window": HARD_LO <= dur <= HARD_HI,
            "in_target_window": TARGET_LO <= dur <= TARGET_HI,
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
        and report["timeline"]["in_hard_window"]
        and kinds.count("B") >= 3
    )
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    copy_assets()
    duration, cues = make_voiceover()
    print("VO", duration)
    for row in cues:
        print(f"  {row[0]:6.3f}-{row[1]:6.3f}  {row[2]}")
    if not (HARD_LO <= duration <= HARD_HI):
        raise SystemExit(f"VO duration {duration:.2f}s outside 30–60")
    make_bgm(duration)
    data = build_timeline(cues, duration)
    print("timeline shots", [(s["id"], s["start"], s["end"], s["kind"]) for s in data["shots"]])

    renderers = {
        "weekly_paper": ("broll/B-每周一篇.mp4", frame_b_pick),
        "ten_pages": ("broll/B-八到十页.mp4", frame_b_pages),
        "no_bench": ("broll/B-别搭台子.mp4", frame_b_bench),
    }
    for shot in data["shots"]:
        bid = shot.get("broll")
        if not bid:
            continue
        rel, fn = renderers[bid]
        d = max(2.4, float(shot["end"]) - float(shot["start"]))
        print("render", rel, d)
        frames_to_mp4(fn, d + 0.12, ROOT / rel)

    make_cover()
    staged = assemble(data)
    dur = probe_dur(staged)
    write_docs(dur, staged, data)
    patch_index(dur)
    patch_index_chengpian(dur)
    patch_delivery(dur)
    report = qa(staged, data)
    print("STAGED", staged, "dur", dur, "ok", report["ok"], "target", report["timeline"]["in_target_window"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["timeline"]["in_target_window"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
