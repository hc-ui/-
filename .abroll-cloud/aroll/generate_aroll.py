# -*- coding: utf-8 -*-
"""Cloud A-roll factory: edge-tts narration + voice/slate preview."""
from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import sys

ROOT = Path("/workspace")
CLOUD = ROOT / ".abroll-cloud"
CATALOG_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else CLOUD / "aroll" / "scout_catalog.json"
CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
AUDIO_DIR = CLOUD / "aroll" / "audio"
SCRATCH = CLOUD / "aroll" / "_scratch"
PREVIEW = ROOT / "成片" / "00-aroll-preview.mp4"
BUILD_PREVIEW = "--no-preview" not in sys.argv
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
W, H, FPS = 1080, 1920, 24
BG, MINT, YELLOW, WHITE, MUTED, CARD = (
    (11, 13, 18),
    (126, 224, 197),
    (245, 193, 92),
    (245, 247, 250),
    (154, 162, 176),
    (24, 28, 38),
)


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout)[-2000:])


def probe(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        text=True,
    )
    return float(out.strip())


async def synth_one(text: str, dest: Path, voice: str) -> None:
    import edge_tts

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".mp3")
    await edge_tts.Communicate(text, voice).save(str(tmp))
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(tmp),
            "-ar",
            "44100",
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(dest),
        ]
    )
    tmp.unlink(missing_ok=True)


def wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    lines, buf = [], ""
    for ch in text:
        trial = buf + ch
        if draw.textlength(trial, font=font) <= max_w:
            buf = trial
        else:
            if buf:
                lines.append(buf)
            buf = ch
    if buf:
        lines.append(buf)
    return lines or [""]


def slate(topic: dict, idx: int, total: int) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    ov = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(ov)
    d.ellipse((-220, -280, 720, 560), fill=(16, 42, 38))
    d.ellipse((480, 1180, 1400, 2100), fill=(42, 32, 16))
    from PIL import ImageFilter

    img = Image.blend(img, ov.filter(ImageFilter.GaussianBlur(110)), 0.58)
    draw = ImageDraw.Draw(img)
    f_tag = ImageFont.truetype(FONT, 36)
    f_title = ImageFont.truetype(FONT, 64)
    f_sub = ImageFont.truetype(FONT, 40)
    f_body = ImageFont.truetype(FONT, 38)
    f_small = ImageFont.truetype(FONT, 28)
    tag = f"A-ROLL  {idx:02d}/{total:02d}"
    tw = draw.textlength(tag, font=f_tag)
    draw.rounded_rectangle((72, 120, 72 + tw + 48, 188), 22, fill=(20, 42, 38))
    draw.text((96, 132), tag, font=f_tag, fill=MINT)
    draw.text((72, 240), topic["title"], font=f_title, fill=WHITE)
    draw.text((72, 330), topic["cover_sub"], font=f_sub, fill=YELLOW)
    draw.rounded_rectangle((72, 430, W - 72, 1480), 36, fill=CARD)
    body_lines = wrap(draw, topic["voiceover"], f_body, W - 180)
    y = 480
    for line in body_lines:
        draw.text((108, y), line, font=f_body, fill=WHITE)
        y += 64
    draw.text((72, 1560), topic["cover_line"], font=f_sub, fill=MINT)
    draw.text((72, 1740), topic["slug"], font=f_small, fill=MUTED)
    draw.text((72, 1790), "VOICE + SLATE  /  非成片精剪", font=f_small, fill=MUTED)
    return img


def clip_from_slate(png: Path, wav: Path, dest: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(png),
            "-i",
            str(wav),
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(FPS),
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(dest),
        ]
    )


async def main() -> None:
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    voice = CATALOG["voice"]
    topics = CATALOG["topics"]
    manifest = []
    clips = []
    for i, topic in enumerate(topics, 1):
        wav = AUDIO_DIR / f"{topic['slug']}.wav"
        print(f"tts {topic['slug']}", flush=True)
        await synth_one(topic["voiceover"], wav, voice)
        dur = probe(wav)
        if BUILD_PREVIEW:
            png = SCRATCH / f"{topic['slug']}.png"
            slate(topic, i, len(topics)).save(png, quality=92)
            mp4 = SCRATCH / f"{topic['slug']}.mp4"
            clip_from_slate(png, wav, mp4)
            clips.append(mp4)
        manifest.append(
            {
                "slug": topic["slug"],
                "title": topic["title"],
                "wav": str(wav.relative_to(ROOT)),
                "duration": round(dur, 3),
                "chars": len(topic["voiceover"]),
            }
        )
        print(f"  {dur:.2f}s", flush=True)

    preview_dur = None
    if BUILD_PREVIEW and clips:
        concat = SCRATCH / "concat.txt"
        concat.write_text("".join(f"file '{c}'\n" for c in clips), encoding="utf-8")
        run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat),
                "-c",
                "copy",
                str(PREVIEW),
            ]
        )
        preview_dur = round(probe(PREVIEW), 3)
        print("preview", PREVIEW, preview_dur)
    man_path = AUDIO_DIR / f"manifest-{CATALOG_PATH.stem}.json"
    man_path.write_text(
        json.dumps(
            {
                "catalog": CATALOG_PATH.name,
                "voice": voice,
                "preview": "成片/00-aroll-preview.mp4" if preview_dur else None,
                "preview_duration": preview_dur,
                "items": manifest,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("manifest", man_path)


if __name__ == "__main__":
    asyncio.run(main())
