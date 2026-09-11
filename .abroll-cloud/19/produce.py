# -*- coding: utf-8 -*-
"""Topic 19 / scout #12: 十二节气先锁十二张首帧.

普通短视频 / 知识口播。方法片，不是 Envoys 神话连载，不走 drama-pipeline。
云端 exclusively：草稿只写 .abroll-cloud/19/，成品中转 成片/19-*.mp4。
禁止 C:\\ D:\\ G:\\ 路径。
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 24
NAME = "十二节气先锁十二张首帧"
STAGED_NAME = "19-十二节气先锁十二张首帧.mp4"
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_REG = "/tmp/NotoSansSC-Regular.otf"
FONT_FALLBACK = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
FACTORY_VO = Path("/workspace/.abroll-cloud/aroll/audio/12_十二节气先锁十二张首帧.wav")
A_SRC = Path("/workspace/.abroll-cloud/06/assets")

BG = (11, 13, 18)
CARD = (24, 28, 38)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
RED = (255, 118, 118)
ORANGE = (232, 132, 78)
ICE = (148, 196, 222)
INK = (22, 24, 28)
CREAM = (245, 247, 250)

# Factory WAV 11.064s；句间静音约 0.73s（silencedetect -32dB / 0.12s）
PHRASE_STARTS = [0.0, 1.449, 4.237, 6.356, 8.542]
DURATION = 11.064
B_LEAD = 0.280  # B 卷比口播早切半拍


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
    path = FONT_BD if bold else FONT_REG
    for candidate in (path, FONT_FALLBACK):
        try:
            return ImageFont.truetype(candidate, size)
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


def paint_season_still(size: tuple[int, int], season: str, filled: float) -> Image.Image:
    """Abstract first-frame placeholders. No characters, no myth serial."""
    w, h = size
    palettes = {
        "春": ((42, 28, 36), (186, 92, 118), (244, 186, 198), (245, 220, 180)),
        "夏": ((18, 36, 28), (36, 120, 78), (245, 193, 92), (210, 236, 170)),
        "秋": ((40, 22, 16), (168, 72, 36), (232, 132, 78), (245, 200, 120)),
        "冬": ((16, 28, 42), (70, 118, 156), (210, 228, 240), (148, 196, 222)),
    }
    c0, c1, c2, c3 = palettes[season]
    img = Image.new("RGB", (w, h), mix(BG, c0, filled))
    d = ImageDraw.Draw(img)
    if filled < 0.08:
        return img
    a = filled
    if season == "春":
        d.ellipse((int(w * 0.12), int(h * 0.38), int(w * 0.78), int(h * 1.05)), fill=mix(c0, c1, a * 0.7))
        for cx, cy, r in ((0.32, 0.30, 0.14), (0.58, 0.22, 0.11), (0.70, 0.40, 0.10)):
            d.ellipse(
                (int(w * (cx - r)), int(h * (cy - r)), int(w * (cx + r)), int(h * (cy + r))),
                fill=mix(c0, c2, a),
            )
        d.ellipse((int(w * 0.50), int(h * 0.28), int(w * 0.62), int(h * 0.36)), fill=mix(c0, c3, a))
    elif season == "夏":
        d.rectangle((0, int(h * 0.62), w, h), fill=mix(c0, c1, a * 0.85))
        d.ellipse((int(w * 0.28), int(h * 0.10), int(w * 0.80), int(h * 0.42)), fill=mix(c0, c2, a))
        d.ellipse((int(w * 0.18), int(h * 0.50), int(w * 0.82), int(h * 0.78)), fill=mix(c0, c3, a * 0.7))
    elif season == "秋":
        d.polygon(
            [(int(w * 0.50), int(h * 0.16)), (int(w * 0.86), int(h * 0.48)), (int(w * 0.50), int(h * 0.80)), (int(w * 0.14), int(h * 0.48))],
            fill=mix(c0, c1, a),
        )
        d.ellipse((int(w * 0.38), int(h * 0.36), int(w * 0.62), int(h * 0.58)), fill=mix(c0, c2, a))
        d.rectangle((0, int(h * 0.78), w, h), fill=mix(c0, c3, a * 0.55))
    else:
        d.ellipse((int(w * -0.10), int(h * 0.55), int(w * 1.10), int(h * 1.20)), fill=mix(c0, c1, a * 0.55))
        for cx, cy, r in ((0.22, 0.22, 0.035), (0.48, 0.16, 0.028), (0.72, 0.28, 0.04), (0.36, 0.40, 0.022), (0.64, 0.44, 0.03)):
            d.ellipse(
                (int(w * (cx - r)), int(h * (cy - r)), int(w * (cx + r)), int(h * (cy + r))),
                fill=mix(c0, c2, a),
            )
        d.ellipse((int(w * 0.58), int(h * 0.10), int(w * 0.92), int(h * 0.32)), fill=mix(c0, c3, a * 0.45))
    return img


def draw_lock(draw: ImageDraw.ImageDraw, x: int, y: int, s: int, color) -> None:
    body = (x + s * 0.18, y + s * 0.42, x + s * 0.82, y + s * 0.92)
    draw.rounded_rectangle(body, radius=max(2, s // 8), fill=color)
    draw.arc((x + s * 0.22, y + s * 0.08, x + s * 0.78, y + s * 0.62), 200, 340, fill=color, width=max(2, s // 7))


def stamp_layer(size: tuple[int, int], text: str, alpha: float) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fnt = font(44)
    tw, th = text_wh(d, text, fnt)
    pad = 22
    box_w, box_h = tw + pad * 2, th + pad * 2
    box = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(box)
    a = int(230 * alpha)
    bd.ellipse((2, 2, box_w - 3, box_h - 3), outline=(*RED, a), width=8)
    bd.ellipse((10, 10, box_w - 11, box_h - 11), outline=(*RED, int(a * 0.7)), width=3)
    bd.text((box_w / 2, box_h / 2), text, font=fnt, fill=(*RED, a), anchor="mm")
    rot = box.rotate(16, expand=True, resample=Image.Resampling.BICUBIC)
    x = (size[0] - rot.width) // 2 + 40
    y = (size[1] - rot.height) // 2 + 80
    layer.alpha_composite(rot, (x, y))
    return layer


def render_b_first_frames(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    seasons = ["春", "夏", "秋", "冬"]
    colors = [MINT, YELLOW, ORANGE, ICE]
    title_f = font(56)
    season_f = font(28)
    out = []
    margin_x, top = 64, 250
    gap_x, gap_y = 18, 16
    col_w = (W - margin_x * 2 - gap_x * 3) // 4
    frame_h = int(col_w * 16 / 9)
    # 3 rows of 9:16 slots under a season label
    label_h = 44
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "首帧墙 · 确认前")
        a0 = appear(t, 0.02)
        d.text((W // 2, 186 + int(lerp(16, 0, a0))), "十二张首帧", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        for c, (season, color) in enumerate(zip(seasons, colors)):
            col_a = appear(t, 0.10 + c * 0.10, 0.24)
            if col_a < 0.04:
                continue
            x0 = margin_x + c * (col_w + gap_x)
            d.text((x0 + col_w // 2, top + int(lerp(12, 0, col_a))), season, font=season_f, fill=mix(BG, color, col_a), anchor="mm")
            for r in range(3):
                slot_a = appear(t, 0.18 + c * 0.10 + r * 0.06, 0.20)
                y0 = top + label_h + r * (frame_h + gap_y) + int(lerp(14, 0, slot_a))
                box = (x0, y0, x0 + col_w, y0 + frame_h)
                rounded(d, box, 14, mix(BG, CARD, max(slot_a, 0.2)))
                still = paint_season_still((max(8, col_w - 10), max(8, frame_h - 10)), season, slot_a)
                img.paste(still, (x0 + 5, y0 + 5))
                d = ImageDraw.Draw(img)
                if slot_a > 0.55:
                    draw_lock(d, x0 + col_w - 36, y0 + 8, 26, mix(CARD, color, slot_a))

        if t >= 1.15:
            st = appear(t, 1.15, 0.22)
            overlay = stamp_layer((W, H), "确认前不动画", st)
            img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
            d = ImageDraw.Draw(img)

        punch = appear(t, 1.55, 0.22)
        if punch > 0.04:
            y = 1648 + int(lerp(20, 0, punch))
            rounded(d, (90, y, 990, y + 168), 28, mix(BG, (42, 24, 22), punch))
            d.text((W // 2, y + 84), "点头之前，不要动画", font=font(46), fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_b_lock_camera(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(52)
    card_f = font(40)
    small = font(28)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "机位 · 字幕")
        a0 = appear(t, 0.02)
        d.text((W // 2, 186 + int(lerp(14, 0, a0))), "先锁机位", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        a1 = appear(t, 0.16)
        if a1 > 0.04:
            y = 250 + int(lerp(20, 0, a1))
            rounded(d, (72, y, 508, y + 320), 28, mix(BG, CARD, a1))
            # locked camera body
            d.rounded_rectangle((168, y + 70, 412, y + 200), radius=22, fill=mix(CARD, MINT, a1 * 0.85))
            d.ellipse((292, y + 104, 368, y + 180), fill=mix(MINT, INK, a1))
            draw_lock(d, 390, y + 58, 42, mix(CARD, YELLOW, a1))
            d.text((290, y + 262), "锁机位", font=card_f, fill=mix(CARD, MINT, a1), anchor="mm")

        a2 = appear(t, 0.32)
        if a2 > 0.04:
            y = 250 + int(lerp(20, 0, a2))
            rounded(d, (572, y, 1008, y + 320), 28, mix(BG, CARD, a2))
            bar = (620, y + 118, 960, y + 178)
            rounded(d, bar, 16, mix(CARD, (56, 40, 40), a2))
            d.text((790, y + 148), "字幕条", font=small, fill=mix(CARD, MUTED, a2), anchor="mm")
            st = appear(t, 0.70, 0.20)
            if st > 0.04:
                x0, x1 = 640, 940
                cy = y + 148
                d.line([(x0, cy), (int(lerp(x0, x1, st)), cy)], fill=mix(CARD, RED, st), width=10)
            d.text((790, y + 262), "不要字幕", font=card_f, fill=mix(CARD, RED, a2), anchor="mm")

        a3 = appear(t, 0.78)
        if a3 > 0.04:
            y = 610 + int(lerp(16, 0, a3))
            rounded(d, (72, y, 1008, y + 560), 28, mix(BG, CARD, a3))
            d.text((W // 2, y + 48), "一季三镜 · 可拆一段", font=small, fill=mix(CARD, MUTED, a3), anchor="mm")
            seasons = [("春", MINT), ("夏", YELLOW), ("秋", ORANGE), ("冬", ICE)]
            lane_top = y + 96
            lane_h = 92
            for si, (season, color) in enumerate(seasons):
                ly = lane_top + si * lane_h
                d.text((118, ly + 36), season, font=small, fill=mix(CARD, color, a3), anchor="mm")
                for k in range(3):
                    cell_a = appear(t, 0.90 + si * 0.06 + k * 0.04, 0.16)
                    cx0 = 180 + k * 270
                    box = (cx0, ly + 10, cx0 + 250, ly + 70)
                    rounded(d, box, 14, mix(CARD, mix(CARD, color, 0.35), max(cell_a, 0.15)))
                    if cell_a > 0.2:
                        d.text((cx0 + 125, ly + 40), "6 秒", font=small, fill=mix(CARD, WHITE, cell_a), anchor="mm")

        punch = appear(t, 1.55, 0.20)
        if punch > 0.04:
            y = 1648 + int(lerp(18, 0, punch))
            rounded(d, (90, y, 990, y + 168), 28, mix(BG, (18, 42, 36), punch))
            d.text((W // 2, y + 84), "先锁机位，不要字幕", font=font(46), fill=mix(BG, MINT, punch), anchor="mm")
        out.append(img)
    return out


def copy_inputs() -> None:
    assets = ROOT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for name in ("V-挥手.mp4", "V-摊手.mp4", "V-指向.mp4", "A-角色-小灯-摊手.jpg"):
        src = A_SRC / name
        dest = assets / name
        if src.exists() and (not dest.exists() or dest.stat().st_size != src.stat().st_size):
            shutil.copy2(src, dest)
    audio = ROOT / "audio"
    audio.mkdir(parents=True, exist_ok=True)
    dest_vo = audio / "vo-full.wav"
    if not dest_vo.exists() or dest_vo.stat().st_size != FACTORY_VO.stat().st_size:
        shutil.copy2(FACTORY_VO, dest_vo)
    dur = probe_dur(dest_vo)
    if abs(dur - DURATION) > 0.05:
        raise SystemExit(f"factory VO duration {dur} != {DURATION}")


def write_align() -> list[tuple[float, float, str]]:
    phrases = [ln.strip() for ln in (ROOT / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    starts = list(PHRASE_STARTS)
    ends = starts[1:] + [DURATION]
    aligned = [(round(s, 3), round(e, 3), p) for s, e, p in zip(starts, ends, phrases)]
    lines = [f"{s:.3f}\t{e:.3f}\t{p}" for s, e, p in aligned]
    (ROOT / "audio" / "vo-align.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return aligned


def build_timeline(aligned: list[tuple[float, float, str]]) -> dict:
    p0, p1, p2, p3, p4 = aligned
    b1 = max(p1[0] + 0.8, p2[0] - B_LEAD)
    shots = [
        {"id": "S01a", "kind": "A", "start": 0.0, "end": p0[1], "src": "assets/V-挥手.mp4", "line": p0[2], "close": True},
        {"id": "S01b", "kind": "A", "start": p0[1], "end": b1, "src": "assets/V-摊手.mp4", "line": p1[2]},
        {"id": "S02", "kind": "B", "start": b1, "end": p2[1], "src": "broll/B-首帧墙.mp4", "line": p2[2], "broll": "first_frames"},
        {"id": "S03", "kind": "B", "start": p2[1], "end": p3[1], "src": "broll/B-锁机位.mp4", "line": p3[2], "broll": "lock_camera"},
        {"id": "S04", "kind": "A", "start": p3[1], "end": DURATION, "src": "assets/V-指向.mp4", "line": p4[2]},
    ]
    for i, shot in enumerate(shots):
        shot["start"] = round(float(shot["start"]), 3)
        shot["end"] = round(float(shot["end"]), 3)
        if shot["end"] <= shot["start"] + 0.12:
            raise SystemExit(f"bad shot {shot}")
        if i:
            shots[i]["start"] = shots[i - 1]["end"]
    shots[-1]["end"] = DURATION
    data = {
        "audio": "audio/vo-full.wav",
        "duration": DURATION,
        "fps": FPS,
        "size": [W, H],
        "title": NAME,
        "bgm": "audio/bgm.wav",
        "shots": shots,
        "a_caps": [
            {"start": p0[0], "end": p0[1], "lines": ["大家好"]},
            {"start": p1[0], "end": b1, "lines": ["十二节气", "先锁十二张首帧"]},
            {"start": p4[0], "end": DURATION, "lines": ["这是方法", "不是神话连载"]},
        ],
        "shutters": [
            {"start": p0[1], "color": list(CREAM)},
            {"start": b1, "color": list(MINT)},
            {"start": p2[1], "color": list(CREAM)},
            {"start": p3[1], "color": list(YELLOW)},
        ],
        "eyebrows": [
            {"start": 0.0, "end": p0[1], "text": "A-ROLL / 1a"},
            {"start": p0[1], "end": b1, "text": "A-ROLL / 1b"},
            {"start": p3[1], "end": DURATION, "text": "A-ROLL / 04"},
        ],
        "cover": {
            "title": NAME,
            "sub": "点头之前，不要动画",
            "line": "这是方法，不是神话连载",
            "src": "assets/A-角色-小灯-摊手.jpg",
        },
    }
    (ROOT / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


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
    if not cuts:
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={duration:.2f}", str(dest)])
        return dest
    delays = []
    parts = []
    for i, t in enumerate(cuts):
        ms = int(t * 1000)
        delays.append(f"aevalsrc=0.012*sin(2*PI*880*t):s=44100:d=0.07,adelay={ms}|{ms}[s{i}]")
        parts.append(f"[s{i}]")
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
    bgm = ROOT / "audio" / "bgm.wav"
    sfx = ROOT / "audio" / "sfx.wav"
    cuts = [float(s["start"]) for s in data["shutters"]]
    make_sfx(cuts, float(data["duration"]))

    final = ROOT / f"00_最终成片_{NAME}.mp4"
    inputs = ["ffmpeg", "-y", "-i", str(burned), "-i", str(audio)]
    filters = ["[1:a]loudnorm=I=-16:LRA=11:TP=-1.5,aformat=sample_rates=44100:channel_layouts=stereo[vo]"]
    mix_ins = ["[vo]"]
    idx = 2
    if bgm.exists():
        inputs += ["-i", str(bgm)]
        filters.append(f"[{idx}:a]adelay=800|800,volume=0.16,highpass=f=140[bg]")
        mix_ins.append("[bg]")
        idx += 1
    if sfx.exists():
        inputs += ["-i", str(sfx)]
        filters.append(f"[{idx}:a]volume=0.28[sfx]")
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
    dest = ROOT / f"00_封面_{NAME}.jpg"
    char = Image.open(ROOT / "assets" / "A-角色-小灯-摊手.jpg").convert("RGB")
    scale = max(W / char.width, H / char.height)
    nw, nh = int(char.width * scale), int(char.height * scale)
    char = char.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - W) // 2
    y = int((nh - H) * 0.62)
    canvas = char.crop((x, y, x + W, y + H))
    overlay = Image.new("RGBA", (W, H), (11, 13, 18, 40))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((70, 80, 1010, 470), radius=36, fill=(22, 24, 28))
    d.text((W // 2, 168), "十二节气", font=font(64), fill=WHITE, anchor="mm")
    d.text((W // 2, 250), "先锁十二张首帧", font=font(56), fill=MINT, anchor="mm")
    d.text((W // 2, 330), "点头之前，不要动画", font=font(36), fill=YELLOW, anchor="mm")
    d.text((W // 2, 400), "这是方法，不是神话连载", font=font(30), fill=MUTED, anchor="mm")
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    canvas.save(ROOT / "final" / "cover.jpg", quality=92)
    return dest


def write_docs(duration: float, staged: Path) -> None:
    import hashlib
    from datetime import datetime, timezone

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    sha = hashlib.sha256(vo.encode("utf-8")).hexdigest()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    status = {
        "schema_version": 1,
        "project_name": "19_十二节气先锁十二张首帧",
        "video_type": "普通短视频",
        "topic_index": 12,
        "slug": "12_十二节气先锁十二张首帧",
        "title": NAME,
        "production_method": "白底小灯 A-roll（06 已有动作）+ 黑底信息图 B-roll + 工厂口播 WAV + FFmpeg",
        "status": "已交付",
        "current_stage": "核验并交付",
        "stage": "delivered",
        "voice": "zh-CN-YunyangNeural",
        "duration": duration,
        "size": [W, H],
        "fps": FPS,
        "script": {"path": "script/voiceover.txt", "sha256": sha},
        "audio": {
            "path": "audio/vo-full.wav",
            "alignment_path": "audio/vo-align.txt",
            "source": "aroll/audio/12_十二节气先锁十二张首帧.wav",
            "sample_rate": 44100,
            "channels": 1,
            "duration_ms": int(duration * 1000),
            "note": "沿用工厂旁白，不重合成；句界来自 silencedetect",
        },
        "deliverables": {
            "final_video": str(staged),
            "project_final": f"00_最终成片_{NAME}.mp4",
            "cover": f"00_封面_{NAME}.jpg",
        },
        "not": "神话剧情连载 / drama-pipeline / Envoys 正片",
        "updated_at": now,
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    explain = f"""# 19 · 十二节气先锁十二张首帧

普通短视频 / 知识口播。**不是**《Envoys of the Seasons》神话连载，不走 drama-pipeline。

- **选题**：云端 `topics.md` 第 12 条；工厂口播 `12_十二节气先锁十二张首帧`
- **来源笔记**（Drive 只读）：`2026-08-13-envoys-of-the-seasons.md`（十二镜 × 6 秒、四季各三镜、锁机位、无字幕、点头前不动画）
- **成片中转**：`成片/19-十二节气先锁十二张首帧.mp4`
- **本集工程成片**：`00_最终成片_十二节气先锁十二张首帧.mp4`
- **草稿**：只在 `/workspace/.abroll-cloud/19/`，不写 `C:` / `D:` / `G:`

钩子：十二节气先锁十二张首帧。  
收束：这是方法，不是神话连载。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {duration:.2f} 秒。
"""
    (ROOT / "项目说明.md").write_text(explain, encoding="utf-8")


def main() -> None:
    copy_inputs()
    aligned = write_align()
    print("ALIGN", aligned)
    data = build_timeline(aligned)
    make_bgm(DURATION)

    b1 = next(s for s in data["shots"] if s["id"] == "S02")
    b2 = next(s for s in data["shots"] if s["id"] == "S03")
    d1 = max(2.2, float(b1["end"]) - float(b1["start"]))
    d2 = max(2.2, float(b2["end"]) - float(b2["start"]))
    print("render B-首帧墙", d1)
    frames_to_mp4(render_b_first_frames(d1), ROOT / "broll" / "B-首帧墙.mp4")
    print("render B-锁机位", d2)
    frames_to_mp4(render_b_lock_camera(d2), ROOT / "broll" / "B-锁机位.mp4")

    make_cover()
    staged = assemble(data)
    write_docs(probe_dur(staged), staged)
    print("STAGED", staged, "dur", probe_dur(staged))


if __name__ == "__main__":
    main()
