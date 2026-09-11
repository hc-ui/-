#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 48 加长重切：远程实习人在工位活在线上。草稿 .abroll-cloud/48-long/。禁止冻帧垫时长。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _long_kit as kit

ROOT = Path(__file__).resolve().parent


def frame_desk(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "人在工位")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 220 + int(kit.lerp(16, 0, a0)) + dy), "人坐着就行", font=kit.font(54), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")

    a1 = kit.appear(t, 0.16)
    y = 320 + int(kit.lerp(20, 0, a1))
    kit.rounded(d, (70, y, 500, y + 520), 32, kit.mix(kit.BG, kit.CARD, a1))
    d.text((285, y + 56), "工位空了", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.rectangle((150, y + 140, 420, y + 360), outline=kit.mix(kit.CARD, kit.RED, a1), width=6)
    d.text((285, y + 250), "空座", font=kit.font(44), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    kit.x_mark(d, 285, y + 430, kit.appear(t, 0.70, 0.22), 32)
    d.text((285, y + 490), "查岗才危险", font=kit.font(28), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (540, y, 1010, y + 520), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((775, y + 56), "人坐着", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    d.ellipse((710, y + 140, 840, y + 270), outline=kit.mix(kit.CARD, kit.MINT, a2), width=8)
    d.arc((680, y + 260, 870, y + 400), 200, 340, fill=kit.mix(kit.CARD, kit.MINT, a2), width=8)
    kit.check_badge(d, 775, y + 430, kit.appear(t, 0.88, 0.22))
    d.text((775, y + 490), "杂活按时应", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")

    punch = kit.appear(t, 1.55, 0.24)
    if punch > 0.04:
        y3 = 900 + int(kit.lerp(18, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 190), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 95), "人不用搬走", font=kit.font(52), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_dual(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "活在线上")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 220 + int(kit.lerp(16, 0, a0))), "双屏一起跑", font=kit.font(54), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")

    a1 = kit.appear(t, 0.16)
    y = 310 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 480), 32, kit.mix(kit.BG, kit.CARD, a1))
    d.text((285, y + 50), "左 · 实验仿真", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    base = y + 400
    pts = []
    for i in range(8):
        px = 120 + i * 42
        py = base - 40 - int(70 * abs(kit.math.sin(t * 1.2 + i * 0.5)))
        pts.append((px, py))
    if len(pts) > 1:
        d.line(pts, fill=kit.mix(kit.CARD, kit.YELLOW, a1), width=6)
    d.text((285, y + 430), "曲线还在走", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (540, y, 1010, y + 480), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((775, y + 50), "右 · 线上项目", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    rows = ["接口联调", "算法迭代", "周报已交"]
    for i, name in enumerate(rows):
        ry = y + 130 + i * 90
        pop = kit.appear(t, 0.55 + i * 0.12, 0.18)
        kit.rounded(d, (590, ry, 960, ry + 72), 18, kit.mix(kit.CARD, (18, 48, 40), max(a2, pop)))
        d.text((775, ry + 36), name, font=kit.font(32), fill=kit.mix(kit.CARD, kit.MINT, pop), anchor="mm")

    punch = kit.appear(t, 1.48, 0.24)
    if punch > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 180), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 90), "考勤和履历一起拿", font=kit.font(48), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_later(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "本地先灰")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 230 + int(kit.lerp(16, 0, a0))), "合肥本地先别探", font=kit.font(50), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")

    rows = [
        (0.18, "今", "现在", "人在工位 · 活在线上", kit.MINT, False),
        (0.70, "二", "研二下", "初稿锁定再谈", kit.MUTED, True),
        (1.15, "三", "研三", "杂活交接后再探", kit.MUTED, True),
    ]
    for idx, (ts, num, head, body, color, dim) in enumerate(rows):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 340 + idx * 190 + int(kit.lerp(16, 0, a))
        kit.rounded(d, (90, y, 990, y + 168), 28, kit.mix(kit.BG, kit.CARD, a))
        kit.rounded(d, (120, y + 36, 220, y + 132), 16, kit.mix(kit.CARD, color, a))
        d.text((170, y + 84), num, font=kit.font(32), fill=kit.mix(color, kit.INK, a), anchor="mm")
        d.text((250, y + 50), head, font=kit.font(40), fill=kit.mix(kit.CARD, color, a), anchor="lm")
        d.text((250, y + 116), body, font=kit.font(28), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        if dim:
            kit.strike_box(d, (250, y + 36, 940, y + 132), kit.appear(t, ts + 0.35, 0.28), kit.mix(kit.CARD, kit.RED, a))

    punch = kit.appear(t, 2.05, 0.24)
    if punch > 0.04:
        y3 = 980 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 180), 28, kit.mix(kit.BG, (42, 28, 18), punch))
        d.text((kit.W // 2, y3 + 90), "本地实习先灰掉", font=kit.font(50), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def main() -> None:
    ep = kit.Episode(ROOT, {
        "name": "远程实习人在工位活在线上",
        "full_title": "远程实习：人在工位，活在线上",
        "staged_name": "48-远程实习人在工位活在线上.mp4",
        "episode": 48,
        "expected_phrases": 18,
        "replaced_short": 13.10,
        "source_note": "topics-batch3.md #48 · 备忘录第二节 3 远程日常实习",
        "hooks": "钩子：远程实习，人在工位，活在线上。\n诊断：不是把人挪出合肥。\n例子：双屏一边仿真一边线上项目。\n再一例：合肥本地实习先灰掉。\n收束：人坐着，活在线上。",
        "cover_lines": ("远程实习", "人在工位"),
        "avoid": "#47 脱产离校；成片 16 工位切片；成片 28 报销；#46 六十分；成片 37 撞课",
        "broll": {
            "S02": ("B-人在工位.mp4", frame_desk),
            "S04": ("B-双屏线上.mp4", frame_dual),
            "S06": ("B-本地先灰.mp4", frame_later),
        },
    })
    ep.produce()


if __name__ == "__main__":
    main()
