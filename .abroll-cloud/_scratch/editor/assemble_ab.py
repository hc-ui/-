# -*- coding: utf-8 -*-
"""Editor QA: assemble complete A-roll + B-roll mp4s. Drafts stay in _scratch."""
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path("/workspace")
CLOUD = ROOT / ".abroll-cloud"
SCRATCH = CLOUD / "_scratch" / "editor"
DELIVER = ROOT / "成片"
W, H, FPS = 1080, 1920, 24
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
NOTO = CLOUD / "02" / "fonts" / "NotoSansSC-Bold.otf"
BG = (11, 13, 18)
MINT = (126, 224, 197)
YELLOW = (245, 193, 92)
WHITE = (245, 247, 250)
MUTED = (154, 162, 176)
CARD = (24, 28, 38)
CREAM = (245, 247, 250)

V_WAVE = CLOUD / "02" / "assets" / "V-挥手.mp4"
V_SHRUG = CLOUD / "02" / "assets" / "V-摊手.mp4"
V_POINT = CLOUD / "02" / "assets" / "V-指向.mp4"
V_THUMB = CLOUD / "02" / "assets" / "V-点赞.mp4"
A_WAVE = CLOUD / "01" / "assets" / "A-挥手.jpg"
A_TALK = CLOUD / "01" / "assets" / "A-正对讲.jpg"
A_POINT = CLOUD / "01" / "assets" / "A-指向.jpg"
A_THUMB = CLOUD / "01" / "assets" / "A-点赞.jpg"
A_EXPLAIN = CLOUD / "01" / "assets" / "A-讲解.jpg"


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
    path = str(NOTO) if NOTO.exists() else FONT
    return ImageFont.truetype(path, size)


def cover_fit(im: Image.Image, w: int, h: int, zoom: float = 1.0, pan_y: float = 0.0) -> Image.Image:
    im = im.convert("RGB")
    scale = max(w / im.width, h / im.height) * zoom
    nw, nh = max(w, int(im.width * scale)), max(h, int(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - w) // 2
    y = int((nh - h) * (0.42 + pan_y))
    y = max(0, min(nh - h, y))
    return im.crop((x, y, x + w, y + h))


def split_caption(text: str) -> list[str]:
    text = text.strip().strip("。").strip()
    if "，" in text and len(text) > 9:
        a, b = text.split("，", 1)
        return [a, b]
    if len(text) > 10:
        mid = len(text) // 2
        return [text[:mid], text[mid:]]
    return [text]


def pill(base: Image.Image, lines: list[str], y: int = 168) -> None:
    lines = [ln for ln in lines if ln]
    if not lines:
        return
    fnt = font(52 if max(len(s) for s in lines) <= 8 else 42)
    dummy = ImageDraw.Draw(base)
    widths, heights = [], []
    for line in lines:
        x0, y0, x1, y1 = dummy.textbbox((0, 0), line, font=fnt)
        widths.append(x1 - x0)
        heights.append(y1 - y0)
    tw = max(widths)
    line_h = max(heights) + 12
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


def make_broll_card(title: str, cards: list[str], punch: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle((72, 88, 116, 92), fill=MINT)
    d.text((136, 72), "B-ROLL", font=font(22), fill=MUTED)
    d.text((540, 220), title, font=font(56), fill=WHITE, anchor="mm")
    if cards:
        gap = 28
        cw = (W - 160 - gap) // 2
        ch = 360
        y = 420
        left, right = (cards + ["", ""])[:2]
        for i, text in enumerate((left, right)):
            x = 80 + i * (cw + gap)
            fill = (28, 36, 34) if i == 0 else (32, 30, 22)
            border = MINT if i == 0 else YELLOW
            d.rounded_rectangle((x, y, x + cw, y + ch), radius=32, outline=border, width=4, fill=fill)
            d.text((x + cw / 2, y + ch / 2), text, font=font(44), fill=WHITE, anchor="mm")
    d.rounded_rectangle((90, 1480, 990, 1720), radius=36, fill=CARD)
    d.text((540, 1600), punch, font=font(48), fill=YELLOW, anchor="mm")
    im.save(dest, quality=94)


def frames_to_mp4(frames: list[Image.Image], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "18",
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


def extract_frame(src: Path, t: float, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-ss", f"{max(0, t):.3f}", "-i", str(src), "-frames:v", "1", "-q:v", "2", str(dest)])


def still_from_src(src: Path, cache: Path, t: float = 0.35) -> Image.Image:
    if src.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
        return Image.open(src).convert("RGB")
    jpg = cache.with_suffix(".src.jpg")
    if not jpg.exists():
        extract_frame(src, t, jpg)
    return Image.open(jpg).convert("RGB")


def render_shot(src: Path, kind: str, dur: float, line: str, dest: Path, close: bool, label: str, cards: list[str] | None) -> None:
    n = max(1, round(dur * FPS))
    cache = dest.with_suffix(".cache.jpg")
    photo = still_from_src(src, cache)
    frames = []
    for i in range(n):
        t = i / FPS
        p = t / max(dur, 0.01)
        if kind == "A":
            zoom = (1.20 - 0.05 * p) if close else (1.06 + 0.04 * p)
            pan = (-0.16 + 0.04 * p) if close else (-0.06 + 0.05 * p)
            img = cover_fit(photo, W, H, zoom=zoom, pan_y=pan)
            eyebrow(img, label)
            pill(img, split_caption(line))
        else:
            zoom = 1.04 + 0.06 * p
            img = Image.new("RGB", (W, H), BG)
            if src.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"} or src.suffix.lower() == ".mp4":
                pic = cover_fit(photo, W, H, zoom=zoom, pan_y=-0.04 + 0.06 * p)
                # darken for type
                dark = Image.new("RGB", (W, H), BG)
                pic = Image.blend(pic, dark, 0.28)
                img.paste(pic)
            eyebrow(img, "B-ROLL")
            if cards:
                d = ImageDraw.Draw(img)
                d.rounded_rectangle((80, 420, 500, 780), radius=28, fill=(20, 42, 38))
                d.rounded_rectangle((580, 420, 1000, 780), radius=28, fill=(42, 34, 16))
                d.text((290, 600), cards[0], font=font(40), fill=MINT, anchor="mm")
                d.text((790, 600), cards[1] if len(cards) > 1 else "", font=font(40), fill=YELLOW, anchor="mm")
            pill(img, split_caption(line), y=200)
        frames.append(img)
    frames_to_mp4(frames, dest)


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


def mix(video: Path, audio: Path, dest: Path, dur: float) -> None:
    bgm = dest.with_name(dest.stem + "-bgm.wav")
    make_bgm(bgm, dur + 0.4)
    run([
        "ffmpeg", "-y",
        "-i", str(video),
        "-i", str(audio),
        "-i", str(bgm),
        "-filter_complex",
        "[1:a]loudnorm=I=-16:LRA=11:TP=-1.5,aformat=sample_rates=44100:channel_layouts=stereo[vo];"
        "[2:a]volume=0.16,adelay=250|250[bg];"
        "[vo][bg]amix=inputs=2:duration=first:dropout_transition=2,alimiter=limit=0.92[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        str(dest),
    ])


def concat(parts: list[Path], dest: Path) -> None:
    lst = dest.with_suffix(".concat.txt")
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
        "-r", str(FPS), str(dest),
    ])


def pick_a_src(shot: str, index: int, n: int, prefer_video: bool = True) -> Path:
    s = shot or ""
    if "挥手" in s or "问候" in s:
        return V_WAVE if prefer_video and V_WAVE.exists() else A_WAVE
    if "指向" in s or "方法" in s:
        return V_POINT if prefer_video and V_POINT.exists() else A_POINT
    if "点赞" in s or "收束" in s:
        return V_THUMB if prefer_video and V_THUMB.exists() else A_THUMB
    if "摊手" in s or "后果" in s:
        return V_SHRUG if prefer_video and V_SHRUG.exists() else A_EXPLAIN
    if "正对" in s or "讲解" in s or "题目" in s:
        return V_SHRUG if prefer_video and V_SHRUG.exists() else A_TALK
    cycle = [V_WAVE, V_SHRUG, V_POINT, V_THUMB]
    stills = [A_WAVE, A_TALK, A_POINT, A_THUMB]
    if prefer_video and cycle[index % 4].exists():
        return cycle[index % 4]
    return stills[index % 4]


def cards_from_shot(shot: str, line: str) -> list[str]:
    if "对照卡" in (shot or "") and "：" in shot:
        rest = shot.split("：", 1)[1]
        if " vs " in rest:
            return [p.strip() for p in rest.split(" vs ", 1)]
        if "、" in rest:
            return [p.strip() for p in rest.split("、", 1)]
        if "缺" in rest:
            return [rest.replace("缺", "").strip() or "有", "缺" + rest.split("缺", 1)[-1]]
    if "，" in line:
        return [p.strip("。") for p in line.split("，", 1)]
    return [line.strip("。")[:6], "对照"]


def allocate(phrases: list[dict], duration: float) -> list[tuple[dict, float, float]]:
    weights = [max(2.0, float(len(p["line"]))) for p in phrases]
    total = sum(weights)
    # B-roll early by ~0.12s: just start B a hair sooner by stealing from previous A
    out = []
    t = 0.0
    for i, (p, w) in enumerate(zip(phrases, weights)):
        if i == len(phrases) - 1:
            end = duration
        else:
            end = t + duration * (w / total)
        if i > 0 and p.get("kind") == "B" and out and out[-1][0].get("kind") == "A":
            steal = min(0.12, (out[-1][2] - out[-1][1]) * 0.15)
            prev = out[-1]
            out[-1] = (prev[0], prev[1], prev[2] - steal)
            t = prev[2] - steal
            end = t + duration * (w / total) if i != len(phrases) - 1 else duration
        out.append((p, t, end))
        t = end
    if out:
        p, a, _ = out[-1]
        out[-1] = (p, a, duration)
    return out


def assemble_from_shots(job: str, title: str, audio: Path, shots: list[dict], dest: Path) -> Path:
    work = SCRATCH / job
    work.mkdir(parents=True, exist_ok=True)
    parts = []
    for i, shot in enumerate(shots):
        dur = float(shot["end"]) - float(shot["start"])
        src = Path(shot["src"])
        if not src.is_absolute():
            # resolve later by caller putting absolute
            src = Path(shot["src"])
        part = work / f"{shot['id']}.mp4"
        print(f"  {job} {shot['id']} {shot['kind']} {dur:.2f}s {src.name}")
        render_shot(
            src=src,
            kind=shot["kind"],
            dur=dur,
            line=shot["line"],
            dest=part,
            close=bool(shot.get("close")),
            label=f"{'A-ROLL' if shot['kind']=='A' else 'B-ROLL'} / {shot['id']}",
            cards=shot.get("cards"),
        )
        parts.append(part)
    concat_path = work / "video_only.mp4"
    concat(parts, concat_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    mix(concat_path, audio, dest, float(shots[-1]["end"]))
    print("FINAL", dest, "dur", probe_dur(dest))
    return dest


def assemble_catalog_topic(topic: dict, number: str, dest_name: str | None = None) -> Path:
    slug = topic["slug"]
    title = topic["title"]
    audio = CLOUD / "aroll" / "audio" / f"{slug}.wav"
    if not audio.exists():
        raise FileNotFoundError(audio)
    duration = probe_dur(audio)
    timed = allocate(topic["phrases"], duration)
    shots = []
    a_idx = 0
    for i, (p, start, end) in enumerate(timed):
        kind = p["kind"]
        shot = p.get("shot", "")
        if kind == "A":
            src = pick_a_src(shot, a_idx, len(topic["phrases"]))
            a_idx += 1
            cards = None
            close = i == 0
        else:
            card_png = SCRATCH / "broll" / f"{slug}_{i}.png"
            pair = cards_from_shot(shot, p["line"])
            make_broll_card(p["line"].strip("。")[:10], pair, topic.get("cover_line", p["line"]), card_png)
            src = card_png
            cards = pair
            close = False
        shots.append({
            "id": f"S{i+1:02d}",
            "kind": kind,
            "start": start,
            "end": end,
            "src": str(src),
            "line": p["line"],
            "close": close,
            "cards": cards,
        })
    out = DELIVER / (dest_name or f"{number}-{title.replace('，', '')}.mp4")
    return assemble_from_shots(slug, title, audio, shots, out)


def assemble_topic01() -> Path:
    data = json.loads((CLOUD / "01" / "timeline.json").read_text(encoding="utf-8"))
    audio = CLOUD / "01" / data["audio"]
    shots = []
    for s in data["shots"]:
        src = CLOUD / "01" / s["src"]
        shots.append({
            **s,
            "src": str(src),
            "cards": s.get("cards"),
        })
    dest = DELIVER / "01-口头答应没有截止日.mp4"
    return assemble_from_shots("01_deadline", data["title"], audio, shots, dest)


def ensure_tts(text: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    # prefer already-made factory wav
    run(["edge-tts", "--voice", "zh-CN-YunyangNeural", "--text", text, "--write-media", str(dest)])
    return dest


def assemble_topic03() -> Path:
    vo = (CLOUD / "03" / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    factory = CLOUD / "aroll" / "audio" / "03_打翻水杯水往天花板流.wav"
    audio = factory if factory.exists() else ensure_tts(vo, CLOUD / "03" / "audio" / "vo-full.wav")
    duration = probe_dur(audio)
    phrases = [
        {"kind": "A", "line": "大家好", "src": CLOUD / "03" / "assets" / "A-挥手.jpg", "close": True},
        {"kind": "A", "line": "打翻水杯，水往天花板流", "src": CLOUD / "03" / "assets" / "A-正对讲.jpg"},
        {"kind": "A", "line": "不是倒放", "src": CLOUD / "03" / "assets" / "xiaodeng-shrug.png"},
        {"kind": "B", "line": "是水比空气轻", "src": CLOUD / "03" / "assets" / "b-ceiling-water.png", "cards": ["水", "比空气轻"]},
        {"kind": "B", "line": "海挂到云下面", "src": CLOUD / "03" / "assets" / "b-hanging-ocean.png", "cards": ["海", "挂在云下"]},
        {"kind": "B", "line": "鱼在天上游", "src": CLOUD / "03" / "assets" / "b-city-caustics.png", "cards": ["鱼", "天上游"]},
        {"kind": "B", "line": "雨变成上雨", "src": CLOUD / "03" / "assets" / "b-rain-up.png", "cards": ["雨", "往上走"]},
        {"kind": "A", "line": "阳光从海里打在楼顶", "src": CLOUD / "03" / "assets" / "A-点赞.jpg"},
    ]
    timed = allocate(phrases, duration)
    shots = []
    for i, (p, start, end) in enumerate(timed):
        shots.append({
            "id": f"S{i+1:02d}",
            "kind": p["kind"],
            "start": start,
            "end": end,
            "src": str(p["src"]),
            "line": p["line"],
            "close": bool(p.get("close")),
            "cards": p.get("cards"),
        })
    dest = DELIVER / "03-打翻水杯水往天花板流.mp4"
    return assemble_from_shots("03_water", "打翻水杯水往天花板流", audio, shots, dest)


def assemble_topic04() -> Path:
    vo = (CLOUD / "04" / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    factory = CLOUD / "aroll" / "audio" / "04_咖啡自己滑向桌边.wav"
    audio = factory if factory.exists() else ensure_tts(vo, CLOUD / "04" / "audio" / "vo-full.wav")
    duration = probe_dur(audio)
    phrases = [
        {"kind": "A", "line": "大家好", "shot": "挥手/问候"},
        {"kind": "A", "line": "咖啡自己滑向桌边", "shot": "正对讲"},
        {"kind": "A", "line": "不是飘", "shot": "摊手：后果"},
        {"kind": "B", "line": "是摩擦力归零", "shot": "对照卡：摩擦 vs 归零"},
        {"kind": "B", "line": "停着的车开始溜", "shot": "对照卡：停车 vs 溜坡"},
        {"kind": "B", "line": "堆好的东西塌成一摊", "shot": "对照卡：堆好 vs 塌摊"},
        {"kind": "B", "line": "绳结自己松开", "shot": "对照卡：打结 vs 自解"},
        {"kind": "A", "line": "三分钟到，整条街冻在滑完的样子", "shot": "收束"},
    ]
    topic = {"slug": "04_coffee", "title": "咖啡自己滑向桌边", "phrases": phrases, "cover_line": "三分钟到，整条街冻住"}
    # reuse catalog assembler timing but custom audio
    timed = allocate(phrases, duration)
    shots = []
    a_idx = 0
    for i, (p, start, end) in enumerate(timed):
        if p["kind"] == "A":
            src = pick_a_src(p.get("shot", ""), a_idx, len(phrases))
            a_idx += 1
            cards = None
        else:
            pair = cards_from_shot(p.get("shot", ""), p["line"])
            png = SCRATCH / "broll" / f"04_{i}.png"
            make_broll_card(p["line"].strip("。")[:10], pair, "摩擦力归零 · 三分钟", png)
            src = png
            cards = pair
        shots.append({
            "id": f"S{i+1:02d}",
            "kind": p["kind"],
            "start": start,
            "end": end,
            "src": str(src),
            "line": p["line"],
            "close": i == 0,
            "cards": cards,
        })
    dest = DELIVER / "04-咖啡自己滑向桌边.mp4"
    return assemble_from_shots("04_coffee", topic["title"], audio, shots, dest)


def main() -> None:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    DELIVER.mkdir(parents=True, exist_ok=True)
    catalog = json.loads((CLOUD / "aroll" / "catalog.json").read_text(encoding="utf-8"))
    by_slug = {t["slug"]: t for t in catalog["topics"]}

    existing = {p.name for p in DELIVER.glob("*.mp4")}
    jobs = []

    if not any(n.startswith("01-") for n in existing) and (CLOUD / "01" / "timeline.json").exists():
        jobs.append(("01", assemble_topic01))
    if not any(n.startswith("03-") for n in existing) and (CLOUD / "03" / "script" / "voiceover.txt").exists():
        jobs.append(("03", assemble_topic03))
    if not any(n.startswith("04-") for n in existing) and (CLOUD / "04" / "script" / "voiceover.txt").exists():
        jobs.append(("04", assemble_topic04))

    extras = [
        ("07", "348_演练脚本没有中止口令"),
        ("08", "349_工单升级没有时限"),
        ("09", "350_值班手机没有备机号"),
        ("10", "353_口播别念链接"),
        ("11", "354_列表项先给结果"),
    ]
    for num, slug in extras:
        if any(n.startswith(f"{num}-") for n in existing):
            continue
        if slug not in by_slug:
            continue
        title = by_slug[slug]["title"]
        if any(title in n for n in existing):
            continue
        jobs.append((num, lambda t=by_slug[slug], n=num: assemble_catalog_topic(t, n)))

    for name, fn in jobs:
        print("====", name)
        fn()


if __name__ == "__main__":
    main()
