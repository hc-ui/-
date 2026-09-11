# -*- coding: utf-8 -*-
"""Topic 22 / 选题 008：松油门车子瞬间停住。云端 A-roll + B-roll。"""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path("/workspace/.abroll-cloud/22")
W, H, FPS = 1080, 1920, 24
NAME = "松油门车子瞬间停住"
VOICE = "zh-CN-YunyangNeural"
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_RG = "/tmp/NotoSansSC-Regular.otf"
FONT_FB = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

BG = (11, 13, 18)
CARD = (24, 28, 38)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
CREAM = (245, 247, 250)
MUTED = (154, 162, 176)
RED = (255, 118, 118)
INK = (28, 32, 36)
B_LEAD = 0.20


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


def new_b_bg() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    overlay = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(overlay)
    d.ellipse((-220, -280, 720, 560), fill=(16, 42, 38))
    d.ellipse((480, 1180, 1400, 2100), fill=(42, 32, 16))
    overlay = overlay.filter(ImageFilter.GaussianBlur(110))
    return Image.blend(img, overlay, 0.58)


def tag_chip(draw: ImageDraw.ImageDraw, t: float, label: str) -> None:
    a = appear(t, 0.0, 0.22)
    if a <= 0:
        return
    fnt = font(32)
    tw, th = text_wh(draw, label, fnt)
    x, y = 84, 88
    rounded(draw, (x - 22, y - 14, x + tw + 22, y + th + 12), 22, mix(BG, (20, 42, 38), a))
    draw.text((x, y), label, font=fnt, fill=mix(BG, MINT, a))


def strike_line(draw, box, t: float, start: float) -> None:
    st = appear(t, start, 0.28)
    if st <= 0.04:
        return
    cy = (box[1] + box[3]) // 2
    x0, x1 = box[0] + 48, box[2] - 48
    draw.line([(x0, cy), (int(lerp(x0, x1, st)), cy)], fill=mix(CARD, RED, st), width=10)


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
    lines = [f"[{int(c['start'] * 1000)}ms-{int(c['end'] * 1000)}ms] {c['text']}" for c in cues]
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
            pull = min(B_LEAD, max(0.0, (shots[i - 1]["end"] - shots[i - 1]["start"]) - 0.55))
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
                color = [126, 224, 197]
            else:
                color = [245, 247, 250]
            if i == len(shots) - 1:
                color = [245, 193, 92]
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
    }
    (ROOT / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("timeline", dur, "shots", len(shots))
    return data


def make_bgm(duration: float) -> Path:
    dest = ROOT / "audio/bgm.wav"
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=196:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=247:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=294:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-filter_complex",
        "[0:a]volume=0.12[a];[1:a]volume=0.08[b];[2:a]volume=0.06[c];"
        "[a][b][c]amix=inputs=3:duration=longest,lowpass=f=520,alimiter=limit=0.35",
        "-ac", "2", "-ar", "44100", str(dest),
    ])
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


def render_b_law(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, sub_f = font(56), font(40), font(30)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "改一条定律")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(20, 0, a0))), "惯性消失", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        a1 = appear(t, 0.28)
        box = (90, 0, 990, 0)
        if a1 > 0.04:
            y = 360 + int(lerp(22, 0, a1))
            box = (90, y, 990, y + 240)
            rounded(d, box, 32, mix(BG, CARD, a1))
            d.text((540, y + 80), "松了还会滑一阵", font=card_f, fill=mix(CARD, YELLOW, a1), anchor="mm")
            d.text((540, y + 160), "力没了还往前冲", font=sub_f, fill=mix(CARD, MUTED, a1), anchor="mm")
            strike_line(d, box, t, 0.85)

        a2 = appear(t, 1.15)
        if a2 > 0.04:
            y = 660 + int(lerp(22, 0, a2))
            rounded(d, (90, y, 990, y + 260), 32, mix(BG, CARD, a2))
            d.text((540, y + 90), "撤力即停", font=title_f, fill=mix(CARD, MINT, a2), anchor="mm")
            d.text((540, y + 180), "没有惯性可借", font=sub_f, fill=mix(CARD, WHITE, a2), anchor="mm")

        punch = appear(t, min(2.05, max(0.9, duration - 1.1)), 0.28)
        if punch > 0.04:
            y = 1040 + int(lerp(24, 0, punch))
            rounded(d, (140, y, 940, y + 200), 30, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y + 100), "不是减速", font=title_f, fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_b_snap(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, sub_f = font(52), font(42), font(30)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "对照")
        a0 = appear(t, 0.02)
        d.text((W // 2, 236 + int(lerp(16, 0, a0))), "不是减速", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        # motion bar: slides then snaps
        track = (120, 320, 960, 420)
        rounded(d, track, 24, mix(BG, (20, 24, 32), appear(t, 0.08)))
        if t < 0.70:
            px = int(lerp(160, 820, min(1.0, t / 0.70)))
        else:
            px = 820
        d.rounded_rectangle((px, 340, px + 90, 400), radius=14, fill=YELLOW if t < 0.70 else MINT)

        a1 = appear(t, 0.55)
        y = 480 + int(lerp(22, 0, a1))
        box = (90, y, 990, y + 240)
        rounded(d, box, 32, mix(BG, CARD, a1))
        d.text((540, y + 80), "慢慢刹住", font=card_f, fill=mix(CARD, YELLOW, a1), anchor="mm")
        d.text((540, y + 160), "还有滑行", font=sub_f, fill=mix(CARD, MUTED, a1), anchor="mm")
        strike_line(d, box, t, 1.05)

        a2 = appear(t, 1.25)
        if a2 > 0.04:
            y2 = 780 + int(lerp(22, 0, a2))
            rounded(d, (90, y2, 990, y2 + 260), 32, mix(BG, (22, 40, 36), a2))
            d.text((540, y2 + 90), "即刻停", font=title_f, fill=mix(CARD, MINT, a2), anchor="mm")
            d.text((540, y2 + 180), "零帧过渡", font=sub_f, fill=mix(CARD, WHITE, a2), anchor="mm")

        punch = appear(t, min(2.0, max(1.4, duration - 0.9)), 0.26)
        if punch > 0.04:
            y3 = 1140 + int(lerp(20, 0, punch))
            rounded(d, (140, y3, 940, y3 + 180), 28, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y3 + 90), "是即刻停", font=title_f, fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def punch_bar(base: Image.Image, t: float, title: str, punch: str) -> None:
    a = appear(t, 0.18, 0.28)
    if a <= 0:
        return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y = 1420 + int((1 - a) * 28)
    d.rounded_rectangle((90, y, 990, y + 280), radius=36, fill=(16, 18, 24, int(230 * a)))
    d.text((540, y + 90), title, font=font(40), fill=(*mix(CARD, MUTED, a), 255), anchor="mm")
    d.text((540, y + 190), punch, font=font(64), fill=(*mix(CARD, WHITE, a), 255), anchor="mm")
    out = Image.alpha_composite(base.convert("RGBA"), layer)
    base.paste(out.convert("RGB"))


def render_b_still(src: Path, duration: float, tag: str, title: str, punch: str) -> list[Image.Image]:
    still = Image.open(src).convert("RGB")
    still = ImageEnhance.Brightness(still).enhance(0.94)
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        p = t / max(duration, 0.01)
        img = cover(still, W, H, zoom=1.04 + 0.08 * p, pan_y=-0.04 + 0.08 * p)
        shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shade)
        for y in range(0, 180):
            sd.line([(0, y), (W, y)], fill=(8, 10, 14, int(90 * (1 - y / 180))))
        for y in range(H - 560, H):
            sd.line([(0, y), (W, y)], fill=(8, 10, 14, int(200 * ((y - (H - 560)) / 560))))
        img = Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")
        d = ImageDraw.Draw(img)
        tag_chip(d, t, tag)
        punch_bar(img, t, title, punch)
        out.append(img)
    return out


def render_b_motion_car(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "钩子")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(16, 0, a0))), "松油门", font=font(56), fill=mix(BG, WHITE, a0), anchor="mm")
        road_y = 860
        d.rectangle((80, road_y, 1000, road_y + 180), fill=mix(BG, (28, 30, 36), appear(t, 0.1)))
        d.line([(80, road_y + 90), (1000, road_y + 90)], fill=mix(BG, YELLOW, 0.5), width=6)
        if t < 0.85:
            cx = int(lerp(180, 780, min(1.0, t / 0.85)))
            col = YELLOW
        else:
            cx = 780
            col = MINT
        d.rounded_rectangle((cx, road_y + 30, cx + 160, road_y + 140), radius=20, fill=col)
        punch = appear(t, 1.05, 0.26)
        if punch > 0.04:
            y = 1180 + int(lerp(20, 0, punch))
            rounded(d, (140, y, 940, y + 200), 30, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y + 100), "车子瞬间停住", font=font(52), fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_b_motion_drop(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "后果 01")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(16, 0, a0))), "脱手的东西", font=font(52), fill=mix(BG, WHITE, a0), anchor="mm")
        hand_y = 420
        d.ellipse((470, hand_y, 610, hand_y + 80), fill=mix(BG, MUTED, appear(t, 0.1)))
        if t < 0.35:
            by = hand_y + 90
        else:
            by = int(lerp(hand_y + 90, 1180, min(1.0, (t - 0.35) / 0.7)))
        d.ellipse((500, by, 580, by + 80), fill=mix(BG, RED, 1.0))
        punch = appear(t, 1.05, 0.26)
        if punch > 0.04:
            y = 1380 + int(lerp(20, 0, punch))
            rounded(d, (140, y, 940, y + 180), 28, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y + 90), "垂直掉下去", font=font(52), fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_b_motion_street(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "回报")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(16, 0, a0))), "整条街", font=font(56), fill=mix(BG, WHITE, a0), anchor="mm")
        # stop-motion blocks: jump then freeze
        phase = 0 if t < 0.55 else (1 if t < 1.05 else 2)
        xs = [160, 360, 560, 760]
        for k, x in enumerate(xs):
            y = 720 + (40 if (phase == 0 and k % 2) else 0) + (0 if phase else int(12 * math.sin(t * 18 + k)))
            col = MINT if phase >= 2 else (YELLOW if phase == 1 else MUTED)
            rounded(d, (x, y, x + 140, y + 220), 18, mix(BG, col, appear(t, 0.12)))
        punch = appear(t, min(1.4, max(1.0, duration - 0.85)), 0.26)
        if punch > 0.04:
            y = 1180 + int(lerp(20, 0, punch))
            rounded(d, (100, y, 980, y + 220), 30, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y + 110), "开始停都是瞬间", font=font(48), fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_broll(data: dict) -> None:
    durs = {}
    for shot in data["shots"]:
        if shot["kind"] == "B":
            durs[shot["src"]] = max(1.4, float(shot["end"]) - float(shot["start"]))

    jobs = {
        "broll/B-定律.mp4": lambda d: render_b_law(d),
        "broll/B-即刻.mp4": lambda d: render_b_snap(d),
    }
    still_jobs = {
        "broll/B-车停.mp4": (ROOT / "assets/t22a-car-instant-stop.png", "钩子", "松油门", "车子瞬间停住", render_b_motion_car),
        "broll/B-脱手.mp4": (ROOT / "assets/t22b-object-drop-vertical.png", "后果 01", "脱手的东西", "垂直掉下去", render_b_motion_drop),
        "broll/B-街道.mp4": (ROOT / "assets/t22d-street-stopmotion.png", "回报", "整条街", "开始停都是瞬间", render_b_motion_street),
    }
    for rel, fn in jobs.items():
        dur = durs.get(rel)
        if not dur:
            raise SystemExit(f"no duration for {rel}")
        print("render", rel, f"{dur:.2f}s")
        frames_to_mp4(fn(dur + 0.12), ROOT / rel)

    for rel, (src, tag, title, punch, fallback) in still_jobs.items():
        dur = durs.get(rel)
        if not dur:
            raise SystemExit(f"no duration for {rel}")
        print("render", rel, f"{dur:.2f}s", "still" if src.exists() else "motion")
        if src.exists():
            frames = render_b_still(src, dur + 0.12, tag, title, punch)
        else:
            frames = fallback(dur + 0.12)
        frames_to_mp4(frames, ROOT / rel)


def kenburns_still(src: Path, dest: Path, dur: float, close: bool) -> None:
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
    run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(src),
        "-t", f"{dur:.3f}", "-vf", vf, "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        str(dest),
    ])


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
        if shot["kind"] == "A" and src.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            kenburns_still(src, dest, dur, bool(shot.get("close")))
        else:
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
    backup = ROOT / "output" / f"{NAME}.mp4"
    backup.parent.mkdir(exist_ok=True)
    shutil.copy2(final, backup)
    (ROOT / "final").mkdir(exist_ok=True)
    shutil.copy2(final, ROOT / "final" / f"{NAME}.mp4")
    staged = Path("/workspace/成片") / f"22-{NAME}.mp4"
    staged.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(final, staged)
    print("FINAL", final, "dur", probe_dur(final))
    print("STAGED", staged, "dur", probe_dur(staged))
    return staged


def write_cover(data: dict) -> Path:
    dest = ROOT / f"00_封面_{NAME}.jpg"
    src = ROOT / data["cover"]["src"]
    if src.exists():
        still = Image.open(src).convert("RGB")
        img = cover(still, W, H, zoom=1.08, pan_y=-0.02)
    else:
        img = new_b_bg()
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rounded_rectangle((70, 160, 1010, 620), radius=40, fill=(10, 12, 16, 210))
    img = Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")
    d = ImageDraw.Draw(img)
    d.text((540, 260), "松油门", font=font(86), fill=WHITE, anchor="mm")
    d.text((540, 380), "车子瞬间停住", font=font(58), fill=YELLOW, anchor="mm")
    d.text((540, 500), "惯性消失 · 撤力即停", font=font(36), fill=MINT, anchor="mm")
    img.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    img.save(ROOT / "final/cover.jpg", quality=92)
    return dest


def write_status(dur: float, staged: Path) -> None:
    vo = (ROOT / "script/voiceover.txt").read_text(encoding="utf-8").strip()
    status = {
        "schema_version": 1,
        "project_name": "22_松油门车子瞬间停住",
        "video_type": "普通短视频",
        "topic_index": 22,
        "topic_id": "008",
        "title": "松油门车子瞬间停住",
        "stage": "delivered",
        "production_method": "白底小灯 A-roll + 黑底对照卡/无字静帧 B-roll + edge-tts Yunyang + FFmpeg",
        "voice": VOICE,
        "duration": round(dur, 3),
        "size": [W, H],
        "fps": FPS,
        "script": {"path": "script/voiceover.txt", "sha256": hashlib.sha256(vo.encode("utf-8")).hexdigest()},
        "staged": str(staged),
        "project_final": f"00_最终成片_{NAME}.mp4",
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    for need in (
        ROOT / "assets/V-挥手.mp4",
        ROOT / "assets/V-摊手.mp4",
        ROOT / "assets/V-指向.mp4",
    ):
        if not need.exists():
            raise FileNotFoundError(need)

    dur, cues = make_voiceover()
    for c in cues:
        print(f"  {c['start']:6.3f}-{c['end']:6.3f}  {c['text']}")
    data = build_timeline(cues, dur)
    render_broll(data)
    write_cover(data)
    staged = assemble(data)
    write_status(dur, staged)
    print("DONE", staged)


if __name__ == "__main__":
    main()
