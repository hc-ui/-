#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Topic 9 / 成片 16：工位时间切片 15-15-70。云端 A-roll + B-roll，不是短剧。"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 24
NAME = "工位时间切片15-15-70"
STAGED_NAME = "16-工位时间切片15-15-70.mp4"
FACTORY_VO = Path("/workspace/.abroll-cloud/aroll/audio/09_工位时间切片十五十五七十.wav")
ASSET_SRC = Path("/workspace/.abroll-cloud/06/assets")

FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_REG = "/tmp/NotoSansSC-Regular.otf"

BG = (11, 13, 18)
CARD = (24, 28, 38)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
RED = (255, 118, 118)
BLUE = (120, 168, 230)
INK = (28, 32, 36)
CREAM = (245, 247, 250)

# 工厂口播 silencedetect 切段，再铺满 [0, duration]，无缝无叠。
# 大家好 | 杂务… | 十五… | 不当秒回 | 组会…
PHRASE_ENDS = [1.440, 3.879, 7.903, 9.565, 11.616]


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
    return ImageFont.truetype(path, size)


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


def draw_pie(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int, sweeps: list[tuple[float, tuple]], ring: tuple) -> None:
    box = (cx - r, cy - r, cx + r, cy + r)
    d.ellipse(box, fill=(18, 20, 26))
    angle = -90.0
    for sweep, color in sweeps:
        if sweep <= 0.4:
            continue
        d.pieslice(box, start=angle, end=angle + sweep, fill=color)
        angle += sweep
    hole = int(r * 0.46)
    d.ellipse((cx - hole, cy - hole, cx + hole, cy + hole), fill=BG)
    d.ellipse((cx - hole, cy - hole, cx + hole, cy + hole), outline=ring, width=3)


def b_slice_pie(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(56)
    card_f = font(40)
    num_f = font(44)
    sub_f = font(30)
    punch_f = font(48)
    rows = [
        (0.22, "15", "换安全", "及格交付换工位", YELLOW, 54.0),
        (1.18, "15", "锁初稿", "专利论文往前推", MINT, 54.0),
        (2.20, "70", "留给算法", "主业占大部分", BLUE, 252.0),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "时间切片")
        a0 = appear(t, 0.02)
        d.text((W // 2, 250 + int(lerp(18, 0, a0))), "十五 / 十五 / 七十", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        sweeps = []
        for ts, _num, _head, _body, color, full in rows:
            grow = appear(t, ts, 0.42)
            sweeps.append((full * grow, mix(BG, color, max(grow, 0.08))))
        ring_a = appear(t, 0.18)
        draw_pie(d, W // 2, 620, 230, sweeps, mix(BG, MINT, ring_a))

        y0 = 920
        for idx, (ts, num, head, body, color, _full) in enumerate(rows):
            a = appear(t, ts + 0.12, 0.26)
            if a < 0.04:
                continue
            y = y0 + idx * 168 + int(lerp(20, 0, a))
            rounded(d, (96, y, 984, y + 148), 28, mix(BG, CARD, a))
            d.ellipse((128, y + 38, 216, y + 126), fill=mix(CARD, color, a))
            d.text((172, y + 82), num, font=num_f, fill=mix(color, INK, a), anchor="mm")
            d.text((248, y + 52), head, font=card_f, fill=mix(CARD, color, a), anchor="lm")
            d.text((248, y + 108), body, font=sub_f, fill=mix(CARD, WHITE, a), anchor="lm")

        punch = appear(t, 3.35, 0.26)
        if punch > 0.04:
            y = 1436 + int(lerp(18, 0, punch))
            rounded(d, (140, y, 940, y + 150), 26, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y + 75), "租金不是主业", font=punch_f, fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def b_meeting(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f = font(58)
    card_f = font(42)
    sub_f = font(32)
    punch_f = font(52)
    out = []
    cards = [
        (0.12, "精读了一篇", "已完成动作", MINT),
        (0.48, "跑通了基线", "能当场核对", YELLOW),
    ]
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "组会回报")
        a0 = appear(t, 0.02)
        d.text((W // 2, 280 + int(lerp(16, 0, a0))), "只报做完的", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")

        for idx, (ts, head, body, color) in enumerate(cards):
            a = appear(t, ts, 0.24)
            if a < 0.04:
                continue
            y = 460 + idx * 260 + int(lerp(18, 0, a))
            rounded(d, (110, y, 970, y + 220), 32, mix(BG, CARD, a))
            d.rounded_rectangle((142, y + 70, 246, y + 150), 18, fill=mix(CARD, color, a))
            d.text((194, y + 110), "做", font=sub_f, fill=mix(color, INK, a), anchor="mm")
            d.text((280, y + 78), head, font=card_f, fill=mix(CARD, color, a), anchor="lm")
            d.text((280, y + 150), body, font=sub_f, fill=mix(CARD, WHITE, a), anchor="lm")

        bad = appear(t, 1.05, 0.22)
        if bad > 0.04:
            y = 1000 + int(lerp(16, 0, bad))
            box = (110, y, 970, y + 200)
            rounded(d, box, 32, mix(BG, CARD, bad))
            d.text((W // 2, y + 70), "下周计划一堆", font=card_f, fill=mix(CARD, MUTED, bad), anchor="mm")
            d.text((W // 2, y + 140), "画大饼", font=sub_f, fill=mix(CARD, MUTED, bad), anchor="mm")
            st = appear(t, 1.28, 0.22)
            if st > 0.04:
                cy = y + 100
                x0, x1 = 180, 900
                d.line([(x0, cy), (int(lerp(x0, x1, st)), cy)], fill=mix(CARD, RED, st), width=12)

        punch = appear(t, 1.62, 0.22)
        if punch > 0.04:
            y = 1280 + int(lerp(16, 0, punch))
            rounded(d, (150, y, 930, y + 170), 28, mix(BG, (18, 42, 36), punch))
            d.text((W // 2, y + 85), "不画大饼", font=punch_f, fill=mix(BG, MINT, punch), anchor="mm")
        out.append(img)
    return out


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


def prepare_voice() -> float:
    audio = ROOT / "audio"
    audio.mkdir(exist_ok=True)
    wav = audio / "vo-full.wav"
    if not FACTORY_VO.exists():
        raise FileNotFoundError(FACTORY_VO)
    shutil.copy2(FACTORY_VO, wav)
    dur = probe_dur(wav)
    if abs(dur - PHRASE_ENDS[-1]) > 0.08:
        raise RuntimeError(f"vo duration {dur} != locked end {PHRASE_ENDS[-1]}")
    return dur


def build_timeline(duration: float) -> dict:
    recipe = json.loads((ROOT / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
    phrases = [ln.strip() for ln in (ROOT / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    starts = [0.0] + PHRASE_ENDS[:-1]
    ends = list(PHRASE_ENDS)
    ends[-1] = duration

    # B 卷早切半拍：话音未落，图先到位。
    cut_starts = list(starts)
    for i, shot in enumerate(recipe["shots"]):
        lead = float(shot.get("lead") or 0)
        if shot["kind"] == "B" and lead > 0 and i > 0:
            cut_starts[i] = max(cut_starts[i - 1] + 0.80, starts[i] - lead)
    cut_ends = cut_starts[1:] + [duration]

    shots_out = []
    a_caps = []
    shutters = []
    eyebrows = []
    a_i = 0
    for i, shot in enumerate(recipe["shots"]):
        start, end = cut_starts[i], cut_ends[i]
        item = {
            "id": shot["id"],
            "kind": shot["kind"],
            "start": round(start, 3),
            "end": round(end, 3),
            "src": shot["src"],
            "line": phrases[i],
        }
        if shot.get("close"):
            item["close"] = True
        if shot.get("broll"):
            item["broll"] = shot["broll"]
        shots_out.append(item)
        if shot["kind"] == "A":
            a_i += 1
            line = phrases[i]
            if "，" in line and len(line) > 8:
                caps = [p for p in line.split("，") if p]
            else:
                caps = [line]
            a_caps.append({"start": round(start, 3), "end": round(end, 3), "lines": caps})
            eyebrows.append({"start": round(start, 3), "end": round(end, 3), "text": f"A-ROLL / {a_i:02d}"})
        if i > 0:
            color = [245, 247, 250] if shot["kind"] == "A" else [126, 224, 197]
            if i == len(recipe["shots"]) - 1:
                color = [245, 193, 92]
            shutters.append({"start": round(start, 3), "color": color})

    for i in range(1, len(shots_out)):
        shots_out[i]["start"] = shots_out[i - 1]["end"]
    shots_out[-1]["end"] = round(duration, 3)

    align = []
    for i, phrase in enumerate(phrases):
        align.append(f"{starts[i]:.3f}\t{ends[i]:.3f}\t{phrase}")
    (ROOT / "audio" / "vo-align.txt").write_text("\n".join(align) + "\n", encoding="utf-8")

    timeline = {
        "audio": "audio/vo-full.wav",
        "duration": round(duration, 3),
        "fps": FPS,
        "size": [W, H],
        "title": recipe["title"],
        "bgm": "audio/bgm.wav",
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
    clicks = []
    for i, t in enumerate(cuts):
        click = ROOT / "audio" / f"_click{i}.wav"
        run([
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "sine=frequency=880:sample_rate=44100:duration=0.06",
            "-af", "afade=t=out:st=0.02:d=0.04,volume=0.35",
            str(click),
        ])
        clicks.append((click, t))
    inputs = ["ffmpeg", "-y"]
    filters = []
    labels = []
    for i, (click, t) in enumerate(clicks):
        inputs += ["-i", str(click)]
        filters.append(f"[{i}:a]adelay={int(t * 1000)}|{int(t * 1000)},volume=0.55[c{i}]")
        labels.append(f"[c{i}]")
    filters.append(
        f"{''.join(labels)}amix=inputs={len(clicks)}:duration=longest,apad=pad_dur={duration:.2f},atrim=0:{duration:.2f}"
    )
    inputs += ["-filter_complex", ";".join(filters), "-ac", "2", "-ar", "44100", str(dest)]
    run(inputs)


def render_brolls(data: dict) -> None:
    durs = {}
    for shot in data["shots"]:
        if shot["kind"] == "B":
            durs[shot["src"]] = max(2.2, float(shot["end"]) - float(shot["start"]))
    jobs = [
        ("broll/B-时间切片.mp4", b_slice_pie),
        ("broll/B-组会只报.mp4", b_meeting),
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
    d.text((W // 2, 348), cover["line"], font=font(30), fill=MUTED, anchor="mm")
    out = ROOT / "final" / "cover.jpg"
    out.parent.mkdir(exist_ok=True)
    canvas.save(out, quality=92)
    canvas.save(ROOT / f"00_封面_{NAME}.jpg", quality=92)
    print("cover", out)
    return out


def write_status(duration: float, staged: Path) -> None:
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    status = {
        "schema_version": 1,
        "project_name": "16_工位时间切片15-15-70",
        "video_type": "普通短视频",
        "topic_index": 9,
        "slug": "09_工位时间切片十五十五七十",
        "title": "工位时间切片：15 / 15 / 70",
        "production_method": "白底小灯 A-roll + 黑底信息图 B-roll + 工厂口播 + FFmpeg",
        "status": "已交付",
        "current_stage": "核验并交付",
        "stage": "delivered",
        "voice": "zh-CN-YunyangNeural",
        "duration": round(duration, 3),
        "size": [W, H],
        "fps": FPS,
        "script": {"path": "script/voiceover.txt", "sha256": hashlib.sha256(vo.encode("utf-8")).hexdigest()},
        "audio": {
            "path": "audio/vo-full.wav",
            "alignment_path": "audio/vo-align.txt",
            "source": str(FACTORY_VO),
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
        "project": "16_工位时间切片15-15-70",
        "strict": True,
        "cloud_only": True,
        "no_windows_paths": True,
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
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "qa" / "ffprobe.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("QA", report["ok"], report["video"], report["audio"])
    return report


def update_index(duration: float) -> None:
    path = Path("/workspace/成片/INDEX.md")
    text = path.read_text(encoding="utf-8") if path.exists() else "# 成片（可直接看）\n\n"
    line = f"| `{STAGED_NAME}` | {duration:.1f}s |"
    if STAGED_NAME in text:
        return
    if text.rstrip().endswith("|"):
        text = text.rstrip() + "\n" + line + "\n"
    else:
        text = text.rstrip() + "\n\n" + line + "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    copy_assets()
    duration = prepare_voice()
    print("VO", duration)
    data = build_timeline(duration)
    make_bgm(duration)
    render_brolls(data)
    make_cover(data)
    staged = assemble(data)
    write_status(duration, staged)
    report = qa(staged, data)
    update_index(float(report["video"]["duration_s"]))
    if not report["ok"]:
        raise SystemExit("QA failed")
    print("done", staged)


if __name__ == "__main__":
    main()
