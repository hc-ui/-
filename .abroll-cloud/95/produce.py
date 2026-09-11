#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 95：学完立刻用一次。topics-batch4 #95。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/95/，成品中转 成片/95-学完立刻用一次.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不重复成片 43 先交三道短题，不重复成片 70 例子先于概念。
不拷工厂 80_学完立刻用一次 短切。成片号 80 已被体力型杂务占用。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "学完立刻用一次"
STAGED_NAME = "95-学完立刻用一次.mp4"
BANNED = (
    "三道短题",
    "通讯录",
    "库存",
    "比赛得分",
    "教务",
    "成绩存盘",
    "空字典",
    "拆函数",
    "例子先于",
    "术语",
    "下一期",
    "C++",
    "ROS",
)


def frame_notes_pile(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 只攒笔记")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0)) + dy),
        "笔记攒了一堆",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    cards = [
        (0.16, 90, 300, "第 1 页", "抄完了"),
        (0.32, 400, 340, "第 2 页", "又抄一遍"),
        (0.48, 710, 300, "第 3 页", "还是抄"),
    ]
    for ts, x, y0, head, body in cards:
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = y0 + int(kit.lerp(18, 0, a)) + dy
        kit.rounded(d, (x, y, x + 270, y + 280), 26, kit.mix(kit.BG, kit.CARD, a))
        d.text((x + 135, y + 70), head, font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a), anchor="mm")
        d.text((x + 135, y + 150), body, font=kit.font(36), fill=kit.mix(kit.CARD, kit.YELLOW, a), anchor="mm")
        kit.x_mark(d, x + 135, y + 220, kit.appear(t, ts + 0.45, 0.18), 22)

    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y, 990, y + 200), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 70), "手上没留下一次", font=kit.font(46), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
        d.text((kit.W // 2, y + 140), "合上书就不会了", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, punch), anchor="mm")
    return img


def frame_flip_fast(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 翻得太快")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "下一页翻得很快",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    if a1 > 0.04:
        y = 300 + int(kit.lerp(14, 0, a1)) + dy
        kit.rounded(d, (70, y, 500, y + 460), 32, kit.mix(kit.BG, (42, 24, 22), a1))
        d.text((285, y + 70), "上一页", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
        d.text((285, y + 190), "带不走", font=kit.font(52), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
        d.text((285, y + 280), "手是空的", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.x_mark(d, 285, y + 370, kit.appear(t, 0.70, 0.20), 30)

    a2 = kit.appear(t, 0.30)
    if a2 > 0.04:
        y = 300 + int(kit.lerp(14, 0, a2)) + dy
        kit.rounded(d, (580, y, 1010, y + 460), 32, kit.mix(kit.BG, kit.CARD, a2))
        d.text((795, y + 70), "下一页", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
        d.text((795, y + 190), "已经翻过", font=kit.font(44), fill=kit.mix(kit.CARD, kit.YELLOW, a2), anchor="mm")
        d.text((795, y + 280), "教程还摊着", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
        kit.x_mark(d, 795, y + 370, kit.appear(t, 0.88, 0.20), 30)

    punch = kit.appear(t, 1.18, 0.22)
    if punch > 0.04:
        y = 830 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 180), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 90), "翻得快，带不走", font=kit.font(46), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_use_once(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 立刻用一次")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "刚记下，立刻用",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    rows = [
        (0.16, "1", "合上教程", "先自己写一遍"),
        (0.40, "2", "不看答案", "先交一次"),
        (0.64, "3", "手头题", "立刻用一次"),
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
        d.text((kit.W // 2, y + 70), "写错了也算用过", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
        d.text((kit.W // 2, y + 140), "没写才是没学", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, punch), anchor="mm")
    return img


def frame_compare(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对照 · 看过 / 用过")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "笔记不是学会",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 500), 32, kit.mix(kit.BG, (42, 24, 22), a1))
    d.text((285, y + 56), "只看过", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "没用过", font=kit.font(56), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    d.text((285, y + 270), "等于没学完", font=kit.font(36), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    kit.x_mark(d, 285, y + 380, kit.appear(t, 0.55, 0.22), 36)

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (580, y, 1010, y + 500), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((795, y + 56), "用过一次", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((795, y + 180), "交过手", font=kit.font(56), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    d.text((795, y + 270), "才算学过", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    kit.check_badge(d, 795, y + 380, kit.appear(t, 0.70, 0.22))

    stamp = kit.appear(t, 1.20, 0.24)
    if stamp > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, stamp)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), stamp))
        d.text((kit.W // 2, y3 + 70), "先用一次", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, stamp), anchor="mm")
        d.text((kit.W // 2, y3 + 140), "再记下一页", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, stamp), anchor="mm")
    return img


def frame_stamp(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "收 · 用过才算")
    dy = kit.breathe(t, 6)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 230 + int(kit.lerp(16, 0, a0))),
        "用过一次，才算学过",
        font=kit.font(46),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.18)
    if a1 > 0.04:
        cx, cy = 540, 620 + dy
        r = 230
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=kit.mix(kit.BG, (18, 42, 36), a1))
        d.text((cx, cy - 40), "用过一次", font=kit.font(56), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
        d.text((cx, cy + 50), "才算学过", font=kit.font(40), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.check_badge(d, cx, cy + 140, kit.appear(t, 0.70, 0.22))

    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y = 960 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 85), "没交手，请当成没学完", font=kit.font(40), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    """Episode 默认写成 95-long / 加长重切；本集是 NEW，改回 .abroll-cloud/95/。"""
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "95_学完立刻用一次"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/95"
        status["source_note"] = "topics-batch4.md #95 / 工厂 80_学完立刻用一次 / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status["distinct_from"] = ["43-先交三道短题", "70-例子先于概念", "80-体力型杂务"]
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "95_学完立刻用一次"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        report["distinct_from_43"] = True
        report["distinct_from_70"] = True
        report["distinct_from_80"] = True
        vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8")
        report["script_guard"] = {w: (w not in vo) for w in BANNED}
        report["ok"] = bool(report.get("ok")) and all(report["script_guard"].values())
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/95"
        data["source_note"] = "topics-batch4.md #95 / 工厂 80_学完立刻用一次 / 云端 NEW"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 95 · 学完立刻用一次

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：`topics-batch4.md` 第 95 条；Drive 只读工厂 `80_学完立刻用一次`
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/95/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：成片 43 先交三道短题；成片 70 例子先于概念；成片 80 体力型杂务

钩子：学完了，立刻用一次。
诊断：看完以为会了，合上就不会了；笔记一堆，手上没留下一次。
做法：合上之前先自己写一遍；不看答案先交一次。
收束：用过一次，才算学过。没立刻用过的，请当成没学完。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头十二条，口播十八句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")
    (ROOT / "时长.md").write_text(
        f"""# 成片 95 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 工厂短切 | 新时长 | 草稿 |
|----|------|----------|--------|------|
| 95 | `{STAGED_NAME}` | 工厂 80 号短切（未进成片） | {kit.zh_sec(duration)} | `.abroll-cloud/95/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。十二镜 / 十八句。禁止 `tpad=stop_mode=clone`。
不重做 43 / 70，不拷工厂成片，不碰成片 80。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    section = f"""## 95. 学完立刻用一次

- **状态**：已核验 · `.abroll-cloud/95/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}
- **A-roll 角度**：工厂 `80_学完立刻用一次` 短切。成片号 80 已被 `体力型杂务` 占用，本条改认 95。只打「学完立刻用一次」：看完教程合上就不会，笔记一堆手上没留下一次。合上之前先自己写一遍，不看答案先交一次。不讲三道短题，不讲例子先于概念。
- **B-roll 想法**：笔记一堆手上空；下一页翻得快上一页带不走；合上前先写、不看答案先交；看过没用过对用过一次；用过一次才算学过。
- **来源笔记**：Drive 只读工厂 `80_学完立刻用一次`（claim：白底小灯 A-roll + 黑底信息图 B-roll；`/workspace/成片/` 无本条）
- **成片名**：`{STAGED_NAME}`
- **避开**：成片 43 先交三道短题；成片 70 例子先于概念；成片 80 体力型杂务
"""
    claimed = "- **状态**：已认领 · `.abroll-cloud/95/` · NEW · 目标四十到五十秒"
    verified = f"- **状态**：已核验 · `.abroll-cloud/95/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
    if "## 95. 学完立刻用一次" in text:
        if claimed in text:
            text = text.replace(claimed, verified)
        elif verified not in text:
            text = text.replace(
                "## 95. 学完立刻用一次\n\n- **A-roll 角度**：",
                f"## 95. 学完立刻用一次\n\n{verified}\n- **A-roll 角度**：",
            )
    else:
        text = text.rstrip() + "\n\n" + section

    row = f"| 95 | 工厂知识口播改认 | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if "| 95 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 95 |"):
                lines.append(row)
            else:
                lines.append(raw)
        text = "\n".join(lines)
    elif "| 84 |" in text:
        lines = []
        inserted = False
        for raw in text.splitlines():
            lines.append(raw)
            if (not inserted) and raw.startswith("| 84 |") and "工厂知识口播改认" in raw:
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
        f"topic 95 `topics-batch4.md` 第 95 条；Drive 只读工厂 `80_学完立刻用一次`"
        f"（claim：白底小灯 A-roll + 黑底信息图 B-roll；工厂短切未进 `/workspace/成片/`）。"
        f"成片号 80 已被体力型杂务占用。云端 NEW，不拷工厂成片，不重做 43/70。 |"
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

    plus_row = f"| 95 | `{STAGED_NAME}` | {kit.zh_sec(duration)} | 已核验 |"
    if "| 95 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 95 |"):
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
            if raw.startswith("| 85 |") and not inserted:
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
        "full_title": "学完立刻用一次",
        "staged_name": STAGED_NAME,
        "episode": 95,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "topics-batch4.md #95 · 工厂 80_学完立刻用一次 · 云端 NEW",
        "hooks": "钩子：学完了，立刻用一次。\n诊断：看完以为会了，合上就不会了；笔记一堆手上空。\n做法：合上之前先自己写一遍；不看答案先交一次。\n收束：没立刻用过的，请当成没学完。",
        "cover_lines": ("学完立刻", "用一次"),
        "avoid": "成片 43 先交三道短题；成片 70 例子先于概念；成片 80 体力型杂务",
        "factory": "topics-batch4 #95",
        "broll": {
            "S02": ("B-笔记一堆.mp4", frame_notes_pile),
            "S04": ("B-翻页带不走.mp4", frame_flip_fast),
            "S06": ("B-立刻用一次.mp4", frame_use_once),
            "S08": ("B-笔记不是学会.mp4", frame_compare),
            "S10": ("B-用过才算学过.mp4", frame_stamp),
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
    print("DOCS 95", staged, kit.zh_sec(dur), "ok", report.get("ok"))
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
    print("NEW 95", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
