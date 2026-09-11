#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 51 加长重切：Agent是第二技能树不是主线。草稿 .abroll-cloud/51-long/。禁止冻帧垫时长。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _long_kit as kit

ROOT = Path(__file__).resolve().parent


def draw_tree(d, cx: int, top: int, nodes: list[str], a: float, accent, dim: bool = False) -> None:
    trunk = kit.mix(kit.CARD, kit.MUTED if dim else accent, a)
    d.line([(cx, top + 36), (cx, top + 360)], fill=trunk, width=10)
    for i, name in enumerate(nodes):
        y = top + 70 + i * 100
        spread = 118 if i else 0
        if i:
            d.line([(cx, y), (cx + (spread if i % 2 else -spread), y)], fill=trunk, width=6)
        nx = cx if i == 0 else cx + (spread if i % 2 else -spread)
        fill = kit.mix(kit.CARD, (28, 32, 40) if dim else (22, 40, 36), a)
        kit.rounded(d, (nx - 110, y - 36, nx + 110, y + 36), 22, fill)
        col = kit.mix(kit.CARD, kit.MUTED if dim else kit.WHITE, a)
        d.text((nx, y), name, font=kit.font(32), fill=col, anchor="mm")


def frame_trees(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 主树")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 230 + int(kit.lerp(16, 0, a0))), "两棵技能树", font=kit.font(54), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")

    a1 = kit.appear(t, 0.18)
    y = 310 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (56, y, 516, y + 620), 36, kit.mix(kit.BG, kit.CARD, a1))
    d.text((286, y + 56), "主树", font=kit.font(34), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
    draw_tree(d, 286, y + 90, ["控制", "机器人", "智能"], a1, kit.MINT, dim=False)
    now = kit.appear(t, 0.80, 0.22)
    if now > 0.04:
        kit.rounded(d, (156, y + 520, 416, y + 584), 20, kit.mix(kit.CARD, (18, 42, 36), now))
        d.text((286, y + 552), "现在先长这棵", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MINT, now), anchor="mm")

    a2 = kit.appear(t, 0.30)
    kit.rounded(d, (564, y, 1024, y + 620), 36, kit.mix(kit.BG, (20, 22, 28), a2))
    d.text((794, y + 56), "副树", font=kit.font(34), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    draw_tree(d, 794, y + 90, ["Agent", "检索", "协议"], a2, kit.MUTED, dim=True)
    fade = kit.appear(t, 0.95, 0.22)
    if fade > 0.04:
        kit.rounded(d, (644, y + 520, 944, y + 584), 20, kit.mix(kit.CARD, (32, 28, 20), fade))
        d.text((794, y + 552), "第二技能树", font=kit.font(28), fill=kit.mix(kit.CARD, kit.YELLOW, fade), anchor="mm")

    punch = kit.appear(t, 1.50, 0.24)
    if punch > 0.04:
        y3 = 1000 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 170), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y3 + 85), "不是当前主线", font=kit.font(50), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_cards(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 上桌")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 230 + int(kit.lerp(16, 0, a0))), "侧牌先别上桌", font=kit.font(52), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")

    a1 = kit.appear(t, 0.18)
    y = 320 + int(kit.lerp(16, 0, a1))
    cards = ["检索增强", "协议", "技能", "智能体"]
    for j, name in enumerate(cards):
        cx = 150 + j * 210
        cy = y + 120
        pop = kit.appear(t, 0.40 + j * 0.10, 0.20)
        kit.rounded(d, (cx - 88, cy - 70, cx + 88, cy + 70), 20, kit.mix(kit.BG, (28, 26, 22), max(a1, pop)))
        d.text((cx, cy), name, font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, pop), anchor="mm")
        if pop > 0.55:
            kit.x_mark(d, cx, cy + 4, pop, 20)

    a2 = kit.appear(t, 1.05)
    y2 = 560 + int(kit.lerp(16, 0, a2))
    kit.rounded(d, (90, y2, 990, y2 + 220), 28, kit.mix(kit.BG, kit.CARD, a2))
    d.text((kit.W // 2, y2 + 70), "长期可以看", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((kit.W // 2, y2 + 140), "机器人加智能体", font=kit.font(44), fill=kit.mix(kit.CARD, kit.YELLOW, a2), anchor="mm")

    punch = kit.appear(t, 1.70, 0.22)
    if punch > 0.04:
        y3 = 860 + int(kit.lerp(14, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 180), 28, kit.mix(kit.BG, (42, 28, 18), punch))
        d.text((kit.W // 2, y3 + 90), "别同时开过多线", font=kit.font(50), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_interest(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "今 · 基础")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 230 + int(kit.lerp(16, 0, a0))), "现在只指基础语言", font=kit.font(48), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")

    a1 = kit.appear(t, 0.16)
    y = 330 + int(kit.lerp(16, 0, a1))
    kit.rounded(d, (80, y, 1000, y + 320), 36, kit.mix(kit.BG, kit.CARD, a1))
    d.text((kit.W // 2, y + 70), "主桌", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    kit.rounded(d, (220, y + 120, 860, y + 250), 28, kit.mix(kit.CARD, (22, 40, 36), a1))
    d.text((kit.W // 2, y + 185), "基础语言", font=kit.font(56), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")

    a2 = kit.appear(t, 0.70)
    y2 = 700 + int(kit.lerp(14, 0, a2))
    kit.rounded(d, (80, y2, 1000, y2 + 200), 28, kit.mix(kit.BG, kit.CARD, a2))
    d.text((kit.W // 2, y2 + 60), "独立小项目还没出来", font=kit.font(36), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
    d.text((kit.W // 2, y2 + 140), "这些只保持兴趣", font=kit.font(36), fill=kit.mix(kit.CARD, kit.YELLOW, a2), anchor="mm")

    punch = kit.appear(t, 1.55, 0.22)
    if punch > 0.04:
        y3 = 960 + int(kit.lerp(14, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 85), "先别抢戏", font=kit.font(52), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def main() -> None:
    ep = kit.Episode(ROOT, {
        "name": "Agent是第二技能树不是主线",
        "full_title": "Agent是第二技能树，不是主线",
        "staged_name": "51-Agent是第二技能树不是主线.mp4",
        "episode": 51,
        "expected_phrases": 18,
        "replaced_short": 12.25,
        "source_note": "topics-batch3.md #51 · 学习与职业规划基线.md Agent 副线",
        "hooks": "钩子：Agent是第二技能树，不是主线。\n诊断：主树先长控制和机器人。\n例子：侧牌不上主桌。\n再一例：独立小项目出来前只保持兴趣。\n收束：第二技能树可以攒，先别抢戏。",
        "cover_lines": ("Agent是", "第二技能树"),
        "avoid": "成片 14 双线 / 五条路；#43 三道短题；成片 15 测控生态位",
        "broll": {
            "S02": ("B-两棵技能树.mp4", frame_trees),
            "S04": ("B-侧牌不上桌.mp4", frame_cards),
            "S06": ("B-只保持兴趣.mp4", frame_interest),
        },
    })
    ep.produce()


if __name__ == "__main__":
    main()
