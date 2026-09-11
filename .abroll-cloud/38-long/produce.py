#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 38 加长重切：分不清改物理和AI画错。草稿 .abroll-cloud/38-long/。禁止冻帧垫时长。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _long_kit as kit

ROOT = Path(__file__).resolve().parent


def frame_bead(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对照 三种尺度")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "同一滴水",
        font=kit.font(56),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.12)
    y = 280 + int(kit.lerp(18, 0, a1)) + dy
    kit.rounded(d, (70, y, 500, y + 430), 32, kit.mix(kit.BG, kit.CARD, a1))
    d.text((285, y + 48), "A · 正常飞溅", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
    cx, cy = 285, y + 210
    for i in range(5):
        rr = 36 + i * 22 + int(10 * kit.math.sin(t * 2.2 + i))
        col = kit.mix(kit.CARD, kit.MINT, a1 * (1.0 - i * 0.14))
        d.arc((cx - rr, cy - rr // 2, cx + rr, cy + rr), 200, 340, fill=col, width=6)
    d.text((285, y + 380), "观众认得出水", font=kit.font(28), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
    kit.check_badge(d, 430, y + 80, kit.appear(t, 0.55, 0.20))

    a2 = kit.appear(t, 0.22)
    kit.rounded(d, (540, y, 1010, y + 430), 32, kit.mix(kit.BG, (42, 26, 22), a2))
    d.text((775, y + 48), "B · 玻璃珠", font=kit.font(30), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")
    bx, by = 775, y + 210 + int(8 * kit.math.sin(t * 1.6))
    r = 92
    d.ellipse((bx - r, by - r, bx + r, by + r), fill=kit.mix(kit.CARD, (70, 90, 110), a2), outline=kit.mix(kit.CARD, kit.RED, a2), width=8)
    d.ellipse((bx - 28, by - 48, bx + 8, by - 12), fill=kit.mix(kit.CARD, kit.WHITE, a2 * 0.55))
    kit.x_mark(d, 920, y + 80, kit.appear(t, 0.72, 0.20), 28)
    d.text((775, y + 380), "看起来像穿帮", font=kit.font(28), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")

    rows = [
        (0.90, "1", "正常飞溅", "观众认得出水", kit.MINT, False),
        (1.25, "2", "微妙玻璃珠", "看起来像穿帮", kit.RED, True),
        (1.60, "3", "整街水洼鼓起", "大到不可能是错", kit.YELLOW, False),
    ]
    for idx, (ts, num, head, body, color, warn) in enumerate(rows):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        pulse = 1.0 + 0.04 * kit.math.sin(t * 2.4 + idx)
        ry = 760 + idx * 150 + int(kit.lerp(14, 0, a)) + int((pulse - 1) * 8)
        kit.rounded(d, (90, ry, 990, ry + 132), 24, kit.mix(kit.BG, kit.CARD, a))
        kit.rounded(d, (120, ry + 24, 214, ry + 108), 16, kit.mix(kit.CARD, color, a))
        d.text((167, ry + 66), num, font=kit.font(32), fill=kit.mix(color, kit.INK, a), anchor="mm")
        d.text((244, ry + 40), head, font=kit.font(36), fill=kit.mix(kit.CARD, color, a), anchor="lm")
        d.text((244, ry + 94), body, font=kit.font(26), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        if warn:
            kit.strike_box(d, (244, ry + 18, 900, ry + 70), kit.appear(t, ts + 0.28, 0.24), kit.mix(kit.CARD, kit.RED, a))

    punch = kit.appear(t, 2.15, 0.22)
    if punch > 0.04:
        y3 = 1240 + int(kit.lerp(14, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 150), 26, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 75), "三种读法", font=kit.font(50), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_draw(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "抽卡 救不了")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "再抽一张",
        font=kit.font(56),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    split = kit.appear(t, 0.55, 0.55)
    gap = int(kit.lerp(0, 70, split))
    a1 = kit.appear(t, 0.16)
    y = 320 + int(kit.lerp(18, 0, a1)) + dy
    left = (80 - gap // 2, y, 530 - gap // 2, y + 360)
    right = (550 + gap // 2, y, 1000 + gap // 2, y + 360)
    kit.rounded(d, left, 30, kit.mix(kit.BG, kit.CARD, a1))
    d.text(((left[0] + left[2]) // 2, y + 90), "物理被改了", font=kit.font(40), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    d.text(((left[0] + left[2]) // 2, y + 180), "你改的那一条", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    kit.rounded(d, right, 30, kit.mix(kit.BG, (42, 26, 22), a1))
    d.text(((right[0] + right[2]) // 2, y + 90), "模型画错了", font=kit.font(40), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    d.text(((right[0] + right[2]) // 2, y + 180), "观众当穿帮", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    if split < 0.35:
        d.text((kit.W // 2, y + 280), "叠在一起", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")

    a2 = kit.appear(t, 1.10)
    cx, cy, r = kit.W // 2, 920 + dy, 150
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=kit.mix(kit.BG, kit.CARD, a2), outline=kit.mix(kit.CARD, kit.YELLOW, a2), width=10)
    d.text((cx, cy), "抽卡", font=kit.font(52), fill=kit.mix(kit.CARD, kit.YELLOW, a2), anchor="mm")
    boom = kit.appear(t, 1.45, 0.22)
    if boom > 0.04:
        kit.x_mark(d, cx, cy, boom, 88)
        y3 = 1160 + int(kit.lerp(16, 0, boom))
        kit.rounded(d, (140, y3, 940, y3 + 180), 28, kit.mix(kit.BG, (42, 28, 18), boom))
        d.text((kit.W // 2, y3 + 90), "救不了", font=kit.font(52), fill=kit.mix(kit.BG, kit.RED, boom), anchor="mm")
    return img


def frame_rules(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "三条规矩")
    dy = kit.breathe(t, 3)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "只改这一条",
        font=kit.font(56),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    stamp = kit.appear(t, 0.20, 0.28)
    if stamp > 0.04:
        kit.rounded(d, (260, 280, 820, 360), 22, kit.mix(kit.BG, (18, 42, 36), stamp))
        d.text((kit.W // 2, 320), "片头字卡先盖上", font=kit.font(32), fill=kit.mix(kit.BG, kit.MINT, stamp), anchor="mm")

    rows = [
        (0.40, "1", "先正常", "再给反常", kit.YELLOW),
        (0.80, "2", "片头字卡", "只改这一条", kit.MINT),
        (1.20, "3", "尺度放大", "大到不像穿帮", kit.CREAM),
    ]
    for idx, (ts, num, head, body, color) in enumerate(rows):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 400 + idx * 230 + int(kit.lerp(16, 0, a)) + dy
        kit.rounded(d, (90, y, 990, y + 206), 28, kit.mix(kit.BG, kit.CARD, a))
        d.ellipse((128, y + 44, 248, y + 164), fill=kit.mix(kit.CARD, color, a))
        d.text((188, y + 104), num, font=kit.font(42), fill=kit.mix(color, kit.INK, a), anchor="mm")
        d.text((280, y + 70), head, font=kit.font(42), fill=kit.mix(kit.CARD, color, a), anchor="lm")
        d.text((280, y + 142), body, font=kit.font(30), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        kit.check_badge(d, 900, y + 104, kit.appear(t, ts + 0.28, 0.18))

    punch = kit.appear(t, 2.00, 0.22)
    if punch > 0.04:
        y3 = 1160 + int(kit.lerp(14, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 170), 26, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 85), "开头先写清", font=kit.font(50), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def main() -> None:
    ep = kit.Episode(ROOT, {
        "name": "分不清改物理和AI画错",
        "full_title": "分不清改物理和AI画错",
        "staged_name": "38-分不清改物理和AI画错.mp4",
        "episode": 38,
        "expected_phrases": 18,
        "replaced_short": 19.88,
        "source_note": "topics-batch3.md #38 · 选题库.md 001 暂缓 · EP001-生产包.md",
        "hooks": "钩子：观众分不清，你是改了物理，还是AI画错。\n诊断：一颗不融进水的球，看起来就像玻璃珠。抽卡救不了。\n例子：同一滴水三种读法——正常飞溅、微妙玻璃珠、整街水洼鼓起。\n再一例：物理和画错叠在一起，撕不开。\n收束：片头写清只改这一条；尺度放大，教训当题目。",
        "cover_lines": ("改了物理", "还是 AI 画错"),
        "avoid": "成片 30 雨滴弹回主钩；定律 001–012 主钩重拍；#39 推不出来的酷画面；#40 零知识秒懂",
        "broll": {
            "S02": ("B-玻璃珠对照.mp4", frame_bead),
            "S04": ("B-抽卡救不了.mp4", frame_draw),
            "S06": ("B-三条规矩.mp4", frame_rules),
        },
    })
    ep.produce()


if __name__ == "__main__":
    main()
