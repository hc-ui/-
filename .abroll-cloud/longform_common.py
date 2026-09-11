#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared A/B-roll helpers for lengthened 成片 56–58. Cloud only."""
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

W, H, FPS = 1080, 1920, 24
VOICE = "zh-CN-YunyangNeural"
RATE = "-10%"
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_REG = "/tmp/NotoSansSC-Regular.otf"
FONT_FALLBACK = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
TARGET_MIN, TARGET_MAX = 40.0, 50.0
LEAD = 0.28

BG = (11, 13, 18)
CARD = (24, 28, 38)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
CREAM = (245, 247, 250)
RED = (255, 118, 118)
INK = (22, 24, 28)


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


_BG_CACHE = None


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


def tag(draw: ImageDraw.ImageDraw, t: float, label: str) -> None:
    a = appear(t, 0.0, 0.22)
    if a <= 0:
        return
    fnt = font(30)
    tw, th = text_wh(draw, label, fnt)
    x, y = 84, 88
    rounded(draw, (x - 22, y - 14, x + tw + 22, y + th + 12), 22, mix(BG, (20, 42, 38), a))
    draw.text((x, y), label, font=fnt, fill=mix(BG, MINT, a))


def frames_to_mp4(frames, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "18",
        str(dest),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    saved_mid = False
    count = 0
    for im in frames:
        rgb = im.convert("RGB")
        if count == 12:
            rgb.save(dest.with_suffix(".jpg"), quality=92)
            saved_mid = True
        proc.stdin.write(rgb.tobytes())
        count += 1
        del rgb
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(err[-2000:])
    if count == 0:
        raise RuntimeError(f"no frames for {dest}")
    if not saved_mid:
        Image.new("RGB", (W, H), BG).save(dest.with_suffix(".jpg"), quality=92)


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


def split_caption(line: str) -> list[str]:
    line = line.strip("。．. ")
    if "，" in line and len(line) > 8:
        parts = [p for p in line.split("，") if p]
        if 1 < len(parts) <= 2:
            return parts
    if len(line) > 12:
        mid = len(line) // 2
        cut = line.rfind("，", 0, mid + 4)
        if cut < 4:
            cut = line.find("，", mid)
        if cut >= 4:
            return [line[:cut], line[cut + 1 :]]
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


def zh_seconds(duration: float) -> str:
    n = int(round(duration))
    digits = "零一二三四五六七八九"
    if n < 10:
        return f"{digits[n]}秒"
    if n == 10:
        return "十秒"
    if n < 20:
        return f"十{digits[n - 10]}秒" if n > 10 else "十秒"
    tens, ones = divmod(n, 10)
    head = f"{digits[tens]}十"
    return head + (digits[ones] + "秒" if ones else "秒")


def lock_script(root: Path, phrases: list[str]) -> str:
    text = "。".join(p.rstrip("。") for p in phrases) + "。"
    (root / "script").mkdir(exist_ok=True)
    (root / "script" / "voiceover.txt").write_text(text + "\n", encoding="utf-8")
    (root / "script" / "phrases.txt").write_text("\n".join(phrases) + "\n", encoding="utf-8")
    return text


async def synthesize_voice(text: str, mp3: Path) -> list[dict]:
    import edge_tts

    comm = edge_tts.Communicate(text, VOICE, rate=RATE)
    bounds: list[dict] = []
    with mp3.open("wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("SentenceBoundary", "WordBoundary"):
                bounds.append(chunk)
    return bounds


def retarget_audio(wav: Path, duration: float) -> float:
    if TARGET_MIN - 0.05 <= duration <= TARGET_MAX + 0.05:
        return duration
    if duration < TARGET_MIN:
        target = min(TARGET_MAX - 1.2, max(TARGET_MIN + 0.8, duration * 1.12))
    else:
        target = max(TARGET_MIN + 1.0, min(48.8, duration * 0.96))
    atempo = duration / target
    if not (0.55 <= atempo <= 1.45):
        raise SystemExit(f"audio {duration:.2f}s cannot retarget to {target:.2f}s (atempo={atempo:.3f})")
    tmp = wav.with_name(wav.stem + "-retarget.wav")
    run(["ffmpeg", "-y", "-i", str(wav), "-filter:a", f"atempo={atempo:.5f}", str(tmp)])
    shutil.move(tmp, wav)
    return probe_dur(wav)


def make_voiceover(root: Path, phrases: list[str]) -> tuple[float, list[tuple[float, float, str]]]:
    text = lock_script(root, phrases)
    audio_dir = root / "audio"
    audio_dir.mkdir(exist_ok=True)
    mp3 = audio_dir / "vo-full.mp3"
    wav = audio_dir / "vo-full.wav"
    fp = hashlib.sha256((text + "\n" + RATE).encode("utf-8")).hexdigest()
    fp_path = audio_dir / "script.sha256"
    aligned: list[tuple[float, float, str]] | None = None
    if (
        wav.exists()
        and wav.stat().st_size > 800
        and (audio_dir / "vo-align.txt").exists()
        and fp_path.exists()
        and fp_path.read_text(encoding="utf-8").strip() == fp
    ):
        duration = probe_dur(wav)
        parsed: list[tuple[float, float, str]] = []
        for line in (audio_dir / "vo-align.txt").read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) >= 3:
                parsed.append((float(parts[0]), float(parts[1]), parts[2]))
        if len(parsed) == len(phrases) and TARGET_MIN - 0.2 <= duration <= TARGET_MAX + 0.2:
            print("reuse VO", wav, duration)
            return duration, close_align(parsed, duration)

    bounds = asyncio.run(synthesize_voice(text, mp3))
    if mp3.stat().st_size < 800:
        raise RuntimeError("tts too small")
    run(["ffmpeg", "-y", "-i", str(mp3), "-ac", "1", "-ar", "44100", str(wav)])
    sentences = [b for b in bounds if b.get("type") == "SentenceBoundary"]
    duration = probe_dur(wav)
    if sentences and len(sentences) >= len(phrases):
        aligned = []
        for i, phrase in enumerate(phrases):
            b = sentences[i]
            start = ticks_to_sec(b["offset"])
            end = start + ticks_to_sec(b["duration"])
            aligned.append((start, end, phrase))
        print("TTS ok", wav, "cues", len(sentences), "dur", duration)
    else:
        print("TTS sentence mismatch", len(sentences), "phrases", len(phrases))
        aligned = None

    old_dur = duration
    duration = retarget_audio(wav, duration)
    if aligned is None:
        aligned = detect_sentence_cues(wav, phrases, duration)
    else:
        if abs(duration - old_dur) > 0.05:
            scale = duration / old_dur
            aligned = [(s * scale, e * scale, p) for s, e, p in aligned]
        aligned = close_align(aligned, duration)

    (audio_dir / "vo-align.txt").write_text(
        "".join(f"{s:.3f}\t{e:.3f}\t{p}\n" for s, e, p in aligned),
        encoding="utf-8",
    )
    (audio_dir / "cues.json").write_text(
        json.dumps([{"start": s, "end": e, "text": p} for s, e, p in aligned], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    def ts(x: float) -> str:
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{(ms // 60000) % 60:02d}:{(ms // 1000) % 60:02d}.{ms % 1000:03d}"

    (audio_dir / "vo.vtt").write_text(
        "WEBVTT\n\n" + "".join(
            f"{i}\n{ts(s)} --> {ts(e)}\n{p}\n\n"
            for i, (s, e, p) in enumerate(aligned, 1)
        ),
        encoding="utf-8",
    )
    fp_path.write_text(fp + "\n", encoding="utf-8")
    return duration, aligned


def close_shots(shots: list[dict], duration: float) -> list[dict]:
    for i, shot in enumerate(shots):
        shot["start"] = round(float(shot["start"]), 3)
        shot["end"] = round(float(shot["end"]), 3)
        if shot["end"] <= shot["start"] + 0.14:
            shot["end"] = min(duration, shot["start"] + 0.18)
            if i + 1 < len(shots):
                shots[i + 1]["start"] = shot["end"]
        if i:
            shots[i]["start"] = shots[i - 1]["end"]
    shots[-1]["end"] = round(duration, 3)
    for shot in shots:
        shot["start"] = round(float(shot["start"]), 3)
        shot["end"] = round(float(shot["end"]), 3)
        if shot["end"] <= shot["start"] + 0.12:
            raise SystemExit(f"bad shot {shot}")
    return shots


def make_bgm(root: Path, duration: float) -> Path:
    dest = root / "audio" / "bgm.wav"
    dest.parent.mkdir(exist_ok=True)
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


def make_sfx(root: Path, cuts: list[float], duration: float) -> Path:
    dest = root / "audio" / "sfx.wav"
    dest.parent.mkdir(exist_ok=True)
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


def render_captions(root: Path, data: dict) -> Path:
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
        "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(dest),
    ])


def assemble(root: Path, data: dict, name: str, staged_name: str) -> Path:
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

    caps = render_captions(root, data)
    burned = shots_dir / "video_subs.mp4"
    run([
        "ffmpeg", "-y", "-i", str(concat), "-i", str(caps),
        "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an", str(burned),
    ])

    audio = root / data["audio"]
    make_bgm(root, float(data["duration"]))
    cuts = [float(s["start"]) for s in data["shutters"]]
    make_sfx(root, cuts, float(data["duration"]))
    bgm = root / "audio" / "bgm.wav"
    sfx = root / "audio" / "sfx.wav"

    final = root / f"00_最终成片_{name}.mp4"
    (root / "final").mkdir(exist_ok=True)
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
        "-t", f"{float(data['duration']):.3f}",
        "-movflags", "+faststart",
        str(final),
    ]
    run(inputs)

    out = root / "output" / f"{name}.mp4"
    out.parent.mkdir(exist_ok=True)
    shutil.copy2(final, out)
    shutil.copy2(final, root / "final" / f"{name}.mp4")

    staged = Path("/workspace/成片") / staged_name
    staged.parent.mkdir(exist_ok=True)
    if staged.resolve() != final.resolve():
        try:
            shutil.copy2(final, staged)
        except shutil.SameFileError:
            pass
    return staged


def copy_named_assets(dest: Path, mapping: dict[str, Path]) -> None:
    dest.mkdir(exist_ok=True)
    for name, src_dir in mapping.items():
        src = src_dir / name
        if not src.exists():
            raise FileNotFoundError(src)
        target = dest / name
        if not target.exists() or target.stat().st_size != src.stat().st_size:
            shutil.copy2(src, target)


def write_docs(root: Path, *, episode: int, name: str, staged_name: str, duration: float, data: dict, note_body: str, source_note: str) -> None:
    vo = (root / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    sha = hashlib.sha256(vo.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    staged = Path("/workspace/成片") / staged_name
    status = {
        "schema_version": 1,
        "project_name": f"{episode}_{name}",
        "video_type": "普通短视频",
        "episode": episode,
        "title": name,
        "source_note": source_note,
        "voice": VOICE,
        "rate": RATE,
        "duration": round(duration, 3),
        "duration_zh": zh_seconds(duration),
        "target_s": [TARGET_MIN, TARGET_MAX],
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
            "project_final": f"00_最终成片_{name}.mp4",
            "cover": f"00_封面_{name}.jpg",
        },
        "staged": f"成片/{staged_name}",
        "cloud_only": True,
        "windows_paths": False,
        "drive_upload": False,
        "not": "drama-pipeline / 仙侠连载 / C:D:G: / Drive 上传",
        "updated_at": now,
    }
    (root / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note = f"""# {episode} · {name}

普通短视频。不是剧情短剧，不走 drama-pipeline。

- **选题**：`{source_note}`
- **成片中转**：`成片/{staged_name}`
- **本集工程成片**：`00_最终成片_{name}.mp4`
- **草稿目录**：`{root}`
- **云端 only**：不写 `C:\\` / `D:\\` / `G:\\`，不传 Drive
- **时长**：{duration:.2f} 秒（{zh_seconds(duration)}），目标四十到五十秒

{note_body}

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，{duration:.2f} 秒（{zh_seconds(duration)}）。镜头 {len(data["shots"])} 条，时间轴闭合。
"""
    (root / "项目说明.md").write_text(note, encoding="utf-8")


def patch_index(staged_name: str, duration: float) -> None:
    line = f"| `{staged_name}` | {duration:.1f}秒（{zh_seconds(duration)}） |"
    for idx in (Path("/workspace/成片/INDEX.md"), Path("/workspace/.abroll-cloud/INDEX.chengpian.md")):
        if not idx.exists():
            continue
        text = idx.read_text(encoding="utf-8")
        token = f"`{staged_name}`"
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
        idx.write_text(text, encoding="utf-8")


def patch_topics_row(episode: int, staged_name: str, duration: float, category: str) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch3.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    new = f"| {episode} | {category} | `{staged_name}` | 已核验 {duration:.1f}秒（{zh_seconds(duration)}） |"
    lines = []
    hit = False
    for raw in text.splitlines():
        if raw.startswith(f"| {episode} |"):
            lines.append(new)
            hit = True
        else:
            lines.append(raw)
    if hit:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    shots = data["shots"]
    overlap = any(shots[i]["end"] > shots[i + 1]["start"] + 0.001 for i in range(len(shots) - 1))
    gap = any(abs(shots[i]["end"] - shots[i + 1]["start"]) > 0.02 for i in range(len(shots) - 1))
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
    dur = float(info["format"]["duration"])
    digest = hashlib.sha256(staged.read_bytes()).hexdigest()
    report = {
        "project": project,
        "strict": True,
        "cloud_only": True,
        "windows_paths": False,
        "drive_upload": False,
        "video_type": "普通短视频",
        "final": str(staged),
        "sha256": digest,
        "bytes": staged.stat().st_size,
        "duration_zh": zh_seconds(dur),
        "target_s": [TARGET_MIN, TARGET_MAX],
        "in_target": TARGET_MIN - 0.15 <= dur <= TARGET_MAX + 0.15,
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
        and report["in_target"]
    )
    (root / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
