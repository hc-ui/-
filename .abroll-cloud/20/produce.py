# -*- coding: utf-8 -*-
"""20 · 凉咖啡重新冒热气，杯壁却结霜。

普通短视频 / 知识口播。改一条定律，不是剧情短剧。
云端 exclusively：草稿只写 .abroll-cloud/20/，成品中转 成片/20-*.mp4。
复用工厂口播 WAV 与 t05 B 卷静帧/短镜。禁止 C:\\ D:\\ G:\\，不上传 Drive。
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path("/workspace/.abroll-cloud/20")
W, H, FPS = 1080, 1920, 24
NAME = "凉咖啡重新冒热气杯壁却结霜"
STAGED_NAME = "20-凉咖啡重新冒热气杯壁却结霜.mp4"
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_RG = "/tmp/NotoSansSC-Regular.otf"
FONT_FB = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
FACTORY_VO = Path("/workspace/.abroll-cloud/aroll/audio/05_凉咖啡冒热气杯壁结霜.wav")
A_SRC = Path("/workspace/.abroll-cloud/06/assets")
T05_SRC = Path("/workspace/.abroll-cloud/broll-assets")

BG = (11, 13, 18)
CARD = (24, 28, 38)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
RED = (255, 118, 118)
ICE = (186, 220, 236)
CREAM = (245, 247, 250)
INK = (22, 24, 28)

# 工厂 WAV 16.296s；句界来自 silencedetect -32dB / 0.12s
# 带逗号的句子拆成两段语音岛，对齐时合并回 phrases.txt
DURATION = 16.296
B_LEAD = 0.200
ALIGN = [
    (0.000, 1.472, "大家好"),
    (1.472, 4.014, "热永远从冷的流向热的"),
    (4.014, 7.456, "凉咖啡重新冒热气，杯壁却结霜"),
    (7.456, 9.324, "冰会重新冻上"),
    (9.324, 12.231, "房间越住越冷，暖气片越烫"),
    (12.231, 13.865, "烟退回火里"),
    (13.865, 16.296, "只反转热，别的物理照旧"),
]


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout)[-2500:])


def probe(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True,
    ).strip()
    return float(out)


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    path = FONT_BD if bold else FONT_RG
    for candidate in (path, FONT_FB):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


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


def text_wh(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=fnt)
    return x1 - x0, y1 - y0


def cover_crop(im: Image.Image, zoom: float, cx: float = 0.5, cy: float = 0.46) -> Image.Image:
    im = im.convert("RGB")
    scale = max(W / im.width, H / im.height) * max(1.0, zoom)
    nw, nh = max(W, int(im.width * scale + 0.5)), max(H, int(im.height * scale + 0.5))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = int((nw - W) * cx)
    y = int((nh - H) * cy)
    x = max(0, min(nw - W, x))
    y = max(0, min(nh - H, y))
    return im.crop((x, y, x + W, y + H))


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


def prepare_inputs() -> float:
    assets = ROOT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for name in ("V-挥手.mp4", "V-摊手.mp4", "V-点赞.mp4", "A-角色-小灯-摊手.jpg"):
        src = A_SRC / name
        dest = assets / name
        if src.exists() and (not dest.exists() or dest.stat().st_size != src.stat().st_size):
            shutil.copy2(src, dest)
        if not dest.exists():
            raise FileNotFoundError(src)
    for name in (
        "t05a-coffee-frost-steam.png",
        "t05b-smoke-into-flame.png",
        "t05-frost-steam.mp4",
        "t05-smoke-back.mp4",
    ):
        src = T05_SRC / name
        dest = assets / name
        if src.exists() and (not dest.exists() or dest.stat().st_size != src.stat().st_size):
            shutil.copy2(src, dest)
        if not dest.exists():
            raise FileNotFoundError(src)
    audio = ROOT / "audio"
    audio.mkdir(parents=True, exist_ok=True)
    vo = audio / "vo-full.wav"
    if not vo.exists() or vo.stat().st_size != FACTORY_VO.stat().st_size:
        shutil.copy2(FACTORY_VO, vo)
    dur = probe(vo)
    if abs(dur - DURATION) > 0.05:
        raise SystemExit(f"factory VO duration {dur} != {DURATION}")
    return dur


def write_align(dur: float) -> list[tuple[float, float, str]]:
    phrases = [ln.strip() for ln in (ROOT / "script/phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    if [p for *_, p in ALIGN] != phrases:
        raise SystemExit(f"ALIGN phrases != phrases.txt: {phrases}")
    cues = [(s, e if i < len(ALIGN) - 1 else dur, line) for i, (s, e, line) in enumerate(ALIGN)]
    cues[-1] = (cues[-1][0], dur, cues[-1][2])
    text = "\n".join(f"{s:.3f}\t{e:.3f}\t{line}" for s, e, line in cues) + "\n"
    (ROOT / "audio/vo-align.txt").write_text(text, encoding="utf-8")
    return cues


def split_caption(line: str) -> list[str]:
    line = line.strip("。．. ")
    if "，" in line:
        parts = [p for p in line.split("，") if p]
        if 1 < len(parts) <= 2:
            return parts
    if line == "热永远从冷的流向热的":
        return ["热永远从冷的", "流向热的"]
    return [line]


def build_timeline(cues: list[tuple[float, float, str]], dur: float) -> dict:
    recipe = json.loads((ROOT / "plan/shot_recipe.json").read_text(encoding="utf-8"))
    pmap = {line: (s, e) for s, e, line in cues}
    shots = []
    for spec in recipe["shots"]:
        ps = spec["phrases"]
        start = pmap[ps[0]][0]
        end = pmap[ps[-1]][1]
        item = {
            "id": spec["id"],
            "kind": spec["kind"],
            "src": spec["src"],
            "line": ps[-1],
            "phrases": ps,
            "start": start,
            "end": end,
        }
        if spec.get("close"):
            item["close"] = True
        if spec.get("broll"):
            item["broll"] = spec["broll"]
        shots.append(item)

    for i in range(1, len(shots)):
        if shots[i]["kind"] == "B" and shots[i - 1]["kind"] == "A":
            pull = min(B_LEAD, max(0.0, (shots[i - 1]["end"] - shots[i - 1]["start"]) - 0.70))
            shots[i]["start"] -= pull
            shots[i - 1]["end"] -= pull
    shots[0]["start"] = 0.0
    for i in range(1, len(shots)):
        shots[i]["start"] = shots[i - 1]["end"]
    shots[-1]["end"] = dur

    a_caps, eyebrows, shutters = [], [], []
    a_i = 0
    for i, shot in enumerate(shots):
        shot["start"] = round(float(shot["start"]), 3)
        shot["end"] = round(float(shot["end"]), 3)
        if shot["end"] <= shot["start"] + 0.12:
            raise SystemExit(f"bad shot {shot}")
        if shot["kind"] == "A":
            a_i += 1
            a_caps.append({
                "start": shot["start"],
                "end": shot["end"],
                "lines": split_caption(shot["line"]),
            })
            eyebrows.append({
                "start": shot["start"],
                "end": shot["end"],
                "text": f"A-ROLL / {a_i:02d}",
            })
        if i > 0:
            if i == len(shots) - 1:
                color = list(YELLOW)
            elif shot["kind"] == "B":
                color = list(MINT)
            else:
                color = list(CREAM)
            shutters.append({"start": shot["start"], "color": color})

    data = {
        "audio": "audio/vo-full.wav",
        "duration": round(dur, 3),
        "fps": FPS,
        "size": [W, H],
        "title": NAME,
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
    return data


def tag_chip(draw: ImageDraw.ImageDraw, t: float, label: str) -> None:
    a = appear(t, 0.0, 0.22)
    if a <= 0:
        return
    fnt = font(30)
    tw, th = text_wh(draw, label, fnt)
    x, y = 84, 88
    draw.rounded_rectangle((x - 22, y - 12, x + tw + 22, y + th + 12), radius=22, fill=mix(BG, (20, 42, 38), a))
    draw.text((x, y), label, font=fnt, fill=mix(BG, MINT, a))


def punch_bar(base: Image.Image, t: float, title: str, punch: str) -> None:
    a = appear(t, 0.16, 0.28)
    if a <= 0.04:
        return
    y = 1460 + int((1 - a) * 28)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((90, y, 990, y + 260), radius=34, fill=(16, 18, 24, int(230 * a)))
    d.text((540, y + 82), title, font=font(36), fill=(*mix(CARD, MUTED, a), 255), anchor="mm")
    d.text((540, y + 176), punch, font=font(58), fill=(*mix(CARD, WHITE, a), 255), anchor="mm")
    out = Image.alpha_composite(base.convert("RGBA"), layer)
    base.paste(out.convert("RGB"))


def shade_still(img: Image.Image) -> Image.Image:
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for y in range(0, 180):
        sd.line([(0, y), (W, y)], fill=(8, 10, 14, int(88 * (1 - y / 180))))
    for y in range(H - 560, H):
        sd.line([(0, y), (W, y)], fill=(8, 10, 14, int(200 * ((y - (H - 560)) / 560))))
    return Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")


def render_b_still(src: Path, duration: float, tag: str, title: str, punch: str,
                   z0: float, z1: float, cx: float, cy0: float, cy1: float) -> list[Image.Image]:
    still = Image.open(src).convert("RGB")
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        p = ease(t / max(duration, 0.01))
        img = cover_crop(still, lerp(z0, z1, p), cx, lerp(cy0, cy1, p))
        img = shade_still(img)
        d = ImageDraw.Draw(img)
        tag_chip(d, t, tag)
        punch_bar(img, t, title, punch)
        out.append(img)
    return out


def new_b_bg() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    overlay = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(overlay)
    d.ellipse((-220, -280, 720, 560), fill=(16, 36, 48))
    d.ellipse((420, 1180, 1380, 2140), fill=(28, 40, 52))
    overlay = overlay.filter(ImageFilter.GaussianBlur(120))
    return Image.blend(img, overlay, 0.58)


def render_b_ice(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        p = ease(t / max(duration, 0.01))
        img = new_b_bg()
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "后果 01")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(16, 0, a0))), "融化停住", font=font(56), fill=mix(BG, WHITE, a0), anchor="mm")

        # water puddle shrinks, cube grows
        cx, cy = 540, 820
        puddle_w = int(lerp(340, 70, p))
        puddle_h = int(lerp(70, 18, p))
        d.ellipse((cx - puddle_w, cy + 120, cx + puddle_w, cy + 120 + puddle_h), fill=mix(BG, (40, 70, 92), 0.85))

        cube = ease((p - 0.12) / 0.78)
        if cube > 0.02:
            s = max(48, int(lerp(48, 210, cube)))
            x0, y0 = cx - s // 2, cy - s // 2 - int(40 * cube)
            col = mix(CARD, ICE, cube)
            left, right = x0 + 16, x0 + s - 10
            top, bot = y0 + 40, y0 + s
            if right > left and bot > top:
                d.polygon(
                    [(left, bot), (right, bot - 12), (right, y0 + 28), (left, top)],
                    fill=mix(col, (120, 168, 196), 0.45),
                )
                d.polygon(
                    [(x0, y0 + 36), (x0 + s - 22, y0 + 18), (right, y0 + 28), (left, top)],
                    fill=mix(col, WHITE, 0.35),
                )
                d.rectangle((left, top, right, bot), fill=col)
            for k in range(7):
                ang = -0.6 + k * 0.22
                L = int(40 + 50 * cube)
                x1 = int(cx + math.cos(ang) * L)
                y1 = int(y0 + 30 + math.sin(ang) * L * 0.4)
                d.line([(cx, y0 + 36), (x1, y1)], fill=mix(ICE, WHITE, cube), width=2)

        punch_bar(img, t, "水洼收回", "重新冻上")
        out.append(img)
    return out


def render_brolls(data: dict) -> None:
    durs = {s["src"]: max(1.4, float(s["end"]) - float(s["start"])) for s in data["shots"] if s["kind"] == "B"}
    jobs = {
        "broll/B-霜杯.mp4": lambda d: render_b_still(
            ROOT / "assets/t05a-coffee-frost-steam.png", d,
            "场景", "凉咖啡在冒热气", "杯壁却结霜",
            1.04, 1.14, 0.50, 0.50, 0.42,
        ),
        "broll/B-回冻.mp4": lambda d: render_b_still(
            ROOT / "assets/t05b-smoke-into-flame.png", d,
            "后果 01", "融化停住", "重新冻上",
            1.42, 1.56, 0.86, 0.82, 0.76,
        ),
        "broll/B-房间.mp4": lambda d: render_b_still(
            ROOT / "assets/t05b-smoke-into-flame.png", d,
            "后果 02", "暖气片发红", "房间更冷",
            1.18, 1.30, 0.78, 0.28, 0.22,
        ),
        "broll/B-回烟.mp4": lambda d: render_b_still(
            ROOT / "assets/t05b-smoke-into-flame.png", d,
            "后果 03", "烟丝倒吸", "退回火里",
            1.10, 1.22, 0.22, 0.62, 0.58,
        ),
    }
    for rel, fn in jobs.items():
        dur = durs.get(rel)
        if not dur:
            raise SystemExit(f"no duration for {rel}")
        print("render", rel, f"{dur:.2f}s")
        frames_to_mp4(fn(dur + 0.12), ROOT / rel)


def draw_eyebrow(base: Image.Image, t: float, eyebrows) -> None:
    label = next((item["text"] for item in eyebrows if item["start"] <= t < item["end"]), None)
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
    src_dur = max(0.01, probe(src))
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


def make_bgm(duration: float) -> Path:
    dest = ROOT / "audio/bgm.wav"
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=174:sample_rate=44100:duration={duration + 1.4:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=220:sample_rate=44100:duration={duration + 1.4:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=261:sample_rate=44100:duration={duration + 1.4:.2f}",
        "-filter_complex",
        "[0:a]volume=0.10[a];[1:a]volume=0.07[b];[2:a]volume=0.05[c];"
        "[a][b][c]amix=inputs=3:duration=longest,lowpass=f=460,alimiter=limit=0.32",
        "-ac", "2", "-ar", "44100", str(dest),
    ])
    return dest


def make_sfx(cuts: list[float], duration: float) -> Path:
    dest = ROOT / "audio/sfx.wav"
    if not cuts:
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={duration:.2f}", str(dest)])
        return dest
    delays, parts = [], []
    for i, t in enumerate(cuts):
        if t < 0.10:
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

    dur = float(data["duration"])
    make_bgm(dur)
    make_sfx([float(s["start"]) for s in data["shutters"]], dur)

    final = ROOT / f"00_最终成片_{NAME}.mp4"
    run([
        "ffmpeg", "-y",
        "-i", str(burned),
        "-i", str(ROOT / data["audio"]),
        "-i", str(ROOT / "audio/bgm.wav"),
        "-i", str(ROOT / "audio/sfx.wav"),
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
    print("FINAL", final, "dur", probe(final))
    print("STAGED", staged, "dur", probe(staged))
    return staged


def make_cover(data: dict) -> Path:
    src = ROOT / data["cover"]["src"]
    img = cover_crop(Image.open(src), 1.08, 0.50, 0.48)
    overlay = Image.new("RGBA", (W, H), (11, 13, 18, 50))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, 140, 1010, 620), radius=40, fill=(16, 18, 24))
    d.text((540, 240), data["cover"]["title"], font=font(52), fill=WHITE, anchor="mm")
    d.text((540, 350), data["cover"]["sub"], font=font(64), fill=ICE, anchor="mm")
    d.text((540, 480), data["cover"]["line"], font=font(34), fill=MINT, anchor="mm")
    dest = ROOT / f"00_封面_{NAME}.jpg"
    img.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    img.save(ROOT / "final/cover.jpg", quality=92)
    print("cover", dest)
    return dest


def write_docs(dur: float, staged: Path) -> None:
    vo = (ROOT / "script/voiceover.txt").read_text(encoding="utf-8").strip()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    status = {
        "schema_version": 1,
        "project_name": "20_凉咖啡重新冒热气杯壁却结霜",
        "video_type": "普通短视频",
        "topic_index": 5,
        "topic_id": "007",
        "slug": "05_凉咖啡冒热气杯壁结霜",
        "delivery_index": 20,
        "title": "凉咖啡重新冒热气，杯壁却结霜",
        "stage": "delivered",
        "production_method": "白底小灯 A-roll（06 已有动作）+ t05 静帧 Ken Burns / 黑底回冻卡 + 工厂口播 WAV + FFmpeg",
        "voice": "zh-CN-YunyangNeural",
        "duration": round(dur, 3),
        "size": [W, H],
        "fps": FPS,
        "script": {"path": "script/voiceover.txt", "sha256": hashlib.sha256(vo.encode("utf-8")).hexdigest()},
        "audio": {
            "path": "audio/vo-full.wav",
            "alignment_path": "audio/vo-align.txt",
            "source": "aroll/audio/05_凉咖啡冒热气杯壁结霜.wav",
            "sample_rate": 44100,
            "channels": 1,
            "note": "沿用工厂旁白，不重合成；句界来自 silencedetect",
        },
        "broll_source": "broll-assets/t05*",
        "staged": str(staged),
        "project_final": f"00_最终成片_{NAME}.mp4",
        "cloud_only": True,
        "updated_at": now,
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = f"""# 20 · 凉咖啡重新冒热气，杯壁却结霜

普通短视频 / 知识口播。**不是**剧情短剧。只改一条热定律。

- **选题**：`topics.md` 第 5 条；选题库第 007 号
- **定律**：热永远从冷的流向热的；其余物理保持正向
- **口播**：工厂 `aroll/audio/05_凉咖啡冒热气杯壁结霜.wav`（YunyangNeural，{dur:.3f}s），不重合成
- **B 卷**：复用 `broll-assets/t05a` / `t05b` 静帧；回冻镜为黑底信息图
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/20/`（禁止进 `成片/` 当渲染目录）
- **未写** `C:` / `D:` / `G:`，未上传 Drive

钩子：凉咖啡重新冒热气，杯壁却结霜。  
收束：只反转热，别的物理照旧。

## 口播

{vo}

## 镜头

| 镜 | 卷 | 口播 | 画面 |
|----|----|------|------|
| S01 | A | 大家好 | 小灯挥手近景 |
| S02 | A | 热永远从冷的流向热的 | 小灯摊手 |
| S03 | B | 凉咖啡重新冒热气，杯壁却结霜 | t05a 霜杯缓推 |
| S04 | B | 冰会重新冻上 | 黑底回冻卡 |
| S05 | B | 房间越住越冷，暖气片越烫 | t05b 暖气/窗霜 |
| S06 | B | 烟退回火里 | t05b 火碗回烟 |
| S07 | A | 只反转热，别的物理照旧 | 小灯点赞 |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {dur:.2f} 秒。
"""
    (ROOT / "项目说明.md").write_text(md, encoding="utf-8")


def qa(final: Path, data: dict) -> dict:
    qa_dir = ROOT / "qa"
    qa_dir.mkdir(exist_ok=True)
    probe_txt = subprocess.check_output(["ffprobe", "-hide_banner", str(final)], stderr=subprocess.STDOUT, text=True)
    (qa_dir / "ffprobe.txt").write_text(probe_txt, encoding="utf-8")
    null = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(final), "-f", "null", "-"],
        capture_output=True, text=True,
    )
    (qa_dir / "decode.txt").write_text(null.stderr or "ok\n", encoding="utf-8")
    if null.returncode != 0:
        raise RuntimeError(null.stderr[-2000:])
    vdur = probe(final)
    adur = probe(ROOT / data["audio"])
    shots = data["shots"]
    closed = abs(shots[0]["start"]) < 1e-6 and abs(shots[-1]["end"] - data["duration"]) < 0.02
    gaps = []
    for i in range(len(shots) - 1):
        if abs(shots[i]["end"] - shots[i + 1]["start"]) > 1e-6:
            gaps.append((shots[i]["id"], shots[i + 1]["id"]))
    info = {
        "video_duration": round(vdur, 3),
        "audio_duration": round(adur, 3),
        "timeline_duration": data["duration"],
        "size": [W, H],
        "closed": closed,
        "gaps": gaps,
        "decode_ok": True,
        "staged": STAGED_NAME,
        "staged_exists": (Path("/workspace/成片") / STAGED_NAME).exists(),
    }
    (qa_dir / "check.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "交付核验.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not closed or gaps:
        raise SystemExit(f"timeline not closed: {info}")
    if abs(vdur - adur) > 0.25:
        raise SystemExit(f"av mismatch {vdur} vs {adur}")
    print("QA", info)
    return info


def main() -> None:
    dur = prepare_inputs()
    cues = write_align(dur)
    print("ALIGN", cues)
    data = build_timeline(cues, dur)
    render_brolls(data)
    make_cover(data)
    staged = assemble(data)
    write_docs(probe(staged), staged)
    qa(staged, data)
    print("DONE", staged)


if __name__ == "__main__":
    main()
