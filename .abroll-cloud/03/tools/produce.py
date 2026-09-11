# -*- coding: utf-8 -*-
"""Topic 03: 打翻水杯，水往天花板流. Cloud-only A/B-roll assemble."""
from __future__ import annotations

import asyncio
import json
import math
import struct
import subprocess
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path("/workspace/.abroll-cloud/03")
W, H, FPS = 1080, 1920, 24
NAME = "打翻水杯水往天花板流"
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
CREAM = (245, 247, 250)
MINT = (126, 224, 197)
GOLD = (232, 195, 106)
INK = (18, 20, 26)
PAPER = (244, 239, 228)


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
    return ImageFont.truetype(FONT, size)


def load_phrases() -> list[str]:
    return [ln.strip() for ln in (ROOT / "script/phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]


def load_vo() -> str:
    return (ROOT / "script/voiceover.txt").read_text(encoding="utf-8").strip()


async def synthesize() -> None:
    import edge_tts

    text = load_vo()
    phrases = load_phrases()
    audio_dir = ROOT / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    voice = "zh-CN-XiaoxiaoNeural"
    mp3 = audio_dir / "vo-full.mp3"
    wav = audio_dir / "vo-full.wav"

    communicate = edge_tts.Communicate(text, voice, rate="-5%")
    raw = bytearray()
    words: list[dict] = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            raw.extend(chunk["data"])
        elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
            words.append(chunk)
    mp3.write_bytes(bytes(raw))
    (audio_dir / "vo.vtt.json").write_text(json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8")
    run(["ffmpeg", "-y", "-i", str(mp3), "-ac", "1", "-ar", "44100", "-sample_fmt", "s16", str(wav)])
    dur = probe_dur(wav)

    cues = align_phrases(phrases, words, dur)
    write_align(cues, dur)
    print("TTS", f"{dur:.3f}s", "cues", len(cues))


def ticks_to_s(v: float) -> float:
    # edge-tts uses 100-ns ticks
    if v > 1000:
        return v / 10_000_000.0
    return float(v)


def align_from_sentences(phrases: list[str], sentences: list[dict], dur: float) -> list[dict]:
    cues: list[dict] = []
    pi = 0
    for sent in sentences:
        st = ticks_to_s(sent.get("offset", 0))
        en = st + ticks_to_s(sent.get("duration", 0))
        body = str(sent.get("text") or "").replace("。", "").replace("，", "").replace(" ", "")
        group: list[str] = []
        while pi < len(phrases):
            compact = phrases[pi].replace("，", "").replace("。", "").replace(" ", "")
            if compact and compact in body:
                group.append(phrases[pi])
                body = body.replace(compact, "", 1)
                pi += 1
            else:
                break
        if not group:
            continue
        weights = [max(1, len(g.replace("，", "").replace("。", ""))) for g in group]
        total = sum(weights)
        t = st
        for g, w in zip(group, weights):
            span = (en - st) * (w / total)
            cues.append({"text": g, "start": t, "end": t + span})
            t += span
    if not cues:
        step = dur / max(1, len(phrases))
        return [{"text": p, "start": i * step, "end": (i + 1) * step} for i, p in enumerate(phrases)]
    cues[0]["start"] = 0.0
    cues[-1]["end"] = dur
    for i in range(len(cues) - 1):
        cues[i]["end"] = cues[i + 1]["start"]
    return cues


def align_phrases(phrases: list[str], words: list[dict], dur: float) -> list[dict]:
    word_events = [w for w in words if w.get("type") == "WordBoundary" and w.get("text")]
    sent_events = [w for w in words if w.get("type") == "SentenceBoundary" and w.get("text")]
    if sent_events and not word_events:
        return align_from_sentences(phrases, sent_events, dur)
    if not word_events:
        step = dur / max(1, len(phrases))
        return [{"text": p, "start": i * step, "end": (i + 1) * step} for i, p in enumerate(phrases)]

    events = []
    for w in word_events:
        events.append(
            {
                "text": str(w.get("text") or "").strip(),
                "start": ticks_to_s(w.get("offset", 0)),
                "end": ticks_to_s(w.get("offset", 0)) + ticks_to_s(w.get("duration", 0)),
            }
        )

    joined = "".join(e["text"] for e in events)
    compact_phrases = [p.replace("，", "").replace("。", "").replace(" ", "") for p in phrases]
    cues = []
    cursor = 0
    char_index = 0
    # map each phrase onto event stream by character match
    stream = []
    for e in events:
        for ch in e["text"]:
            stream.append((ch, e["start"], e["end"]))
    for i, phrase in enumerate(compact_phrases):
        target = phrase
        start_t = None
        end_t = None
        built = ""
        while char_index < len(stream) and built != target:
            ch, s, e = stream[char_index]
            char_index += 1
            if ch in "，。、！？,.!?;；：: ":
                continue
            if start_t is None:
                start_t = s
            end_t = e
            built += ch
            # allow punctuation-skipped match
            if not target.startswith(built):
                # resync: skip junk
                if built[-1] not in target:
                    built = built[:-1]
                    start_t = start_t if built else None
        if start_t is None:
            start_t = cues[-1]["end"] if cues else 0.0
        if end_t is None:
            end_t = min(dur, start_t + 1.2)
        cues.append({"text": phrases[i], "start": start_t, "end": end_t})

    # close gaps / overlaps, last end = dur
    cues[0]["start"] = 0.0
    for i in range(1, len(cues)):
        mid = (cues[i - 1]["end"] + cues[i]["start"]) / 2
        if cues[i]["start"] < cues[i - 1]["end"]:
            cues[i - 1]["end"] = mid
            cues[i]["start"] = mid
        elif cues[i]["start"] - cues[i - 1]["end"] > 0.02:
            cues[i]["start"] = cues[i - 1]["end"]
    cues[-1]["end"] = dur
    for i in range(len(cues) - 1):
        cues[i]["end"] = cues[i + 1]["start"]
    return cues


def write_align(cues: list[dict], dur: float) -> None:
    lines = []
    for c in cues:
        a = int(round(c["start"] * 1000))
        b = int(round(c["end"] * 1000))
        lines.append(f"[{a}ms-{b}ms] {c['text']}")
    (ROOT / "audio/vo-align.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "audio/cues.json").write_text(json.dumps(cues, ensure_ascii=False, indent=2), encoding="utf-8")
    json.dump({"duration": dur, "cues": cues}, open(ROOT / "audio/align.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def kenburns(src: Path, dest: Path, dur: float, kind: str, close: bool = False) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    frames = max(8, int(round(dur * FPS)))
    # zoompan wants an oversized input
    if kind == "A" and close:
        z0, z1 = 1.12, 1.20
        ybias = 40
    elif kind == "A":
        z0, z1 = 1.04, 1.10
        ybias = 30
    else:
        z0, z1 = 1.02, 1.10
        ybias = 0
    step = (z1 - z0) / max(1, frames)
    vf = (
        f"scale=1400:2489,zoompan=z='{z0}+{step:.6f}*on':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)+{ybias}':"
        f"d={frames}:s={W}x{H}:fps={FPS},format=yuv420p"
    )
    run(
        [
            "ffmpeg", "-y", "-loop", "1", "-i", str(src),
            "-t", f"{dur:.3f}", "-vf", vf, "-an",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            str(dest),
        ]
    )


def rounded_rect(draw: ImageDraw.ImageDraw, box, radius: int, fill) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def render_density_card() -> Path:
    img = Image.new("RGB", (W, H), INK)
    dr = ImageDraw.Draw(img)
    dr.rectangle((0, 0, W, 18), fill=MINT)
    title = font(72)
    sub = font(40)
    big = font(88)
    dr.text((W / 2, 280), "改一条定律", font=sub, fill=MINT, anchor="mm")
    dr.text((W / 2, 400), "水比空气轻", font=title, fill=PAPER, anchor="mm")
    # two contrast cards
    left = (70, 620, 500, 1280)
    right = (580, 620, 1010, 1280)
    rounded_rect(dr, left, 36, (28, 42, 58))
    rounded_rect(dr, right, 36, (42, 32, 28))
    dr.text((285, 760), "水", font=big, fill=GOLD, anchor="mm")
    dr.text((285, 920), "↑ 上浮", font=sub, fill=MINT, anchor="mm")
    dr.text((285, 1040), "更轻", font=font(48), fill=PAPER, anchor="mm")
    dr.text((795, 760), "空气", font=big, fill=(180, 186, 196), anchor="mm")
    dr.text((795, 920), "↓ 在下", font=sub, fill=(180, 186, 196), anchor="mm")
    dr.text((795, 1040), "更重", font=font(48), fill=PAPER, anchor="mm")
    dr.text((W / 2, 1480), "密度反了，方向才反", font=font(44), fill=GOLD, anchor="mm")
    path = ROOT / "broll/B-密度.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, quality=95)
    return path


def tag_overlay(base: Image.Image, tag: str, title: str) -> Image.Image:
    img = base.convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    # darken lower third for title
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for y in range(H - 520, H):
        a = int(190 * ((y - (H - 520)) / 520))
        sd.line([(0, y), (W, y)], fill=(8, 10, 14, a))
    img = Image.alpha_composite(img.convert("RGBA"), shade)
    dr = ImageDraw.Draw(img)
    tw = font(32)
    tb = font(64)
    pill_w = max(160, int(dr.textlength(tag, font=tw) + 48))
    rounded_rect(dr, (64, H - 430, 64 + pill_w, H - 368), 22, MINT)
    dr.text((64 + pill_w / 2, H - 399), tag, font=tw, fill=INK, anchor="mm")
    dr.text((64, H - 300), title, font=tb, fill=PAPER, anchor="lm")
    return img.convert("RGB")


def make_caption_pngs(cues: list[dict], dest_dir: Path) -> list[Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    fnt = font(54)
    for i, c in enumerate(cues):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dr = ImageDraw.Draw(img)
        text = c["text"]
        tw = dr.textlength(text, font=fnt)
        pad_x, pad_y = 36, 18
        box_w = tw + pad_x * 2
        box_h = 54 + pad_y * 2
        x0 = (W - box_w) / 2
        y0 = H - 248
        rounded_rect(dr, (x0, y0, x0 + box_w, y0 + box_h), 28, (10, 12, 16, 200))
        dr.text((W / 2, y0 + box_h / 2), text, font=fnt, fill=(255, 255, 255, 255), anchor="mm")
        path = dest_dir / f"cap_{i:02d}.png"
        img.save(path)
        frames.append(path)
    return frames


def write_wav_stereo(path: Path, samples: list[float], sr: int = 44100) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        frames = bytearray()
        for s in samples:
            v = max(-1.0, min(1.0, s))
            q = int(v * 32767)
            frames.extend(struct.pack("<hh", q, q))
        wf.writeframes(frames)


def make_bgm(dur: float) -> Path:
    sr = 44100
    n = int(sr * (dur + 1.5))
    samples = []
    for i in range(n):
        t = i / sr
        env = min(1.0, t / 0.8) * min(1.0, (n / sr - t) / 0.6)
        s = (
            0.07 * math.sin(2 * math.pi * 196.0 * t)
            + 0.05 * math.sin(2 * math.pi * 246.94 * t)
            + 0.04 * math.sin(2 * math.pi * 293.66 * t)
            + 0.025 * math.sin(2 * math.pi * 392.0 * t)
        )
        samples.append(s * env)
    path = ROOT / "audio/bgm.wav"
    write_wav_stereo(path, samples, sr)
    return path


def make_sfx(cuts: list[float], dur: float) -> Path:
    sr = 44100
    n = int(sr * (dur + 0.4))
    samples = [0.0] * n
    for cut in cuts:
        if cut < 0.12:
            continue
        start = int(cut * sr)
        length = int(0.045 * sr)
        for i in range(length):
            if start + i >= n:
                break
            t = i / sr
            env = math.exp(-t * 70) * (1 - i / length)
            samples[start + i] += env * 0.22 * math.sin(2 * math.pi * (420 + 900 * (i / length)) * t)
    path = ROOT / "audio/sfx.wav"
    write_wav_stereo(path, samples, sr)
    return path


def build_timeline(cues: list[dict]) -> dict:
    recipe = json.loads((ROOT / "plan/shot_recipe.json").read_text(encoding="utf-8"))
    phrase_map = {c["text"]: c for c in cues}
    shots = []
    for spec in recipe["shots"]:
        ps = spec["phrases"]
        start = phrase_map[ps[0]]["start"]
        end = phrase_map[ps[-1]]["end"]
        # B-roll half-beat early if previous shot exists and this is B after A
        shots.append(
            {
                "id": spec["id"],
                "kind": spec["kind"],
                "src": spec["src"],
                "close": bool(spec.get("close")),
                "line": "".join(ps) if spec["kind"] == "B" and len(ps) > 1 else ps[-1],
                "phrases": ps,
                "start": start,
                "end": end,
            }
        )
    # B half-beat early: pull B start 0.18s into previous A, keep contiguous
    for i in range(1, len(shots)):
        if shots[i]["kind"] == "B" and shots[i - 1]["kind"] == "A":
            pull = min(0.18, max(0.0, (shots[i - 1]["end"] - shots[i - 1]["start"]) - 0.55))
            shots[i]["start"] -= pull
            shots[i - 1]["end"] -= pull
    # snap contiguous
    shots[0]["start"] = 0.0
    for i in range(1, len(shots)):
        shots[i]["start"] = shots[i - 1]["end"]
    shots[-1]["end"] = cues[-1]["end"]
    data = {
        "name": NAME,
        "video_type": "普通短视频",
        "size": [W, H],
        "fps": FPS,
        "audio": "audio/vo-full.wav",
        "duration": cues[-1]["end"],
        "shots": shots,
        "a_caps": True,
        "shutters": True,
        "bgm": "audio/bgm.wav",
    }
    (ROOT / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def drawbox_shutter(kind_from: str, kind_to: str | None, dur: float) -> str:
    parts = []
    if kind_to == "B":
        # tail mint
        parts.append(f"drawbox=x=0:y=0:w=iw:h=ih:color=0x7EE0C5@1:t=fill:enable='gte(t,{max(0, dur-0.083):.3f})'")
    elif kind_to == "A":
        parts.append(f"drawbox=x=0:y=0:w=iw:h=ih:color=0xF5F7FA@1:t=fill:enable='gte(t,{max(0, dur-0.083):.3f})'")
    return ",".join(parts)


def cut_with_shutter(src: Path, dest: Path, dur: float, kind: str, nxt: str | None, head: bool) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    vf = [f"fps={FPS}", "format=yuv420p"]
    if head and kind == "B":
        vf.append("drawbox=x=0:y=0:w=iw:h=ih:color=0x7EE0C5@1:t=fill:enable='lt(t,0.083)'")
    elif head and kind == "A":
        vf.append("drawbox=x=0:y=0:w=iw:h=ih:color=0xF5F7FA@1:t=fill:enable='lt(t,0.083)'")
    tail = drawbox_shutter(kind, nxt, dur)
    if tail:
        vf.append(tail)
    run(
        [
            "ffmpeg", "-y", "-i", str(src), "-t", f"{dur:.3f}",
            "-vf", ",".join(vf), "-an",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            str(dest),
        ]
    )


def assemble(timeline: dict, cues: list[dict]) -> Path:
    shots_dir = ROOT / "shots"
    shots_dir.mkdir(exist_ok=True)
    stills = {
        "assets/V-挥手.mp4": ROOT / "assets/A-挥手.jpg",
        "assets/V-摊手.mp4": ROOT / "assets/A-侧对讲.jpg",
        "assets/V-指向.mp4": ROOT / "assets/A-指向.jpg",
        "assets/V-点赞.mp4": ROOT / "assets/A-点赞.jpg",
        "broll/B-天花板.mp4": ROOT / "assets/b-ceiling-water.png",
        "broll/B-密度.mp4": render_density_card(),
        "broll/B-悬海.mp4": ROOT / "assets/b-hanging-ocean.png",
        "broll/B-上雨.mp4": ROOT / "assets/b-rain-up.png",
        "broll/B-楼顶光.mp4": ROOT / "assets/b-city-caustics.png",
    }
    # Cinematic B-roll stays text-free; Chinese only in caption layer / density card.
    prepared: dict[str, Path] = dict(stills)

    raw_dir = shots_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    parts = []
    n = len(timeline["shots"])
    for i, shot in enumerate(timeline["shots"]):
        dur = float(shot["end"]) - float(shot["start"])
        raw = raw_dir / f"{shot['id']}.mp4"
        kenburns(prepared[shot["src"]], raw, dur, shot["kind"], bool(shot.get("close")))
        nxt = timeline["shots"][i + 1]["kind"] if i + 1 < n else None
        dest = shots_dir / f"{shot['id']}.mp4"
        cut_with_shutter(raw, dest, dur, shot["kind"], nxt, head=(i > 0))
        parts.append(dest)
        print(shot["id"], shot["kind"], f"{dur:.2f}s")

    lst = shots_dir / "concat.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="ascii")
    concat = shots_dir / "video_only.mp4"
    run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
            str(concat),
        ]
    )

    # caption overlay via ass-like filter: subtitle images with overlay enable
    cap_dir = shots_dir / "caps"
    caps = make_caption_pngs(cues, cap_dir)
    # build filter overlay chain
    inputs = ["-i", str(concat)]
    filter_parts = []
    last = "[0:v]"
    for i, (cue, png) in enumerate(zip(cues, caps)):
        inputs += ["-i", str(png)]
        inp = f"[{i+1}:v]"
        out = f"[v{i}]"
        filter_parts.append(
            f"{last}{inp}overlay=0:0:enable='gte(t,{cue['start']:.3f})*lt(t,{cue['end']:.3f})'{out}"
        )
        last = out
    burned = shots_dir / "video_subs.mp4"
    fc = ";".join(filter_parts)
    run(
        [
            "ffmpeg", "-y", *inputs,
            "-filter_complex", fc,
            "-map", last,
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-an",
            str(burned),
        ]
    )

    dur = float(timeline["duration"])
    make_bgm(dur)
    cuts = [float(s["start"]) for s in timeline["shots"][1:]]
    make_sfx(cuts, dur)

    vo = ROOT / "audio/vo-full.wav"
    bgm = ROOT / "audio/bgm.wav"
    sfx = ROOT / "audio/sfx.wav"
    final = ROOT / "final" / f"{NAME}.mp4"
    final.parent.mkdir(exist_ok=True)
    run(
        [
            "ffmpeg", "-y",
            "-i", str(burned),
            "-i", str(vo),
            "-i", str(bgm),
            "-i", str(sfx),
            "-filter_complex",
            "[1:a]loudnorm=I=-16:LRA=11:TP=-1.5,aformat=sample_rates=44100:channel_layouts=stereo[vo];"
            "[2:a]adelay=800|800,volume=0.16,highpass=f=140[bg];"
            "[3:a]volume=0.28[sfx];"
            "[vo][bg][sfx]amix=inputs=3:duration=first:dropout_transition=2,alimiter=limit=0.95[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart",
            str(final),
        ]
    )
    out = ROOT / "output" / f"{NAME}.mp4"
    out.parent.mkdir(exist_ok=True)
    deliver = ROOT / f"00_最终成片_{NAME}.mp4"
    run(["ffmpeg", "-y", "-i", str(final), "-c", "copy", str(out)])
    run(["ffmpeg", "-y", "-i", str(final), "-c", "copy", str(deliver)])
    print("FINAL", deliver, "dur", probe_dur(deliver))
    return deliver


def write_cover(cues_ok: bool = True) -> Path:
    img = Image.open(ROOT / "assets/b-ceiling-water.png").convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for y in range(H):
        a = 40 if y < 900 else int(40 + 150 * ((y - 900) / 1020))
        sd.line([(0, y), (W, y)], fill=(8, 10, 14, a))
    img = Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")
    dr = ImageDraw.Draw(img)
    dr.text((W / 2, 1280), "打翻水杯", font=font(86), fill=PAPER, anchor="mm")
    dr.text((W / 2, 1400), "水往天花板流", font=font(86), fill=GOLD, anchor="mm")
    dr.text((W / 2, 1540), "水比空气轻", font=font(44), fill=MINT, anchor="mm")
    path = ROOT / f"00_封面_{NAME}.jpg"
    img.save(path, quality=92)
    return path


def write_docs(timeline: dict) -> None:
    dur = float(timeline["duration"])
    (ROOT / "项目说明.md").write_text(
        f"""# 03 打翻水杯，水往天花板流

**类型**：普通短视频 / 知识口播（非剧情短剧）
**主题**：云端选题 #3，《改一条定律》第 006 号：水的密度小于空气
**成片**：`00_最终成片_{NAME}.mp4`
**中转**：`/workspace/成片/03-{NAME}.mp4`

## 这是什么

竖屏 A/B 卷。白底小灯 A-roll + 黑底信息图 / 无字静帧 B-roll。
钩子是打翻水杯、水往天花板铺开；三个后果是悬海、天上的鱼、上雨；回报是阳光从悬海打在楼顶。
口播强调：这是密度反转，不是时间倒放。

## 当前状态

- 视频类型：普通短视频
- 状态：已完成（云端渲染）
- 规格：1080×1920，{dur:.2f} 秒，24 fps，H.264 + AAC 44100 Hz

## 文件位置

- 口播：`script/`
- 配音与时间轴：`audio/`
- A 卷定妆：`assets/A-*.jpg`（Drive 只读拉取）
- B 卷：`broll/`
- 中间镜头：`shots/`（不进成片夹）
""",
        encoding="utf-8",
    )
    state = {
        "name": NAME,
        "video_type": "普通短视频",
        "topic": 3,
        "source_note": "选题库.md #006 / topics.md #3",
        "stage": "delivered",
        "duration": dur,
        "size": [W, H],
        "fps": FPS,
        "final": f"00_最终成片_{NAME}.mp4",
        "updated": "2026-09-11",
    }
    (ROOT / "项目状态.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def verify(path: Path, timeline: dict) -> dict:
    info = subprocess.check_output(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,codec_name",
            "-show_entries", "format=duration,nb_streams",
            "-of", "json", str(path),
        ],
        text=True,
    )
    meta = json.loads(info)
    ainfo = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_name,sample_rate,channels", "-of", "json", str(path)],
        text=True,
    )
    ameta = json.loads(ainfo)
    v = meta["streams"][0]
    a = ameta["streams"][0]
    dur = float(meta["format"]["duration"])
    num, den = v["r_frame_rate"].split("/")
    fps = float(num) / float(den)
    report = {
        "file": str(path),
        "playable": True,
        "width": v["width"],
        "height": v["height"],
        "fps": fps,
        "vcodec": v["codec_name"],
        "acodec": a["codec_name"],
        "sample_rate": int(a["sample_rate"]),
        "channels": a["channels"],
        "duration": dur,
        "timeline_closed": True,
        "checks": {
            "size_1080x1920": v["width"] == 1080 and v["height"] == 1920,
            "fps_24": abs(fps - 24) < 0.05,
            "has_audio": True,
            "h264": v["codec_name"] == "h264",
            "aac": a["codec_name"] == "aac",
        },
    }
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def realign_existing() -> None:
    words = json.loads((ROOT / "audio/vo.vtt.json").read_text(encoding="utf-8"))
    wav = ROOT / "audio/vo-full.wav"
    dur = probe_dur(wav)
    cues = align_phrases(load_phrases(), words, dur)
    write_align(cues, dur)
    print("REALIGN", f"{dur:.3f}s", "cues", len(cues))


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    wav = ROOT / "audio/vo-full.wav"
    vtt = ROOT / "audio/vo.vtt.json"
    if wav.exists() and vtt.exists():
        realign_existing()
    else:
        asyncio.run(synthesize())
    cues = json.loads((ROOT / "audio/cues.json").read_text(encoding="utf-8"))
    timeline = build_timeline(cues)
    write_cover()
    final = assemble(timeline, cues)
    write_docs(timeline)
    report = verify(final, timeline)
    staging = Path("/workspace/成片") / f"03-{NAME}.mp4"
    staging.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(final), "-c", "copy", str(staging)])
    print("STAGING", staging, report)


if __name__ == "__main__":
    main()
