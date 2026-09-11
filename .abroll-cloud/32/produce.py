# -*- coding: utf-8 -*-
"""Topic 32 / 选题库 011：注视增重。云端 A-roll + B-roll。

普通短视频 / 知识口播。假想定律：质量随被注视时间增加。
草稿只写 .abroll-cloud/32/，成品中转 成片/32-注视增重.mp4。
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

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path("/workspace/.abroll-cloud/32")
A_SRC = Path("/workspace/.abroll-cloud/06/assets")
W, H, FPS = 1080, 1920, 24
NAME = "注视增重"
STAGED_NAME = "32-注视增重.mp4"
VOICE = "zh-CN-YunyangNeural"
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_RG = "/tmp/NotoSansSC-Regular.otf"
FONT_FB = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

BG = (16, 12, 10)
CARD = (36, 28, 22)
AMBER = (232, 168, 72)
COPPER = (196, 112, 64)
GOLD = (245, 193, 92)
MINT = (126, 224, 197)
CYAN = (88, 214, 232)
WHITE = (245, 247, 250)
CREAM = (245, 247, 250)
MUTED = (154, 162, 176)
RED = (255, 118, 118)
WOOD = (92, 58, 36)
WOOD_DK = (58, 36, 22)
APPLE = (196, 48, 42)
APPLE_DK = (120, 28, 26)
LEAF = (62, 140, 78)
INK = (22, 20, 18)
FLOOR = (28, 24, 22)


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


def ease_in(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t


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
    cues_path = audio / "cues.json"

    if wav.exists() and wav.stat().st_size > 800 and cues_path.exists():
        dur = probe_dur(wav)
        cues = json.loads(cues_path.read_text(encoding="utf-8"))
        if len(cues) == len(phrases):
            print("reuse VO", wav, f"{dur:.3f}s")
            return dur, cues

    bounds = asyncio.run(synthesize_voice(text, mp3))
    (audio / "vo.vtt.json").write_text(json.dumps(bounds, ensure_ascii=False, indent=2), encoding="utf-8")
    run(["ffmpeg", "-y", "-i", str(mp3), "-ac", "1", "-ar", "44100", "-sample_fmt", "s16", str(wav)])
    dur = probe_dur(wav)
    cues = align_phrases(phrases, bounds, dur)
    lines = [f"{c['start']:.3f}\t{c['end']:.3f}\t{c['text']}" for c in cues]
    (audio / "vo-align.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    cues_path.write_text(json.dumps(cues, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("TTS", f"{dur:.3f}s", "cues", len(cues))
    return dur, cues


def split_caption(line: str) -> list[str]:
    line = line.strip("。．. ")
    if "，" in line and len(line) > 8:
        parts = [p for p in line.split("，") if p]
        if 1 < len(parts) <= 2:
            return parts
    if "：" in line and len(line) > 10:
        parts = [p for p in line.split("：") if p]
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
            pull = min(0.28, max(0.0, (shots[i - 1]["end"] - shots[i - 1]["start"]) - 0.55))
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
            color = list(AMBER) if shot["kind"] == "B" else list(CREAM)
            if i == len(shots) - 1:
                color = list(GOLD)
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
        "topic_id": "011",
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
        "cue_map": {c["text"]: [round(c["start"], 3), round(c["end"], 3)] for c in cues},
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
            0.055 * math.sin(2 * math.pi * 164.81 * t)
            + 0.038 * math.sin(2 * math.pi * 196.00 * t)
            + 0.026 * math.sin(2 * math.pi * 246.94 * t)
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
            samples[start + i] += env * 0.22 * math.sin(2 * math.pi * (380 + 620 * (i / length)) * t)
    path = ROOT / "audio/sfx.wav"
    write_wav_stereo(path, samples, sr)
    return path


# ---------- B-roll ----------
def new_b_bg() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    overlay = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(overlay)
    d.ellipse((-260, -300, 760, 620), fill=(48, 28, 14))
    d.ellipse((380, 1200, 1440, 2140), fill=(28, 16, 12))
    overlay = overlay.filter(ImageFilter.GaussianBlur(120))
    return Image.blend(img, overlay, 0.62)


def tag_chip(draw: ImageDraw.ImageDraw, t: float, label: str, color=AMBER) -> None:
    a = appear(t, 0.0, 0.22)
    if a <= 0:
        return
    fnt = font(30)
    tw, th = text_wh(draw, label, fnt)
    x, y = 84, 88
    rounded(draw, (x - 22, y - 14, x + tw + 22, y + th + 12), 22, mix(BG, (48, 32, 16), a))
    draw.text((x, y), label, font=fnt, fill=mix(BG, color, a))


def strike_line(draw, box, t: float, start: float) -> None:
    st = appear(t, start, 0.28)
    if st <= 0.04:
        return
    cy = (box[1] + box[3]) // 2
    x0, x1 = box[0] + 48, box[2] - 48
    draw.line([(x0, cy), (int(lerp(x0, x1, st)), cy)], fill=mix(CARD, RED, st), width=10)


def punch_bar(img: Image.Image, t: float, title: str, punch: str, start: float = 0.22) -> None:
    a = appear(t, start, 0.26)
    if a <= 0:
        return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y = 1480 + int((1 - a) * 24)
    d.rounded_rectangle((86, y, 994, y + 280), radius=34, fill=(16, 12, 10, int(228 * a)))
    d.text((540, y + 88), title, font=font(38), fill=(*mix(CARD, MUTED, a), 255), anchor="mm")
    d.text((540, y + 186), punch, font=font(58), fill=(*mix(CARD, AMBER, a), 255), anchor="mm")
    out = Image.alpha_composite(img.convert("RGBA"), layer)
    img.paste(out.convert("RGB"))


def draw_gaze(draw, cx: int, cy: int, t: float, n: int = 7) -> None:
    srcs = [(180, 80), (540, 40), (900, 80)]
    for sx, sy in srcs:
        fade = 0.18 + 0.12 * (0.5 + 0.5 * math.sin(t * 3.2 + sx))
        draw.line([(sx, sy), (cx, cy)], fill=mix(BG, AMBER, fade), width=3)
    r = int(28 + 8 * math.sin(t * 6))
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=mix(BG, GOLD, 0.55), width=3)


def render_b_law(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, sub_f = font(52), font(40), font(30)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "假想定律")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(18, 0, a0))), "被盯着越久", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        d.text((W // 2, 320 + int(lerp(18, 0, a0))), "东西越重", font=title_f, fill=mix(BG, AMBER, a0), anchor="mm")

        a1 = appear(t, 0.28)
        if a1 > 0.04:
            y = 400 + int(lerp(20, 0, a1))
            box = (90, y, 990, y + 220)
            rounded(d, box, 30, mix(BG, CARD, a1))
            d.text((540, y + 74), "质量固定不变", font=card_f, fill=mix(CARD, GOLD, a1), anchor="mm")
            d.text((540, y + 150), "看不看一个样", font=sub_f, fill=mix(CARD, MUTED, a1), anchor="mm")
            strike_line(d, box, t, 0.82)

        a2 = appear(t, 1.10)
        if a2 > 0.04:
            y = 670 + int(lerp(20, 0, a2))
            rounded(d, (90, y, 990, y + 240), 30, mix(BG, CARD, a2))
            d.text((540, y + 82), "注视时间加进质量", font=title_f, fill=mix(CARD, AMBER, a2), anchor="mm")
            d.text((540, y + 168), "盯得越久越重", font=sub_f, fill=mix(CARD, WHITE, a2), anchor="mm")

        punch = appear(t, min(1.90, max(0.9, duration - 1.05)), 0.26)
        if punch > 0.04:
            y = 980 + int(lerp(22, 0, punch))
            rounded(d, (160, y, 920, y + 180), 28, mix(BG, (48, 28, 14), punch))
            d.text((W // 2, y + 90), "假想定律", font=title_f, fill=mix(BG, GOLD, punch), anchor="mm")
        out.append(img)
    return out


def render_b_apple(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        p = ease_in(min(1.0, t / max(duration * 0.85, 0.01)))
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "钩子")

        # table
        table_y = 1180
        d.rectangle((0, table_y, W, H), fill=WOOD_DK)
        d.polygon([(40, table_y), (1040, table_y), (1080, 1320), (0, 1320)], fill=WOOD)
        d.line([(40, table_y), (1040, table_y)], fill=mix(WOOD, AMBER, 0.25), width=4)

        sink = int(lerp(0, 210, p))
        dent_w = int(lerp(90, 280, p))
        dent_h = int(lerp(18, 90, p))
        ax, ay = 540, table_y - 70 + sink
        d.ellipse((ax - dent_w, table_y - dent_h // 2, ax + dent_w, table_y + dent_h), fill=WOOD_DK)
        d.ellipse((ax - dent_w + 20, table_y - 8, ax + dent_w - 20, table_y + dent_h - 10), fill=mix(WOOD_DK, INK, 0.45))

        draw_gaze(d, ax, ay - 20, t)

        # apple
        ar = 92
        d.ellipse((ax - ar, ay - ar + 8, ax + ar, ay + ar + 8), fill=APPLE_DK)
        d.ellipse((ax - ar + 6, ay - ar, ax + ar - 10, ay + ar - 6), fill=APPLE)
        d.ellipse((ax - 36, ay - 58, ax - 4, ay - 22), fill=mix(APPLE, WHITE, 0.22))
        d.rectangle((ax - 5, ay - ar - 18, ax + 5, ay - ar + 8), fill=(72, 44, 28))
        d.ellipse((ax + 8, ay - ar - 28, ax + 48, ay - ar + 2), fill=LEAF)

        punch_bar(img, t, "盯着苹果", "压进桌面", start=0.14)
        out.append(img)
    return out


def _person(draw, x: int, y: int, scale: float, col, a: float) -> None:
    s = scale
    head_r = int(22 * s)
    draw.ellipse((x - head_r, y - int(110 * s) - head_r, x + head_r, y - int(110 * s) + head_r), fill=mix(BG, col, a))
    draw.rounded_rectangle(
        (x - int(28 * s), y - int(88 * s), x + int(28 * s), y - int(8 * s)),
        radius=12, fill=mix(BG, col, a),
    )
    draw.line([(x, y - int(8 * s)), (x - int(16 * s), y + int(28 * s))], fill=mix(BG, col, a), width=max(4, int(7 * s)))
    draw.line([(x, y - int(8 * s)), (x + int(16 * s), y + int(28 * s))], fill=mix(BG, col, a), width=max(4, int(7 * s)))


def render_b_crowd(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    spots = [(-210, 40), (210, 36), (-120, 70), (130, 74), (-280, 90), (280, 86), (0, 96), (-50, 50), (60, 48)]
    out = []
    for i in range(n):
        t = i / FPS
        p = ease_in(min(1.0, t / max(duration * 0.88, 0.01)))
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "后果 01")

        floor_y = 1280
        d.rectangle((0, floor_y, W, H), fill=FLOOR)
        sink = int(lerp(0, 240, p))
        shown = 2 + int(p * (len(spots) - 2))

        # vitrine
        cx, cy = 540, 720 + sink
        glass = mix(BG, (210, 220, 228), 0.35)
        d.rounded_rectangle((cx - 170, cy - 220, cx + 170, cy + 200), radius=16, outline=mix(BG, AMBER, 0.55), width=6)
        d.rectangle((cx - 160, cy - 210, cx + 160, cy + 190), fill=mix(BG, (28, 32, 40), 0.55))
        # artifact
        d.polygon([(cx - 40, cy + 40), (cx + 40, cy + 40), (cx + 28, cy - 70), (cx - 28, cy - 70)], fill=mix(BG, COPPER, 0.9))
        d.ellipse((cx - 36, cy - 92, cx + 36, cy - 48), fill=mix(BG, GOLD, 0.85))
        d.rectangle((cx - 180, cy + 190, cx + 180, cy + 220), fill=mix(BG, WOOD, 0.8))

        for k, (dx, dy) in enumerate(spots[:shown]):
            a = appear(t, 0.08 + k * 0.08, 0.22)
            _person(d, cx + dx, floor_y - 10 + dy, 0.92, MUTED if k % 2 else CREAM, a)

        # pit under case
        d.ellipse((cx - 200, floor_y - 20 + sink // 4, cx + 200, floor_y + 50 + sink // 3), fill=mix(FLOOR, INK, 0.7))

        punch_bar(img, t, "围观越密", "展柜越陷", start=0.12)
        out.append(img)
    return out


def render_b_mirror(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        p = ease_in(min(1.0, t / max(duration * 0.86, 0.01)))
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "后果 02")

        floor_y = 1320
        d.rectangle((0, floor_y, W, H), fill=FLOOR)

        # mirror frame
        mx0, my0, mx1, my1 = 430, 280, 980, 1280
        rounded(d, (mx0, my0, mx1, my1), 18, mix(BG, GOLD, 0.85))
        rounded(d, (mx0 + 22, my0 + 22, mx1 - 22, my1 - 22), 10, mix(BG, (28, 32, 40), 0.92))

        # real person (left)
        a = appear(t, 0.06)
        _person(d, 260, floor_y, 1.15, CREAM, a)

        # reflection: heavier / sinking
        rx = 705
        sink = int(lerp(0, 180, p))
        scale = lerp(1.15, 1.45, p)
        _person(d, rx, floor_y - 40 + sink, scale, mix(CREAM, COPPER, 0.45), a)
        draw_gaze(d, rx, floor_y - 160 + sink, t, n=5)

        if p > 0.35:
            cr = appear(t, duration * 0.35, 0.3)
            col = mix(FLOOR, GOLD, cr)
            cy = floor_y + 20
            d.line([(rx - 80, cy), (rx - 10, cy + 40), (rx + 90, cy + 10)], fill=col, width=6)
            d.line([(rx - 10, cy + 40), (rx + 20, cy + 90)], fill=col, width=4)
            d.line([(rx + 40, cy + 8), (rx + 120, cy + 70)], fill=mix(FLOOR, RED, cr * 0.8), width=4)

        punch_bar(img, t, "镜子里的自己", "越来越重", start=0.12)
        out.append(img)
    return out


def render_b_frame(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        p = ease_in(min(1.0, t / max(duration * 0.88, 0.01)))
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "回报")

        wall_a = appear(t, 0.02)
        d.rectangle((0, 220, W, 1480), fill=mix(BG, (42, 34, 30), wall_a * 0.55))
        floor_y = 1480
        d.rectangle((0, floor_y, W, H), fill=mix(BG, FLOOR, wall_a))
        d.line([(0, floor_y), (W, floor_y)], fill=mix(FLOOR, AMBER, 0.25), width=4)

        # abstract painting + gold frame (not a real artwork)
        sink = int(lerp(0, 520, p))
        fx0, fy0, fx1, fy1 = 220, 360 + sink, 860, 1180 + sink
        d.rectangle((fx0, fy0, fx1, fy1), fill=mix(BG, GOLD, 0.9))
        d.rectangle((fx0 + 28, fy0 + 28, fx1 - 28, fy1 - 28), fill=mix(BG, (48, 36, 72), 0.95))
        d.ellipse((340, 520 + sink, 620, 820 + sink), fill=mix((48, 36, 72), COPPER, 0.7))
        d.polygon([(480, 460 + sink), (720, 700 + sink), (300, 760 + sink)], fill=mix((48, 36, 72), AMBER, 0.45))

        # floor occludes the sunk part
        d.rectangle((0, floor_y, W, H), fill=FLOOR)
        d.line([(0, floor_y), (W, floor_y)], fill=mix(FLOOR, AMBER, 0.35), width=5)

        # remaining top rail if sunk far enough
        if fy0 < floor_y:
            visible_bottom = min(fy1, floor_y)
            if visible_bottom > fy0:
                d.rectangle((fx0, fy0, fx1, min(fy0 + 36, visible_bottom)), fill=mix(BG, GOLD, 0.95))

        punch_bar(img, t, "最有名的那幅画", "只露画框上沿", start=min(0.9, max(0.2, duration - 1.5)))
        out.append(img)
    return out


def render_broll(data: dict) -> None:
    durs = {}
    for shot in data["shots"]:
        if shot["kind"] == "B":
            durs[shot["src"]] = max(1.5, float(shot["end"]) - float(shot["start"]))
    jobs = [
        ("broll/B-定律.mp4", render_b_law),
        ("broll/B-苹果.mp4", render_b_apple),
        ("broll/B-围观.mp4", render_b_crowd),
        ("broll/B-镜子.mp4", render_b_mirror),
        ("broll/B-画框.mp4", render_b_frame),
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
    d.rectangle((76, 88, 120, 92), fill=(*AMBER, 230))
    d.text((136, 78), label, font=font(22), fill=(90, 98, 108, 220))


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
    pd.rectangle((10, 14, 20, box_h - 14), fill=(*AMBER, 235))
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
        "[2:a]adelay=800|800,volume=0.16,highpass=f=140[bg];"
        "[3:a]volume=0.28[sfx];"
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
    frames = render_b_apple(2.4)
    img = frames[min(28, len(frames) - 1)].copy()
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rounded_rectangle((70, 160, 1010, 640), radius=40, fill=(12, 10, 8, 216))
    img = Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")
    d = ImageDraw.Draw(img)
    d.text((540, 260), "盯着苹果", font=font(86), fill=WHITE, anchor="mm")
    d.text((540, 390), "压进桌面", font=font(64), fill=AMBER, anchor="mm")
    d.text((540, 520), "假想定律 · 注视增重", font=font(36), fill=GOLD, anchor="mm")
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
        "project_name": "32_注视增重",
        "video_type": "普通短视频",
        "episode": 32,
        "topic_id": "011",
        "source_note": "选题库.md #011 / 质量随注视增加",
        "title": NAME,
        "stage": "delivered",
        "status": "已交付",
        "current_stage": "核验并交付",
        "production_method": "白底小灯 A-roll（06 已有动作）+ 黑底注视增重信息图 B-roll + edge-tts Yunyang + FFmpeg",
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
        "siblings_avoided": ["002", "003", "005", "006", "007", "008", "009", "010"],
        "updated_at": now,
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    explain = f"""# 32 · 注视增重

普通短视频 / 知识口播。**不是**剧情短剧，不走 drama-pipeline。

- **选题**：Drive `选题库.md` 第 **011** 号 · 质量随被注视时间增加（`topics-batch2.md` #32）
- **结构**：片头标明假想定律 → 钩子（苹果压进桌面）→ 三个后果（围观下沉 / 镜子增重 / 名作更深）→ 画框上沿回报
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/32/`
- **云端 only**：未写 `C:\\` / `D:\\` / `G:\\`，未上传 Drive

钩子：盯着苹果，苹果压进桌面。  
收束：最有名的那幅画整幅沉进地板，只露画框上沿。

白底小灯 A-roll + 黑底注视增重信息图 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {dur:.2f} 秒。镜头 {len(data["shots"])} 条，时间轴闭合。
"""
    (ROOT / "项目说明.md").write_text(explain, encoding="utf-8")


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
    (qa_dir / "ffprobe.json").write_text(probe, encoding="utf-8")
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
        "project": "32_注视增重",
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
            "b_shots": sum(1 for s in shots if s["kind"] == "B"),
            "a_shots": sum(1 for s in shots if s["kind"] == "A"),
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
        and report["timeline"]["b_shots"] >= 3
        and report["timeline"]["a_shots"] >= 2
    )
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def copy_assets() -> None:
    assets = ROOT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    src_root = A_SRC if A_SRC.exists() else Path("/workspace/.abroll-cloud/29/assets")
    for name in ("V-挥手.mp4", "V-摊手.mp4", "V-指向.mp4", "A-角色-小灯-摊手.jpg"):
        src = src_root / name
        if not src.exists():
            raise FileNotFoundError(src)
        dest = assets / name
        if not dest.exists() or dest.stat().st_size != src.stat().st_size:
            shutil.copy2(src, dest)


def main() -> None:
    copy_assets()
    dur, cues = make_voiceover()
    for row in cues:
        print(f"  {row['start']:6.3f}-{row['end']:6.3f}  {row['text']}")
    data = build_timeline(cues, dur)
    render_broll(data)
    write_cover()
    staged = assemble(data)
    dur_final = probe_dur(staged)
    write_docs(dur_final, staged, data)
    patch_index(dur_final)
    report = qa(staged, data)
    print("STAGED", staged, "dur", dur_final, "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))
    print("DONE", staged)


if __name__ == "__main__":
    main()
