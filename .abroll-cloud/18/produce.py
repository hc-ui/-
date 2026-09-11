#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Topic 11 / 成片 18: 开源小工具涨星靠外发. Cloud-only A-roll + B-roll."""
from __future__ import annotations

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
NAME = "开源小工具涨星靠外发"
VOICE = "zh-CN-YunyangNeural"
FACTORY_WAV = Path("/workspace/.abroll-cloud/aroll/audio/11_涨星靠外发不靠改说明.wav")
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
INK = (28, 32, 36)
TERM = (16, 20, 28)

LEAD = 0.28  # B-roll 比口播早半拍


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout)[-2500:])


def probe_dur(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
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
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{W}x{H}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "fast",
        "-crf",
        "18",
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


def detect_sentence_cues(wav: Path, phrases: list[str], duration: float) -> list[tuple[float, float, str]]:
    """Map factory VO pauses to locked phrases. Long silences ≈ sentence gaps."""
    proc = subprocess.run(
        [
            "ffmpeg",
            "-i",
            str(wav),
            "-af",
            "silencedetect=noise=-32dB:d=0.12",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
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

    # Merge bursts split only by a short comma pause.
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
        for i in range(len(cues) - 1):
            cues[i] = (cues[i][0], cues[i + 1][0], cues[i][2])
        last_s, _, last_p = cues[-1]
        cues[-1] = (last_s, duration, last_p)
        return cues

    weights = [max(1, len(p.replace("，", "").replace("。", ""))) for p in phrases]
    total = sum(weights)
    t = 0.0
    cues = []
    for phrase, w in zip(phrases, weights):
        span = duration * (w / total)
        cues.append((t, t + span, phrase))
        t += span
    cues[-1] = (cues[-1][0], duration, cues[-1][2])
    return cues


def prepare_voiceover() -> tuple[float, list[tuple[float, float, str]]]:
    audio_dir = ROOT / "audio"
    audio_dir.mkdir(exist_ok=True)
    wav = audio_dir / "vo-full.wav"
    if not wav.exists() or wav.stat().st_size < 1000:
        if not FACTORY_WAV.exists():
            raise FileNotFoundError(FACTORY_WAV)
        shutil.copy2(FACTORY_WAV, wav)
    duration = probe_dur(wav)
    phrases = [ln.strip() for ln in (ROOT / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    cues = detect_sentence_cues(wav, phrases, duration)
    cues[0] = (0.0, cues[0][1], cues[0][2])
    for i in range(1, len(cues)):
        cues[i] = (cues[i - 1][1], cues[i][1], cues[i][2])
    cues[-1] = (cues[-1][0], duration, cues[-1][2])

    align_lines = [f"{s:.3f}\t{e:.3f}\t{p}" for s, e, p in cues]
    (audio_dir / "vo-align.txt").write_text("\n".join(align_lines) + "\n", encoding="utf-8")

    vtt = ["WEBVTT", ""]
    for i, (s, e, p) in enumerate(cues, 1):

        def ts(v: float) -> str:
            ms = int(round(v * 1000))
            return f"{ms // 3600000:02d}:{(ms // 60000) % 60:02d}:{(ms // 1000) % 60:02d}.{ms % 1000:03d}"

        vtt.append(str(i))
        vtt.append(f"{ts(s)} --> {ts(e)}")
        vtt.append(p + "。")
        vtt.append("")
    (audio_dir / "vo.vtt").write_text("\n".join(vtt), encoding="utf-8")
    return duration, cues


def make_bgm(duration: float) -> Path:
    dest = ROOT / "audio" / "bgm.wav"
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=196:sample_rate=44100:duration={duration + 1.2:.2f}",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=247:sample_rate=44100:duration={duration + 1.2:.2f}",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=294:sample_rate=44100:duration={duration + 1.2:.2f}",
            "-filter_complex",
            "[0:a]volume=0.12[a];[1:a]volume=0.08[b];[2:a]volume=0.06[c];"
            "[a][b][c]amix=inputs=3:duration=longest,lowpass=f=520,alimiter=limit=0.35",
            "-ac",
            "2",
            "-ar",
            "44100",
            str(dest),
        ]
    )
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


def strike_text(draw, x: int, y: int, text: str, fnt, t: float, start: float, color=RED) -> None:
    st = appear(t, start, 0.28)
    if st <= 0.04:
        return
    tw, th = text_wh(draw, text, fnt)
    cy = y
    x0, x1 = x - 8, x + tw + 8
    draw.line([(x0, cy), (int(lerp(x0, x1, st)), cy)], fill=mix(CARD, color, st), width=8)


def check_badge(draw, cx: int, cy: int, a: float) -> None:
    if a <= 0.04:
        return
    r = 36
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=mix(CARD, (18, 56, 46), a))
    col = mix(CARD, MINT, a)
    draw.line([(cx - 16, cy + 2), (cx - 4, cy + 16), (cx + 20, cy - 14)], fill=col, width=8)


def term_tokens(draw, x: int, y: int, tokens: list[tuple[str, tuple]], fnt, gap: int = 28) -> None:
    cx = x
    for text, color in tokens:
        draw.text((cx, y), text, font=fnt, fill=color, anchor="lm")
        tw, _ = text_wh(draw, text, fnt)
        cx += tw + gap


def render_b_outreach(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(52)
    card_f = font(44)
    sub_f = font(32)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "对照 涨星")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(18, 0, a0))), "三十秒讲清一个痛点", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        a1 = appear(t, 0.18)
        y = 360 + int(lerp(24, 0, a1))
        rounded(d, (90, y, 990, y + 280), 32, mix(BG, CARD, a1))
        d.text((160, y + 90), "改 README", font=card_f, fill=mix(CARD, YELLOW, a1), anchor="lm")
        d.text((160, y + 180), "星还是零", font=sub_f, fill=mix(CARD, MUTED, a1), anchor="lm")
        star = appear(t, 0.32)
        rounded(d, (760, y + 88, 940, y + 188), 22, mix(CARD, (48, 24, 24), star))
        d.text((850, y + 138), "0星", font=title_f, fill=mix(CARD, RED, star), anchor="mm")
        strike_text(d, 160, y + 90, "改 README", card_f, t, 0.62)

        a2 = appear(t, 0.88)
        y2 = 690 + int(lerp(24, 0, a2))
        rounded(d, (90, y2, 990, y2 + 280), 32, mix(BG, (22, 40, 36), a2))
        d.text((160, y2 + 90), "发到讨论区", font=card_f, fill=mix(CARD, MINT, a2), anchor="lm")
        d.text((160, y2 + 180), "对的人看见", font=sub_f, fill=mix(CARD, WHITE, a2), anchor="lm")
        check_badge(d, 850, y2 + 140, appear(t, 1.08, 0.22))

        punch = appear(t, 1.42, 0.26)
        if punch > 0.04:
            y3 = 1060 + int(lerp(22, 0, punch))
            rounded(d, (140, y3, 940, y3 + 200), 28, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y3 + 100), "不靠改说明", font=title_f, fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_b_tools(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(48)
    card_f = font(40)
    sub_f = font(30)
    mono = font(28, bold=False)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "演示 小工具")
        a0 = appear(t, 0.02)
        d.text((W // 2, 236 + int(lerp(16, 0, a0))), "课表变成日历", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        a1 = appear(t, 0.18)
        y = 310 + int(lerp(22, 0, a1))
        rounded(d, (80, y, 1000, y + 430), 30, mix(BG, TERM, a1))
        d.ellipse((110, y + 28, 142, y + 60), fill=mix(TERM, RED, a1))
        d.ellipse((160, y + 28, 192, y + 60), fill=mix(TERM, YELLOW, a1))
        d.ellipse((210, y + 28, 242, y + 60), fill=mix(TERM, MINT, a1))
        d.text((280, y + 44), "kebiao2ics", font=sub_f, fill=mix(TERM, MUTED, a1), anchor="lm")
        term_tokens(
            d,
            120,
            y + 130,
            [("$", mix(TERM, MUTED, a1)), ("kebiao2ics", mix(TERM, MINT, a1)), ("课表.xls", mix(TERM, WHITE, a1))],
            mono,
        )
        line2 = appear(t, 0.48)
        term_tokens(
            d,
            120,
            y + 190,
            [("wrote", mix(TERM, MUTED, line2)), ("周一·08:00", mix(TERM, WHITE, line2)), ("高等数学.ics", mix(TERM, YELLOW, line2))],
            mono,
        )

        cal = appear(t, 0.70)
        if cal > 0.04:
            rounded(d, (120, y + 250, 960, y + 390), 22, mix(TERM, (28, 44, 40), cal))
            d.text((200, y + 300), "日历弹出", font=sub_f, fill=mix(TERM, MINT, cal), anchor="lm")
            d.text((200, y + 350), "第一节课 · 08:00", font=card_f, fill=mix(TERM, WHITE, cal), anchor="lm")

        a2 = appear(t, 1.15)
        y2 = 780 + int(lerp(22, 0, a2))
        rounded(d, (80, y2, 1000, y2 + 360), 30, mix(BG, TERM, a2))
        d.ellipse((110, y2 + 28, 142, y2 + 60), fill=mix(TERM, RED, a2))
        d.ellipse((160, y2 + 28, 192, y2 + 60), fill=mix(TERM, YELLOW, a2))
        d.ellipse((210, y2 + 28, 242, y2 + 60), fill=mix(TERM, MINT, a2))
        d.text((280, y2 + 44), "whoseport", font=sub_f, fill=mix(TERM, MUTED, a2), anchor="lm")
        term_tokens(
            d,
            120,
            y2 + 130,
            [("$", mix(TERM, MUTED, a2)), ("whoseport", mix(TERM, YELLOW, a2)), ("3000", mix(TERM, WHITE, a2))],
            mono,
        )
        line3 = appear(t, 1.42)
        term_tokens(
            d,
            120,
            y2 + 200,
            [(":3000", mix(TERM, MUTED, line3)), ("node", mix(TERM, WHITE, line3)), ("18420", mix(TERM, YELLOW, line3))],
            mono,
        )
        d.text((120, y2 + 270), "谁占了端口", font=card_f, fill=mix(TERM, MINT, line3), anchor="lm")

        punch = appear(t, min(2.05, max(1.6, duration - 0.9)), 0.26)
        if punch > 0.04:
            y3 = 1220 + int(lerp(20, 0, punch))
            rounded(d, (160, y3, 920, y3 + 170), 26, mix(BG, (42, 32, 16), punch))
            d.text((W // 2, y3 + 85), "三十秒能看懂", font=title_f, fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def split_caption(line: str) -> list[str]:
    line = line.strip("。．. ")
    if "，" in line and len(line) > 8:
        parts = [p for p in line.split("，") if p]
        if 1 < len(parts) <= 2:
            return parts
    return [line]


def build_timeline(cues: list[tuple[float, float, str]], duration: float) -> dict:
    recipe = json.loads((ROOT / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
    by_line = {p: (s, e) for s, e, p in cues}
    # phrases 0..5
    p0, p1, p2, p3, p4, p5 = cues
    b1 = max(p0[1] + 1.2, p3[0] - LEAD)
    b2 = max(b1 + 1.0, p4[0] - LEAD)
    if b1 <= p0[1] + 0.4:
        b1 = p3[0]
    if b2 <= b1 + 0.8:
        b2 = p4[0]

    shots = [
        {
            "id": "S01a",
            "kind": "A",
            "start": 0.0,
            "end": round(p0[1], 3),
            "src": "assets/V-挥手.mp4",
            "line": p0[2],
            "close": True,
        },
        {
            "id": "S01b",
            "kind": "A",
            "start": round(p0[1], 3),
            "end": round(b1, 3),
            "src": "assets/V-摊手.mp4",
            "line": f"{p1[2]} / {p2[2]}",
        },
        {
            "id": "S02",
            "kind": "B",
            "start": round(b1, 3),
            "end": round(b2, 3),
            "src": "broll/B-对照外发.mp4",
            "line": p3[2],
            "broll": "outreach",
        },
        {
            "id": "S03",
            "kind": "B",
            "start": round(b2, 3),
            "end": round(p4[1], 3),
            "src": "broll/B-课表端口.mp4",
            "line": p4[2],
            "broll": "tools",
        },
        {
            "id": "S04",
            "kind": "A",
            "start": round(p4[1], 3),
            "end": round(duration, 3),
            "src": "assets/V-点赞.mp4",
            "line": p5[2],
        },
    ]
    for i, shot in enumerate(shots):
        if shot["end"] <= shot["start"] + 0.12:
            shot["end"] = min(duration, shot["start"] + 0.16)
            if i + 1 < len(shots):
                shots[i + 1]["start"] = shot["end"]
    shots[-1]["end"] = round(duration, 3)

    a_caps = [
        {"start": 0.0, "end": round(p0[1], 3), "lines": ["大家好"]},
        {"start": round(p1[0], 3), "end": round(p1[1], 3), "lines": split_caption(p1[2])},
        {"start": round(p2[0], 3), "end": round(min(p2[1], b1), 3), "lines": split_caption(p2[2])},
        {"start": round(p5[0], 3), "end": round(duration, 3), "lines": split_caption(p5[2])},
    ]
    a_caps = [c for c in a_caps if c["end"] > c["start"] + 0.08]

    shutters = [
        {"start": round(p0[1], 3), "color": list(CREAM)},
        {"start": round(b1, 3), "color": list(MINT)},
        {"start": round(b2, 3), "color": list(CREAM)},
        {"start": round(p4[1], 3), "color": list(YELLOW)},
    ]
    eyebrows = [
        {"start": 0.0, "end": round(p0[1], 3), "text": "A-ROLL / 1a"},
        {"start": round(p0[1], 3), "end": round(b1, 3), "text": "A-ROLL / 1b"},
        {"start": round(p5[0], 3), "end": round(duration, 3), "text": "A-ROLL / 04"},
    ]

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
        "_by_line_unused": list(by_line.keys()),
    }
    data.pop("_by_line_unused", None)
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
    fnt = font(22)
    d.rectangle((76, 88, 120, 92), fill=(*MINT, 230))
    d.text((136, 78), label, font=fnt, fill=(90, 98, 108, 220))


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
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgba",
        "-s",
        f"{W}x{H}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-an",
        "-c:v",
        "qtrle",
        "-pix_fmt",
        "argb",
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
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-t",
            f"{dur:.3f}",
            "-vf",
            vf,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
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
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lst),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(FPS),
            str(concat),
        ]
    )

    caps = render_captions(data)
    burned = shots_dir / "video_subs.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(concat),
            "-i",
            str(caps),
            "-filter_complex",
            "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-an",
            str(burned),
        ]
    )

    audio = ROOT / data["audio"]
    bgm = ROOT / "audio" / "bgm.wav"
    sfx = ROOT / "audio" / "sfx.wav"
    final = ROOT / f"00_最终成片_{NAME}.mp4"
    (ROOT / "final").mkdir(exist_ok=True)

    cuts = [float(s["start"]) for s in data["shutters"]]
    make_sfx(cuts, float(data["duration"]))

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
        "-filter_complex",
        ";".join(filters),
        "-map",
        "0:v",
        "-map",
        "[a]",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "18",
        "-c:a",
        "aac",
        "-ar",
        "44100",
        "-ac",
        "2",
        "-b:a",
        "192k",
        "-shortest",
        "-movflags",
        "+faststart",
        str(final),
    ]
    run(inputs)

    out = ROOT / "output" / f"{NAME}.mp4"
    out.parent.mkdir(exist_ok=True)
    shutil.copy2(final, out)
    shutil.copy2(final, ROOT / "final" / f"{NAME}.mp4")

    staged = Path("/workspace/成片") / f"18-{NAME}.mp4"
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
    d.text((W // 2, 160), "开源小工具", font=font(58), fill=WHITE, anchor="mm")
    d.text((W // 2, 250), "涨星靠外发", font=font(58), fill=YELLOW, anchor="mm")
    d.text((W // 2, 340), cover["sub"], font=font(40), fill=MINT, anchor="mm")
    d.text((W // 2, 410), cover["line"], font=font(30), fill=MUTED, anchor="mm")
    dest = ROOT / f"00_封面_{NAME}.jpg"
    canvas.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    canvas.save(ROOT / "final" / "cover.jpg", quality=92)
    return dest


def write_status(duration: float, staged: Path) -> None:
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    sha = hashlib.sha256(vo.encode("utf-8")).hexdigest()
    status = {
        "schema_version": 1,
        "project_name": "18_开源小工具涨星靠外发",
        "video_type": "普通短视频",
        "slug": "11_涨星靠外发不靠改说明",
        "topic_index": 11,
        "episode": 18,
        "title": NAME,
        "voice": VOICE,
        "duration": round(duration, 3),
        "size": [W, H],
        "fps": FPS,
        "stage": "delivered",
        "status": "已交付",
        "current_stage": "核验并交付",
        "production_method": "白底小灯 A-roll + 黑底信息图 B-roll + 工厂 Yunyang 口播 + FFmpeg",
        "script": {"path": "script/voiceover.txt", "sha256": sha},
        "audio": {
            "path": "audio/vo-full.wav",
            "alignment_path": "audio/vo-align.txt",
            "voice_id": VOICE,
            "sample_rate": 44100,
            "channels": 1,
            "duration_ms": int(duration * 1000),
            "note": "复用工厂口播 aroll/audio/11_涨星靠外发不靠改说明.wav；静音切句对齐",
        },
        "deliverables": {
            "final_video": str(staged),
            "project_final": f"00_最终成片_{NAME}.mp4",
            "cover": f"00_封面_{NAME}.jpg",
        },
        "staged": f"成片/18-{NAME}.mp4",
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    for name in ("V-挥手.mp4", "V-摊手.mp4", "V-点赞.mp4", "A-角色-小灯-摊手.jpg"):
        path = ROOT / "assets" / name
        if not path.exists():
            raise FileNotFoundError(path)

    duration, cues = prepare_voiceover()
    print("VO", duration)
    for row in cues:
        print(f"  {row[0]:6.3f}-{row[1]:6.3f}  {row[2]}")
    make_bgm(duration)
    data = build_timeline(cues, duration)
    print("timeline shots", [(s["id"], s["start"], s["end"]) for s in data["shots"]])

    b1 = max(2.2, float(data["shots"][2]["end"]) - float(data["shots"][2]["start"]))
    b2 = max(2.4, float(data["shots"][3]["end"]) - float(data["shots"][3]["start"]))
    print("render B-对照外发", b1)
    frames_to_mp4(render_b_outreach(b1 + 0.12), ROOT / "broll" / "B-对照外发.mp4")
    print("render B-课表端口", b2)
    frames_to_mp4(render_b_tools(b2 + 0.12), ROOT / "broll" / "B-课表端口.mp4")

    make_cover()
    staged = assemble(data)
    write_status(duration, staged)
    print("STAGED", staged, "dur", probe_dur(staged))


if __name__ == "__main__":
    main()
