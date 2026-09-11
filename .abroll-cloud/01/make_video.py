# -*- coding: utf-8 -*-
"""Cloud-only A-roll + B-roll assemble. Drafts stay in this folder."""
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 24
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
BG = (11, 13, 18)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
CARD = (24, 28, 38)
RED = (255, 118, 118)


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout)[-2500:])


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size)


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def mix(c0, c1, a: float):
    a = max(0.0, min(1.0, a))
    return tuple(int(c1[i] * a + c0[i] * (1 - a)) for i in range(3))


def cover(im: Image.Image, w: int, h: int, zoom: float = 1.0, pan_y: float = 0.0) -> Image.Image:
    im = im.convert("RGB")
    scale = max(w / im.width, h / im.height) * zoom
    nw, nh = max(w, int(im.width * scale)), max(h, int(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - w) // 2
    y = int((nh - h) * (0.42 + pan_y))
    y = max(0, min(nh - h, y))
    return im.crop((x, y, x + w, y + h))


def pill(base: Image.Image, lines: list[str], y: int = 168) -> None:
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
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pill_im = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill_im)
    pd.rounded_rectangle((0, 0, box_w - 1, box_h - 1), radius=28, fill=(22, 24, 28, 214))
    pd.rectangle((10, 14, 20, box_h - 14), fill=(*MINT, 235))
    for i, line in enumerate(lines):
        pd.text((box_w / 2 + 4, pad_y + line_h * i), line, font=fnt, fill=(*WHITE, 255), anchor="mt")
    shadow = pill_im.filter(ImageFilter.GaussianBlur(8))
    layer.alpha_composite(shadow, (x0, y + 4))
    layer.alpha_composite(pill_im, (x0, y))
    out = Image.alpha_composite(base.convert("RGBA"), layer)
    base.paste(out.convert("RGB"))


def eyebrow(base: Image.Image, label: str) -> None:
    d = ImageDraw.Draw(base)
    fnt = font(22)
    d.rectangle((76, 88, 120, 92), fill=MINT)
    d.text((136, 74), label, font=fnt, fill=(90, 98, 108))


def tag_chip(base: Image.Image, label: str, color=MINT) -> None:
    d = ImageDraw.Draw(base)
    fnt = font(28)
    x0, y0, x1, y1 = d.textbbox((0, 0), label, font=fnt)
    tw, th = x1 - x0, y1 - y0
    box = (72, 86, 72 + tw + 44, 86 + th + 28)
    d.rounded_rectangle(box, radius=20, fill=(20, 42, 38))
    d.text((94, 96), label, font=fnt, fill=color)


def big_card(base: Image.Image, title: str, t_local: float) -> None:
    a = ease((t_local - 0.12) / 0.38)
    if a <= 0:
        return
    y = 1420 + int((1 - a) * 28)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((90, y, 990, y + 220), radius=36, fill=(*CARD, int(230 * a)))
    fnt = font(64)
    col = mix(CARD, WHITE, a)
    d.text((540, y + 110), title, font=fnt, fill=(*col, 255), anchor="mm")
    out = Image.alpha_composite(base.convert("RGBA"), layer)
    base.paste(out.convert("RGB"))


def shutter(base: Image.Image, t_local: float, color) -> Image.Image:
    if t_local < 0 or t_local > 0.16:
        return base
    p = t_local / 0.16
    if p < 0.5:
        w = max(2, int(W * p * 2))
        x0 = 0
    else:
        w = max(2, int(W * (1 - (p - 0.5) * 2)))
        x0 = W - w
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(layer).rectangle((x0, 0, x0 + w, H), fill=(*color, 235))
    return Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")


def split_line(text: str) -> list[str]:
    text = text.strip("。")
    if "，" in text and len(text) > 8:
        return [p + "，" if i == 0 else p + "。" for i, p in enumerate(text.split("，", 1))]
    return [text + "。"] if not text.endswith("。") else [text]


def frame_a(src: Path, t_local: float, dur: float, shot: dict) -> Image.Image:
    zoom = 1.12 if shot.get("close") else 1.04
    pan = -0.08 + 0.04 * (t_local / max(dur, 0.01))
    if shot.get("close"):
        pan = -0.18 + 0.03 * (t_local / max(dur, 0.01))
        zoom = 1.22 - 0.04 * (t_local / max(dur, 0.01))
    img = cover(Image.open(src), W, H, zoom=zoom, pan_y=pan)
    eyebrow(img, f"A-ROLL / {shot['id']}")
    pill(img, split_line(shot["line"]))
    return shutter(img, t_local, MINT)


def frame_b(src: Path, t_local: float, dur: float, shot: dict) -> Image.Image:
    zoom = 1.06 + 0.05 * (t_local / max(dur, 0.01))
    base = Image.new("RGB", (W, H), BG)
    photo = cover(Image.open(src), W, H, zoom=zoom, pan_y=-0.06 + 0.08 * (t_local / max(dur, 0.01)))
    # darken lower third so cards read
    grad = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        if y > 1180:
            gd.line((0, y, W, y), fill=int(min(210, (y - 1180) * 0.55)))
    dark = Image.new("RGB", (W, H), BG)
    photo = Image.composite(dark, photo, grad)
    base.paste(photo)
    tag = shot.get("tag", "B-ROLL")
    color = RED if tag.startswith("错") else MINT
    tag_chip(base, tag, color)
    if shot.get("card"):
        big_card(base, shot["card"], t_local)
    pill(base, split_line(shot["line"]), y=210)
    return shutter(base, t_local, YELLOW if shot.get("card") == "一句结果" else MINT)


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
    err = proc.stderr.read().decode("utf-8", "replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(err[-2000:])


def make_bgm(dest: Path, dur: float) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"sine=frequency=196:duration={dur:.3f}",
        "-f", "lavfi", "-i", f"sine=frequency=247:duration={dur:.3f}",
        "-f", "lavfi", "-i", f"sine=frequency=294:duration={dur:.3f}",
        "-filter_complex",
        "amix=inputs=3:duration=longest,lowpass=f=420,volume=0.07,alimiter=limit=0.25",
        "-ac", "2", "-ar", "44100", str(dest),
    ])


def main() -> None:
    data = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
    shots = data["shots"]
    audio = ROOT / data["audio"]
    dur = float(data["duration"])
    shots_dir = ROOT / "shots"
    shots_dir.mkdir(exist_ok=True)
    parts: list[Path] = []
    for shot in shots:
        start, end = float(shot["start"]), float(shot["end"])
        length = end - start
        n = max(1, round(length * FPS))
        src = ROOT / shot["src"]
        frames = []
        for i in range(n):
            t_local = i / FPS
            if shot["kind"] == "A":
                frames.append(frame_a(src, t_local, length, shot))
            else:
                frames.append(frame_b(src, t_local, length, shot))
        dest = shots_dir / f"{shot['id']}.mp4"
        print(shot["id"], shot["kind"], f"{length:.2f}s", src.name)
        frames_to_mp4(frames, dest)
        parts.append(dest)

    lst = shots_dir / "concat.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    concat = shots_dir / "video_only.mp4"
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-r", str(FPS), str(concat),
    ])

    bgm = ROOT / "audio" / "bgm.wav"
    make_bgm(bgm, dur)
    final_dir = ROOT / "final"
    final_dir.mkdir(exist_ok=True)
    mixed = final_dir / f"{data['title']}.mp4"
    run([
        "ffmpeg", "-y",
        "-i", str(concat),
        "-i", str(audio),
        "-i", str(bgm),
        "-filter_complex",
        "[1:a]loudnorm=I=-16:LRA=11:TP=-1.5,aformat=sample_rates=44100:channel_layouts=stereo[vo];"
        "[2:a]volume=0.18,adelay=200|200[bg];"
        "[vo][bg]amix=inputs=2:duration=first:dropout_transition=2,alimiter=limit=0.92[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        str(mixed),
    ])

    # cover from first A-roll still
    cover_img = cover(Image.open(ROOT / "assets/A-挥手.jpg"), W, H, zoom=1.18, pan_y=-0.16)
    d = ImageDraw.Draw(cover_img)
    d.rounded_rectangle((90, 90, 990, 430), radius=36, fill=(11, 13, 18, 220))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle((90, 90, 990, 430), radius=36, fill=(11, 13, 18, 200))
    cover_img = Image.alpha_composite(cover_img.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(cover_img)
    d.text((540, 180), "周报为什么", font=font(72), fill=WHITE, anchor="mm")
    d.text((540, 280), "没人读", font=font(92), fill=MINT, anchor="mm")
    d.text((540, 370), "先写结果 · 再写动作", font=font(36), fill=YELLOW, anchor="mm")
    cover_path = final_dir / "cover.jpg"
    cover_img.save(cover_path, quality=92)

    dest_root = ROOT.parent.parent / "成片"
    dest_root.mkdir(exist_ok=True)
    out = dest_root / "01-周报为什么没人读.mp4"
    run(["ffmpeg", "-y", "-i", str(mixed), "-c", "copy", str(out)])
    print("FINAL", out, "dur", dur)


if __name__ == "__main__":
    main()
