# -*- coding: utf-8 -*-
"""17 · 从窗台纸鹤拉到地球夜侧 — 云端 A-roll + B-roll（非剧情）。"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 24
NAME = "从窗台纸鹤拉到地球夜侧"
STAGED = Path("/workspace/成片") / f"17-{NAME}.mp4"
VOICE_SRC = Path("/workspace/.abroll-cloud/aroll/audio/10_窗台纸鹤拉到地球夜侧.wav")
ASSET_SRC = Path("/workspace/.abroll-cloud/06/assets")
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_RG = "/tmp/NotoSansSC-Regular.otf"

BG = (11, 13, 18)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
CARD = (24, 28, 38)
CREAM = (245, 247, 250)
INK = (28, 32, 36)

# Energy islands on factory VO (12.456s). B 卷早切半拍。
# 大家好 0.33–0.65；拉开 1.49–3.55；落回 4.44–6.14；翻转 6.89–9.54；收束 10.31–11.62
ALIGN = [
    (0.000, 1.280, "大家好"),
    (1.280, 4.280, "从窗台纸鹤，拉到地球夜侧"),
    (4.280, 6.780, "再落回掌心的玻璃弹珠"),
    (6.780, 10.200, "同一个东西，尺度一换，意思就翻了"),
    (10.200, 12.456, "不讲人物，只讲尺度"),
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
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", size)


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


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


def prepare_inputs() -> float:
    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "audio").mkdir(exist_ok=True)
    vo = ROOT / "audio" / "vo-full.wav"
    if not vo.exists() or vo.stat().st_size < 1000:
        shutil.copy2(VOICE_SRC, vo)
    for name in ("V-挥手.mp4", "V-摊手.mp4", "V-点赞.mp4", "A-角色-小灯-摊手.jpg"):
        dest = ROOT / "assets" / name
        src = ASSET_SRC / name
        if src.exists() and (not dest.exists() or dest.stat().st_size < 1000):
            shutil.copy2(src, dest)
    dur = probe(vo)
    return dur


def write_align(dur: float) -> list[tuple[float, float, str]]:
    cues = [(s, e if i < len(ALIGN) - 1 else dur, line) for i, (s, e, line) in enumerate(ALIGN)]
    cues[-1] = (cues[-1][0], dur, cues[-1][2])
    text = "\n".join(f"[{int(s * 1000)}ms-{int(e * 1000)}ms] {line}" for s, e, line in cues) + "\n"
    (ROOT / "audio" / "vo-align.txt").write_text(text, encoding="utf-8")
    return cues


def write_timeline(cues: list[tuple[float, float, str]], dur: float) -> dict:
    recipe = json.loads((ROOT / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
    shots, a_caps, shutters, eyebrows = [], [], [], []
    a_i = 0
    for i, shot in enumerate(recipe["shots"]):
        start, end, line = cues[i]
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
        shots.append(item)
        if shot["kind"] == "A":
            a_i += 1
            if "，" in line and len(line) > 10:
                left, right = line.split("，", 1)
                lines = [left, right]
            else:
                lines = [line]
            a_caps.append({"start": round(start, 3), "end": round(end, 3), "lines": lines})
            eyebrows.append({"start": round(start, 3), "end": round(end, 3), "text": f"A-ROLL / {a_i:02d}"})
        if i > 0:
            if shot["kind"] == "B":
                color = [126, 224, 197] if i == 1 else [245, 193, 92]
            else:
                color = [245, 247, 250]
            shutters.append({"start": round(start, 3), "color": color})

    data = {
        "audio": "audio/vo-full.wav",
        "duration": round(dur, 3),
        "fps": FPS,
        "size": [W, H],
        "title": NAME,
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
    fnt = font(28)
    tw, th = text_wh(draw, label, fnt)
    x, y = 72, 86
    draw.rounded_rectangle((x - 18, y - 12, x + tw + 22, y + th + 14), radius=20, fill=mix(BG, (20, 42, 38), a))
    draw.text((x, y), label, font=fnt, fill=mix(BG, MINT, a))


def punch_card(base: Image.Image, t: float, start: float, title: str) -> None:
    a = appear(t, start, 0.28)
    if a <= 0.04:
        return
    y = 1548 + int((1 - a) * 26)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((90, y, 990, y + 220), radius=34, fill=(*CARD, int(228 * a)))
    d.text((540, y + 110), title, font=font(52), fill=(*mix(CARD, WHITE, a), 255), anchor="mm")
    out = Image.alpha_composite(base.convert("RGBA"), layer)
    base.paste(out.convert("RGB"))


def draw_ladder(draw: ImageDraw.ImageDraw, t: float, duration: float, labels: list[str]) -> None:
    if not labels:
        return
    stage = min(len(labels) - 1, int((t / max(duration, 0.01)) * len(labels)))
    fnt = font(26)
    y = 1788
    gap = 220
    x0 = (W - gap * (len(labels) - 1)) // 2
    for i, lab in enumerate(labels):
        a = appear(t, 0.08 + i * 0.12, 0.2)
        if a <= 0:
            continue
        col = MINT if i <= stage else MUTED
        draw.text((x0 + i * gap, y), lab, font=fnt, fill=mix(BG, col, a), anchor="mm")
        if i < len(labels) - 1:
            draw.line([(x0 + i * gap + 56, y), (x0 + (i + 1) * gap - 56, y)], fill=mix(BG, MUTED, a * 0.7), width=3)


def render_zoom(duration: float, dest: Path) -> None:
    crane = Image.open(ROOT / "broll/stills/t10-crane-sill.png")
    city = Image.open(ROOT / "broll/stills/t10-window-city.png")
    earth = Image.open(ROOT / "broll/stills/t10-earth-night.png")
    n = max(1, round(duration * FPS))
    frames = []
    for i in range(n):
        t = i / FPS
        p = t / max(duration, 0.01)
        if p < 0.36:
            local = ease(p / 0.36)
            img = cover_crop(crane, lerp(1.34, 1.08, local), 0.50, 0.58)
            fade = 0.0
            nxt = None
        elif p < 0.68:
            local = ease((p - 0.36) / 0.32)
            img = cover_crop(crane, lerp(1.08, 1.02, local), 0.50, 0.50)
            nxt = cover_crop(city, lerp(1.20, 1.06, local), 0.50, 0.42)
            fade = local
        else:
            local = ease((p - 0.68) / 0.32)
            img = cover_crop(city, lerp(1.06, 1.02, local), 0.50, 0.40)
            nxt = cover_crop(earth, lerp(1.28, 1.02, local), 0.50, 0.55)
            fade = local
        if nxt is not None and fade > 0:
            img = Image.blend(img, nxt, fade)
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "尺度 拉开")
        draw_ladder(d, t, duration, ["纸鹤", "城市", "地球"])
        punch_card(img, t, max(0.2, duration - 0.95), "窗台 → 地球夜侧")
        frames.append(img)
    frames_to_mp4(frames, dest)
    frames[min(len(frames) // 2, len(frames) - 1)].save(dest.with_suffix(".jpg"), quality=90)


def render_marble(duration: float, dest: Path) -> None:
    still = Image.open(ROOT / "broll/stills/t10-marble-palm.png")
    n = max(1, round(duration * FPS))
    frames = []
    for i in range(n):
        t = i / FPS
        p = ease(t / max(duration, 0.01))
        img = cover_crop(still, lerp(1.06, 1.26, p), 0.50, 0.52)
        d = ImageDraw.Draw(img)
        tag_chip(d, t, "尺度 落回")
        punch_card(img, t, 0.55, "同一夜城，缩回掌心")
        frames.append(img)
    frames_to_mp4(frames, dest)
    frames[min(len(frames) // 2, len(frames) - 1)].save(dest.with_suffix(".jpg"), quality=90)


def render_brolls(data: dict) -> None:
    for shot in data["shots"]:
        if shot["kind"] != "B":
            continue
        dur = float(shot["end"]) - float(shot["start"])
        dest = ROOT / shot["src"]
        print("broll", dest.name, f"{dur:.2f}s")
        if shot.get("broll") == "zoom_out":
            render_zoom(dur, dest)
        else:
            render_marble(dur, dest)


def render_caps(data: dict) -> None:
    dur = float(data["duration"])
    cues = [(c["start"], c["end"], c["lines"]) for c in data["a_caps"]]
    shutters = [(s["start"], tuple(s["color"])) for s in data["shutters"]]
    brows = [(e["start"], e["end"], e["text"]) for e in data["eyebrows"]]
    n = max(1, round(dur * FPS))
    dest = ROOT / "shots" / "caption_layer.mov"
    dest.parent.mkdir(exist_ok=True)

    def frame_at(t: float) -> Image.Image:
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        label = next((text for s, e, text in brows if s <= t < e), None)
        if label:
            d.rectangle((76, 88, 120, 92), fill=(*MINT, 230))
            d.text((136, 76), label, font=font(22), fill=(90, 98, 108, 220))
        lines = next((ln for s, e, ln in cues if s <= t < e), None)
        if lines:
            fnt = font(56 if len(lines) == 1 and max(len(s) for s in lines) <= 8 else 48)
            dummy = ImageDraw.Draw(img)
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
            y = 168
            pill = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
            pd = ImageDraw.Draw(pill)
            pd.rounded_rectangle((0, 0, box_w - 1, box_h - 1), radius=28, fill=(22, 24, 28, 214))
            pd.rectangle((10, 14, 20, box_h - 14), fill=(*MINT, 235))
            for j, line in enumerate(lines):
                pd.text((box_w / 2 + 4, pad_y + line_h * j), line, font=fnt, fill=(*WHITE, 255), anchor="mt")
            shadow = pill.filter(ImageFilter.GaussianBlur(8))
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sh.alpha_composite(shadow, (x0, y + 4))
            img.alpha_composite(sh)
            img.alpha_composite(pill, (x0, y))
        for start, color in shutters:
            dt = t - start
            if 0 <= dt <= 0.16:
                p = dt / 0.16
                if p < 0.5:
                    ww = max(2, int(W * p * 2))
                    xx = 0
                else:
                    ww = max(2, int(W * (1 - (p - 0.5) * 2)))
                    xx = W - ww
                layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(layer).rectangle((xx, 0, xx + ww, H), fill=(*color, 235))
                img = Image.alpha_composite(img, layer)
        return img

    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "qtrle", "-pix_fmt", "argb", str(dest),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    for i in range(n):
        proc.stdin.write(frame_at(i / FPS).tobytes())
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(err[-2500:])
    print("caps", dest, n)


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
    run(["ffmpeg", "-y", "-i", str(src), "-t", f"{dur:.3f}", "-vf", vf, "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18", str(dest)])


def make_bgm(dur: float) -> Path:
    dest = ROOT / "audio" / "bgm.wav"
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=196:sample_rate=44100:duration={dur + 2:.2f}",
        "-f", "lavfi", "-i", f"sine=frequency=247:sample_rate=44100:duration={dur + 2:.2f}",
        "-filter_complex",
        "[0:a][1:a]amix=inputs=2:duration=longest,lowpass=f=420,volume=0.22,aformat=sample_rates=44100:channel_layouts=stereo",
        str(dest),
    ])
    return dest


def assemble(data: dict) -> Path:
    shots_dir = ROOT / "shots"
    shots_dir.mkdir(exist_ok=True)
    parts: list[Path] = []
    for shot in data["shots"]:
        dest = shots_dir / f"{shot['id']}.mp4"
        dur = float(shot["end"]) - float(shot["start"])
        print(shot["id"], shot["kind"], f"{dur:.2f}s", shot["src"])
        cut_shot(ROOT / shot["src"], dur, dest, shot["kind"], bool(shot.get("close")))
        parts.append(dest)

    lst = shots_dir / "concat.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    concat = shots_dir / "video_only.mp4"
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
        str(concat),
    ])
    caps = shots_dir / "caption_layer.mov"
    burned = shots_dir / "video_subs.mp4"
    run([
        "ffmpeg", "-y", "-i", str(concat), "-i", str(caps),
        "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an", str(burned),
    ])

    dur = float(data["duration"])
    bgm = make_bgm(dur)
    audio = ROOT / data["audio"]
    final = ROOT / f"00_最终成片_{NAME}.mp4"
    (ROOT / "final").mkdir(exist_ok=True)
    run([
        "ffmpeg", "-y", "-i", str(burned), "-i", str(audio), "-i", str(bgm),
        "-filter_complex",
        "[1:a]loudnorm=I=-16:LRA=11:TP=-1.5,aformat=sample_rates=44100:channel_layouts=stereo[vo];"
        "[2:a]adelay=800|800,volume=0.18,highpass=f=140[bg];"
        "[vo][bg]amix=inputs=2:duration=first:dropout_transition=2,alimiter=limit=0.95[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        str(final),
    ])
    run(["cp", "-f", str(final), str(ROOT / "final" / f"{NAME}.mp4")])
    STAGED.parent.mkdir(parents=True, exist_ok=True)
    run(["cp", "-f", str(final), str(STAGED)])
    print("FINAL", final, "dur", probe(final))
    print("STAGED", STAGED, "dur", probe(STAGED))
    return final


def make_cover(data: dict) -> None:
    src = ROOT / data["cover"]["src"]
    img = cover_crop(Image.open(src), 1.08, 0.50, 0.58)
    overlay = Image.new("RGBA", (W, H), (11, 13, 18, 40))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((72, 96, 1008, 470), radius=36, fill=(22, 24, 28))
    d.text((540, 176), data["cover"]["title"], font=font(46), fill=WHITE, anchor="mm")
    d.text((540, 278), data["cover"]["sub"], font=font(40), fill=MINT, anchor="mm")
    d.text((540, 372), data["cover"]["line"], font=font(30), fill=MUTED, anchor="mm")
    dest = ROOT / f"00_封面_{NAME}.jpg"
    img.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    img.save(ROOT / "final" / "cover.jpg", quality=92)
    print("cover", dest)


def write_docs(dur: float) -> None:
    status = {
        "schema_version": 1,
        "video_type": "普通短视频",
        "slug": "10_窗台纸鹤拉到地球夜侧",
        "topic_index": 10,
        "delivery_index": 17,
        "stage": "delivered",
        "title": NAME,
        "voice": "zh-CN-YunyangNeural",
        "duration": round(dur, 3),
        "size": [W, H],
        "fps": FPS,
        "staged": f"成片/17-{NAME}.mp4",
        "project_final": f"00_最终成片_{NAME}.mp4",
        "cloud_only": True,
        "updated_at": "2026-09-11",
    }
    (ROOT / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = f"""# 17 · 从窗台纸鹤拉到地球夜侧

普通短视频 / 知识口播。**不是**剧情短剧。只讲尺度，不讲人物。

- **选题**：云端 `topics.md` 第 10 条 Earth Zoom Out
- **来源笔记**：`选题与镜头.md`（窗台到宇宙、雨滴里的城、沙漏里的海）；网上格式表 Earth Zoom Out
- **口播**：工厂 `aroll/audio/10_窗台纸鹤拉到地球夜侧.wav`（YunyangNeural，12.456s）
- **类型**：竖屏 A 卷白底小灯 + B 卷无字静帧拉开（中文只在组装层叠）
- **规格**：1080×1920 / 24fps / H.264 + AAC 44100
- **工程成片**：`00_最终成片_{NAME}.mp4`
- **中转**：`/workspace/成片/17-{NAME}.mp4`
- **草稿**：`/workspace/.abroll-cloud/17/`（禁止进 `成片/` 当渲染目录）

## 一条观点

同一个物件，尺度一换，意义翻转：窗台纸鹤 → 城市 → 地球夜侧 → 掌心玻璃弹珠里的同一夜城。

## 镜头

| 镜 | 卷 | 口播 | 画面 |
|----|----|------|------|
| S01 | A | 大家好 | 小灯挥手近景 |
| S02 | B | 从窗台纸鹤，拉到地球夜侧 | 纸鹤特写拉开到夜城再到地球夜侧 |
| S03 | B | 再落回掌心的玻璃弹珠 | 掌心弹珠里倒映夜城 |
| S04 | A | 同一个东西，尺度一换，意思就翻了 | 小灯摊手 |
| S05 | A | 不讲人物，只讲尺度 | 小灯点赞收束 |

未拍可选嵌套镜（雨滴水冠、沙漏里的海）：12 秒口播只锁一个点。
"""
    (ROOT / "项目说明.md").write_text(md, encoding="utf-8")


def qa(final: Path, data: dict) -> None:
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
        "staged_exists": STAGED.exists(),
        "staged_bytes": STAGED.stat().st_size if STAGED.exists() else 0,
    }
    (qa_dir / "check.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not closed or gaps:
        raise SystemExit(f"timeline not closed: {info}")
    if abs(vdur - adur) > 0.25:
        raise SystemExit(f"av mismatch {vdur} vs {adur}")
    print("QA", info)


def main() -> None:
    os.chdir(ROOT)
    dur = prepare_inputs()
    cues = write_align(dur)
    data = write_timeline(cues, dur)
    render_brolls(data)
    render_caps(data)
    final = assemble(data)
    make_cover(data)
    write_docs(probe(final))
    qa(final, data)
    print("done", probe(final))


if __name__ == "__main__":
    main()
