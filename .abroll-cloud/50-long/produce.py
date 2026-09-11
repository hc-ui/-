#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 50 加长重切：绑定一个主力博士。草稿 .abroll-cloud/50-long/。禁止冻帧垫时长。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _long_kit as kit

ROOT = Path(__file__).resolve().parent


def draw_person(d, cx: int, cy: int, a: float, accent, label: str, dim: bool = False) -> None:
    if a <= 0.04:
        return
    col = kit.mix(kit.CARD, kit.MUTED if dim else accent, a)
    d.ellipse((cx - 38, cy - 86, cx + 38, cy - 10), outline=col, width=6)
    d.arc((cx - 52, cy - 8, cx + 52, cy + 70), 200, 340, fill=col, width=6)
    d.text((cx, cy + 88), label, font=kit.font(28), fill=col, anchor="mm")


def frame_one(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 一个")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 230 + int(kit.lerp(16, 0, a0))), "认准一位主力", font=kit.font(54), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")

    a1 = kit.appear(t, 0.16)
    y = 320 + int(kit.lerp(20, 0, a1))
    kit.rounded(d, (70, y, 500, y + 520), 32, kit.mix(kit.BG, kit.CARD, a1))
    d.text((285, y + 56), "广撒网", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    for j, name in enumerate(["甲", "乙", "丙", "丁"]):
        cx = 160 + (j % 2) * 150
        cy = y + 170 + (j // 2) * 160
        draw_person(d, cx, cy, a1, kit.MUTED, name, dim=True)
        kit.x_mark(d, cx, cy - 10, kit.appear(t, 0.72 + j * 0.08, 0.18), 22)
    kit.strike_box(d, (110, y + 30, 460, y + 86), kit.appear(t, 0.90, 0.28), kit.mix(kit.CARD, kit.RED, a1))

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (540, y, 1010, y + 520), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((775, y + 56), "主力博士", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    draw_person(d, 775, y + 210, a2, kit.MINT, "稳")
    ring = kit.appear(t, 0.70, 0.28)
    if ring > 0.04:
        d.ellipse((775 - 78, y + 116, 775 + 78, y + 272), outline=kit.mix(kit.CARD, kit.YELLOW, ring), width=8)
    d.text((775, y + 360), "有论文任务", font=kit.font(34), fill=kit.mix(kit.CARD, kit.YELLOW, a2), anchor="mm")
    d.text((775, y + 430), "高年级 · 一条线", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")

    punch = kit.appear(t, 1.55, 0.24)
    if punch > 0.04:
        y3 = 900 + int(kit.lerp(18, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 190), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 95), "只绑一个", font=kit.font(56), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_load(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "你给")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 230 + int(kit.lerp(16, 0, a0))), "减负换过关", font=kit.font(54), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")

    a1 = kit.appear(t, 0.18)
    y = 320 + int(kit.lerp(16, 0, a1))
    kit.rounded(d, (70, y, 500, y + 360), 32, kit.mix(kit.BG, (22, 40, 36), a1))
    d.text((285, y + 70), "自动化搭建", font=kit.font(40), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
    d.text((285, y + 170), "平台里繁琐的活", font=kit.font(30), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
    d.text((285, y + 260), "你去承担", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")

    a2 = kit.appear(t, 0.32)
    kit.rounded(d, (540, y, 1010, y + 360), 32, kit.mix(kit.BG, kit.CARD, a2))
    d.text((775, y + 70), "上位机数据", font=kit.font(40), fill=kit.mix(kit.CARD, kit.YELLOW, a2), anchor="mm")
    d.text((775, y + 170), "处理掉他腾不出的手", font=kit.font(28), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
    d.text((775, y + 260), "工程能力换筹码", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")

    rows = [(1.10, "名", "共同署名"), (1.40, "利", "专利位次")]
    for i, (ts, num, head) in enumerate(rows):
        a = kit.appear(t, ts, 0.20)
        if a < 0.04:
            continue
        x = 90 + i * 460
        yy = 730 + int(kit.lerp(14, 0, a))
        kit.rounded(d, (x, yy, x + 430, yy + 140), 24, kit.mix(kit.BG, kit.CARD, a))
        d.text((x + 215, yy + 70), f"{num}  {head}", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MINT, a), anchor="mm")

    punch = kit.appear(t, 1.90, 0.22)
    if punch > 0.04:
        y3 = 940 + int(kit.lerp(14, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 85), "用工程能力换筹码", font=kit.font(46), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_swap(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "换 · 同盟")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 228 + int(kit.lerp(16, 0, a0))), "结成利益同盟", font=kit.font(54), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")

    a1 = kit.appear(t, 0.16)
    y = 310 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 1010, y + 300), 32, kit.mix(kit.BG, kit.CARD, a1))
    d.text((kit.W // 2, y + 50), "论文署名栏", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    kit.rounded(d, (110, y + 96, 500, y + 188), 18, kit.mix(kit.CARD, (32, 36, 46), a1))
    d.text((305, y + 142), "博士甲", font=kit.font(40), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
    plus = kit.appear(t, 0.62, 0.22)
    if plus > 0.04:
        d.text((540, y + 142), "+", font=kit.font(48), fill=kit.mix(kit.CARD, kit.YELLOW, plus), anchor="mm")
        kit.rounded(d, (590, y + 96, 970, y + 188), 18, kit.mix(kit.CARD, (18, 48, 40), plus))
        d.text((780, y + 142), "你", font=kit.font(40), fill=kit.mix(kit.CARD, kit.MINT, plus), anchor="mm")
    d.text((kit.W // 2, y + 246), "专利位次一并写上", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")

    a2 = kit.appear(t, 0.90)
    y2 = 650 + int(kit.lerp(16, 0, a2))
    kit.rounded(d, (70, y2, 1010, y2 + 240), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((kit.W // 2, y2 + 70), "数据盘", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    cx, cy = kit.W // 2, y2 + 150
    d.ellipse((cx - 54, cy - 54, cx + 54, cy + 54), outline=kit.mix(kit.CARD, kit.YELLOW, a2), width=8)
    stamp = kit.appear(t, 1.20, 0.24)
    if stamp > 0.04:
        d.ellipse((cx + 40, cy - 70, cx + 128, cy + 18), outline=kit.mix(kit.CARD, kit.MINT, stamp), width=7)
        d.text((cx + 84, cy - 26), "可引用", font=kit.font(22), fill=kit.mix(kit.CARD, kit.MINT, stamp), anchor="mm")

    punch = kit.appear(t, 1.85, 0.22)
    if punch > 0.04:
        y3 = 960 + int(kit.lerp(14, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 85), "本条只拍同盟", font=kit.font(50), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def main() -> None:
    ep = kit.Episode(ROOT, {
        "name": "绑定一个主力博士",
        "full_title": "绑定一个主力博士",
        "staged_name": "50-绑定一个主力博士.mp4",
        "episode": 50,
        "expected_phrases": 18,
        "replaced_short": 13.33,
        "source_note": "topics-batch3.md #50 · 备忘录第四节 2 绑定主力博士",
        "hooks": "钩子：绑定一个主力博士，结成利益同盟。\n诊断：不是广撒网。\n例子：自动化和数据处理换署名位次。\n再一例：毕业数据合法引用授权。\n收束：过关靠同盟，不靠广撒网。",
        "cover_lines": ("绑定一个", "主力博士"),
        "avoid": "成片 15 测控生态位；成片 14 / 16 / 28；#46–#49",
        "broll": {
            "S02": ("B-只绑一个.mp4", frame_one),
            "S04": ("B-减负换筹码.mp4", frame_load),
            "S06": ("B-换署名数据.mp4", frame_swap),
        },
    })
    ep.produce()


if __name__ == "__main__":
    main()
