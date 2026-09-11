#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 88：学术放养工位收紧。topics-batch4 #88。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/88/，成品中转 成片/88-学术放养工位收紧.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不重复成片 16 时间切片、79 组会工坊、80 体力杂务、81 请假两方案。
"""
from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "学术放养工位收紧"
STAGED_NAME = "88-学术放养工位收紧.mp4"
WORKSPACE_DRAFT = Path("/workspace/.abroll-cloud/88")
BANNED = [
    "下一期", "赵老师", "十五十五七十", "秒回", "只报做完",
    "报销", "六十分", "评优", "租金", "脱产", "实习",
    "假条", "工期大饼", "攻坚工坊", "先摸惯例",
]


def frame_hands_off(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 他不下场")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0)) + dy),
        "题怎么推，他很少下场",
        font=kit.font(46),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    cards = [
        (0.16, 70, "算法推导", "不改"),
        (0.36, 560, "控制回路", "不盯"),
    ]
    for ts, x, head, body in cards:
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 340 + int(kit.lerp(18, 0, a)) + dy
        kit.rounded(d, (x, y, x + 450, y + 420), 32, kit.mix(kit.BG, kit.CARD, a))
        d.text((x + 225, y + 90), head, font=kit.font(40), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="mm")
        d.text((x + 225, y + 190), body, font=kit.font(64), fill=kit.mix(kit.CARD, kit.RED, a), anchor="mm")
        kit.x_mark(d, x + 225, y + 300, kit.appear(t, ts + 0.28, 0.18), 36)
    punch = kit.appear(t, 1.20, 0.22)
    if punch > 0.04:
        y = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 170), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 85), "细节自己消化", font=kit.font(50), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_empty_chair(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 人在才算")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "放养不是没人管",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.16)
    y = 320 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 510, y + 520), 32, kit.mix(kit.BG, (42, 24, 22), a1))
    d.text((290, y + 56), "空椅子", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    cx, cy = 290, y + 230
    d.rectangle((cx - 70, cy + 40, cx + 70, cy + 150), fill=kit.mix(kit.CARD, (48, 28, 24), a1))
    d.rectangle((cx - 110, cy - 10, cx + 110, cy + 50), fill=kit.mix(kit.CARD, (62, 36, 30), a1))
    d.text((cx, cy + 95), "空", font=kit.font(48), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    kit.x_mark(d, cx, y + 430, kit.appear(t, 0.55, 0.18), 34)
    d.text((290, y + 480), "才是大事", font=kit.font(28), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (540, y, 1010, y + 520), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((775, y + 56), "题怎么推", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((775, y + 200), "放养", font=kit.font(64), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    d.text((775, y + 300), "不等于失踪", font=kit.font(36), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
    kit.check_badge(d, 775, y + 400, kit.appear(t, 0.80, 0.18))

    punch = kit.appear(t, 1.20, 0.22)
    if punch > 0.04:
        y3 = 900 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 170), 28, kit.mix(kit.BG, (42, 32, 16), punch))
        d.text((kit.W // 2, y3 + 85), "椅子空着才报警", font=kit.font(48), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_random_cal(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 通知说不准")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "周末也可能叫人",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.14)
    y = 320 + int(kit.lerp(16, 0, a1))
    kit.rounded(d, (90, y, 990, y + 520), 32, kit.mix(kit.BG, kit.CARD, a1))
    days = ["一", "二", "三", "四", "五", "六", "日"]
    for i, lab in enumerate(days):
        x = 140 + i * 120
        hot = lab in ("六", "日")
        aa = kit.appear(t, 0.22 + i * 0.06, 0.16)
        fill = kit.mix(kit.CARD, (56, 28, 24) if hot else (28, 32, 40), aa)
        kit.rounded(d, (x, y + 70, x + 100, y + 200), 16, fill)
        d.text((x + 50, y + 135), lab, font=kit.font(40), fill=kit.mix(kit.CARD, kit.RED if hot else kit.WHITE, aa), anchor="mm")
    stamp = kit.appear(t, 0.70, 0.22)
    if stamp > 0.04:
        d.text((kit.W // 2, y + 280), "假日前夕", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MUTED, stamp), anchor="mm")
        bolt = 0.55 + 0.45 * abs(math.sin(t * 3.2))
        kit.rounded(d, (280, y + 330, 800, y + 460), 24, kit.mix(kit.CARD, (56, 36, 16), stamp))
        d.text((kit.W // 2, y + 395), "临时会 · 说开就开", font=kit.font(40), fill=kit.mix(kit.CARD, kit.YELLOW, stamp * bolt), anchor="mm")
    punch = kit.appear(t, 1.20, 0.22)
    if punch > 0.04:
        y3 = 900 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 170), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y3 + 85), "通知没有日历", font=kit.font(50), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_balloons(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 宏观比喻")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "比喻听完就散",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    labels = [(0.16, 220, "宏观"), (0.34, 540, "规划"), (0.52, 820, "比喻")]
    for ts, x, lab in labels:
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        lift = int(kit.lerp(40, -10, a)) - int(28 * (t - ts) * a)
        cy = 520 + lift + dy
        r = 110
        d.ellipse((x - r, cy - r, x + r, cy + r), fill=kit.mix(kit.BG, (42, 36, 22), a))
        d.text((x, cy), lab, font=kit.font(40), fill=kit.mix(kit.CARD, kit.YELLOW, a), anchor="mm")
        d.line([(x, cy + r - 8), (x, cy + r + 70)], fill=kit.mix(kit.CARD, kit.MUTED, a), width=6)
    punch = kit.appear(t, 1.10, 0.22)
    if punch > 0.04:
        y = 900 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (140, y, 940, y + 170), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 85), "听完就飘走", font=kit.font(50), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_contract(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "收 · 职业契约")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "契约摆正就行",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.16)
    y = 320 + int(kit.lerp(16, 0, a1))
    kit.rounded(d, (70, y, 510, y + 420), 32, kit.mix(kit.BG, (22, 40, 36), a1))
    d.text((290, y + 70), "学术", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((290, y + 180), "放养", font=kit.font(64), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
    d.text((290, y + 280), "题自己啃", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
    kit.check_badge(d, 290, y + 350, kit.appear(t, 0.70, 0.18))

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (570, y, 1010, y + 420), 32, kit.mix(kit.BG, (42, 32, 16), a2))
    d.text((790, y + 70), "工位", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((790, y + 180), "收紧", font=kit.font(64), fill=kit.mix(kit.CARD, kit.YELLOW, a2), anchor="mm")
    d.text((790, y + 280), "人要坐住", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
    kit.check_badge(d, 790, y + 350, kit.appear(t, 0.82, 0.18))

    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y3 = 820 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 100), "别等指引和托底", font=kit.font(48), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "88_学术放养工位收紧"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/88"
        status["source_note"] = "topics-batch4.md #88 / 备忘录第一节2 学术放养工位收紧 / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "88_学术放养工位收紧"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8")
        report["script_guard"] = {w: (w not in vo) for w in BANNED}
        report["ok"] = bool(report.get("ok")) and all(report["script_guard"].values())
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/88"
        data["source_note"] = "topics-batch4.md #88 / 备忘录第一节2 学术放养工位收紧 / 云端 NEW"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 88 · 学术放养工位收紧

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：`topics-batch4.md` 第 88 条；Drive 只读备忘录第一节 2「学术放养，工位收紧」
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/88/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：成片 16 时间切片；成片 14 技术栈自己建；#79 组会不是攻坚工坊；#80 体力型杂务；#81 请假带两方案；成片 47/48 实习
- **时长**：{kit.zh_sec(duration)}（目标四十到五十秒）

钩子：学术放养，工位收紧。  
诊断：题怎么推他很少下场；椅子空着才是大事。  
例子：周末和假日前夕都可能临时叫人；宏观比喻听完就散。  
收束：职业契约摆正。人坐住，题自己啃。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。不念真名。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头十二条，口播十七句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")
    (ROOT / "时长.md").write_text(
        f"""# 成片 88 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 工厂短切 | 新时长 | 草稿 |
|----|------|----------|--------|------|
| 88 | `{STAGED_NAME}` | 无（本号未进成片） | {kit.zh_sec(duration)} | `.abroll-cloud/88/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。十二镜 / 十七句。禁止 `tpad=stop_mode=clone`。
不重做 16（时间切片）、79（组会工坊）、80（体力杂务）、81（请假两方案）。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    claimed = "- **状态**：已认领 · `.abroll-cloud/88/` · `成片/88-学术放养工位收紧.mp4` · NEW · 目标四十到五十秒"
    verified = f"- **状态**：已核验 · `.abroll-cloud/88/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
    if claimed in text:
        text = text.replace(claimed, verified)
    elif verified.split(" · ")[0] in text and f"`成片/{STAGED_NAME}`" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("- **状态**") and "`.abroll-cloud/88/`" in raw:
                lines.append(verified)
            else:
                lines.append(raw)
        text = "\n".join(lines)
        if not text.endswith("\n"):
            text += "\n"
    claimed_row = "| 88 | 专硕导师双轨 | `88-学术放养工位收紧.mp4` | 已认领 `.abroll-cloud/88/` |"
    new_row = f"| 88 | 专硕导师双轨 | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if claimed_row in text:
        text = text.replace(claimed_row, new_row)
    elif "| 88 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 88 |"):
                lines.append(new_row)
            else:
                lines.append(raw)
        text = "\n".join(lines)
        if not text.endswith("\n"):
            text += "\n"
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def patch_delivery_new(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    row = (
        f"| `成片/{STAGED_NAME}` | 1080×1920 h264+aac 44.1k stereo | {kit.zh_sec(duration)} | "
        f"topic 88 `topics-batch4.md` 第 88 条；Drive 只读备忘录第一节 2「学术放养，工位收紧」。云端 NEW |"
    )
    token = f"`成片/{STAGED_NAME}`"
    if token in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("|") and token in raw:
                lines.append(row)
            else:
                lines.append(raw)
        text = "\n".join(lines)
    else:
        lines = text.splitlines()
        rebuilt = []
        inserted = False
        for raw in lines:
            if (not inserted) and "仙侠云海突进" in raw and raw.strip().startswith("|"):
                rebuilt.append(row)
                inserted = True
            rebuilt.append(raw)
        if not inserted:
            rebuilt.append(row)
        text = "\n".join(rebuilt)
    plus_row = f"| 88 | `{STAGED_NAME}` | {kit.zh_sec(duration)} | 已核验 |"
    if "| 88 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 88 |"):
                lines.append(plus_row)
            else:
                lines.append(raw)
        text = "\n".join(lines)
    elif plus_row not in text:
        lines = text.splitlines()
        out = []
        inserted = False
        for raw in lines:
            out.append(raw)
            if raw.startswith("| 73 |") and not inserted:
                out.append(plus_row)
                inserted = True
        if not inserted:
            out.append(plus_row)
        text = "\n".join(out)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def sync_workspace_draft() -> None:
    if ROOT.resolve() == WORKSPACE_DRAFT.resolve():
        return
    WORKSPACE_DRAFT.mkdir(parents=True, exist_ok=True)
    skip = {"__pycache__"}
    for src in ROOT.rglob("*"):
        if src.is_dir() or any(p in skip for p in src.parts):
            continue
        rel = src.relative_to(ROOT)
        dest = WORKSPACE_DRAFT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "学术放养工位收紧",
        "staged_name": STAGED_NAME,
        "episode": 88,
        "expected_phrases": 17,
        "replaced_short": 0,
        "source_note": "topics-batch4.md #88 / 备忘录第一节2 学术放养工位收紧 / 云端 NEW",
        "hooks": "钩子：学术放养，工位收紧。\n诊断：题怎么推他很少下场；空椅子才是大事。\n例子：周末和假日前夕都可能临时叫。\n收束：职业契约摆正；人坐住，题自己啃。",
        "cover_lines": ("学术放养", "工位收紧"),
        "avoid": "成片 16 时间切片；成片 14 技术栈自己建；#79 组会工坊；#80 体力杂务；#81 请假两方案",
        "factory": "topics-batch4 #88",
        "broll": {
            "S02": ("B-他不下场.mp4", frame_hands_off),
            "S04": ("B-空椅大事.mp4", frame_empty_chair),
            "S06": ("B-临时会.mp4", frame_random_cal),
            "S08": ("B-比喻散掉.mp4", frame_balloons),
            "S10": ("B-职业契约.mp4", frame_contract),
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
    report = ep.qa(staged, data)
    report["chengpian"] = str(staged)
    report["chengpian_duration_s"] = dur
    report["chengpian_duration_zh"] = kit.zh_sec(dur)
    report["draft_duration_s"] = draft_dur
    report["draft_duration_zh"] = kit.zh_sec(draft_dur)
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8")
    report["script_guard"] = {w: (w not in vo) for w in BANNED}
    report["ok"] = bool(report.get("ok")) and all(report["script_guard"].values())
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rewrite_docs(dur)
    patch_topics(dur)
    patch_delivery_new(dur)
    sync_workspace_draft()
    print("DOCS 88", staged, kit.zh_sec(dur), "ok", report.get("ok"))
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


def main() -> None:
    if "--docs-only" in sys.argv:
        finish_docs()
        return
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8")
    hit = [w for w in BANNED if w in vo]
    if hit:
        raise SystemExit(f"banned words in VO: {hit}")
    ep = episode()
    report = ep.produce()
    staged = Path("/workspace/成片") / STAGED_NAME
    dur = kit.probe_dur(staged) if staged.exists() else float(report.get("chengpian_duration_s") or report["video"]["duration_s"])
    rewrite_docs(dur)
    patch_topics(dur)
    patch_delivery_new(dur)
    sync_workspace_draft()
    print("NEW 88", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
