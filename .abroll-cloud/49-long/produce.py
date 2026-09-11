#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 49 加长重切：研一汇报先精读一篇顶刊。草稿 .abroll-cloud/49-long/。禁止冻帧垫时长。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _long_kit as kit

ROOT = Path(__file__).resolve().parent


def draw_slide(d, cx: int, cy: int, page: int, flip: float, a: float) -> None:
    if a <= 0.04:
        return
    w, h = 300, 380
    for i, off in enumerate((40, 22)):
        col = kit.mix(kit.BG, (18, 20, 28), a * (0.55 + i * 0.15))
        kit.rounded(d, (cx - w // 2 + off, cy - h // 2 + off // 3, cx + w // 2 + off, cy + h // 2 + off // 3), 22, col)
    squeeze = 1.0 - 0.62 * abs(kit.math.sin(flip * kit.math.pi))
    sw = max(36, int(w * squeeze))
    x0, y0 = cx - sw // 2, cy - h // 2
    kit.rounded(d, (x0, y0, x0 + sw, y0 + h), 22, kit.mix(kit.BG, kit.CARD, a))
    kit.rounded(d, (x0, y0, x0 + sw, y0 + 64), 22, kit.mix(kit.CARD, kit.YELLOW, a))
    if sw > 120:
        d.text((cx, y0 + 32), f"{page:02d} / 10", font=kit.font(28), fill=kit.mix(kit.YELLOW, kit.INK, a), anchor="mm")
        d.text((cx, y0 + 96), "顶刊图", font=kit.font(26), fill=kit.mix(kit.CARD, kit.MUTED, a), anchor="mm")


def frame_pages(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "精读主菜")
    dy = kit.breathe(t, 3)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 220 + int(kit.lerp(16, 0, a0))), "八到十页", font=kit.font(56), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")
    page = 1 + int((t * 3.6) % 10)
    flip = (t * 3.6) % 1.0
    draw_slide(d, kit.W // 2, 520 + dy, page, flip, kit.appear(t, 0.08, 0.22))
    cards = [
        (0.70, "背", "背景", "这篇在解什么", kit.YELLOW),
        (1.05, "法", "方法", "图表规范写清", kit.MINT),
        (1.40, "结", "结论", "读者能带走的", kit.CREAM),
    ]
    for idx, (ts, num, head, body, color) in enumerate(cards):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 760 + idx * 130 + int(kit.lerp(14, 0, a))
        kit.rounded(d, (90, y, 990, y + 116), 24, kit.mix(kit.BG, kit.CARD, a))
        kit.rounded(d, (120, y + 22, 214, y + 94), 16, kit.mix(kit.CARD, color, a))
        d.text((167, y + 58), num, font=kit.font(32), fill=kit.mix(color, kit.INK, a), anchor="mm")
        d.text((244, y + 36), head, font=kit.font(36), fill=kit.mix(kit.CARD, color, a), anchor="lm")
        d.text((244, y + 84), body, font=kit.font(26), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
    punch = kit.appear(t, 2.00, 0.22)
    if punch > 0.04:
        y = 1180 + int(kit.lerp(14, 0, punch)) + dy
        kit.rounded(d, (160, y, 920, y + 130), 26, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 65), "讲清三件事", font=kit.font(48), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_done(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "已完成")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 230 + int(kit.lerp(16, 0, a0))), "只报做完的动作", font=kit.font(50), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")
    dones = [
        (0.20, "精", "精读了文献", "页码图表都齐"),
        (0.70, "仿", "跑通了仿真", "开源基线能复现"),
        (1.20, "课", "课实验做完", "已经交得出去"),
    ]
    for idx, (ts, num, head, body) in enumerate(dones):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 340 + idx * 200 + int(kit.lerp(16, 0, a))
        kit.rounded(d, (90, y, 990, y + 176), 28, kit.mix(kit.BG, kit.CARD, a))
        d.ellipse((130, y + 40, 230, y + 140), fill=kit.mix(kit.CARD, kit.MINT, a))
        d.text((180, y + 90), num, font=kit.font(36), fill=kit.mix(kit.MINT, kit.INK, a), anchor="mm")
        d.text((270, y + 52), head, font=kit.font(40), fill=kit.mix(kit.CARD, kit.MINT, a), anchor="lm")
        d.text((270, y + 118), body, font=kit.font(28), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        kit.check_badge(d, 900, y + 88, kit.appear(t, ts + 0.28, 0.18))
    punch = kit.appear(t, 2.05, 0.22)
    if punch > 0.04:
        y = 980 + int(kit.lerp(14, 0, punch)) + dy
        kit.rounded(d, (140, y, 940, y + 170), 26, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 85), "已经做完的动作", font=kit.font(48), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_bench(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 承诺")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 230 + int(kit.lerp(16, 0, a0))), "别报没搭完的台", font=kit.font(50), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")

    a1 = kit.appear(t, 0.16)
    y = 330 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (80, y, 1000, y + 280), 32, kit.mix(kit.BG, kit.CARD, a1))
    d.text((kit.W // 2, y + 70), "下周一定搭完温控台", font=kit.font(40), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    d.text((kit.W // 2, y + 150), "超出能力的工程承诺", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    kit.strike_box(d, (160, y + 40, 920, y + 100), kit.appear(t, 0.55, 0.28), kit.mix(kit.CARD, kit.RED, a1))
    kit.x_mark(d, 540, y + 220, kit.appear(t, 0.72, 0.20), 36)

    a2 = kit.appear(t, 0.95)
    y2 = 660 + int(kit.lerp(16, 0, a2))
    kit.rounded(d, (80, y2, 1000, y2 + 250), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((kit.W // 2, y2 + 80), "这篇精读完了", font=kit.font(44), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    d.text((kit.W // 2, y2 + 160), "组会能带走的", font=kit.font(28), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
    kit.check_badge(d, 900, y2 + 80, kit.appear(t, 1.20, 0.18))

    punch = kit.appear(t, 1.90, 0.22)
    if punch > 0.04:
        y3 = 980 + int(kit.lerp(14, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 170), 26, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 85), "这篇精读完了", font=kit.font(50), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def main() -> None:
    ep = kit.Episode(ROOT, {
        "name": "研一汇报先精读一篇顶刊",
        "full_title": "研一汇报先精读一篇顶刊",
        "staged_name": "49-研一汇报先精读一篇顶刊.mp4",
        "episode": 49,
        "expected_phrases": 18,
        "replaced_short": 13.50,
        "source_note": "topics-batch3.md #49 · 备忘录第三节 4 研一周会汇报战术",
        "hooks": "钩子：研一汇报，先精读一篇顶刊。\n诊断：还没进实验，别先报搭台。\n例子：八到十页讲清背景方法结论。\n再一例：别报下周一定搭完温控台。\n收束：文献精读才是主菜。",
        "cover_lines": ("研一汇报", "先精读一篇顶刊"),
        "avoid": "成片 16 只报做完主标题；成片 37 撞课；#46–#48；#50",
        "broll": {
            "S02": ("B-八到十页.mp4", frame_pages),
            "S04": ("B-已完成动作.mp4", frame_done),
            "S06": ("B-别搭台子.mp4", frame_bench),
        },
    })
    ep.produce()


if __name__ == "__main__":
    main()
