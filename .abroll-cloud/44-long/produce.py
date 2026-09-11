#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 44 加长重切：忙完一天却没推进。草稿 .abroll-cloud/44-long/。禁止冻帧垫时长。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _long_kit as kit

ROOT = Path(__file__).resolve().parent


def frame_react(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 反应")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0)) + dy),
        "整天都在反应",
        font=kit.font(54),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    rows = [
        (0.16, "回", "回消息", "已读很快", kit.YELLOW),
        (0.42, "救", "救火", "插进来的都急", kit.RED),
        (0.68, "插", "插队", "正事被挤走", kit.MUTED),
    ]
    for idx, (ts, num, head, body, color) in enumerate(rows):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 320 + idx * 178 + int(kit.lerp(18, 0, a))
        kit.rounded(d, (90, y, 990, y + 158), 28, kit.mix(kit.BG, kit.CARD, a))
        kit.rounded(d, (120, y + 36, 214, y + 122), 16, kit.mix(kit.CARD, color, a))
        d.text((167, y + 79), num, font=kit.font(34), fill=kit.mix(color, kit.INK, a), anchor="mm")
        d.text((244, y + 48), head, font=kit.font(42), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        d.text((244, y + 112), body, font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a), anchor="lm")
        kit.strike_box(d, (244, y + 28, 920, y + 130), kit.appear(t, ts + 0.70, 0.28), kit.mix(kit.CARD, kit.RED, a))

    empty = kit.appear(t, 1.55, 0.24)
    if empty > 0.04:
        pulse = 0.82 + 0.18 * kit.math.sin(t * 2.2)
        y = 900 + int(kit.lerp(18, 0, empty)) + dy
        kit.rounded(d, (90, y, 990, y + 210), 28, kit.mix(kit.BG, (42, 28, 18), empty * pulse))
        d.text((kit.W // 2, y + 72), "推进栏", font=kit.font(32), fill=kit.mix(kit.BG, kit.MUTED, empty), anchor="mm")
        d.text((kit.W // 2, y + 140), "空的", font=kit.font(56), fill=kit.mix(kit.BG, kit.YELLOW, empty), anchor="mm")

    punch = kit.appear(t, 2.05, 0.22)
    if punch > 0.04:
        y = 1160 + int(kit.lerp(16, 0, punch))
        kit.rounded(d, (140, y, 940, y + 150), 26, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 75), "没有一件推进", font=kit.font(50), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_trace(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 一件")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0)) + dy),
        "只留一件",
        font=kit.font(54),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    rows = [
        (0.16, "1", "写下这一件", "必须推进，不是回复", kit.YELLOW),
        (0.48, "2", "能留下痕迹", "文档 / 代码 / 决定", kit.MINT),
        (0.80, "3", "一件动了", "比十件反应值钱", kit.CREAM),
    ]
    for idx, (ts, num, head, body, color) in enumerate(rows):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 320 + idx * 188 + int(kit.lerp(18, 0, a))
        kit.rounded(d, (90, y, 990, y + 168), 28, kit.mix(kit.BG, kit.CARD, a))
        d.ellipse((128, y + 40, 220, y + 132), fill=kit.mix(kit.CARD, color, a))
        d.text((174, y + 86), num, font=kit.font(36), fill=kit.mix(color, kit.INK, a), anchor="mm")
        d.text((248, y + 54), head, font=kit.font(40), fill=kit.mix(kit.CARD, color, a), anchor="lm")
        d.text((248, y + 118), body, font=kit.font(28), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        kit.check_badge(d, 900, y + 86, kit.appear(t, ts + 0.55, 0.20))

    punch = kit.appear(t, 1.70, 0.24)
    if punch > 0.04:
        y = 940 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (140, y, 940, y + 180), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 90), "一件动了才算", font=kit.font(52), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_tomorrow(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "先问明天")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "临时插入先问明天",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 320 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 520), 32, kit.mix(kit.BG, (22, 40, 36), a1))
    d.text((285, y + 56), "今天这一件", font=kit.font(34), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
    kit.rounded(d, (120, y + 130, 450, y + 320), 24, kit.mix(kit.CARD, (18, 48, 40), a1))
    d.text((285, y + 190), "留下痕迹", font=kit.font(40), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
    d.text((285, y + 260), "先保，不让路", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
    kit.check_badge(d, 285, y + 410, kit.appear(t, 0.80, 0.22))
    d.text((285, y + 480), "今天只保这一件", font=kit.font(26), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (540, y, 1010, y + 520), 32, kit.mix(kit.BG, kit.CARD, a2))
    d.text((775, y + 56), "插进来的", font=kit.font(34), fill=kit.mix(kit.CARD, kit.YELLOW, a2), anchor="mm")
    inserts = ["临时会", "加急回复", "顺手杂活"]
    for i, name in enumerate(inserts):
        ry = y + 130 + i * 90
        pop = kit.appear(t, 0.55 + i * 0.14, 0.18)
        kit.rounded(d, (590, ry, 960, ry + 72), 18, kit.mix(kit.CARD, (42, 32, 18), max(a2, pop)))
        d.text((720, ry + 36), name, font=kit.font(30), fill=kit.mix(kit.CARD, kit.WHITE, pop), anchor="mm")
        d.text((900, ry + 36), "明天?", font=kit.font(26), fill=kit.mix(kit.CARD, kit.YELLOW, pop), anchor="mm")

    punch = kit.appear(t, 1.85, 0.24)
    if punch > 0.04:
        y3 = 900 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 180), 28, kit.mix(kit.BG, (42, 28, 18), punch))
        d.text((kit.W // 2, y3 + 90), "先问明天再让路", font=kit.font(50), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def main() -> None:
    ep = kit.Episode(ROOT, {
        "name": "忙完一天却没推进",
        "full_title": "忙完一天却没推进",
        "staged_name": "44-忙完一天却没推进.mp4",
        "episode": 44,
        "expected_phrases": 18,
        "replaced_short": 14.46,
        "source_note": "工厂 44_忙完一天却没推进 · 44-long 加长重切（官方 topics-batch3 #44 是菜单拆函数，本集成片号占用）",
        "hooks": "钩子：忙完一天却没推进。\n诊断：不是不够努力，是整天都在反应。\n方法：今天只留一件能留下痕迹的动作。\n再一例：临时插入先问明天。\n收束：动了，今天才算过。",
        "cover_lines": ("忙完一天", "却没推进"),
        "avoid": "成片00打断；成片16切片；成片26待办；#45会议结束；#46六十分；官方#44菜单拆函数",
        "factory": "工厂 44_忙完一天却没推进",
        "broll": {
            "S02": ("B-整天反应.mp4", frame_react),
            "S04": ("B-一件痕迹.mp4", frame_trace),
            "S06": ("B-先问明天.mp4", frame_tomorrow),
        },
    })
    ep.produce()


if __name__ == "__main__":
    main()
