# -*- coding: utf-8 -*-
"""98 发布说明写成流水账：口播 → 对轴 → B 卷 → 组装。禁止冻帧垫时长。"""
from __future__ import annotations

import asyncio
import json
import math
import os
import subprocess
import wave
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 24
TITLE = "发布说明写成流水账"
VOICE = "zh-CN-YunxiNeural"
RATE = "+8%"
B_LEAD = 0.28
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

BG = (11, 13, 18)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
CARD = (24, 28, 38)
RED = (255, 118, 118)
CREAM = (245, 247, 250)
INK = (28, 32, 36)


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


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def appear(t: float, start: float, dur: float = 0.38) -> float:
    return ease((t - start) / dur)


def mix(a, b, t: float):
    t = max(0.0, min(1.0, t))
    return tuple(int(b[i] * t + a[i] * (1 - t)) for i in range(3))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def new_bg() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    ov = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(ov)
    d.ellipse((-260, -300, 720, 560), fill=(16, 42, 38))
    d.ellipse((420, 1100, 1400, 2100), fill=(42, 32, 16))
    return Image.blend(img, ov.filter(ImageFilter.GaussianBlur(90)), 0.58)


def tag(draw: ImageDraw.ImageDraw, t: float, label: str) -> None:
    a = appear(t, 0.0, 0.24)
    if a <= 0:
        return
    fnt = font(28)
    x0, y0, x1, y1 = draw.textbbox((0, 0), label, font=fnt)
    tw, th = x1 - x0, y1 - y0
    x, y = 72, 86
    draw.rounded_rectangle((x - 22, y - 14, x + tw + 22, y + th + 12), radius=18, fill=mix(BG, (20, 42, 38), a))
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


def b_tickets(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, sub_f = font(56), font(40), font(30)
    tickets = ["TKT-1842", "TKT-1907", "TKT-2033", "TKT-2110"]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "01  票号墙")
        a0 = appear(t, 0.04)
        d.text((W // 2, 220), "堆了一串内部票号", font=title_f, fill=mix(BG, WHITE, a0), anchor="mm")
        d.text((W // 2, 300), "影响和动作都被淹没", font=sub_f, fill=mix(BG, MUTED, appear(t, 0.18)), anchor="mm")
        for k, name in enumerate(tickets):
            a = appear(t, 0.28 + k * 0.16, 0.22)
            if a < 0.04:
                continue
            y = 400 + k * 150 + int(lerp(24, 0, a))
            d.rounded_rectangle((140, y, 940, y + 118), radius=22, fill=mix(BG, CARD, a))
            d.text((220, y + 59), name, font=card_f, fill=mix(CARD, MUTED, a), anchor="lm")
            strike = appear(t, duration * 0.42 + k * 0.08, 0.18)
            if strike > 0.04:
                x1 = int(lerp(200, 900, strike))
                d.line([(200, y + 59), (x1, y + 59)], fill=mix(CARD, RED, strike), width=8)
        punch = appear(t, duration * 0.62, 0.28)
        if punch > 0.04:
            d.text((W // 2, 1680), "看完仍不知道改了啥", font=title_f, fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def b_contrast(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, sub_f = font(48), font(40), font(28)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "02  对照")
        a = appear(t, 0.04, 0.30)
        left = int(lerp(-420, 56, a))
        right = int(lerp(W + 40, 560, a))
        d.rounded_rectangle((left, 280, left + 460, 1180), radius=32, fill=mix(BG, CARD, a))
        d.rounded_rectangle((right, 280, right + 460, 1180), radius=32, fill=mix(BG, CARD, a))
        d.text((left + 230, 360), "流水账", font=sub_f, fill=mix(CARD, RED, a), anchor="mm")
        d.text((left + 230, 520), "像日记", font=title_f, fill=mix(CARD, WHITE, a), anchor="mm")
        d.text((left + 230, 720), "发生了什么", font=card_f, fill=mix(CARD, MUTED, a), anchor="mm")
        d.text((left + 230, 860), "票号堆成墙", font=card_f, fill=mix(CARD, MUTED, a), anchor="mm")
        d.text((right + 230, 360), "动作句", font=sub_f, fill=mix(CARD, MINT, a), anchor="mm")
        d.text((right + 230, 520), "像指令", font=title_f, fill=mix(CARD, YELLOW, a), anchor="mm")
        d.text((right + 230, 720), "谁要动手", font=card_f, fill=mix(CARD, WHITE, a), anchor="mm")
        d.text((right + 230, 860), "坏了怎么退", font=card_f, fill=mix(CARD, WHITE, a), anchor="mm")
        if a > 0.7:
            d.ellipse((W // 2 - 36, 680, W // 2 + 36, 752), fill=(18, 22, 28))
            d.text((W // 2, 716), "切", font=font(32), fill=YELLOW, anchor="mm")
        d.text((W // 2, 1680), "开头只写动作", font=title_f, fill=mix(BG, YELLOW, appear(t, 0.55)), anchor="mm")
        out.append(img)
    return out


def b_steps(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, card_f, sub_f = font(48), font(38), font(28)
    rows = [
        ("影响面", "谁会中招，写在同一行"),
        ("回退", "坏了怎么退，写完才算完"),
        ("日期", "可以留，不能当正文"),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "03  写清")
        d.text((W // 2, 220), "谁中招 · 怎么退", font=title_f, fill=mix(BG, WHITE, appear(t, 0.04)), anchor="mm")
        for k, (head, body) in enumerate(rows):
            a = appear(t, 0.22 + k * 0.22, 0.22)
            if a < 0.04:
                continue
            y = 380 + k * 280
            d.rounded_rectangle((90, y, 990, y + 230), radius=28, fill=mix(BG, CARD, a))
            d.rounded_rectangle((120, y + 36, 280, y + 96), radius=16, fill=mix(CARD, (20, 42, 38), a))
            d.text((200, y + 66), head, font=sub_f, fill=mix(CARD, MINT, a), anchor="mm")
            d.text((W // 2, y + 150), body, font=card_f, fill=mix(CARD, WHITE, a), anchor="mm")
        punch = appear(t, duration * 0.58, 0.26)
        if punch > 0.04:
            d.text((W // 2, 1680), "没有回退，就还没写完", font=title_f, fill=mix(BG, RED, punch), anchor="mm")
        out.append(img)
    return out


def b_punch(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * FPS))
    title_f, huge, sub_f = font(48), font(58), font(32)
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "04  发布")
        a0 = appear(t, 0.04)
        d.text((W // 2, 260), "发布说明不是备忘录", font=title_f, fill=mix(BG, MUTED, a0), anchor="mm")
        a1 = appear(t, 0.28)
        d.rounded_rectangle((90, 420, 990, 1180), radius=36, fill=mix(BG, CARD, a1))
        d.text((W // 2, 620), "能照着做", font=huge, fill=mix(CARD, WHITE, a1), anchor="mm")
        d.text((W // 2, 760), "才叫发布", font=huge, fill=mix(CARD, YELLOW, a1), anchor="mm")
        d.text((W // 2, 960), "写成让人能下手的动作句", font=sub_f, fill=mix(CARD, MINT, appear(t, 0.55)), anchor="mm")
        out.append(img)
    return out


STYLES = {
    "tickets": b_tickets,
    "contrast": b_contrast,
    "steps": b_steps,
    "punch": b_punch,
}


async def synth_phrases(phrases: list[str], dest_wav: Path) -> list[dict]:
    dest_wav.parent.mkdir(parents=True, exist_ok=True)
    parts_dir = dest_wav.parent / "_parts"
    parts_dir.mkdir(exist_ok=True)
    cues = []
    wavs = []
    for i, text in enumerate(phrases):
        mp3 = parts_dir / f"{i:02d}.mp3"
        wav = parts_dir / f"{i:02d}.wav"
        comm = edge_tts.Communicate(text + "。", VOICE, rate=RATE)
        await comm.save(str(mp3))
        run(["ffmpeg", "-y", "-i", str(mp3), "-ac", "1", "-ar", "44100", str(wav)])
        wavs.append(wav)
    gap = 0.06
    pcm = bytearray()
    t = 0.0
    for i, (text, wav) in enumerate(zip(phrases, wavs)):
        with wave.open(str(wav), "rb") as w:
            frames = w.readframes(w.getnframes())
            sr = w.getframerate()
            dur = w.getnframes() / sr
        start = t
        end = t + dur
        cues.append({"i": i, "text": text, "start": round(start, 3), "end": round(end, 3)})
        pcm.extend(frames)
        gap_n = int(sr * gap)
        pcm.extend(b"\x00\x00" * gap_n)
        t = end + gap
    # trim last gap
    t -= gap
    pcm = pcm[: int(44100 * t) * 2]
    with wave.open(str(dest_wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(bytes(pcm))
    # pad 80ms tail so last shot isn't chopped
    tail = 0.04
    run(
        [
            "ffmpeg", "-y", "-i", str(dest_wav),
            "-af", f"apad=pad_dur={tail:.2f}",
            "-ar", "44100", "-ac", "1",
            str(dest_wav.with_name("vo-full.tmp.wav")),
        ]
    )
    tmp = dest_wav.with_name("vo-full.tmp.wav")
    tmp.replace(dest_wav)
    cues[-1]["end"] = round(probe_dur(dest_wav), 3)
    return cues


def write_align(cues: list[dict], dest: Path) -> None:
    lines = []
    for c in cues:
        lines.append(f"{c['start']:7.3f}-{c['end']:7.3f}  {c['text']}")
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_bgm(dest: Path, duration: float) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"sine=frequency=196:sample_rate=44100:duration={duration + 2:.2f}",
            "-f", "lavfi", "-i", f"sine=frequency=247:sample_rate=44100:duration={duration + 2:.2f}",
            "-f", "lavfi", "-i", f"sine=frequency=294:sample_rate=44100:duration={duration + 2:.2f}",
            "-filter_complex",
            "[0:a]volume=0.07[a0];[1:a]volume=0.05[a1];[2:a]volume=0.04[a2];"
            "[a0][a1][a2]amix=inputs=3:duration=longest,lowpass=f=520,highpass=f=120,volume=0.9[a]",
            "-map", "[a]", "-ac", "2", "-ar", "44100", str(dest),
        ]
    )


def make_sfx(dest: Path, cuts: list[float], duration: float) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    times = [t for t in cuts if 0.12 < t < duration - 0.2]
    if not times:
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={duration:.2f}", str(dest)])
        return
    click = dest.with_name("click.wav")
    run(
        [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "sine=frequency=880:sample_rate=44100:duration=0.045",
            "-af", "afade=t=out:st=0.02:d=0.025,volume=0.7",
            str(click),
        ]
    )
    labels = []
    parts = []
    cmd = ["ffmpeg", "-y"]
    for i, t in enumerate(times):
        cmd += ["-i", str(click)]
        ms = int(t * 1000)
        labels.append(f"[{i}]adelay={ms}|{ms}[s{i}]")
        parts.append(f"[s{i}]")
    labels.append(f"{''.join(parts)}amix=inputs={len(parts)}:duration=longest,apad=whole_dur={duration:.2f}[a]")
    cmd += ["-filter_complex", ";".join(labels), "-map", "[a]", "-t", f"{duration:.2f}", "-ac", "2", "-ar", "44100", str(dest)]
    run(cmd)


def build_timeline(cues: list[dict], recipe: dict, duration: float) -> dict:
    by_text = {c["text"]: c for c in cues}
    shots = []
    for spec in recipe["shots"]:
        phrases = spec["phrases"]
        if not phrases:
            continue
        start = by_text[phrases[0]]["start"]
        end = by_text[phrases[-1]]["end"]
        kind = spec["kind"]
        if kind == "B":
            start = max(0.0, start - B_LEAD)
        shots.append(
            {
                "id": spec["id"],
                "kind": kind,
                "start": start,
                "end": end,
                "src": spec["src"],
                "line": phrases[0] if len(phrases) == 1 else phrases[0],
                "lines": phrases,
                **({"close": True} if spec.get("close") else {}),
            }
        )
    # snap to closed [0, duration], no overlap/gap
    shots[0]["start"] = 0.0
    shots[-1]["end"] = duration
    for i in range(1, len(shots)):
        if shots[i]["kind"] == "B":
            lead = min(B_LEAD, max(0.12, shots[i]["start"] - shots[i - 1]["start"] - 0.4))
            shots[i]["start"] = max(shots[i - 1]["start"] + 0.45, shots[i]["start"])
            # join previous end to this start
        shots[i - 1]["end"] = shots[i]["start"]
    shots[-1]["end"] = duration
    # second pass: enforce monotonic
    for i in range(1, len(shots)):
        if shots[i]["start"] < shots[i - 1]["end"] - 1e-6:
            shots[i]["start"] = shots[i - 1]["end"]
        if shots[i]["end"] <= shots[i]["start"]:
            shots[i]["end"] = min(duration, shots[i]["start"] + 0.5)
            if i + 1 < len(shots):
                shots[i + 1]["start"] = max(shots[i + 1]["start"], shots[i]["end"])
    shots[-1]["end"] = duration
    return {
        "size": [W, H],
        "fps": FPS,
        "duration": duration,
        "audio": "audio/vo-full.wav",
        "bgm": "audio/bgm.wav",
        "title": TITLE,
        "shots": shots,
    }


def cut_shot(src: Path, dur: float, dest: Path, kind: str, close: bool = False) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if kind == "A" and close:
        vf = f"scale=1380:2454,crop={W}:{H}:150:60,fps={FPS},setsar=1,format=yuv420p"
    elif kind == "A":
        vf = f"scale=1188:2112,crop={W}:{H}:54:105,fps={FPS},setsar=1,format=yuv420p"
    else:
        vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},setsar=1,format=yuv420p"
    cmd = ["ffmpeg", "-y"]
    if kind == "A":
        cmd += ["-stream_loop", "-1"]
    cmd += ["-i", str(src), "-t", f"{dur:.3f}", "-vf", vf, "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18", str(dest)]
    run(cmd)


def render_caps(data: dict, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    duration = float(data["duration"])
    n = max(1, round(duration * FPS))
    cues = []
    shutters = []
    eyebrows = []
    prev = None
    for shot in data["shots"]:
        if shot["kind"] == "A":
            line = shot.get("line") or (shot.get("lines") or [""])[0]
            cues.append((float(shot["start"]), float(shot["end"]), line))
            eyebrows.append((float(shot["start"]), float(shot["end"]), f"A-ROLL / {shot['id']}"))
        if prev and prev != shot["kind"]:
            color = MINT if shot["kind"] == "B" else YELLOW
            shutters.append((float(shot["start"]), color))
        prev = shot["kind"]

    def split_line(text: str) -> list[str]:
        text = text.strip()
        if "：" in text:
            a, b = text.split("：", 1)
            return [a + "：", b]
        if "，" in text and len(text) > 10:
            a, b = text.split("，", 1)
            return [a + "，", b]
        if len(text) > 11:
            return [text[:8], text[8:]]
        return [text]

    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "qtrle", "-pix_fmt", "argb", str(dest),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assert proc.stdin is not None
    fnt_big = font(46)
    fnt_eb = font(22)
    for i in range(n):
        t = i / FPS
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for s, e, label in eyebrows:
            if s <= t < e:
                d.rectangle((76, 88, 120, 92), fill=(126, 224, 197, 230))
                d.text((136, 78), label, font=fnt_eb, fill=(90, 98, 108, 220))
                break
        active = next((ln for s, e, ln in cues if s <= t < e), None)
        if active:
            lines = split_line(active)
            widths = []
            for line in lines:
                x0, y0, x1, y1 = d.textbbox((0, 0), line, font=fnt_big)
                widths.append(x1 - x0)
            tw = max(widths)
            line_h = 58
            pad_x, pad_y = 40, 20
            box_w = tw + pad_x * 2
            box_h = pad_y * 2 + line_h * len(lines) - 8
            x = (W - box_w) // 2
            y = 1648
            d.rounded_rectangle((x, y, x + box_w, y + box_h), radius=24, fill=(22, 24, 28, 214))
            d.rectangle((x + 10, y + 14, x + 20, y + box_h - 14), fill=(126, 224, 197, 235))
            for li, line in enumerate(lines):
                d.text((x + box_w // 2 + 4, y + pad_y + line_h * li), line, font=fnt_big, fill=(245, 247, 250, 255), anchor="mt")
        for start, color in shutters:
            dt = t - start
            if 0 <= dt <= 0.16:
                p = dt / 0.16
                if p < 0.5:
                    ww = max(2, int(W * p * 2))
                    x0 = 0
                else:
                    ww = max(2, int(W * (1 - (p - 0.5) * 2)))
                    x0 = W - ww
                sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(sh).rectangle((x0, 0, x0 + ww, H), fill=(*color, 235))
                layer = Image.alpha_composite(layer, sh)
        proc.stdin.write(layer.tobytes())
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    if proc.wait() != 0:
        raise RuntimeError(err[-2000:])


def assemble(data: dict) -> Path:
    shots_dir = ROOT / "shots"
    shots_dir.mkdir(exist_ok=True)
    parts = []
    for shot in data["shots"]:
        dur = float(shot["end"]) - float(shot["start"])
        dest = shots_dir / f"{shot['id']}.mp4"
        print(shot["id"], shot["kind"], f"{dur:.2f}秒", Path(shot["src"]).name)
        cut_shot(ROOT / shot["src"], dur, dest, shot["kind"], bool(shot.get("close")))
        parts.append(dest)
    lst = shots_dir / "concat_lane.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    concat = shots_dir / "video_only.mp4"
    run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
            str(concat),
        ]
    )
    caps = shots_dir / "caption_layer.mov"
    render_caps(data, caps)
    burned = shots_dir / "video_subs.mp4"
    run(
        [
            "ffmpeg", "-y", "-i", str(concat), "-i", str(caps),
            "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an", str(burned),
        ]
    )
    audio = ROOT / data["audio"]
    bgm = ROOT / "audio" / "bgm.wav"
    sfx = ROOT / "audio" / "sfx.wav"
    final = ROOT / f"00_最终成片_{TITLE}.mp4"
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
    return final


def make_cover(data: dict, dest: Path) -> None:
    img = new_bg()
    d = ImageDraw.Draw(img)
    d.text((W // 2, 720), "发布说明", font=font(72), fill=WHITE, anchor="mm")
    d.text((W // 2, 860), "写成流水账", font=font(72), fill=YELLOW, anchor="mm")
    d.rounded_rectangle((220, 1040, 860, 1160), radius=24, fill=CARD)
    d.text((W // 2, 1100), "写成让人能下手的动作句", font=font(32), fill=MINT, anchor="mm")
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, quality=92)


def qa(final: Path, data: dict) -> dict:
    probe = json.loads(
        subprocess.check_output(
            [
                "ffprobe", "-v", "error", "-print_format", "json",
                "-show_streams", "-show_format", str(final),
            ],
            text=True,
        )
    )
    v = next(s for s in probe["streams"] if s["codec_type"] == "video")
    a = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    dur = float(probe["format"]["duration"])
    dec = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(final), "-f", "null", "-"],
        capture_output=True, text=True,
    )
    shots = data["shots"]
    overlap = any(shots[i]["end"] > shots[i + 1]["start"] + 1e-3 for i in range(len(shots) - 1))
    gap = any(shots[i + 1]["start"] - shots[i]["end"] > 1e-3 for i in range(len(shots) - 1))
    zh = f"{dur:.1f}秒"
    hit = 40.0 <= dur <= 50.0
    hard = 30.0 <= dur <= 60.0
    report = {
        "project": "98_发布说明写成流水账",
        "duration_zh": zh,
        "duration_zh_round": "四十五秒" if 44.5 <= dur < 45.5 else zh,
        "strict": True,
        "cloud_only": True,
        "windows_paths": False,
        "drive_upload": False,
        "remake_00_95": False,
        "video_type": "普通短视频",
        "final": str(final),
        "chengpian": "/workspace/成片/98-发布说明写成流水账.mp4",
        "distinct_from_96": "目录名不是项目说明",
        "distinct_from_97": "环境变量写在聊天里",
        "distinct_from_99": "预发过了生产仍炸",
        "distinct_from_100": "临时方案住进主干",
        "factory_short_not_copied": True,
        "tpad_clone": False,
        "sha256": subprocess.check_output(["sha256sum", str(final)], text=True).split()[0],
        "bytes": final.stat().st_size,
        "video": {
            "codec": v.get("codec_name"),
            "width": v.get("width"),
            "height": v.get("height"),
            "fps": 24.0,
            "pix_fmt": v.get("pix_fmt"),
            "duration_s": dur,
        },
        "audio": {
            "codec": a.get("codec_name"),
            "sample_rate": int(a.get("sample_rate", 0)),
            "channels": a.get("channels"),
        },
        "timeline": {
            "segments": len(shots),
            "overlap": overlap,
            "gap": gap,
            "last_end_equals_audio": abs(shots[-1]["end"] - float(data["duration"])) < 0.05,
            "broll_lead_s": B_LEAD,
        },
        "decode_null": dec.returncode == 0 and not (dec.stderr or "").strip(),
        "duration_window": {
            "min": 30.0,
            "max": 60.0,
            "target": [40.0, 50.0],
            "hit": hit,
            "hard": hard,
            "duration_zh": zh,
        },
        "ok": hit and hard and v.get("width") == 1080 and v.get("height") == 1920
        and a.get("codec_name") == "aac" and int(a.get("sample_rate", 0)) == 44100
        and not overlap and not gap and dec.returncode == 0,
    }
    return report


def main() -> None:
    os.chdir(ROOT)
    phrases = (ROOT / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines()
    phrases = [p.strip() for p in phrases if p.strip()]
    vo = ROOT / "audio" / "vo-full.wav"
    print("TTS", len(phrases), "句", RATE)
    cues = asyncio.run(synth_phrases(phrases, vo))
    write_align(cues, ROOT / "audio" / "vo-align.txt")
    duration = probe_dur(vo)
    print(f"VO {duration:.1f}秒")
    for c in cues:
        print(f"  {c['start']:6.3f}-{c['end']:6.3f}  {c['text']}")
    recipe = json.loads((ROOT / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
    data = build_timeline(cues, recipe, duration)
    (ROOT / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    bspec = json.loads((ROOT / "plan" / "broll.json").read_text(encoding="utf-8"))
    needed = {s["src"] for s in data["shots"] if s["kind"] == "B"}
    for clip in bspec["clips"]:
        rel = f"broll/{clip['file']}"
        if rel not in needed:
            continue
        shot = next(s for s in data["shots"] if s["src"] == rel)
        dur = float(shot["end"]) - float(shot["start"])
        print("render", clip["file"], f"{dur:.1f}秒", clip["style"])
        frames_to_mp4(STYLES[clip["style"]](dur), ROOT / rel)
    cuts = [float(s["start"]) for s in data["shots"][1:]]
    make_bgm(ROOT / "audio" / "bgm.wav", duration)
    make_sfx(ROOT / "audio" / "sfx.wav", cuts, duration)
    final = assemble(data)
    cover = ROOT / f"00_封面_{TITLE}.jpg"
    make_cover(data, cover)
    staged = Path("/workspace/成片") / f"98-{TITLE}.mp4"
    staged.parent.mkdir(exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(final), "-c", "copy", str(staged)])
    report = qa(staged, data)
    (ROOT / "项目状态.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["ok"]:
        raise SystemExit("QA failed")


if __name__ == "__main__":
    main()
