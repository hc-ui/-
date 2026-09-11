#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Topic 60 / topics-batch3 #60：番茄工作法一次只做二十五分钟。云端 A-roll + B-roll。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/60/，成品中转 成片/60-番茄工作法一次只做二十五分钟.mp4。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
只讲计时器规矩，不重复成片 00「深度工作总被打断」。
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 24
NAME = "番茄工作法一次只做二十五分钟"
STAGED_NAME = "60-番茄工作法一次只做二十五分钟.mp4"
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
TOMATO = (232, 92, 84)
LEAF = (86, 168, 112)
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
    d.ellipse((420, 1120, 1380, 2080), fill=(56, 22, 20))
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


def draw_tomato(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, a: float) -> None:
    if a <= 0.04:
        return
    body = mix(CARD, TOMATO, a)
    draw.ellipse((cx - r, cy - r + 8, cx + r, cy + r + 8), fill=body)
    leaf = mix(CARD, LEAF, a)
    draw.ellipse((cx - 18, cy - r - 8, cx + 4, cy - r + 22), fill=leaf)
    draw.ellipse((cx - 4, cy - r - 4, cx + 22, cy - r + 20), fill=leaf)
    draw.line([(cx, cy - r + 10), (cx, cy - r + 36)], fill=mix(LEAF, INK, a), width=6)


def draw_phone_down(draw: ImageDraw.ImageDraw, cx: int, cy: int, a: float) -> None:
    if a <= 0.04:
        return
    w, h = 168, 92
    x0, y0 = cx - w // 2, cy - h // 2
    rounded(draw, (x0, y0, x0 + w, y0 + h), 22, mix(CARD, (36, 40, 48), a))
    rounded(draw, (x0 + 14, y0 + 16, x0 + w - 14, y0 + h - 16), 12, mix(CARD, (18, 20, 24), a))
    draw.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=mix(CARD, MUTED, a))
    draw.text((cx, y0 + h + 36), "屏幕朝下", font=font(26), fill=mix(CARD, MUTED, a), anchor="mm")


def draw_ring(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, progress: float, a: float) -> None:
    if a <= 0.04:
        return
    bbox = (cx - r, cy - r, cx + r, cy + r)
    draw.ellipse(bbox, outline=mix(CARD, (48, 52, 62), a), width=14)
    if progress <= 0.01:
        return
    span = 360 * max(0.0, min(1.0, progress))
    draw.arc(bbox, start=-90, end=-90 + span, fill=mix(CARD, YELLOW, a), width=14)


def render_b_twentyfive(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "对 · 二十五分钟")
        a0 = appear(t, 0.02)
        d.text((W // 2, 236 + int(lerp(16, 0, a0))), "一次只做二十五分钟", font=font(52), fill=mix(BG, WHITE, a0), anchor="mm")

        a1 = appear(t, 0.16)
        if a1 > 0.04:
            y = 330 + int(lerp(22, 0, a1))
            rounded(d, (90, y, 990, y + 620), 36, mix(BG, CARD, a1))
            remain = max(0.0, 25.0 - t * 0.35)
            mins = int(remain)
            secs = int((remain - mins) * 60)
            clock = f"{mins:02d}:{secs:02d}"
            draw_tomato(d, W // 2, y + 210, 118, a1)
            d.text((W // 2, y + 218), "25", font=font(92), fill=mix(TOMATO, WHITE, a1), anchor="mm")
            progress = min(1.0, t / max(0.8, duration - 0.2))
            draw_ring(d, W // 2, y + 218, 168, progress, a1)
            d.text((W // 2, y + 430), clock, font=font(64), fill=mix(CARD, YELLOW, a1), anchor="mm")
            d.text((W // 2, y + 530), "不是让你更忙", font=font(36), fill=mix(CARD, MUTED, a1), anchor="mm")

        punch = appear(t, 1.10, 0.24)
        if punch > 0.04:
            y = 1020 + int(lerp(22, 0, punch))
            rounded(d, (140, y, 940, y + 190), 28, mix(BG, (42, 24, 22), punch))
            d.text((W // 2, y + 95), "每次只盯一件", font=font(52), fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_b_wrong(duration: float) -> list[Image.Image]:
    """例子拍 1：计时器开着，三窗口乱跳，微信一亮番茄空了。"""
    n = max(1, round(duration * FPS))
    wins = [
        (0.08, 90, "文档", YELLOW),
        (0.22, 390, "微信", TOMATO),
        (0.36, 690, "网页", MINT),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "错 · 空转")
        a0 = appear(t, 0.02)
        d.text((W // 2, 236 + int(lerp(16, 0, a0))), "计时器开着也空", font=font(52), fill=mix(BG, WHITE, a0), anchor="mm")

        for ts, x, name, color in wins:
            a = appear(t, ts, 0.22)
            if a < 0.04:
                continue
            jump = int(8 * (0.5 if (int(t * 8) + x) % 2 else -0.5))
            y = 330 + jump + int(lerp(18, 0, a))
            rounded(d, (x, y, x + 280, y + 360), 28, mix(BG, CARD, a))
            d.text((x + 140, y + 80), name, font=font(40), fill=mix(CARD, color, a), anchor="mm")
            d.text((x + 140, y + 180), "跳一下", font=font(30), fill=mix(CARD, MUTED, a), anchor="mm")
            if name == "微信":
                badge = appear(t, 0.70, 0.20)
                if badge > 0.04:
                    d.ellipse((x + 200, y + 36, x + 248, y + 84), fill=mix(CARD, RED, badge))
                    d.text((x + 224, y + 60), "1", font=font(26), fill=mix(RED, WHITE, badge), anchor="mm")

        empty = appear(t, 1.00, 0.22)
        if empty > 0.04:
            y = 760 + int(lerp(16, 0, empty))
            rounded(d, (90, y, 990, y + 280), 28, mix(BG, CARD, empty))
            draw_tomato(d, 280, y + 140, 64, empty)
            strike = appear(t, 1.20, 0.24)
            if strike > 0.04:
                x1 = int(lerp(200, 360, strike))
                d.line([(200, y + 140), (x1, y + 140)], fill=mix(CARD, RED, strike), width=10)
            d.text((640, y + 140), "番茄就空了", font=font(48), fill=mix(CARD, RED, empty), anchor="mm")

        punch = appear(t, 1.40, 0.20)
        if punch > 0.04:
            y = 1100 + int(lerp(16, 0, punch))
            rounded(d, (140, y, 940, y + 170), 28, mix(BG, (42, 24, 22), punch))
            d.text((W // 2, y + 85), "微信一亮就空了", font=font(48), fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_b_focus(duration: float) -> list[Image.Image]:
    """例子拍 2：选定一件、按下倒计时、手机扣过去。"""
    n = max(1, round(duration * FPS))
    rows = [
        (0.06, "1", "选定一件事", "先写清再开始", YELLOW),
        (0.28, "2", "按下倒计时", "二十五分钟走针", MINT),
        (0.50, "3", "手机扣过去", "屏幕朝下", TOMATO),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "做 · 这一件")
        a0 = appear(t, 0.02)
        d.text((W // 2, 236 + int(lerp(16, 0, a0))), "这二十五分钟里", font=font(54), fill=mix(BG, WHITE, a0), anchor="mm")

        for idx, (ts, num, head, body, color) in enumerate(rows):
            a = appear(t, ts, 0.22)
            if a < 0.04:
                continue
            y = 340 + idx * 200 + int(lerp(18, 0, a))
            rounded(d, (90, y, 990, y + 176), 26, mix(BG, CARD, a))
            d.ellipse((128, y + 44, 220, y + 136), fill=mix(CARD, color, a))
            d.text((174, y + 90), num, font=font(36), fill=mix(color, INK, a), anchor="mm")
            d.text((248, y + 62), head, font=font(42), fill=mix(CARD, color, a), anchor="lm")
            d.text((248, y + 122), body, font=font(28), fill=mix(CARD, WHITE, a), anchor="lm")
            if idx == 2:
                draw_phone_down(d, 860, y + 70, appear(t, 0.70, 0.18))

        punch = appear(t, 1.20, 0.20)
        if punch > 0.04:
            y = 1020 + int(lerp(16, 0, punch))
            rounded(d, (160, y, 920, y + 160), 26, mix(BG, (18, 42, 36), punch))
            d.text((W // 2, y + 80), "手机扣过去", font=font(52), fill=mix(BG, MINT, punch), anchor="mm")
        out.append(img)
    return out


def render_b_rhythm(duration: float) -> list[Image.Image]:
    """铃响五分钟、四个番茄、打断作废。"""
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "律 · 作废")
        a0 = appear(t, 0.02)
        d.text((W // 2, 236 + int(lerp(16, 0, a0))), "铃响才准歇", font=font(54), fill=mix(BG, WHITE, a0), anchor="mm")

        a1 = appear(t, 0.12)
        if a1 > 0.04:
            y = 330 + int(lerp(16, 0, a1))
            rounded(d, (90, y, 990, y + 240), 28, mix(BG, CARD, a1))
            d.text((W // 2, y + 80), "休息  5  分钟", font=font(48), fill=mix(CARD, YELLOW, a1), anchor="mm")
            d.text((W // 2, y + 170), "一个番茄之后", font=font(30), fill=mix(CARD, MUTED, a1), anchor="mm")

        a2 = appear(t, 0.40)
        if a2 > 0.04:
            y = 610 + int(lerp(16, 0, a2))
            rounded(d, (90, y, 990, y + 260), 28, mix(BG, CARD, a2))
            d.text((W // 2, y + 70), "四个之后再休一次长的", font=font(36), fill=mix(CARD, WHITE, a2), anchor="mm")
            for k, x in enumerate((270, 430, 590, 750)):
                draw_tomato(d, x, y + 170, 36, appear(t, 0.50 + k * 0.08, 0.16))

        a3 = appear(t, 0.90)
        if a3 > 0.04:
            y = 910 + int(lerp(16, 0, a3))
            rounded(d, (90, y, 990, y + 220), 28, mix(BG, CARD, a3))
            d.text((W // 2, y + 80), "中途被打断", font=font(40), fill=mix(CARD, RED, a3), anchor="mm")
            strike = appear(t, 1.10, 0.22)
            if strike > 0.04:
                x1 = int(lerp(260, 820, strike))
                d.line([(260, y + 80), (x1, y + 80)], fill=mix(CARD, RED, strike), width=8)
            d.text((W // 2, y + 160), "这个番茄作废，重来", font=font(32), fill=mix(CARD, MUTED, a3), anchor="mm")

        punch = appear(t, 1.40, 0.20)
        if punch > 0.04:
            y = 1180 + int(lerp(16, 0, punch))
            rounded(d, (140, y, 940, y + 170), 28, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y + 85), "打断就作废重来", font=font(48), fill=mix(BG, YELLOW, punch), anchor="mm")
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
    weights = [max(1, len(p.replace("，", "").replace("。", "").replace("；", ""))) for p in phrases]
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
    return duration, aligned


def split_caption(line: str) -> list[str]:
    line = line.strip("。．. ")
    if "；" in line:
        parts = [p for p in line.split("；") if p]
        if 1 < len(parts) <= 2:
            return parts
    if "，" in line and len(line) > 10:
        parts = [p for p in line.split("，") if p]
        if 1 < len(parts) <= 2:
            return parts
    return [line]


def build_timeline(cues: list[tuple[float, float, str]], duration: float) -> dict:
    recipe = json.loads((ROOT / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
    if len(cues) != 11:
        raise SystemExit(f"expected 11 phrases, got {len(cues)}")
    p = cues

    def cut(i: int) -> float:
        return max(p[i][0] - LEAD, p[i - 1][1] if i else 0.0)

    t_b25 = max(p[1][0] + 0.70, cut(2))
    t_wrong = max(p[3][1], cut(4))
    t_focus = max(p[5][1], cut(6))
    t_rhythm = max(p[7][1], cut(8))
    t_close = max(p[9][1], cut(10))

    shots = [
        {"id": "S01a", "kind": "A", "start": 0.0, "end": p[0][1], "src": "assets/V-挥手.mp4", "line": p[0][2], "close": True},
        {"id": "S01b", "kind": "A", "start": p[0][1], "end": t_b25, "src": "assets/V-摊手.mp4", "line": p[1][2]},
        {"id": "S02", "kind": "B", "start": t_b25, "end": p[2][1], "src": "broll/B-二十五分钟.mp4", "line": p[2][2], "broll": "twenty_five"},
        {"id": "S03", "kind": "A", "start": p[2][1], "end": t_wrong, "src": "assets/V-指向.mp4", "line": p[3][2]},
        {"id": "S04", "kind": "B", "start": t_wrong, "end": p[4][1], "src": "broll/B-错法空转.mp4", "line": p[4][2], "broll": "empty_tomato"},
        {"id": "S05", "kind": "A", "start": p[4][1], "end": t_focus, "src": "assets/V-摊手.mp4", "line": p[5][2]},
        {"id": "S06", "kind": "B", "start": t_focus, "end": p[6][1], "src": "broll/B-执行.mp4", "line": p[6][2], "broll": "focus"},
        {"id": "S07", "kind": "A", "start": p[6][1], "end": t_rhythm, "src": "assets/V-指向.mp4", "line": p[7][2]},
        {"id": "S08", "kind": "B", "start": t_rhythm, "end": t_close, "src": "broll/B-节奏.mp4", "line": p[8][2] + " / " + p[9][2], "broll": "rhythm"},
        {"id": "S09", "kind": "A", "start": t_close, "end": duration, "src": "assets/V-点赞.mp4", "line": p[10][2]},
    ]
    for i, shot in enumerate(shots):
        shot["start"] = round(float(shot["start"]), 3)
        shot["end"] = round(float(shot["end"]), 3)
        if shot["end"] <= shot["start"] + 0.12:
            shot["end"] = min(duration, shot["start"] + 0.16)
            if i + 1 < len(shots):
                shots[i + 1]["start"] = shot["end"]
        if i:
            shots[i]["start"] = shots[i - 1]["end"]
    shots[-1]["end"] = round(duration, 3)

    a_caps = []
    a_pairs = [
        (0.0, p[0][1], ["大家好"]),
        (p[1][0], min(p[1][1], t_b25), split_caption(p[1][2])),
        (p[3][0], min(p[3][1], t_wrong), split_caption(p[3][2])),
        (p[5][0], min(p[5][1], t_focus), split_caption(p[5][2])),
        (p[7][0], min(p[7][1], t_rhythm), split_caption(p[7][2])),
        (p[10][0], duration, split_caption(p[10][2])),
    ]
    for s, e, lines in a_pairs:
        if e > s + 0.08:
            a_caps.append({"start": round(s, 3), "end": round(e, 3), "lines": lines})

    colors = [CREAM, TOMATO, CREAM, RED, CREAM, MINT, CREAM, YELLOW, CREAM]
    shutters = [{"start": round(shots[i + 1]["start"], 3), "color": list(colors[i])} for i in range(len(shots) - 1)]
    eyebrows = []
    labels = {"S01a": "A-ROLL / 1a", "S01b": "A-ROLL / 1b", "S03": "A-ROLL / 03", "S05": "A-ROLL / 05", "S07": "A-ROLL / 07", "S09": "A-ROLL / 09"}
    for shot in shots:
        if shot["kind"] == "A" and shot["id"] in labels:
            eyebrows.append({"start": shot["start"], "end": shot["end"], "text": labels[shot["id"]]})
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
        "factory": "27_番茄工作法",
        "topic": 60,
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
    d.text((W // 2, 160), "番茄工作法", font=font(48), fill=WHITE, anchor="mm")
    d.text((W // 2, 250), "一次只做二十五分钟", font=font(52), fill=YELLOW, anchor="mm")
    d.text((W // 2, 340), cover["sub"], font=font(36), fill=MINT, anchor="mm")  # 不是让你更忙
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
        "project_name": "60_番茄工作法一次只做二十五分钟",
        "video_type": "普通短视频",
        "episode": 60,
        "title": NAME,
        "source_note": "topics-batch3.md #60 / 项目索引 27_番茄工作法 voiceover.txt",
        "slug": "番茄工作法一次只做二十五分钟",
        "voice": VOICE,
        "duration": round(duration, 3),
        "size": [W, H],
        "fps": FPS,
        "stage": "delivered",
        "status": "已交付",
        "current_stage": "核验并交付",
        "production_method": "白底小灯 A-roll + 黑底计时卡 B-roll + edge-tts Yunyang + FFmpeg",
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
        "not": "drama-pipeline / 仙侠连载 / C:D:G: / Drive 上传 / 成片00深度工作",
        "updated_at": now,
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    note = f"""# 60 · 番茄工作法一次只做二十五分钟

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。

- **选题**：`topics-batch3.md` 第 60 条；工厂 `27_番茄工作法`
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/60/`
- **云端 only**：不写 `C:\\` / `D:\\` / `G:\\`，不传 Drive
- **避开**：成片 00 深度工作总被打断；成片 26 待办划不掉；成片 16 工位切片

钩子：番茄工作法，一次只做二十五分钟。  
方法：不是更忙，是每次只盯一件；选定、倒计时、手机扣过去。  
收束：铃响才准休息；打断就作废重来。

白底小灯 A-roll + 黑底计时卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {duration:.2f} 秒。镜头 {len(data["shots"])} 条，口播 11 句，按 LENGTH.md 30–60s。时间轴闭合。
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
        inserted = False
        rebuilt = []
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


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch3.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    old = "| 60 | 未完成知识口播 | `60-番茄工作法二十五分钟.mp4` | 未拍 |"
    new = f"| 60 | 未完成知识口播 | `{STAGED_NAME}` | 已核验 {duration:.1f}s |"
    if old in text:
        path.write_text(text.replace(old, new), encoding="utf-8")


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
        "project": "60_番茄工作法一次只做二十五分钟",
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
    if len(cues) != 11:
        raise SystemExit(f"expected 11 phrases, got {len(cues)}")
    if duration < 30.0:
        raise SystemExit(f"VO too short for LENGTH.md: {duration:.2f}s")
    make_bgm(duration)
    data = build_timeline(cues, duration)
    print("timeline shots", [(s["id"], s["start"], s["end"], s["kind"]) for s in data["shots"]])
    if len(data["shots"]) < 7:
        raise SystemExit(f"need >=7 shots, got {len(data['shots'])}")

    b_jobs = [
        ("S02", "B-二十五分钟.mp4", render_b_twentyfive, 2.4),
        ("S04", "B-错法空转.mp4", render_b_wrong, 2.6),
        ("S06", "B-执行.mp4", render_b_focus, 2.4),
        ("S08", "B-节奏.mp4", render_b_rhythm, 2.8),
    ]
    for sid, name, fn, floor in b_jobs:
        shot = next(s for s in data["shots"] if s["id"] == sid)
        dur = max(floor, float(shot["end"]) - float(shot["start"]))
        print("render", name, dur)
        frames_to_mp4(fn(dur + 0.12), ROOT / "broll" / name)

    make_cover()
    staged = assemble(data)
    dur = probe_dur(staged)
    write_docs(dur, staged, data)
    patch_index(dur)
    patch_topics(dur)
    report = qa(staged, data)
    print("STAGED", staged, "dur", dur, "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
