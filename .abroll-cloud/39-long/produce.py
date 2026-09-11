#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 39 加长重切：推不出来的酷画面删掉。草稿 .abroll-cloud/39-long/。禁止冻帧垫时长。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _long_kit as kit

ROOT = Path(__file__).resolve().parent


def frame_structure(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "结构锁死")
    dy = kit.breathe(t, 3)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0)) + dy),
        "每期结构先锁死",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    rows = [
        (0.16, "改", "改一条定律", "只动这一条", kit.AMBER),
        (0.52, "推", "推出三个后果", "能从定律推出来", kit.YELLOW),
        (0.90, "报", "最后一个当回报", "尺度放大留给它", kit.MINT),
    ]
    for idx, (ts, num, head, body, color) in enumerate(rows):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 320 + idx * 210 + int(kit.lerp(18, 0, a)) + kit.breathe(t + idx, 3)
        kit.rounded(d, (90, y, 990, y + 186), 28, kit.mix(kit.BG, kit.CARD, a))
        kit.rounded(d, (120, y + 36, 236, y + 150), 18, kit.mix(kit.CARD, color, a))
        d.text((178, y + 93), num, font=kit.font(40), fill=kit.mix(color, kit.INK, a), anchor="mm")
        d.text((268, y + 62), head, font=kit.font(40), fill=kit.mix(kit.CARD, color, a), anchor="lm")
        d.text((268, y + 124), body, font=kit.font(28), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        if idx < 2:
            ay = y + 186
            fade = kit.appear(t, ts + 0.28, 0.18)
            if fade > 0.04:
                d.line([(kit.W // 2, ay + 4), (kit.W // 2, ay + 20)], fill=kit.mix(kit.CARD, kit.MUTED, fade), width=6)
    punch = kit.appear(t, 1.85, 0.24)
    if punch > 0.04:
        y3 = 1000 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 85), "结构先锁，再谈酷", font=kit.font(48), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_cut_five(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "五砍三")
    dy = kit.breathe(t, 3)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "想到五个砍到三个",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    hub = kit.appear(t, 0.10, 0.20)
    if hub > 0.04:
        kit.rounded(d, (300, 270 + dy, 780, 360 + dy), 22, kit.mix(kit.BG, (42, 30, 14), hub))
        d.text((kit.W // 2, 315 + dy), "改的那条定律", font=kit.font(34), fill=kit.mix(kit.BG, kit.AMBER, hub), anchor="mm")
    cards = [
        (0.22, "1", "后果甲", "反直觉，好拍", kit.MINT, False),
        (0.40, "2", "后果乙", "能连上定律", kit.YELLOW, False),
        (0.58, "3", "炫光效", "好看但推不出", kit.RED, True),
        (0.76, "4", "后果丙", "留给回报镜", kit.CREAM, False),
        (0.94, "5", "酷空镜", "连不上就划掉", kit.RED, True),
    ]
    for idx, (ts, num, head, body, color, kill) in enumerate(cards):
        a = kit.appear(t, ts, 0.20)
        if a < 0.04:
            continue
        y = 390 + idx * 132 + int(kit.lerp(14, 0, a))
        kit.rounded(d, (90, y, 990, y + 118), 22, kit.mix(kit.BG, kit.CARD, a))
        kit.rounded(d, (118, y + 22, 208, y + 96), 14, kit.mix(kit.CARD, color, a))
        d.text((163, y + 59), num, font=kit.font(32), fill=kit.mix(color, kit.INK, a), anchor="mm")
        d.text((236, y + 34), head, font=kit.font(34), fill=kit.mix(kit.CARD, color, a), anchor="lm")
        d.text((236, y + 82), body, font=kit.font(24), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        if not kill:
            line_a = kit.appear(t, 1.20, 0.22)
            if line_a > 0.04:
                d.line([(kit.W // 2, 360 + dy), (163, y + 8)], fill=kit.mix(kit.CARD, kit.AMBER, line_a * 0.7), width=3)
        if kill:
            kit.strike_box(d, (236, y + 20, 940, y + 98), kit.appear(t, 1.45, 0.28), kit.mix(kit.CARD, kit.RED, a))
            kit.x_mark(d, 900, y + 59, kit.appear(t, 1.55, 0.20), 22)
    punch = kit.appear(t, 2.05, 0.24)
    if punch > 0.04:
        y3 = 1080 + int(kit.lerp(14, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 150), 26, kit.mix(kit.BG, (42, 28, 18), punch))
        d.text((kit.W // 2, y3 + 75), "推不出来的先划掉", font=kit.font(46), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_unlink(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "连不上就删")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "连不上，观众当假",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    hub = kit.appear(t, 0.10, 0.20)
    hx, hy = kit.W // 2, 400 + dy
    if hub > 0.04:
        d.ellipse((hx - 110, hy - 110, hx + 110, hy + 110), fill=kit.mix(kit.BG, (42, 30, 14), hub))
        d.text((hx, hy - 18), "改的", font=kit.font(34), fill=kit.mix(kit.BG, kit.AMBER, hub), anchor="mm")
        d.text((hx, hy + 28), "那条", font=kit.font(34), fill=kit.mix(kit.BG, kit.AMBER, hub), anchor="mm")
    keeps = [
        (0.32, 120, 620, "后果一", "箭头连得上", kit.MINT),
        (0.50, 390, 700, "后果二", "箭头连得上", kit.YELLOW),
        (0.68, 660, 620, "后果三", "只放大这一张", kit.AMBER),
    ]
    for ts, x, y, head, body, color in keeps:
        a = kit.appear(t, ts, 0.20)
        if a < 0.04:
            continue
        yy = y + int(kit.lerp(16, 0, a))
        line_a = kit.appear(t, ts + 0.06, 0.16)
        if line_a > 0.04:
            d.line([(hx, hy + 110), (x + 140, yy)], fill=kit.mix(kit.CARD, color, line_a), width=6)
        kit.rounded(d, (x, yy, x + 280, yy + 168), 22, kit.mix(kit.BG, kit.CARD, a))
        d.text((x + 140, yy + 52), head, font=kit.font(32), fill=kit.mix(kit.CARD, color, a), anchor="mm")
        d.text((x + 140, yy + 112), body, font=kit.font(24), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="mm")
        if head == "后果三":
            kit.check_badge(d, x + 236, yy + 36, kit.appear(t, 1.55, 0.18))
    orphan = kit.appear(t, 0.42, 0.20)
    if orphan > 0.04:
        ox, oy = 800, 360 + int(kit.lerp(18, 0, orphan)) + dy
        kit.rounded(d, (ox, oy, ox + 230, oy + 150), 22, kit.mix(kit.BG, (48, 24, 24), orphan))
        d.text((ox + 115, oy + 46), "酷图", font=kit.font(34), fill=kit.mix(kit.CARD, kit.RED, orphan), anchor="mm")
        d.text((ox + 115, oy + 100), "连不上", font=kit.font(26), fill=kit.mix(kit.CARD, kit.WHITE, orphan), anchor="mm")
        kit.x_mark(d, ox + 115, oy + 74, kit.appear(t, 1.25, 0.22), 36)
        kit.strike_box(d, (ox + 16, oy + 20, ox + 214, oy + 130), kit.appear(t, 1.30, 0.24), kit.mix(kit.CARD, kit.RED, orphan))
    punch = kit.appear(t, 2.00, 0.24)
    if punch > 0.04:
        y3 = 980 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 180), 28, kit.mix(kit.BG, (42, 28, 18), punch))
        d.text((kit.W // 2, y3 + 90), "推不出来，就删", font=kit.font(50), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def reuse_voiceover(ep: kit.Episode):
    wav = ep.root / "audio" / "vo-full.wav"
    align = ep.root / "audio" / "vo-align.txt"
    phrases = ep.load_phrases()
    if wav.exists() and align.exists():
        duration = kit.probe_dur(wav)
        aligned = []
        for line in align.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) >= 3:
                aligned.append((float(parts[0]), float(parts[1]), parts[2]))
        if kit.TARGET_LO <= duration <= kit.TARGET_HI and [p for *_, p in aligned] == phrases:
            print("reuse VO", duration, kit.zh_sec(duration))
            ep.write_align_files(aligned, duration)
            return duration, aligned
    return kit.Episode.make_voiceover(ep)


def main() -> None:
    ep = kit.Episode(ROOT, {
        "name": "推不出来的酷画面删掉",
        "full_title": "推不出来的酷画面，一律删掉",
        "staged_name": "39-推不出来的酷画面删掉.mp4",
        "episode": 39,
        "expected_phrases": 18,
        "replaced_short": 15.25,
        "source_note": "topics-batch3.md #39 · 选题库开篇 推演纪律",
        "hooks": "钩子：推不出来的酷画面，一律删掉。\n诊断：不是不够酷，是连不上改的那条定律。\n例子：改一条、推三个、最后一个当回报。\n再一例：五张后果砍到三张，连不上的酷图划掉。\n收束：删掉，比硬留假镜头强。",
        "cover_lines": ("推不出来", "一律删掉"),
        "avoid": "#38 改物理对照；成片 30 雨滴弹回；成片 29 故事没锁；选题 #40 零知识排序",
        "broll": {
            "S02": ("B-结构锁死.mp4", frame_structure),
            "S04": ("B-五砍三.mp4", frame_cut_five),
            "S06": ("B-连不上就删.mp4", frame_unlink),
        },
    })
    ep.make_voiceover = lambda: reuse_voiceover(ep)
    ep.produce()


if __name__ == "__main__":
    main()
