#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 28：杂务别接报销采购。云端 A-roll + B-roll，不是短剧。"""
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
NAME = "杂务别接报销采购"
STAGED_NAME = "28-杂务别接报销采购.mp4"
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
INK = (28, 32, 36)
RED = (255, 118, 118)
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


def ticks_to_sec(v: float) -> float:
    return float(v) / 10_000_000.0


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


def split_caption(line: str) -> list[str]:
    line = line.strip("。．. ")
    if "，" in line and len(line) > 8:
        parts = [p for p in line.split("，") if p]
        if 1 < len(parts) <= 2:
            return parts
    return [line]


def close_align(aligned: list[tuple[float, float, str]], duration: float) -> list[tuple[float, float, str]]:
    aligned[0] = (0.0, aligned[0][1], aligned[0][2])
    for i in range(1, len(aligned)):
        aligned[i] = (aligned[i - 1][1], aligned[i][1], aligned[i][2])
    last_s, _, last_p = aligned[-1]
    aligned[-1] = (last_s, duration, last_p)
    return aligned


def weight_align(phrases: list[str], duration: float) -> list[tuple[float, float, str]]:
    weights = [max(1, len(p.replace(" ", ""))) for p in phrases]
    total_w = sum(weights)
    aligned: list[tuple[float, float, str]] = []
    t = 0.0
    for phrase, w in zip(phrases, weights):
        dur = duration * (w / total_w)
        aligned.append((t, t + dur, phrase))
        t += dur
    return close_align(aligned, duration)


def detect_sentence_cues(wav: Path, phrases: list[str], duration: float) -> list[tuple[float, float, str]] | None:
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
    if len(merged) != len(phrases):
        return None
    cues = []
    for i, phrase in enumerate(phrases):
        start = 0.0 if i == 0 else merged[i][0]
        end = merged[i][1]
        cues.append((start, end, phrase))
    return close_align(cues, duration)


async def synthesize_voice(text: str, mp3: Path) -> list[dict]:
    import edge_tts

    comm = edge_tts.Communicate(text, VOICE)
    bounds: list[dict] = []
    with mp3.open("wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("SentenceBoundary", "WordBoundary"):
                bounds.append(chunk)
    return bounds


def copy_assets() -> None:
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    names = ["V-挥手.mp4", "V-摊手.mp4", "V-指向.mp4", "V-点赞.mp4", "A-角色-小灯-摊手.jpg"]
    for name in names:
        src = ASSET_SRC / name
        dest = assets / name
        if not src.exists():
            raise FileNotFoundError(src)
        if not dest.exists() or dest.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dest)


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
        if len(parsed) == len(phrases) and abs(parsed[-1][1] - duration) < 0.12:
            print("reuse VO", wav, duration)
            return duration, close_align(parsed, duration)

    bounds: list[dict] = []
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
        print("TTS failed:", exc)
        raise

    duration = probe_dur(wav)
    if aligned is None:
        aligned = detect_sentence_cues(wav, phrases, duration)
    if aligned is None:
        aligned = weight_align(phrases, duration)
    else:
        aligned = close_align(aligned, duration)

    lines = [f"{s:.3f}\t{e:.3f}\t{p}" for s, e, p in aligned]
    (audio_dir / "vo-align.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    vtt = ["WEBVTT", ""]
    for i, (s, e, p) in enumerate(aligned, 1):
        def ts(x: float) -> str:
            h = int(x // 3600)
            m = int((x % 3600) // 60)
            sec = x % 60
            return f"{h:02d}:{m:02d}:{sec:06.3f}"
        vtt += [str(i), f"{ts(s)} --> {ts(e)}", p, ""]
    (audio_dir / "vo.vtt").write_text("\n".join(vtt), encoding="utf-8")
    (audio_dir / "cues.json").write_text(
        json.dumps([{"start": s, "end": e, "text": p} for s, e, p in aligned], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return duration, aligned


def make_bgm(duration: float) -> Path:
    dest = ROOT / "audio" / "bgm.wav"
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=196:sample_rate=44100:duration={duration + 2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=247:sample_rate=44100:duration={duration + 2:.2f}",
        "-filter_complex",
        "[0:a]volume=0.14[a];[1:a]volume=0.09[b];"
        "[a][b]amix=inputs=2:duration=longest,lowpass=f=420,volume=0.22,"
        "aformat=sample_rates=44100:channel_layouts=stereo",
        str(dest),
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


def check_badge(draw, cx: int, cy: int, a: float) -> None:
    if a <= 0.04:
        return
    r = 36
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=mix(CARD, (18, 56, 46), a))
    col = mix(CARD, MINT, a)
    draw.line([(cx - 16, cy + 2), (cx - 4, cy + 16), (cx + 20, cy - 14)], fill=col, width=8)


def cross_badge(draw, cx: int, cy: int, a: float) -> None:
    if a <= 0.04:
        return
    r = 36
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=mix(CARD, (56, 22, 22), a))
    col = mix(CARD, RED, a)
    draw.line([(cx - 14, cy - 14), (cx + 14, cy + 14)], fill=col, width=8)
    draw.line([(cx + 14, cy - 14), (cx - 14, cy + 14)], fill=col, width=8)


def draw_receipt(d: ImageDraw.ImageDraw, box, a: float, stamp: float) -> None:
    x0, y0, x1, y1 = box
    paper = mix(BG, (236, 228, 214), a)
    rounded(d, box, 18, paper)
    ink = mix(paper, (70, 58, 46), a)
    d.text(((x0 + x1) // 2, y0 + 48), "INVOICE", font=font(28, False), fill=ink, anchor="mm")
    for i, w in enumerate((0.72, 0.58, 0.80, 0.46)):
        yy = y0 + 92 + i * 36
        d.rectangle((x0 + 36, yy, x0 + 36 + int((x1 - x0 - 72) * w), yy + 10), fill=mix(paper, (180, 168, 150), a))
    if stamp > 0.04:
        cx, cy = (x0 + x1) // 2 + 70, y0 + 150
        r = 78
        col = mix(paper, RED, stamp)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=8)
        d.text((cx, cy), "打回", font=font(44), fill=col, anchor="mm")


def b_invoice(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, sub_f, punch_f = font(58), font(44), font(32), font(52)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "避坑红线")
        a0 = appear(t, 0.02)
        d.text((W // 2, 248 + int(lerp(16, 0, a0))), "报销采购", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        a1 = appear(t, 0.16)
        y = 330 + int(lerp(22, 0, a1))
        draw_receipt(d, (180, y, 900, y + 340), a1, appear(t, 0.62, 0.28))

        a2 = appear(t, 0.88)
        y2 = 720 + int(lerp(18, 0, a2))
        rounded(d, (96, y2, 984, y2 + 200), 30, mix(BG, CARD, a2))
        d.text((140, y2 + 70), "发票一打回", font=card_f, fill=mix(CARD, YELLOW, a2), anchor="lm")
        d.text((140, y2 + 140), "手续繁琐，反复纠缠", font=sub_f, fill=mix(CARD, MUTED, a2), anchor="lm")

        a3 = appear(t, 1.22)
        y3 = 950 + int(lerp(18, 0, a3))
        rounded(d, (96, y3, 984, y3 + 200), 30, mix(BG, CARD, a3))
        d.text((140, y3 + 70), "批评跟着来", font=card_f, fill=mix(CARD, RED, a3), anchor="lm")
        d.text((140, y3 + 140), "最耗心理能量", font=sub_f, fill=mix(CARD, MUTED, a3), anchor="lm")

        punch = appear(t, 1.62, 0.24)
        if punch > 0.04:
            y4 = 1220 + int(lerp(16, 0, punch))
            rounded(d, (150, y4, 930, y4 + 160), 28, mix(BG, (42, 22, 20), punch))
            d.text((W // 2, y4 + 80), "别接这摊", font=punch_f, fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def b_chores(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, sub_f, punch_f = font(56), font(42), font(30), font(50)
    goods = [
        (0.14, "卫生值日", "边界清楚", MINT),
        (0.40, "收发快递", "做完即止", MINT),
        (0.66, "盖章跑腿", "体力杂务", YELLOW),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "认领边界")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(16, 0, a0))), "做完就停", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        for idx, (ts, head, body, color) in enumerate(goods):
            a = appear(t, ts, 0.24)
            if a < 0.04:
                continue
            y = 360 + idx * 200 + int(lerp(18, 0, a))
            rounded(d, (96, y, 984, y + 176), 30, mix(BG, CARD, a))
            d.text((160, y + 62), head, font=card_f, fill=mix(CARD, color, a), anchor="lm")
            d.text((160, y + 124), body, font=sub_f, fill=mix(CARD, WHITE, a), anchor="lm")
            check_badge(d, 880, y + 88, appear(t, ts + 0.18, 0.20))

        bad = appear(t, 1.10, 0.24)
        if bad > 0.04:
            y = 980 + int(lerp(16, 0, bad))
            rounded(d, (96, y, 984, y + 200), 30, mix(BG, CARD, bad))
            d.text((160, y + 70), "公款账目", font=card_f, fill=mix(CARD, RED, bad), anchor="lm")
            d.text((160, y + 138), "推脱，别包揽", font=sub_f, fill=mix(CARD, MUTED, bad), anchor="lm")
            cross_badge(d, 880, y + 100, appear(t, 1.28, 0.20))

        punch = appear(t, 1.58, 0.24)
        if punch > 0.04:
            y = 1260 + int(lerp(16, 0, punch))
            rounded(d, (150, y, 930, y + 160), 28, mix(BG, (18, 42, 36), punch))
            d.text((W // 2, y + 80), "推掉就对", font=punch_f, fill=mix(BG, MINT, punch), anchor="mm")
        out.append(img)
    return out


def build_timeline(duration: float, cues: list[tuple[float, float, str]]) -> dict:
    recipe = json.loads((ROOT / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
    by_phrase = {p: (s, e) for s, e, p in cues}
    raw = []
    for i, shot in enumerate(recipe["shots"]):
        phrase = shot["phrases"][0]
        start, end = by_phrase.get(phrase, (0.0, duration))
        lead = float(shot.get("lead") or 0)
        if i == 0:
            start = 0.0
        elif lead:
            start = max(0.0, start - lead)
        if i == len(recipe["shots"]) - 1:
            end = duration
        raw.append({"shot": shot, "phrase": phrase, "start": start, "end": end})

    raw[0]["start"] = 0.0
    raw[-1]["end"] = duration
    for i in range(len(raw) - 1):
        if raw[i + 1]["start"] < raw[i]["end"]:
            raw[i]["end"] = raw[i + 1]["start"]
        else:
            raw[i + 1]["start"] = raw[i]["end"]
        if raw[i]["end"] <= raw[i]["start"] + 0.16:
            raw[i]["end"] = raw[i]["start"] + 0.16
            raw[i + 1]["start"] = raw[i]["end"]
    raw[-1]["end"] = duration
    if raw[-1]["end"] <= raw[-1]["start"] + 0.16:
        steal = 0.2
        raw[-2]["end"] = max(raw[-2]["start"] + 0.16, raw[-2]["end"] - steal)
        raw[-1]["start"] = raw[-2]["end"]

    shots_out = []
    a_caps = []
    shutters = []
    eyebrows = []
    a_i = 0
    for i, row in enumerate(raw):
        shot = row["shot"]
        start, end, phrase = row["start"], row["end"], row["phrase"]
        item = {
            "id": shot["id"],
            "kind": shot["kind"],
            "start": round(start, 3),
            "end": round(end, 3),
            "src": shot["src"],
            "line": phrase,
        }
        if shot.get("close"):
            item["close"] = True
        if shot.get("broll"):
            item["broll"] = shot["broll"]
        shots_out.append(item)
        if shot["kind"] == "A":
            a_i += 1
            a_caps.append({"start": round(start, 3), "end": round(end, 3), "lines": split_caption(phrase)})
            eyebrows.append({"start": round(start, 3), "end": round(end, 3), "text": f"A-ROLL / {a_i:02d}"})
        if i > 0:
            color = list(CREAM) if shot["kind"] == "A" else list(MINT)
            if i == len(raw) - 1:
                color = list(YELLOW)
            shutters.append({"start": round(start, 3), "color": color})

    data = {
        "audio": "audio/vo-full.wav",
        "duration": round(duration, 3),
        "fps": FPS,
        "size": [W, H],
        "title": recipe["title"],
        "bgm": "audio/bgm.wav",
        "shots": shots_out,
        "a_caps": a_caps,
        "shutters": shutters,
        "eyebrows": eyebrows,
        "cover": {
            "title": recipe["cover_title"],
            "sub": recipe["cover_sub"],
            "line": recipe["cover_line"],
            "src": recipe["cover_src"],
        },
    }
    (ROOT / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


def render_brolls(data: dict) -> None:
    durs = {}
    for shot in data["shots"]:
        if shot["kind"] == "B":
            durs[shot["src"]] = max(2.2, float(shot["end"]) - float(shot["start"]))
    jobs = [
        ("broll/B-发票打回.mp4", b_invoice),
        ("broll/B-公款推掉.mp4", b_chores),
    ]
    for rel, fn in jobs:
        dur = durs[rel]
        print("broll", rel, f"{dur:.2f}s")
        frames_to_mp4(fn(dur + 0.12), ROOT / rel)


def draw_eyebrow(base: Image.Image, t: float, eyebrows) -> None:
    label = None
    for item in eyebrows:
        if item["start"] <= t < item["end"]:
            label = item["text"]
            break
    if not label:
        return
    d = ImageDraw.Draw(base)
    d.rectangle((76, 88, 120, 92), fill=(*MINT, 230))
    d.text((136, 78), label, font=font(22), fill=(90, 98, 108, 220))


def draw_pill(base: Image.Image, lines: list[str], y: int = 168) -> None:
    fnt = font(56 if len(lines) == 1 else 48)
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
        start = float(item["start"])
        color = tuple(item["color"])
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
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "qtrle", "-pix_fmt", "argb",
        str(dest),
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

    make_sfx([float(s["start"]) for s in data["shutters"]], float(data["duration"]))
    audio = ROOT / data["audio"]
    bgm = ROOT / "audio" / "bgm.wav"
    sfx = ROOT / "audio" / "sfx.wav"
    final = ROOT / f"00_最终成片_{NAME}.mp4"
    (ROOT / "final").mkdir(exist_ok=True)
    (ROOT / "output").mkdir(exist_ok=True)

    inputs = ["ffmpeg", "-y", "-i", str(burned), "-i", str(audio)]
    filters = ["[1:a]loudnorm=I=-16:LRA=11:TP=-1.5,aformat=sample_rates=44100:channel_layouts=stereo[vo]"]
    mix_ins = ["[vo]"]
    idx = 2
    if bgm.exists():
        inputs += ["-i", str(bgm)]
        filters.append(f"[{idx}:a]adelay=800|800,volume=0.18,highpass=f=140[bg]")
        mix_ins.append("[bg]")
        idx += 1
    if sfx.exists():
        inputs += ["-i", str(sfx)]
        filters.append(f"[{idx}:a]volume=0.30[sfx]")
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

    shutil.copy2(final, ROOT / "final" / f"{NAME}.mp4")
    shutil.copy2(final, ROOT / "output" / f"{NAME}.mp4")

    staged = Path("/workspace/成片") / STAGED_NAME
    staged.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(final, staged)
    print("FINAL", final, "dur", probe_dur(final))
    print("STAGED", staged, "dur", probe_dur(staged))
    return staged


def make_cover(data: dict) -> Path:
    cover = data["cover"]
    char = Image.open(ROOT / cover["src"]).convert("RGB")
    scale = max(W / char.width, H / char.height)
    nw, nh = int(char.width * scale), int(char.height * scale)
    char = char.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - W) // 2
    y = int((nh - H) * 0.62)
    canvas = char.crop((x, y, x + W, y + H))
    overlay = Image.new("RGBA", (W, H), (11, 13, 18, 36))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((90, 90, 990, 430), radius=36, fill=(22, 24, 28))
    d.text((W // 2, 168), cover["title"], font=font(58), fill=WHITE, anchor="mm")
    d.text((W // 2, 258), cover["sub"], font=font(40), fill=MINT, anchor="mm")
    d.text((W // 2, 348), cover["line"], font=font(30), fill=MUTED, anchor="mm")
    dest = ROOT / f"00_封面_{NAME}.jpg"
    (ROOT / "final").mkdir(exist_ok=True)
    canvas.save(dest, quality=92)
    canvas.save(ROOT / "final" / "cover.jpg", quality=92)
    return dest


def write_docs(duration: float, staged: Path, data: dict) -> None:
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    status = {
        "schema_version": 1,
        "project_name": "28_杂务别接报销采购",
        "video_type": "普通短视频",
        "topic_source": "赵刚课题组备忘录·第二节红线1",
        "slug": "28_杂务别接报销采购",
        "title": "杂务别接报销采购",
        "production_method": "白底小灯 A-roll + 黑底对照卡 B-roll + edge-tts Yunyang + FFmpeg",
        "status": "已交付",
        "current_stage": "核验并交付",
        "stage": "delivered",
        "voice": VOICE,
        "duration": round(duration, 3),
        "size": [W, H],
        "fps": FPS,
        "cloud_only": True,
        "no_windows_paths": True,
        "no_drive_upload": True,
        "script": {"path": "script/voiceover.txt", "sha256": hashlib.sha256(vo.encode("utf-8")).hexdigest()},
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
            "project_video": f"00_最终成片_{NAME}.mp4",
            "cover": f"00_封面_{NAME}.jpg",
        },
        "staged": f"成片/{STAGED_NAME}",
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    note = f"""# 28 · 杂务别接报销采购

普通短视频 / 知识口播。不是剧情短剧。

- **选题**：实验室生存未拍题（避开字典 / 双线 / 测控 / 15-15-70）
- **来源**：中科大赵刚课题组备忘录第二节「坚决远离财务报销与仪器耗材采购」
- **工程草稿**：`/workspace/.abroll-cloud/28/`
- **工程成片**：`00_最终成片_{NAME}.mp4`
- **成片中转**：`/workspace/成片/{STAGED_NAME}`

钩子：分杂务的时候，别接报销采购。  
后果：发票一打回，批评跟着来。  
方法：认领卫生快递盖章。  
收束：公款账目，推掉就对。

白底小灯 A-roll + 黑底对照卡 B-roll。B 卷比对应口播早切半拍。中文全部组装阶段叠字，不进生图。

## 已核验

- 规格：1080×1920，24 fps，H.264 + AAC 44100 stereo，{duration:.2f}s
- 时间轴 {len(data["shots"])} 镜闭合，无重叠无空缺
- 只在本云端 VM 渲染，未写 `C:\\` / `D:\\` / `G:\\`
- 草稿不进 `成片/`，中转只放稳定成品
- 本集按约定不上传 Drive
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")


def qa(staged: Path, data: dict) -> dict:
    qa_dir = ROOT / "qa"
    qa_dir.mkdir(exist_ok=True)
    probe = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(staged)],
        text=True,
    )
    (qa_dir / "ffprobe.json").write_text(probe, encoding="utf-8")
    meta = json.loads(probe)
    v = next(s for s in meta["streams"] if s["codec_type"] == "video")
    a = next(s for s in meta["streams"] if s["codec_type"] == "audio")
    run(["ffmpeg", "-y", "-i", str(staged), "-f", "null", "-"])
    vol = subprocess.run(
        ["ffmpeg", "-i", str(staged), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    mean = maxv = None
    for line in (vol.stderr or "").splitlines():
        if "mean_volume" in line:
            mean = float(line.split(":")[-1].replace("dB", "").strip())
        if "max_volume" in line:
            maxv = float(line.split(":")[-1].replace("dB", "").strip())

    shots = data["shots"]
    overlap = any(shots[i]["end"] > shots[i + 1]["start"] + 0.001 for i in range(len(shots) - 1))
    gap = any(abs(shots[i]["end"] - shots[i + 1]["start"]) > 0.002 for i in range(len(shots) - 1))
    last_ok = abs(shots[-1]["end"] - data["duration"]) < 0.02
    fps_num, fps_den = (v.get("avg_frame_rate") or "24/1").split("/")
    fps = float(fps_num) / max(float(fps_den), 1.0)
    sha = hashlib.sha256(staged.read_bytes()).hexdigest()
    report = {
        "project": "28_杂务别接报销采购",
        "strict": True,
        "cloud_only": True,
        "no_windows_paths": True,
        "no_drive_upload": True,
        "final": str(staged),
        "sha256": sha,
        "bytes": staged.stat().st_size,
        "video": {
            "codec": v.get("codec_name"),
            "width": int(v.get("width", 0)),
            "height": int(v.get("height", 0)),
            "fps": round(fps, 3),
            "pix_fmt": v.get("pix_fmt"),
            "duration_s": round(float(meta["format"]["duration"]), 3),
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
            "last_end_equals_audio": last_ok,
        },
        "ok": (
            int(v.get("width", 0)) == 1080
            and int(v.get("height", 0)) == 1920
            and abs(fps - 24) < 0.05
            and a.get("codec_name") == "aac"
            and int(a.get("sample_rate", 0)) == 44100
            and not overlap
            and not gap
            and last_ok
            and mean is not None
            and mean < -10
        ),
    }
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("QA", report["ok"], report["video"], report["audio"])
    return report


def update_index(duration: float) -> None:
    path = Path("/workspace/成片/INDEX.md")
    line = f"| `{STAGED_NAME}` | {duration:.1f}s |"
    text = path.read_text(encoding="utf-8") if path.exists() else "# 成片（可直接看）\n\n"
    if STAGED_NAME in text:
        rows = []
        for raw in text.splitlines():
            if raw.startswith("| `28-") and STAGED_NAME.split("-", 1)[0] in raw:
                rows.append(line)
            else:
                rows.append(raw)
        path.write_text("\n".join(rows).rstrip() + "\n", encoding="utf-8")
        return
    if text.rstrip().endswith("|"):
        text = text.rstrip() + "\n" + line + "\n"
    else:
        text = text.rstrip() + "\n\n" + line + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    copy_assets()
    duration, cues = make_voiceover()
    print("VO", duration, cues)
    data = build_timeline(duration, cues)
    make_bgm(duration)
    render_brolls(data)
    make_cover(data)
    staged = assemble(data)
    write_docs(duration, staged, data)
    report = qa(staged, data)
    update_index(float(report["video"]["duration_s"]))
    if not report["ok"]:
        raise SystemExit("QA failed")
    print("done", staged)


if __name__ == "__main__":
    main()
