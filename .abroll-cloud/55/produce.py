#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Topic 55 / topics-batch3 #55：先给能截的那句。工厂 297。云端 A-roll + B-roll。

普通短视频 / 口播工艺。草稿只写 .abroll-cloud/55/，成品中转 成片/55-先给能截的那句.mp4。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
云端无 V-正对讲，S01b 用摊手。加长 40–50 秒，覆盖短切。
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
NAME = "先给能截的那句"
STAGED_NAME = "55-先给能截的那句.mp4"
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


_BG_CACHE: Image.Image | None = None


def new_bg() -> Image.Image:
    global _BG_CACHE
    if _BG_CACHE is None:
        img = Image.new("RGB", (W, H), BG)
        overlay = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(overlay)
        d.ellipse((-220, -280, 720, 560), fill=(16, 42, 38))
        d.ellipse((480, 1180, 1400, 2100), fill=(42, 32, 16))
        overlay = overlay.filter(ImageFilter.GaussianBlur(110))
        _BG_CACHE = Image.blend(img, overlay, 0.58)
    return _BG_CACHE.copy()


def phone_frame(draw: ImageDraw.ImageDraw, box, a: float, color) -> None:
    if a <= 0.04:
        return
    x0, y0, x1, y1 = box
    col = mix(BG, color, a)
    draw.rounded_rectangle((x0, y0, x1, y1), radius=36, outline=col, width=8)
    draw.rounded_rectangle((x0 + 18, y0 + 16, x1 - 18, y0 + 36), radius=8, fill=mix(BG, (40, 44, 54), a))
    cx = (x0 + x1) // 2
    draw.rounded_rectangle((cx - 48, y1 - 28, cx + 48, y1 - 12), radius=8, fill=mix(BG, (40, 44, 54), a))


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


def drift(t: float, amp: float = 10.0, period: float = 3.2) -> int:
    return int(amp * math.sin(t * math.tau / period))


def render_b_bury(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    draft = [
        ("开头先铺了一段过程", False),
        ("又补两句谁都用不上的背景", False),
        ("能截的那句先给", True),
        ("后面还跟着解释和例子", False),
        ("听众已经滑走了", False),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "错 · 埋中间")
        a0 = appear(t, 0.02)
        d.text((W // 2, 220 + int(lerp(16, 0, a0))), "好句子埋中间", font=font(50), fill=mix(BG, WHITE, a0), anchor="mm")
        a1 = appear(t, 0.16)
        y = 310 + drift(t, 8, 3.4)
        rounded(d, (72, y, 1008, y + 600), 32, mix(BG, CARD, a1))
        d.text((W // 2, y + 48), "长稿 · 第一屏", font=font(28), fill=mix(CARD, MUTED, a1), anchor="mm")
        for j, (line, gold) in enumerate(draft):
            aj = appear(t, 0.22 + j * 0.16, 0.22)
            if aj <= 0.04:
                continue
            ly = y + 110 + j * 86
            if gold:
                rounded(d, (110, ly - 32, 970, ly + 44), 16, mix(CARD, (46, 38, 20), aj))
            d.text((W // 2, ly), line, font=font(40 if gold else 34), fill=mix(CARD, YELLOW if gold else MUTED, aj), anchor="mm")
        diag = appear(t, 1.30, 0.24)
        if diag > 0.04:
            rounded(d, (120, 980 + drift(t, 5, 2.8), 960, 1090 + drift(t, 5, 2.8)), 22, mix(BG, (42, 28, 18), diag))
            d.text((W // 2, 1035 + drift(t, 5, 2.8)), "不是句子不好 · 是挤在过程里", font=font(30), fill=mix(BG, YELLOW, diag), anchor="mm")
        punch = appear(t, 2.10, 0.26)
        if punch > 0.04:
            y3 = 1140 + int(lerp(18, 0, punch))
            rounded(d, (140, y3, 940, y3 + 150), 26, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y3 + 75), "图上截不走", font=font(48), fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_b_fail(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    blob = ["开头铺了一段过程", "又补两句背景", "能截的那句先给", "后面还跟着解释"]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "错 · 整段套住")
        a0 = appear(t, 0.02)
        d.text((W // 2, 220 + int(lerp(14, 0, a0))), "截图框套住整段", font=font(48), fill=mix(BG, WHITE, a0), anchor="mm")
        a1 = appear(t, 0.16)
        y = 310 + drift(t, 8, 3.1)
        rounded(d, (80, y, 1000, y + 540), 32, mix(BG, CARD, a1))
        d.text((W // 2, y + 50), "听众想截一张图", font=font(28), fill=mix(CARD, MUTED, a1), anchor="mm")
        for j, line in enumerate(blob):
            aj = appear(t, 0.28 + j * 0.16, 0.20)
            if aj <= 0.04:
                continue
            ly = y + 130 + j * 80
            d.text((W // 2, ly), line, font=font(34), fill=mix(CARD, YELLOW if j == 2 else MUTED, aj), anchor="mm")
        frame = appear(t, 1.10, 0.26)
        if frame > 0.04:
            phone_frame(d, (100, y + 20, 980, y + 510), frame, RED)
        punch = appear(t, 1.80, 0.24)
        if punch > 0.04:
            y3 = 980 + int(lerp(16, 0, punch)) + drift(t, 5, 2.8)
            rounded(d, (100, y3, 980, y3 + 190), 26, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y3 + 60), "框住的却是一整段废话", font=font(36), fill=mix(BG, WHITE, punch), anchor="mm")
            d.text((W // 2, y3 + 130), "转发看不懂要记哪句", font=font(40), fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_b_phone(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "对 · 只框一行")
        a0 = appear(t, 0.02)
        d.text((W // 2, 220 + int(lerp(14, 0, a0))), "手机只能框一行", font=font(48), fill=mix(BG, WHITE, a0), anchor="mm")
        a1 = appear(t, 0.16)
        y = 320 + drift(t, 7, 3.0)
        rounded(d, (120, y, 960, y + 520), 36, mix(BG, CARD, a1))
        d.text((W // 2, y + 70), "单独成句 · 前后留白", font=font(28), fill=mix(CARD, MUTED, a1), anchor="mm")
        gold = appear(t, 0.40, 0.24)
        gy = y + 230
        rounded(d, (180, gy - 70, 900, gy + 80), 22, mix(CARD, (22, 40, 36), gold))
        d.text((W // 2, gy), "能截的那句先给", font=font(48), fill=mix(CARD, YELLOW, gold), anchor="mm")
        d.text((W // 2, y + 400), "前后各留一行空白", font=font(30), fill=mix(CARD, MUTED, a1), anchor="mm")
        frame = appear(t, 1.10, 0.26)
        if frame > 0.04:
            phone_frame(d, (160, gy - 120, 920, gy + 130), frame, MINT)
        punch = appear(t, 1.70, 0.24)
        if punch > 0.04:
            y3 = 980 + int(lerp(16, 0, punch))
            rounded(d, (140, y3, 940, y3 + 160), 26, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y3 + 80), "框多了没人转", font=font(46), fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_b_lift(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "对 · 拎到前")
        a0 = appear(t, 0.02)
        d.text((W // 2, 220 + int(lerp(14, 0, a0))), "拎到第一屏", font=font(50), fill=mix(BG, WHITE, a0), anchor="mm")
        a1 = appear(t, 0.16)
        y = 310 + drift(t, 8, 3.2)
        rounded(d, (90, y, 990, y + 360), 32, mix(BG, CARD, a1))
        d.text((W // 2, y + 70), "别让金句躲在第三屏", font=font(28), fill=mix(CARD, MUTED, a1), anchor="mm")
        gold = appear(t, 0.42, 0.24)
        d.text((W // 2, y + 200), "能截的那句先给", font=font(50), fill=mix(CARD, YELLOW, gold), anchor="mm")
        a2 = appear(t, 1.10)
        if a2 > 0.04:
            y2 = 720 + drift(t + 0.4, 6, 2.7)
            rounded(d, (90, y2, 990, y2 + 220), 28, mix(BG, (22, 40, 36), a2))
            d.text((W // 2, y2 + 70), "这不是列表先给结果", font=font(34), fill=mix(CARD, WHITE, a2), anchor="mm")
            d.text((W // 2, y2 + 150), "是截图传播", font=font(42), fill=mix(CARD, MINT, a2), anchor="mm")
        punch = appear(t, 1.90, 0.24)
        if punch > 0.04:
            y3 = 1000 + int(lerp(16, 0, punch))
            rounded(d, (140, y3, 940, y3 + 160), 26, mix(BG, (18, 42, 36), punch))
            d.text((W // 2, y3 + 80), "第一屏只放那句", font=font(46), fill=mix(BG, MINT, punch), anchor="mm")
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
    return duration, aligned


def build_timeline(cues: list[tuple[float, float, str]], duration: float) -> dict:
    recipe = json.loads((ROOT / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
    expected = [p for shot in recipe["shots"] for p in shot["phrases"]]
    got = [c[2] for c in cues]
    if got != expected:
        raise SystemExit(f"phrase mismatch\nexp={expected}\ngot={got}")

    cursor = 0
    shots = []
    t0 = 0.0
    for spec in recipe["shots"]:
        nph = len(spec["phrases"])
        end = float(cues[cursor + nph - 1][1])
        if spec is recipe["shots"][-1]:
            end = duration
        shot = {
            "id": spec["id"],
            "kind": spec["kind"],
            "start": round(t0, 3),
            "end": round(end, 3),
            "src": spec["src"],
            "line": spec["phrases"][0],
            "phrases": spec["phrases"],
        }
        if spec.get("close"):
            shot["close"] = True
        if spec.get("broll"):
            shot["broll"] = spec["broll"]
        if spec.get("cap"):
            shot["cap"] = spec["cap"]
        shots.append(shot)
        t0 = end
        cursor += nph

    for i, shot in enumerate(shots):
        if shot["end"] <= shot["start"] + 0.12:
            raise SystemExit(f"bad shot {shot}")
        if i:
            shots[i]["start"] = shots[i - 1]["end"]
    shots[-1]["end"] = round(duration, 3)
    for shot in shots:
        shot["start"] = round(float(shot["start"]), 3)
        shot["end"] = round(float(shot["end"]), 3)

    a_caps = []
    idx = 0
    for spec, shot in zip(recipe["shots"], shots):
        nph = len(spec["phrases"])
        if spec["kind"] == "A":
            if spec.get("cap"):
                a_caps.append({"start": shot["start"], "end": shot["end"], "lines": spec["cap"]})
            else:
                for j in range(nph):
                    s, e, text = cues[idx + j]
                    a_caps.append({
                        "start": round(max(s, shot["start"]), 3),
                        "end": round(min(e, shot["end"]), 3),
                        "lines": [text.rstrip("。")],
                    })
        idx += nph
    a_caps = [c for c in a_caps if c["end"] > c["start"] + 0.08]

    colors = [CREAM, MINT, YELLOW]
    shutters = []
    eyebrows = []
    a_n = 0
    for i, shot in enumerate(shots):
        if i:
            shutters.append({"start": shot["start"], "color": list(colors[i % 3])})
        if shot["kind"] == "A":
            a_n += 1
            eyebrows.append({"start": shot["start"], "end": shot["end"], "text": f"A-ROLL / {a_n:02d}"})

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
        "factory": "297_先给能截的那句",
        "topic": 55,
        "no_freeze": True,
        "target_duration": [40, 50],
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
        print("staged already linked", staged)
    else:
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
    d.text((W // 2, 160), "先给", font=font(48), fill=WHITE, anchor="mm")
    d.text((W // 2, 250), "能截的那句", font=font(64), fill=YELLOW, anchor="mm")
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
        "project_name": "55_先给能截的那句",
        "video_type": "普通短视频",
        "episode": 55,
        "title": NAME,
        "source_note": "topics-batch3.md #55 / 工厂 297_先给能截的那句 voiceover.txt",
        "slug": "297_先给能截的那句",
        "voice": VOICE,
        "duration": round(duration, 3),
        "size": [W, H],
        "fps": FPS,
        "stage": "delivered",
        "status": "已交付",
        "current_stage": "核验并交付",
        "production_method": "白底小灯 A-roll（往返循环）+ 黑底对照卡 B-roll + edge-tts Yunyang + FFmpeg",
        "target_duration_s": [40, 50],
        "no_freeze": True,
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

    note = f"""# 55 · 先给能截的那句

普通短视频 / 口播工艺。不是剧情短剧，不走 drama-pipeline。

- **选题**：`topics-batch3.md` 第 55 条；工厂 `297_先给能截的那句`
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/55/`
- **云端 only**：不写 `C:\\` / `D:\\` / `G:\\`，不传 Drive

钩子：能截的那句先给。  
后果：好句子埋在中间，图上截不走。  
收束：单独成句，前后留白；写完稿，把那句拎到第一屏。

白底小灯 A-roll（短则往返循环，不定格）+ 黑底对照卡 B-roll。目标 40–50 秒。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {duration:.2f} 秒。镜头 {len(data["shots"])} 条，时间轴闭合。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")


def patch_index(duration: float) -> None:
    idx = Path("/workspace/成片/INDEX.md")
    line = f"| `{STAGED_NAME}` | {duration:.1f}秒 |"
    if not idx.exists():
        idx.write_text(
            "# 成片（可直接看）\n\n竖屏口播 1080×1920，H.264 + AAC。\n\n| 文件 | 时长 |\n|------|------|\n"
            + line + "\n",
            encoding="utf-8",
        )
        return
    text = idx.read_text(encoding="utf-8")
    token = f"`{STAGED_NAME}`"
    seen = False
    out_lines = []
    in_table = False
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
    decode_err = "\n".join(
        ln for ln in (null.stderr or "").splitlines()
        if ln.strip() and "no version information available" not in ln and "libncursesw" not in ln
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
        "project": "55_先给能截的那句",
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
        "decode_null": null.returncode == 0 and not decode_err.strip(),
        "duration_in_target": 40.0 <= float(info["format"]["duration"]) <= 50.5,
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
        and report["duration_in_target"]
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
        "bury": render_b_bury,
        "shot_fail": render_b_fail,
        "phone_crop": render_b_phone,
        "lift": render_b_lift,
    }
    for shot in data["shots"]:
        if shot["kind"] != "B":
            continue
        key = shot["broll"]
        d = max(2.4, float(shot["end"]) - float(shot["start"]))
        dest = ROOT / shot["src"]
        print("render", dest.name, d)
        frames_to_mp4(renders[key](d + 0.16), dest)

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
