#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Topic 05 cloud A-roll + B-roll: 先给选项再要决定."""
from __future__ import annotations

import asyncio
import json
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 24
NAME = "先给选项再要决定"
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
FONT_FALLBACK = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
VOICE = "zh-CN-YunyangNeural"

BG = (11, 13, 18)
CARD = (24, 28, 38)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
CREAM = (236, 241, 239)
INK = (28, 32, 36)
RED = (255, 118, 118)

A_STILLS = {
    "wave": ROOT / "assets" / "xiaodeng-wave.png",
    "shrug": ROOT / "assets" / "xiaodeng-shrug.png",
    "point": ROOT / "assets" / "xiaodeng-point.png",
}


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


def font(size: int) -> ImageFont.FreeTypeFont:
    for path in (FONT_PATH, FONT_FALLBACK):
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
    x0, y0, x1, y1 = draw.textbbox((0, 0), label, font=fnt)
    tw, th = x1 - x0, y1 - y0
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


def ticks_to_sec(v: float) -> float:
    return float(v) / 10_000_000.0


def make_voiceover() -> tuple[float, list[tuple[float, float, str]]]:
    text = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    phrases = [ln.strip() for ln in (ROOT / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    audio_dir = ROOT / "audio"
    audio_dir.mkdir(exist_ok=True)
    mp3 = audio_dir / "vo-full.mp3"
    wav = audio_dir / "vo-full.wav"
    bounds = asyncio.run(synthesize_voice(text, mp3))
    run(["ffmpeg", "-y", "-i", str(mp3), "-ac", "1", "-ar", "44100", str(wav)])
    duration = probe_dur(wav)

    sentences = [b for b in bounds if b.get("type") == "SentenceBoundary"]
    aligned: list[tuple[float, float, str]] = []
    if sentences and len(sentences) >= len(phrases):
        for i, phrase in enumerate(phrases):
            b = sentences[i]
            start = ticks_to_sec(b["offset"])
            end = start + ticks_to_sec(b["duration"])
            aligned.append((start, end, phrase))
    else:
        weights = [max(1, len(p)) for p in phrases]
        total_w = sum(weights)
        t = 0.0
        for phrase, w in zip(phrases, weights):
            dur = duration * (w / total_w)
            aligned.append((t, t + dur, phrase))
            t += dur

    # Close gaps / clamp to audio
    aligned[0] = (0.0, aligned[0][1], aligned[0][2])
    for i in range(1, len(aligned)):
        aligned[i] = (aligned[i - 1][1], aligned[i][1], aligned[i][2])
    last_s, _, last_p = aligned[-1]
    aligned[-1] = (last_s, duration, last_p)

    lines = []
    for s, e, p in aligned:
        lines.append(f"{s:.3f}\t{e:.3f}\t{p}")
    (audio_dir / "vo-align.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return duration, aligned


def make_bgm(duration: float) -> Path:
    dest = ROOT / "audio" / "bgm.wav"
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=196:sample_rate=44100:duration={duration + 1:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=247:sample_rate=44100:duration={duration + 1:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=294:sample_rate=44100:duration={duration + 1:.2f}",
        "-filter_complex",
        "[0:a]volume=0.12[a];[1:a]volume=0.08[b];[2:a]volume=0.06[c];"
        "[a][b][c]amix=inputs=3:duration=longest,lowpass=f=520,alimiter=limit=0.35",
        "-ac", "2", "-ar", "44100", str(dest),
    ])
    return dest


def make_sfx(cuts: list[float], duration: float) -> Path:
    dest = ROOT / "audio" / "sfx.wav"
    if not cuts:
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={duration:.2f}", str(dest)])
        return dest
    for i, t in enumerate(cuts):
        click = ROOT / "audio" / f"_click{i}.wav"
        run([
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "sine=frequency=880:sample_rate=44100:duration=0.06",
            "-af", "afade=t=out:st=0.02:d=0.04,volume=0.35",
            str(click),
        ])
    inputs = ["ffmpeg", "-y"]
    filters = []
    mix_labels = []
    for i, t in enumerate(cuts):
        click = ROOT / "audio" / f"_click{i}.wav"
        inputs += ["-i", str(click)]
        filters.append(f"[{i}:a]adelay={int(t * 1000)}|{int(t * 1000)},volume=0.55[c{i}]")
        mix_labels.append(f"[c{i}]")
    filters.append(f"{''.join(mix_labels)}amix=inputs={len(cuts)}:duration=longest,apad=pad_dur={duration:.2f},atrim=0:{duration:.2f}")
    inputs += ["-filter_complex", ";".join(filters), "-ac", "2", "-ar", "44100", str(dest)]
    run(inputs)
    return dest


def still_to_aroll(src: Path, dest: Path, duration: float, close: bool = False) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    frames = max(1, round(duration * FPS))
    # Ken Burns: slow zoom on white-studio still
    z_end = 1.12 if close else 1.06
    vf = (
        f"scale=1200:2134:force_original_aspect_ratio=increase,"
        f"crop=1200:2134,"
        f"zoompan=z='min(1+({z_end}-1)*on/{frames},{z_end})':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)-40':"
        f"d={frames}:s={W}x{H}:fps={FPS},"
        f"fps={FPS},setsar=1,format=yuv420p"
    )
    run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(src),
        "-t", f"{duration:.3f}", "-vf", vf,
        "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        str(dest),
    ])


def render_b_options(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(56)
    card_f = font(44)
    small = font(32)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "01 选项")
        a0 = appear(t, 0.02)
        d.text((W // 2, 260 + int(lerp(20, 0, a0))), "开放问题", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        d.text((W // 2, 340), "不知道从哪答", font=small, fill=mix(BG, MUTED, appear(t, 0.16)), anchor="mm")

        a1 = appear(t, 0.28)
        y = 430 + int(lerp(24, 0, a1))
        rounded(d, (100, y, 500, y + 280), 32, mix(BG, CARD, a1))
        d.text((300, y + 90), "空问", font=small, fill=mix(CARD, MUTED, a1), anchor="mm")
        d.text((300, y + 175), "？", font=title_f, fill=mix(CARD, WHITE, a1), anchor="mm")

        a2 = appear(t, 0.48)
        y2 = 430 + int(lerp(24, 0, a2))
        rounded(d, (580, y2, 980, y2 + 280), 32, mix(BG, (32, 44, 40), a2))
        d.text((780, y2 + 90), "选项", font=small, fill=mix(CARD, YELLOW, a2), anchor="mm")
        d.text((780, y2 + 175), "A  /  B", font=card_f, fill=mix(CARD, WHITE, a2), anchor="mm")

        a3 = appear(t, 0.86)
        d.text((W // 2, 860 + int(lerp(18, 0, a3))), "先给两个选项", font=title_f, fill=mix(BG, YELLOW, a3), anchor="mm")
        d.text((W // 2, 960), "对方才知道从哪答", font=small, fill=mix(BG, MINT, a3), anchor="mm")
        out.append(img)
    return out


def render_b_choose(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(58)
    card_f = font(44)
    small = font(34)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "02 决定")
        a0 = appear(t, 0.02)
        rounded(d, (120, 400, 960, 720), 36, mix(BG, CARD, a0))
        d.text((W // 2, 560), "再问选哪个", font=card_f, fill=mix(CARD, YELLOW, a0), anchor="mm")
        if t >= 0.95:
            a2 = appear(t, 0.95, 0.22)
            d.text((W // 2, 900 + int(lerp(16, 0, a2))), "要决定", font=title_f, fill=mix(BG, WHITE, a2), anchor="mm")
            d.text((W // 2, 1010), "先降低选择成本", font=small, fill=mix(BG, MINT, a2), anchor="mm")
        out.append(img)
    return out


def build_timeline(aligned: list[tuple[float, float, str]], duration: float) -> dict:
    # phrases: 大家好 / 开放问题 / 先给两个选项再问选哪个 / 要决定
    p0, p1, p2, p3 = aligned
    b_start = max(0.0, p2[0] - 0.28)  # 画面先于口播半拍
    mid = p2[0] + (p2[1] - p2[0]) * 0.48
    shots = [
        {"id": "S01a", "kind": "A", "start": 0.0, "end": p0[1], "src": "assets/A-挥手.mp4", "close": True, "line": p0[2]},
        {"id": "S01b", "kind": "A", "start": p0[1], "end": b_start, "src": "assets/A-摊手.mp4", "line": p1[2]},
        {"id": "S02", "kind": "B", "start": b_start, "end": mid, "src": "broll/B-两个选项.mp4", "line": "先给两个选项"},
        {"id": "S03", "kind": "B", "start": mid, "end": p2[1], "src": "broll/B-选哪个.mp4", "line": "再问选哪个"},
        {"id": "S04", "kind": "A", "start": p2[1], "end": duration, "src": "assets/A-指向.mp4", "line": p3[2]},
    ]
    # Fix any inverted durations
    for i, shot in enumerate(shots):
        if shot["end"] <= shot["start"] + 0.12:
            nxt = shots[i + 1]["end"] if i + 1 < len(shots) else duration
            shot["end"] = min(duration, shot["start"] + 0.16)
            if i + 1 < len(shots):
                shots[i + 1]["start"] = shot["end"]
    shots[-1]["end"] = duration
    data = {
        "audio": "audio/vo-full.wav",
        "duration": duration,
        "fps": FPS,
        "size": [W, H],
        "bgm": "audio/bgm.wav",
        "shots": shots,
        "a_caps": [
            (p0[0], p0[1], [p0[2].replace("。", "")]),
            (p1[0], p1[0] + (p1[1] - p1[0]) * 0.55, ["丢一个开放问题"]),
            (p1[0] + (p1[1] - p1[0]) * 0.55, p1[1], ["对方不知道从哪答"]),
            (p3[0], p3[0] + (p3[1] - p3[0]) * 0.42, ["要决定"]),
            (p3[0] + (p3[1] - p3[0]) * 0.42, duration, ["先降低选择成本"]),
        ],
        "shutters": [
            (b_start, list(MINT)),
            (mid, list(WHITE)),
            (p2[1], list(YELLOW)),
        ],
        "eyebrows": [
            (0.0, b_start, "A-ROLL / 01"),
            (p2[1], duration, "A-ROLL / 02"),
        ],
    }
    (ROOT / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def draw_eyebrow(base: Image.Image, t: float, eyebrows) -> None:
    label = None
    for s, e, text in eyebrows:
        if s <= t < e:
            label = text
            break
    if not label:
        return
    d = ImageDraw.Draw(base)
    fnt = font(22)
    d.rectangle((76, 88, 120, 92), fill=(*MINT, 230))
    d.text((136, 78), label, font=fnt, fill=(90, 98, 108, 220))


def draw_pill(base: Image.Image, lines: list[str], y: int = 168) -> None:
    fnt = font(56 if len(lines) == 1 else 50)
    dummy = ImageDraw.Draw(base)
    widths, heights = [], []
    for line in lines:
        x0, y0, x1, y1 = dummy.textbbox((0, 0), line, font=fnt)
        widths.append(x1 - x0)
        heights.append(y1 - y0)
    tw = max(widths)
    line_h = max(heights) + 10
    pad_x, pad_y = 40, 22
    box_w = tw + pad_x * 2
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
    for start, color in shutters:
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
    cues = data["a_caps"]
    shutters = data["shutters"]
    eyebrows = data["eyebrows"]

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
        draw_eyebrow(img, t, eyebrows)
        for s, e, lines in cues:
            if s <= t < e:
                draw_pill(img, lines)
                break
        img = draw_shutter(img, t, shutters)
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
    if dur > src_dur + 0.05:
        vf = f"tpad=stop_mode=clone:stop_duration={dur - src_dur:.3f},{vf}" if kind != "A" else f"setpts=PTS*{dur / src_dur:.6f},{vf}"
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
    final = ROOT / "final" / f"{NAME}.mp4"
    final.parent.mkdir(exist_ok=True)

    cuts = [float(s) for s, _ in data["shutters"]]
    make_sfx(cuts, float(data["duration"]))

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
    run(["ffmpeg", "-y", "-i", str(final), "-c", "copy", str(out)])
    run(["ffmpeg", "-y", "-i", str(final), "-c", "copy", str(ROOT / f"00_最终成片_{NAME}.mp4")])

    staged = Path("/workspace/成片") / f"05-{NAME}.mp4"
    staged.parent.mkdir(exist_ok=True)
    shutil.copy2(final, staged)
    return staged


def make_cover() -> Path:
    dest = ROOT / f"00_封面_{NAME}.jpg"
    img = new_bg()
    d = ImageDraw.Draw(img)
    still = Image.open(A_STILLS["wave"]).convert("RGB")
    still = still.resize((720, 1280), Image.Resampling.LANCZOS)
    img.paste(still.crop((0, 200, 720, 980)), (180, 520))
    d.rectangle((0, 0, W, 480), fill=BG)
    title = font(64)
    sub = font(36)
    d.text((W // 2, 180), "先给选项", font=title, fill=WHITE, anchor="mm")
    d.text((W // 2, 270), "再要决定", font=title, fill=YELLOW, anchor="mm")
    d.text((W // 2, 370), "开放问题不知从哪答", font=sub, fill=MUTED, anchor="mm")
    img.save(dest, quality=92)
    return dest


def write_status(duration: float, staged: Path) -> None:
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    import hashlib

    sha = hashlib.sha256(vo.encode("utf-8")).hexdigest()
    status = {
        "schema_version": 1,
        "project_name": "05_先给选项再要决定",
        "video_type": "普通短视频",
        "production_method": "白底小灯 A-roll 静帧Ken Burns + 黑底信息图 B-roll + edge-tts Yunyang + FFmpeg",
        "status": "已交付",
        "current_stage": "核验并交付",
        "script": {"path": "script/voiceover.txt", "sha256": sha},
        "audio": {
            "path": "audio/vo-full.wav",
            "alignment_path": "audio/vo-align.txt",
            "voice_id": VOICE,
            "sample_rate": 44100,
            "channels": 1,
            "duration_ms": int(duration * 1000),
            "note": "云端替代豆包 TTS：edge-tts zh-CN-YunyangNeural",
        },
        "deliverables": {
            "final_video": str(staged),
            "cover": f"00_封面_{NAME}.jpg",
        },
        "updated_at": "2026-09-11T10:55:00Z",
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    for still in A_STILLS.values():
        if not still.exists():
            raise FileNotFoundError(still)

    duration, aligned = make_voiceover()
    print("VO", duration, aligned)
    make_bgm(duration)
    data = build_timeline(aligned, duration)

    still_to_aroll(A_STILLS["wave"], ROOT / "assets" / "A-挥手.mp4", max(2.2, float(data["shots"][0]["end"]) + 0.4), close=True)
    still_to_aroll(A_STILLS["shrug"], ROOT / "assets" / "A-摊手.mp4", 4.2, close=False)
    still_to_aroll(A_STILLS["point"], ROOT / "assets" / "A-指向.mp4", 3.4, close=False)

    b1 = max(1.2, float(data["shots"][2]["end"]) - float(data["shots"][2]["start"]))
    b2 = max(1.2, float(data["shots"][3]["end"]) - float(data["shots"][3]["start"]))
    frames_to_mp4(render_b_options(b1 + 0.15), ROOT / "broll" / "B-两个选项.mp4")
    frames_to_mp4(render_b_choose(b2 + 0.15), ROOT / "broll" / "B-选哪个.mp4")

    make_cover()
    staged = assemble(data)
    write_status(duration, staged)
    print("STAGED", staged, "dur", probe_dur(staged))


if __name__ == "__main__":
    main()
