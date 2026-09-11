#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 40 加长：对齐为什么对齐到半夜。40-long，无 freeze-pad。"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from PIL import ImageDraw

sys.path.insert(0, "/workspace/.abroll-cloud")
import _longcut as L

ROOT = Path(__file__).resolve().parent
NAME = "对齐为什么对齐到半夜"
STAGED_NAME = "40-对齐为什么对齐到半夜.mp4"
W, H, FPS = L.W, L.H, L.FPS
BG, CARD, MINT, YELLOW, WHITE, MUTED, RED, INK, AMBER = (
    L.BG, L.CARD, L.MINT, L.YELLOW, L.WHITE, L.MUTED, L.RED, L.INK, L.AMBER,
)
font, appear, lerp, mix, rounded, tag, new_bg = L.font, L.appear, L.lerp, L.mix, L.rounded, L.tag, L.new_bg
bob, strike_line, check_badge, frames_to_mp4 = L.bob, L.strike_line, L.check_badge, L.frames_to_mp4


def draw_clock(draw, cx: int, cy: int, scale: float, a: float, t: float) -> None:
    if a <= 0.04:
        return
    r = int(118 * scale)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=mix(BG, CARD, a), outline=mix(CARD, AMBER, a), width=8)
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        x0 = cx + int((r - 18) * math.cos(ang))
        y0 = cy + int((r - 18) * math.sin(ang))
        x1 = cx + int((r - 6) * math.cos(ang))
        y1 = cy + int((r - 6) * math.sin(ang))
        draw.line([(x0, y0), (x1, y1)], fill=mix(CARD, MUTED, a), width=3)
    sweep = (t % 3.6) / 3.6
    hour = math.radians(-90 + 8)
    minute = math.radians(-90 + lerp(240, 358, sweep))
    draw.line([(cx, cy), (cx + int(r * 0.48 * math.cos(hour)), cy + int(r * 0.48 * math.sin(hour)))], fill=mix(CARD, WHITE, a), width=8)
    draw.line([(cx, cy), (cx + int(r * 0.78 * math.cos(minute)), cy + int(r * 0.78 * math.sin(minute)))], fill=mix(CARD, AMBER, a), width=6)
    draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=mix(CARD, YELLOW, a))
    draw.text((cx, cy + r + 36), "半夜", font=font(26), fill=mix(BG, AMBER, a), anchor="mm")


def draw_knot(draw, cx: int, cy: int, a: float, t: float) -> None:
    if a <= 0.04:
        return
    for i, label in enumerate(("议题", "工期", "接口", "预算", "风险")):
        ang = math.radians(-90 + i * 72 + t * 22)
        r = 86
        x = cx + int(r * math.cos(ang))
        y = cy + int(r * math.sin(ang))
        draw.line([(cx, cy), (x, y)], fill=mix(CARD, RED, a), width=6)
        draw.ellipse((x - 28, y - 28, x + 28, y + 28), fill=mix(CARD, (48, 24, 24), a))
        draw.text((x, y), label, font=font(20), fill=mix(CARD, WHITE, a), anchor="mm")
    draw.ellipse((cx - 36, cy - 36, cx + 36, cy + 36), fill=mix(CARD, RED, a))
    draw.text((cx, cy), "捆", font=font(28), fill=mix(RED, INK, a), anchor="mm")


def render_b_take_decision(duration: float) -> list:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "01 带走决定")
        a0 = appear(t, 0.02)
        d.text((W // 2, 220 + bob(t)), "对齐不是把人留下", font=font(50), fill=mix(BG, WHITE, a0), anchor="mm")
        bad = appear(t, duration * 0.12)
        if bad > 0.04:
            y = 430 + int(lerp(18, 0, bad)) + bob(t, 4, 1.3)
            rounded(d, (90, y, 990, y + 200), 28, mix(BG, CARD, bad))
            d.text((W // 2, y + 60), "错", font=font(28), fill=mix(CARD, RED, bad), anchor="mm")
            d.text((W // 2, y + 130), "把人留下过夜", font=font(44), fill=mix(CARD, WHITE, bad), anchor="mm")
            strike_line(d, (180, y + 150, 900, y + 170), appear(t, duration * 0.28, 0.35), mix(CARD, RED, bad))
        good = appear(t, duration * 0.42)
        if good > 0.04:
            y = 700 + int(lerp(18, 0, good)) + bob(t + 0.4, 4, 1.1)
            rounded(d, (90, y, 990, y + 200), 28, mix(BG, (22, 40, 36), good))
            d.text((W // 2, y + 60), "对", font=font(28), fill=mix(CARD, MINT, good), anchor="mm")
            d.text((W // 2, y + 130), "把决定带走", font=font(44), fill=mix(CARD, YELLOW, good), anchor="mm")
            check_badge(d, 900, y + 100, appear(t, duration * 0.55, 0.2))
        punch = appear(t, duration * 0.72, 0.24)
        if punch > 0.04:
            y = 1000 + int(lerp(16, 0, punch))
            rounded(d, (140, y, 940, y + 160), 26, mix(BG, (42, 28, 14), punch))
            d.text((W // 2, y + 80), "对齐是带走决定", font=font(48), fill=mix(BG, AMBER, punch), anchor="mm")
        out.append(img)
    return out


def render_b_one_line(duration: float) -> list:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "02 一句议题")
        a0 = appear(t, 0.02)
        d.text((W // 2, 210 + bob(t, 3)), "先写必须对齐的那一句", font=font(46), fill=mix(BG, WHITE, a0), anchor="mm")
        draw_clock(d, 270, 460, 1.0, appear(t, 0.06, 0.24), t)
        draw_knot(d, 800, 460, appear(t, 0.14, 0.24), t)
        a1 = appear(t, duration * 0.22)
        if a1 > 0.04:
            y = 680 + int(lerp(20, 0, a1))
            rounded(d, (80, y, 1000, y + 190), 28, mix(BG, CARD, a1))
            d.text((W // 2, y + 52), "不要捆", font=font(28), fill=mix(CARD, RED, a1), anchor="mm")
            d.text((W // 2, y + 118), "十个问题一起聊", font=font(40), fill=mix(CARD, WHITE, a1), anchor="mm")
            strike_line(d, (220, y + 140, 860, y + 158), appear(t, duration * 0.34, 0.28), mix(CARD, RED, a1))
        a2 = appear(t, duration * 0.42)
        if a2 > 0.04:
            y = 900 + int(lerp(20, 0, a2))
            rounded(d, (80, y, 1000, y + 200), 28, mix(BG, (22, 40, 36), a2))
            d.text((W // 2, y + 58), "只要这句", font=font(28), fill=mix(CARD, MINT, a2), anchor="mm")
            d.text((W // 2, y + 130), "一个议题 · 一次一句", font=font(40), fill=mix(CARD, YELLOW, a2), anchor="mm")
        punch = appear(t, duration * 0.68, 0.22)
        if punch > 0.04:
            y = 1160 + int(lerp(16, 0, punch))
            rounded(d, (140, y, 940, y + 150), 26, mix(BG, (42, 28, 14), punch))
            d.text((W // 2, y + 75), "写不清，先别开", font=font(48), fill=mix(BG, AMBER, punch), anchor="mm")
        out.append(img)
    return out


def render_b_one_dissent(duration: float) -> list:
    n = max(1, round(duration * FPS))
    bubbles = [
        (0.08, 160, 340, "方案 A", RED),
        (0.16, 560, 300, "方案 B", YELLOW),
        (0.24, 360, 500, "方案 C", MUTED),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "03 一个分歧")
        a0 = appear(t, 0.02)
        d.text((W // 2, 210 + bob(t, 3)), "每人只带一个分歧", font=font(48), fill=mix(BG, WHITE, a0), anchor="mm")
        pile = appear(t, duration * 0.28, 0.35)
        for ts, x, y, label, color in bubbles:
            a = appear(t, ts, 0.20)
            if a < 0.04:
                continue
            yy = y + int(lerp(18, 0, a)) + int(pile * 36) + bob(t + ts, 3, 2.0)
            rounded(d, (x, yy, x + 360, yy + 120), 24, mix(BG, CARD, a))
            d.text((x + 180, yy + 60), label, font=font(40), fill=mix(CARD, color, a), anchor="mm")
            if pile > 0.2:
                strike_line(d, (x + 20, yy + 20, x + 340, yy + 100), pile, mix(CARD, RED, a))
        warn = appear(t, duration * 0.38)
        if warn > 0.04:
            y = 700 + int(lerp(16, 0, warn))
            rounded(d, (80, y, 1000, y + 180), 28, mix(BG, CARD, warn))
            d.text((W // 2, y + 56), "分歧堆一起", font=font(28), fill=mix(CARD, MUTED, warn), anchor="mm")
            d.text((W // 2, y + 118), "聊天可以过夜", font=font(40), fill=mix(CARD, RED, warn), anchor="mm")
        good = appear(t, duration * 0.58)
        if good > 0.04:
            y = 920 + int(lerp(16, 0, good))
            rounded(d, (80, y, 1000, y + 180), 28, mix(BG, (22, 40, 36), good))
            d.text((240, y + 90), "决定不能过夜", font=font(40), fill=mix(CARD, MINT, good), anchor="lm")
            check_badge(d, 860, y + 90, appear(t, duration * 0.68, 0.18))
        punch = appear(t, duration * 0.78, 0.22)
        if punch > 0.04:
            y = 1160 + int(lerp(16, 0, punch))
            rounded(d, (120, y, 960, y + 150), 26, mix(BG, (42, 28, 14), punch))
            d.text((W // 2, y + 75), "一个分歧，才拍得了板", font=font(42), fill=mix(BG, AMBER, punch), anchor="mm")
        out.append(img)
    return out


def render_b_seven_days(duration: float) -> list:
    n = max(1, round(duration * FPS))
    rows = [
        (0.12, "记", "有共识", "当场记下", MINT),
        (0.28, "定", "没共识", "负责人先定", YELLOW),
        (0.44, "七", "先定七天", "也能再改", AMBER),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "04 到点拍板")
        a0 = appear(t, 0.02)
        d.text((W // 2, 210 + bob(t, 3)), "到点必须带走决定", font=font(48), fill=mix(BG, WHITE, a0), anchor="mm")
        tick = appear(t, 0.08, 0.22)
        if tick > 0.04:
            rounded(d, (360, 290 + bob(t, 3), 720, 410 + bob(t, 3)), 22, mix(BG, CARD, tick))
            d.text((W // 2, 350 + bob(t, 3)), "到点", font=font(48), fill=mix(CARD, AMBER, tick), anchor="mm")
        for idx, (frac, num, head, body, color) in enumerate(rows):
            a = appear(t, duration * frac, 0.22)
            if a < 0.04:
                continue
            y = 460 + idx * 176 + int(lerp(18, 0, a)) + bob(t + idx, 3, 1.4)
            rounded(d, (90, y, 990, y + 156), 26, mix(BG, CARD, a))
            d.rounded_rectangle((120, y + 36, 220, y + 120), 16, fill=mix(CARD, color, a))
            d.text((170, y + 78), num, font=font(30), fill=mix(color, INK, a), anchor="mm")
            d.text((250, y + 48), head, font=font(40), fill=mix(CARD, color, a), anchor="lm")
            d.text((250, y + 110), body, font=font(28), fill=mix(CARD, WHITE, a), anchor="lm")
        punch = appear(t, duration * 0.72, 0.22)
        if punch > 0.04:
            y = 1040 + int(lerp(16, 0, punch))
            rounded(d, (140, y, 940, y + 160), 26, mix(BG, (42, 28, 14), punch))
            d.text((W // 2, y + 80), "先定不是永远定", font=font(48), fill=mix(BG, AMBER, punch), anchor="mm")
        out.append(img)
    return out


def render_b_must_leave(duration: float) -> list:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "05 散会带走")
        a0 = appear(t, 0.02)
        d.text((W // 2, 230 + bob(t, 3)), "散会必须带走决定", font=font(48), fill=mix(BG, WHITE, a0), anchor="mm")
        good = appear(t, duration * 0.16)
        if good > 0.04:
            y = 420 + int(lerp(16, 0, good)) + bob(t, 4)
            rounded(d, (90, y, 990, y + 200), 28, mix(BG, (22, 40, 36), good))
            d.text((W // 2, y + 70), "带走一个决定", font=font(42), fill=mix(CARD, MINT, good), anchor="mm")
            d.text((W // 2, y + 140), "人才能回家", font=font(30), fill=mix(CARD, WHITE, good), anchor="mm")
            check_badge(d, 900, y + 100, appear(t, duration * 0.30, 0.2))
        bad = appear(t, duration * 0.42)
        if bad > 0.04:
            y = 700 + int(lerp(16, 0, bad))
            rounded(d, (90, y, 990, y + 200), 28, mix(BG, CARD, bad))
            d.text((W // 2, y + 70), "不定", font=font(32), fill=mix(CARD, RED, bad), anchor="mm")
            d.text((W // 2, y + 140), "再对齐到半夜", font=font(42), fill=mix(CARD, WHITE, bad), anchor="mm")
            strike_line(d, (180, y + 150, 900, y + 170), appear(t, duration * 0.55, 0.3), mix(CARD, RED, bad))
        punch = appear(t, duration * 0.72, 0.22)
        if punch > 0.04:
            y = 1000 + int(lerp(16, 0, punch))
            rounded(d, (140, y, 940, y + 160), 26, mix(BG, (42, 28, 14), punch))
            d.text((W // 2, y + 80), "不定就散不了", font=font(50), fill=mix(BG, AMBER, punch), anchor="mm")
        out.append(img)
    return out


def make_cover() -> Path:
    data = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
    cover = data["cover"]
    from PIL import Image
    char = Image.open(ROOT / cover["src"]).convert("RGB")
    scale = max(W / char.width, H / char.height)
    nw, nh = int(char.width * scale), int(char.height * scale)
    char = char.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - W) // 2
    y = int((nh - H) * 0.62)
    canvas = char.crop((x, y, x + W, y + H))
    overlay = Image.new("RGBA", (W, H), (8, 10, 22, 56))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((70, 80, 1010, 470), radius=36, fill=(22, 24, 28))
    d.text((W // 2, 160), "对齐为什么", font=font(48), fill=WHITE, anchor="mm")
    d.text((W // 2, 250), "对齐到半夜", font=font(64), fill=AMBER, anchor="mm")
    d.text((W // 2, 340), cover["sub"], font=font(32), fill=MINT, anchor="mm")
    d.text((W // 2, 410), cover["line"], font=font(30), fill=MUTED, anchor="mm")
    dest = ROOT / f"00_封面_{NAME}.jpg"
    canvas.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    canvas.save(ROOT / "final" / "cover.jpg", quality=92)
    return dest


def main() -> None:
    L.copy_assets(ROOT, [
        "V-挥手.mp4", "V-摊手.mp4", "V-指向.mp4", "V-点赞.mp4",
        "V-正对讲.mp4", "A-角色-小灯-摊手.jpg",
    ])
    duration, cues = L.ensure_vo_window(ROOT)
    print("VO", duration)
    for row in cues:
        print(f"  {row[0]:6.3f}-{row[1]:6.3f}  {row[2]}")
    L.make_bgm(ROOT, duration, (147, 185, 220))
    data = L.build_timeline(ROOT, cues, duration)
    print("timeline", [(s["id"], s["start"], s["end"], s["kind"]) for s in data["shots"]])

    mapping = {
        "take_decision": ("B-带走决定.mp4", render_b_take_decision),
        "one_line": ("B-一句议题.mp4", render_b_one_line),
        "one_dissent": ("B-一个分歧.mp4", render_b_one_dissent),
        "seven_days": ("B-先定七天.mp4", render_b_seven_days),
        "must_leave": ("B-带走决定2.mp4", render_b_must_leave),
    }
    for shot in data["shots"]:
        key = shot.get("broll")
        if not key:
            continue
        fname, renderer = mapping[key]
        d = max(2.4, float(shot["end"]) - float(shot["start"]))
        print("render", fname, d)
        frames_to_mp4(renderer(d + 0.12), ROOT / "broll" / fname)

    make_cover()
    staged = L.assemble(ROOT, data, NAME, STAGED_NAME, accent=AMBER)
    dur = L.probe_dur(staged)
    note = """# 40 · 对齐为什么对齐到半夜（加长）

普通短视频 / 知识口播。草稿 `{draft}`。覆盖短切。

- **成片**：`成片/{staged}`
- **云端 only**：不写盘符，不传 Drive，无 freeze-pad

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {duration:.2f} 秒。镜头 {nshots} 条。
"""
    L.write_docs(ROOT, dur, staged, data, {
        "project_name": "40_对齐为什么对齐到半夜_long",
        "episode": 40,
        "title": NAME,
        "source_note": "40-long 加长重切 / 工厂 40_对齐为什么对齐到半夜",
        "unused_of": "45会议结束 / 01口头答应 / 08工单时限",
        "staged_name": STAGED_NAME,
        "note_md": note,
    })
    L.patch_index(STAGED_NAME, dur)
    L.patch_delivery_row("40", STAGED_NAME, dur)
    report = L.qa(ROOT, staged, data, "40_对齐为什么对齐到半夜_long")
    print("STAGED", staged, "dur", dur, "ok", report["ok"], "target", report["in_target_window"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
