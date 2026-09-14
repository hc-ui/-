#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 102：评审只看格式。工厂 102 短切加长。云端 NEW。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "评审只看格式"
STAGED_NAME = "102-评审只看格式.mp4"
BANNED = (
    "找茬", "人锅", "环境变量", "目录名", "流水账", "临时方案",
    "下一期", "文件名", "C++", "ROS", "学完立刻", "三道短题",
    "加机器", "口头同步", "主干",
)


def frame_format_skin(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 只看格式")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 210 + int(kit.lerp(16, 0, a0)) + dy), "空格和命名都改了", font=kit.font(46), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")
    cards = [(0.16, 80, 320, "空格", "对齐了"), (0.32, 405, 350, "命名", "也改了"), (0.48, 730, 320, "逻辑", "没人碰")]
    for ts, x, y0, head, body in cards:
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = y0 + int(kit.lerp(18, 0, a)) + dy
        kit.rounded(d, (x, y, x + 270, y + 280), 26, kit.mix(kit.BG, kit.CARD, a))
        d.text((x + 135, y + 80), head, font=kit.font(40), fill=kit.mix(kit.CARD, kit.YELLOW, a), anchor="mm")
        d.text((x + 135, y + 160), body, font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="mm")
        if head == "逻辑":
            kit.x_mark(d, x + 135, y + 230, kit.appear(t, ts + 0.40, 0.18), 22)
        else:
            kit.check_badge(d, x + 135, y + 230, kit.appear(t, ts + 0.40, 0.18))
    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y, 990, y + 200), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 70), "格式听着认真", font=kit.font(46), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
        d.text((kit.W // 2, y + 140), "逻辑没人碰", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, punch), anchor="mm")
    return img


def frame_tool_vs_prod(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 工具过了")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 210 + int(kit.lerp(16, 0, a0))), "不是没评审，是只审了皮", font=kit.font(42), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")
    a1 = kit.appear(t, 0.16)
    if a1 > 0.04:
        y = 300 + int(kit.lerp(14, 0, a1)) + dy
        kit.rounded(d, (70, y, 500, y + 460), 32, kit.mix(kit.BG, (22, 40, 36), a1))
        d.text((285, y + 70), "格式检查", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
        d.text((285, y + 190), "工具过了", font=kit.font(48), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
        d.text((285, y + 280), "人再过一遍", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.x_mark(d, 285, y + 370, kit.appear(t, 0.70, 0.20), 30)
    a2 = kit.appear(t, 0.30)
    if a2 > 0.04:
        y = 300 + int(kit.lerp(14, 0, a2)) + dy
        kit.rounded(d, (580, y, 1010, y + 460), 32, kit.mix(kit.BG, (42, 24, 22), a2))
        d.text((795, y + 70), "真正风险", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
        d.text((795, y + 190), "还在睡觉", font=kit.font(48), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")
        d.text((795, y + 280), "逻辑没人碰", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
        kit.x_mark(d, 795, y + 370, kit.appear(t, 0.88, 0.20), 30)
    punch = kit.appear(t, 1.18, 0.22)
    if punch > 0.04:
        y = 830 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 180), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 90), "皮过了，等于没过", font=kit.font(44), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_three_q(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 先问三件事")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 210 + int(kit.lerp(16, 0, a0))), "评审先问三件事", font=kit.font(50), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")
    rows = [(0.16, "1", "边界", "有没有人走到"), (0.40, "2", "失败", "会不会拖垮整条链"), (0.64, "3", "回退", "当时能不能立刻停")]
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
        d.text((kit.W // 2, y + 70), "边界、失败、回退", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
        d.text((kit.W // 2, y + 140), "这三件先过完", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, punch), anchor="mm")
    return img


def frame_bot_vs_human(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对照 · 机器人 / 人")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 210 + int(kit.lerp(16, 0, a0))), "格式交给机器人", font=kit.font(48), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")
    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 500), 32, kit.mix(kit.BG, kit.CARD, a1))
    d.text((285, y + 56), "机器人", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "管格式", font=kit.font(52), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
    d.text((285, y + 270), "空格和命名", font=kit.font(36), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
    kit.check_badge(d, 285, y + 380, kit.appear(t, 0.55, 0.22))
    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (580, y, 1010, y + 500), 32, kit.mix(kit.BG, (18, 42, 36), a2))
    d.text((795, y + 56), "人", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((795, y + 180), "审会炸", font=kit.font(52), fill=kit.mix(kit.CARD, kit.YELLOW, a2), anchor="mm")
    d.text((795, y + 270), "逻辑和回退", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    kit.check_badge(d, 795, y + 380, kit.appear(t, 0.70, 0.22))
    stamp = kit.appear(t, 1.20, 0.24)
    if stamp > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, stamp)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), stamp))
        d.text((kit.W // 2, y3 + 70), "人只审会炸的地方", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, stamp), anchor="mm")
        d.text((kit.W // 2, y3 + 140), "对照只打这一点", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, stamp), anchor="mm")
    return img


def frame_not_done(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "收 · 还没过")
    dy = kit.breathe(t, 6)
    a0 = kit.appear(t, 0.02)
    d.text((kit.W // 2, 230 + int(kit.lerp(16, 0, a0))), "改完空格，不等于评审结束", font=kit.font(40), fill=kit.mix(kit.BG, kit.WHITE, a0), anchor="mm")
    a1 = kit.appear(t, 0.18)
    if a1 > 0.04:
        cx, cy = 540, 620 + dy
        r = 230
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=kit.mix(kit.BG, (18, 42, 36), a1))
        d.text((cx, cy - 40), "皮过了", font=kit.font(52), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
        d.text((cx, cy + 50), "不等于能上线", font=kit.font(34), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.x_mark(d, cx, cy + 140, kit.appear(t, 0.70, 0.22), 28)
    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y = 960 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 85), "逻辑没审，请当成还没过", font=kit.font(40), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status.update({
            "project_name": "102_评审只看格式",
            "cut": "new-40s",
            "draft": ".abroll-cloud/102",
            "duration": round(duration, 3),
            "duration_zh": kit.zh_sec(duration),
        })
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    (ROOT / "项目说明.md").write_text(
        f"""# 102 · 评审只看格式

普通短视频 / 知识口播。NEW，不是重做。

- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/102/`
- **记忆库父目录**：`AI视频项目/102_评审只看格式/`（云端不可写 G:，不回退 C/D）
- **时长**：约 {kit.zh_sec(duration)}

## 口播

{vo}
""",
        encoding="utf-8",
    )
    (ROOT / "时长.md").write_text(
        f"""# 成片 102 时长（中文秒）

| 号 | 成片 | 新时长 | 草稿 |
|----|------|--------|------|
| 102 | `{STAGED_NAME}` | {kit.zh_sec(duration)} | `.abroll-cloud/102/` |
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    row = f"| 102 | 工厂知识口播 | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if "| 102 |" in text:
        lines = [row if raw.startswith("| 102 |") else raw for raw in text.splitlines()]
        text = "\n".join(lines)
    else:
        lines = text.splitlines()
        rebuilt = []
        inserted = False
        for raw in lines:
            rebuilt.append(raw)
            if raw.startswith("| 99 |") and not inserted:
                rebuilt.append(row)
                inserted = True
        if not inserted:
            rebuilt.append(row)
        text = "\n".join(rebuilt)
    block = f"""
## 102. 评审只看格式

- **状态**：已核验 · `.abroll-cloud/102/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}
- **A-roll 角度**：工厂 `102_评审只看格式` 短切。只打「评审只看格式」：空格和命名都改了，逻辑没人碰。格式交给机器人，人只审会炸的地方。
- **成片名**：`{STAGED_NAME}`
- **避开**：成片 68 评审找茬；成片 66 点头；兄弟 96/97/98/99/100/101
"""
    if "## 102. 评审只看格式" in text:
        text = text.replace("- **状态**：已认领 · `.abroll-cloud/102/` · NEW · 目标四十到五十秒", f"- **状态**：已核验 · `.abroll-cloud/102/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}")
    else:
        if not text.endswith("\n"):
            text += "\n"
        text += block
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": NAME,
        "staged_name": STAGED_NAME,
        "episode": 102,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "工厂 102_评审只看格式 · 云端 NEW",
        "hooks": "钩子：评审只看格式。\n收束：逻辑没审，请当成还没过。",
        "cover_lines": ("评审", "只看格式"),
        "avoid": "68 / 66 / 62 / 兄弟 96-101",
        "factory": "工厂 102_评审只看格式",
        "broll": {
            "S02": ("B-只改空格命名.mp4", frame_format_skin),
            "S04": ("B-工具过生产不过.mp4", frame_tool_vs_prod),
            "S06": ("B-先问三件事.mp4", frame_three_q),
            "S08": ("B-人只审会炸.mp4", frame_bot_vs_human),
            "S10": ("B-皮过了还没过.mp4", frame_not_done),
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
    print("NEW 102", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
