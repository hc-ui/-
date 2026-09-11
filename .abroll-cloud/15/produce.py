#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Topic 8 → episode 15. Cloud A-roll + B-roll, not drama.

Uses factory VO and t08 B-roll from .abroll-cloud/broll-assets/.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import struct
import subprocess
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
CLOUD = ROOT.parent
W, H, FPS = 1080, 1920, 24
NAME = "在生医实验室抢测控生态位"
EP = "15"
FACTORY_VO = CLOUD / "aroll" / "audio" / "08_生医实验室抢测控生态位.wav"
BROLL_DIR = CLOUD / "broll-assets"
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
    "V-指向.mp4": CLOUD / "06" / "assets" / "V-指向.mp4",
    "xiaodeng-wave.png": CLOUD / "05" / "assets" / "xiaodeng-wave.png",
}

T08 = {
    "B-温控台.mp4": BROLL_DIR / "t08-tec-bench.mp4",
    "B-显微.mp4": BROLL_DIR / "t08-cells.mp4",
    "B-湿实验对照.mp4": BROLL_DIR / "t08-card-wet-vs-control.mp4",
    "t08a-tec-control-bench.png": BROLL_DIR / "t08a-tec-control-bench.png",
    "t08b-microscope-cells.png": BROLL_DIR / "t08b-microscope-cells.png",
    "t08-card-wet-vs-control.png": BROLL_DIR / "t08-card-wet-vs-control.png",
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


def appear(t: float, start: float, dur: float = 0.32) -> float:
    return ease_out((t - start) / dur)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def mix(c0, c1, a: float):
    a = max(0.0, min(1.0, a))
    return tuple(int(c1[i] * a + c0[i] * (1 - a)) for i in range(3))


def load_phrases() -> list[str]:
    return [ln.strip() for ln in (ROOT / "script/phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]


def ensure_assets() -> None:
    (ROOT / "assets").mkdir(parents=True, exist_ok=True)
    (ROOT / "broll").mkdir(parents=True, exist_ok=True)
    for name, src in A_SOURCES.items():
        dest = ROOT / "assets" / name
        if src.exists() and not dest.exists():
            shutil.copy2(src, dest)
        if not dest.exists():
            raise FileNotFoundError(src)
    for name, src in T08.items():
        dest = ROOT / "broll" / name
        if src.exists() and not dest.exists():
            shutil.copy2(src, dest)
        if name.endswith(".mp4") and not dest.exists():
            raise FileNotFoundError(src)


def copy_factory_vo() -> Path:
    audio = ROOT / "audio"
    audio.mkdir(parents=True, exist_ok=True)
    dest = audio / "vo-full.wav"
    if not FACTORY_VO.exists():
        raise FileNotFoundError(FACTORY_VO)
    run(["ffmpeg", "-y", "-i", str(FACTORY_VO), "-ac", "1", "-ar", "44100", "-sample_fmt", "s16", str(dest)])
    return dest


def detect_silences(path: Path) -> list[tuple[float, float]]:
    p = subprocess.run(
        ["ffmpeg", "-i", str(path), "-af", "silencedetect=noise=-32dB:d=0.12", "-f", "null", "-"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    starts: list[float] = []
    pairs: list[tuple[float, float]] = []
    for line in (p.stderr or "").splitlines():
        if "silence_start:" in line:
            starts.append(float(line.split("silence_start:")[1].split()[0].split("|")[0]))
        elif "silence_end:" in line:
            end = float(line.split("silence_end:")[1].split()[0].split("|")[0])
            st = starts.pop(0) if starts else 0.0
            pairs.append((st, end))
    if starts:
        pairs.append((starts[0], probe_dur(path)))
    return pairs


def speech_islands(dur: float, silences: list[tuple[float, float]]) -> list[tuple[float, float]]:
    islands: list[tuple[float, float]] = []
    t = 0.0
    for s, e in silences:
        if s > t + 0.05:
            islands.append((t, s))
        t = max(t, e)
    if t < dur - 0.05:
        islands.append((t, dur))
    return islands


def merge_islands(islands: list[tuple[float, float]], gap: float = 0.28) -> list[tuple[float, float]]:
    if not islands:
        return []
    out = [islands[0]]
    for a, b in islands[1:]:
        ps, pe = out[-1]
        if a - pe <= gap:
            out[-1] = (ps, b)
        else:
            out.append((a, b))
    return out


def align_phrases(phrases: list[str], dur: float, vo: Path) -> list[dict]:
    islands = merge_islands(speech_islands(dur, detect_silences(vo)))
    if not islands:
        step = dur / len(phrases)
        return [{"text": p, "start": i * step, "end": (i + 1) * step} for i, p in enumerate(phrases)]

    assigned: list[tuple[float, float]] = []
    extra = len(islands) - len(phrases)
    comma_idxs = [i for i, p in enumerate(phrases) if "，" in p]
    merge_at = set(comma_idxs[: max(0, extra)])
    if extra >= 0 and extra <= len(phrases):
        j = 0
        for i, _p in enumerate(phrases):
            if i in merge_at and j + 1 < len(islands):
                assigned.append((islands[j][0], islands[j + 1][1]))
                j += 2
            else:
                assigned.append(islands[j])
                j += 1
            if j >= len(islands) and i + 1 < len(phrases):
                assigned = []
                break
    if len(assigned) != len(phrases):
        weights = [max(1, len(re.sub(r"[，。\s]", "", p))) for p in phrases]
        total = sum(weights)
        t = 0.0
        assigned = []
        for p, w in zip(phrases, weights):
            span = dur * (w / total)
            assigned.append((t, t + span))
            t += span

    starts = [0.0]
    for s, _e in assigned[1:]:
        starts.append(s)
    cues = []
    for i, p in enumerate(phrases):
        start = starts[i]
        end = starts[i + 1] if i + 1 < len(starts) else dur
        cues.append({"text": p, "start": start, "end": end})
    cues[0]["start"] = 0.0
    cues[-1]["end"] = dur
    for i in range(len(cues) - 1):
        cues[i]["end"] = cues[i + 1]["start"]
    return cues


def write_align(cues: list[dict], dur: float) -> None:
    lines = [f"{c['start']:.3f}\t{c['end']:.3f}\t{c['text']}" for c in cues]
    (ROOT / "audio/vo-align.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "audio/cues.json").write_text(json.dumps(cues, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "audio/align.json").write_text(
        json.dumps({"duration": dur, "cues": cues}, ensure_ascii=False, indent=2), encoding="utf-8"
    )


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
    n = int(sr * (dur + 1.4))
    samples = []
    for i in range(n):
        t = i / sr
        env = min(1.0, t / 0.7) * min(1.0, (n / sr - t) / 0.55)
        s = (
            0.07 * math.sin(2 * math.pi * 174.61 * t)
            + 0.05 * math.sin(2 * math.pi * 220.0 * t)
            + 0.035 * math.sin(2 * math.pi * 261.63 * t)
            + 0.02 * math.sin(2 * math.pi * 329.63 * t)
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
        length = int(0.045 * sr)
        for i in range(length):
            if start + i >= n:
                break
            t = i / sr
            env = math.exp(-t * 70) * (1 - i / length)
            samples[start + i] += env * 0.20 * math.sin(2 * math.pi * (420 + 880 * (i / length)) * t)
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


def rounded(draw: ImageDraw.ImageDraw, xy, r: int, fill) -> None:
    draw.rounded_rectangle(xy, radius=r, fill=fill)


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


def render_flow_card(duration: float) -> Path:
    n = max(1, round(duration * FPS))
    title_f = font(64)
    card_f = font(48)
    sub_f = font(34)
    tag_f = font(32)
    out = []
    nodes = [
        (0.18, "泵", "微量泵", "给流量", MINT),
        (0.55, "阀", "气压阀", "给压力", YELLOW),
        (0.92, "感", "传感器", "回闭环", MINT),
    ]
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        a0 = appear(t, 0.0, 0.22)
        rounded(d, (72, 86, 340, 150), 22, mix(BG, (20, 42, 38), a0))
        d.text((90, 100), "02 微流控", font=tag_f, fill=mix(BG, MINT, a0))
        d.text((W // 2, 250 + int(lerp(18, 0, a0))), "恒流 / 恒压", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        d.text((W // 2, 330), "闭环，不是开环加液", font=sub_f, fill=mix(BG, MUTED, appear(t, 0.12)), anchor="mm")

        y0 = 430
        for idx, (ts, num, head, body, color) in enumerate(nodes):
            a = appear(t, ts, 0.28)
            if a < 0.04:
                continue
            y = y0 + idx * 230 + int(lerp(22, 0, a))
            rounded(d, (90, y, 990, y + 200), 32, mix(BG, CARD, a))
            d.ellipse((130, y + 56, 230, y + 156), fill=mix(CARD, color, a))
            d.text((180, y + 106), num, font=card_f, fill=mix(color, INK, a), anchor="mm")
            d.text((270, y + 70), head, font=title_f, fill=mix(CARD, color, a), anchor="lm")
            d.text((270, y + 140), body, font=card_f, fill=mix(CARD, WHITE, a), anchor="lm")
            if idx < 2 and appear(t, ts + 0.28, 0.2) > 0.5:
                d.polygon([(540, y + 210), (560, y + 234), (520, y + 234)], fill=mix(BG, MUTED, a))

        punch = appear(t, 1.05, 0.24)
        if punch > 0.04:
            y = 1540 + int(lerp(20, 0, punch))
            rounded(d, (120, y, 960, y + 200), 28, mix(BG, (18, 42, 36), punch))
            d.text((W // 2, y + 100), "开环加液不算生态位", font=card_f, fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    dest = ROOT / "broll" / "B-微流控.mp4"
    frames_to_mp4(out, dest)
    return dest


def build_timeline(cues: list[dict], duration: float) -> dict:
    recipe = json.loads((ROOT / "plan/shot_recipe.json").read_text(encoding="utf-8"))
    pmap = {c["text"]: c for c in cues}
    shots = []
    for spec in recipe["shots"]:
        ps = spec["phrases"]
        start = pmap[ps[0]]["start"]
        end = pmap[ps[-1]]["end"]
        shots.append(
            {
                "id": spec["id"],
                "kind": spec["kind"],
                "src": spec["src"],
                "close": bool(spec.get("close")),
                "line": ps[-1] if len(ps) == 1 else "".join(ps),
                "phrases": ps,
                "start": start,
                "end": end,
            }
        )
    for i in range(1, len(shots)):
        if shots[i]["kind"] != "B":
            continue
        prev_len = shots[i - 1]["end"] - shots[i - 1]["start"]
        pull = min(0.24, max(0.0, prev_len - 0.70))
        shots[i]["start"] -= pull
        shots[i - 1]["end"] -= pull
    shots[0]["start"] = 0.0
    for i in range(1, len(shots)):
        shots[i]["start"] = shots[i - 1]["end"]
    shots[-1]["end"] = duration

    p0, p1, p2, p3, p4, p5 = cues
    data = {
        "audio": "audio/vo-full.wav",
        "duration": duration,
        "fps": FPS,
        "size": [W, H],
        "title": NAME,
        "video_type": "普通短视频",
        "bgm": "audio/bgm.wav",
        "shots": shots,
        "a_caps": [
            {"start": p0["start"], "end": p0["end"], "lines": ["大家好"]},
            {
                "start": p1["start"],
                "end": p1["start"] + (p1["end"] - p1["start"]) * 0.48,
                "lines": ["交叉组缺的是闭环"],
            },
            {
                "start": p1["start"] + (p1["end"] - p1["start"]) * 0.48,
                "end": p1["end"],
                "lines": ["不是再多一个养细胞的人"],
            },
            {
                "start": p5["start"],
                "end": p5["start"] + (p5["end"] - p5["start"]) * 0.55,
                "lines": ["包装成测控底层"],
            },
            {
                "start": p5["start"] + (p5["end"] - p5["start"]) * 0.55,
                "end": duration,
                "lines": ["才贴答辩"],
            },
        ],
        "b_caps": [
            {"start": p2["start"], "end": p2["end"], "tag": "01 温控", "title": "自适应温控"},
            {"start": p4["start"], "end": p4["end"], "tag": "03 视觉", "title": "冻存细胞检测"},
        ],
        "shutters": [
            {"start": shots[1]["start"], "color": list(CREAM)},
            {"start": shots[2]["start"], "color": list(MINT)},
            {"start": shots[3]["start"], "color": list(YELLOW)},
            {"start": shots[4]["start"], "color": list(MINT)},
            {"start": shots[5]["start"], "color": list(YELLOW)},
        ],
        "eyebrows": [
            {"start": 0.0, "end": shots[2]["start"], "text": "A-ROLL / 15"},
            {"start": shots[5]["start"], "end": duration, "text": "A-ROLL / 收束"},
        ],
        "cover": {
            "title": "在生医实验室抢测控生态位",
            "sub": "缺的是闭环，不是养细胞",
            "line": "包装成测控底层",
            "src": "broll/t08a-tec-control-bench.png",
        },
    }
    (ROOT / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def draw_eyebrow(base: Image.Image, t: float, eyebrows) -> None:
    label = None
    for e in eyebrows:
        if e["start"] <= t < e["end"]:
            label = e["text"]
            break
    if not label:
        return
    d = ImageDraw.Draw(base)
    d.rectangle((76, 88, 120, 92), fill=(*MINT, 230))
    d.text((136, 78), label, font=font(22), fill=(90, 98, 108, 220))


def draw_pill(base: Image.Image, lines: list[str], y: int = 168) -> None:
    fnt = font(52 if len(lines) == 1 else 46)
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


def draw_b_label(base: Image.Image, tag: str, title: str) -> None:
    d = ImageDraw.Draw(base)
    tf, sf = font(30), font(48)
    tw = d.textbbox((0, 0), tag, font=tf)
    pill_w = tw[2] - tw[0] + 48
    y = H - 360
    rounded(d, (72, y, 72 + pill_w, y + 64), 20, (*MINT, 230))
    d.text((72 + pill_w / 2, y + 32), tag, font=tf, fill=(*INK, 255), anchor="mm")
    shade = Image.new("RGBA", (W, 220), (8, 10, 14, 0))
    sd = ImageDraw.Draw(shade)
    for i in range(220):
        sd.line([(0, i), (W, i)], fill=(8, 10, 14, int(170 * (i / 220))))
    base.alpha_composite(shade, (0, H - 220))
    ImageDraw.Draw(base).text((72, H - 150), title, font=sf, fill=(*WHITE, 255), anchor="lm")


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
        kind = "A"
        for shot in data["shots"]:
            if shot["start"] <= t < shot["end"] or (
                shot is data["shots"][-1] and abs(t - shot["end"]) < 1e-6
            ):
                kind = shot["kind"]
                break
        if kind == "A":
            for cap in data["a_caps"]:
                if cap["start"] <= t < cap["end"]:
                    draw_pill(img, cap["lines"])
                    break
        else:
            for cap in data.get("b_caps", []):
                if cap["start"] <= t < cap["end"]:
                    draw_b_label(img, cap["tag"], cap["title"])
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
            "[2:a]adelay=800|800,volume=0.16,highpass=f=140[bg];"
            "[3:a]volume=0.28[sfx];"
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
    src = ROOT / "broll" / "t08a-tec-control-bench.png"
    img = Image.open(src).convert("RGB")
    img = img.resize((W, H), Image.Resampling.LANCZOS)
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for y in range(H):
        a = 70 if y < 700 else int(70 + 140 * ((y - 700) / 1220))
        sd.line([(0, y), (W, y)], fill=(8, 10, 14, min(210, a)))
    canvas = Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")
    d = ImageDraw.Draw(canvas)
    rounded(d, (70, 160, 1010, 620), 36, (22, 24, 28))
    d.text((W // 2, 250), "在生医实验室", font=font(58), fill=WHITE, anchor="mm")
    d.text((W // 2, 340), "抢测控生态位", font=font(64), fill=YELLOW, anchor="mm")
    d.text((W // 2, 440), "缺的是闭环，不是养细胞", font=font(36), fill=MINT, anchor="mm")
    d.text((W // 2, 530), "包装成测控底层", font=font(32), fill=MUTED, anchor="mm")
    dest = ROOT / f"00_封面_{NAME}.jpg"
    canvas.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    shutil.copy2(dest, ROOT / "final" / "cover.jpg")
    return dest


def write_docs(duration: float, staged: Path, report: dict) -> None:
    vo = (ROOT / "script/voiceover.txt").read_text(encoding="utf-8").strip()
    sha = hashlib.sha256(vo.encode("utf-8")).hexdigest()
    (ROOT / "项目说明.md").write_text(
        f"""# 15 · 在生医实验室抢测控生态位

普通短视频 / 知识口播。不是剧情短剧。

- **选题**：`topics.md` 第 8 条
- **来源**：中科大赵刚课题组备忘录第四节；学习与职业规划基线（细胞温控 / PID·MPC）
- **工程目录**：`/workspace/.abroll-cloud/15/`
- **工程成片**：`00_最终成片_{NAME}.mp4`
- **中转成片**：`{staged}`

## 这是什么

竖屏 A/B 卷。白底小灯说判断，黑底图讲三个测控包装：自适应温控、微流控恒流恒压、冻存细胞显微检测。收束：包装成测控底层，才贴答辩。

钩子：交叉组缺的是闭环，不是再多一个养细胞的人。

## 当前状态

- 视频类型：普通短视频
- 状态：已交付到 `成片/`
- 规格：1080×1920，{duration:.2f} 秒，24 fps，H.264 + AAC 44100 Hz

## 素材

- 口播：工厂 WAV `aroll/audio/08_生医实验室抢测控生态位.wav`（未重合成）
- A 卷：`06/assets/V-挥手|摊手|指向.mp4`
- B 卷：t08 测控台 / 显微短镜；微流控对照卡代码绘制
- t08 湿实验对照卡只作封面备份，不成片目录墙

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
        "project_name": "15_在生医实验室抢测控生态位",
        "video_type": "普通短视频",
        "topic_index": 8,
        "episode": 15,
        "production_method": "工厂口播 + 白底小灯 A-roll + t08 B-roll + 代码微流控卡 + FFmpeg",
        "status": "已交付",
        "current_stage": "核验并交付",
        "script": {"path": "script/voiceover.txt", "sha256": sha},
        "audio": {
            "path": "audio/vo-full.wav",
            "alignment_path": "audio/vo-align.txt",
            "voice_id": "factory-08 Yunyang",
            "sample_rate": 44100,
            "channels": 1,
            "duration_ms": int(duration * 1000),
            "note": "沿用 aroll/audio/08_生医实验室抢测控生态位.wav，按 silencedetect 闭合成短语轴",
        },
        "deliverables": {
            "final_video": f"00_最终成片_{NAME}.mp4",
            "staged": str(staged),
            "cover": f"00_封面_{NAME}.jpg",
        },
        "qa": report,
        "updated_at": "2026-09-11T11:30:00Z",
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
        },
    }
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def extract_qa(path: Path, times: list[float]) -> None:
    qa = ROOT / "qa"
    qa.mkdir(exist_ok=True)
    for i, t in enumerate(times):
        dest = qa / f"f{i:02d}_{t:.2f}s.jpg"
        run(["ffmpeg", "-y", "-ss", f"{max(0, t):.3f}", "-i", str(path), "-frames:v", "1", str(dest)])


def update_index(duration: float) -> None:
    idx = Path("/workspace/成片/INDEX.md")
    if not idx.exists():
        return
    text = idx.read_text(encoding="utf-8")
    row = f"| `{EP}-{NAME}.mp4` | {duration:.1f}s |"
    if f"{EP}-{NAME}.mp4" in text:
        return
    lines = text.rstrip().splitlines()
    insert_at = len(lines)
    for i, ln in enumerate(lines):
        if ln.startswith("| `仙侠"):
            insert_at = i
            break
    lines.insert(insert_at, row)
    idx.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_assets()
    vo = copy_factory_vo()
    duration = probe_dur(vo)
    phrases = load_phrases()
    cues = align_phrases(phrases, duration, vo)
    write_align(cues, duration)
    print("VO", f"{duration:.3f}s")
    for c in cues:
        print(f"  {c['start']:.3f}-{c['end']:.3f}  {c['text']}")

    data = build_timeline(cues, duration)
    flow_dur = max(2.4, float(data["shots"][3]["end"]) - float(data["shots"][3]["start"]) + 0.2)
    render_flow_card(flow_dur)
    make_cover()
    staged = assemble(data)
    report = verify(staged)
    write_docs(duration, staged, report)
    mids = [((s["start"] + s["end"]) / 2) for s in data["shots"]]
    extract_qa(staged, [0.35] + mids + [max(0.05, duration - 0.35)])
    update_index(probe_dur(staged))
    print("QA", json.dumps(report["checks"], ensure_ascii=False))


if __name__ == "__main__":
    main()
