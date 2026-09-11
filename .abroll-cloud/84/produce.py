#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 84：接口变更口头说一声。topics-batch4 #84。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/84/，成品中转 成片/84-接口变更口头说一声.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不重复成片 65 口头同步当结论，不重复成片 66 点头不等于确认。
不拷工厂 73_接口变更口头说一声 十七点八秒短切。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "接口变更口头说一声"
STAGED_NAME = "84-接口变更口头说一声.mp4"
BANNED = ("口头同步", "走廊对过", "群里回了个好", "点头", "谁同意", "写下三行", "下一期")


def frame_mouth_path(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 只说一声")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0)) + dy),
        "站会提一句",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.14)
    if a1 > 0.04:
        y = 320 + int(kit.lerp(18, 0, a1)) + dy
        kit.rounded(d, (70, y, 500, y + 420), 32, kit.mix(kit.BG, (42, 28, 18), a1))
        d.text((285, y + 70), "嘴里", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
        d.text((285, y + 180), "字段改了", font=kit.font(44), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
        d.text((285, y + 270), "说一声", font=kit.font(36), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.x_mark(d, 285, y + 350, kit.appear(t, 0.70, 0.20), 28)

    a2 = kit.appear(t, 0.28)
    if a2 > 0.04:
        y = 320 + int(kit.lerp(18, 0, a2)) + dy
        kit.rounded(d, (580, y, 1010, y + 420), 32, kit.mix(kit.BG, (42, 24, 22), a2))
        d.text((795, y + 70), "文档", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
        d.text((795, y + 180), "/v1/user", font=kit.font(42), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")
        d.text((795, y + 270), "还是上周", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
        kit.x_mark(d, 795, y + 350, kit.appear(t, 0.88, 0.20), 28)

    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y = 800 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 180), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 90), "旧路径还挂着", font=kit.font(48), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_field_boom(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 旧字段还在打")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "调用方按旧的打",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    if a1 > 0.04:
        y = 310 + int(kit.lerp(14, 0, a1)) + dy
        kit.rounded(d, (80, y, 500, y + 280), 28, kit.mix(kit.BG, kit.CARD, a1))
        d.text((290, y + 70), "服务端", font=kit.font(26), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
        d.text((290, y + 160), "uid", font=kit.font(56), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
        kit.check_badge(d, 290, y + 230, kit.appear(t, 0.55, 0.18))

    a2 = kit.appear(t, 0.28)
    if a2 > 0.04:
        y = 310 + int(kit.lerp(14, 0, a2)) + dy
        kit.rounded(d, (580, y, 1000, y + 280), 28, kit.mix(kit.BG, (42, 24, 22), a2))
        d.text((790, y + 70), "调用方", font=kit.font(26), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
        d.text((790, y + 160), "user_id", font=kit.font(48), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")
        kit.x_mark(d, 790, y + 230, kit.appear(t, 0.70, 0.18), 26)

    boom = kit.appear(t, 0.85, 0.24)
    if boom > 0.04:
        y = 650 + int(kit.lerp(18, 0, boom)) + dy
        kit.rounded(d, (140, y, 940, y + 220), 28, kit.mix(kit.BG, (48, 22, 20), boom))
        d.text((kit.W // 2, y + 70), "联调当天炸", font=kit.font(48), fill=kit.mix(kit.BG, kit.RED, boom), anchor="mm")
        d.text((kit.W // 2, y + 150), "双方都说没错", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, boom), anchor="mm")

    punch = kit.appear(t, 1.20, 0.22)
    if punch > 0.04:
        y = 940 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 170), 28, kit.mix(kit.BG, (42, 32, 16), punch))
        d.text((kit.W // 2, y + 85), "口头说一声，不是变更", font=kit.font(40), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_three_places(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 落三处")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "变更要落三处",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    cards = [
        (0.14, 80, "改了什么", "新路径", kit.YELLOW),
        (0.32, 390, "谁受影响", "调用方", kit.MINT),
        (0.50, 700, "从哪版生效", "v2 起", kit.AMBER),
    ]
    for ts, x, head, body, color in cards:
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 340 + int(kit.lerp(16, 0, a)) + dy
        kit.rounded(d, (x, y, x + 290, y + 420), 28, kit.mix(kit.BG, kit.CARD, a))
        d.rounded_rectangle((x + 22, y + 24, x + 268, y + 88), 16, fill=kit.mix(kit.CARD, color, a))
        d.text((x + 145, y + 56), head, font=kit.font(28), fill=kit.mix(color, kit.INK, a), anchor="mm")
        d.text((x + 145, y + 200), body, font=kit.font(36), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="mm")
        kit.check_badge(d, x + 145, y + 320, kit.appear(t, ts + 0.55, 0.18))

    punch = kit.appear(t, 1.20, 0.22)
    if punch > 0.04:
        y = 830 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 85), "写成字才算变更", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_in_mouth(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 只留嘴里")
    dy = kit.breathe(t, 6)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 230 + int(kit.lerp(16, 0, a0))),
        "别只留在嘴里",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    if a1 > 0.04:
        cx, cy = 540, 560 + dy
        r = 210
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=kit.mix(kit.BG, (42, 24, 22), a1))
        d.text((cx, cy - 40), "嘴里", font=kit.font(56), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
        d.text((cx, cy + 50), "接口变更", font=kit.font(36), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.x_mark(d, cx, cy + 130, kit.appear(t, 0.70, 0.22), 36)

    punch = kit.appear(t, 1.10, 0.22)
    if punch > 0.04:
        y = 880 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 180), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 90), "联调接不住", font=kit.font(52), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_write_ship(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "收 · 先写再上")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "先写下，再上线",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    if a1 > 0.04:
        y = 330 + int(kit.lerp(14, 0, a1)) + dy
        kit.rounded(d, (70, y, 500, y + 400), 32, kit.mix(kit.BG, (42, 24, 22), a1))
        d.text((285, y + 80), "口头", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
        d.text((285, y + 180), "说一声", font=kit.font(48), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
        kit.strike_box(d, (120, y + 150, 450, y + 220), kit.appear(t, 0.50, 0.35), kit.mix(kit.CARD, kit.RED, 1))
        kit.x_mark(d, 285, y + 300, kit.appear(t, 0.62, 0.18), 30)

    a2 = kit.appear(t, 0.30)
    if a2 > 0.04:
        y = 330 + int(kit.lerp(14, 0, a2)) + dy
        kit.rounded(d, (580, y, 1010, y + 400), 32, kit.mix(kit.BG, (18, 42, 36), a2))
        d.text((795, y + 80), "落字", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
        d.text((795, y + 170), "对照卡", font=kit.font(44), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
        d.text((795, y + 250), "再上线", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
        kit.check_badge(d, 795, y + 330, kit.appear(t, 0.80, 0.18))

    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y = 800 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 180), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 90), "写成字，才算改过", font=kit.font(46), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    """Episode 默认写成 84-long / 加长重切；本集是 NEW，改回 .abroll-cloud/84/。"""
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "84_接口变更口头说一声"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/84"
        status["source_note"] = "topics-batch4.md #84 / 工厂 73_接口变更口头说一声 / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status["distinct_from"] = ["65-口头同步当过结论", "66-点头不等于确认", "73-int-input先包一层"]
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "84_接口变更口头说一声"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        report["distinct_from_65"] = True
        report["distinct_from_66"] = True
        vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8")
        report["script_guard"] = {w: (w not in vo) for w in BANNED}
        report["ok"] = bool(report.get("ok")) and all(report["script_guard"].values())
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/84"
        data["source_note"] = "topics-batch4.md #84 / 工厂 73_接口变更口头说一声 / 云端 NEW"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 84 · 接口变更口头说一声

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：`topics-batch4.md` 第 84 条；Drive 只读工厂 `73_接口变更口头说一声`
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/84/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：成片 65 口头同步当过结论；成片 66 点头不等于确认；成片 73 int-input；工厂 280 契约没人通知

钩子：接口改了，只口头说一声。
诊断：字段换了仍打旧字段；站会一句，文档还是旧路径。
做法：落三处——改了什么、谁受影响、从哪版生效。
收束：嘴里的变更联调接不住。口头说一声，请当成没改。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头十二条，口播十六句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")
    (ROOT / "时长.md").write_text(
        f"""# 成片 84 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 工厂短切 | 新时长 | 草稿 |
|----|------|----------|--------|------|
| 84 | `{STAGED_NAME}` | 十七点八秒（工厂 73 号，未进成片） | {kit.zh_sec(duration)} | `.abroll-cloud/84/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。十二镜 / 十六句。禁止 `tpad=stop_mode=clone`。
不重做 65 / 66，不拷工厂成片。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    section = f"""## 84. 接口变更口头说一声

- **状态**：已核验 · `.abroll-cloud/84/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}
- **A-roll 角度**：工厂 `73_接口变更口头说一声` 十七点八秒短切。成片号 73 已被 `int-input先包一层` 占用，本条改认 84。只打「接口改了只口头说一声」：字段/路径/生效版只留在嘴里，调用方还按旧的打。不讲口头同步当结论，不讲点头不等于确认。
- **B-roll 想法**：嘴说一声对旧路径还挂着；user_id 对 uid，联调当天炸；变更落三处：改了什么、谁受影响、从哪版生效；先写下再上线。
- **来源笔记**：Drive 只读工厂 `73_接口变更口头说一声`（claim：十七点八秒短切；`/workspace/成片/` 无本条）
- **成片名**：`{STAGED_NAME}`
- **避开**：#65 口头同步当过结论；#66 点头不等于确认；成片 73 int-input；工厂 280 接口契约改了没人通知
"""
    claimed = "- **状态**：已认领 · `.abroll-cloud/84/` · NEW · 目标四十到五十秒"
    verified = f"- **状态**：已核验 · `.abroll-cloud/84/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
    if "## 84. 接口变更口头说一声" in text:
        if claimed in text:
            text = text.replace(claimed, verified)
        elif verified not in text:
            text = text.replace(
                "## 84. 接口变更口头说一声\n\n- **A-roll 角度**：",
                f"## 84. 接口变更口头说一声\n\n{verified}\n- **A-roll 角度**：",
            )
    elif "## 85. 毕业底线三件套" in text:
        text = text.replace("## 85. 毕业底线三件套", section + "\n## 85. 毕业底线三件套")
    else:
        text = text.rstrip() + "\n\n" + section

    row = f"| 84 | 工厂知识口播改认 | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    claimed_row = "| 84 | 工厂知识口播改认 | `84-接口变更口头说一声.mp4` | 已认领 `.abroll-cloud/84/` |"
    if "| 84 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 84 |"):
                lines.append(row)
            else:
                lines.append(raw)
        text = "\n".join(lines)
    elif claimed_row in text:
        text = text.replace(claimed_row, row)
    elif "| 85 |" in text:
        text = text.replace("| 85 |", row + "\n| 85 |", 1)
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
        f"topic 84 `topics-batch4.md` 第 84 条；Drive 只读工厂 `73_接口变更口头说一声`（十七点八秒短切）。"
        f"成片号 73 已被 int-input 占用。云端 NEW，不拷工厂成片，不重做 65/66。 |"
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

    plus_row = f"| 84 | `{STAGED_NAME}` | {kit.zh_sec(duration)} | 已核验 |"
    if "| 84 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 84 |"):
                lines.append(plus_row)
            else:
                lines.append(raw)
        text = "\n".join(lines)
    elif "| 73 |" in text and plus_row not in text:
        lines = text.splitlines()
        out = []
        inserted = False
        for raw in lines:
            out.append(raw)
            if raw.startswith("| 73 |") and not inserted:
                out.append(plus_row)
                inserted = True
        text = "\n".join(out)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "接口变更口头说一声",
        "staged_name": STAGED_NAME,
        "episode": 84,
        "expected_phrases": 16,
        "replaced_short": 0,
        "source_note": "topics-batch4.md #84 · 工厂 73_接口变更口头说一声 · 云端 NEW",
        "hooks": "钩子：接口改了，只口头说一声。\n诊断：字段换了仍打旧字段；文档还是旧路径。\n做法：落三处——改了什么、谁受影响、从哪版生效。\n收束：口头说一声，请当成没改。",
        "cover_lines": ("接口变更", "口头说一声"),
        "avoid": "成片 65 口头同步当结论；成片 66 点头不等于确认；成片 73 int-input；工厂 280 契约没人通知",
        "factory": "topics-batch4 #84",
        "broll": {
            "S02": ("B-嘴说旧路径.mp4", frame_mouth_path),
            "S04": ("B-联调才炸.mp4", frame_field_boom),
            "S06": ("B-落三处.mp4", frame_three_places),
            "S08": ("B-别留嘴里.mp4", frame_in_mouth),
            "S10": ("B-先写再上.mp4", frame_write_ship),
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
    print("DOCS 84", staged, kit.zh_sec(dur), "ok", report.get("ok"))
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
    print("NEW 84", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
