# -*- coding: utf-8 -*-
"""Episode 25 · 切镜不要白闪.

Drive 项目索引 `15_切镜不要白闪`：普通短视频 / 知识口播。
白底小灯 A-roll + 黑底信息图 B-roll。不是剧情，不走 drama-pipeline。
云端 exclusively：草稿只写 .abroll-cloud/25/，成品中转 成片/25-*.mp4。
禁止 C:\\ D:\\ G:\\ 路径，禁止 Drive 上传。
"""
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

ROOT = Path(__file__).resolve().parent
CLOUD = ROOT.parent
W, H, FPS = 1080, 1920, 24
NAME = "切镜不要白闪"
EP = "25"
STAGED_NAME = f"{EP}-{NAME}.mp4"
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_RG = "/tmp/NotoSansSC-Regular.otf"
FONT_WQY = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
VOICE = "zh-CN-YunyangNeural"
B_LEAD = 0.280

BG = (11, 13, 18)
CARD = (24, 28, 38)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
CREAM = (236, 241, 239)
RED = (255, 118, 118)
INK = (22, 24, 28)

A_SOURCES = {
    "V-挥手.mp4": CLOUD / "06" / "assets" / "V-挥手.mp4",
    "V-摊手.mp4": CLOUD / "06" / "assets" / "V-摊手.mp4",
    "V-指向.mp4": CLOUD / "06" / "assets" / "V-指向.mp4",
    "V-点赞.mp4": CLOUD / "06" / "assets" / "V-点赞.mp4",
    "A-角色-小灯-摊手.jpg": CLOUD / "06" / "assets" / "A-角色-小灯-摊手.jpg",
}
STILL_CLIPS = {
    "V-正对讲.mp4": CLOUD / "03" / "assets" / "A-正对讲.jpg",
    "V-侧对讲.mp4": CLOUD / "03" / "assets" / "A-侧对讲.jpg",
}

RECIPE = [
    {"id": "S01a", "kind": "A", "src": "assets/V-挥手.mp4", "close": True, "n": 1},
    {"id": "S01b", "kind": "A", "src": "assets/V-正对讲.mp4", "n": 1},
    {"id": "S01c", "kind": "A", "src": "assets/V-摊手.mp4", "n": 1},
    {"id": "S02", "kind": "B", "src": "broll/B-白闪反例.mp4", "n": 3},
    {"id": "S03", "kind": "A", "src": "assets/V-指向.mp4", "n": 1},
    {"id": "S04", "kind": "B", "src": "broll/B-色块快门.mp4", "n": 3},
    {"id": "S05", "kind": "A", "src": "assets/V-正对讲.mp4", "n": 1},
    {"id": "S06", "kind": "B", "src": "broll/B-硬切对照.mp4", "n": 2},
    {"id": "S07a", "kind": "A", "src": "assets/V-侧对讲.mp4", "n": 1},
    {"id": "S07b", "kind": "A", "src": "assets/V-点赞.mp4", "n": 1},
]


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


def load_phrases() -> list[str]:
    return [ln.strip() for ln in (ROOT / "script/phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]


def still_to_clip(src: Path, dest: Path, dur: float = 4.2) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    vf = (
        f"scale=1188:2112,crop={W}:{H}:'54+10*t':'70+8*t',"
        f"fps={FPS},setsar=1,format=yuv420p"
    )
    run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(src), "-t", f"{dur:.2f}",
        "-vf", vf, "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18", str(dest),
    ])


def ensure_assets() -> None:
    (ROOT / "assets").mkdir(parents=True, exist_ok=True)
    (ROOT / "broll").mkdir(parents=True, exist_ok=True)
    for name, src in A_SOURCES.items():
        dest = ROOT / "assets" / name
        if src.exists() and not dest.exists():
            shutil.copy2(src, dest)
        if not dest.exists():
            raise FileNotFoundError(src)
    for name, src in STILL_CLIPS.items():
        dest = ROOT / "assets" / name
        if dest.exists() and dest.stat().st_size > 8000:
            continue
        if not src.exists():
            raise FileNotFoundError(src)
        still_to_clip(src, dest, 4.4)
        shutil.copy2(src, ROOT / "assets" / src.name)


async def _edge_tts(text: str, dest: Path) -> None:
    import edge_tts

    comm = edge_tts.Communicate(text, VOICE, rate="+4%")
    await comm.save(str(dest))


def synth_vo() -> Path:
    audio = ROOT / "audio"
    audio.mkdir(parents=True, exist_ok=True)
    dest = audio / "vo-full.wav"
    if dest.exists() and dest.stat().st_size > 20000:
        return dest
    text = (ROOT / "script/voiceover.txt").read_text(encoding="utf-8").strip()
    mp3 = audio / "vo-raw.mp3"
    asyncio.run(_edge_tts(text, mp3))
    run([
        "ffmpeg", "-y", "-i", str(mp3),
        "-ac", "1", "-ar", "44100", "-sample_fmt", "s16", str(dest),
    ])
    return dest


def detect_silences(path: Path) -> list[tuple[float, float]]:
    p = subprocess.run(
        ["ffmpeg", "-i", str(path), "-af", "silencedetect=noise=-32dB:d=0.10", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
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
        if s > t + 0.04:
            islands.append((t, s))
        t = max(t, e)
    if t < dur - 0.04:
        islands.append((t, dur))
    return islands


def merge_islands(islands: list[tuple[float, float]], gap: float = 0.26) -> list[tuple[float, float]]:
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
    assigned: list[tuple[float, float]] = []
    if islands and abs(len(islands) - len(phrases)) <= 3:
        extra = len(islands) - len(phrases)
        comma_idxs = [i for i, p in enumerate(phrases) if "，" in p or "：" in p]
        merge_at = set(comma_idxs[: max(0, extra)])
        j = 0
        ok = True
        for i, _p in enumerate(phrases):
            if i in merge_at and j + 1 < len(islands):
                assigned.append((islands[j][0], islands[j + 1][1]))
                j += 2
            elif j < len(islands):
                assigned.append(islands[j])
                j += 1
            else:
                ok = False
                break
        if not ok or len(assigned) != len(phrases):
            assigned = []
    if len(assigned) != len(phrases):
        weights = [max(1, len(re.sub(r"[，。：\s]", "", p))) for p in phrases]
        total = sum(weights)
        t = 0.0
        assigned = []
        for w in weights:
            span = dur * (w / total)
            assigned.append((t, t + span))
            t += span
    starts = [0.0]
    for s, _e in assigned[1:]:
        starts.append(max(starts[-1] + 0.12, s))
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


def split_cap(text: str) -> list[str]:
    text = text.replace("。", "").replace("：", "").strip()
    if len(text) <= 8:
        return [text]
    for sep in ("，", "、"):
        if sep in text:
            parts = [p for p in text.split(sep) if p]
            if 1 < len(parts) <= 3:
                return parts[:2]
    mid = math.ceil(len(text) / 2)
    return [text[:mid], text[mid:]]


def build_timeline(cues: list[dict], duration: float) -> dict:
    shots = []
    i = 0
    for rec in RECIPE:
        n = rec["n"]
        group = cues[i: i + n]
        i += n
        start = group[0]["start"]
        end = group[-1]["end"]
        line = "".join(c["text"] for c in group)
        shots.append({
            "id": rec["id"],
            "kind": rec["kind"],
            "start": start,
            "end": end,
            "src": rec["src"],
            "line": line,
            **({"close": True} if rec.get("close") else {}),
        })
    if i != len(cues):
        raise RuntimeError(f"recipe phrases {i} != cues {len(cues)}")

    for idx, shot in enumerate(shots):
        if shot["kind"] != "B" or idx == 0:
            continue
        steal = min(B_LEAD, max(0.0, (shots[idx - 1]["end"] - shots[idx - 1]["start"]) - 0.55))
        if steal > 0.04:
            shot["start"] = round(shot["start"] - steal, 3)
            shots[idx - 1]["end"] = shot["start"]

    shots[0]["start"] = 0.0
    shots[-1]["end"] = duration
    for idx in range(len(shots) - 1):
        shots[idx]["end"] = shots[idx + 1]["start"]

    a_caps = []
    eyebrows = []
    a_n = 0
    for shot in shots:
        if shot["kind"] != "A":
            continue
        a_n += 1
        a_caps.append({
            "start": shot["start"],
            "end": shot["end"],
            "lines": split_cap(shot["line"]),
        })
        eyebrows.append({
            "start": shot["start"],
            "end": shot["end"],
            "text": f"A-ROLL / {a_n:02d}",
        })

    shutters = []
    pal = [MINT, CREAM, YELLOW]
    for idx, shot in enumerate(shots[1:], start=1):
        shutters.append({"start": shot["start"], "color": list(pal[(idx - 1) % 3])})

    data = {
        "size": [W, H],
        "fps": FPS,
        "duration": duration,
        "audio": "audio/vo-full.wav",
        "bgm": "audio/bgm.wav",
        "video_type": "普通短视频",
        "shots": shots,
        "a_caps": a_caps,
        "eyebrows": eyebrows,
        "shutters": shutters,
        "cover": f"00_封面_{NAME}.jpg",
    }
    (ROOT / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


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


def flash_wipe(draw: ImageDraw.ImageDraw, t: float, start: float, color, dur: float = 0.20) -> None:
    dt = t - start
    if not (0 <= dt <= dur):
        return
    p = dt / dur
    if p < 0.5:
        wdt = max(10, int(W * p * 2))
        x0 = 0
    else:
        wdt = max(10, int(W * (1 - (p - 0.5) * 2)))
        x0 = W - wdt
    draw.rectangle((x0, 0, x0 + wdt, H), fill=color)


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


def b_flash_bad(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, small = font(72), font(52), font(34)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "01 白闪反例")
        a = appear(t, 0.02)
        d.text((W // 2, 300), "切镜为什么", font=card_f, fill=mix(BG, WHITE, a), anchor="mm")
        d.text((W // 2, 400), "不能白闪", font=title_f, fill=mix(BG, YELLOW, a), anchor="mm")
        if t < duration * 0.42:
            aa = appear(t, 0.45, 0.26)
            rounded(d, (110, 560, 970, 1420), 40, mix(BG, CARD, aa))
            d.text((W // 2, 760), "白闪一下", font=card_f, fill=mix(CARD, WHITE, aa), anchor="mm")
            d.text((W // 2, 920), "眼睛被打醒", font=title_f, fill=mix(CARD, RED, aa), anchor="mm")
            d.text((W // 2, 1140), "不是转场，是打断", font=small, fill=mix(CARD, MUTED, aa), anchor="mm")
            flash_wipe(d, t, 1.05, WHITE)
            flash_wipe(d, t, 2.05, WHITE)
        else:
            aa = appear(t, duration * 0.42, 0.22)
            rounded(d, (110, 560, 970, 1420), 40, mix(BG, CARD, aa))
            d.text((W // 2, 760), "节奏断了", font=title_f, fill=mix(CARD, WHITE, aa), anchor="mm")
            d.text((W // 2, 920), "信息也断了", font=title_f, fill=mix(CARD, RED, aa), anchor="mm")
            d.text((W // 2, 1140), "看两秒就开始累", font=small, fill=mix(CARD, MUTED, aa), anchor="mm")
        out.append(img)
    return out


def b_shutter_how(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, small = font(64), font(48), font(32)
    colors = [("薄荷", MINT), ("奶油", CREAM), ("明黄", YELLOW)]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "02 色块快门")
        a = appear(t, 0.02)
        d.text((W // 2, 280), "两镜之间", font=card_f, fill=mix(BG, WHITE, a), anchor="mm")
        d.text((W // 2, 380), "塞一帧色块", font=title_f, fill=mix(BG, MINT, a), anchor="mm")
        if t < duration * 0.36:
            aa = appear(t, 0.32, 0.24)
            rounded(d, (90, 520, 490, 1320), 36, mix(BG, CREAM, aa))
            rounded(d, (590, 520, 990, 1320), 36, mix(BG, CARD, aa))
            d.text((290, 780), "镜 A", font=card_f, fill=mix(CREAM, INK, aa), anchor="mm")
            d.text((790, 780), "镜 B", font=card_f, fill=mix(CARD, WHITE, aa), anchor="mm")
            d.text((W // 2, 1480), "中间只放色块", font=small, fill=mix(BG, MUTED, aa), anchor="mm")
            flash_wipe(d, t, 1.00, MINT)
        else:
            d.text((W // 2, 500), "选一种颜色扫过去", font=small, fill=mix(BG, MUTED, appear(t, duration * 0.36)), anchor="mm")
            gap, pw, ph = 28, 260, 420
            total = 3 * pw + 2 * gap
            x0 = (W - total) // 2
            for idx, (name, col) in enumerate(colors):
                aa = appear(t, duration * 0.36 + idx * 0.20, 0.18)
                if aa < 0.04:
                    continue
                x = x0 + idx * (pw + gap)
                rounded(d, (x, 620, x + pw, 620 + ph), 32, mix(BG, col, aa))
                d.text((x + pw // 2, 820), name, font=card_f, fill=mix(col, INK, aa), anchor="mm")
            flash_wipe(d, t, duration * 0.36 + 0.85, YELLOW)
            flash_wipe(d, t, duration * 0.36 + 1.65, CREAM)
        out.append(img)
    return out


def b_rule(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, small = font(64), font(48), font(32)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "03 一条铁律")
        if t < duration * 0.40:
            a = appear(t, 0.02)
            d.text((W // 2, 300), "记住", font=small, fill=mix(BG, MUTED, a), anchor="mm")
            left = int(lerp(-30, 80, a))
            right = int(lerp(W + 30, 560, a))
            rounded(d, (left, 420, left + 440, 1280), 36, mix(BG, CARD, a))
            rounded(d, (right, 420, right + 440, 1280), 36, mix(BG, CARD, a))
            d.text((left + 220, 680), "硬切", font=card_f, fill=mix(CARD, MINT, a), anchor="mm")
            d.text((left + 220, 840), "可以", font=title_f, fill=mix(CARD, WHITE, a), anchor="mm")
            d.text((right + 220, 680), "白闪", font=card_f, fill=mix(CARD, RED, a), anchor="mm")
            d.text((right + 220, 840), "不行", font=title_f, fill=mix(CARD, WHITE, a), anchor="mm")
        else:
            a = appear(t, duration * 0.40, 0.22)
            rounded(d, (90, 420, 990, 1360), 40, mix(BG, CARD, a))
            d.text((W // 2, 680), "色块一盖", font=title_f, fill=mix(CARD, MINT, a), anchor="mm")
            d.text((W // 2, 840), "下一条再进来", font=card_f, fill=mix(CARD, WHITE, a), anchor="mm")
            d.text((W // 2, 1040), "颜色就是转场", font=small, fill=mix(CARD, YELLOW, a), anchor="mm")
            d.text((W // 2, 1140), "观众还停在内容里", font=small, fill=mix(CARD, MUTED, a), anchor="mm")
            flash_wipe(d, t, duration * 0.40 + 0.65, MINT)
            flash_wipe(d, t, duration * 0.40 + 1.45, YELLOW)
        out.append(img)
    return out


def render_broll(shots: list[dict]) -> None:
    jobs = {
        "broll/B-白闪反例.mp4": b_flash_bad,
        "broll/B-色块快门.mp4": b_shutter_how,
        "broll/B-硬切对照.mp4": b_rule,
    }
    for shot in shots:
        if shot["kind"] != "B":
            continue
        dest = ROOT / shot["src"]
        fn = jobs[shot["src"]]
        dur = max(2.4, float(shot["end"]) - float(shot["start"]) + 0.15)
        print("broll", dest.name, f"{dur:.2f}s")
        frames_to_mp4(fn(dur), dest)


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
    delays, parts = [], []
    for i, t in enumerate(cuts):
        if t < 0.08:
            continue
        ms = int(t * 1000)
        delays.append(f"aevalsrc=0.012*sin(2*PI*880*t):s=44100:d=0.07,adelay={ms}|{ms}[s{i}]")
        parts.append(f"[s{i}]")
    if not parts:
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={duration:.2f}", str(dest)])
        return dest
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
    fnt = font(56 if len(lines) == 1 and max(len(s) for s in lines) <= 8 else 48)
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
        vf = (
            f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},setsar=1,format=yuv420p"
        )
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

    duration = float(data["duration"])
    make_bgm(duration)
    make_sfx([float(s["start"]) for s in data["shutters"]], duration)

    audio = ROOT / data["audio"]
    bgm = ROOT / "audio" / "bgm.wav"
    sfx = ROOT / "audio" / "sfx.wav"
    final = ROOT / f"00_最终成片_{NAME}.mp4"
    run([
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
    ])

    out = ROOT / "output" / f"{NAME}.mp4"
    out.parent.mkdir(exist_ok=True)
    (ROOT / "final").mkdir(exist_ok=True)
    shutil.copy2(final, out)
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
    overlay = Image.new("RGBA", (W, H), (11, 13, 18, 48))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((70, 80, 1010, 500), radius=36, fill=(22, 24, 28))
    d.text((W // 2, 170), "切镜", font=font(68), fill=WHITE, anchor="mm")
    d.text((W // 2, 260), "不要白闪", font=font(64), fill=YELLOW, anchor="mm")
    d.text((W // 2, 350), "改用色块快门", font=font(36), fill=MINT, anchor="mm")
    d.text((W // 2, 430), "硬切可以，白闪不行", font=font(30), fill=MUTED, anchor="mm")
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    canvas.save(ROOT / "final" / "cover.jpg", quality=92)
    return dest


def write_docs(duration: float, staged: Path, report: dict) -> None:
    vo = (ROOT / "script/voiceover.txt").read_text(encoding="utf-8").strip()
    sha = hashlib.sha256(vo.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (ROOT / "项目说明.md").write_text(
        f"""# 25 · 切镜不要白闪

普通短视频 / 知识口播。**不是**剧情短剧，不走 drama-pipeline。

- **选题**：Drive `项目索引.md` → `15_切镜不要白闪`（整段配音与对齐）
- **跳过**：`25_仙侠云海突进`；已做成片名 `深度工作总被打断`、`三秒留人` 及 `成片/00-`～`19-`
- **工程目录**：`/workspace/.abroll-cloud/25/`
- **工程成片**：`00_最终成片_{NAME}.mp4`
- **中转成片**：`{staged}`
- **草稿只在本 VM**，不写 `C:` / `D:` / `G:`，不传 Drive

钩子：这条只讲一件事——切镜为什么不能白闪。  
主线：白闪打断节奏 → 色块快门（薄荷 / 奶油 / 明黄）→ 硬切可以、白闪不行。  
收束：按这个切，知识视频才不会看两秒就累。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {duration:.2f} 秒。
""",
        encoding="utf-8",
    )
    status = {
        "schema_version": 1,
        "project_name": "25_切镜不要白闪",
        "video_type": "普通短视频",
        "source_index": "15_切镜不要白闪",
        "episode": 25,
        "title": NAME,
        "production_method": "白底小灯 A-roll + 黑底信息图 B-roll + edge-tts Yunyang + FFmpeg",
        "status": "已交付",
        "current_stage": "核验并交付",
        "voice": VOICE,
        "duration": duration,
        "size": [W, H],
        "fps": FPS,
        "script": {"path": "script/voiceover.txt", "sha256": sha},
        "audio": {
            "path": "audio/vo-full.wav",
            "alignment_path": "audio/vo-align.txt",
            "sample_rate": 44100,
            "channels": 1,
            "note": "云端 edge-tts 整段合成，短语轴 silencedetect，正文以原文为准",
        },
        "deliverables": {
            "final_video": f"/workspace/成片/{STAGED_NAME}",
            "project_final": f"00_最终成片_{NAME}.mp4",
            "cover": f"00_封面_{NAME}.jpg",
        },
        "not": "剧情短剧 / drama-pipeline / 仙侠云海突进 / Drive 上传 / C:D:G:",
        "qa": report,
        "updated_at": now,
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify(path: Path) -> dict:
    meta = json.loads(subprocess.check_output(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,codec_name",
            "-show_entries", "format=duration", "-of", "json", str(path),
        ],
        text=True,
    ))
    ameta = json.loads(subprocess.check_output(
        [
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=codec_name,sample_rate,channels",
            "-of", "json", str(path),
        ],
        text=True,
    ))
    v, a = meta["streams"][0], ameta["streams"][0]
    dur = float(meta["format"]["duration"])
    num, den = v["r_frame_rate"].split("/")
    fps = float(num) / float(den)
    dec = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"],
        capture_output=True, text=True,
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
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "qa").mkdir(exist_ok=True)
    (ROOT / "qa/ffprobe.txt").write_text(json.dumps(meta, indent=2) + "\n" + json.dumps(ameta, indent=2), encoding="utf-8")
    (ROOT / "qa/decode.txt").write_text(dec.stderr or "ok\n", encoding="utf-8")
    return report


def extract_qa(path: Path, times: list[float]) -> None:
    qa = ROOT / "qa"
    qa.mkdir(exist_ok=True)
    for i, t in enumerate(times):
        dest = qa / f"f{i:02d}_{t:.2f}s.jpg"
        run(["ffmpeg", "-y", "-ss", f"{max(0, t):.3f}", "-i", str(path), "-frames:v", "1", "-q:v", "3", str(dest)])


def update_index(duration: float) -> None:
    idx = Path("/workspace/成片/INDEX.md")
    text = idx.read_text(encoding="utf-8") if idx.exists() else "# 成片（可直接看）\n\n"
    row = f"| `{STAGED_NAME}` | {duration:.1f}s |"
    if STAGED_NAME in text:
        lines = [row if (STAGED_NAME in ln and ln.startswith("|")) else ln for ln in text.splitlines()]
        idx.write_text("\n".join(lines) + "\n", encoding="utf-8")
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
    vo = synth_vo()
    duration = probe_dur(vo)
    phrases = load_phrases()
    cues = align_phrases(phrases, duration, vo)
    write_align(cues, duration)
    print("VO", f"{duration:.3f}s")
    for c in cues:
        print(f"  {c['start']:.3f}-{c['end']:.3f}  {c['text']}")

    data = build_timeline(cues, duration)
    render_broll(data["shots"])
    make_cover()
    staged = assemble(data)
    report = verify(staged)
    write_docs(duration, staged, report)
    mids = [((s["start"] + s["end"]) / 2) for s in data["shots"]]
    extract_qa(staged, [0.35] + mids + [max(0.05, duration - 0.40)])
    update_index(probe_dur(staged))
    print("STAGED", staged, "dur", probe_dur(staged))
    print("QA", json.dumps(report["checks"], ensure_ascii=False))
    if not all(report["checks"].values()):
        raise SystemExit("QA failed")


if __name__ == "__main__":
    main()
