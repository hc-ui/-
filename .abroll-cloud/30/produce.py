# -*- coding: utf-8 -*-
"""Topic 30 / 选题库 001：雨滴弹回。云端 A-roll + B-roll。

普通短视频 / 知识口播。只改一条定律：水的表面张力 ×100。
先正常后反常 → 三个后果 → 整街凸洼回报。
草稿只写 .abroll-cloud/30/，成品中转 成片/30-雨滴弹回.mp4。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
import shutil
import struct
import subprocess
import wave
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path("/workspace/.abroll-cloud/30")
A_SRC = Path("/workspace/.abroll-cloud/06/assets")
W, H, FPS = 1080, 1920, 24
NAME = "雨滴弹回"
STAGED_NAME = "30-雨滴弹回.mp4"
VOICE = "zh-CN-YunyangNeural"
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_RG = "/tmp/NotoSansSC-Regular.otf"
FONT_FB = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

BG = (8, 12, 20)
CARD = (20, 26, 38)
MINT = (126, 224, 197)
CYAN = (88, 214, 232)
ICE = (186, 230, 242)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
CREAM = (245, 247, 250)
MUTED = (154, 162, 176)
RED = (255, 118, 118)
NAVY = (14, 22, 40)
WARM = (232, 168, 72)
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
    for path in ((FONT_BD if bold else FONT_RG), FONT_FB):
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


def ticks_to_s(v: float) -> float:
    if v > 1000:
        return v / 10_000_000.0
    return float(v)


def cover(im: Image.Image, w: int, h: int, zoom: float = 1.0, pan_y: float = 0.0) -> Image.Image:
    im = im.convert("RGB")
    scale = max(w / im.width, h / im.height) * zoom
    nw, nh = max(w, int(im.width * scale)), max(h, int(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - w) // 2
    y = int((nh - h) * (0.42 + pan_y))
    y = max(0, min(nh - h, y))
    return im.crop((x, y, x + w, y + h))


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


# ---------- TTS ----------
async def synthesize_voice(text: str, mp3: Path) -> list[dict]:
    import edge_tts

    comm = edge_tts.Communicate(text, VOICE, rate="-4%")
    bounds: list[dict] = []
    with mp3.open("wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("SentenceBoundary", "WordBoundary"):
                bounds.append(chunk)
    return bounds


def compact(s: str) -> str:
    for ch in "，。、！？,.!?;；：: “”\"' ":
        s = s.replace(ch, "")
    return s


def align_phrases(phrases: list[str], bounds: list[dict], dur: float) -> list[dict]:
    sents = [b for b in bounds if b.get("type") == "SentenceBoundary" and b.get("text")]
    words = [b for b in bounds if b.get("type") == "WordBoundary" and b.get("text")]
    cues: list[dict] = []

    if sents:
        used = [False] * len(sents)
        for phrase in phrases:
            target = compact(phrase)
            best = None
            best_i = -1
            for i, sent in enumerate(sents):
                if used[i]:
                    continue
                body = compact(str(sent.get("text") or ""))
                if target and (target in body or body in target):
                    best, best_i = sent, i
                    break
            if best is None:
                for i, sent in enumerate(sents):
                    if not used[i]:
                        best, best_i = sent, i
                        break
            if best is None:
                continue
            used[best_i] = True
            st = ticks_to_s(best.get("offset", 0))
            en = st + ticks_to_s(best.get("duration", 0))
            cues.append({"text": phrase, "start": st, "end": en})

    if len(cues) != len(phrases) and words:
        stream = []
        for w in words:
            st = ticks_to_s(w.get("offset", 0))
            en = st + ticks_to_s(w.get("duration", 0))
            for ch in str(w.get("text") or ""):
                if ch not in "，。、！？,.!?;；：: “”\"' ":
                    stream.append((ch, st, en))
        cues = []
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
                if not target.startswith(built):
                    if built[-1] not in target:
                        built = built[:-1]
                        start_t = start_t if built else None
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


def make_voiceover() -> tuple[float, list[dict]]:
    text = (ROOT / "script/voiceover.txt").read_text(encoding="utf-8").strip()
    phrases = [ln.strip() for ln in (ROOT / "script/phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    audio = ROOT / "audio"
    audio.mkdir(parents=True, exist_ok=True)
    mp3 = audio / "vo-full.mp3"
    wav = audio / "vo-full.wav"
    bounds = asyncio.run(synthesize_voice(text, mp3))
    (audio / "vo.vtt.json").write_text(json.dumps(bounds, ensure_ascii=False, indent=2), encoding="utf-8")
    run(["ffmpeg", "-y", "-i", str(mp3), "-ac", "1", "-ar", "44100", "-sample_fmt", "s16", str(wav)])
    dur = probe_dur(wav)
    cues = align_phrases(phrases, bounds, dur)
    lines = [f"{c['start']:.3f}\t{c['end']:.3f}\t{c['text']}" for c in cues]
    (audio / "vo-align.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (audio / "cues.json").write_text(json.dumps(cues, ensure_ascii=False, indent=2), encoding="utf-8")
    print("TTS", f"{dur:.3f}s", "cues", len(cues))
    return dur, cues


def split_caption(line: str) -> list[str]:
    line = line.strip("。．. ")
    if "，" in line and len(line) > 8:
        parts = [p for p in line.split("，") if p]
        if 1 < len(parts) <= 2:
            return parts
    return [line]


def build_timeline(cues: list[dict], dur: float) -> dict:
    recipe = json.loads((ROOT / "plan/shot_recipe.json").read_text(encoding="utf-8"))
    pmap = {c["text"]: c for c in cues}
    shots = []
    for spec in recipe["shots"]:
        ps = spec["phrases"]
        start = pmap[ps[0]]["start"]
        end = pmap[ps[-1]]["end"]
        item = {
            "id": spec["id"],
            "kind": spec["kind"],
            "src": spec["src"],
            "close": bool(spec.get("close")),
            "line": ps[-1],
            "phrases": ps,
            "start": start,
            "end": end,
        }
        if spec.get("broll"):
            item["broll"] = spec["broll"]
        shots.append(item)

    for i in range(1, len(shots)):
        if shots[i]["kind"] == "B" and shots[i - 1]["kind"] == "A":
            pull = min(LEAD, max(0.0, (shots[i - 1]["end"] - shots[i - 1]["start"]) - 0.55))
            shots[i]["start"] -= pull
            shots[i - 1]["end"] -= pull
    shots[0]["start"] = 0.0
    for i in range(1, len(shots)):
        shots[i]["start"] = shots[i - 1]["end"]
    shots[-1]["end"] = dur

    a_caps = []
    eyebrows = []
    shutters = []
    for i, shot in enumerate(shots):
        if shot["kind"] == "A":
            a_caps.append({
                "start": round(shot["start"], 3),
                "end": round(shot["end"], 3),
                "lines": split_caption(shot["line"]),
            })
            eyebrows.append({
                "start": round(shot["start"], 3),
                "end": round(shot["end"], 3),
                "text": f"A-ROLL / {shot['id'][-2:]}",
            })
        if i > 0:
            color = list(MINT) if shot["kind"] == "B" else list(CREAM)
            if i == len(shots) - 1:
                color = list(YELLOW)
            shutters.append({"start": round(shot["start"], 3), "color": color})
        shot["start"] = round(shot["start"], 3)
        shot["end"] = round(shot["end"], 3)

    data = {
        "audio": "audio/vo-full.wav",
        "duration": round(dur, 3),
        "fps": FPS,
        "size": [W, H],
        "title": recipe["title"],
        "video_type": "普通短视频",
        "topic_id": "001",
        "bgm": "audio/bgm.wav",
        "shots": shots,
        "a_caps": a_caps,
        "shutters": shutters,
        "eyebrows": eyebrows,
        "cover": {
            "title": recipe["cover_title"],
            "sub": recipe["cover_sub"],
            "line": recipe["cover_line"],
        },
    }
    (ROOT / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("timeline", dur, "shots", len(shots))
    return data


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
            0.050 * math.sin(2 * math.pi * 174.61 * t)
            + 0.036 * math.sin(2 * math.pi * 220.00 * t)
            + 0.024 * math.sin(2 * math.pi * 261.63 * t)
            + 0.014 * math.sin(2 * math.pi * 329.63 * t)
        )
        samples.append(s * env)
    path = ROOT / "audio/bgm.wav"
    write_wav_stereo(path, samples, sr)
    return path


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
            samples[start + i] += env * 0.22 * math.sin(2 * math.pi * (480 + 640 * (i / length)) * t)
    path = ROOT / "audio/sfx.wav"
    write_wav_stereo(path, samples, sr)
    return path


# ---------- B-roll drawing ----------
def new_b_bg() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    overlay = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(overlay)
    d.ellipse((-280, -360, 760, 620), fill=(18, 36, 58))
    d.ellipse((300, 1200, 1380, 2140), fill=(36, 24, 16))
    overlay = overlay.filter(ImageFilter.GaussianBlur(120))
    return Image.blend(img, overlay, 0.62)


def tag_chip(draw: ImageDraw.ImageDraw, t: float, label: str) -> None:
    a = appear(t, 0.0, 0.22)
    if a <= 0:
        return
    fnt = font(30)
    tw, th = text_wh(draw, label, fnt)
    x, y = 84, 88
    rounded(draw, (x - 22, y - 14, x + tw + 22, y + th + 12), 22, mix(BG, (16, 38, 48), a))
    draw.text((x, y), label, font=fnt, fill=mix(BG, CYAN, a))


def strike_line(draw, box, t: float, start: float) -> None:
    st = appear(t, start, 0.28)
    if st <= 0.04:
        return
    cy = (box[1] + box[3]) // 2
    x0, x1 = box[0] + 48, box[2] - 48
    draw.line([(x0, cy), (int(lerp(x0, x1, st)), cy)], fill=mix(CARD, RED, st), width=10)


def punch_bar(img: Image.Image, t: float, title: str, punch: str, start: float = 0.18) -> None:
    a = appear(t, start, 0.26)
    if a <= 0:
        return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y = 1480 + int((1 - a) * 24)
    d.rounded_rectangle((86, y, 994, y + 280), radius=34, fill=(12, 16, 26, int(228 * a)))
    d.text((540, y + 88), title, font=font(38), fill=(*mix(CARD, MUTED, a), 255), anchor="mm")
    d.text((540, y + 186), punch, font=font(58), fill=(*mix(CARD, CYAN, a), 255), anchor="mm")
    out = Image.alpha_composite(img.convert("RGBA"), layer)
    img.paste(out.convert("RGB"))


def shade_still(still: Image.Image, t: float, duration: float) -> Image.Image:
    p = t / max(duration, 0.01)
    img = cover(still, W, H, zoom=1.04 + 0.08 * p, pan_y=-0.03 + 0.07 * p)
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for y in range(0, 200):
        sd.line([(0, y), (W, y)], fill=(8, 10, 14, int(100 * (1 - y / 200))))
    for y in range(H - 580, H):
        sd.line([(0, y), (W, y)], fill=(8, 10, 14, int(210 * ((y - (H - 580)) / 580))))
    return Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")


def draw_umbrella(d: ImageDraw.ImageDraw, cx: int, cy: int, dent: float) -> None:
    dent = max(0.0, min(1.0, dent))
    # canopy
    rx, ry = 430, 210
    body = (22, 26, 34)
    d.ellipse((cx - rx, cy - ry + int(dent * 28), cx + rx, cy + ry + int(dent * 18)), fill=body)
    # ribs
    for k in range(-4, 5):
        ang = math.radians(k * 16)
        x1 = cx + int(math.sin(ang) * (rx - 18))
        y1 = cy + int(math.cos(ang) * (ry - 12)) + int(dent * 16)
        d.line([(cx, cy - 8), (x1, y1 + 40)], fill=(36, 42, 54), width=4)
    # warm grazing highlight
    d.arc((cx - rx + 20, cy - ry + 10, cx - 40, cy + 80), start=200, end=320, fill=mix(body, WARM, 0.45), width=6)
    # tip
    d.ellipse((cx - 14, cy - ry - 18, cx + 14, cy - ry + 16), fill=(70, 74, 82))
    if dent > 0.05:
        drx = int(70 + 50 * dent)
        dry = int(22 + 28 * dent)
        d.ellipse((cx - drx, cy - 10, cx + drx, cy + dry + 20), fill=(12, 14, 20))


def draw_drop(d: ImageDraw.ImageDraw, x: float, y: float, rx: float, ry: float, alpha: float = 1.0) -> None:
    if alpha <= 0.04 or rx < 4 or ry < 4:
        return
    col = mix(BG, CYAN, 0.82 * alpha)
    rim = mix(BG, ICE, 0.95 * alpha)
    d.ellipse((int(x - rx), int(y - ry), int(x + rx), int(y + ry)), fill=col, outline=rim, width=4)
    hx, hy = x - rx * 0.28, y - ry * 0.32
    d.ellipse((int(hx - 16), int(hy - 12), int(hx + 22), int(hy + 16)), fill=mix(col, WHITE, 0.55 * alpha))
    d.ellipse((int(x + 8), int(y + 6), int(x + 26), int(y + 22)), fill=mix(col, WARM, 0.7 * alpha))


def draw_splash_bits(d: ImageDraw.ImageDraw, cx: int, cy: int, age: float) -> None:
    for k in range(18):
        ang = math.radians(-20 + k * 12)
        dist = 40 + age * (220 + (k % 5) * 18)
        fade = max(0.0, 1.0 - age * 1.15)
        if fade <= 0.04:
            continue
        px = cx + math.sin(ang) * dist
        py = cy - abs(math.cos(ang)) * dist * 0.72 + age * 80
        rr = max(3, 16 - age * 12)
        d.ellipse((int(px - rr), int(py - rr * 0.8), int(px + rr), int(py + rr * 0.8)), fill=mix(BG, ICE, fade))


def render_b_law(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, sub_f = font(56), font(40), font(30)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        draw_drop(d, 540, 1080, 78, 78, 0.35 + 0.08 * math.sin(t * 3))
        tag_chip(d, t, "改一条定律")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(18, 0, a0))), "水的表面张力", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        a1 = appear(t, 0.26)
        if a1 > 0.04:
            y = 340 + int(lerp(20, 0, a1))
            box = (90, y, 990, y + 220)
            rounded(d, box, 30, mix(BG, CARD, a1))
            d.text((540, y + 74), "水是软的，会溅开", font=card_f, fill=mix(CARD, YELLOW, a1), anchor="mm")
            d.text((540, y + 150), "砸伞就炸成水花", font=sub_f, fill=mix(CARD, MUTED, a1), anchor="mm")
            strike_line(d, box, t, 0.78)

        a2 = appear(t, 1.05)
        if a2 > 0.04:
            y = 600 + int(lerp(20, 0, a2))
            rounded(d, (90, y, 990, y + 240), 30, mix(BG, CARD, a2))
            d.text((540, y + 82), "张力乘一百", font=title_f, fill=mix(CARD, CYAN, a2), anchor="mm")
            d.text((540, y + 168), "水球有一层皮，会弹", font=sub_f, fill=mix(CARD, WHITE, a2), anchor="mm")

        punch = appear(t, min(1.85, max(0.9, duration - 1.05)), 0.26)
        if punch > 0.04:
            y = 980 + int(lerp(22, 0, punch))
            rounded(d, (160, y, 920, y + 180), 28, mix(BG, (18, 42, 48), punch))
            d.text((W // 2, y + 90), "×100", font=title_f, fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def _umbrella_drop_state(t: float, duration: float, mode: str) -> dict:
    p = t / max(duration, 0.01)
    contact = 0.32
    if p < contact:
        u = p / contact
        return {
            "x": 540.0,
            "y": lerp(280, 980, u ** 1.35),
            "rx": 72.0,
            "ry": 72.0,
            "dent": 0.0,
            "alive": True,
            "splash": 0.0,
        }
    age = (p - contact) / max(1e-6, 1 - contact)
    if mode == "splash":
        return {"x": 540.0, "y": 980.0, "rx": 0.0, "ry": 0.0, "dent": 0.15, "alive": False, "splash": age}
    # bounce: squash, then two hops, then settle
    if age < 0.16:
        u = age / 0.16
        return {
            "x": 540.0,
            "y": 980 + 18 * u,
            "rx": lerp(72, 108, u),
            "ry": lerp(72, 38, u),
            "dent": u,
            "alive": True,
            "splash": 0.0,
        }
    if age < 0.42:
        u = (age - 0.16) / 0.26
        hop = math.sin(u * math.pi)
        return {
            "x": 540.0 + 10 * u,
            "y": 980 - 210 * hop,
            "rx": lerp(108, 68, hop),
            "ry": lerp(38, 86, hop),
            "dent": max(0.0, 1 - u * 1.4),
            "alive": True,
            "splash": 0.0,
        }
    if age < 0.64:
        u = (age - 0.42) / 0.22
        hop = math.sin(u * math.pi)
        return {
            "x": 556 + 16 * u,
            "y": 980 - 90 * hop,
            "rx": lerp(78, 64, hop),
            "ry": lerp(52, 80, hop),
            "dent": 0.18 * (1 - u),
            "alive": True,
            "splash": 0.0,
        }
    u = min(1.0, (age - 0.64) / 0.36)
    return {
        "x": 572 + 36 * u,
        "y": 992,
        "rx": 70,
        "ry": 66,
        "dent": 0.06,
        "alive": True,
        "splash": 0.0,
    }


def render_b_impact(duration: float, mode: str) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    tag = "先正常" if mode == "splash" else "再反常"
    title = "雨砸伞" if mode == "splash" else "砸下去压个坑"
    punch = "炸开" if mode == "splash" else "弹回来"
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        st = _umbrella_drop_state(t, duration, mode)
        draw_umbrella(d, 540, 1040, st["dent"])
        if st["alive"]:
            draw_drop(d, st["x"], st["y"], st["rx"], st["ry"])
        if st["splash"] > 0:
            draw_splash_bits(d, 540, 1000, st["splash"])
        tag_chip(d, t, tag)
        punch_bar(img, t, title, punch, start=0.12)
        out.append(img)
    return out


def render_b_still(src: Path, duration: float, tag: str, title: str, punch: str) -> list[Image.Image]:
    still = ImageEnhance.Color(Image.open(src).convert("RGB")).enhance(1.05)
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = shade_still(still, t, duration)
        d = ImageDraw.Draw(img)
        tag_chip(d, t, tag)
        punch_bar(img, t, title, punch, start=0.14)
        out.append(img)
    return out


def render_broll(data: dict) -> None:
    durs = {}
    for shot in data["shots"]:
        if shot["kind"] == "B":
            durs[shot["src"]] = max(1.5, float(shot["end"]) - float(shot["start"]))
    jobs = [
        ("broll/B-定律.mp4", lambda d: render_b_law(d)),
        ("broll/B-正常.mp4", lambda d: render_b_impact(d, "splash")),
        ("broll/B-弹回.mp4", lambda d: render_b_impact(d, "bounce")),
        ("broll/B-凝胶.mp4", lambda d: render_b_still(ROOT / "assets/t30b-gel-asphalt.png", d, "后果 01", "落地不飞溅", "像凝胶球")),
        ("broll/B-落叶.mp4", lambda d: render_b_still(ROOT / "assets/t30c-leaf-convex.png", d, "后果 02", "落叶压出坑", "浮着不沉")),
        ("broll/B-凸街.mp4", lambda d: render_b_still(ROOT / "assets/t30d-convex-street.png", d, "回报", "整条街水洼", "全是凸的")),
    ]
    for rel, fn in jobs:
        dur = durs.get(rel)
        if not dur:
            raise SystemExit(f"no duration for {rel}")
        print("render", rel, f"{dur:.2f}s")
        frames = fn(dur + 0.12)
        dest = ROOT / rel
        frames_to_mp4(frames, dest)


# ---------- captions / assemble ----------
def draw_eyebrow(base: Image.Image, t: float, eyebrows) -> None:
    label = None
    for item in eyebrows:
        if item["start"] <= t < item["end"]:
            label = item["text"]
            break
    if not label:
        return
    d = ImageDraw.Draw(base)
    d.rectangle((76, 88, 120, 92), fill=(*CYAN, 230))
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
    pd.rectangle((10, 14, 20, box_h - 14), fill=(*CYAN, 235))
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
    dest = ROOT / "shots/caption_layer.mov"
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
    print("caps", dest, "frames", n)
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
        if kind == "A":
            vf = f"setpts=PTS*{dur / src_dur:.6f},{vf}"
        else:
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
    make_bgm(float(data["duration"]))
    make_sfx(cuts, float(data["duration"]))

    vo = ROOT / data["audio"]
    bgm = ROOT / "audio/bgm.wav"
    sfx = ROOT / "audio/sfx.wav"
    final = ROOT / f"00_最终成片_{NAME}.mp4"
    run([
        "ffmpeg", "-y",
        "-i", str(burned),
        "-i", str(vo),
        "-i", str(bgm),
        "-i", str(sfx),
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
    ])
    (ROOT / "output").mkdir(exist_ok=True)
    (ROOT / "final").mkdir(exist_ok=True)
    shutil.copy2(final, ROOT / "output" / f"{NAME}.mp4")
    shutil.copy2(final, ROOT / "final" / f"{NAME}.mp4")
    staged = Path("/workspace/成片") / STAGED_NAME
    staged.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(final, staged)
    print("FINAL", final, "dur", probe_dur(final))
    print("STAGED", staged, "dur", probe_dur(staged))
    return staged


def write_cover() -> Path:
    dest = ROOT / f"00_封面_{NAME}.jpg"
    still = Image.open(ROOT / "assets/t30a-umbrella-bounce.png").convert("RGB")
    img = cover(still, W, H, zoom=1.08, pan_y=-0.02)
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rounded_rectangle((70, 160, 1010, 620), radius=40, fill=(10, 14, 22, 214))
    img = Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")
    d = ImageDraw.Draw(img)
    d.text((540, 260), "雨滴砸伞", font=font(86), fill=WHITE, anchor="mm")
    d.text((540, 380), "不炸开，弹回来", font=font(56), fill=CYAN, anchor="mm")
    d.text((540, 500), "表面张力 ×100", font=font(36), fill=YELLOW, anchor="mm")
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    img.save(ROOT / "final" / "cover.jpg", quality=92)
    return dest


def write_docs(dur: float, staged: Path, data: dict) -> None:
    vo = (ROOT / "script/voiceover.txt").read_text(encoding="utf-8").strip()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    status = {
        "schema_version": 1,
        "project_name": "30_雨滴弹回",
        "video_type": "普通短视频",
        "episode": 30,
        "topic_id": "001",
        "source_note": "选题库.md #001 / 水的表面张力 ×100",
        "title": NAME,
        "stage": "delivered",
        "status": "已交付",
        "current_stage": "核验并交付",
        "production_method": "白底小灯 A-roll + 黑底弹跳信息图/无字静帧 B-roll + edge-tts Yunyang + FFmpeg",
        "voice": VOICE,
        "duration": round(dur, 3),
        "size": [W, H],
        "fps": FPS,
        "script": {"path": "script/voiceover.txt", "sha256": hashlib.sha256(vo.encode("utf-8")).hexdigest()},
        "audio": {
            "path": "audio/vo-full.wav",
            "alignment_path": "audio/vo-align.txt",
            "voice_id": VOICE,
            "sample_rate": 44100,
            "channels": 1,
            "duration_ms": int(dur * 1000),
            "note": "云端 edge-tts zh-CN-YunyangNeural，未走本机盘符",
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
        "not": "剧情短剧 / drama-pipeline / Drive 上传 / C: D: G:",
        "siblings_avoided": ["002", "006", "007", "009", "010", "003", "005", "008"],
        "updated_at": now,
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    explain = f"""# 30 · 雨滴弹回

普通短视频 / 知识口播。**不是**剧情短剧，不走 drama-pipeline。

- **选题**：Drive `选题库.md` 第 **001** 号 · 水的表面张力 ×100
- **结构**：改一条定律 → 先正常后反常 → 三个后果（凝胶球 / 落叶不沉 / 水面鼓起）→ 整街凸洼回报
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/30/`
- **云端 only**：未写 `C:\\\\` / `D:\\\\` / `G:\\\\`，未上传 Drive

钩子：雨砸伞，不炸开，弹回来。  
收束：整条街的水洼，全是凸的。

白底小灯 A-roll + 黑底弹跳信息图 / 无字静帧 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {dur:.2f} 秒。镜头 {len(data["shots"])} 条，时间轴闭合。
"""
    (ROOT / "项目说明.md").write_text(explain, encoding="utf-8")


def copy_assets() -> None:
    assets = ROOT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for name in ("V-挥手.mp4", "V-摊手.mp4", "V-指向.mp4", "A-角色-小灯-摊手.jpg"):
        src = A_SRC / name
        if not src.exists():
            raise FileNotFoundError(src)
        dest = assets / name
        if not dest.exists() or dest.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dest)
    for name in (
        "t30a-umbrella-bounce.png",
        "t30b-gel-asphalt.png",
        "t30c-leaf-convex.png",
        "t30d-convex-street.png",
    ):
        if not (assets / name).exists():
            raise FileNotFoundError(assets / name)


def patch_index(duration: float) -> None:
    idx = Path("/workspace/成片/INDEX.md")
    row = f"| `{STAGED_NAME}` | {duration:.1f}s |"
    if idx.exists():
        text = idx.read_text(encoding="utf-8")
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
    else:
        idx.write_text(
            "# 成片（可直接看）\n\n竖屏口播 1080×1920，H.264 + AAC。\n\n| 文件 | 时长 |\n|------|------|\n"
            + row + "\n",
            encoding="utf-8",
        )


def patch_delivery(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    row = (
        f"| `成片/{STAGED_NAME}` | 1080×1920 h264+aac 44.1k stereo | "
        f"{duration:.2f}s | topic 30 选题库 001 雨滴弹回 |"
    )
    if STAGED_NAME in text:
        lines = []
        for ln in text.splitlines():
            if STAGED_NAME in ln and ln.startswith("|"):
                lines.append(row)
            else:
                lines.append(ln)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    lines = text.splitlines()
    insert_at = None
    for i, ln in enumerate(lines):
        if ln.startswith("| `成片/仙侠"):
            insert_at = i
            break
    if insert_at is None:
        lines.append(row)
    else:
        lines.insert(insert_at, row)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
        "project": "30_雨滴弹回",
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


def extract_qa(path: Path, times: list[float]) -> None:
    qa = ROOT / "qa"
    qa.mkdir(exist_ok=True)
    for i, t in enumerate(times):
        dest = qa / f"f{i:02d}_{t:.2f}s.jpg"
        run(["ffmpeg", "-y", "-ss", f"{max(0, t):.3f}", "-i", str(path), "-frames:v", "1", "-q:v", "3", str(dest)])


def main() -> None:
    copy_assets()
    dur, cues = make_voiceover()
    for row in cues:
        print(f"  {row['start']:6.3f}-{row['end']:6.3f}  {row['text']}")
    data = build_timeline(cues, dur)
    render_broll(data)
    write_cover()
    staged = assemble(data)
    final_dur = probe_dur(staged)
    write_docs(final_dur, staged, data)
    report = qa(staged, data)
    mids = [((s["start"] + s["end"]) / 2) for s in data["shots"]]
    extract_qa(staged, [0.35] + mids + [max(0.05, final_dur - 0.40)])
    patch_index(final_dur)
    patch_delivery(final_dur)
    print("STAGED", staged, "dur", final_dur, "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
