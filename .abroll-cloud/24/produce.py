# -*- coding: utf-8 -*-
"""Topic 24: 口播结尾别报时长.

普通短视频 / 口播工艺。白底小灯 A-roll + 黑底信息图 B-roll。
云端 only：草稿 .abroll-cloud/24/，成品中转 成片/24-*.mp4。
禁止 C:\\ D:\\ G:\\；禁止 Drive 上传。不走 drama-pipeline。
"""
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
NAME = "口播结尾别报时长"
STAGED_NAME = "24-口播结尾别报时长.mp4"
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_REG = "/tmp/NotoSansSC-Regular.otf"
FONT_FALLBACK = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
A_SRC = Path("/workspace/.abroll-cloud/06/assets")
VOICE = "zh-CN-YunyangNeural"
B_LEAD = 0.280

BG = (11, 13, 18)
CARD = (24, 28, 38)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
RED = (255, 118, 118)
INK = (22, 24, 28)
CREAM = (245, 247, 250)


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
    path = FONT_BD if bold else FONT_REG
    for candidate in (path, FONT_FALLBACK):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def ease_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def appear(t: float, start: float, dur: float = 0.28) -> float:
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
    d.ellipse((-260, -300, 760, 620), fill=(16, 42, 38))
    d.ellipse((420, 1180, 1380, 2140), fill=(46, 30, 16))
    overlay = overlay.filter(ImageFilter.GaussianBlur(120))
    return Image.blend(img, overlay, 0.58)


def tag(draw: ImageDraw.ImageDraw, t: float, label: str) -> None:
    a = appear(t, 0.0, 0.20)
    if a <= 0:
        return
    fnt = font(30)
    tw, th = text_wh(draw, label, fnt)
    x, y = 84, 86
    rounded(draw, (x - 22, y - 12, x + tw + 22, y + th + 12), 22, mix(BG, (20, 42, 38), a))
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
    frames[min(len(frames) // 2, len(frames) - 1)].save(dest.with_suffix(".jpg"), quality=92)


def strike_line(draw: ImageDraw.ImageDraw, box, progress: float, color) -> None:
    x0, y0, x1, y1 = box
    if progress <= 0.04:
        return
    mid = (y0 + y1) / 2
    x_end = lerp(x0 + 28, x1 - 28, min(1.0, progress))
    draw.line([(x0 + 28, mid), (x_end, mid)], fill=color, width=10)


def render_b_wash(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "错 · 报时长")
        a0 = appear(t, 0.02)
        d.text((W // 2, 186 + int(lerp(16, 0, a0))), "结尾报时长", font=font(56), fill=mix(BG, WHITE, a0), anchor="mm")

        a1 = appear(t, 0.16)
        if a1 > 0.04:
            y = 280 + int(lerp(20, 0, a1))
            rounded(d, (72, y, 508, y + 420), 28, mix(BG, CARD, a1))
            d.text((290, y + 78), "动作刚落地", font=font(40), fill=mix(CARD, WHITE, a1), anchor="mm")
            d.text((290, y + 168), "听众正要去做", font=font(30), fill=mix(CARD, MUTED, a1), anchor="mm")
            d.rounded_rectangle((140, y + 230, 440, y + 350), radius=22, fill=mix(CARD, MINT, a1 * 0.85))
            d.text((290, y + 290), "去做", font=font(48), fill=mix(MINT, INK, a1), anchor="mm")

        a2 = appear(t, 0.32)
        if a2 > 0.04:
            y = 280 + int(lerp(20, 0, a2))
            rounded(d, (572, y, 1008, y + 420), 28, mix(BG, CARD, a2))
            d.text((790, y + 78), "本集约十秒", font=font(40), fill=mix(CARD, RED, a2), anchor="mm")
            d.text((790, y + 168), "倒数盖过指令", font=font(30), fill=mix(CARD, MUTED, a2), anchor="mm")
            clock = appear(t, 0.70, 0.22)
            d.ellipse((690, y + 210, 890, y + 370), outline=mix(CARD, RED, a2), width=8)
            d.text((790, y + 290), "10s", font=font(48), fill=mix(CARD, YELLOW, a2), anchor="mm")
            if clock > 0.04:
                strike_line(d, (600, y + 50, 980, y + 110), clock, mix(CARD, RED, clock))

        punch = appear(t, 1.45, 0.22)
        if punch > 0.04:
            y = 1648 + int(lerp(20, 0, punch))
            rounded(d, (90, y, 990, y + 168), 28, mix(BG, (42, 24, 22), punch))
            d.text((W // 2, y + 84), "动作指令被冲掉", font=font(46), fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_b_cut(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "改法 · 删时长")
        a0 = appear(t, 0.02)
        d.text((W // 2, 186 + int(lerp(14, 0, a0))), "写完结尾", font=font(56), fill=mix(BG, WHITE, a0), anchor="mm")

        a1 = appear(t, 0.16)
        if a1 > 0.04:
            y = 280 + int(lerp(18, 0, a1))
            rounded(d, (72, y, 1008, y + 300), 28, mix(BG, CARD, a1))
            d.text((W // 2, y + 90), "只留一个动作", font=font(48), fill=mix(CARD, MINT, a1), anchor="mm")
            d.text((W // 2, y + 190), "收束给指令，不报秒", font=font(32), fill=mix(CARD, MUTED, a1), anchor="mm")

        a2 = appear(t, 0.40)
        if a2 > 0.04:
            y = 640 + int(lerp(16, 0, a2))
            rounded(d, (72, y, 1008, y + 420), 28, mix(BG, CARD, a2))
            d.text((W // 2, y + 70), "时长划掉", font=font(40), fill=mix(CARD, WHITE, a2), anchor="mm")
            bar = (180, y + 160, 900, y + 250)
            rounded(d, bar, 18, mix(CARD, (56, 40, 40), a2))
            d.text((W // 2, y + 205), "本集约十秒", font=font(36), fill=mix(CARD, MUTED, a2), anchor="mm")
            st = appear(t, 0.78, 0.22)
            if st > 0.04:
                strike_line(d, bar, st, mix(CARD, RED, st))
            d.text((W // 2, y + 330), "不要口头报秒", font=font(34), fill=mix(CARD, YELLOW, a2), anchor="mm")

        punch = appear(t, 1.40, 0.20)
        if punch > 0.04:
            y = 1648 + int(lerp(18, 0, punch))
            rounded(d, (90, y, 990, y + 168), 28, mix(BG, (18, 42, 36), punch))
            d.text((W // 2, y + 84), "把时长删掉", font=font(46), fill=mix(BG, MINT, punch), anchor="mm")
        out.append(img)
    return out


def copy_inputs() -> None:
    assets = ROOT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for name in ("V-挥手.mp4", "V-摊手.mp4", "V-指向.mp4", "A-角色-小灯-摊手.jpg"):
        src = A_SRC / name
        dest = assets / name
        if not src.exists():
            raise SystemExit(f"missing A-roll asset {src}")
        if not dest.exists() or dest.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dest)


def ticks_to_sec(v: float) -> float:
    return float(v) / 10_000_000.0


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


def make_voiceover() -> tuple[float, list[tuple[float, float, str]]]:
    text = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    phrases = [ln.strip() for ln in (ROOT / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    audio = ROOT / "audio"
    audio.mkdir(exist_ok=True)
    mp3 = audio / "vo-full.mp3"
    wav = audio / "vo-full.wav"
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

    aligned[0] = (0.0, aligned[0][1], aligned[0][2])
    for i in range(1, len(aligned)):
        aligned[i] = (aligned[i - 1][1], aligned[i][1], aligned[i][2])
    last_s, _, last_p = aligned[-1]
    aligned[-1] = (last_s, duration, last_p)
    aligned = [(round(s, 3), round(e, 3), p) for s, e, p in aligned]
    (audio / "vo-align.txt").write_text("".join(f"{s:.3f}\t{e:.3f}\t{p}\n" for s, e, p in aligned), encoding="utf-8")
    return duration, aligned


def build_timeline(aligned: list[tuple[float, float, str]], duration: float) -> dict:
    p0, p1, p2, p3, p4 = aligned
    b1 = max(p1[0] + 0.7, p2[0] - B_LEAD)
    b2 = max(p3[0] + 0.55, p4[0] - B_LEAD)
    shots = [
        {"id": "S01a", "kind": "A", "start": 0.0, "end": p0[1], "src": "assets/V-挥手.mp4", "line": p0[2], "close": True},
        {"id": "S01b", "kind": "A", "start": p0[1], "end": b1, "src": "assets/V-摊手.mp4", "line": p1[2]},
        {"id": "S02", "kind": "B", "start": b1, "end": p2[1], "src": "broll/B-时长冲掉.mp4", "line": p2[2], "broll": "wash"},
        {"id": "S03", "kind": "A", "start": p2[1], "end": b2, "src": "assets/V-指向.mp4", "line": p3[2]},
        {"id": "S04", "kind": "B", "start": b2, "end": duration, "src": "broll/B-时长删掉.mp4", "line": p4[2], "broll": "cut"},
    ]
    for i, shot in enumerate(shots):
        shot["start"] = round(float(shot["start"]), 3)
        shot["end"] = round(float(shot["end"]), 3)
        if shot["end"] <= shot["start"] + 0.12:
            raise SystemExit(f"bad shot {shot}")
        if i:
            shots[i]["start"] = shots[i - 1]["end"]
    shots[-1]["end"] = duration
    data = {
        "audio": "audio/vo-full.wav",
        "duration": duration,
        "fps": FPS,
        "size": [W, H],
        "title": NAME,
        "bgm": "audio/bgm.wav",
        "shots": shots,
        "a_caps": [
            {"start": p0[0], "end": p0[1], "lines": ["大家好"]},
            {"start": p1[0], "end": b1, "lines": ["口播结尾别报时长"]},
            {"start": p3[0], "end": b2, "lines": ["收束只留一个动作"]},
        ],
        "shutters": [
            {"start": p0[1], "color": list(CREAM)},
            {"start": b1, "color": list(MINT)},
            {"start": p2[1], "color": list(CREAM)},
            {"start": b2, "color": list(MINT)},
        ],
        "eyebrows": [
            {"start": 0.0, "end": p0[1], "text": "A-ROLL / 1a"},
            {"start": p0[1], "end": b1, "text": "A-ROLL / 1b"},
            {"start": p2[1], "end": b2, "text": "A-ROLL / 03"},
        ],
        "cover": {
            "title": NAME,
            "sub": "报时长会冲掉动作",
            "line": "收束只留一个动作",
            "src": "assets/A-角色-小灯-摊手.jpg",
        },
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
        ms = int(t * 1000)
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
    d.rectangle((76, 88, 120, 92), fill=(*MINT, 230))
    d.text((136, 78), label, font=font(22), fill=(90, 98, 108, 220))


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

    audio = ROOT / data["audio"]
    bgm = ROOT / "audio" / "bgm.wav"
    sfx = ROOT / "audio" / "sfx.wav"
    cuts = [float(s["start"]) for s in data["shutters"]]
    make_sfx(cuts, float(data["duration"]))

    final = ROOT / f"00_最终成片_{NAME}.mp4"
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
    (ROOT / "final").mkdir(exist_ok=True)
    shutil.copy2(final, ROOT / "final" / f"{NAME}.mp4")

    staged = Path("/workspace/成片") / STAGED_NAME
    staged.parent.mkdir(exist_ok=True)
    shutil.copy2(final, staged)
    return staged


def make_cover() -> Path:
    dest = ROOT / f"00_封面_{NAME}.jpg"
    char = Image.open(ROOT / "assets" / "A-角色-小灯-摊手.jpg").convert("RGB")
    scale = max(W / char.width, H / char.height)
    nw, nh = int(char.width * scale), int(char.height * scale)
    char = char.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - W) // 2
    y = int((nh - H) * 0.62)
    canvas = char.crop((x, y, x + W, y + H))
    overlay = Image.new("RGBA", (W, H), (11, 13, 18, 40))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((70, 80, 1010, 470), radius=36, fill=(22, 24, 28))
    d.text((W // 2, 168), "口播结尾", font=font(64), fill=WHITE, anchor="mm")
    d.text((W // 2, 250), "别报时长", font=font(56), fill=MINT, anchor="mm")
    d.text((W // 2, 330), "报时长会冲掉动作", font=font(36), fill=YELLOW, anchor="mm")
    d.text((W // 2, 400), "收束只留一个动作", font=font(30), fill=MUTED, anchor="mm")
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    canvas.save(ROOT / "final" / "cover.jpg", quality=92)
    return dest


def write_docs(duration: float, staged: Path) -> None:
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    sha = hashlib.sha256(vo.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    status = {
        "schema_version": 1,
        "project_name": "24_口播结尾别报时长",
        "video_type": "普通短视频",
        "slug": "350_口播结尾别报时长",
        "title": NAME,
        "production_method": "白底小灯 A-roll（06 已有动作）+ 黑底信息图 B-roll + edge-tts + FFmpeg",
        "status": "已交付",
        "current_stage": "核验并交付",
        "stage": "delivered",
        "voice": VOICE,
        "duration": duration,
        "size": [W, H],
        "fps": FPS,
        "script": {"path": "script/voiceover.txt", "sha256": sha},
        "audio": {
            "path": "audio/vo-full.wav",
            "alignment_path": "audio/vo-align.txt",
            "source": "edge-tts zh-CN-YunyangNeural",
            "sample_rate": 44100,
            "channels": 1,
            "duration_ms": int(duration * 1000),
        },
        "deliverables": {
            "final_video": str(staged),
            "project_final": f"00_最终成片_{NAME}.mp4",
            "cover": f"00_封面_{NAME}.jpg",
        },
        "not": "drama-pipeline / 仙侠短剧 / Drive 上传 / C:D:G:",
        "updated_at": now,
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    explain = f"""# 24 · 口播结尾别报时长

普通短视频 / 口播工艺。**不是**短剧，不走 drama-pipeline。

- **选题**：Drive `_claims/350_口播结尾别报时长.claim`
- **口播原文**：Drive scratch `350_口播结尾别报时长/script/voiceover.txt`
- **成片中转**：`成片/24-口播结尾别报时长.mp4`
- **本集工程成片**：`00_最终成片_口播结尾别报时长.mp4`
- **草稿**：只在 `/workspace/.abroll-cloud/24/`，不写 `C:` / `D:` / `G:`，不上传 Drive

钩子：口播结尾别报时长。  
收束：写完结尾，把时长删掉。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {duration:.2f} 秒。
"""
    (ROOT / "项目说明.md").write_text(explain, encoding="utf-8")


def main() -> None:
    copy_inputs()
    duration, aligned = make_voiceover()
    print("ALIGN", aligned, "DUR", duration)
    data = build_timeline(aligned, duration)
    make_bgm(duration)

    b1 = next(s for s in data["shots"] if s["id"] == "S02")
    b2 = next(s for s in data["shots"] if s["id"] == "S04")
    d1 = max(2.2, float(b1["end"]) - float(b1["start"]))
    d2 = max(2.2, float(b2["end"]) - float(b2["start"]))
    print("render B-时长冲掉", d1)
    frames_to_mp4(render_b_wash(d1), ROOT / "broll" / "B-时长冲掉.mp4")
    print("render B-时长删掉", d2)
    frames_to_mp4(render_b_cut(d2), ROOT / "broll" / "B-时长删掉.mp4")

    make_cover()
    staged = assemble(data)
    write_docs(probe_dur(staged), staged)
    print("STAGED", staged, "dur", probe_dur(staged))


if __name__ == "__main__":
    main()
