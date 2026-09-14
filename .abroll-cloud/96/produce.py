#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 96：目录名不是项目说明。Drive 项目索引.md。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/96/，成品中转 成片/96-目录名不是项目说明.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不拷工厂 96_密钥轮转拖到过期。不重做 00-95。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "目录名不是项目说明"
STAGED_NAME = "96-目录名不是项目说明.mp4"
BANNED = (
    "下一期",
    "如图所示",
    "密钥",
    "轮转",
    "环境变量",
    "临时方案",
    "学完立刻",
    "三道短题",
    "C++",
    "ROS",
    ".md",
    ".mp4",
    "http",
)


def frame_same_number(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 同号当一条")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0)) + dy),
        "十二号不是一条",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(18, 0, a1)) + dy
    kit.rounded(d, (70, y, 500, y + 500), 32, kit.mix(kit.BG, kit.CARD, a1))
    d.text((285, y + 56), "十二号", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "三秒留人", font=kit.font(48), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    d.text((285, y + 270), "知识口播", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")

    a2 = kit.appear(t, 0.30)
    kit.rounded(d, (580, y, 1010, y + 500), 32, kit.mix(kit.BG, (42, 24, 22), a2))
    d.text((795, y + 56), "也是十二号", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((795, y + 180), "郑人买履", font=kit.font(48), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")
    d.text((795, y + 270), "海报风", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
    kit.x_mark(d, 795, y + 380, kit.appear(t, 0.72, 0.20), 32)

    punch = kit.appear(t, 1.18, 0.22)
    if punch > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 180), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y3 + 90), "同号不是同一条片子", font=kit.font(42), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_pending(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 待补当交付")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "用途以说明为准",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    rows = [
        (0.16, "阶段", "待补说明", False),
        (0.40, "推荐成品", "空着", False),
        (0.64, "项目说明", "才算数", True),
    ]
    for idx, (ts, head, body, ok) in enumerate(rows):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 300 + idx * 168 + int(kit.lerp(16, 0, a))
        fill = (18, 42, 36) if ok else kit.CARD
        kit.rounded(d, (90, y, 990, y + 148), 26, kit.mix(kit.BG, fill, a))
        d.text((130, y + 50), head, font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a), anchor="lm")
        d.text((130, y + 108), body, font=kit.font(40), fill=kit.mix(kit.CARD, kit.MINT if ok else kit.YELLOW, a), anchor="lm")
        if ok:
            kit.check_badge(d, 900, y + 74, kit.appear(t, ts + 0.28, 0.18))
        else:
            kit.x_mark(d, 900, y + 74, kit.appear(t, ts + 0.28, 0.18), 22)

    punch = kit.appear(t, 1.22, 0.22)
    if punch > 0.04:
        y = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y, 990, y + 180), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 90), "待补说明，别当已经交了", font=kit.font(40), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_craft(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 看制作方式")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "怎么拍，看这一列",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 500), 32, kit.mix(kit.BG, (22, 40, 36), a1))
    d.text((285, y + 70), "制作方式", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 200), "白底小灯", font=kit.font(48), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
    d.text((285, y + 290), "口播 A 卷", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
    kit.check_badge(d, 285, y + 400, kit.appear(t, 0.55, 0.20))

    a2 = kit.appear(t, 0.30)
    kit.rounded(d, (580, y, 1010, y + 500), 32, kit.mix(kit.BG, kit.CARD, a2))
    d.text((795, y + 70), "制作方式", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((795, y + 200), "黑底对照卡", font=kit.font(44), fill=kit.mix(kit.CARD, kit.YELLOW, a2), anchor="mm")
    d.text((795, y + 290), "画面 B 卷", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
    kit.check_badge(d, 795, y + 400, kit.appear(t, 0.72, 0.20))

    punch = kit.appear(t, 1.18, 0.22)
    if punch > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 180), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 90), "这一列才告诉你怎么拍", font=kit.font(40), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_recommend(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 推荐成品")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "成片看这一格",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 500), 32, kit.mix(kit.BG, (42, 24, 22), a1))
    d.text((285, y + 56), "凭感觉", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "猜目录", font=kit.font(52), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    d.text((285, y + 270), "找错片子", font=kit.font(36), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    kit.x_mark(d, 285, y + 380, kit.appear(t, 0.55, 0.22), 36)

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (580, y, 1010, y + 500), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((795, y + 56), "推荐成品", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((795, y + 180), "写路径", font=kit.font(52), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    d.text((795, y + 270), "才是成片", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    kit.check_badge(d, 795, y + 380, kit.appear(t, 0.70, 0.22))

    punch = kit.appear(t, 1.20, 0.24)
    if punch > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 180), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 90), "那一格写的是路径", font=kit.font(42), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_drawer(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对照 · 标签 / 说明")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "标签不是说明",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    cards = [
        (0.16, 90, 300, "目录名", "抽屉标签"),
        (0.36, 400, 340, "项目说明", "用途"),
        (0.56, 710, 300, "成品列", "交付"),
    ]
    for ts, x, y0, head, body in cards:
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = y0 + int(kit.lerp(18, 0, a)) + dy
        kit.rounded(d, (x, y, x + 270, y + 280), 26, kit.mix(kit.BG, kit.CARD, a))
        d.text((x + 135, y + 80), head, font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a), anchor="mm")
        d.text((x + 135, y + 170), body, font=kit.font(40), fill=kit.mix(kit.CARD, kit.MINT if head != "目录名" else kit.YELLOW, a), anchor="mm")
        if head == "目录名":
            kit.x_mark(d, x + 135, y + 230, kit.appear(t, ts + 0.40, 0.18), 20)
        else:
            kit.check_badge(d, x + 135, y + 230, kit.appear(t, ts + 0.40, 0.18))

    punch = kit.appear(t, 1.18, 0.22)
    if punch > 0.04:
        y = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y, 990, y + 180), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 90), "说明书和成品列，才是索引", font=kit.font(38), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_stamp(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "收 · 先翻说明")
    dy = kit.breathe(t, 6)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 230 + int(kit.lerp(16, 0, a0))),
        "先翻说明，再叫完成",
        font=kit.font(46),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.18)
    if a1 > 0.04:
        cx, cy = 540, 620 + dy
        r = 230
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=kit.mix(kit.BG, (18, 42, 36), a1))
        d.text((cx, cy - 40), "先翻说明", font=kit.font(56), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
        d.text((cx, cy + 50), "再叫完成", font=kit.font(40), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.check_badge(d, cx, cy + 140, kit.appear(t, 0.70, 0.22))

    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y = 960 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 85), "目录名不是项目说明", font=kit.font(42), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    """本集是 NEW，改回 .abroll-cloud/96/。"""
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "96_目录名不是项目说明"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/96"
        status["source_note"] = "Drive 项目索引.md / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status["distinct_from"] = ["96-密钥轮转拖到过期", "95-学完立刻用一次", "70-例子先于概念"]
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "96_目录名不是项目说明"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        report["distinct_from_factory_96"] = True
        vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8")
        report["script_guard"] = {w: (w not in vo) for w in BANNED}
        report["ok"] = bool(report.get("ok")) and all(report["script_guard"].values())
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/96"
        data["source_note"] = "Drive 项目索引.md / 云端 NEW"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 96 · 目录名不是项目说明

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：Drive 只读 `项目索引.md`（2026-09-11；用途以各目录项目说明为准）
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/96/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：工厂 96 密钥轮转拖到过期；成片 00–95；成片 70 / 95

钩子：打开索引，最先骗你的是目录名。
诊断：十二号既有三秒留人，也有郑人买履。同号不是同一条片子。
做法：用途以项目说明为准。要找成片，去看推荐成品那一格。
收束：目录名只是抽屉标签。先翻项目说明，再开口叫完成。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头十三条，口播十四句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")
    (ROOT / "时长.md").write_text(
        f"""# 成片 96 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 来源 | 新时长 | 草稿 |
|----|------|------|--------|------|
| 96 | `{STAGED_NAME}` | Drive 项目索引.md | {kit.zh_sec(duration)} | `.abroll-cloud/96/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。十三镜 / 十四句。禁止 `tpad=stop_mode=clone`。
不拷工厂 96 密钥轮转，不重做 00–95。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    section = f"""## 96. 目录名不是项目说明

- **状态**：已核验 · `.abroll-cloud/96/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}
- **A-roll 角度**：Drive `项目索引.md`。只打「目录名不是项目说明」：同号会撞、待补不是交付、成片看推荐成品列。不讲密钥轮转，不讲学完立刻用一次。
- **B-roll 想法**：十二号两条片子并排；待补说明打叉、项目说明打勾；制作方式 A 灯 / B 卡；推荐成品写路径；抽屉标签对说明书；先翻说明再叫完成。
- **来源笔记**：Drive 只读 `项目索引.md`（用途以各目录项目说明为准；`/workspace/成片/` 无本条）
- **成片名**：`{STAGED_NAME}`
- **避开**：工厂 96 密钥轮转拖到过期；成片 00–95；成片 70 / 95
"""
    text = path.read_text(encoding="utf-8")
    token = "## 96. 目录名不是项目说明"
    if token in text:
        # keep existing body; only refresh status line if present
        claimed = "- **状态**：已认领 · `.abroll-cloud/96/` · NEW · 目标四十到五十秒"
        verified = f"- **状态**：已核验 · `.abroll-cloud/96/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
        if claimed in text:
            text = text.replace(claimed, verified)
    else:
        text = text.rstrip() + "\n\n" + section
    row = f"| 96 | 项目索引（未用过） | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if "| 96 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 96 |"):
                lines.append(row)
            else:
                lines.append(raw)
        text = "\n".join(lines)
    elif "| 95 |" in text:
        lines = []
        inserted = False
        for raw in text.splitlines():
            lines.append(raw)
            if (not inserted) and raw.startswith("| 95 |"):
                lines.append(row)
                inserted = True
        text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def patch_delivery_new(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    new = (
        f"| `成片/{STAGED_NAME}` | 1080×1920 h264+aac 44.1k stereo | {kit.zh_sec(duration)} | "
        f"topic 96 Drive 只读 `项目索引.md`（用途以项目说明为准；同号会撞；推荐成品列才是交付）。"
        f"云端 NEW，不拷工厂 96 密钥轮转，不重做 00–95。 |"
    )
    token = f"`成片/{STAGED_NAME}`"
    if token in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("|") and token in raw:
                lines.append(new)
            else:
                lines.append(raw)
        text = "\n".join(lines)
    else:
        lines = text.splitlines()
        rebuilt = []
        inserted = False
        for raw in lines:
            if (not inserted) and "仙侠云海突进" in raw and raw.strip().startswith("|"):
                rebuilt.append(new)
                inserted = True
            rebuilt.append(raw)
        if not inserted:
            rebuilt.append(new)
        text = "\n".join(rebuilt)

    plus_row = f"| 96 | `{STAGED_NAME}` | {kit.zh_sec(duration)} | 已核验 |"
    if "| 96 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 96 |"):
                lines.append(plus_row)
            else:
                lines.append(raw)
        text = "\n".join(lines)
    elif "## 本轮 61+（核验中）" in text:
        lines = text.splitlines()
        out = []
        inserted = False
        for raw in lines:
            out.append(raw)
            if raw.startswith("| 95 |") and not inserted:
                out.append(plus_row)
                inserted = True
        if not inserted:
            out.append(plus_row)
        text = "\n".join(out)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "目录名不是项目说明",
        "staged_name": STAGED_NAME,
        "episode": 96,
        "expected_phrases": 14,
        "replaced_short": 0,
        "source_note": "Drive 项目索引.md · 云端 NEW",
        "hooks": "钩子：打开索引，最先骗你的是目录名。\n诊断：十二号既有三秒留人，也有郑人买履。\n做法：用途以项目说明为准；成片看推荐成品列。\n收束：先翻项目说明，再开口叫完成。",
        "cover_lines": ("目录名不是", "项目说明"),
        "avoid": "工厂 96 密钥轮转拖到过期；成片 00–95；成片 70 / 95",
        "factory": "项目索引.md",
        "broll": {
            "S02": ("B-同号不是一条.mp4", frame_same_number),
            "S04": ("B-待补不是交付.mp4", frame_pending),
            "S06": ("B-制作方式那一列.mp4", frame_craft),
            "S08": ("B-推荐成品.mp4", frame_recommend),
            "S10": ("B-抽屉标签.mp4", frame_drawer),
            "S12": ("B-先翻说明.mp4", frame_stamp),
        },
    })


def finish_docs() -> None:
    ep = episode()
    staged = Path("/workspace/成片") / STAGED_NAME
    draft = ROOT / f"00_最终成片_{NAME}.mp4"
    if not staged.exists():
        raise SystemExit(f"missing staged {staged}")
    data = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
    dur = kit.probe_dur(staged)
    draft_dur = kit.probe_dur(draft) if draft.exists() else dur
    ep.write_docs(draft_dur, staged, data)
    ep.patch_index_line(Path("/workspace/成片/INDEX.md"), dur)
    ep.patch_index_line(Path("/workspace/.abroll-cloud/INDEX.chengpian.md"), dur)
    patch_delivery_new(dur)
    report = ep.qa(staged, data)
    report["chengpian"] = str(staged)
    report["chengpian_duration_s"] = dur
    report["chengpian_duration_zh"] = kit.zh_sec(dur)
    report["draft_duration_s"] = draft_dur
    report["draft_duration_zh"] = kit.zh_sec(draft_dur)
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rewrite_docs(dur)
    patch_topics(dur)
    print("DOCS 96", staged, kit.zh_sec(dur), "ok", report.get("ok"))
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


def main() -> None:
    if "--docs-only" in sys.argv:
        finish_docs()
        return
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8")
    hit = [w for w in BANNED if w in vo]
    if hit:
        raise SystemExit(f"banned phrases in VO: {hit}")
    ep = episode()
    report = ep.produce()
    staged = Path("/workspace/成片") / STAGED_NAME
    dur = kit.probe_dur(staged) if staged.exists() else float(report.get("chengpian_duration_s") or report["video"]["duration_s"])
    rewrite_docs(dur)
    patch_topics(dur)
    patch_delivery_new(dur)
    print("NEW 96", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
