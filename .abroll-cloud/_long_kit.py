#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared long-cut A/B-roll kit. No freeze-pad. Cloud only."""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 24
VOICE = "zh-CN-YunyangNeural"
ASSET_SRC = Path("/workspace/.abroll-cloud/06/assets")
FONT_BD = "/tmp/NotoSansSC-Bold.otf"
FONT_REG = "/tmp/NotoSansSC-Regular.otf"
FONT_FALLBACK = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

BG = (11, 13, 18)
CARD = (24, 28, 38)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
CREAM = (245, 247, 250)
RED = (255, 118, 118)
AMBER = (255, 168, 76)
INK = (22, 24, 28)
LEAD = 0.28
TARGET_LO, TARGET_HI = 40.0, 50.0
HARD_LO, HARD_HI = 30.0, 60.0
MAX_TPAD_S = 0.0  # freeze-pad forbidden


def zh_sec(sec: float) -> str:
    return f"{sec:.1f}秒"


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
    for path in ((FONT_BD if bold else FONT_REG), FONT_FALLBACK):
        try:
            return ImageFont.FreeTypeFont(path, size) if False else ImageFont.truetype(path, size)
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


def breathe(t: float, amp: float = 5.0) -> int:
    return int(amp * math.sin(t * 1.35))


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


def strike_box(draw: ImageDraw.ImageDraw, box, progress: float, color) -> None:
    x0, y0, x1, y1 = box
    if progress <= 0.04:
        return
    mid = (y0 + y1) / 2
    x_end = lerp(x0 + 24, x1 - 24, min(1.0, progress))
    draw.line([(x0 + 24, mid), (x_end, mid)], fill=color, width=10)


def check_badge(draw, cx: int, cy: int, a: float) -> None:
    if a <= 0.04:
        return
    r = 36
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=mix(CARD, (18, 56, 46), a))
    col = mix(CARD, MINT, a)
    draw.line([(cx - 16, cy + 2), (cx - 4, cy + 16), (cx + 20, cy - 14)], fill=col, width=8)


def x_mark(draw, cx: int, cy: int, a: float, size: int = 28) -> None:
    if a <= 0.04:
        return
    col = mix(CARD, RED, a)
    draw.line([(cx - size, cy - size), (cx + size, cy + size)], fill=col, width=10)
    draw.line([(cx + size, cy - size), (cx - size, cy + size)], fill=col, width=10)


def split_caption(line: str) -> list[str]:
    line = line.strip("。．. ")
    if "，" in line and len(line) > 8:
        parts = [p for p in line.split("，") if p]
        if 1 < len(parts) <= 2:
            return parts
    return [line]


def ticks_to_sec(v: float) -> float:
    return float(v) / 10_000_000.0


def close_align(aligned: list[tuple[float, float, str]], duration: float) -> list[tuple[float, float, str]]:
    aligned[0] = (0.0, aligned[0][1], aligned[0][2])
    for i in range(1, len(aligned)):
        aligned[i] = (aligned[i - 1][1], aligned[i][1], aligned[i][2])
    last_s, _, last_p = aligned[-1]
    aligned[-1] = (last_s, duration, last_p)
    return aligned


def weight_align(phrases: list[str], duration: float) -> list[tuple[float, float, str]]:
    weights = [max(1, len(p.replace("，", "").replace("。", ""))) for p in phrases]
    total = sum(weights)
    t = 0.0
    aligned = []
    for phrase, w in zip(phrases, weights):
        span = duration * (w / total)
        aligned.append((t, t + span, phrase))
        t += span
    return close_align(aligned, duration)


def detect_sentence_cues(wav: Path, phrases: list[str], duration: float) -> list[tuple[float, float, str]]:
    proc = subprocess.run(
        ["ffmpeg", "-i", str(wav), "-af", "silencedetect=noise=-32dB:d=0.12", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    log = proc.stderr
    starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", log)]
    silences: list[tuple[float, float]] = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else duration
        silences.append((s, min(e, duration)))
    speech: list[tuple[float, float]] = []
    cursor = 0.0
    for s, e in silences:
        if s - cursor >= 0.18:
            speech.append((cursor, s))
        cursor = max(cursor, e)
    if duration - cursor >= 0.18:
        speech.append((cursor, duration))
    speech = [(max(0.0, a), min(duration, b)) for a, b in speech if b - a >= 0.15]
    merged: list[tuple[float, float]] = []
    for a, b in speech:
        if merged and a - merged[-1][1] < 0.45:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    if len(merged) == len(phrases):
        cues = []
        for i, phrase in enumerate(phrases):
            start = 0.0 if i == 0 else merged[i][0]
            end = merged[i][1]
            cues.append((start, end, phrase))
        return close_align(cues, duration)
    return weight_align(phrases, duration)


async def synthesize_voice(text: str, mp3: Path, rate: str) -> list[dict]:
    import edge_tts

    comm = edge_tts.Communicate(text, VOICE, rate=rate)
    bounds: list[dict] = []
    with mp3.open("wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("SentenceBoundary", "WordBoundary"):
                bounds.append(chunk)
    return bounds


def stream_broll(frame_fn: Callable[[float], Image.Image], duration: float, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    n = max(1, round(duration * FPS))
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18",
        str(dest),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    mid = None
    mid_i = min(n // 2, n - 1)
    for i in range(n):
        im = frame_fn(i / FPS)
        if i == mid_i:
            mid = im.copy()
        proc.stdin.write(im.convert("RGB").tobytes())
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(err[-2000:])
    if mid is not None:
        mid.save(dest.with_suffix(".jpg"), quality=92)


class Episode:
    def __init__(self, root: Path, cfg: dict):
        self.root = root
        self.name = cfg["name"]
        self.full_title = cfg.get("full_title", cfg["name"])
        self.staged_name = cfg["staged_name"]
        self.episode = int(cfg["episode"])
        self.expected_phrases = int(cfg.get("expected_phrases", 18))
        self.replaced_short = float(cfg.get("replaced_short", 0))
        self.source_note = cfg["source_note"]
        self.hooks = cfg["hooks"]
        self.cover_lines = cfg["cover_lines"]
        self.avoid = cfg.get("avoid", "")
        self.factory = cfg.get("factory", f"topics-batch3 #{cfg['episode']}")
        self.broll = cfg["broll"]  # sid -> (filename, frame_fn)

    def load_phrases(self) -> list[str]:
        return [ln.strip() for ln in (self.root / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]

    def write_align_files(self, aligned: list[tuple[float, float, str]], duration: float) -> None:
        audio_dir = self.root / "audio"
        audio_dir.mkdir(exist_ok=True)
        (audio_dir / "vo-align.txt").write_text(
            "".join(f"{s:.3f}\t{e:.3f}\t{p}\n" for s, e, p in aligned),
            encoding="utf-8",
        )
        cues = [{"start": round(s, 3), "end": round(e, 3), "text": p} for s, e, p in aligned]
        (audio_dir / "cues.json").write_text(json.dumps(cues, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        vtt = ["WEBVTT", ""]
        for i, (s, e, p) in enumerate(aligned, 1):
            def ts(x: float) -> str:
                ms = int(round(x * 1000))
                return f"{ms // 3600000:02d}:{(ms // 60000) % 60:02d}:{(ms // 1000) % 60:02d}.{ms % 1000:03d}"

            vtt += [str(i), f"{ts(s)} --> {ts(e)}", p, ""]
        (audio_dir / "vo.vtt").write_text("\n".join(vtt), encoding="utf-8")
        (audio_dir / "vo.vtt.json").write_text(
            json.dumps({"duration": round(duration, 3), "duration_zh": zh_sec(duration), "cues": cues}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def synth_once(self, text: str, phrases: list[str], rate: str) -> tuple[float, list[tuple[float, float, str]]]:
        audio_dir = self.root / "audio"
        audio_dir.mkdir(exist_ok=True)
        mp3 = audio_dir / "vo-full.mp3"
        wav = audio_dir / "vo-full.wav"
        bounds = asyncio.run(synthesize_voice(text, mp3, rate))
        if mp3.stat().st_size < 800:
            raise RuntimeError("tts too small")
        run(["ffmpeg", "-y", "-i", str(mp3), "-ac", "1", "-ar", "44100", str(wav)])
        duration = probe_dur(wav)
        sentences = [b for b in bounds if b.get("type") == "SentenceBoundary"]
        if sentences and len(sentences) >= len(phrases):
            aligned = []
            for i, phrase in enumerate(phrases):
                b = sentences[i]
                start = ticks_to_sec(b["offset"])
                end = start + ticks_to_sec(b["duration"])
                aligned.append((start, end, phrase))
            aligned = close_align(aligned, duration)
            print("TTS sentence cues", len(sentences), "rate", rate, "dur", duration, zh_sec(duration))
        else:
            aligned = detect_sentence_cues(wav, phrases, duration)
            print("TTS silencedetect/weight cues", "rate", rate, "dur", duration, zh_sec(duration))
        return duration, aligned

    def make_voiceover(self) -> tuple[float, list[tuple[float, float, str]]]:
        text = (self.root / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
        phrases = self.load_phrases()
        if len(phrases) != self.expected_phrases:
            raise SystemExit(f"need {self.expected_phrases} phrases, got {len(phrases)}")
        wav = self.root / "audio" / "vo-full.wav"
        # Faster first: ~190–210 汉字 land in the 40–50s window.
        rates = ["+6%", "+4%", "+2%", "-2%", "-4%"]
        best_target = None
        best_hard = None
        last = None
        for rate in rates:
            try:
                duration, aligned = self.synth_once(text, phrases, rate)
            except Exception as exc:
                print("TTS attempt failed", rate, exc)
                continue
            last = (rate, duration, aligned)
            print(f"VO rate={rate} duration={duration:.3f}s {zh_sec(duration)}")
            if TARGET_LO <= duration <= TARGET_HI:
                best_target = (rate, duration, aligned)
                break
            if HARD_LO <= duration <= HARD_HI:
                if best_hard is None or abs(duration - 45.0) < abs(best_hard[1] - 45.0):
                    best_hard = (rate, duration, aligned)
        picked = best_target or best_hard or last
        if picked is None:
            if wav.exists() and wav.stat().st_size > 800:
                duration = probe_dur(wav)
                aligned = detect_sentence_cues(wav, phrases, duration)
                self.write_align_files(aligned, duration)
                return duration, aligned
            raise RuntimeError("TTS failed all rates")
        win_rate, duration, aligned = picked
        if abs(probe_dur(wav) - duration) > 0.15:
            print("re-synth winning rate", win_rate)
            duration, aligned = self.synth_once(text, phrases, win_rate)
        self.write_align_files(aligned, duration)
        return duration, aligned

    def make_bgm(self, duration: float) -> Path:
        dest = self.root / "audio" / "bgm.wav"
        run([
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"sine=frequency=196:sample_rate=44100:duration={duration + 1.2:.2f}",
            "-f", "lavfi", "-i", f"sine=frequency=247:sample_rate=44100:duration={duration + 1.2:.2f}",
            "-f", "lavfi", "-i", f"sine=frequency=294:sample_rate=44100:duration={duration + 1.2:.2f}",
            "-filter_complex",
            "[0:a]volume=0.11[a];[1:a]volume=0.07[b];[2:a]volume=0.05[c];"
            "[a][b][c]amix=inputs=3:duration=longest,lowpass=f=500,alimiter=limit=0.32",
            "-ac", "2", "-ar", "44100", str(dest),
        ])
        return dest

    def make_sfx(self, cuts: list[float], duration: float) -> Path:
        dest = self.root / "audio" / "sfx.wav"
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

    def build_timeline(self, cues: list[tuple[float, float, str]], duration: float) -> dict:
        recipe = json.loads((self.root / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
        if len(cues) != self.expected_phrases:
            raise SystemExit(f"need {self.expected_phrases} cues, got {len(cues)}")
        by_text = {p: (s, e, p) for s, e, p in cues}

        shots = []
        cursor = 0.0
        for spec in recipe["shots"]:
            phrase_cues = [by_text[p] for p in spec["phrases"]]
            first_s, last_e = phrase_cues[0][0], phrase_cues[-1][1]
            start = cursor
            if spec["kind"] == "B":
                start = min(first_s, max(cursor, first_s - LEAD))
                start = max(cursor, start)
            end = last_e
            shots.append({
                "id": spec["id"],
                "kind": spec["kind"],
                "start": start,
                "end": end,
                "src": spec["src"],
                "line": spec["phrases"][0],
                "phrases": spec["phrases"],
                **({"close": True} if spec.get("close") else {}),
                **({"broll": spec["broll"]} if spec.get("broll") else {}),
            })
            cursor = end

        for shot in shots:
            if shot["end"] <= shot["start"] + 0.14:
                shot["end"] = min(duration, shot["start"] + 0.18)
        for i in range(1, len(shots)):
            shots[i]["start"] = shots[i - 1]["end"]
        shots[0]["start"] = 0.0
        shots[-1]["end"] = duration
        for shot in shots:
            shot["start"] = round(float(shot["start"]), 3)
            shot["end"] = round(float(shot["end"]), 3)

        a_caps = []
        for spec, shot in zip(recipe["shots"], shots):
            if spec["kind"] != "A":
                continue
            for phrase in spec["phrases"]:
                s, e, _ = by_text[phrase]
                cap_s = max(s, shot["start"])
                cap_e = min(e, shot["end"])
                if cap_e > cap_s + 0.08:
                    a_caps.append({"start": round(cap_s, 3), "end": round(cap_e, 3), "lines": split_caption(phrase)})

        palette = {"A": list(CREAM)}
        b_colors = [list(MINT), list(YELLOW), list(AMBER)]
        shutters = []
        b_i = 0
        for shot in shots[1:]:
            if shot["kind"] == "B":
                color = b_colors[b_i % len(b_colors)]
                b_i += 1
            else:
                color = palette["A"]
            shutters.append({"start": shot["start"], "color": color})

        eyebrows = []
        for spec, shot in zip(recipe["shots"], shots):
            if spec["kind"] != "A":
                continue
            eyebrows.append({"start": shot["start"], "end": shot["end"], "text": f"A-ROLL / {spec['id'][1:]}"})

        data = {
            "audio": "audio/vo-full.wav",
            "duration": round(duration, 3),
            "duration_zh": zh_sec(duration),
            "fps": FPS,
            "size": [W, H],
            "title": recipe["title"],
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
            "cue_map": {p: [round(s, 3), round(e, 3)] for s, e, p in cues},
            "b_lead_s": LEAD,
            "video_type": "普通短视频",
            "factory": self.factory,
            "topic": self.episode,
            "cut": "long-40s",
            "draft": f".abroll-cloud/{self.episode}-long",
            "freeze_pad": False,
        }
        (self.root / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return data

    def draw_eyebrow(self, base: Image.Image, t: float, eyebrows) -> None:
        label = None
        for item in eyebrows:
            if item["start"] <= t < item["end"]:
                label = item["text"]
                break
        if not label:
            return
        d = ImageDraw.Draw(base)
        fnt = font(22)
        d.rectangle((76, 88, 120, 92), fill=(*MINT, 230))
        d.text((136, 78), label, font=fnt, fill=(90, 98, 108, 220))

    def draw_pill(self, base: Image.Image, lines: list[str], y: int = 168) -> None:
        fnt = font(56 if len(lines) == 1 and max(len(s) for s in lines) <= 8 else 42)
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

    def draw_shutter(self, base: Image.Image, t: float, shutters) -> Image.Image:
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

    def render_captions(self, data: dict) -> Path:
        dest = self.root / "shots" / "caption_layer.mov"
        dest.parent.mkdir(parents=True, exist_ok=True)
        duration = float(data["duration"])
        n = max(1, round(duration * FPS))
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "qtrle", "-pix_fmt", "argb", str(dest),
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        assert proc.stdin is not None
        for i in range(n):
            t = i / FPS
            img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            self.draw_eyebrow(img, t, data["eyebrows"])
            for cue in data["a_caps"]:
                if cue["start"] <= t < cue["end"]:
                    self.draw_pill(img, cue["lines"])
                    break
            img = self.draw_shutter(img, t, data["shutters"])
            proc.stdin.write(img.tobytes())
        proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
        if proc.wait() != 0:
            raise RuntimeError(err[-2500:])
        return dest

    def cut_shot(self, src: Path, dur: float, dest: Path, kind: str, close: bool = False) -> None:
        """Loop short A-roll. Never freeze last frame. Never slow-mo stretch to pad."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        src_dur = max(0.01, probe_dur(src))
        if kind == "A" and close:
            vf = f"scale=1380:2454,crop={W}:{H}:150:60,fps={FPS},setsar=1,format=yuv420p"
        elif kind == "A":
            vf = f"scale=1188:2112,crop={W}:{H}:54:105,fps={FPS},setsar=1,format=yuv420p"
        else:
            vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},setsar=1,format=yuv420p"
        cmd = ["ffmpeg", "-y"]
        if dur > src_dur + 0.02:
            cmd += ["-stream_loop", "-1"]
        cmd += [
            "-i", str(src), "-t", f"{dur:.3f}",
            "-vf", vf, "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18", str(dest),
        ]
        run(cmd)
        got = probe_dur(dest)
        if got + 0.12 < dur:
            raise RuntimeError(f"cut short {dest.name}: {got:.3f} < {dur:.3f} (freeze-pad forbidden)")

    def assemble(self, data: dict) -> Path:
        shots_dir = self.root / "shots"
        shots_dir.mkdir(exist_ok=True)
        parts: list[Path] = []
        for shot in data["shots"]:
            dur = float(shot["end"]) - float(shot["start"])
            src = self.root / shot["src"]
            dest = shots_dir / f"{shot['id']}.mp4"
            print(shot["id"], shot["kind"], f"{dur:.2f}s", zh_sec(dur), src.name)
            if shot["kind"] == "B":
                src_dur = probe_dur(src)
                if src_dur + 0.05 < dur:
                    raise RuntimeError(f"B-roll shorter than shot, would freeze-pad: {src.name} {src_dur:.3f} < {dur:.3f}")
            self.cut_shot(src, dur, dest, shot["kind"], bool(shot.get("close")))
            parts.append(dest)

        lst = shots_dir / "concat.txt"
        lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
        concat = shots_dir / "video_only.mp4"
        run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
            str(concat),
        ])

        caps = self.render_captions(data)
        burned = shots_dir / "video_subs.mp4"
        run([
            "ffmpeg", "-y", "-i", str(concat), "-i", str(caps),
            "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an", str(burned),
        ])

        audio = self.root / data["audio"]
        bgm = self.root / "audio" / "bgm.wav"
        sfx = self.root / "audio" / "sfx.wav"
        cuts = [float(s["start"]) for s in data["shutters"]]
        self.make_sfx(cuts, float(data["duration"]))

        final = self.root / f"00_最终成片_{self.name}.mp4"
        (self.root / "final").mkdir(exist_ok=True)
        inputs = ["ffmpeg", "-y", "-i", str(burned), "-i", str(audio)]
        filters = ["[1:a]loudnorm=I=-16:LRA=11:TP=-1.5,aformat=sample_rates=44100:channel_layouts=stereo[vo]"]
        mix_ins = ["[vo]"]
        idx = 2
        if bgm.exists():
            inputs += ["-i", str(bgm)]
            filters.append(f"[{idx}:a]adelay=800|800,volume=0.15,highpass=f=140[bg]")
            mix_ins.append("[bg]")
            idx += 1
        if sfx.exists():
            inputs += ["-i", str(sfx)]
            filters.append(f"[{idx}:a]volume=0.26[sfx]")
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

        def safe_copy(src: Path, dest: Path) -> None:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() and dest.resolve() == src.resolve():
                return
            try:
                if dest.exists() and dest.samefile(src):
                    return
            except OSError:
                pass
            shutil.copy2(src, dest)

        out = self.root / "output" / f"{self.name}.mp4"
        safe_copy(final, out)
        safe_copy(final, self.root / "final" / f"{self.name}.mp4")
        staged, overwritten, existing_dur = self.resolve_stage_target(final)
        print(
            "STAGE",
            staged,
            "overwritten" if overwritten else "kept-existing",
            zh_sec(existing_dur),
        )
        return staged

    def resolve_stage_target(self, final: Path) -> tuple[Path, bool, float]:
        """Copy into 成片/ only when missing or shorter than 30s. Never freeze-pad."""
        dest = Path("/workspace/成片") / self.staged_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            try:
                existing = probe_dur(dest)
            except Exception:
                existing = 0.0
            if existing >= HARD_LO:
                print(f"KEEP 成片 {dest.name} {zh_sec(existing)}（已≥{HARD_LO:.0f}秒），不覆盖")
                return final, False, existing
            print(f"OVERWRITE 成片 {dest.name} {zh_sec(existing)}（<{HARD_LO:.0f}秒）")
        else:
            print(f"STAGE new 成片 {dest.name}")
        if dest.exists():
            try:
                if dest.resolve() == final.resolve() or dest.samefile(final):
                    return dest, True, probe_dur(dest)
            except OSError:
                pass
        shutil.copy2(final, dest)
        return dest, True, probe_dur(dest)

    def make_cover(self) -> Path:
        data = json.loads((self.root / "timeline.json").read_text(encoding="utf-8"))
        cover = data["cover"]
        char = Image.open(self.root / cover["src"]).convert("RGB")
        scale = max(W / char.width, H / char.height)
        nw, nh = int(char.width * scale), int(char.height * scale)
        char = char.resize((nw, nh), Image.Resampling.LANCZOS)
        x = (nw - W) // 2
        y = int((nh - H) * 0.62)
        canvas = char.crop((x, y, x + W, y + H))
        overlay = Image.new("RGBA", (W, H), (11, 13, 18, 48))
        canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
        d = ImageDraw.Draw(canvas)
        d.rounded_rectangle((70, 80, 1010, 470), radius=36, fill=(22, 24, 28))
        line1, line2 = self.cover_lines
        d.text((W // 2, 160), line1, font=font(52), fill=WHITE, anchor="mm")
        d.text((W // 2, 250), line2, font=font(58), fill=YELLOW, anchor="mm")
        d.text((W // 2, 340), cover["sub"], font=font(36), fill=MINT, anchor="mm")
        d.text((W // 2, 410), cover["line"], font=font(30), fill=MUTED, anchor="mm")
        dest = self.root / f"00_封面_{self.name}.jpg"
        canvas.save(dest, quality=92)
        (self.root / "final").mkdir(exist_ok=True)
        canvas.save(self.root / "final" / "cover.jpg", quality=92)
        return dest

    def copy_assets(self) -> None:
        dest = self.root / "assets"
        dest.mkdir(exist_ok=True)
        for name in ("V-挥手.mp4", "V-摊手.mp4", "V-指向.mp4", "V-点赞.mp4", "A-角色-小灯-摊手.jpg"):
            src = ASSET_SRC / name
            if not src.exists():
                raise FileNotFoundError(src)
            target = dest / name
            if not target.exists() or target.stat().st_size != src.stat().st_size:
                shutil.copy2(src, target)

    def patch_index_line(self, path: Path, duration: float) -> None:
        line = f"| `{self.staged_name}` | {zh_sec(duration)} |"
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8")
        token = f"`{self.staged_name}`"
        out_lines = []
        seen = False
        for raw in text.splitlines():
            if raw.startswith("|") and token in raw:
                if not seen:
                    out_lines.append(line)
                    seen = True
                continue
            out_lines.append(raw)
        if not seen:
            inserted = False
            rebuilt = []
            for raw in out_lines:
                if (not inserted) and "仙侠云海突进" in raw and raw.strip().startswith("|"):
                    rebuilt.append(line)
                    inserted = True
                rebuilt.append(raw)
            if not inserted:
                rebuilt.append(line)
            out_lines = rebuilt
        text = "\n".join(out_lines)
        if not text.endswith("\n"):
            text += "\n"
        path.write_text(text, encoding="utf-8")

    def patch_delivery(self, duration: float) -> None:
        path = Path("/workspace/.abroll-cloud/DELIVERY.md")
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8")
        new = (
            f"| `成片/{self.staged_name}` | 1080×1920 h264+aac 44.1k stereo | {zh_sec(duration)} | "
            f"topic {self.episode} 加长重切（{self.episode}-long，覆盖 {self.replaced_short:.1f}秒短切） |"
        )
        pat = rf"\| `成片/{re.escape(self.staged_name)}` \|[^\n]+\|"
        if re.search(pat, text):
            text = re.sub(pat, new, text, count=1)
        else:
            lines = text.splitlines()
            rebuilt = []
            inserted = False
            for raw in lines:
                if (not inserted) and "仙侠云海突进" in raw and raw.strip().startswith("|"):
                    rebuilt.append(new)
                    inserted = True
                rebuilt.append(raw)
            if not inserted:
                rebuilt.append(new)
            text = "\n".join(rebuilt)
        if not text.endswith("\n"):
            text += "\n"
        path.write_text(text, encoding="utf-8")

    def write_docs(self, duration: float, staged: Path, data: dict) -> None:
        vo = (self.root / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
        sha = hashlib.sha256(vo.encode("utf-8")).hexdigest()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        n = self.episode
        status = {
            "schema_version": 1,
            "project_name": f"{n}_{self.name}_long",
            "video_type": "普通短视频",
            "episode": n,
            "cut": "long-40s",
            "title": self.name,
            "full_title": self.full_title,
            "source_note": self.source_note,
            "slug": self.name,
            "voice": VOICE,
            "duration": round(duration, 3),
            "duration_zh": zh_sec(duration),
            "size": [W, H],
            "fps": FPS,
            "stage": "delivered",
            "status": "已交付",
            "current_stage": "核验并交付",
            "production_method": "白底小灯 A-roll + 黑底对照卡 B-roll + edge-tts Yunyang + FFmpeg",
            "freeze_pad": False,
            "script": {"path": "script/voiceover.txt", "sha256": sha, "phrases": self.expected_phrases},
            "audio": {
                "path": "audio/vo-full.wav",
                "alignment_path": "audio/vo-align.txt",
                "voice_id": VOICE,
                "sample_rate": 44100,
                "channels": 1,
                "duration_ms": int(duration * 1000),
            },
            "deliverables": {
                "final_video": str(staged),
                "project_final": f"00_最终成片_{self.name}.mp4",
                "cover": f"00_封面_{self.name}.jpg",
            },
            "staged": f"成片/{self.staged_name}",
            "draft": f".abroll-cloud/{n}-long",
            "qa_video": str(staged),
            "replaced_short_cut_s": self.replaced_short,
            "cloud_only": True,
            "windows_paths": False,
            "drive_upload": False,
            "not": "drama-pipeline / 仙侠连载 / C:D:G: / Drive 上传 / freeze-pad",
            "updated_at": now,
        }
        (self.root / "项目状态.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        note = f"""# {n} · {self.full_title}（加长重切）

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。

- **选题**：{self.source_note}
- **成片中转**：`成片/{self.staged_name}`（覆盖原 {zh_sec(self.replaced_short)} 短切）
- **本集工程成片**：`00_最终成片_{self.name}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/{n}-long/`
- **云端 only**：不写 `C:\\` / `D:\\` / `G:\\`，不传 Drive
- **禁止冻帧垫时长**：A 镜循环，B 镜按口播重画，不用末帧克隆
- **避开**：{self.avoid}

{self.hooks}

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {zh_sec(duration)}。镜头 {len(data["shots"])} 条，口播 {self.expected_phrases} 句，时间轴闭合。
"""
        (self.root / "项目说明.md").write_text(note, encoding="utf-8")

    def qa(self, staged: Path, data: dict) -> dict:
        qa_dir = self.root / "qa"
        qa_dir.mkdir(exist_ok=True)
        probe = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(staged)],
            text=True,
        )
        (qa_dir / "ffprobe.json").write_text(probe, encoding="utf-8")
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
        dur = float(info["format"]["duration"])
        digest = hashlib.sha256(staged.read_bytes()).hexdigest()
        kinds = [s["kind"] for s in shots]
        kit_src = Path(__file__).read_text(encoding="utf-8")
        freeze_token = "tpad" + "=stop_mode" + "=clone"
        slowmo_token = "setpts=" + "PTS*"
        no_tpad = freeze_token not in kit_src and slowmo_token not in kit_src
        report = {
            "project": f"{self.episode}_{self.name}_long",
            "strict": True,
            "cloud_only": True,
            "windows_paths": False,
            "drive_upload": False,
            "video_type": "普通短视频",
            "cut": "long-40s",
            "final": str(staged),
            "project_final": str(self.root / f"00_最终成片_{self.name}.mp4"),
            "sha256": digest,
            "bytes": staged.stat().st_size,
            "replaced_short_cut_s": self.replaced_short,
            "freeze_pad": False,
            "no_tpad_clone_in_kit": no_tpad,
            "video": {
                "codec": v.get("codec_name"),
                "width": int(v.get("width", 0)),
                "height": int(v.get("height", 0)),
                "fps": fps,
                "pix_fmt": v.get("pix_fmt"),
                "duration_s": dur,
                "duration_zh": zh_sec(dur),
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
                "a_shots": kinds.count("A"),
                "b_shots": kinds.count("B"),
                "phrases": self.expected_phrases,
                "overlap": overlap,
                "gap": gap,
                "last_end_equals_audio": abs(shots[-1]["end"] - data["duration"]) < 0.05,
                "broll_lead_s": LEAD,
                "in_hard_window": HARD_LO <= dur <= HARD_HI,
                "in_target_window": TARGET_LO <= dur <= TARGET_HI,
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
            and report["timeline"]["in_hard_window"]
            and kinds.count("A") >= 4
            and kinds.count("B") >= 3
            and no_tpad
        )
        (self.root / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return report

    def produce(self) -> dict:
        self.copy_assets()
        duration, cues = self.make_voiceover()
        print("VO", duration, zh_sec(duration))
        for row in cues:
            print(f"  {row[0]:6.3f}-{row[1]:6.3f}  {row[2]}")
        if not (HARD_LO <= duration <= HARD_HI):
            raise SystemExit(f"VO duration {zh_sec(duration)} outside {HARD_LO:.0f}-{HARD_HI:.0f}秒")
        self.make_bgm(duration)
        data = self.build_timeline(cues, duration)
        print("timeline shots", [(s["id"], s["start"], s["end"], s["kind"], zh_sec(s["end"] - s["start"])) for s in data["shots"]])

        for sid, (fname, frame_fn) in self.broll.items():
            shot = next(s for s in data["shots"] if s["id"] == sid)
            d = max(2.4, float(shot["end"]) - float(shot["start"]))
            dest = self.root / "broll" / fname
            print("render", fname, d, zh_sec(d))
            stream_broll(frame_fn, d + 0.18, dest)
            if probe_dur(dest) + 0.05 < d:
                raise RuntimeError(f"B-roll too short after render {fname}")

        self.make_cover()
        qa_path = self.assemble(data)
        draft_final = self.root / f"00_最终成片_{self.name}.mp4"
        draft_dur = probe_dur(draft_final)
        staged_path = Path("/workspace/成片") / self.staged_name
        cheng_dur = probe_dur(staged_path) if staged_path.exists() else draft_dur
        self.write_docs(draft_dur, qa_path, data)
        self.patch_index_line(Path("/workspace/成片/INDEX.md"), cheng_dur)
        self.patch_index_line(Path("/workspace/.abroll-cloud/INDEX.chengpian.md"), cheng_dur)
        self.patch_delivery(cheng_dur)
        report = self.qa(qa_path, data)
        report["chengpian"] = str(staged_path) if staged_path.exists() else str(qa_path)
        report["chengpian_duration_s"] = cheng_dur
        report["chengpian_duration_zh"] = zh_sec(cheng_dur)
        report["draft_duration_s"] = draft_dur
        report["draft_duration_zh"] = zh_sec(draft_dur)
        (self.root / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("QA", qa_path, "draft", zh_sec(draft_dur), "成片", zh_sec(cheng_dur), "ok", report["ok"])
        if not report["ok"]:
            raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))
        return report
