#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Episode 27 · 三秒留人. Cloud A-roll + B-roll from locked Drive VO/timeline.

Drive source: 12_三秒留人. Not drama. No C:/D:/G:. No Drive upload.
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import struct
import subprocess
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
CLOUD = ROOT.parent
W, H, FPS = 1080, 1920, 24
NAME = "三秒留人"
EP = "27"
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_RG = "/tmp/NotoSansSC-Regular.otf"
FONT_WQY = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

BG = (11, 13, 18)
CARD = (24, 28, 38)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
CREAM = (245, 247, 250)
RED = (255, 118, 118)
INK = (28, 32, 36)

A_SOURCES = {
    "V-挥手.mp4": CLOUD / "06" / "assets" / "V-挥手.mp4",
    "V-摊手.mp4": CLOUD / "06" / "assets" / "V-摊手.mp4",
    "V-点赞.mp4": CLOUD / "06" / "assets" / "V-点赞.mp4",
    "A-角色-小灯-摊手.jpg": CLOUD / "06" / "assets" / "A-角色-小灯-摊手.jpg",
    "A-正对讲.jpg": CLOUD / "03" / "assets" / "A-正对讲.jpg",
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


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    for path in ((FONT_BD if bold else FONT_RG), FONT_WQY):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def ease_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def appear(t: float, start: float, dur: float = 0.38) -> float:
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


def load_timeline() -> dict:
    return json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))


def ensure_assets() -> None:
    (ROOT / "assets").mkdir(parents=True, exist_ok=True)
    (ROOT / "broll").mkdir(parents=True, exist_ok=True)
    (ROOT / "audio").mkdir(parents=True, exist_ok=True)
    for name, src in A_SOURCES.items():
        dest = ROOT / "assets" / name
        if src.exists() and not dest.exists():
            shutil.copy2(src, dest)
        if not dest.exists():
            raise FileNotFoundError(src)
    vo = ROOT / "audio" / "vo-full.wav"
    if not vo.exists():
        raise FileNotFoundError(vo)


def kenburns_still(src: Path, dest: Path, dur: float, close: bool = False) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    frames = max(8, int(round(dur * FPS)))
    if close:
        z0, z1, ybias = 1.14, 1.22, 36
    else:
        z0, z1, ybias = 1.04, 1.11, 24
    step = (z1 - z0) / max(1, frames)
    vf = (
        f"scale=1400:2489:force_original_aspect_ratio=increase,crop=1400:2489,"
        f"zoompan=z='{z0}+{step:.6f}*on':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)+{ybias}':"
        f"d={frames}:s={W}x{H}:fps={FPS},format=yuv420p"
    )
    run(
        [
            "ffmpeg", "-y", "-loop", "1", "-i", str(src),
            "-t", f"{dur:.3f}", "-vf", vf, "-an",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            str(dest),
        ]
    )


def ensure_talking_a() -> Path:
    dest = ROOT / "assets" / "V-正对讲.mp4"
    if dest.exists() and dest.stat().st_size > 10000:
        return dest
    still = ROOT / "assets" / "A-正对讲.jpg"
    kenburns_still(still, dest, 6.2, close=False)
    return dest


def write_wav_stereo(path: Path, samples: list[float], sr: int = 44100) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        buf = bytearray()
        for s in samples:
            q = int(max(-1.0, min(1.0, s)) * 32767)
            buf.extend(struct.pack("<hh", q, q))
        wf.writeframes(buf)


def make_bgm(dur: float) -> Path:
    sr = 44100
    n = int(sr * (dur + 1.6))
    samples = []
    for i in range(n):
        t = i / sr
        env = min(1.0, t / 0.8) * min(1.0, (n / sr - t) / 0.7)
        s = (
            0.07 * math.sin(2 * math.pi * 196.0 * t)
            + 0.05 * math.sin(2 * math.pi * 246.94 * t)
            + 0.035 * math.sin(2 * math.pi * 293.66 * t)
            + 0.02 * math.sin(2 * math.pi * 392.0 * t)
        )
        samples.append(s * env)
    dest = ROOT / "audio/bgm.wav"
    write_wav_stereo(dest, samples, sr)
    return dest


def make_sfx(cuts: list[float], dur: float) -> Path:
    sr = 44100
    n = int(sr * (dur + 0.4))
    samples = [0.0] * n
    for cut in cuts:
        if cut < 0.10:
            continue
        start = int(cut * sr)
        length = int(0.05 * sr)
        for i in range(length):
            if start + i >= n:
                break
            t = i / sr
            env = math.exp(-t * 72) * (1 - i / length)
            samples[start + i] += env * 0.24 * math.sin(2 * math.pi * (440 + 880 * (i / length)) * t)
    dest = ROOT / "audio/sfx.wav"
    write_wav_stereo(dest, samples, sr)
    return dest


def new_bg() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    overlay = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(overlay)
    d.ellipse((-240, -300, 760, 620), fill=(16, 42, 38))
    d.ellipse((420, 1180, 1360, 2080), fill=(42, 32, 16))
    overlay = overlay.filter(ImageFilter.GaussianBlur(120))
    return Image.blend(img, overlay, 0.58)


def tag(draw, t: float, label: str) -> None:
    a = appear(t, 0.0, 0.24)
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
    frames[min(len(frames) // 2, len(frames) - 1)].save(dest.with_suffix(".jpg"), quality=92)


def b_relate(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, huge, sub_f = font(62), font(72), font(40)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "钩子 先问这一句")
        a0 = appear(t, 0.02)
        d.text((W // 2, 320 + int(lerp(22, 0, a0))), "观众刷到你", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        d.text((W // 2, 410), "只问一件事", font=sub_f, fill=mix(BG, MUTED, appear(t, 0.18)), anchor="mm")
        a1 = appear(t, 0.55)
        punch = appear(t, 2.05, 0.28)
        if a1 > 0.04:
            y = 560 + int(lerp(28, 0, a1))
            rounded(d, (84, y, 996, y + 540), 40, mix(BG, CARD, a1))
            d.text((W // 2, y + 165), "这跟我", font=huge, fill=mix(CARD, WHITE, a1), anchor="mm")
            d.text((W // 2, y + 300), "有没有关系", font=huge, fill=mix(CARD, YELLOW, a1), anchor="mm")
            d.text((W // 2, y + 430), "没有，就划走", font=sub_f, fill=mix(CARD, MUTED, a1), anchor="mm")
        if punch > 0.04:
            y2 = 1200 + int(lerp(24, 0, punch))
            rounded(d, (140, y2, 940, y2 + 240), 32, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y2 + 120), "先回答这一句", font=title_f, fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def b_result(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, sub_f = font(56), font(50), font(36)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "钩子 不是打招呼")
        a0 = appear(t, 0.02)
        d.text((W // 2, 300 + int(lerp(20, 0, a0))), "先甩他正在亏的结果", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        a1 = appear(t, 0.28)
        if a1 > 0.04:
            y = 480 + int(lerp(24, 0, a1))
            rounded(d, (105, y, 975, y + 220), 32, mix(BG, CARD, a1))
            d.text((W // 2, y + 110), "大家好，我是……", font=card_f, fill=mix(CARD, MUTED, a1), anchor="mm")
            strike = appear(t, 0.55, 0.22)
            if strike > 0.04:
                x1 = int(lerp(195, 885, strike))
                d.line([(195, y + 110), (x1, y + 110)], fill=mix(CARD, RED, strike), width=12)
        a2 = appear(t, 0.85)
        if a2 > 0.04:
            y = 780 + int(lerp(24, 0, a2))
            rounded(d, (105, y, 975, y + 420), 34, mix(BG, CARD, a2))
            d.text((W // 2, y + 140), "你正在亏的是", font=sub_f, fill=mix(CARD, MUTED, a2), anchor="mm")
            d.text((W // 2, y + 260), "前三秒被划走", font=title_f, fill=mix(CARD, YELLOW, a2), anchor="mm")
        out.append(img)
    return out


def b_formula(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, sub_f, small = font(56), font(44), font(36), font(32)
    t1, t2, t2b, t3 = 0.12, 2.7, 4.4, 8.0
    rows = [
        (t1, "01", "第一秒", "别报名字，先报损失", YELLOW),
        (t2, "02", "第二秒", "甩对照", MINT),
        (t3, "03", "第三秒", "给一条马上能改的指令", YELLOW),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "三秒公式")
        d.text(
            (W // 2, 280 + int(lerp(18, 0, appear(t, 0.02)))),
            "前三秒只做三件事",
            font=title_f,
            fill=mix(BG, WHITE, appear(t, 0.02)),
            anchor="mm",
        )
        y0 = 390
        for idx, (ts, num, head, body, color) in enumerate(rows):
            a = appear(t, ts, 0.28)
            if a < 0.04:
                continue
            y = y0 + idx * 280 + int(lerp(22, 0, a))
            rounded(d, (84, y, 996, y + 250), 34, mix(BG, CARD, a))
            d.ellipse((120, y + 75, 210, y + 165), fill=mix(CARD, color, a))
            d.text((165, y + 120), num, font=small, fill=mix(color, INK, a), anchor="mm")
            d.text((240, y + 85), head, font=sub_f, fill=mix(CARD, color, a), anchor="lm")
            d.text((240, y + 165), body, font=card_f, fill=mix(CARD, WHITE, a), anchor="lm")
        if t2 <= t < t3:
            a = appear(t, t2b, 0.22)
            if a > 0.04:
                rounded(d, (120, 1470, 960, 1750), 28, mix(BG, (32, 24, 20), a))
                d.text((W // 2, 1550), "多数人：自我介绍", font=sub_f, fill=mix(BG, RED, a), anchor="mm")
                d.text((W // 2, 1660), "留下的人：给冲突", font=sub_f, fill=mix(BG, MINT, a), anchor="mm")
        out.append(img)
    return out


def b_specific(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, sub_f, vs_f = font(58), font(36), font(48)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "铁律")
        a = appear(t, 0.02, 0.28)
        left = int(lerp(-480, 54, a))
        right = int(lerp(W + 30, 546, a))
        rounded(d, (left, 390, left + 480, 1230), 34, mix(BG, CARD, a))
        rounded(d, (right, 390, right + 480, 1230), 34, mix(BG, CARD, a))
        d.text((left + 240, 520), "热闹", font=title_f, fill=mix(BG, MUTED, a), anchor="mm")
        d.text((left + 240, 660), "音效堆满", font=sub_f, fill=mix(BG, MUTED, a), anchor="mm")
        d.text((left + 240, 750), "表情包乱闪", font=sub_f, fill=mix(BG, MUTED, a), anchor="mm")
        d.text((right + 240, 520), "具体", font=title_f, fill=mix(BG, YELLOW, a), anchor="mm")
        d.text((right + 240, 660), "一句损失", font=sub_f, fill=mix(BG, WHITE, a), anchor="mm")
        d.text((right + 240, 750), "一对对照", font=sub_f, fill=mix(BG, WHITE, a), anchor="mm")
        if a > 0.7:
            d.ellipse((W // 2 - 42, 750, W // 2 + 42, 834), fill=(18, 22, 28))
            d.text((W // 2, 792), "vs", font=vs_f, fill=YELLOW, anchor="mm")
        a2 = appear(t, 1.15)
        if a2 > 0.04:
            d.text((W // 2, 1470 + int(lerp(20, 0, a2))), "留人不是更热闹", font=title_f, fill=mix(BG, WHITE, a2), anchor="mm")
            d.text((W // 2, 1590), "是更具体", font=title_f, fill=mix(BG, YELLOW, a2), anchor="mm")
        out.append(img)
    return out


def render_broll(data: dict) -> None:
    durs = {}
    for shot in data["shots"]:
        if shot["kind"] == "B":
            durs[shot["src"]] = max(1.4, float(shot["end"]) - float(shot["start"]))
    jobs = [
        ("broll/B-跟我有关.mp4", b_relate),
        ("broll/B-先甩结果.mp4", b_result),
        ("broll/B-三秒公式.mp4", b_formula),
        ("broll/B-更具体.mp4", b_specific),
    ]
    for rel, fn in jobs:
        dur = durs.get(rel)
        if not dur:
            raise SystemExit(f"no duration for {rel}")
        print("render", rel, f"{dur:.2f}s")
        frames = fn(dur + 0.08)
        dest = ROOT / rel
        frames_to_mp4(frames, dest)


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
    for item in shutters:
        dt = t - float(item["start"])
        color = tuple(item["color"])
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
        for cap in data["a_caps"]:
            if cap["start"] <= t < cap["end"]:
                draw_pill(img, cap["lines"])
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
        vf = (
            f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},setsar=1,format=yuv420p"
        )
    if kind == "A" and dur > src_dur + 0.05:
        vf = f"setpts=PTS*{dur / src_dur:.6f},{vf}"
    elif dur > src_dur + 0.02:
        vf = f"{vf},tpad=stop_mode=clone:stop_duration={dur - src_dur:.3f}"
    run(
        [
            "ffmpeg", "-y", "-i", str(src), "-t", f"{dur:.3f}",
            "-vf", vf, "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            str(dest),
        ]
    )


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
    run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
            str(concat),
        ]
    )

    caps = render_captions(data)
    burned = shots_dir / "video_subs.mp4"
    run(
        [
            "ffmpeg", "-y", "-i", str(concat), "-i", str(caps),
            "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an",
            str(burned),
        ]
    )

    duration = float(data["duration"])
    make_bgm(duration)
    make_sfx([float(s["start"]) for s in data["shots"][1:]], duration)

    audio = ROOT / data["audio"]
    bgm = ROOT / "audio" / "bgm.wav"
    sfx = ROOT / "audio" / "sfx.wav"
    final = ROOT / "final" / f"{NAME}.mp4"
    final.parent.mkdir(exist_ok=True)
    run(
        [
            "ffmpeg", "-y",
            "-i", str(burned), "-i", str(audio), "-i", str(bgm), "-i", str(sfx),
            "-filter_complex",
            "[1:a]loudnorm=I=-16:LRA=11:TP=-1.5,aformat=sample_rates=44100:channel_layouts=stereo[vo];"
            "[2:a]adelay=800|800,volume=0.18,highpass=f=140[bg];"
            "[3:a]volume=0.30[sfx];"
            "[vo][bg][sfx]amix=inputs=3:duration=first:dropout_transition=2,alimiter=limit=0.95[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart",
            str(final),
        ]
    )

    deliver = ROOT / f"00_最终成片_{NAME}.mp4"
    out = ROOT / "output" / f"{NAME}.mp4"
    out.parent.mkdir(exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(final), "-c", "copy", str(deliver)])
    run(["ffmpeg", "-y", "-i", str(final), "-c", "copy", str(out)])

    staged = Path("/workspace/成片") / f"{EP}-{NAME}.mp4"
    staged.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(final), "-c", "copy", str(staged)])
    print("FINAL", deliver, "dur", probe_dur(deliver))
    print("STAGED", staged, "dur", probe_dur(staged))
    return staged


def make_cover() -> Path:
    src = ROOT / "assets" / "A-角色-小灯-摊手.jpg"
    char = Image.open(src).convert("RGB")
    scale = max(W / char.width, H / char.height)
    nw, nh = int(char.width * scale), int(char.height * scale)
    char = char.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - W) // 2
    y = int((nh - H) * 0.62)
    canvas = char.crop((x, y, x + W, y + H))
    overlay = Image.new("RGBA", (W, H), (11, 13, 18, 48))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(canvas)
    rounded(d, (90, 90, 990, 430), 36, (22, 24, 28))
    d.text((W // 2, 168), "前三秒怎么留人", font=font(58), fill=WHITE, anchor="mm")
    d.text((W // 2, 258), "钩子不是打招呼", font=font(44), fill=MINT, anchor="mm")
    d.text((W // 2, 348), "损失 · 对照 · 指令", font=font(30), fill=MUTED, anchor="mm")
    dest = ROOT / f"00_封面_{NAME}.jpg"
    dest.parent.mkdir(exist_ok=True)
    canvas.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    shutil.copy2(dest, ROOT / "final" / "cover.jpg")
    return dest


def write_docs(duration: float, staged: Path, report: dict) -> None:
    vo = (ROOT / "script/voiceover.txt").read_text(encoding="utf-8").strip()
    sha = hashlib.sha256(vo.encode("utf-8")).hexdigest()
    (ROOT / "项目说明.md").write_text(
        f"""# 27 · 三秒留人

普通短视频 / 知识口播。不是剧情短剧。

- **来源**：Drive `12_三秒留人`（锁定口播 + 锁定时间轴）
- **工程目录**：`/workspace/.abroll-cloud/27/`
- **工程成片**：`00_最终成片_{NAME}.mp4`
- **中转成片**：`{staged}`

## 这是什么

竖屏 A/B 卷。白底小灯说判断，黑底图讲前三秒留人：先问「跟我有没有关系」，再甩损失、对照、指令。收束：留人不是更热闹，是更具体。

钩子：知识视频不是输在后面讲得浅，是输在前三秒被划走。

## 当前状态

- 视频类型：普通短视频
- 状态：已交付到 `成片/`（只在本 Linux VM，未上传 Drive，未写 C/D/G）
- 规格：1080×1920，{duration:.2f} 秒，24 fps，H.264 + AAC 44100 Hz

## 素材

- 口播：Drive 锁定 `vo-full.wav`（豆包 `zh_female_vv_uranus_bigtts`，30.839s，未重合成）
- 时间轴：Drive 锁定 `timeline.json`（8 镜，无重叠无空缺）
- A 卷：本机 `06/assets` 挥手/摊手/点赞；正对讲由 `03/assets/A-正对讲.jpg` Ken Burns
- B 卷：代码绘制黑底卡（跟我有关 / 先甩结果 / 三秒公式 / 更具体）
- 垫乐：云端合成，未下载 Mixkit

## 文件位置

- 口播：`script/`
- 配音与时间轴：`audio/`
- 镜头表：`timeline.json`
- 中间镜头：`shots/`（不进成片夹）
""",
        encoding="utf-8",
    )
    status = {
        "schema_version": 1,
        "project_name": "27_三秒留人",
        "drive_source": "12_三秒留人",
        "video_type": "普通短视频",
        "episode": 27,
        "production_method": "Drive 锁定口播/时间轴 + 白底小灯 A-roll + 代码黑底 B-roll + FFmpeg",
        "status": "已交付",
        "current_stage": "核验并交付",
        "script": {"path": "script/voiceover.txt", "sha256": sha},
        "audio": {
            "path": "audio/vo-full.wav",
            "alignment_path": "audio/vo-align.txt",
            "voice_id": "zh_female_vv_uranus_bigtts",
            "sample_rate": 44100,
            "channels": 1,
            "duration_ms": 30839,
            "note": "沿用 Drive 12_三秒留人 锁定 WAV，未重合成",
        },
        "deliverables": {
            "final_video": f"00_最终成片_{NAME}.mp4",
            "staged": str(staged),
            "cover": f"00_封面_{NAME}.jpg",
        },
        "qa": report,
        "updated_at": "2026-09-11T11:50:00Z",
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")


def verify(path: Path) -> dict:
    meta = json.loads(
        subprocess.check_output(
            [
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate,codec_name",
                "-show_entries", "format=duration",
                "-of", "json", str(path),
            ],
            text=True,
        )
    )
    ameta = json.loads(
        subprocess.check_output(
            [
                "ffprobe", "-v", "error", "-select_streams", "a:0",
                "-show_entries", "stream=codec_name,sample_rate,channels",
                "-of", "json", str(path),
            ],
            text=True,
        )
    )
    v, a = meta["streams"][0], ameta["streams"][0]
    dur = float(meta["format"]["duration"])
    num, den = v["r_frame_rate"].split("/")
    fps = float(num) / float(den)
    dec = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    report = {
        "file": str(path),
        "playable": dec.returncode == 0,
        "decode_stderr": (dec.stderr or "")[-400:],
        "width": v["width"],
        "height": v["height"],
        "fps": fps,
        "vcodec": v["codec_name"],
        "acodec": a["codec_name"],
        "sample_rate": int(a["sample_rate"]),
        "channels": a["channels"],
        "duration": dur,
        "checks": {
            "size_1080x1920": v["width"] == 1080 and v["height"] == 1920,
            "fps_24": abs(fps - 24) < 0.05,
            "h264": v["codec_name"] == "h264",
            "aac": a["codec_name"] == "aac",
            "ar_44100": int(a["sample_rate"]) == 44100,
            "decode_ok": dec.returncode == 0,
            "duration_locked": abs(dur - 30.839) < 0.25,
        },
    }
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    qa_dir = ROOT / "qa"
    qa_dir.mkdir(exist_ok=True)
    (qa_dir / "ffprobe.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def extract_qa(path: Path, times: list[float]) -> None:
    qa = ROOT / "qa"
    qa.mkdir(exist_ok=True)
    for i, t in enumerate(times):
        dest = qa / f"f{i:02d}_{t:.2f}s.jpg"
        run(["ffmpeg", "-y", "-ss", f"{max(0, t):.3f}", "-i", str(path), "-frames:v", "1", str(dest)])


def update_index(duration: float) -> None:
    idx = Path("/workspace/成片/INDEX.md")
    row = f"| `{EP}-{NAME}.mp4` | {duration:.1f}s |"
    if idx.exists():
        text = idx.read_text(encoding="utf-8")
    else:
        text = "# 成片（可直接看）\n\n竖屏口播 1080×1920，H.264 + AAC。\n\n| 文件 | 时长 |\n|------|------|\n"
    if f"{EP}-{NAME}.mp4" in text:
        return
    lines = text.rstrip().splitlines()
    insert_at = len(lines)
    for i, ln in enumerate(lines):
        if ln.startswith("| `仙侠"):
            insert_at = i
            break
    lines.insert(insert_at, row)
    patched = []
    for ln in lines:
        if "00-" in ln and "19-" in ln and "均已" in ln and "27" not in ln:
            ln = ln.replace("均已在本目录。", "均已在本目录；本轮补 `27-三秒留人.mp4`。")
        patched.append(ln)
    idx.parent.mkdir(parents=True, exist_ok=True)
    idx.write_text("\n".join(patched) + "\n", encoding="utf-8")


def main() -> None:
    ensure_assets()
    ensure_talking_a()
    vo = ROOT / "audio" / "vo-full.wav"
    vo_dur = probe_dur(vo)
    data = load_timeline()
    if abs(vo_dur - float(data["duration"])) > 0.05:
        print("WARN vo", vo_dur, "timeline", data["duration"])
    data["duration"] = float(data["duration"])
    print("VO", f"{vo_dur:.3f}s", "locked", data["duration"])
    render_broll(data)
    make_cover()
    staged = assemble(data)
    report = verify(staged)
    write_docs(probe_dur(staged), staged, report)
    mids = [((s["start"] + s["end"]) / 2) for s in data["shots"]]
    extract_qa(staged, [0.35] + mids + [max(0.05, float(data["duration"]) - 0.35)])
    update_index(probe_dur(staged))
    print("QA", json.dumps(report["checks"], ensure_ascii=False))
    failed = [k for k, v in report["checks"].items() if not v]
    if failed:
        raise SystemExit(f"QA failed: {failed}")


if __name__ == "__main__":
    main()
