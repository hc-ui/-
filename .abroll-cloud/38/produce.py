#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 38：分不清改物理和AI画错。云端 A-roll + B-roll，跟 topics-batch3 #38，不是短剧。"""
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
NAME = "分不清改物理和AI画错"
STAGED_NAME = "38-分不清改物理和AI画错.mp4"
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
CREAM = (236, 241, 239)
RED = (255, 118, 118)
INK = (28, 32, 36)
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


def split_caption(line: str) -> list[str]:
    line = line.strip("。．. ")
    if "，" in line:
        parts = [p for p in line.split("，") if p]
        if 1 < len(parts) <= 3 and all(len(p) <= 12 for p in parts):
            return parts
    if len(line) > 10:
        mid = len(line) // 2
        return [line[:mid], line[mid:]]
    return [line]


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
    dest = ROOT / "assets"
    dest.mkdir(exist_ok=True)
    for name in ("V-挥手.mp4", "V-摊手.mp4", "V-指向.mp4", "V-点赞.mp4", "A-角色-小灯-摊手.jpg"):
        src = ASSET_SRC / name
        if not src.exists():
            raise FileNotFoundError(src)
        target = dest / name
        if not target.exists() or target.stat().st_size != src.stat().st_size:
            shutil.copy2(src, target)


def make_voiceover() -> tuple[float, list[dict]]:
    text = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    phrases = [ln.strip() for ln in (ROOT / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    audio = ROOT / "audio"
    audio.mkdir(exist_ok=True)
    mp3 = audio / "vo-full.mp3"
    wav = audio / "vo-full.wav"
    align_path = audio / "vo-align.txt"
    if wav.exists() and wav.stat().st_size > 800 and align_path.exists():
        parsed = []
        for line in align_path.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) >= 3:
                parsed.append({"start": float(parts[0]), "end": float(parts[1]), "text": parts[2]})
        if len(parsed) == len(phrases) and [c["text"] for c in parsed] == phrases:
            dur = probe_dur(wav)
            parsed[0]["start"] = 0.0
            for i in range(1, len(parsed)):
                parsed[i]["start"] = parsed[i - 1]["end"]
            parsed[-1]["end"] = dur
            print("reuse VO", dur)
            return dur, parsed

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
    vtt = ["WEBVTT", ""]
    for i, c in enumerate(cues, 1):
        def ts(x: float) -> str:
            ms = int(round(x * 1000))
            return f"{ms // 3600000:02d}:{(ms // 60000) % 60:02d}:{(ms // 1000) % 60:02d}.{ms % 1000:03d}"

        vtt += [str(i), f"{ts(c['start'])} --> {ts(c['end'])}", c["text"], ""]
    (audio / "vo.vtt").write_text("\n".join(vtt), encoding="utf-8")
    return dur, cues


def build_timeline(duration: float, cues: list[dict]) -> dict:
    recipe = json.loads((ROOT / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
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

    shots_out = []
    a_caps = []
    shutters = []
    eyebrows = []
    a_i = 0
    for i, (shot, _ps, _pe) in enumerate(raw):
        start, end = cut_starts[i], cut_ends[i]
        item = {
            "id": shot["id"],
            "kind": shot["kind"],
            "start": round(start, 3),
            "end": round(end, 3),
            "src": shot["src"],
            "line": "，".join(shot["phrases"]),
        }
        if shot.get("close"):
            item["close"] = True
        if shot.get("broll"):
            item["broll"] = shot["broll"]
        shots_out.append(item)

        if shot["kind"] == "A":
            if i == 0 or shots_out[i - 1]["kind"] != "A":
                a_i += 1
            for phrase in shot["phrases"]:
                cue = phrase_lookup[phrase]
                cap_s = max(start, cue["start"])
                cap_e = min(end, cue["end"])
                if cap_e - cap_s < 0.08:
                    continue
                a_caps.append({"start": round(cap_s, 3), "end": round(cap_e, 3), "lines": split_caption(phrase)})
            eyebrows.append({"start": round(start, 3), "end": round(end, 3), "text": f"A-ROLL / {a_i:02d}"})
        if i > 0:
            if shot["kind"] == "B" and shots_out[i - 1]["kind"] == "A":
                shutters.append({"start": round(start, 3), "color": list(MINT)})
            elif shot["kind"] == "A":
                shutters.append({"start": round(start, 3), "color": list(YELLOW)})
            else:
                shutters.append({"start": round(start, 3), "color": list(CREAM)})

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
        "locked_copy": "topics-batch3.md #38 / EP001-生产包.md",
        "b_lead_s": LEAD,
        "video_type": "普通短视频",
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
        "cue_map": {c["text"]: [round(c["start"], 3), round(c["end"], 3)] for c in cues},
    }
    (ROOT / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return timeline


def make_bgm(duration: float) -> None:
    dest = ROOT / "audio" / "bgm.wav"
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=196:sample_rate=44100:duration={duration + 2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=247:sample_rate=44100:duration={duration + 2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=294:sample_rate=44100:duration={duration + 2:.2f}",
        "-filter_complex",
        "[0:a]volume=0.12[a];[1:a]volume=0.08[b];[2:a]volume=0.06[c];"
        "[a][b][c]amix=inputs=3:duration=longest,lowpass=f=520,alimiter=limit=0.35",
        "-ac", "2", "-ar", "44100", str(dest),
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


def render_b_bead(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(52)
    card_f = font(44)
    sub_f = font(30, bold=False)
    rows = [
        (0.10, "正常飞溅", "观众认得出水", MINT, False),
        (0.42, "微妙玻璃珠", "看起来像穿帮", RED, True),
        (0.78, "整街水洼鼓起", "大到不可能是错", YELLOW, False),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "对照 三种尺度")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(16, 0, a0))), "同一滴水", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        d.text((W // 2, 330), "三种读法", font=sub_f, fill=mix(BG, MUTED, appear(t, 0.12)), anchor="mm")
        for idx, (ts, head, body, color, warn) in enumerate(rows):
            a = appear(t, ts, 0.22)
            if a < 0.04:
                continue
            y = 420 + idx * 280 + int(lerp(20, 0, a))
            rounded(d, (90, y, 990, y + 246), 30, mix(BG, CARD, a))
            d.rounded_rectangle((120, y + 58, 214, y + 186), 18, fill=mix(CARD, color, a))
            d.text((167, y + 122), str(idx + 1), font=font(40), fill=mix(color, INK, a), anchor="mm")
            d.text((248, y + 86), head, font=card_f, fill=mix(CARD, color, a), anchor="lm")
            d.text((248, y + 168), body, font=sub_f, fill=mix(CARD, WHITE, a), anchor="lm")
            if warn:
                strike = appear(t, ts + 0.28, 0.20)
                if strike > 0.04:
                    tw, _ = text_wh(d, head, card_f)
                    x1 = int(lerp(248, 248 + tw + 8, strike))
                    d.line([(248, y + 86), (x1, y + 86)], fill=mix(CARD, RED, strike), width=8)
        out.append(img)
    return out


def render_b_draw(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(64)
    card_f = font(48)
    sub_f = font(32, bold=False)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "抽卡 救不了")
        a0 = appear(t, 0.02)
        d.text((W // 2, 280 + int(lerp(18, 0, a0))), "再抽一张", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        a1 = appear(t, 0.18)
        cx, cy, r = W // 2, 780, 220
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=mix(BG, CARD, a1), outline=mix(CARD, YELLOW, a1), width=10)
        d.text((cx, cy), "抽卡", font=title_f, fill=mix(CARD, YELLOW, a1), anchor="mm")
        boom = appear(t, 0.55, 0.22)
        if boom > 0.04:
            d.line([(cx - 150, cy - 150), (cx + 150, cy + 150)], fill=mix(CARD, RED, boom), width=18)
            d.line([(cx + 150, cy - 150), (cx - 150, cy + 150)], fill=mix(CARD, RED, boom), width=18)
            y = 1180 + int(lerp(18, 0, boom))
            rounded(d, (140, y, 940, y + 200), 28, mix(BG, (42, 28, 18), boom))
            d.text((W // 2, y + 100), "救不了", font=card_f, fill=mix(BG, RED, boom), anchor="mm")
        d.text((W // 2, 1480), "微妙对照会被当成穿帮", font=sub_f, fill=mix(BG, MUTED, appear(t, 0.72)), anchor="mm")
        out.append(img)
    return out


def render_b_rules(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(56)
    card_f = font(42)
    sub_f = font(30, bold=False)
    rows = [
        (0.12, "1", "先正常", "再给反常", YELLOW),
        (0.42, "2", "片头字卡", "只改这一条", MINT),
        (0.72, "3", "尺度放大", "大到不像穿帮", CREAM),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "三条规矩")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(16, 0, a0))), "只改这一条", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        d.text((W // 2, 340), "开头先写清", font=sub_f, fill=mix(BG, MUTED, appear(t, 0.12)), anchor="mm")
        for idx, (ts, num, head, body, color) in enumerate(rows):
            a = appear(t, ts, 0.22)
            if a < 0.04:
                continue
            y = 430 + idx * 280 + int(lerp(18, 0, a))
            rounded(d, (90, y, 990, y + 246), 30, mix(BG, CARD, a))
            d.ellipse((128, y + 58, 248, y + 178), fill=mix(CARD, color, a))
            d.text((188, y + 118), num, font=font(42), fill=mix(color, INK, a), anchor="mm")
            d.text((280, y + 90), head, font=card_f, fill=mix(CARD, color, a), anchor="lm")
            d.text((280, y + 168), body, font=sub_f, fill=mix(CARD, WHITE, a), anchor="lm")
        out.append(img)
    return out


def render_brolls(data: dict) -> None:
    durs = {}
    for shot in data["shots"]:
        if shot["kind"] == "B":
            durs[shot["src"]] = max(2.2, float(shot["end"]) - float(shot["start"]))
    jobs = [
        ("broll/B-玻璃珠对照.mp4", render_b_bead),
        ("broll/B-抽卡救不了.mp4", render_b_draw),
        ("broll/B-三条规矩.mp4", render_b_rules),
    ]
    for rel, fn in jobs:
        dur = durs[rel]
        print("broll", rel, f"{dur:.2f}s")
        frames_to_mp4(fn(dur + 0.12), ROOT / rel)


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
    long = any(len(s) > 8 for s in lines)
    fnt = font(48 if long or len(lines) > 1 else 56)
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
    make_sfx([float(s["start"]) for s in data["shutters"]], float(data["duration"]))
    final = ROOT / f"00_最终成片_{NAME}.mp4"
    (ROOT / "final").mkdir(exist_ok=True)
    inputs = ["ffmpeg", "-y", "-i", str(burned), "-i", str(audio)]
    filters = ["[1:a]loudnorm=I=-16:LRA=11:TP=-1.5,aformat=sample_rates=44100:channel_layouts=stereo[vo]"]
    mix_ins = ["[vo]"]
    idx = 2
    bgm = ROOT / "audio" / "bgm.wav"
    sfx = ROOT / "audio" / "sfx.wav"
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
    d.text((W // 2, 160), cover["title"], font=font(58), fill=WHITE, anchor="mm")
    d.text((W // 2, 250), cover["sub"], font=font(52), fill=YELLOW, anchor="mm")
    d.text((W // 2, 340), "抽卡救不了", font=font(36), fill=MINT, anchor="mm")
    d.text((W // 2, 410), cover["line"], font=font(30), fill=MUTED, anchor="mm")
    dest = ROOT / f"00_封面_{NAME}.jpg"
    canvas.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    canvas.save(ROOT / "final" / "cover.jpg", quality=92)
    return dest


def write_docs(duration: float, staged: Path, data: dict) -> None:
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    sha = hashlib.sha256(vo.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    status = {
        "schema_version": 1,
        "project_name": "38_分不清改物理和AI画错",
        "video_type": "普通短视频",
        "episode": 38,
        "title": NAME,
        "source_note": "topics-batch3.md #38 / 选题库.md 001 暂缓 / EP001-生产包.md",
        "voice": VOICE,
        "duration": round(duration, 3),
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
            "project_final": f"00_最终成片_{NAME}.mp4",
            "cover": f"00_封面_{NAME}.jpg",
        },
        "staged": f"成片/{STAGED_NAME}",
        "cloud_only": True,
        "windows_paths": False,
        "drive_upload": False,
        "not": "drama-pipeline / 仙侠连载 / 成片30雨滴弹回主钩",
        "updated_at": now,
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note = f"""# 38 · 分不清改物理和AI画错

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。

- **选题**：`topics-batch3.md` 第 38 条；Drive `选题库.md` 第 001 号暂缓说明；`EP001-生产包.md`
- **明确不用**：成片 30「雨滴弹回」当主钩；定律主钩重拍
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿目录**：`/workspace/.abroll-cloud/38/`
- **云端 only**：不写 `C:\\` / `D:\\` / `G:\\`，不传 Drive

钩子：一颗不融进水的球，观众当 AI 画错。  
方法：抽卡救不了。先给正常再给反常；片头写清只改这一条。  
收束：尺度放大，大到不可能是穿帮。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {duration:.2f} 秒。镜头 {len(data["shots"])} 条，时间轴闭合。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")


def patch_index(duration: float) -> None:
    idx = Path("/workspace/成片/INDEX.md")
    line = f"| `{STAGED_NAME}` | {duration:.1f}s |"
    if idx.exists():
        text = idx.read_text(encoding="utf-8")
        if STAGED_NAME not in text:
            if not text.endswith("\n"):
                text += "\n"
            text += line + "\n"
            idx.write_text(text, encoding="utf-8")
    else:
        idx.write_text(
            "# 成片（可直接看）\n\n竖屏口播 1080×1920，H.264 + AAC。\n\n| 文件 | 时长 |\n|------|------|\n"
            + line + "\n",
            encoding="utf-8",
        )


def qa(staged: Path, data: dict) -> dict:
    qa_dir = ROOT / "qa"
    qa_dir.mkdir(exist_ok=True)
    probe = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(staged)],
        text=True,
    )
    (qa_dir / "ffprobe.txt").write_text(probe, encoding="utf-8")
    info = json.loads(probe)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next(s for s in info["streams"] if s["codec_type"] == "audio")
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
    shots = data["shots"]
    overlap = any(shots[i]["end"] > shots[i + 1]["start"] + 0.001 for i in range(len(shots) - 1))
    gap = any(abs(shots[i]["end"] - shots[i + 1]["start"]) > 0.02 for i in range(len(shots) - 1))
    fps_num, fps_den = (v.get("r_frame_rate") or "24/1").split("/")
    fps = float(fps_num) / float(fps_den or 1)
    digest = hashlib.sha256(staged.read_bytes()).hexdigest()
    report = {
        "project": "38_分不清改物理和AI画错",
        "strict": True,
        "cloud_only": True,
        "windows_paths": False,
        "drive_upload": False,
        "video_type": "普通短视频",
        "final": str(staged),
        "project_final": str(ROOT / f"00_最终成片_{NAME}.mp4"),
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
    )
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    copy_assets()
    duration, cues = make_voiceover()
    print("VO", duration)
    for row in cues:
        print(f"  {row['start']:6.3f}-{row['end']:6.3f}  {row['text']}")
    make_bgm(duration)
    data = build_timeline(duration, cues)
    print("timeline shots", [(s["id"], s["start"], s["end"], s["kind"]) for s in data["shots"]])
    render_brolls(data)
    make_cover()
    staged = assemble(data)
    dur = probe_dur(staged)
    write_docs(dur, staged, data)
    patch_index(dur)
    report = qa(staged, data)
    print("STAGED", staged, "dur", dur, "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
