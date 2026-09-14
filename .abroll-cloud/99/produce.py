#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 99：事故复盘只写人锅。工厂 95 短切改认。云端 NEW。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "事故复盘只写人锅"
STAGED_NAME = "99-事故复盘只写人锅.mp4"
BANNED = (
    "找茬会", "日志", "环境变量", "目录名", "流水账", "临时方案",
    "下一期", "文件名", "C++", "ROS", "学完立刻", "三道短题",
)


def frame_name_wall(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 只写人锅")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 210 + int(kit.lerp(16, 0, a0)) + dy), "会开完了，锅也分完了", font=kit.font(46), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")
    cards = [(0.16, 80, 320, "甲", "点过名"), (0.32, 405, 350, "乙", "也圈了"), (0.48, 730, 320, "丙", "锅分完")]
    for ts, x, y0, head, body in cards:
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = y0 + int(kit.lerp(18, 0, a)) + dy
        kit.rounded(d, (x, y, x + 270, y + 280), 26, kit.mix(kit.BG, kit.CARD, a))
        d.ellipse((x + 86, y + 36, x + 184, y + 134), fill=kit.mix(kit.CARD, (58, 32, 30), a))
        d.text((x + 135, y + 85), head, font=kit.font(40), fill=kit.mix(kit.CARD, kit.YELLOW, a), anchor="mm")
        d.text((x + 135, y + 180), body, font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="mm")
        kit.x_mark(d, x + 135, y + 230, kit.appear(t, ts + 0.40, 0.18), 22)
    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y, 990, y + 200), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 70), "名字圈出来", font=kit.font(46), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
        d.text((kit.W // 2, y + 140), "像事情已经结束了", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, punch), anchor="mm")
    return img


def frame_system_allows(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 只写到人")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 210 + int(kit.lerp(16, 0, a0))), "不是没人负责", font=kit.font(48), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")
    a1 = kit.appear(t, 0.16)
    if a1 > 0.04:
        y = 300 + int(kit.lerp(14, 0, a1)) + dy
        kit.rounded(d, (70, y, 500, y + 460), 32, kit.mix(kit.BG, (42, 24, 22), a1))
        d.text((285, y + 70), "点名到人", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
        d.text((285, y + 190), "听着负责", font=kit.font(48), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
        d.text((285, y + 280), "坑还在原处", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.x_mark(d, 285, y + 370, kit.appear(t, 0.70, 0.20), 30)
    a2 = kit.appear(t, 0.30)
    if a2 > 0.04:
        y = 300 + int(kit.lerp(14, 0, a2)) + dy
        kit.rounded(d, (580, y, 1010, y + 460), 32, kit.mix(kit.BG, kit.CARD, a2))
        d.text((795, y + 70), "系统允许点错", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
        d.text((795, y + 190), "却没人改门", font=kit.font(48), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")
        d.text((795, y + 280), "责任只写到人", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
        kit.x_mark(d, 795, y + 370, kit.appear(t, 0.88, 0.20), 30)
    punch = kit.appear(t, 1.18, 0.22)
    if punch > 0.04:
        y = 830 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 180), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 90), "点名痛快，门还开着", font=kit.font(44), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_three_gates(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 先问机制")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 210 + int(kit.lerp(16, 0, a0))), "复盘先问机制", font=kit.font(50), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")
    rows = [(0.16, "1", "哪道门", "当时没有拦住"), (0.40, "2", "哪条信息", "当时根本看不见"), (0.64, "3", "哪条规则", "还在诱人走捷径")]
    for idx, (ts, num, head, body) in enumerate(rows):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 300 + idx * 168 + int(kit.lerp(16, 0, a))
        kit.rounded(d, (90, y, 990, y + 148), 26, kit.mix(kit.BG, kit.CARD, a))
        d.ellipse((128, y + 34, 220, y + 126), fill=kit.mix(kit.CARD, kit.MINT, a))
        d.text((174, y + 80), num, font=kit.font(36), fill=kit.mix(kit.MINT, kit.INK, a), anchor="mm")
        d.text((248, y + 50), head, font=kit.font(40), fill=kit.mix(kit.CARD, kit.MINT, a), anchor="lm")
        d.text((248, y + 108), body, font=kit.font(28), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        kit.check_badge(d, 900, y + 74, kit.appear(t, ts + 0.28, 0.18))
    punch = kit.appear(t, 1.28, 0.22)
    if punch > 0.04:
        y = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y, 990, y + 200), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 70), "门补上，信息补上", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
        d.text((kit.W // 2, y + 140), "捷径先拆掉", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, punch), anchor="mm")
    return img


def frame_compare(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对照 · 面子 / 机制")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 210 + int(kit.lerp(16, 0, a0))), "对人负责，其实是改机制", font=kit.font(42), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")
    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 500), 32, kit.mix(kit.BG, (42, 24, 22), a1))
    d.text((285, y + 56), "改面子", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "写下名字", font=kit.font(52), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    d.text((285, y + 270), "不等于结束", font=kit.font(36), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    kit.x_mark(d, 285, y + 380, kit.appear(t, 0.55, 0.22), 36)
    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (580, y, 1010, y + 500), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((795, y + 56), "改机制", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((795, y + 180), "把门补上", font=kit.font(52), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    d.text((795, y + 270), "坑才离开", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    kit.check_badge(d, 795, y + 380, kit.appear(t, 0.70, 0.22))
    stamp = kit.appear(t, 1.20, 0.24)
    if stamp > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, stamp)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), stamp))
        d.text((kit.W // 2, y3 + 70), "不是改一圈面子", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, stamp), anchor="mm")
        d.text((kit.W // 2, y3 + 140), "对照只打这一点", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, stamp), anchor="mm")
    return img


def frame_stamp(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "收 · 坑还在")
    dy = kit.breathe(t, 6)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 230 + int(kit.lerp(16, 0, a0))), "写下名字，不等于复盘结束", font=kit.font(42), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")
    a1 = kit.appear(t, 0.18)
    if a1 > 0.04:
        cx, cy = 540, 620 + dy
        r = 230
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=kit.mix(kit.BG, (18, 42, 36), a1))
        d.text((cx, cy - 40), "坑还在原处", font=kit.font(52), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
        d.text((cx, cy + 50), "请当成还没复完", font=kit.font(34), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.check_badge(d, cx, cy + 140, kit.appear(t, 0.70, 0.22))
    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y = 960 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 85), "没改机制，复盘不算完", font=kit.font(40), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status.update({
            "project_name": "99_事故复盘只写人锅",
            "cut": "new-40s",
            "draft": ".abroll-cloud/99",
            "duration": round(duration, 3),
            "duration_zh": kit.zh_sec(duration),
        })
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    (ROOT / "项目说明.md").write_text(
        f"""# 99 · 事故复盘只写人锅

普通短视频 / 知识口播。NEW，不是重做。

- **成片中转**：`成片/{STAGED_NAME}`
- **草稿根**：`/workspace/.abroll-cloud/99/`
- **时长**：约 {kit.zh_sec(duration)}

## 口播

{vo}
""",
        encoding="utf-8",
    )
    (ROOT / "时长.md").write_text(
        f"""# 成片 99 时长（中文秒）

| 号 | 成片 | 新时长 | 草稿 |
|----|------|--------|------|
| 99 | `{STAGED_NAME}` | {kit.zh_sec(duration)} | `.abroll-cloud/99/` |
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    row = f"| 99 | 工厂知识口播改认 | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if "| 99 |" in text:
        lines = [row if raw.startswith("| 99 |") else raw for raw in text.splitlines()]
        text = "\n".join(lines)
    verified = f"- **状态**：已核验 · `.abroll-cloud/99/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
    text = text.replace("- **状态**：已认领 · `.abroll-cloud/99/` · NEW · 目标四十到五十秒", verified)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": NAME,
        "staged_name": STAGED_NAME,
        "episode": 99,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "工厂 95_事故复盘只写人锅 · 云端 NEW · 改认 99",
        "hooks": "钩子：事故复盘只写人锅。\n收束：坑还在原处，请当成还没复完。",
        "cover_lines": ("事故复盘", "只写人锅"),
        "avoid": "68 / 91 / 95 / 兄弟 96-98/100",
        "factory": "工厂 95_事故复盘只写人锅",
        "broll": {
            "S02": ("B-名字圈完.mp4", frame_name_wall),
            "S04": ("B-系统允许点错.mp4", frame_system_allows),
            "S06": ("B-先问机制.mp4", frame_three_gates),
            "S08": ("B-改机制不是改面子.mp4", frame_compare),
            "S10": ("B-坑还在没复完.mp4", frame_stamp),
        },
    })


def main() -> None:
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8")
    hit = [w for w in BANNED if w in vo]
    if hit:
        raise SystemExit(f"banned phrases in VO: {hit}")
    ep = episode()
    report = ep.produce()
    staged = Path("/workspace/成片") / STAGED_NAME
    dur = kit.probe_dur(staged) if staged.exists() else float(report["video"]["duration_s"])
    rewrite_docs(dur)
    patch_topics(dur)
    print("NEW 99", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
