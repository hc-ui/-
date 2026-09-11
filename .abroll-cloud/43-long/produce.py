#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 43 加长重切：先交三道短题。草稿 .abroll-cloud/43-long/。禁止冻帧垫时长。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _long_kit as kit

ROOT = Path(__file__).resolve().parent


def frame_weld(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 焊在一起")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 230 + int(kit.lerp(16, 0, a0))),
        "卡的不是新语法",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.18)
    y = 330 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 420), 32, kit.mix(kit.BG, (22, 40, 36), a1))
    d.text((285, y + 56), "过", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 150), "语法见过", font=kit.font(44), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
    d.text((285, y + 230), "if / for / 字典", font=kit.font(30), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
    kit.check_badge(d, 285, y + 330, kit.appear(t, 0.70, 0.22))

    a2 = kit.appear(t, 0.30)
    kit.rounded(d, (580, y, 1010, y + 420), 32, kit.mix(kit.BG, kit.CARD, a2))
    d.text((795, y + 56), "崩", font=kit.font(28), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")
    d.text((795, y + 150), "焊在一起", font=kit.font(44), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")
    d.text((795, y + 230), "一开菜单就炸", font=kit.font(30), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
    kit.x_mark(d, 795, y + 330, kit.appear(t, 0.88, 0.22), 28)

    crack = kit.appear(t, 0.46, 0.20)
    if crack > 0.04:
        cx = kit.W // 2
        d.line([(cx, y + 40), (cx - 8, y + 140), (cx + 10, y + 240), (cx, y + 380)], fill=kit.mix(kit.BG, kit.RED, crack), width=8)

    punch = kit.appear(t, 1.55, 0.24)
    if punch > 0.04:
        y3 = 820 + int(kit.lerp(18, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 190), 28, kit.mix(kit.BG, (42, 28, 18), punch))
        d.text((kit.W // 2, y3 + 95), "是拼装，不是新词", font=kit.font(50), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_cards(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 先交短题")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 230 + int(kit.lerp(16, 0, a0))),
        "先交这三道",
        font=kit.font(54),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    rows = [(0.16, "1", "通讯录"), (0.32, "2", "库存"), (0.48, "3", "从值找键")]
    for i, (ts, num, head) in enumerate(rows):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 320 + i * 150 + int(kit.lerp(16, 0, a))
        kit.rounded(d, (90, y, 990, y + 130), 26, kit.mix(kit.BG, kit.CARD, a))
        d.ellipse((128, y + 28, 220, y + 120), fill=kit.mix(kit.CARD, kit.MINT, a))
        d.text((174, y + 74), num, font=kit.font(36), fill=kit.mix(kit.MINT, kit.INK, a), anchor="mm")
        d.text((250, y + 65), head, font=kit.font(42), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        kit.check_badge(d, 900, y + 65, kit.appear(t, ts + 0.28, 0.18))

    bad = kit.appear(t, 1.05, 0.22)
    if bad > 0.04:
        y = 780 + int(kit.lerp(14, 0, bad))
        kit.rounded(d, (90, y, 990, y + 150), 26, kit.mix(kit.BG, (42, 28, 18), bad))
        d.text((kit.W // 2, y + 52), "再做一个教务", font=kit.font(40), fill=kit.mix(kit.CARD, kit.YELLOW, bad), anchor="mm")
        d.text((kit.W // 2, y + 110), "规模太大，先别开", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, bad), anchor="mm")
        kit.strike_box(d, (180, y + 20, 900, y + 90), kit.appear(t, 1.28, 0.28), kit.mix(kit.CARD, kit.RED, bad))

    punch = kit.appear(t, 1.70, 0.22)
    if punch > 0.04:
        y3 = 980 + int(kit.lerp(14, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 85), "别再开教务菜单", font=kit.font(50), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_split(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 先拆")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 228 + int(kit.lerp(16, 0, a0))),
        "大案例先拆开",
        font=kit.font(54),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    steps = [
        (0.16, "1", "菜单能退出", "先活下来"),
        (0.36, "2", "再增和列出", "第二刀"),
        (0.56, "3", "最后才统计", "别一上来就算"),
    ]
    for i, (ts, num, head, body) in enumerate(steps):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 320 + i * 160 + int(kit.lerp(16, 0, a))
        kit.rounded(d, (90, y, 990, y + 140), 26, kit.mix(kit.BG, kit.CARD, a))
        d.ellipse((128, y + 30, 216, y + 118), fill=kit.mix(kit.CARD, kit.MINT, a))
        d.text((172, y + 74), num, font=kit.font(34), fill=kit.mix(kit.MINT, kit.INK, a), anchor="mm")
        d.text((248, y + 48), head, font=kit.font(40), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        d.text((248, y + 104), body, font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a), anchor="lm")
        kit.check_badge(d, 900, y + 70, kit.appear(t, ts + 0.28, 0.18))

    punch = kit.appear(t, 1.55, 0.22)
    if punch > 0.04:
        y3 = 860 + int(kit.lerp(14, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 190), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 95), "短题交完，再开新章", font=kit.font(48), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def main() -> None:
    ep = kit.Episode(ROOT, {
        "name": "先交三道短题",
        "full_title": "先交三道短题，别再开教务菜单",
        "staged_name": "43-先交三道短题.mp4",
        "episode": 43,
        "expected_phrases": 18,
        "replaced_short": 19.7,
        "source_note": "topics-batch3.md #43 · 学习与职业规划基线.md 怎么精进立刻条",
        "hooks": "钩子：先交三道短题，别再开教务菜单。\n诊断：卡点在拼装，不是新语法。\n例子：通讯录 / 库存 / 从值找键。\n再一例：大案例拆成退出、增列出、统计。\n收束：短题交完，再开新章。",
        "cover_lines": ("先交", "三道短题"),
        "avoid": "成片 13 从值找键教学；#42 append；#44 函数；#41 空字典；成片 14 五条路",
        "broll": {
            "S02": ("B-焊在一起.mp4", frame_weld),
            "S04": ("B-三道短题.mp4", frame_cards),
            "S06": ("B-先拆再开章.mp4", frame_split),
        },
    })
    ep.produce()


if __name__ == "__main__":
    main()
