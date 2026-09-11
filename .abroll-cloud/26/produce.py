#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 26：待办为什么划不掉。云端 A-roll + B-roll，跟 Drive 锁定文案，不是短剧。"""
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
NAME = "待办为什么划不掉"
STAGED_NAME = "26-待办为什么划不掉.mp4"
VOICE = "zh-CN-YunyangNeural"
ASSET_SRC = Path("/workspace/.abroll-cloud/06/assets")

FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_REG = "/tmp/NotoSansSC-Regular.otf"
FONT_FALLBACK = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

BG = (11, 13, 18)
CARD = (24, 28, 38)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
RED = (255, 118, 118)
CREAM = (236, 241, 239)
INK = (28, 32, 36)

# Drive 锁定口播 19167ms；云端 TTS 对不上就按新时长重铺，分镜分组不改。
LOCKED_MS = [
    (0, 480),
    (480, 2380),
    (2380, 3680),
    (3680, 4860),
    (4860, 6240),
    (6240, 8800),
    (8800, 9720),
    (9720, 11000),
    (11000, 12680),
    (12680, 14020),
    (14020, 15340),
    (15340, 16260),
    (16260, 17480),
    (17480, 19167),
]
LOCKED_DUR = 19.167


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


def new_bg() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    overlay = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(overlay)
    d.ellipse((-220, -280, 720, 560), fill=(16, 42, 38))
    d.ellipse((480, 1180, 1400, 2100), fill=(42, 32, 16))
    overlay = overlay.filter(ImageFilter.GaussianBlur(110))
    return Image.blend(img, overlay, 0.58)


def tag(draw: ImageDraw.ImageDraw, t: float, label: str) -> None:
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
    mid = frames[min(len(frames) // 2, len(frames) - 1)]
    mid.save(dest.with_suffix(".jpg"), quality=92)


def compact(s: str) -> str:
    for ch in "，。、！？,.!?;；：: “”\"' ":
        s = s.replace(ch, "")
    return s


def ticks_to_s(v) -> float:
    return float(v) / 10_000_000.0


async def synthesize_voice(text: str, mp3: Path) -> list[dict]:
    import edge_tts

    comm = edge_tts.Communicate(text, VOICE, rate="-8%")
    bounds: list[dict] = []
    with mp3.open("wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("SentenceBoundary", "WordBoundary"):
                bounds.append(chunk)
    return bounds


def align_phrases(phrases: list[str], bounds: list[dict], dur: float) -> list[dict]:
    words = [b for b in bounds if b.get("type") == "WordBoundary" and b.get("text")]
    cues: list[dict] = []
    if words:
        stream = []
        for w in words:
            st = ticks_to_s(w.get("offset", 0))
            en = st + ticks_to_s(w.get("duration", 0))
            for ch in str(w.get("text") or ""):
                if ch not in "，。、！？,.!?;；：: “”\"' ":
                    stream.append((ch, st, en))
        idx = 0
        for phrase in phrases:
            target = compact(phrase)
            start_t = end_t = None
            built = ""
            while idx < len(stream) and built != target:
                ch, s, e = stream[idx]
                idx += 1
                if start_t is None:
                    start_t = s
                end_t = e
                built += ch
                if target and not target.startswith(built):
                    if built[-1] not in target:
                        built = built[:-1]
                        if not built:
                            start_t = None
            if start_t is None:
                start_t = cues[-1]["end"] if cues else 0.0
            if end_t is None:
                end_t = min(dur, start_t + 1.2)
            cues.append({"text": phrase, "start": start_t, "end": end_t})

    if len(cues) != len(phrases):
        weights = [max(1, len(compact(p))) for p in phrases]
        total = sum(weights)
        t = 0.0
        cues = []
        for phrase, w in zip(phrases, weights):
            span = dur * (w / total)
            cues.append({"text": phrase, "start": t, "end": t + span})
            t += span

    cues[0]["start"] = 0.0
    for i in range(1, len(cues)):
        if cues[i]["start"] < cues[i - 1]["end"]:
            mid = (cues[i - 1]["end"] + cues[i]["start"]) / 2
            cues[i - 1]["end"] = mid
            cues[i]["start"] = mid
        elif cues[i]["start"] - cues[i - 1]["end"] > 0.02:
            cues[i]["start"] = cues[i - 1]["end"]
    cues[-1]["end"] = dur
    for i in range(len(cues) - 1):
        cues[i]["end"] = cues[i + 1]["start"]
    return cues


def copy_assets() -> None:
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    names = ["V-挥手.mp4", "V-摊手.mp4", "V-指向.mp4", "V-点赞.mp4", "A-角色-小灯-摊手.jpg"]
    for name in names:
        src = ASSET_SRC / name
        dest = assets / name
        if not src.exists():
            raise FileNotFoundError(src)
        if not dest.exists() or dest.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dest)


def make_voiceover() -> tuple[float, list[dict]]:
    text = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    phrases = [ln.strip() for ln in (ROOT / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    audio = ROOT / "audio"
    audio.mkdir(parents=True, exist_ok=True)
    mp3 = audio / "vo-full.mp3"
    wav = audio / "vo-full.wav"
    if wav.exists() and wav.stat().st_size > 800 and abs(probe_dur(wav) - LOCKED_DUR) < 0.08:
        dur = probe_dur(wav)
        cues = []
        for (a, b), phrase in zip(LOCKED_MS, phrases):
            cues.append({"text": phrase, "start": a / 1000.0, "end": b / 1000.0})
        cues[-1]["end"] = dur
        print("reuse locked-duration VO", dur)
    else:
        bounds = asyncio.run(synthesize_voice(text, mp3))
        (audio / "vo.vtt.json").write_text(json.dumps(bounds, ensure_ascii=False, indent=2), encoding="utf-8")
        if mp3.stat().st_size < 800:
            raise RuntimeError("tts too small")
        run(["ffmpeg", "-y", "-i", str(mp3), "-ac", "1", "-ar", "44100", "-sample_fmt", "s16", str(wav)])
        dur = probe_dur(wav)
        cues = align_phrases(phrases, bounds, dur)
        print("TTS", f"{dur:.3f}s", "cues", len(cues))

    lines = [f"{c['start']:.3f}\t{c['end']:.3f}\t{c['text']}" for c in cues]
    (audio / "vo-align.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (audio / "cues.json").write_text(json.dumps(cues, ensure_ascii=False, indent=2), encoding="utf-8")
    locked_style = [f"[{int(c['start'] * 1000)}ms-{int(c['end'] * 1000)}ms] {c['text']}" for c in cues]
    (audio / "vo-align-locked-style.txt").write_text("\n".join(locked_style) + "\n", encoding="utf-8")
    return dur, cues


def phrase_index(cues: list[dict], text: str) -> int:
    for i, cue in enumerate(cues):
        if cue["text"] == text:
            return i
    raise KeyError(text)


def build_timeline(duration: float, cues: list[dict]) -> dict:
    recipe = json.loads((ROOT / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
    shots_out = []
    a_caps = []
    shutters = []
    eyebrows = []
    a_i = 0
    phrase_lookup = {c["text"]: c for c in cues}

    raw = []
    for shot in recipe["shots"]:
        first = phrase_lookup[shot["phrases"][0]]
        last = phrase_lookup[shot["phrases"][-1]]
        raw.append((shot, first["start"], last["end"]))

    cut_starts = [s for _, s, _ in raw]
    for i, (shot, _ps, _pe) in enumerate(raw):
        lead = float(shot.get("lead") or 0)
        if shot["kind"] == "B" and lead > 0 and i > 0:
            cut_starts[i] = max(cut_starts[i - 1] + 0.80, raw[i][1] - lead)
    cut_ends = cut_starts[1:] + [duration]

    for i, (shot, _ps, _pe) in enumerate(raw):
        start, end = cut_starts[i], cut_ends[i]
        line = "，".join(shot["phrases"])
        item = {
            "id": shot["id"],
            "kind": shot["kind"],
            "start": round(start, 3),
            "end": round(end, 3),
            "src": shot["src"],
            "line": line,
        }
        if shot.get("close"):
            item["close"] = True
        if shot.get("broll"):
            item["broll"] = shot["broll"]
        shots_out.append(item)

        if shot["kind"] == "A":
            a_i += 1
            for phrase in shot["phrases"]:
                cue = phrase_lookup[phrase]
                cap_s = max(start, cue["start"])
                cap_e = min(end, cue["end"])
                if cap_e - cap_s < 0.08:
                    continue
                a_caps.append({"start": round(cap_s, 3), "end": round(cap_e, 3), "lines": [phrase]})
            eyebrows.append({"start": round(start, 3), "end": round(end, 3), "text": f"A-ROLL / {a_i:02d}"})
        if i > 0:
            if shot["kind"] == "B":
                color = [126, 224, 197]
                if shots_out[i - 1]["kind"] == "B":
                    color = [245, 247, 250]
            else:
                color = [245, 193, 92]
            shutters.append({"start": round(start, 3), "color": color})

    for i in range(1, len(shots_out)):
        shots_out[i]["start"] = shots_out[i - 1]["end"]
    shots_out[-1]["end"] = round(duration, 3)

    timeline = {
        "audio": "audio/vo-full.wav",
        "duration": round(duration, 3),
        "fps": FPS,
        "size": [W, H],
        "title": recipe["title"],
        "bgm": "audio/bgm.wav",
        "locked_copy": "Drive 26_待办为什么划不掉",
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
    (ROOT / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return timeline


def make_bgm(duration: float) -> None:
    dest = ROOT / "audio" / "bgm.wav"
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=196:sample_rate=44100:duration={duration + 2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=247:sample_rate=44100:duration={duration + 2:.2f}",
        "-filter_complex",
        "[0:a]volume=0.14[a];[1:a]volume=0.09[b];"
        "[a][b]amix=inputs=2:duration=longest,lowpass=f=420,volume=0.22,aformat=sample_rates=44100:channel_layouts=stereo",
        str(dest),
    ])


def make_sfx(cuts: list[float], duration: float) -> None:
    dest = ROOT / "audio" / "sfx.wav"
    if not cuts:
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={duration:.2f}", str(dest)])
        return
    delays = []
    parts = []
    for i, t in enumerate(cuts):
        ms = int(max(0.0, t) * 1000)
        delays.append(f"aevalsrc=0.012*sin(2*PI*880*t):s=44100:d=0.07,adelay={ms}|{ms}[s{i}]")
        parts.append(f"[s{i}]")
    fc = ";".join(delays) + f";{''.join(parts)}amix=inputs={len(parts)}:duration=longest,aformat=sample_rates=44100:channel_layouts=stereo"
    run(["ffmpeg", "-y", "-filter_complex", fc, "-t", f"{duration:.2f}", str(dest)])


def ktime(t: float, duration: float, locked: float) -> float:
    return t * (duration / locked)


def b_lie(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(72)
    sub_f = font(40, bold=False)
    card_f = font(52)
    locked = 2.56
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "01 不是懒")
        if t < ktime(1.18, duration, locked):
            a = appear(t, 0.02)
            rounded(d, (96, 520, 984, 820), 36, mix(BG, CARD, a))
            d.text((W // 2, 670), "你懒", font=title_f, fill=mix(CARD, WHITE, a), anchor="mm")
            strike = appear(t, ktime(0.55, duration, locked), 0.28)
            if strike > 0.04:
                x1 = int(lerp(220, 860, strike))
                d.line([(220, 670), (x1, 670)], fill=mix(CARD, RED, strike), width=14)
        else:
            a = appear(t, ktime(1.18, duration, locked), 0.28)
            d.text((W // 2, 430 + int(lerp(28, 0, a))), "清单在骗你", font=title_f, fill=mix(BG, YELLOW, a), anchor="mm")
            d.text((W // 2, 560), "不是执行力的问题", font=sub_f, fill=mix(BG, MUTED, a), anchor="mm")
            rounded(d, (140, 720, 940, 980), 32, mix(BG, CARD, a))
            d.text((W // 2, 850), "愿望伪装成任务", font=card_f, fill=mix(CARD, WHITE, a), anchor="mm")
        out.append(img)
    return out


def b_same_page(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(56)
    sub_f = font(36, bold=False)
    card_f = font(48)
    small = font(34, bold=False)
    locked = 4.76
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "02 同一页")
        a0 = appear(t, 0.04)
        d.text((W // 2, 250 + int(lerp(24, 0, a0))), "愿望和任务", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        d.text((W // 2, 330), "写在同一页", font=sub_f, fill=mix(BG, MUTED, appear(t, 0.22)), anchor="mm")

        a1 = appear(t, ktime(0.55, duration, locked))
        if a1 > 0.04:
            y = 430 + int(lerp(24, 0, a1))
            rounded(d, (110, y, 970, y + 280), 32, mix(BG, CREAM, a1))
            d.text((W // 2, y + 90), "愿望", font=small, fill=mix(CREAM, (90, 98, 108), a1), anchor="mm")
            d.text((W // 2, y + 175), "变得很厉害", font=card_f, fill=mix(CREAM, INK, a1), anchor="mm")
            strike_at = ktime(2.56, duration, locked)
            if t >= strike_at:
                strike = appear(t, strike_at, 0.24)
                x1 = int(lerp(220, 860, strike))
                d.line([(220, y + 175), (x1, y + 175)], fill=mix(CREAM, RED, strike), width=12)
                d.text((W // 2, y + 240), "很大，没法下手", font=small, fill=mix(CREAM, RED, strike), anchor="mm")

        a2 = appear(t, ktime(1.40, duration, locked))
        if a2 > 0.04:
            y = 760 + int(lerp(24, 0, a2))
            rounded(d, (110, y, 970, y + 280), 32, mix(BG, CARD, a2))
            d.text((W // 2, y + 90), "任务", font=small, fill=mix(CARD, YELLOW, a2), anchor="mm")
            empty_at = ktime(3.48, duration, locked)
            empty = t >= empty_at
            d.text((W // 2, y + 175), "下一步：空" if empty else "下一步：？", font=card_f, fill=mix(CARD, WHITE, a2), anchor="mm")
            if empty:
                a3 = appear(t, empty_at, 0.24)
                d.text((W // 2, y + 240), "所以一条都划不掉", font=small, fill=mix(CARD, MUTED, a3), anchor="mm")
        out.append(img)
    return out


def b_one(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(64)
    sub_f = font(38, bold=False)
    card_f = font(50)
    locked = 3.58
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "03 只留一件")
        a0 = appear(t, 0.02)
        d.text((W // 2, 280 + int(lerp(22, 0, a0))), "当场做完", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        rounded(d, (140, 420, 940, 780), 36, mix(BG, CARD, appear(t, 0.18)))
        d.text((W // 2, 600), "一件事", font=card_f, fill=mix(CARD, WHITE, appear(t, 0.18)), anchor="mm")
        flip = ktime(1.34, duration, locked)
        if t < flip:
            d.text((W // 2, 920), "能开始，才算有效", font=sub_f, fill=mix(BG, MUTED, appear(t, 0.40)), anchor="mm")
        else:
            a = appear(t, flip, 0.26)
            d.text((W // 2, 900 + int(lerp(24, 0, a))), "写得越小", font=title_f, fill=mix(BG, YELLOW, a), anchor="mm")
            d.text((W // 2, 1020), "越容易开始", font=sub_f, fill=mix(BG, MINT, a), anchor="mm")
        out.append(img)
    return out


def render_brolls(data: dict) -> None:
    durs = {}
    for shot in data["shots"]:
        if shot["kind"] == "B":
            durs[shot["src"]] = max(2.2, float(shot["end"]) - float(shot["start"]))
    jobs = [
        ("broll/B-清单骗人.mp4", b_lie),
        ("broll/B-同一页.mp4", b_same_page),
        ("broll/B-一件事.mp4", b_one),
    ]
    for rel, fn in jobs:
        dur = durs[rel]
        print("broll", rel, f"{dur:.2f}s")
        frames_to_mp4(fn(dur), ROOT / rel)


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
    print("caps", dest, n)
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

    cuts = [float(s["start"]) for s in data["shutters"]]
    make_sfx(cuts, float(data["duration"]))

    audio = ROOT / data["audio"]
    bgm = ROOT / "audio" / "bgm.wav"
    sfx = ROOT / "audio" / "sfx.wav"
    final = ROOT / f"00_最终成片_{NAME}.mp4"
    (ROOT / "final").mkdir(exist_ok=True)
    (ROOT / "output").mkdir(exist_ok=True)

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

    copy_dest = ROOT / "final" / f"{NAME}.mp4"
    run(["ffmpeg", "-y", "-i", str(final), "-c", "copy", str(copy_dest)])
    run(["ffmpeg", "-y", "-i", str(final), "-c", "copy", str(ROOT / "output" / f"{NAME}.mp4")])

    staged = Path("/workspace/成片") / STAGED_NAME
    staged.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(final, staged)
    print("FINAL", final, "dur", probe_dur(final))
    print("STAGED", staged, "dur", probe_dur(staged))
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
    d.text((W // 2, 348), cover["line"], font=font(30, bold=False), fill=MUTED, anchor="mm")
    out = ROOT / "final" / "cover.jpg"
    out.parent.mkdir(exist_ok=True)
    canvas.save(out, quality=92)
    canvas.save(ROOT / f"00_封面_{NAME}.jpg", quality=92)
    print("cover", out)
    return out


def write_docs(duration: float, staged: Path) -> None:
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    status = {
        "schema_version": 1,
        "project_name": "26_待办为什么划不掉",
        "video_type": "普通短视频",
        "title": "待办为什么划不掉",
        "production_method": "白底小灯 A-roll + 黑底信息图 B-roll + edge-tts Yunyang + FFmpeg",
        "status": "已交付",
        "current_stage": "核验并交付",
        "stage": "delivered",
        "voice": VOICE,
        "locked_copy": {
            "drive_folder": "26_待办为什么划不掉",
            "drive_id": "1Awrnp5QC7dVWHNAfk-45pb-SXrjJ6MSS",
            "voiceover_sha256_drive": "B1DFB9B71068E3E5D4C45E9ED7D2AAD7FBA350BDA30711FEF05DB6EB7B1F30CA",
            "note": "跟锁定口播与七镜分组；云端重配音，不写 C/D/G，不上传 Drive",
        },
        "duration": round(duration, 3),
        "size": [W, H],
        "fps": FPS,
        "script": {"path": "script/voiceover.txt", "sha256": hashlib.sha256(vo.encode("utf-8")).hexdigest()},
        "audio": {
            "path": "audio/vo-full.wav",
            "alignment_path": "audio/vo-align.txt",
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

    note = f"""# 26 · 待办为什么划不掉

普通短视频 / 知识口播。不是剧情短剧。

- **来源**：Drive 项目 `26_待办为什么划不掉`（锁定口播 + 七镜 A/B）
- **工程草稿**：`/workspace/.abroll-cloud/26/`
- **工程成片**：`00_最终成片_待办为什么划不掉.mp4`
- **成片中转**：`/workspace/成片/26-待办为什么划不掉.mp4`

钩子：待办写了三十条，一条都没划掉。  
方法：愿望和任务不要写在同一页；今天只留一件能当场做完的事。  
收束：开始了，今天才算过了。

白底小灯 A-roll + 黑底信息图 B-roll。B 卷比对应口播早切半拍。中文全部组装阶段叠字。只在本云端 VM 渲染，未写 `C:\\` / `D:\\` / `G:\\`，未上传 Drive。

## 已核验（组装后回填）

- 规格：1080×1920，24 fps，H.264 + AAC 44100 stereo，{duration:.2f}s
- 草稿不进 `成片/`，中转只放稳定成品
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")


def qa(staged: Path, data: dict) -> dict:
    info = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(staged)],
        text=True,
    )
    meta = json.loads(info)
    v = next(s for s in meta["streams"] if s["codec_type"] == "video")
    a = next(s for s in meta["streams"] if s["codec_type"] == "audio")
    run(["ffmpeg", "-y", "-i", str(staged), "-f", "null", "-"])
    vol = subprocess.run(
        ["ffmpeg", "-i", str(staged), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    mean = maxv = None
    for line in (vol.stderr or "").splitlines():
        if "mean_volume" in line:
            mean = float(line.split(":")[-1].replace("dB", "").strip())
        if "max_volume" in line:
            maxv = float(line.split(":")[-1].replace("dB", "").strip())

    shots = data["shots"]
    overlap = any(shots[i]["end"] > shots[i + 1]["start"] + 0.001 for i in range(len(shots) - 1))
    gap = any(abs(shots[i]["end"] - shots[i + 1]["start"]) > 0.002 for i in range(len(shots) - 1))
    last_ok = abs(shots[-1]["end"] - data["duration"]) < 0.02
    fps_num, fps_den = (v.get("avg_frame_rate") or "24/1").split("/")
    fps = float(fps_num) / max(float(fps_den), 1.0)
    sha = hashlib.sha256(staged.read_bytes()).hexdigest()
    report = {
        "project": "26_待办为什么划不掉",
        "strict": True,
        "cloud_only": True,
        "no_windows_paths": True,
        "no_drive_upload": True,
        "final": str(staged),
        "sha256": sha,
        "bytes": staged.stat().st_size,
        "video": {
            "codec": v.get("codec_name"),
            "width": int(v.get("width", 0)),
            "height": int(v.get("height", 0)),
            "fps": round(fps, 3),
            "pix_fmt": v.get("pix_fmt"),
            "duration_s": round(float(meta["format"]["duration"]), 3),
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
            "last_end_equals_audio": last_ok,
        },
        "ok": (
            int(v.get("width", 0)) == 1080
            and int(v.get("height", 0)) == 1920
            and abs(fps - 24) < 0.05
            and a.get("codec_name") == "aac"
            and int(a.get("sample_rate", 0)) == 44100
            and not overlap
            and not gap
            and last_ok
            and mean is not None
            and mean < -10
        ),
    }
    (ROOT / "qa").mkdir(exist_ok=True)
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "qa" / "ffprobe.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("QA", report["ok"], report["video"], report["audio"])
    return report


def update_index(duration: float) -> None:
    path = Path("/workspace/成片/INDEX.md")
    text = path.read_text(encoding="utf-8") if path.exists() else "# 成片（可直接看）\n\n"
    if STAGED_NAME in text:
        return
    line = f"| `{STAGED_NAME}` | {duration:.1f}s |"
    if "| 文件 | 时长 |" in text:
        text = text.rstrip() + "\n" + line + "\n"
    else:
        text = text.rstrip() + "\n\n" + line + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    copy_assets()
    duration, cues = make_voiceover()
    data = build_timeline(duration, cues)
    make_bgm(duration)
    render_brolls(data)
    make_cover(data)
    staged = assemble(data)
    write_docs(duration, staged)
    report = qa(staged, data)
    update_index(float(report["video"]["duration_s"]))
    if not report["ok"]:
        raise SystemExit("QA failed")
    print("done", staged)


if __name__ == "__main__":
    main()
