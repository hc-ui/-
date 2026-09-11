#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 92：就业栈别绑死生医。topics-batch4 #92。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/92/，成品中转 成片/92-就业栈别绑死生医.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不重做成片 14 双线，不重做成片 90 抽件。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "就业栈别绑死生医"
STAGED_NAME = "92-就业栈别绑死生医.mp4"
BANNED = (
    "两条线",
    "就业技术栈自己建",
    "Python 学扎实",
    "五条路",
    "可迁移",
    "抽走",
    "留下场景",
    "养细胞",
    "试剂名",
    "会建回路",
    "我做过生医",
    "课题是矿",
    "籍贯",
    "生态位",
    "测控底层",
    "包装成",
    "开题盲审",
    "下一期",
    "赵老师",
)


def punch(d, t: float, start: float, text: str, mint: bool = True) -> None:
    a = kit.appear(t, start, 0.22)
    if a <= 0.04:
        return
    y = 1040 + kit.breathe(t, 6)
    fill = kit.mix(kit.BG, (18, 42, 36) if mint else (42, 32, 16), a)
    ink = kit.mix(kit.BG, kit.MINT if mint else kit.YELLOW, a)
    kit.rounded(d, (120, y, 960, y + 170), 28, fill)
    d.text((kit.W // 2, y + 85), text, font=kit.font(46), fill=ink, anchor="mm")


def frame_incubator(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 栈指向培养箱")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 228 + int(kit.lerp(16, 0, a0)) + dy),
        "栈别指向培养箱",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.14)
    if a1 > 0.04:
        y = 330 + dy
        kit.rounded(d, (70, y, 500, y + 500), 32, kit.mix(kit.BG, (42, 24, 22), a1))
        d.text((285, y + 80), "焊死", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
        d.text((285, y + 200), "培养箱", font=kit.font(52), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
        d.text((285, y + 300), "应用名", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.strike_box(d, (120, y + 160, 450, y + 240), kit.appear(t, 0.42, 0.35), kit.mix(kit.CARD, kit.RED, 1))
        kit.x_mark(d, 285, y + 400, kit.appear(t, 0.58, 0.18), 32)

    a2 = kit.appear(t, 0.28)
    if a2 > 0.04:
        y = 330 + kit.breathe(t + 0.2, 4)
        kit.rounded(d, (580, y, 1010, y + 500), 32, kit.mix(kit.BG, (18, 42, 36), a2))
        d.text((795, y + 80), "指向", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
        d.text((795, y + 200), "换房间", font=kit.font(52), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
        d.text((795, y + 300), "能力还在", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
        kit.check_badge(d, 795, y + 400, kit.appear(t, 0.72, 0.18))

    punch(d, t, 1.05, "不是指向培养箱")
    return img


def frame_intern(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 入口只留一扇")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 228 + int(kit.lerp(14, 0, a0))),
        "实习别只投生仪厂",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.14)
    if a1 > 0.04:
        y = 330 + dy
        kit.rounded(d, (90, y, 990, y + 220), 32, kit.mix(kit.BG, (42, 24, 22), a1))
        d.text((kit.W // 2, y + 70), "只投 · 生仪厂", font=kit.font(44), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
        d.text((kit.W // 2, y + 150), "栈焊进一间实验室", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
        kit.x_mark(d, 930, y + 70, kit.appear(t, 0.40, 0.18), 26)

    doors = [
        (0.36, 90, "体外诊断"),
        (0.50, 400, "运动控制"),
        (0.64, 710, "工业采集"),
    ]
    for ts, x, label in doors:
        a = kit.appear(t, ts, 0.20)
        if a < 0.04:
            continue
        y = 600 + kit.breathe(t + ts, 5)
        locked = label == "体外诊断"
        fill = kit.mix(kit.BG, (42, 24, 22) if locked else kit.CARD, a)
        kit.rounded(d, (x, y, x + 280, y + 260), 28, fill)
        d.text((x + 140, y + 90), "门", font=kit.font(26), fill=kit.mix(kit.CARD, kit.MUTED, a), anchor="mm")
        d.text((x + 140, y + 160), label, font=kit.font(32), fill=kit.mix(kit.CARD, kit.RED if locked else kit.WHITE, a), anchor="mm")
        if locked:
            kit.x_mark(d, x + 140, y + 210, kit.appear(t, ts + 0.18, 0.16), 22)
        else:
            kit.x_mark(d, x + 140, y + 210, kit.appear(t, ts + 0.18, 0.16), 22)

    punch(d, t, 1.08, "焊进一间实验室", mint=False)
    return img


def frame_handbook(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 夜读跟着湿台")
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 228 + int(kit.lerp(14, 0, a0))),
        "夜读别只翻细胞手册",
        font=kit.font(46),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.14)
    y = 330 + kit.breathe(t, 5)
    if a1 > 0.04:
        kit.rounded(d, (110, y, 970, y + 260), 32, kit.mix(kit.BG, (42, 24, 22), a1))
        d.text((kit.W // 2, y + 90), "细胞手册", font=kit.font(52), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
        kit.strike_box(d, (220, y + 50, 860, y + 140), kit.appear(t, 0.40, 0.35), kit.mix(kit.CARD, kit.RED, 1))
        d.text((kit.W // 2, y + 190), "栈跟着湿台走", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")

    chips = [(0.46, 90, "控制", kit.YELLOW), (0.60, 560, "系统", kit.MINT)]
    for ts, x, label, color in chips:
        a = kit.appear(t, ts, 0.20)
        if a < 0.04:
            continue
        cy = 660 + kit.breathe(t + ts, 5)
        kit.rounded(d, (x, cy, x + 430, cy + 220), 28, kit.mix(kit.BG, kit.CARD, a))
        d.text((x + 215, cy + 110), label, font=kit.font(48), fill=kit.mix(kit.CARD, color, a), anchor="mm")
        kit.check_badge(d, x + 360, cy + 50, kit.appear(t, ts + 0.22, 0.16))

    punch(d, t, 1.08, "别跟着湿台走")
    return img


def frame_room_city(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 房间不是城")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 228 + int(kit.lerp(14, 0, a0)) + dy),
        "生医是现在的房间",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.14)
    if a1 > 0.04:
        y = 330 + dy
        kit.rounded(d, (70, y, 500, y + 500), 32, kit.mix(kit.BG, kit.CARD, a1))
        d.text((285, y + 80), "房间", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
        d.text((285, y + 210), "生医", font=kit.font(64), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
        d.text((285, y + 330), "现在的工位", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")

    a2 = kit.appear(t, 0.30)
    if a2 > 0.04:
        y = 330 + kit.breathe(t + 0.15, 4)
        kit.rounded(d, (580, y, 1010, y + 500), 32, kit.mix(kit.BG, (18, 42, 36), a2))
        d.text((795, y + 70), "城", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
        d.text((795, y + 170), "控制", font=kit.font(44), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
        d.text((795, y + 250), "机器人", font=kit.font(44), fill=kit.mix(kit.CARD, kit.YELLOW, a2), anchor="mm")
        d.text((795, y + 330), "系统", font=kit.font(44), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
        kit.check_badge(d, 795, y + 420, kit.appear(t, 0.72, 0.18))

    punch(d, t, 1.05, "不是住一辈子的城", mint=False)
    return img


def frame_answer(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 先报本事")
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 228 + int(kit.lerp(14, 0, a0))),
        "别先报应用名",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.14)
    y = 330 + kit.breathe(t, 5)
    if a1 > 0.04:
        kit.rounded(d, (110, y, 970, y + 240), 32, kit.mix(kit.BG, (42, 24, 22), a1))
        d.text((kit.W // 2, y + 80), "待过哪类实验室", font=kit.font(44), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
        kit.strike_box(d, (180, y + 40, 900, y + 120), kit.appear(t, 0.38, 0.35), kit.mix(kit.CARD, kit.RED, 1))
        d.text((kit.W // 2, y + 170), "应用名不是答案", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")

    a2 = kit.appear(t, 0.46)
    if a2 > 0.04:
        cy = 640 + kit.breathe(t + 0.2, 5)
        kit.rounded(d, (110, cy, 970, cy + 260), 32, kit.mix(kit.BG, (18, 42, 36), a2))
        d.text((kit.W // 2, cy + 90), "会把系统稳住", font=kit.font(48), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
        d.text((kit.W // 2, cy + 180), "先报本事", font=kit.font(30), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
        kit.check_badge(d, 900, cy + 70, kit.appear(t, 0.70, 0.16))

    punch(d, t, 1.10, "先报系统稳住")
    return img


def rewrite_docs(duration: float) -> None:
    """Episode 默认写成 92-long / 加长重切；本集是 NEW，改回 .abroll-cloud/92/。"""
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "92_就业栈别绑死生医"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/92"
        status["source_note"] = "topics-batch4.md #92 / 学习基线就业栈别绑死生医 / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status["distinct_from"] = [
            "成片/14-导师课题毕业就业技术栈自己建.mp4",
            "成片/90-从课题抽可迁移能力.mp4",
            "成片/15-在生医实验室抢测控生态位.mp4",
        ]
        status["cloud_only"] = True
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "92_就业栈别绑死生医"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        report["distinct_from_14_90"] = True
        vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8")
        report["script_guard"] = {w: (w not in vo) for w in BANNED}
        keep = {
            "14": Path("/workspace/成片/14-导师课题毕业就业技术栈自己建.mp4"),
            "90": Path("/workspace/成片/90-从课题抽可迁移能力.mp4"),
        }
        report["keep_14_90"] = {
            key: {"exists": path.exists(), "bytes": path.stat().st_size if path.exists() else 0}
            for key, path in keep.items()
        }
        report["ok"] = (
            bool(report.get("ok"))
            and all(report["script_guard"].values())
            and all(v["exists"] for v in report["keep_14_90"].values())
            and bool(report.get("timeline", {}).get("in_target_window", False))
        )
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/92"
        data["source_note"] = "topics-batch4.md #92 / 学习基线就业栈别绑死生医 / 云端 NEW"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 92 · 就业栈别绑死生医

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：`topics-batch4.md` 第 92 条；Drive 只读学习基线 2026-08-24 不把长期就业技术栈绑定在生物医学应用领域
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/92/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：成片 14 双线 / Python 先扎实；成片 90 从课题抽可迁移能力；成片 15 抢测控生态位

钩子：课题可以偏生医，就业栈别焊死在生医上。
诊断：长期栈指向能换房间的能力，不是指向培养箱。
例子：工入口别只留给体外诊断；实习只投生仪厂等于焊进一间实验室。
收束：栈指向房间外面，人才能走出去。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。不念真名。NEW，不重做 14 / 90。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头十二条，口播十六句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")
    (ROOT / "时长.md").write_text(
        f"""# 成片 92 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。不重做 14，不重做 90。

| 号 | 成片 | 对照 14 | 对照 90 | 新时长 | 草稿 |
|----|------|---------|---------|--------|------|
| 92 | `{STAGED_NAME}` | 十四点一秒（双线） | 五十秒（抽件） | {kit.zh_sec(duration)} | `.abroll-cloud/92/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。十二镜 / 十六句。禁止 `tpad=stop_mode=clone`。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    section = f"""## 92. 就业栈别绑死生医

- **状态**：已核验 · `.abroll-cloud/92/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}
- **A-roll 角度**：学习基线「不把长期就业技术栈绑定在生物医学应用领域」。成片 14 已拍双线分开、Python 先扎实；成片 90 已拍从课题抽可迁移能力。本条只打栈的指向：课题可以偏生医，就业栈别焊死在生医应用上。不讲双线怎么开，不讲从课题里抽件。
- **B-roll 想法**：培养箱打叉对换房间打勾；只投生仪厂焊进一间实验室；细胞手册划掉；生医是房间，城是控制/机器人/系统；先报系统稳住。
- **来源笔记**：Drive 只读 `学习与职业规划基线.md`（2026-08-24 第四条；`/workspace/成片/` 无本条）
- **成片名**：`{STAGED_NAME}`
- **避开**：成片 14 双线；成片 90 抽件；成片 15 生态位；成片 51 Agent 副线
"""
    claimed = "- **状态**：已认领 · `.abroll-cloud/92/` · NEW · 目标四十到五十秒"
    verified = f"- **状态**：已核验 · `.abroll-cloud/92/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
    if "## 92. 就业栈别绑死生医" in text:
        if claimed in text:
            text = text.replace(claimed, verified)
        elif verified not in text:
            text = text.replace(
                "## 92. 就业栈别绑死生医\n\n- **A-roll 角度**：",
                f"## 92. 就业栈别绑死生医\n\n{verified}\n- **A-roll 角度**：",
            )
    else:
        text = text.rstrip() + "\n\n" + section

    row = f"| 92 | 学习基线口播 | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if "| 92 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 92 |"):
                lines.append(row)
            else:
                lines.append(raw)
        text = "\n".join(lines)
    elif "| 94 |" in text:
        text = text.replace("| 94 |", row + "\n| 94 |", 1)
    elif "| 84 |" in text:
        text = text.replace("| 84 |", row + "\n| 84 |", 1)
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
        f"topic 92 `topics-batch4.md` 第 92 条；Drive 只读 `学习与职业规划基线.md`"
        f"（2026-08-24「不把长期就业技术栈绑定在生物医学应用领域」）。云端 NEW，不重做 14 / 90。 |"
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
        marker = "| `成片/仙侠云海突进.mp4`"
        if marker in text:
            text = text.replace(marker, new + "\n" + marker)
        else:
            if not text.endswith("\n"):
                text += "\n"
            text += new + "\n"
    plus_row = f"| 92 | `{STAGED_NAME}` | {kit.zh_sec(duration)} | 已核验 |"
    if "| 92 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 92 |"):
                lines.append(plus_row)
            else:
                lines.append(raw)
        text = "\n".join(lines)
    elif "| 90 |" in text and plus_row not in text:
        lines = text.splitlines()
        out = []
        inserted = False
        for raw in lines:
            out.append(raw)
            if raw.startswith("| 90 |") and not inserted:
                out.append(plus_row)
                inserted = True
        text = "\n".join(out)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "就业栈别绑死生医",
        "staged_name": STAGED_NAME,
        "episode": 92,
        "expected_phrases": 16,
        "replaced_short": 0,
        "source_note": "topics-batch4.md #92 · 学习基线就业栈别绑死生医 · 云端 NEW",
        "hooks": "钩子：课题可以偏生医，就业栈别焊死在生医上。\n诊断：长期栈指向能换房间的能力，不是指向培养箱。\n例子：工入口别只留给体外诊断；实习只投生仪厂等于焊进实验室。\n收束：栈指向房间外面，人才能走出去。",
        "cover_lines": ("就业栈", "别绑死生医"),
        "avoid": "成片 14 双线 / Python 先扎实；成片 90 从课题抽可迁移能力；成片 15 抢测控生态位",
        "factory": "topics-batch4 #92",
        "broll": {
            "S02": ("B-别指向培养箱.mp4", frame_incubator),
            "S04": ("B-实习焊进实验室.mp4", frame_intern),
            "S06": ("B-夜读细胞手册.mp4", frame_handbook),
            "S08": ("B-房间不是城.mp4", frame_room_city),
            "S10": ("B-先报系统稳住.mp4", frame_answer),
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
    print("DOCS 92", staged, kit.zh_sec(dur), "ok", report.get("ok"))
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
    if "14-" in STAGED_NAME or "90-" in STAGED_NAME:
        raise SystemExit("refusing remake filename")
    ep = episode()
    report = ep.produce()
    staged = Path("/workspace/成片") / STAGED_NAME
    dur = kit.probe_dur(staged) if staged.exists() else float(report.get("chengpian_duration_s") or report["video"]["duration_s"])
    rewrite_docs(dur)
    patch_topics(dur)
    patch_delivery_new(dur)
    print("NEW 92", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
