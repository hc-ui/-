#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 101：加机器当优化。工厂 101 短切加长。云端 NEW。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "加机器当优化"
STAGED_NAME = "101-加机器当优化.mp4"
BANNED = (
    "找茬会", "环境变量", "目录名", "流水账", "临时方案",
    "密钥", "人锅", "下一期", "文件名", "C++", "ROS",
    "评审只看", "试点", "验收",
)


def frame_painkiller(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 账单止痛")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0)) + dy),
        "机器加上去，页面好像顺了",
        font=kit.font(40),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    cards = [
        (0.16, 80, 320, "加一台", "好像顺了"),
        (0.32, 405, 350, "再加一台", "更顺一点"),
        (0.48, 730, 320, "账单", "先开了"),
    ]
    for ts, x, y0, head, body in cards:
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = y0 + int(kit.lerp(18, 0, a)) + dy
        kit.rounded(d, (x, y, x + 270, y + 280), 26, kit.mix(kit.BG, kit.CARD, a))
        d.text((x + 135, y + 80), head, font=kit.font(36), fill=kit.mix(kit.CARD, kit.YELLOW, a), anchor="mm")
        d.text((x + 135, y + 170), body, font=kit.font(30), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="mm")
        kit.x_mark(d, x + 135, y + 230, kit.appear(t, ts + 0.40, 0.18), 22)
    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y, 990, y + 200), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 70), "那不叫优化", font=kit.font(46), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
        d.text((kit.W // 2, y + 140), "叫把账单当止痛药", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, punch), anchor="mm")
    return img


def frame_bill_boom(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 流量先炸账单")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "流量一来，账单先炸",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.16)
    if a1 > 0.04:
        y = 300 + int(kit.lerp(14, 0, a1)) + dy
        kit.rounded(d, (70, y, 500, y + 460), 32, kit.mix(kit.BG, (42, 24, 22), a1))
        d.text((285, y + 70), "多开几台", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
        d.text((285, y + 190), "慢查询", font=kit.font(48), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
        d.text((285, y + 280), "还在原处", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.x_mark(d, 285, y + 370, kit.appear(t, 0.70, 0.20), 30)
    a2 = kit.appear(t, 0.30)
    if a2 > 0.04:
        y = 300 + int(kit.lerp(14, 0, a2)) + dy
        kit.rounded(d, (580, y, 1010, y + 460), 32, kit.mix(kit.BG, kit.CARD, a2))
        d.text((795, y + 70), "同一段慢", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
        d.text((795, y + 190), "照样慢", font=kit.font(48), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")
        d.text((795, y + 280), "只是账单更大", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
        kit.x_mark(d, 795, y + 370, kit.appear(t, 0.88, 0.20), 30)
    punch = kit.appear(t, 1.18, 0.22)
    if punch > 0.04:
        y = 830 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 180), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 90), "多开几台，慢还是那段", font=kit.font(40), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_measure(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 先量瓶颈")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "先量是谁在拖",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    rows = [
        (0.16, "1", "先量", "谁在拖时间"),
        (0.40, "2", "再决定", "加机器或改代码"),
        (0.64, "3", "量过再加", "才叫买时间"),
    ]
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
        d.text((kit.W // 2, y + 70), "没量就加", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
        d.text((kit.W // 2, y + 140), "只是把慢摊到更多账单上", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, punch), anchor="mm")
    return img


def frame_compare(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对照 · 买时间 / 买完结")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "对照只打这一点",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 500), 32, kit.mix(kit.BG, (42, 24, 22), a1))
    d.text((285, y + 56), "当完结", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "加完就停", font=kit.font(48), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    d.text((285, y + 270), "慢还在原处", font=kit.font(36), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    kit.x_mark(d, 285, y + 380, kit.appear(t, 0.55, 0.22), 36)
    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (580, y, 1010, y + 500), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((795, y + 56), "买时间", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((795, y + 180), "先量再加", font=kit.font(48), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    d.text((795, y + 270), "根才会走", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    kit.check_badge(d, 795, y + 380, kit.appear(t, 0.70, 0.22))
    stamp = kit.appear(t, 1.20, 0.24)
    if stamp > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, stamp)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), stamp))
        d.text((kit.W // 2, y3 + 70), "慢还在原处", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, stamp), anchor="mm")
        d.text((kit.W // 2, y3 + 140), "只是人先看见账单", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, stamp), anchor="mm")
    return img


def frame_stamp(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "收 · 还没优化")
    dy = kit.breathe(t, 6)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 230 + int(kit.lerp(16, 0, a0))),
        "没量过瓶颈",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.18)
    if a1 > 0.04:
        cx, cy = 540, 620 + dy
        r = 230
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=kit.mix(kit.BG, (18, 42, 36), a1))
        d.text((cx, cy - 40), "请当成", font=kit.font(40), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        d.text((cx, cy + 50), "还没优化", font=kit.font(52), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
        kit.check_badge(d, cx, cy + 140, kit.appear(t, 0.70, 0.22))
    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y = 960 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 85), "账单降了，也不算做完", font=kit.font(40), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status.update({
            "project_name": "101_加机器当优化",
            "cut": "new-40s",
            "draft": ".abroll-cloud/101",
            "duration": round(duration, 3),
            "duration_zh": kit.zh_sec(duration),
            "official": "AI视频项目/101_加机器当优化/00_最终成片_加机器当优化.mp4",
            "transit": f"成片/{STAGED_NAME}",
        })
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    (ROOT / "项目说明.md").write_text(
        f"""# 101 · 加机器当优化

普通短视频 / 知识口播。NEW，不是重做。

- **路径规则**：共享记忆《本机公共路径与强制约束》2026-09-12 所有视频统一落盘；成品进 `AI视频项目/<NN_中文项目名>/00_最终成片_*`。不自创 `云端成片-*`。
- **成片中转**：`成片/{STAGED_NAME}`（只进成品，草稿不进）
- **正式成品相对路径**：`AI视频项目/101_加机器当优化/00_最终成片_加机器当优化.mp4`
- **草稿根**：`/workspace/.abroll-cloud/101/`
- **时长**：约 {kit.zh_sec(duration)}

## 口播

{vo}
""",
        encoding="utf-8",
    )
    (ROOT / "时长.md").write_text(
        f"""# 成片 101 时长（中文秒）

| 号 | 成片中转 | 新时长 | 草稿 |
|----|----------|--------|------|
| 101 | `{STAGED_NAME}` | {kit.zh_sec(duration)} | `.abroll-cloud/101/` |
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    row = f"| 101 | 工厂知识口播加长 | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if "| 101 |" in text:
        lines = [row if raw.startswith("| 101 |") else raw for raw in text.splitlines()]
        text = "\n".join(lines)
    else:
        if not text.endswith("\n"):
            text += "\n"
        text += "\n" + row + "\n"
    block = (
        "\n## 101. 加机器当优化\n\n"
        f"- **状态**：已核验 · `.abroll-cloud/101/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}\n"
        "- **A-roll 角度**：工厂 `101_加机器当优化` 短切。只打「加机器当优化」。不拷十六秒短切。\n"
        f"- **成片名**：`{STAGED_NAME}`\n"
    )
    if "## 101." not in text:
        text += block
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": NAME,
        "staged_name": STAGED_NAME,
        "episode": 101,
        "expected_phrases": 18,
        "replaced_short": 16.875,
        "source_note": "工厂 101_加机器当优化 · 云端 NEW",
        "hooks": "钩子：加机器当优化。\n收束：没量过瓶颈，请当成还没优化。",
        "cover_lines": ("加机器", "当优化"),
        "avoid": "62 / 61 / 兄弟 96-100 / 102",
        "factory": "工厂 101_加机器当优化",
        "broll": {
            "S02": ("B-账单止痛药.mp4", frame_painkiller),
            "S04": ("B-流量账单先炸.mp4", frame_bill_boom),
            "S06": ("B-先量瓶颈.mp4", frame_measure),
            "S08": ("B-对照买时间.mp4", frame_compare),
            "S10": ("B-还没优化.mp4", frame_stamp),
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
    print("NEW 101", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
