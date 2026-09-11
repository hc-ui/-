#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared helpers for 40-long / 47-long. Cloud-only. No freeze-pad."""
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

W, H, FPS = 1080, 1920, 24
VOICE = "zh-CN-YunyangNeural"
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_REG = "/tmp/NotoSansSC-Regular.otf"
FONT_FALLBACK = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
LEAD = 0.28
TARGET_MIN, TARGET_MAX = 40.0, 50.0
HARD_MIN, HARD_MAX = 30.0, 60.0

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


def bob(t: float, amp: float = 5.0, speed: float = 1.7) -> int:
    return int(amp * math.sin(t * speed))


def new_bg(tint: str = "navy") -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    overlay = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(overlay)
    if tint == "teal":
        d.ellipse((-220, -280, 720, 560), fill=(16, 42, 38))
        d.ellipse((480, 1180, 1400, 2100), fill=(42, 32, 16))
    else:
        d.ellipse((-260, -320, 640, 520), fill=(16, 22, 48))
        d.ellipse((420, 980, 1380, 1980), fill=(48, 28, 12))
    overlay = overlay.filter(ImageFilter.GaussianBlur(120))
    return Image.blend(img, overlay, 0.62)


def tag(draw: ImageDraw.ImageDraw, t: float, label: str, color=AMBER) -> None:
    a = appear(t, 0.0, 0.22)
    if a <= 0:
        return
    fnt = font(30)
    tw, th = text_wh(draw, label, fnt)
    x, y = 84, 88
    rounded(draw, (x - 22, y - 14, x + tw + 22, y + th + 12), 22, mix(BG, (20, 32, 56), a))
    draw.text((x, y), label, font=fnt, fill=mix(BG, color, a))


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


def make_voiceover(root: Path, rate: str = "-6%") -> tuple[float, list[tuple[float, float, str]]]:
    text = (root / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    phrases = [ln.strip() for ln in (root / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    audio_dir = root / "audio"
    audio_dir.mkdir(exist_ok=True)
    mp3 = audio_dir / "vo-full.mp3"
    wav = audio_dir / "vo-full.wav"
    aligned: list[tuple[float, float, str]] | None = None
    bounds = asyncio.run(synthesize_voice(text, mp3, rate))
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
        print("TTS ok", wav, "cues", len(sentences), "rate", rate)
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


def ensure_vo_window(root: Path) -> tuple[float, list[tuple[float, float, str]]]:
    """Synthesize VO; nudge rate so duration lands in 40–50s when possible."""
    phrases = [ln.strip() for ln in (root / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    wav = root / "audio" / "vo-full.wav"
    align = root / "audio" / "vo-align.txt"
    if wav.exists() and wav.stat().st_size > 800 and align.exists():
        duration = probe_dur(wav)
        parsed: list[tuple[float, float, str]] = []
        for line in align.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) >= 3:
                parsed.append((float(parts[0]), float(parts[1]), parts[2]))
        if len(parsed) == len(phrases) and TARGET_MIN <= duration <= TARGET_MAX:
            print(f"reuse VO in target window dur={duration:.3f}")
            return duration, close_align(parsed, duration)
    duration, cues = make_voiceover(root, rate="-6%")
    print(f"VO attempt rate=-6% dur={duration:.3f}")
    if TARGET_MIN <= duration <= TARGET_MAX:
        return duration, cues
    if duration < TARGET_MIN:
        for rate in ("-8%", "-10%", "-12%"):
            duration, cues = make_voiceover(root, rate=rate)
            print(f"VO attempt rate={rate} dur={duration:.3f}")
            if duration >= TARGET_MIN and duration <= HARD_MAX:
                return duration, cues
    elif duration > TARGET_MAX:
        for rate in ("-4%", "-2%", "+0%", "+4%", "+8%"):
            duration, cues = make_voiceover(root, rate=rate)
            print(f"VO attempt rate={rate} dur={duration:.3f}")
            if duration <= TARGET_MAX and duration >= HARD_MIN:
                return duration, cues
    if duration < HARD_MIN or duration > HARD_MAX:
        raise SystemExit(f"VO duration {duration:.2f}s outside hard window {HARD_MIN}-{HARD_MAX}")
    return duration, cues


def make_bgm(root: Path, duration: float, freqs: tuple[int, int, int] = (147, 185, 220)) -> Path:
    dest = root / "audio" / "bgm.wav"
    f0, f1, f2 = freqs
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency={f0}:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency={f1}:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency={f2}:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-filter_complex",
        "[0:a]volume=0.10[a];[1:a]volume=0.07[b];[2:a]volume=0.05[c];"
        "[a][b][c]amix=inputs=3:duration=longest,lowpass=f=460,alimiter=limit=0.30",
        "-ac", "2", "-ar", "44100", str(dest),
    ])
    return dest


def make_sfx(root: Path, cuts: list[float], duration: float) -> Path:
    dest = root / "audio" / "sfx.wav"
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


def build_timeline(root: Path, cues: list[tuple[float, float, str]], duration: float) -> dict:
    recipe = json.loads((root / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
    phrase_to_i = {p: i for i, (*_, p) in enumerate(cues)}
    missing = []
    for spec in recipe["shots"]:
        for p in spec["phrases"]:
            if p not in phrase_to_i:
                missing.append(p)
    if missing:
        raise SystemExit(f"recipe phrases not in cues: {missing}")

    shots = []
    for spec in recipe["shots"]:
        idxs = [phrase_to_i[p] for p in spec["phrases"]]
        start = 0.0 if not shots else float(cues[idxs[0]][0])
        end = float(cues[idxs[-1]][1])
        shot = {
            "id": spec["id"],
            "kind": spec["kind"],
            "start": round(start, 3),
            "end": round(end, 3),
            "src": spec["src"],
            "line": spec["phrases"][0],
            "phrases": spec["phrases"],
        }
        if spec.get("close"):
            shot["close"] = True
        if spec.get("broll"):
            shot["broll"] = spec["broll"]
        shots.append(shot)

    shots[0]["start"] = 0.0
    for i in range(1, len(shots)):
        shots[i]["start"] = shots[i - 1]["end"]
    shots[-1]["end"] = round(duration, 3)
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

    a_caps = []
    for shot in shots:
        if shot["kind"] != "A":
            continue
        for phrase in shot["phrases"]:
            i = phrase_to_i[phrase]
            start = max(cues[i][0], shot["start"])
            end = min(cues[i][1], shot["end"])
            if end > start + 0.08:
                a_caps.append({"start": round(start, 3), "end": round(end, 3), "lines": split_caption(phrase)})

    colors = [CREAM, AMBER, MINT, YELLOW]
    shutters = []
    for i, shot in enumerate(shots[1:], start=1):
        shutters.append({"start": shot["start"], "color": list(colors[i % len(colors)])})
    eyebrows = []
    for shot in shots:
        if shot["kind"] == "A":
            eyebrows.append({"start": shot["start"], "end": shot["end"], "text": f"A-ROLL / {shot['id']}"})

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
        "no_freeze_pad": True,
    }
    (root / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


def draw_eyebrow(base: Image.Image, t: float, eyebrows, accent=AMBER) -> None:
    label = None
    for item in eyebrows:
        if item["start"] <= t < item["end"]:
            label = item["text"]
            break
    if not label:
        return
    d = ImageDraw.Draw(base)
    fnt = font(22)
    d.rectangle((76, 88, 120, 92), fill=(*accent, 230))
    d.text((136, 78), label, font=fnt, fill=(90, 98, 108, 220))


def draw_pill(base: Image.Image, lines: list[str], y: int = 168, accent=AMBER) -> None:
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
    pd.rectangle((10, 14, 20, box_h - 14), fill=(*accent, 235))
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


def render_captions(root: Path, data: dict, accent=AMBER) -> Path:
    dest = root / "shots" / "caption_layer.mov"
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
        draw_eyebrow(img, t, data["eyebrows"], accent=accent)
        for cue in data["a_caps"]:
            if cue["start"] <= t < cue["end"]:
                draw_pill(img, cue["lines"], accent=accent)
                break
        img = draw_shutter(img, t, data["shutters"])
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(err[-2500:])
    return dest


def cut_shot(src: Path, dur: float, dest: Path, kind: str, close: bool = False) -> None:
    """Trim or loop. Never tpad/freeze-pad."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    src_dur = max(0.01, probe_dur(src))
    if kind == "A" and close:
        vf = f"scale=1380:2454,crop={W}:{H}:150:60,fps={FPS},setsar=1,format=yuv420p"
    elif kind == "A":
        vf = f"scale=1188:2112,crop={W}:{H}:54:105,fps={FPS},setsar=1,format=yuv420p"
    else:
        vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},setsar=1,format=yuv420p"
    cmd = ["ffmpeg", "-y"]
    if kind == "A" and dur > src_dur + 0.04:
        cmd += ["-stream_loop", "-1"]
    cmd += [
        "-i", str(src), "-t", f"{dur:.3f}",
        "-vf", vf, "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18", str(dest),
    ]
    run(cmd)


def assemble(root: Path, data: dict, name: str, staged_name: str, accent=AMBER) -> Path:
    shots_dir = root / "shots"
    shots_dir.mkdir(exist_ok=True)
    parts: list[Path] = []
    for shot in data["shots"]:
        dur = float(shot["end"]) - float(shot["start"])
        src = root / shot["src"]
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

    caps = render_captions(root, data, accent=accent)
    burned = shots_dir / "video_subs.mp4"
    run([
        "ffmpeg", "-y", "-i", str(concat), "-i", str(caps),
        "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an", str(burned),
    ])

    audio = root / data["audio"]
    bgm = root / "audio" / "bgm.wav"
    sfx = root / "audio" / "sfx.wav"
    cuts = [float(s["start"]) for s in data["shutters"]]
    make_sfx(root, cuts, float(data["duration"]))

    final = root / f"00_最终成片_{name}.mp4"
    (root / "final").mkdir(exist_ok=True)
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

    out = root / "output" / f"{name}.mp4"
    safe_copy(final, out)
    safe_copy(final, root / "final" / f"{name}.mp4")
    staged = Path("/workspace/成片") / staged_name
    safe_copy(final, staged)
    return staged


def copy_assets(root: Path, names: list[str]) -> None:
    dest = root / "assets"
    dest.mkdir(exist_ok=True)
    search = [
        Path("/workspace/.abroll-cloud/06/assets"),
        Path("/workspace/.abroll-cloud/25/assets"),
        Path("/workspace/.abroll-cloud/57/assets"),
    ]
    for name in names:
        src = None
        for folder in search:
            cand = folder / name
            if cand.exists():
                src = cand
                break
        if src is None:
            raise FileNotFoundError(name)
        target = dest / name
        if not target.exists() or target.stat().st_size != src.stat().st_size:
            shutil.copy2(src, target)


def write_docs(root: Path, duration: float, staged: Path, data: dict, meta: dict) -> None:
    vo = (root / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    sha = hashlib.sha256(vo.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    status = {
        "schema_version": 1,
        "project_name": meta["project_name"],
        "video_type": "普通短视频",
        "episode": meta["episode"],
        "title": meta["title"],
        "cut": "long-40s",
        "source_note": meta["source_note"],
        "unused_of": meta.get("unused_of", ""),
        "voice": VOICE,
        "duration": round(duration, 3),
        "size": [W, H],
        "fps": FPS,
        "stage": "delivered",
        "status": "已交付",
        "current_stage": "核验并交付",
        "production_method": "白底小灯 A-roll + 黑底对照卡 B-roll + edge-tts Yunyang + FFmpeg",
        "no_freeze_pad": True,
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
            "project_final": f"00_最终成片_{meta['title']}.mp4",
            "cover": f"00_封面_{meta['title']}.jpg",
        },
        "staged": f"成片/{meta['staged_name']}",
        "draft": str(root),
        "cloud_only": True,
        "windows_paths": False,
        "drive_upload": False,
        "not": "drama-pipeline / 仙侠连载 / C:D:G: / Drive 上传 / freeze-pad",
        "updated_at": now,
    }
    (root / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note = meta["note_md"].format(vo=vo, duration=duration, nshots=len(data["shots"]), staged=meta["staged_name"], draft=str(root))
    (root / "项目说明.md").write_text(note, encoding="utf-8")


def patch_index(staged_name: str, duration: float) -> None:
    idx = Path("/workspace/成片/INDEX.md")
    line = f"| `{staged_name}` | {duration:.1f}s |"
    if not idx.exists():
        idx.write_text(
            "# 成片（可直接看）\n\n竖屏口播 1080×1920，H.264 + AAC。\n\n| 文件 | 时长 |\n|------|------|\n"
            + line + "\n",
            encoding="utf-8",
        )
        return
    text = idx.read_text(encoding="utf-8")
    pattern = re.compile(rf"\| `{re.escape(staged_name)}` \| [0-9.]+s \|")
    if pattern.search(text):
        text = pattern.sub(line, text)
    elif staged_name not in text:
        if not text.endswith("\n"):
            text += "\n"
        text += line + "\n"
    idx.write_text(text, encoding="utf-8")


def patch_delivery_row(ep: str, staged_name: str, duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    new = f"| `成片/{staged_name}` | 1080×1920 h264+aac 44.1k stereo | {duration:.2f}s | topic {ep} 加长重切（{duration:.1f}s，无 freeze-pad） |"
    pat = re.compile(rf"\| `成片/{re.escape(staged_name)}` \|[^\n]*")
    if pat.search(text):
        text = pat.sub(new, text)
        path.write_text(text, encoding="utf-8")
    row_pat = re.compile(rf"\| {ep} \| `{re.escape(staged_name)}` \|[^\n]*")
    row = f"| {ep} | `{staged_name}` | 已核验 {duration:.1f}s |"
    if row_pat.search(text):
        text = path.read_text(encoding="utf-8")
        text = row_pat.sub(row, text)
        path.write_text(text, encoding="utf-8")


def qa(root: Path, staged: Path, data: dict, project: str) -> dict:
    qa_dir = root / "qa"
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
    dur = float(info["format"]["duration"])
    report = {
        "project": project,
        "strict": True,
        "cloud_only": True,
        "windows_paths": False,
        "drive_upload": False,
        "no_freeze_pad": True,
        "video_type": "普通短视频",
        "final": str(staged),
        "sha256": digest,
        "bytes": staged.stat().st_size,
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
            "overlap": overlap,
            "gap": gap,
            "last_end_equals_audio": abs(shots[-1]["end"] - data["duration"]) < 0.05,
            "broll_lead_s": LEAD,
        },
        "decode_null": null.returncode == 0 and not (null.stderr or "").strip(),
        "in_hard_window": HARD_MIN <= dur <= HARD_MAX,
        "in_target_window": TARGET_MIN <= dur <= TARGET_MAX,
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
        and report["in_hard_window"]
    )
    (root / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
