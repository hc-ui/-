#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Topic 14 / topics.md #7: 导师课题毕业，就业技术栈自己建. Cloud A-roll + B-roll."""
from __future__ import annotations

import asyncio
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 24
NAME = "导师课题毕业就业技术栈自己建"
STAGED_NAME = "14-导师课题毕业就业技术栈自己建.mp4"
VOICE = "zh-CN-YunyangNeural"
FACTORY_WAV = Path("/workspace/.abroll-cloud/aroll/audio/07_导师课题毕业就业自己建.wav")
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


def new_b_bg() -> Image.Image:
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


def close_align(aligned: list[tuple[float, float, str]], duration: float) -> list[tuple[float, float, str]]:
    aligned[0] = (0.0, aligned[0][1], aligned[0][2])
    for i in range(1, len(aligned)):
        aligned[i] = (aligned[i - 1][1], aligned[i][1], aligned[i][2])
    last_s, _, last_p = aligned[-1]
    aligned[-1] = (last_s, duration, last_p)
    return aligned


def make_voiceover() -> tuple[float, list[tuple[float, float, str]]]:
    text = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    phrases = [ln.strip() for ln in (ROOT / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    audio_dir = ROOT / "audio"
    audio_dir.mkdir(exist_ok=True)
    mp3 = audio_dir / "vo-full.mp3"
    wav = audio_dir / "vo-full.wav"
    aligned: list[tuple[float, float, str]] | None = None
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
        print("TTS fallback factory wav:", exc)
        if not FACTORY_WAV.exists():
            raise
        run(["ffmpeg", "-y", "-i", str(FACTORY_WAV), "-ac", "1", "-ar", "44100", str(wav)])

    duration = probe_dur(wav)
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
    return duration, aligned


def make_bgm(duration: float) -> Path:
    dest = ROOT / "audio" / "bgm.wav"
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=196:sample_rate=44100:duration={duration + 2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=247:sample_rate=44100:duration={duration + 2:.2f}",
        "-filter_complex",
        "[0:a][1:a]amix=inputs=2:duration=longest,lowpass=f=420,volume=0.22,aformat=sample_rates=44100:channel_layouts=stereo",
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


def strike_line(draw: ImageDraw.ImageDraw, box, t: float, start: float) -> None:
    st = appear(t, start, 0.28)
    if st <= 0.04:
        return
    cy = (box[1] + box[3]) // 2
    x0, x1 = box[0] + 36, box[2] - 36
    draw.line([(x0, cy), (int(lerp(x0, x1, st)), cy)], fill=mix(CARD, RED, st), width=10)


def cover_photo(path: Path, zoom: float, progress: float) -> Image.Image:
    src = Image.open(path).convert("RGB")
    scale = max(W / src.width, H / src.height) * zoom
    nw, nh = max(W, int(src.width * scale)), max(H, int(src.height * scale))
    src = src.resize((nw, nh), Image.Resampling.LANCZOS)
    x = int((nw - W) * 0.5)
    y = int((nh - H) * lerp(0.38, 0.22, progress))
    return src.crop((x, y, x + W, y + H))


def b_two_tracks(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, sub_f, punch_f = font(64), font(48), font(32), font(52)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "双轨并行")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(20, 0, a0))), "两条线", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        a1 = appear(t, 0.22)
        if a1 > 0.04:
            y = 360 + int(lerp(24, 0, a1))
            rounded(d, (72, y, 516, y + 620), 36, mix(BG, CARD, a1))
            d.text((294, y + 90), "科研线", font=card_f, fill=mix(CARD, YELLOW, a1), anchor="mm")
            for j, line in enumerate(("开题", "专利", "盲审")):
                d.text((294, y + 230 + j * 110), line, font=sub_f, fill=mix(CARD, WHITE, a1), anchor="mm")

            rounded(d, (564, y, 1008, y + 620), 36, mix(BG, (20, 40, 36), a1))
            d.text((786, y + 90), "就业线", font=card_f, fill=mix(CARD, MINT, a1), anchor="mm")
            for j, line in enumerate(("Python", "能力栈", "自己建")):
                d.text((786, y + 230 + j * 110), line, font=sub_f, fill=mix(CARD, WHITE, a1), anchor="mm")

        punch = appear(t, min(1.35, duration * 0.55), 0.28)
        if punch > 0.04:
            y = 1100 + int(lerp(22, 0, punch))
            rounded(d, (120, y, 960, y + 200), 32, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y + 100), "毕业不绑死就业", font=punch_f, fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def b_python_first(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    still = ROOT / "assets" / "t07a-lab-and-code-split.png"
    title_f, chip_f, punch_f = font(50), font(34), font(48)
    chips = [("01", "数据处理", MINT), ("02", "闭环温控", YELLOW), ("03", "采集自动化", MINT)]
    out = []
    for i in range(n):
        t = i / FPS
        p = i / max(1, n - 1)
        photo = cover_photo(still, lerp(1.04, 1.12, p), p)
        veil = Image.new("RGB", (W, H), BG)
        img = Image.blend(photo, veil, 0.28)
        d = ImageDraw.Draw(img)
        tag(d, t, "可带走")
        a0 = appear(t, 0.06)
        rounded(d, (90, 220, 990, 400), 32, mix(BG, (18, 22, 28), a0 * 0.92))
        d.text((W // 2, 310), "先把 Python 学扎实", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        y0 = 1280
        for idx, (num, head, color) in enumerate(chips):
            a = appear(t, 0.28 + idx * 0.16, 0.26)
            if a < 0.04:
                continue
            x = 72 + idx * 336
            y = y0 + int(lerp(18, 0, a))
            rounded(d, (x, y, x + 312, y + 150), 24, mix(BG, CARD, a))
            d.ellipse((x + 22, y + 52, x + 70, y + 100), fill=mix(CARD, color, a))
            d.text((x + 46, y + 76), num, font=font(22), fill=mix(color, INK, a), anchor="mm")
            d.text((x + 88, y + 76), head, font=chip_f, fill=mix(CARD, WHITE, a), anchor="lm")

        punch = appear(t, min(1.2, duration * 0.5), 0.26)
        if punch > 0.04:
            y = 1480 + int(lerp(16, 0, punch))
            rounded(d, (220, y, 860, y + 120), 26, mix(BG, (18, 42, 36), punch))
            d.text((W // 2, y + 60), "技术栈自己建", font=punch_f, fill=mix(BG, MINT, punch), anchor="mm")
        out.append(img)
    return out


def b_no_five(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, sub_f, punch_f = font(56), font(52), font(32), font(52)
    rows = [
        (0.18, "C++", "热门不是开工令"),
        (0.48, "ROS2", "后置，不抢现在"),
        (0.78, "PyTorch", "先别并线"),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "先别开坑")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(18, 0, a0))), "别同时开五条路", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        y0 = 380
        for idx, (ts, head, body) in enumerate(rows):
            a = appear(t, ts, 0.26)
            if a < 0.04:
                continue
            y = y0 + idx * 220 + int(lerp(22, 0, a))
            box = (96, y, 984, y + 188)
            rounded(d, box, 28, mix(BG, CARD, a))
            d.text((180, y + 70), head, font=card_f, fill=mix(CARD, WHITE, a), anchor="lm")
            d.text((180, y + 136), body, font=sub_f, fill=mix(CARD, MUTED, a), anchor="lm")
            strike_line(d, box, t, ts + 0.42)

        punch = appear(t, min(1.55, duration * 0.62), 0.26)
        if punch > 0.04:
            y = 1180 + int(lerp(20, 0, punch))
            rounded(d, (140, y, 940, y + 180), 30, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y + 90), "一条线先走通", font=punch_f, fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def build_timeline(aligned: list[tuple[float, float, str]], duration: float) -> dict:
    recipe = json.loads((ROOT / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
    by_phrase = {p: (s, e) for s, e, p in aligned}
    raw: list[dict] = []
    for i, shot in enumerate(recipe["shots"]):
        phrase = shot["phrases"][0]
        if phrase in by_phrase:
            start, end = by_phrase[phrase]
        else:
            start, end = 0.0, duration
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
        # B 卷早切：下一镜若带 lead，本镜在话音未落处让位
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
            a_caps.append({"start": round(start, 3), "end": round(end, 3), "lines": split_caption(phrase)})
            eyebrows.append({"start": round(start, 3), "end": round(end, 3), "text": f"A-ROLL / {shot['id'][-2:]}"})
        color = list(CREAM) if shot["kind"] == "A" else list(MINT)
        if i == len(raw) - 1:
            color = list(YELLOW)
        if i > 0:
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


def render_broll(data: dict) -> None:
    durs = {}
    for shot in data["shots"]:
        if shot["kind"] == "B":
            durs[shot["src"]] = max(1.2, float(shot["end"]) - float(shot["start"]))
    jobs = [
        ("broll/B-双轨.mp4", b_two_tracks),
        ("broll/B-Python.mp4", b_python_first),
        ("broll/B-别开五条.mp4", b_no_five),
    ]
    for rel, fn in jobs:
        dur = durs[rel]
        print("broll", rel, f"{dur:.2f}s")
        frames_to_mp4(fn(dur + 0.12), ROOT / rel)


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
    make_sfx([float(s["start"]) for s in data["shutters"]], float(data["duration"]))

    final = ROOT / f"00_最终成片_{NAME}.mp4"
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

    out = ROOT / "output" / f"{NAME}.mp4"
    out.parent.mkdir(exist_ok=True)
    shutil.copy2(final, out)
    shutil.copy2(final, ROOT / "final" / f"{NAME}.mp4")

    staged = Path("/workspace/成片") / STAGED_NAME
    staged.parent.mkdir(exist_ok=True)
    shutil.copy2(final, staged)
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
    canvas.save(dest, quality=92)
    canvas.save(ROOT / "final" / "cover.jpg", quality=92)
    return dest


def write_docs(duration: float, staged: Path, data: dict) -> None:
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    sha = hashlib.sha256(vo.encode("utf-8")).hexdigest()
    status = {
        "schema_version": 1,
        "project_name": "14_导师课题毕业就业技术栈自己建",
        "video_type": "普通短视频",
        "topic_index": 7,
        "slug": "07_导师课题毕业就业自己建",
        "status": "已交付",
        "current_stage": "核验并交付",
        "production_method": "白底小灯 A-roll + 黑底对照卡 B-roll + edge-tts Yunyang + FFmpeg",
        "voice": VOICE,
        "duration": round(duration, 3),
        "size": [W, H],
        "fps": FPS,
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
            "project_video": f"00_最终成片_{NAME}.mp4",
            "cover": f"00_封面_{NAME}.jpg",
        },
        "staged": f"成片/{STAGED_NAME}",
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    note = f"""# 14 导师课题毕业，就业技术栈自己建

**给用户看：** `成片/{STAGED_NAME}`  
**工程目录：** `/workspace/.abroll-cloud/14/`

## 这是什么

普通竖屏知识短视频（A-roll + B-roll）。`topics.md` 第 7 条：控制专硕「科研毕业线 + 就业能力线」并行，不把长期就业绑在生医课题上。

白底小灯 A-roll + 黑底对照卡 / 分屏工位 B-roll。口播锁定工厂文案 `07_导师课题毕业就业自己建`。不是剧情短剧。

## 当前状态

- 视频类型：普通短视频
- 状态：已交付到 `成片/`
- 成片：1080×1920，24 fps，约 {duration:.2f} 秒，H.264 + AAC 44100 stereo
- 工程成片：`00_最终成片_{NAME}.mp4`
- 草稿不进 `成片/`，只放成品 mp4

## 口播

{vo}

## 已核验结果

- 配音：edge-tts `{VOICE}`（失败则回退工厂 wav），44100 Hz
- 画面：A/B 轮切；字幕只叠 A-roll；切镜用色块快门
- B 卷比对应口播早切约半拍
- 镜头数：{len(data["shots"])}；时间轴闭合到 {duration:.3f}s

## 依据

- `.abroll-cloud/pipeline.md`、`topics.md` #7
- `aroll/scripts/07_导师课题毕业就业自己建.md`
- `broll-assets` 选题 7 静帧（生图不烧中文；中文代码绘制）
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")


def qa(staged: Path, data: dict) -> dict:
    qa_dir = ROOT / "qa"
    qa_dir.mkdir(exist_ok=True)
    probe = subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(staged)], text=True)
    (qa_dir / "ffprobe.txt").write_text(probe, encoding="utf-8")
    info = json.loads(probe)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next(s for s in info["streams"] if s["codec_type"] == "audio")
    null = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(staged), "-f", "null", "-"],
        capture_output=True, text=True,
    )
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
        "project": "14_导师课题毕业就业技术栈自己建",
        "strict": True,
        "cloud_only": True,
        "final": str(staged),
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
        },
        "decode_ok": null.returncode == 0 and not (null.stderr or "").strip(),
        "ok": True,
    }
    report["ok"] = (
        report["video"]["width"] == 1080
        and report["video"]["height"] == 1920
        and abs(report["video"]["fps"] - 24) < 0.05
        and report["video"]["codec"] == "h264"
        and report["audio"]["codec"] == "aac"
        and report["audio"]["sample_rate"] == 44100
        and report["decode_ok"]
        and not overlap
        and not gap
        and report["timeline"]["last_end_equals_audio"]
    )
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    for rel in (
        "assets/V-挥手.mp4",
        "assets/V-摊手.mp4",
        "assets/V-指向.mp4",
        "assets/t07a-lab-and-code-split.png",
        "script/voiceover.txt",
        "plan/shot_recipe.json",
    ):
        if not (ROOT / rel).exists():
            raise FileNotFoundError(ROOT / rel)

    duration, aligned = make_voiceover()
    print("VO", duration, aligned)
    make_bgm(duration)
    data = build_timeline(aligned, duration)
    print("timeline", json.dumps(data["shots"], ensure_ascii=False, indent=2))
    render_broll(data)
    make_cover(data)
    staged = assemble(data)
    write_docs(duration, staged, data)
    report = qa(staged, data)
    print("STAGED", staged, "dur", probe_dur(staged), "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
