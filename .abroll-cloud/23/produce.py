# -*- coding: utf-8 -*-
"""Topic 23 / 选题库 005：声音可以被看见。云端 A-roll + B-roll。

普通短视频 / 知识口播。改一条定律 → 三个后果 → 空屋回报。
草稿只写 .abroll-cloud/23/，成品中转 成片/23-*.mp4。
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

ROOT = Path("/workspace/.abroll-cloud/23")
A_SRC = Path("/workspace/.abroll-cloud/06/assets")
W, H, FPS = 1080, 1920, 24
NAME = "说话时嘴前有涟漪"
STAGED_NAME = "23-说话时嘴前有涟漪.mp4"
VOICE = "zh-CN-YunyangNeural"
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_RG = "/tmp/NotoSansSC-Regular.otf"
FONT_FB = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

BG = (8, 10, 18)
CARD = (20, 24, 38)
MINT = (126, 224, 197)
CYAN = (88, 214, 232)
ICE = (164, 220, 236)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
CREAM = (245, 247, 250)
MUTED = (154, 162, 176)
RED = (255, 118, 118)
VIOLET = (132, 118, 214)
NAVY = (18, 28, 56)
INK = (16, 18, 28)


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
            if shot["kind"] == "B":
                color = list(CYAN)
            else:
                color = list(CREAM)
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
        "topic_id": "005",
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
            0.055 * math.sin(2 * math.pi * 174.61 * t)
            + 0.04 * math.sin(2 * math.pi * 220.0 * t)
            + 0.028 * math.sin(2 * math.pi * 261.63 * t)
            + 0.016 * math.sin(2 * math.pi * 329.63 * t)
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
            samples[start + i] += env * 0.22 * math.sin(2 * math.pi * (520 + 760 * (i / length)) * t)
    path = ROOT / "audio/sfx.wav"
    write_wav_stereo(path, samples, sr)
    return path


# ---------- B-roll ----------
def new_b_bg() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    overlay = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(overlay)
    d.ellipse((-280, -340, 780, 640), fill=(12, 36, 52))
    d.ellipse((360, 1180, 1420, 2160), fill=(28, 18, 52))
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


def draw_rings(draw, cx: int, cy: int, t: float, *, n: int = 5, speed: float = 140.0,
               max_r: float = 420.0, color=CYAN, width: int = 5, frozen: bool = False) -> None:
    for k in range(n):
        if frozen:
            r = int(70 + k * 58)
            fade = 0.55 - k * 0.07
        else:
            phase = (t * speed + k * (max_r / n)) % (max_r + 50)
            r = int(phase)
            fade = max(0.0, 1.0 - phase / (max_r + 50))
        if r < 10 or fade <= 0.04:
            continue
        col = mix(BG, color, fade)
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=width)


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
    d.rounded_rectangle((86, y, 994, y + 280), radius=34, fill=(12, 16, 26, int(228 * a)))
    d.text((540, y + 88), title, font=font(38), fill=(*mix(CARD, MUTED, a), 255), anchor="mm")
    d.text((540, y + 186), punch, font=font(58), fill=(*mix(CARD, CYAN, a), 255), anchor="mm")
    out = Image.alpha_composite(img.convert("RGBA"), layer)
    img.paste(out.convert("RGB"))


def render_b_law(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, sub_f = font(56), font(40), font(30)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        draw_rings(d, 540, 980, t, n=6, speed=150, max_r=520, color=CYAN, width=4)
        tag_chip(d, t, "改一条定律")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(18, 0, a0))), "声音可以被看见", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        a1 = appear(t, 0.26)
        if a1 > 0.04:
            y = 340 + int(lerp(20, 0, a1))
            box = (90, y, 990, y + 220)
            rounded(d, box, 30, mix(BG, CARD, a1))
            d.text((540, y + 74), "声音只进耳朵", font=card_f, fill=mix(CARD, YELLOW, a1), anchor="mm")
            d.text((540, y + 150), "空气里什么都没有", font=sub_f, fill=mix(CARD, MUTED, a1), anchor="mm")
            strike_line(d, box, t, 0.78)

        a2 = appear(t, 1.05)
        if a2 > 0.04:
            y = 600 + int(lerp(20, 0, a2))
            rounded(d, (90, y, 990, y + 240), 30, mix(BG, CARD, a2))
            d.text((540, y + 82), "声纹写在空气里", font=title_f, fill=mix(CARD, CYAN, a2), anchor="mm")
            d.text((540, y + 168), "涟漪、冲击、静纹", font=sub_f, fill=mix(CARD, WHITE, a2), anchor="mm")

        punch = appear(t, min(1.85, max(0.9, duration - 1.05)), 0.26)
        if punch > 0.04:
            y = 980 + int(lerp(22, 0, punch))
            rounded(d, (160, y, 920, y + 180), 28, mix(BG, (18, 42, 48), punch))
            d.text((W // 2, y + 90), "看得见", font=title_f, fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_b_ripples(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "后果 01")
        cx, cy = 540, 720
        draw_rings(d, cx, cy + 40, t, n=7, speed=170, max_r=480, color=CYAN, width=6)
        draw_rings(d, cx, cy + 40, t + 0.18, n=4, speed=130, max_r=360, color=ICE, width=3)

        a = appear(t, 0.08)
        head = mix(BG, (36, 40, 52), a)
        d.ellipse((cx - 92, cy - 150, cx + 92, cy + 70), fill=head)
        d.ellipse((cx - 28, cy - 40, cx + 28, cy + 8), fill=mix(head, INK, a))
        # mouth opening as sound source
        mouth = mix(head, CYAN, 0.35 + 0.25 * (0.5 + 0.5 * math.sin(t * 8)))
        d.ellipse((cx - 36, cy + 18, cx + 36, cy + 58), fill=mouth)

        punch_bar(img, t, "说话时", "嘴前有涟漪", start=0.16)
        out.append(img)
    return out


def render_b_shock(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    src = (220, 980)
    glass = (780, 720)
    hit_r = 560
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "后果 02")

        # expanding shock from floor impact
        r = int(40 + t * 280)
        fade = max(0.15, 1.0 - t / max(duration, 0.01) * 0.35)
        d.ellipse((src[0] - r, src[1] - r, src[0] + r, src[1] + r), outline=mix(BG, CYAN, fade), width=7)
        r2 = int(max(0, r - 70))
        if r2 > 16:
            d.ellipse((src[0] - r2, src[1] - r2, src[0] + r2, src[1] + r2), outline=mix(BG, ICE, fade * 0.7), width=4)

        # glass silhouette — intact until wave arrives
        gx, gy = glass
        a = appear(t, 0.06)
        body = mix(BG, (210, 224, 232), a * 0.88)
        d.polygon(
            [(gx - 70, gy - 160), (gx + 78, gy - 150), (gx + 62, gy + 150), (gx - 86, gy + 158)],
            outline=body,
        )
        d.line([(gx - 70, gy - 160), (gx + 78, gy - 150), (gx + 62, gy + 150), (gx - 86, gy + 158), (gx - 70, gy - 160)], fill=body, width=6)
        d.line([(gx - 10, gy - 140), (gx + 8, gy + 130)], fill=mix(BG, ICE, a * 0.7), width=3)

        arrived = r >= hit_r - 80
        if arrived:
            crack_a = appear(t, 1.05, 0.18)
            cr = mix(BG, YELLOW, crack_a)
            d.line([(gx - 8, gy - 40), (gx + 24, gy + 10), (gx - 18, gy + 70)], fill=cr, width=5)
            d.line([(gx + 24, gy + 10), (gx + 52, gy + 36)], fill=cr, width=3)
            d.text((gx, gy + 210), "才裂", font=font(36), fill=mix(BG, YELLOW, crack_a), anchor="mm")
        else:
            d.text((gx, gy + 210), "还没碎", font=font(36), fill=mix(BG, MUTED, a), anchor="mm")

        d.ellipse((src[0] - 18, src[1] - 10, src[0] + 18, src[1] + 16), fill=mix(BG, CYAN, 0.8))
        punch_bar(img, t, "杯子还没碎", "冲击波已经到了", start=0.12)
        out.append(img)
    return out


def render_b_city(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    sources = [(180, 420), (900, 380), (300, 980), (820, 1100), (540, 560)]
    house = (430, 1240, 650, 1540)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "回报")
        a0 = appear(t, 0.02)
        d.text((W // 2, 236 + int(lerp(14, 0, a0))), "天空铺满声纹", font=font(52), fill=mix(BG, WHITE, a0), anchor="mm")

        # crossing city soundscape
        for si, (sx, sy) in enumerate(sources):
            draw_rings(
                d, sx, sy, t + si * 0.11,
                n=4, speed=120 + si * 8, max_r=380,
                color=CYAN if si % 2 == 0 else VIOLET, width=3,
            )

        # skyline
        sky_a = appear(t, 0.18)
        if sky_a > 0.04:
            base_y = 1180
            d.rectangle((0, base_y, W, H), fill=mix(BG, NAVY, sky_a * 0.55))
            for bx, bw, bh in ((40, 90, 160), (150, 70, 220), (240, 110, 140), (680, 80, 200), (780, 130, 170), (930, 90, 240)):
                d.rectangle((bx, base_y - bh, bx + bw, base_y + 20), fill=mix(NAVY, (28, 36, 58), sky_a))

        # quiet house — no rings inside
        ha = appear(t, min(1.15, max(0.7, duration * 0.42)), 0.28)
        if ha > 0.04:
            x0, y0, x1, y1 = house
            rounded(d, (x0, y0, x1, y1), 18, mix(NAVY, (8, 10, 16), ha))
            d.polygon([(x0 - 16, y0 + 8), ((x0 + x1) // 2, y0 - 70), (x1 + 16, y0 + 8)], fill=mix(NAVY, (22, 24, 32), ha))
            d.rectangle((x0 + 70, y0 + 90, x1 - 70, y1 - 40), fill=mix((8, 10, 16), INK, ha))
            d.text(((x0 + x1) // 2, y1 + 36), "空屋", font=font(36), fill=mix(BG, YELLOW, ha), anchor="mm")

        punch_bar(img, t, "最安静的一块", "是一间空屋", start=min(1.35, max(0.85, duration - 1.4)))
        out.append(img)
    return out


def render_broll(data: dict) -> None:
    durs = {}
    for shot in data["shots"]:
        if shot["kind"] == "B":
            durs[shot["src"]] = max(1.5, float(shot["end"]) - float(shot["start"]))
    jobs = [
        ("broll/B-定律.mp4", render_b_law),
        ("broll/B-涟漪.mp4", render_b_ripples),
        ("broll/B-冲击波.mp4", render_b_shock),
        ("broll/B-空屋.mp4", render_b_city),
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
    img = new_b_bg()
    d = ImageDraw.Draw(img)
    draw_rings(d, 540, 980, 1.4, n=6, speed=0.0001, max_r=1, color=CYAN, width=6, frozen=True)
    draw_rings(d, 540, 980, 0.0, n=5, speed=0.0001, max_r=1, color=ICE, width=3, frozen=True)
    d.ellipse((500, 930, 580, 1010), fill=mix(BG, CYAN, 0.85))
    d.rounded_rectangle((70, 160, 1010, 620), radius=40, fill=(10, 14, 22))
    d.text((540, 260), "说话时", font=font(86), fill=WHITE, anchor="mm")
    d.text((540, 380), "嘴前有涟漪", font=font(64), fill=CYAN, anchor="mm")
    d.text((540, 500), "声音可以被看见", font=font(36), fill=YELLOW, anchor="mm")
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    img.save(ROOT / "final" / "cover.jpg", quality=92)
    return dest


def write_docs(dur: float, staged: Path) -> None:
    vo = (ROOT / "script/voiceover.txt").read_text(encoding="utf-8").strip()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    status = {
        "schema_version": 1,
        "project_name": "23_说话时嘴前有涟漪",
        "video_type": "普通短视频",
        "topic_id": "005",
        "source_note": "选题库.md #005 / 声音可以被看见",
        "title": NAME,
        "stage": "delivered",
        "status": "已交付",
        "current_stage": "核验并交付",
        "production_method": "白底小灯 A-roll（06 已有动作）+ 黑底声纹信息图 B-roll + edge-tts Yunyang + FFmpeg",
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
        "not": "剧情短剧 / drama-pipeline / Drive 上传 / C: D: G:",
        "siblings_avoided": ["002", "006", "007", "009", "010"],
        "updated_at": now,
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    explain = f"""# 23 · 说话时，嘴前有涟漪

普通短视频 / 知识口播。**不是**剧情短剧，不走 drama-pipeline。

- **选题**：Drive `选题库.md` 第 **005** 号 · 声音可以被看见
- **结构**：改一条定律 → 三个后果（涟漪 / 冲击波先到 / 静纹）→ 空屋回报
- **成片中转**：`成片/23-说话时嘴前有涟漪.mp4`
- **本集工程成片**：`00_最终成片_说话时嘴前有涟漪.mp4`
- **草稿根**：`/workspace/.abroll-cloud/23/`
- **云端 only**：未写 `C:\\` / `D:\\` / `G:\\`，未上传 Drive

钩子：说话时，嘴前有涟漪。  
收束：最安静的一块，是一间空屋。

白底小灯 A-roll + 黑底声纹信息图 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {dur:.2f} 秒。
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


def main() -> None:
    copy_assets()
    dur, cues = make_voiceover()
    data = build_timeline(cues, dur)
    render_broll(data)
    write_cover()
    staged = assemble(data)
    write_docs(probe_dur(staged), staged)
    print("DONE", staged)


if __name__ == "__main__":
    main()
