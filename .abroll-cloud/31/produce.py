# -*- coding: utf-8 -*-
"""Topic 31 / 选题库 012：贴地冻雨。云端 A-roll + B-roll。

普通短视频 / 知识口播。改一条定律 → 三个后果 → 琥珀城回报。
草稿只写 .abroll-cloud/31/，成品中转 成片/31-贴地冻雨.mp4。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
"""
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

ROOT = Path("/workspace/.abroll-cloud/31")
A_SRC = Path("/workspace/.abroll-cloud/06/assets")
W, H, FPS = 1080, 1920, 24
NAME = "贴地冻雨"
STAGED_NAME = "31-贴地冻雨.mp4"
VOICE = "zh-CN-YunyangNeural"
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_RG = "/tmp/NotoSansSC-Regular.otf"
FONT_FB = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

BG = (8, 12, 18)
CARD = (22, 28, 38)
MINT = (126, 224, 197)
CYAN = (120, 210, 232)
ICE = (176, 228, 240)
AMBER = (232, 176, 88)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
CREAM = (245, 247, 250)
MUTED = (154, 162, 176)
RED = (255, 118, 118)
B_LEAD = 0.28


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


def u32(i: int) -> int:
    x = (i * 0x9E3779B1) & 0xFFFFFFFF
    x ^= x >> 16
    x = (x * 0x85EBCA6B) & 0xFFFFFFFF
    x ^= x >> 13
    return x


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
    d.ellipse((-280, -340, 780, 640), fill=(12, 36, 48))
    d.ellipse((360, 1180, 1420, 2160), fill=(48, 32, 16))
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


def shade_still(img: Image.Image) -> Image.Image:
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for y in range(0, 180):
        sd.line([(0, y), (W, y)], fill=(8, 10, 14, int(90 * (1 - y / 180))))
    for y in range(H - 560, H):
        sd.line([(0, y), (W, y)], fill=(8, 10, 14, int(200 * ((y - (H - 560)) / 560))))
    return Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")


def punch_bar(base: Image.Image, t: float, title: str, punch: str, start: float = 0.16) -> None:
    a = appear(t, start, 0.28)
    if a <= 0:
        return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y = 1420 + int((1 - a) * 28)
    d.rounded_rectangle((90, y, 990, y + 280), radius=36, fill=(12, 16, 22, int(230 * a)))
    d.text((540, y + 90), title, font=font(40), fill=(*mix(CARD, MUTED, a), 255), anchor="mm")
    d.text((540, y + 190), punch, font=font(58), fill=(*mix(CARD, AMBER, a), 255), anchor="mm")
    out = Image.alpha_composite(base.convert("RGBA"), layer)
    base.paste(out.convert("RGB"))


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
    vtt = ["WEBVTT", ""]
    for i, c in enumerate(cues, 1):
        def ts(x: float) -> str:
            ms = int(round(x * 1000))
            return f"{ms // 3600000:02d}:{(ms // 60000) % 60:02d}:{(ms // 1000) % 60:02d}.{ms % 1000:03d}"

        vtt += [str(i), f"{ts(c['start'])} --> {ts(c['end'])}", c["text"], ""]
    (audio / "vo.vtt").write_text("\n".join(vtt), encoding="utf-8")
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
                color = list(CYAN)
            else:
                color = list(CREAM)
            if i == len(shots) - 1:
                color = list(AMBER)
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
        "topic_id": "012",
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
        "b_lead_s": B_LEAD,
    }
    (ROOT / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("timeline", dur, "shots", len(shots))
    return data


def make_bgm(duration: float) -> Path:
    dest = ROOT / "audio/bgm.wav"
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=174.61:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=220:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=261.63:sample_rate=44100:duration={duration + 1.2:.2f}",
        "-filter_complex",
        "[0:a]volume=0.11[a];[1:a]volume=0.07[b];[2:a]volume=0.05[c];"
        "[a][b][c]amix=inputs=3:duration=longest,lowpass=f=480,alimiter=limit=0.32",
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
        delays.append(f"aevalsrc=0.010*sin(2*PI*660*t):s=44100:d=0.06,adelay={ms}|{ms}[s{i}]")
        parts.append(f"[s{i}]")
    fc = ";".join(delays) + f";{''.join(parts)}amix=inputs={len(parts)}:duration=longest,aformat=sample_rates=44100:channel_layouts=stereo"
    run(["ffmpeg", "-y", "-filter_complex", fc, "-t", f"{duration:.2f}", str(dest)])
    return dest


# ---------- B-roll ----------
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
        d.text((W // 2, 250 + int(lerp(18, 0, a0))), "低处时间极慢", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        a1 = appear(t, 0.26)
        if a1 > 0.04:
            y = 360 + int(lerp(22, 0, a1))
            box = (90, y, 990, y + 240)
            rounded(d, box, 32, mix(BG, CARD, a1))
            d.text((540, y + 80), "到处一样快", font=card_f, fill=mix(CARD, YELLOW, a1), anchor="mm")
            d.text((540, y + 160), "雨同时落地", font=sub_f, fill=mix(CARD, MUTED, a1), anchor="mm")
            strike_line(d, box, t, 0.82)

        a2 = appear(t, 1.10)
        if a2 > 0.04:
            y = 660 + int(lerp(22, 0, a2))
            rounded(d, (90, y, 990, y + 260), 32, mix(BG, (22, 40, 40), a2))
            d.text((540, y + 90), "贴地几乎凝固", font=title_f, fill=mix(CARD, AMBER, a2), anchor="mm")
            d.text((540, y + 180), "高处照常流逝", font=sub_f, fill=mix(CARD, WHITE, a2), anchor="mm")

        punch = appear(t, min(1.95, max(0.9, duration - 1.05)), 0.26)
        if punch > 0.04:
            y = 1040 + int(lerp(22, 0, punch))
            rounded(d, (140, y, 940, y + 200), 30, mix(BG, (42, 30, 16), punch))
            d.text((W // 2, y + 100), "低处极慢", font=title_f, fill=mix(BG, AMBER, punch), anchor="mm")
        out.append(img)
    return out


def draw_split_rain(draw: ImageDraw.ImageDraw, t: float, line_y: int) -> None:
    """Upper rain falls; ground-layer drops stay frozen. Same frame, two rates."""
    # glowing stratification line
    for k, a in ((18, 40), (8, 90), (3, 180)):
        draw.line([(40, line_y), (W - 40, line_y)], fill=(*AMBER, a) if False else mix(BG, AMBER, a / 220), width=k)

    # falling streaks above the line
    for i in range(42):
        hsh = u32(i + 31)
        x = 30 + (hsh % (W - 60))
        speed = 520 + (hsh >> 8) % 280
        length = 28 + (hsh >> 16) % 36
        phase = ((hsh >> 4) % 1000) / 1000.0
        y = int((-80 + ((t * speed) + phase * (line_y + 80)) % (line_y + 80)))
        if y > line_y - 8:
            continue
        y1 = min(line_y - 6, y + length)
        fade = 0.35 + 0.45 * ((hsh >> 20) % 80) / 80.0
        draw.line([(x, y), (x, y1)], fill=mix(BG, ICE, fade), width=2)

    # frozen beads below the line
    for i in range(28):
        hsh = u32(i + 310)
        x = 50 + (hsh % (W - 100))
        y = line_y + 24 + (hsh >> 9) % max(40, H - line_y - 220)
        jitter = 0.4 * math.sin(t * 1.2 + i)
        r = 5 + (hsh >> 18) % 5
        cx, cy = int(x + jitter), int(y)
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=mix(BG, AMBER, 0.72))
        draw.ellipse((cx - 2, cy - 3, cx + 1, cy), fill=mix(AMBER, WHITE, 0.45))


def render_b_rain(duration: float) -> list[Image.Image]:
    still = Image.open(ROOT / "assets/t31a-two-layer-rain.png").convert("RGB")
    still = ImageEnhance.Brightness(still).enhance(0.92)
    n = max(1, round(duration * FPS))
    line_y = int(H * 0.62)
    out = []
    for i in range(n):
        t = i / FPS
        p = t / max(duration, 0.01)
        img = cover(still, W, H, zoom=1.03 + 0.07 * p, pan_y=-0.03 + 0.06 * p)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        # dim a band so overlay rain reads
        ld.rectangle((0, 0, W, line_y), fill=(6, 10, 16, 28))
        img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
        d = ImageDraw.Draw(img)
        draw_split_rain(d, t, line_y)
        img = shade_still(img)
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "钩子")
        punch_bar(img, t, "贴地的雨滴冻住了", "上面还在下")
        out.append(img)
    return out


def render_b_still(src: Path, duration: float, tag: str, title: str, punch: str) -> list[Image.Image]:
    still = Image.open(src).convert("RGB")
    still = ImageEnhance.Brightness(still).enhance(0.94)
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        p = t / max(duration, 0.01)
        img = cover(still, W, H, zoom=1.04 + 0.08 * p, pan_y=-0.04 + 0.08 * p)
        img = shade_still(img)
        d = ImageDraw.Draw(img)
        tag_chip(d, t, tag)
        punch_bar(img, t, title, punch)
        out.append(img)
    return out


def render_broll(data: dict) -> None:
    durs = {}
    for shot in data["shots"]:
        if shot["kind"] == "B":
            durs[shot["src"]] = max(1.5, float(shot["end"]) - float(shot["start"]))
    jobs = [
        ("broll/B-定律.mp4", lambda d: render_b_law(d)),
        ("broll/B-冻雨.mp4", lambda d: render_b_rain(d)),
        ("broll/B-灰尘.mp4", lambda d: render_b_still(ROOT / "assets/t31b-amber-dust.png", d, "后果 01", "地面灰尘", "千年不动")),
        ("broll/B-草木.mp4", lambda d: render_b_still(ROOT / "assets/t31c-grass-trees.png", d, "后果 02", "矮草几乎不长", "高树疯长")),
        ("broll/B-钥匙.mp4", lambda d: render_b_still(ROOT / "assets/t31d-key-in-gel.png", d, "后果 03", "掉在地上的东西", "再也捡不起来")),
        ("broll/B-琥珀城.mp4", lambda d: render_b_still(ROOT / "assets/t31e-amber-city.png", d, "回报", "低处像琥珀", "高处照常走")),
    ]
    for rel, fn in jobs:
        dur = durs.get(rel)
        if not dur:
            raise SystemExit(f"no duration for {rel}")
        print("render", rel, f"{dur:.2f}s")
        frames_to_mp4(fn(dur + 0.12), ROOT / rel)


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
    box_w = min(W - 80, tw + pad_x * 2)
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
        "[3:a]volume=0.26[sfx];"
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


def write_cover(data: dict) -> Path:
    dest = ROOT / f"00_封面_{NAME}.jpg"
    still = Image.open(ROOT / data["cover"]["src"]).convert("RGB")
    img = cover(still, W, H, zoom=1.08, pan_y=-0.02)
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rounded_rectangle((70, 160, 1010, 620), radius=40, fill=(10, 14, 20, 214))
    img = Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")
    d = ImageDraw.Draw(img)
    d.text((540, 260), "贴地冻雨", font=font(86), fill=WHITE, anchor="mm")
    d.text((540, 380), "上面还在下", font=font(58), fill=AMBER, anchor="mm")
    d.text((540, 500), "低处时间极慢", font=font(36), fill=CYAN, anchor="mm")
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    img.save(ROOT / "final/cover.jpg", quality=92)
    return dest


def write_docs(dur: float, staged: Path, data: dict) -> None:
    vo = (ROOT / "script/voiceover.txt").read_text(encoding="utf-8").strip()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sha = hashlib.sha256(vo.encode("utf-8")).hexdigest()
    status = {
        "schema_version": 1,
        "project_name": "31_贴地冻雨",
        "video_type": "普通短视频",
        "episode": 31,
        "topic_id": "012",
        "source_note": "topics-batch2.md #31 / 选题库.md 第012号 · 低处的时间流逝极慢",
        "title": NAME,
        "stage": "delivered",
        "status": "已交付",
        "current_stage": "核验并交付",
        "production_method": "白底小灯 A-roll + 黑底对照卡/无字静帧 B-roll（两层雨速叠加）+ edge-tts Yunyang + FFmpeg",
        "voice": VOICE,
        "duration": round(dur, 3),
        "size": [W, H],
        "fps": FPS,
        "script": {"path": "script/voiceover.txt", "sha256": sha},
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
        "siblings_avoided": ["001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011"],
        "updated_at": now,
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    explain = f"""# 31 · 贴地冻雨

普通短视频 / 知识口播。**不是**剧情短剧，不走 drama-pipeline。

- **选题**：`topics-batch2.md` #31；Drive `选题库.md` 第 **012** 号 · 低处的时间流逝极慢
- **结构**：改一条定律 → 三个后果（灰尘 / 草木 / 捡不起来）→ 琥珀城回报
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/31/`
- **云端 only**：未写 `C:\\` / `D:\\` / `G:\\`，未上传 Drive

钩子：贴地的雨滴冻住了，上面还在下。  
收束：低处像琥珀，高处照常走。

白底小灯 A-roll + 黑底对照卡 / 无字静帧 B-roll。钩子镜在同一构图叠两层雨速。中文在代码绘制 / 组装叠加，生图不烧字。

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
    frames_dir = qa_dir / "frames"
    frames_dir.mkdir(exist_ok=True)
    picks = [
        (0.35, "ep31_a_hello"),
        (float(shots[2]["start"]) + 0.35, "ep31_b_law"),
        (float(shots[3]["start"]) + 0.40, "ep31_b_rain"),
        (float(shots[4]["start"]) + 0.30, "ep31_b_dust"),
        (float(shots[5]["start"]) + 0.30, "ep31_b_plants"),
        (float(shots[6]["start"]) + 0.35, "ep31_b_key"),
        (float(shots[7]["start"]) + 0.40, "ep31_b_city"),
    ]
    for t, name in picks:
        run([
            "ffmpeg", "-y", "-ss", f"{max(0.0, t):.3f}", "-i", str(staged),
            "-frames:v", "1", str(frames_dir / f"{name}.jpg"),
        ])
    report = {
        "project": "31_贴地冻雨",
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
            "broll_lead_s": B_LEAD,
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
        "t31a-two-layer-rain.png",
        "t31b-amber-dust.png",
        "t31c-grass-trees.png",
        "t31d-key-in-gel.png",
        "t31e-amber-city.png",
    ):
        if not (assets / name).exists():
            raise FileNotFoundError(assets / name)


def main() -> None:
    copy_assets()
    dur, cues = make_voiceover()
    for c in cues:
        print(f"  {c['start']:6.3f}-{c['end']:6.3f}  {c['text']}")
    data = build_timeline(cues, dur)
    render_broll(data)
    write_cover(data)
    staged = assemble(data)
    cut_dur = probe_dur(staged)
    write_docs(cut_dur, staged, data)
    patch_index(cut_dur)
    report = qa(staged, data)
    print("STAGED", staged, "dur", cut_dur, "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
