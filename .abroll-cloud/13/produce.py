#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Topic 13 / topics.md #6: 字典靠名字，不是第几个. Cloud A-roll + B-roll."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
WORK = Path("/workspace")
W, H, FPS = 1080, 1920, 24
NAME = "字典靠名字不是第几个"
TITLE = "字典靠名字，不是第几个"
B_LEAD = 0.28
VOICE_NOTE = "复用工厂口播 .abroll-cloud/aroll/audio/06_字典靠名字不是第几个.wav"

BG = (11, 13, 18)
CARD = (24, 28, 38)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
CREAM = (245, 247, 250)
RED = (255, 118, 118)
INK = (28, 32, 36)

FONT_CANDIDATES = (
    Path("/tmp/NotoSansSC-Bold.otf"),
    Path("/tmp/NotoSansSC-Regular.otf"),
    Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
    Path("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"),
)

FACTORY_WAV = WORK / ".abroll-cloud/aroll/audio/06_字典靠名字不是第几个.wav"
BROLL_DIR = WORK / ".abroll-cloud/broll-assets"
A_SOURCES = {
    "V-挥手.mp4": WORK / ".abroll-cloud/06/assets/V-挥手.mp4",
    "V-摊手.mp4": WORK / ".abroll-cloud/06/assets/V-摊手.mp4",
    "V-点赞.mp4": WORK / ".abroll-cloud/06/assets/V-点赞.mp4",
    "A-角色-小灯-摊手.jpg": WORK / ".abroll-cloud/06/assets/A-角色-小灯-摊手.jpg",
}
PLATES = {
    "boxes": BROLL_DIR / "t06-boxes.mp4",
    "boxes_still": BROLL_DIR / "t06a-named-boxes-vs-numbers.png",
    "key": BROLL_DIR / "t06b-key-not-index.png",
    "card": BROLL_DIR / "t06-card-dict-vs-list.png",
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
    for path in FONT_CANDIDATES:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
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


def ensure_assets() -> None:
    dest = ROOT / "assets"
    dest.mkdir(parents=True, exist_ok=True)
    for name, src in A_SOURCES.items():
        if not src.exists():
            raise FileNotFoundError(src)
        target = dest / name
        if not target.exists() or target.stat().st_size != src.stat().st_size:
            shutil.copy2(src, target)
    plates = ROOT / "assets" / "plates"
    plates.mkdir(parents=True, exist_ok=True)
    for name, src in PLATES.items():
        if not src.exists():
            raise FileNotFoundError(src)
        target = plates / src.name
        if not target.exists() or target.stat().st_size != src.stat().st_size:
            shutil.copy2(src, target)


def prepare_voice() -> Path:
    audio = ROOT / "audio"
    audio.mkdir(parents=True, exist_ok=True)
    wav = audio / "vo-full.wav"
    if not FACTORY_WAV.exists():
        raise FileNotFoundError(FACTORY_WAV)
    if not wav.exists() or wav.stat().st_size != FACTORY_WAV.stat().st_size:
        shutil.copy2(FACTORY_WAV, wav)
    return wav


def speech_islands(wav: Path, noise_db: float = -35.0, min_silence: float = 0.12) -> list[tuple[float, float]]:
    p = subprocess.run(
        [
            "ffmpeg", "-i", str(wav),
            "-af", f"silencedetect=noise={noise_db}dB:d={min_silence}",
            "-f", "null", "-",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    starts: list[float] = []
    ends: list[float] = []
    for line in (p.stderr or "").splitlines():
        if "silence_start:" in line:
            starts.append(float(line.split("silence_start:")[1].strip()))
        elif "silence_end:" in line:
            ends.append(float(line.split("silence_end:")[1].split("|")[0].strip()))
    dur = probe_dur(wav)
    # Invert silences → speech. Leading silence_start=0 is common.
    cursor = 0.0
    islands: list[tuple[float, float]] = []
    events: list[tuple[float, str]] = [(s, "s") for s in starts] + [(e, "e") for e in ends]
    events.sort()
    speaking = True
    # If first event is silence_start at ~0, we begin in silence.
    if starts and starts[0] < 0.05:
        speaking = False
        cursor = 0.0
    for t, kind in events:
        if kind == "s" and speaking:
            if t - cursor > 0.04:
                islands.append((cursor, t))
            speaking = False
        elif kind == "e" and not speaking:
            cursor = t
            speaking = True
    if speaking and dur - cursor > 0.04:
        islands.append((cursor, dur))
    return islands


def align_phrases(wav: Path) -> tuple[float, list[tuple[float, float, str]]]:
    phrases = [ln.strip() for ln in (ROOT / "script/phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    dur = probe_dur(wav)
    islands = speech_islands(wav)
    if len(islands) < len(phrases):
        raise RuntimeError(f"too few speech islands: {len(islands)} < {len(phrases)} {islands}")

    # Short gaps are commas; long gaps are phrase boundaries.
    groups: list[list[tuple[float, float]]] = [[islands[0]]]
    for prev, cur in zip(islands, islands[1:]):
        gap = cur[0] - prev[1]
        if gap < 0.45:
            groups[-1].append(cur)
        else:
            groups.append([cur])

    # If extra islands (factory WAV has 9 islands / 6 phrases), keep merging shortest leftover gap.
    while len(groups) > len(phrases):
        gaps = []
        for i in range(len(groups) - 1):
            gaps.append((groups[i + 1][0][0] - groups[i][-1][1], i))
        _, idx = min(gaps)
        groups[idx].extend(groups[idx + 1])
        del groups[idx + 1]
    while len(groups) < len(phrases):
        # split the longest group
        gi = max(range(len(groups)), key=lambda i: groups[i][-1][1] - groups[i][0][0])
        g = groups[gi]
        if len(g) < 2:
            break
        mid = len(g) // 2
        groups = groups[:gi] + [g[:mid], g[mid:]] + groups[gi + 1 :]

    if len(groups) != len(phrases):
        raise RuntimeError(f"phrase group mismatch {len(groups)} vs {len(phrases)}: {groups}")

    raw = [(g[0][0], g[-1][1], p) for g, p in zip(groups, phrases)]
    closed: list[tuple[float, float, str]] = []
    for i, (s, e, p) in enumerate(raw):
        start = 0.0 if i == 0 else raw[i - 1][1] if False else (raw[i - 1][1] + s) / 2
        closed.append((s, e, p))
    # Close: start of phrase i = end of previous island group start (use next island start as boundary)
    aligned: list[tuple[float, float, str]] = []
    for i, phrase in enumerate(phrases):
        start = 0.0 if i == 0 else groups[i][0][0]
        end = groups[i + 1][0][0] if i + 1 < len(groups) else dur
        aligned.append((start, end, phrase))
    aligned[0] = (0.0, aligned[0][1], aligned[0][2])
    aligned[-1] = (aligned[-1][0], dur, aligned[-1][2])
    for i in range(len(aligned) - 1):
        aligned[i] = (aligned[i][0], aligned[i + 1][0], aligned[i][2])

    lines = [f"{s:.3f}\t{e:.3f}\t{p}" for s, e, p in aligned]
    (ROOT / "audio/vo-align.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    pretty = [f"[{int(s * 1000)}ms-{int(e * 1000)}ms] {p}" for s, e, p in aligned]
    (ROOT / "audio/vo-align-pretty.txt").write_text("\n".join(pretty) + "\n", encoding="utf-8")
    return dur, aligned


def build_timeline(aligned: list[tuple[float, float, str]], duration: float) -> dict:
    recipe = json.loads((ROOT / "plan/shot_recipe.json").read_text(encoding="utf-8"))
    p0, p1, p2, p3, p4, p5 = aligned
    b0 = max(p0[1] + 0.35, p2[0] - B_LEAD)

    starts = [0.0, p0[1], b0, p3[0], p4[0], p5[0]]
    ends = starts[1:] + [duration]
    # Keep monotonic and min length
    for i in range(len(starts)):
        if ends[i] <= starts[i] + 0.16:
            ends[i] = min(duration, starts[i] + 0.18)
            if i + 1 < len(starts):
                starts[i + 1] = ends[i]
    ends[-1] = duration

    shots_out = []
    a_caps = []
    eyebrows = []
    shutters = []
    for i, spec in enumerate(recipe["shots"]):
        start, end = round(starts[i], 3), round(ends[i], 3)
        item = {
            "id": spec["id"],
            "kind": spec["kind"],
            "start": start,
            "end": end,
            "src": spec["src"],
            "line": spec["phrases"][0],
        }
        if spec.get("close"):
            item["close"] = True
        if spec.get("broll"):
            item["broll"] = spec["broll"]
        shots_out.append(item)
        if spec["kind"] == "A":
            line = spec["phrases"][0].strip("。")
            if "，" in line and len(line) > 8:
                left, right = line.split("，", 1)
                mid = start + (end - start) * 0.48
                a_caps.append({"start": start, "end": round(mid, 3), "lines": [left]})
                a_caps.append({"start": round(mid, 3), "end": end, "lines": [right]})
            else:
                a_caps.append({"start": start, "end": end, "lines": [line]})
            eyebrows.append({"start": start, "end": end, "text": f"A-ROLL / {spec['id'][-2:]}"})
        if i > 0:
            color = list(CREAM) if spec["kind"] == "A" else list(MINT)
            if i == len(recipe["shots"]) - 1:
                color = list(YELLOW)
            shutters.append({"start": start, "color": color})

    data = {
        "audio": "audio/vo-full.wav",
        "duration": round(duration, 3),
        "fps": FPS,
        "size": [W, H],
        "title": TITLE,
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


def make_bgm(duration: float) -> Path:
    dest = ROOT / "audio/bgm.wav"
    run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"sine=frequency=196:sample_rate=44100:duration={duration + 1.6:.2f}",
            "-f", "lavfi", "-i", f"sine=frequency=247:sample_rate=44100:duration={duration + 1.6:.2f}",
            "-filter_complex",
            "[0:a][1:a]amix=inputs=2:duration=longest,lowpass=f=420,volume=0.22,aformat=sample_rates=44100:channel_layouts=stereo",
            str(dest),
        ]
    )
    return dest


def make_sfx(cuts: list[float], duration: float) -> Path:
    dest = ROOT / "audio/sfx.wav"
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
        proc.stdin.write(im.convert("RGB").resize((W, H), Image.Resampling.LANCZOS).tobytes())
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(err[-2000:])
    mid = frames[min(len(frames) // 2, len(frames) - 1)]
    mid.convert("RGB").save(dest.with_suffix(".jpg"), quality=92)


def decode_video_frames(src: Path, count: int) -> list[Image.Image]:
    cmd = [
        "ffmpeg", "-i", str(src),
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=rgb24",
        "-f", "rawvideo", "-",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    assert proc.stdout is not None
    frame_size = W * H * 3
    frames: list[Image.Image] = []
    while True:
        buf = proc.stdout.read(frame_size)
        if len(buf) < frame_size:
            break
        frames.append(Image.frombytes("RGB", (W, H), buf))
    proc.stdout.close()
    proc.wait()
    if not frames:
        raise RuntimeError(f"no frames from {src}")
    while len(frames) < count:
        frames.append(frames[-1].copy())
    return frames[:count]


def kenburns_still(src: Path, count: int, z0: float = 1.04, z1: float = 1.14) -> list[Image.Image]:
    im = Image.open(src).convert("RGB")
    # cover 1080x1920 then zoom
    scale = max(W / im.width, H / im.height) * 1.18
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    out = []
    for i in range(count):
        p = i / max(1, count - 1)
        z = lerp(z0, z1, p)
        cw, ch = int(W * z), int(H * z)
        x = (nw - cw) // 2
        y = max(0, int((nh - ch) * 0.42))
        crop = im.crop((x, y, x + cw, y + ch)).resize((W, H), Image.Resampling.LANCZOS)
        out.append(crop)
    return out


def dim_plate(im: Image.Image, top_a: int = 170, bot_a: int = 200) -> Image.Image:
    base = im.convert("RGBA")
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for y in range(H):
        if y < 520:
            a = int(top_a * (1 - y / 520) + 70 * (y / 520))
        elif y > 1280:
            a = int(70 + (bot_a - 70) * ((y - 1280) / 640))
        else:
            a = 70
        sd.line([(0, y), (W, y)], fill=(8, 10, 14, a))
    return Image.alpha_composite(base, shade).convert("RGB")


def tag_label(draw: ImageDraw.ImageDraw, t: float, label: str) -> None:
    a = appear(t, 0.0, 0.22)
    if a <= 0:
        return
    fnt = font(28)
    tw, th = text_wh(draw, label, fnt)
    x, y = 84, 88
    rounded(draw, (x - 22, y - 12, x + tw + 22, y + th + 12), 22, mix(BG, (20, 42, 38), a))
    draw.text((x, y), label, font=fnt, fill=mix(BG, MINT, a))


def punch_bar(draw: ImageDraw.ImageDraw, t: float, when: float, text: str, fill_bg, fill_fg) -> None:
    a = appear(t, when, 0.28)
    if a <= 0.04:
        return
    y = 1580 + int(lerp(28, 0, a))
    rounded(draw, (90, y, 990, y + 220), 28, mix(BG, fill_bg, a))
    draw.text((W // 2, y + 110), text, font=font(56), fill=mix(BG, fill_fg, a), anchor="mm")


def render_b_key(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    plates = decode_video_frames(ROOT / "assets/plates/t06-boxes.mp4", n)
    title_f, card_f, sub_f = font(56), font(40), font(30)
    out = []
    for i in range(n):
        t = i / FPS
        img = dim_plate(plates[i], 190, 210)
        d = ImageDraw.Draw(img)
        tag_label(d, t, "对照 键不是下标")
        a0 = appear(t, 0.04)
        d.text((W // 2, 220 + int(lerp(18, 0, a0))), "方括号里是键", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        d.text((W // 2, 300), "取出的是值，不是整对", font=sub_f, fill=mix(BG, MUTED, appear(t, 0.16)), anchor="mm")

        a1 = appear(t, 0.28)
        if a1 > 0.04:
            y = 1180 + int(lerp(20, 0, a1))
            rounded(d, (70, y, 500, y + 280), 28, mix(BG, CARD, a1))
            d.text((285, y + 70), "列表", font=sub_f, fill=mix(CARD, MUTED, a1), anchor="mm")
            d.text((285, y + 150), "0 / 1 / 2", font=card_f, fill=mix(CARD, WHITE, a1), anchor="mm")
            d.text((285, y + 220), "第几个", font=sub_f, fill=mix(CARD, YELLOW, a1), anchor="mm")
            rounded(d, (580, y, 1010, y + 280), 28, mix(BG, (22, 40, 36), a1))
            d.text((795, y + 70), "字典", font=sub_f, fill=mix(CARD, MINT, a1), anchor="mm")
            d.text((795, y + 150), "张三 → 92", font=card_f, fill=mix(CARD, WHITE, a1), anchor="mm")
            d.text((795, y + 220), "靠名字", font=sub_f, fill=mix(CARD, YELLOW, a1), anchor="mm")
        punch_bar(d, t, 1.15, "拿出来的是值", (42, 28, 18), YELLOW)
        out.append(img)
    return out


def render_b_loop(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    plates = kenburns_still(ROOT / "assets/plates/t06b-key-not-index.png", n, 1.02, 1.10)
    title_f, card_f, sub_f, code_f = font(54), font(38), font(28), font(34)
    rows = [
        (0.35, "张三", "92", True),
        (0.70, "李四", "88", False),
        (1.05, "王五", "76", False),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = dim_plate(plates[i], 200, 180)
        d = ImageDraw.Draw(img)
        tag_label(d, t, "反查 只能循环")
        a0 = appear(t, 0.02)
        d.text((W // 2, 210 + int(lerp(16, 0, a0))), "从分数找姓名", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        d.text((W // 2, 286), "没有反向下标", font=sub_f, fill=mix(BG, MUTED, appear(t, 0.14)), anchor="mm")

        a1 = appear(t, 0.22)
        if a1 > 0.04:
            rounded(d, (90, 340, 990, 470), 22, mix(BG, (18, 22, 28), a1))
            d.text((W // 2, 405), "for k, v in scores.items()", font=code_f, fill=mix(CARD, MINT, a1), anchor="mm")

        y0 = 510
        for idx, (ts, name, score, hit) in enumerate(rows):
            a = appear(t, ts, 0.24)
            if a < 0.04:
                continue
            y = y0 + idx * 150 + int(lerp(18, 0, a))
            fill = (28, 46, 40) if hit else CARD
            rounded(d, (120, y, 960, y + 128), 24, mix(BG, fill, a))
            mark = "✓" if hit else "·"
            mark_c = MINT if hit else MUTED
            d.text((180, y + 64), mark, font=card_f, fill=mix(CARD, mark_c, a), anchor="mm")
            d.text((320, y + 64), name, font=card_f, fill=mix(CARD, WHITE, a), anchor="lm")
            d.text((820, y + 64), score, font=card_f, fill=mix(CARD, YELLOW if hit else MUTED, a), anchor="mm")
        punch_bar(d, t, 1.55, "只能循环比", (18, 42, 36), MINT)
        out.append(img)
    return out


def render_b_wrong(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    # Dark studio, one point: students[92] is wrong.
    title_f, card_f, sub_f = font(50), font(48), font(30)
    out = []
    for i in range(n):
        t = i / FPS
        img = Image.new("RGB", (W, H), BG)
        overlay = Image.new("RGB", (W, H), BG)
        od = ImageDraw.Draw(overlay)
        od.ellipse((-200, -240, 700, 520), fill=(42, 18, 18))
        od.ellipse((400, 1200, 1300, 2100), fill=(16, 42, 38))
        overlay = overlay.filter(ImageFilter.GaussianBlur(110))
        img = Image.blend(img, overlay, 0.58)
        d = ImageDraw.Draw(img)
        tag_label(d, t, "错法 分数当序号")
        a0 = appear(t, 0.02)
        d.text((W // 2, 260 + int(lerp(16, 0, a0))), "不能拿分数当序号", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        a1 = appear(t, 0.22)
        if a1 > 0.04:
            y = 520 + int(lerp(22, 0, a1))
            rounded(d, (90, y, 990, y + 360), 32, mix(BG, (42, 22, 22), a1))
            d.text((W // 2, y + 90), "不要这样写", font=sub_f, fill=mix(CARD, RED, a1), anchor="mm")
            d.text((W // 2, y + 190), "students[92]", font=font(64), fill=mix(CARD, WHITE, a1), anchor="mm")
            st = appear(t, 0.70, 0.28)
            if st > 0.04:
                x0, x1 = 180, 900
                cy = y + 190
                d.line([(x0, cy), (int(lerp(x0, x1, st)), cy)], fill=mix(CARD, RED, st), width=12)
            d.text((W // 2, y + 290), "方括号里不是名次", font=sub_f, fill=mix(CARD, MUTED, a1), anchor="mm")

        punch_bar(d, t, 1.05, "分数不是下标", (42, 28, 18), YELLOW)
        out.append(img)
    return out


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
    dest = ROOT / "shots/caption_layer.mov"
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
        for cue in cues:
            if cue["start"] <= t < cue["end"]:
                draw_pill(img, cue["lines"])
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

    audio = ROOT / data["audio"]
    bgm = ROOT / "audio/bgm.wav"
    sfx = ROOT / "audio/sfx.wav"
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

    backup = ROOT / "output" / f"{NAME}.mp4"
    backup.parent.mkdir(exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(final), "-c", "copy", str(backup)])
    (ROOT / "final").mkdir(exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(final), "-c", "copy", str(ROOT / "final" / f"{NAME}.mp4")])

    staged = WORK / "成片" / f"13-{NAME}.mp4"
    staged.parent.mkdir(exist_ok=True)
    shutil.copy2(final, staged)
    return staged


def make_cover(data: dict) -> Path:
    dest = ROOT / f"00_封面_{NAME}.jpg"
    char = Image.open(ROOT / data["cover"]["src"]).convert("RGB")
    scale = max(W / char.width, H / char.height)
    nw, nh = int(char.width * scale), int(char.height * scale)
    char = char.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - W) // 2
    y = int((nh - H) * 0.62)
    canvas = char.crop((x, y, x + W, y + H))
    overlay = Image.new("RGBA", (W, H), (11, 13, 18, 40))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((90, 90, 990, 430), radius=36, fill=(22, 24, 28))
    d.text((W // 2, 168), data["cover"]["title"], font=font(58), fill=WHITE, anchor="mm")
    d.text((W // 2, 258), data["cover"]["sub"], font=font(40), fill=MINT, anchor="mm")
    d.text((W // 2, 348), data["cover"]["line"], font=font(30), fill=MUTED, anchor="mm")
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    shutil.copy2(dest, ROOT / "final/cover.jpg")
    return dest


def write_docs(data: dict, staged: Path, qa: dict) -> None:
    vo = (ROOT / "script/voiceover.txt").read_text(encoding="utf-8").strip()
    sha = hashlib.sha256(vo.encode("utf-8")).hexdigest()
    dur = float(data["duration"])
    (ROOT / "项目说明.md").write_text(
        f"""# 13 字典靠名字，不是第几个

**给用户看：** `{staged.relative_to(WORK)}`  
**工程目录：** `{ROOT}`

## 这是什么

普通竖屏知识短视频（A-roll + B-roll），不是剧情短剧。  
选题：`topics.md` 第 6 条，Python `scores[k]` / 字典靠名字不是第几个。  
成片序号 13，避免和已交付的 `成片/06-先给场景再给方法.mp4` 撞号。

白底小灯 A-roll（搪胶 IP 动作镜）+ 黑底对照卡 B-roll。  
B 卷用了 `broll-assets` 的 t06 柜格短镜与钥匙静帧；中文在组装/绘卡阶段叠，不烧进生图。

钩子：方括号里是键，不是序号。  
收束：字典靠名字。

## 口播

{vo}

## 当前状态

- 视频类型：普通短视频
- 状态：已交付到 `成片/`
- 规格：1080×1920，24 fps，约 {dur:.2f} 秒，H.264 + AAC 44100 stereo
- 配音：工厂口播 Yunyang，44100 Hz 单声道 WAV（不对工厂 WAV 重做 TTS）
- B 卷比对应口播早切约半拍
- 全程只在 `/workspace` 渲染，没有写 C:/ D:/ G:

## 文件位置

- 口播：`script/`
- 配音与时间轴：`audio/`
- A 卷：`assets/V-*.mp4`
- B 卷：`broll/`
- 中间镜头：`shots/`（不进成片夹）
""",
        encoding="utf-8",
    )
    status = {
        "schema_version": 1,
        "project_name": "13_字典靠名字不是第几个",
        "video_type": "普通短视频",
        "topic_index": 6,
        "episode": 13,
        "slug": "06_字典靠名字不是第几个",
        "production_method": "白底小灯 A-roll + t06 柜格/对照卡 B-roll + 工厂口播 + FFmpeg",
        "status": "已交付",
        "current_stage": "核验并交付",
        "script": {"path": "script/voiceover.txt", "sha256": sha},
        "audio": {
            "path": "audio/vo-full.wav",
            "alignment_path": "audio/vo-align.txt",
            "voice_id": "zh-CN-YunyangNeural",
            "sample_rate": 44100,
            "channels": 1,
            "duration_ms": int(dur * 1000),
            "note": VOICE_NOTE,
        },
        "deliverables": {
            "final_video": str(staged),
            "project_final": f"00_最终成片_{NAME}.mp4",
            "cover": f"00_封面_{NAME}.jpg",
        },
        "qa": qa,
        "updated_at": "2026-09-11T11:30:00Z",
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def qa_final(staged: Path, data: dict) -> dict:
    probe = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(staged)],
        text=True,
    )
    info = json.loads(probe)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next(s for s in info["streams"] if s["codec_type"] == "audio")
    vol = subprocess.run(
        ["ffmpeg", "-i", str(staged), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    ).stderr
    mean = maxv = None
    for line in vol.splitlines():
        if "mean_volume:" in line:
            mean = float(line.split("mean_volume:")[1].split("dB")[0].strip())
        if "max_volume:" in line:
            maxv = float(line.split("max_volume:")[1].split("dB")[0].strip())
    null = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(staged), "-f", "null", "-"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    shots = data["shots"]
    closed = abs(float(shots[0]["start"])) < 1e-6 and abs(float(shots[-1]["end"]) - float(data["duration"])) < 0.04
    gap = False
    overlap = False
    for i in range(len(shots) - 1):
        if abs(float(shots[i]["end"]) - float(shots[i + 1]["start"])) > 0.02:
            gap = True
        if float(shots[i]["end"]) - float(shots[i + 1]["start"]) > 0.02:
            overlap = True
    fps_txt = v.get("r_frame_rate") or v.get("avg_frame_rate") or "0/1"
    num, den = fps_txt.split("/")
    fps = float(num) / float(den or 1)
    qa = {
        "project": "13_字典靠名字不是第几个",
        "final": str(staged),
        "sha256": hashlib.sha256(staged.read_bytes()).hexdigest(),
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
            "closed": closed,
            "last_end_equals_audio": closed,
        },
        "decode_error": (null.stderr or "")[-400:],
        "ok": (
            int(v.get("width", 0)) == 1080
            and int(v.get("height", 0)) == 1920
            and abs(fps - 24) < 0.05
            and v.get("codec_name") == "h264"
            and a.get("codec_name") == "aac"
            and int(a.get("sample_rate", 0)) == 44100
            and mean is not None
            and mean < -10
            and not gap
            and not overlap
            and closed
            and null.returncode == 0
        ),
    }
    (ROOT / "交付核验.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return qa


def render_brolls(data: dict) -> None:
    by_id = {s["id"]: s for s in data["shots"]}
    jobs = [
        ("S02", "broll/B-键不是下标.mp4", render_b_key),
        ("S03", "broll/B-循环反查.mp4", render_b_loop),
        ("S04", "broll/B-分数不是序号.mp4", render_b_wrong),
    ]
    for sid, rel, fn in jobs:
        shot = by_id[sid]
        dur = max(2.4, float(shot["end"]) - float(shot["start"]) + 0.12)
        print("render", rel, dur)
        frames_to_mp4(fn(dur), ROOT / rel)


def main() -> None:
    os.chdir(ROOT)
    ensure_assets()
    wav = prepare_voice()
    duration, aligned = align_phrases(wav)
    print("VO", duration)
    for row in aligned:
        print(" ", f"{row[0]:.3f}-{row[1]:.3f}", row[2])
    data = build_timeline(aligned, duration)
    make_bgm(duration)
    render_brolls(data)
    make_cover(data)
    staged = assemble(data)
    qa = qa_final(staged, data)
    write_docs(data, staged, qa)
    print("STAGED", staged, "dur", probe_dur(staged), "ok", qa["ok"])
    if not qa["ok"]:
        raise SystemExit(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
