#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 42 加长重切：列表用 append，别用等号盖掉。草稿 .abroll-cloud/42-long/。禁止冻帧垫时长。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _long_kit as kit

ROOT = Path(__file__).resolve().parent


def score_chip(d, box, num, a, fill, ink) -> None:
    if a <= 0.04:
        return
    kit.rounded(d, box, 22, kit.mix(kit.BG, fill, a))
    cx = (box[0] + box[2]) / 2
    cy = (box[1] + box[3]) / 2
    d.text((cx, cy), num, font=kit.font(48), fill=kit.mix(fill, ink, a), anchor="mm")


def frame_append(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 追加")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 220 + int(kit.lerp(16, 0, a0)) + dy), "往里加用 append", font=kit.font(52), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")

    a1 = kit.appear(t, 0.16)
    if a1 > 0.04:
        y = 310 + int(kit.lerp(18, 0, a1))
        kit.rounded(d, (80, y, 1000, y + 150), 28, kit.mix(kit.BG, kit.CARD, a1))
        d.text((kit.W // 2, y + 75), "scores.append(92)", font=kit.font(44), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")

    chips = [("88", 0.36, kit.WHITE), ("91", 0.54, kit.WHITE), ("85", 0.72, kit.WHITE), ("92", 1.12, kit.MINT)]
    y = 520 + dy
    for idx, (num, ts, ink) in enumerate(chips):
        a = kit.appear(t, ts, 0.22)
        x0 = 86 + idx * 234
        fill = (36, 64, 56) if idx < 3 else (42, 56, 28)
        score_chip(d, (x0, y, x0 + 214, y + 176), num, a, fill, ink)
        if a > 0.04:
            label = "还在" if idx < 3 else "新贴"
            d.text((x0 + 107, y + 210), label, font=kit.font(26), fill=kit.mix(kit.BG, kit.MUTED if idx < 3 else kit.YELLOW, a), anchor="mm")

    a2 = kit.appear(t, 1.20)
    if a2 > 0.04:
        d.text((kit.W // 2, 780), "末尾多贴一张", font=kit.font(34), fill=kit.mix(kit.BG, kit.MUTED, a2), anchor="mm")

    punch = kit.appear(t, 1.55, 0.24)
    if punch > 0.04:
        y3 = 900 + int(kit.lerp(18, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 190), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 95), "列表还在，只是更长", font=kit.font(48), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
        kit.check_badge(d, 900, y3 + 95, punch)
    return img


def frame_assign(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 等号")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 220 + int(kit.lerp(16, 0, a0))), "等号盖掉整列", font=kit.font(52), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")

    a1 = kit.appear(t, 0.16)
    if a1 > 0.04:
        y = 310 + int(kit.lerp(18, 0, a1))
        box = (80, y, 1000, y + 150)
        kit.rounded(d, box, 28, kit.mix(kit.BG, kit.CARD, a1))
        d.text((kit.W // 2, y + 75), "scores = 92", font=kit.font(48), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
        kit.strike_box(d, box, kit.appear(t, 0.85, 0.28), kit.mix(kit.CARD, kit.RED, a1))

    wipe = kit.appear(t, 1.05, 0.40)
    chips = ["88", "91", "85"]
    y = 520 + dy
    for idx, num in enumerate(chips):
        a = kit.appear(t, 0.32 + idx * 0.12)
        x0 = 90 + idx * 230
        fade = kit.mix((36, 40, 52), (18, 14, 16), wipe)
        score_chip(d, (x0, y, x0 + 210, y + 176), num, a, fade, kit.mix(kit.WHITE, kit.RED, wipe))
        if wipe > 0.2:
            kit.x_mark(d, x0 + 105, y + 88, wipe, 28)
    if wipe > 0.08:
        kit.rounded(d, (320, 760, 760, 980), 28, kit.mix(kit.BG, (56, 22, 24), wipe))
        d.text((540, 870), "92", font=kit.font(84), fill=kit.mix(kit.BG, kit.YELLOW, wipe), anchor="mm")

    punch = kit.appear(t, 1.70, 0.24)
    if punch > 0.04:
        y3 = 1080 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 180), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y3 + 90), "光秃秃的九十二", font=kit.font(50), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_stack(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对照 · 贴与换")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 220 + int(kit.lerp(16, 0, a0))), "一张张贴，别整叠换", font=kit.font(48), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")

    a1 = kit.appear(t, 0.16)
    y = 310 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 560), 32, kit.mix(kit.BG, (22, 40, 36), a1))
    d.text((285, y + 50), "对 · 贴", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
    slips = ["88", "91", "85", "92"]
    for i, num in enumerate(slips):
        pop = kit.appear(t, 0.40 + i * 0.16, 0.18)
        sy = y + 110 + i * 90 + int(kit.lerp(14, 0, pop))
        kit.rounded(d, (120, sy, 450, sy + 76), 16, kit.mix(kit.CARD, (18, 48, 40), max(a1, pop)))
        d.text((285, sy + 38), f"成绩条 {num}", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MINT, pop), anchor="mm")
    kit.check_badge(d, 285, y + 510, kit.appear(t, 1.10, 0.20))

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (580, y, 1010, y + 560), 32, kit.mix(kit.BG, kit.CARD, a2))
    d.text((795, y + 50), "错 · 换", font=kit.font(32), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")
    stack_a = kit.appear(t, 0.50, 0.22)
    for i, num in enumerate(("88", "91", "85")):
        sy = y + 130 + i * 28
        kit.rounded(d, (640, sy, 950, sy + 110), 14, kit.mix(kit.CARD, (36, 28, 28), stack_a * (1 - i * 0.12)))
        d.text((795, sy + 36), num, font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, stack_a), anchor="mm")
    cover = kit.appear(t, 1.15, 0.30)
    if cover > 0.04:
        kit.rounded(d, (640, y + 200, 950, y + 430), 18, kit.mix(kit.CARD, (56, 22, 24), cover))
        d.text((795, y + 300), "92", font=kit.font(72), fill=kit.mix(kit.CARD, kit.YELLOW, cover), anchor="mm")
        kit.strike_box(d, (660, y + 220, 930, y + 410), cover, kit.mix(kit.CARD, kit.RED, cover))
        kit.x_mark(d, 795, y + 500, cover, 30)

    punch = kit.appear(t, 1.70, 0.24)
    if punch > 0.04:
        y3 = 940 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 180), 28, kit.mix(kit.BG, (42, 28, 18), punch))
        d.text((kit.W // 2, y3 + 90), "赋值会抹掉前面", font=kit.font(50), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def main() -> None:
    ep = kit.Episode(ROOT, {
        "name": "列表用append别用等号",
        "full_title": "列表用 append，别用等号盖掉",
        "staged_name": "42-列表用append别用等号.mp4",
        "episode": 42,
        "expected_phrases": 18,
        "replaced_short": 17.54,
        "source_note": "topics-batch3.md #42 · 学习与职业规划基线.md 不足第4条",
        "hooks": "钩子：列表用 append，别用等号盖掉。\n对照：scores.append(92) 往末尾加；scores = 92 整列变成一个数。\n再一例：成绩条一张张贴，下一张纸把整叠换掉就全没了。\n收束：该加就 append，别用等号换掉整列。",
        "cover_lines": ("列表用 append", "别用等号盖掉"),
        "avoid": "字典靠名字 / 从值找键（成片 13）；空字典写在循环外（#41）；嵌套字典；#43 短题；#44 函数",
        "broll": {
            "S02": ("B-追加.mp4", frame_append),
            "S04": ("B-等号盖掉.mp4", frame_assign),
            "S06": ("B-整叠换掉.mp4", frame_stack),
        },
    })
    ep.produce()


if __name__ == "__main__":
    main()
