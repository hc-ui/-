#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 73：int-input先包一层。topics-batch4 #73。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/73/，成品中转 成片/73-int-input先包一层.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不重复成片 64 空字典出生地。只打生输入直接转整数这一个炸点。
"""
from __future__ import annotations

import json
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "int-input先包一层"
STAGED_NAME = "73-int-input先包一层.mp4"


def frame_explode(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 一敲就炸")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0)) + dy),
        "键盘敲「甲」",
        font=kit.font(54),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    keys = [("7", 0.12), ("8", 0.16), ("9", 0.20), ("甲", 0.28), ("0", 0.22), ("退", 0.26)]
    press = kit.appear(t, 0.55, 0.28)
    for idx, (label, ts) in enumerate(keys):
        a = kit.appear(t, ts, 0.18)
        if a < 0.04:
            continue
        col = idx % 3
        row = idx // 3
        x = 160 + col * 260
        y = 300 + row * 170 + int(kit.lerp(14, 0, a))
        hot = label == "甲"
        sink = int(10 * press) if hot else 0
        fill = kit.mix(kit.CARD, (58, 28, 24) if hot else kit.CARD, a)
        kit.rounded(d, (x, y + sink, x + 220, y + 140 + sink), 22, kit.mix(kit.BG, fill, a))
        color = kit.YELLOW if hot else kit.WHITE
        d.text((x + 110, y + 70 + sink), label, font=kit.font(48 if hot else 40), fill=kit.mix(kit.CARD, color, a), anchor="mm")

    a1 = kit.appear(t, 0.70, 0.24)
    if a1 > 0.04:
        y = 680 + int(kit.lerp(18, 0, a1)) + dy
        kit.rounded(d, (140, y, 940, y + 240), 28, kit.mix(kit.BG, (42, 24, 22), a1))
        d.text((kit.W // 2, y + 70), "喂进整数转换", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
        d.text((kit.W // 2, y + 160), "当场炸掉", font=kit.font(56), fill=kit.mix(kit.BG, kit.RED, a1), anchor="mm")
        kit.x_mark(d, 200, y + 120, kit.appear(t, 0.95, 0.18), 26)
        kit.x_mark(d, 880, y + 120, kit.appear(t, 1.00, 0.18), 26)

    punch = kit.appear(t, 1.25, 0.22)
    if punch > 0.04:
        y3 = 980 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 170), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y3 + 85), "空串和字母都会炸", font=kit.font(42), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_wrap(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 先包一层")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "先把输入包住",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    rows = [
        (0.16, "1", "先收字", "先收下字符串"),
        (0.40, "2", "再认数字", "认出来才往下"),
        (0.64, "3", "认不出重问", "别让程序死掉"),
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

    punch = kit.appear(t, 1.30, 0.24)
    if punch > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y3, 990, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 70), "认出来了", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, punch), anchor="mm")
        d.text((kit.W // 2, y3 + 130), "再交给菜单", font=kit.font(50), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_case_pass(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 过关再进")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "选项一只吃过关数字",
        font=kit.font(46),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 440), 32, kit.mix(kit.BG, (42, 24, 22), a1))
    d.text((285, y + 56), "没过关", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "甲", font=kit.font(72), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    kit.x_mark(d, 285, y + 300, kit.appear(t, 0.55, 0.22), 36)
    d.text((285, y + 390), "不准进分支", font=kit.font(28), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (540, y, 1010, y + 440), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((775, y + 56), "过关后", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((775, y + 180), "1", font=kit.font(72), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    kit.check_badge(d, 775, y + 300, kit.appear(t, 0.70, 0.22))
    d.text((775, y + 390), "再进选项一", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")

    stamp = kit.appear(t, 1.20, 0.24)
    if stamp > 0.04:
        y3 = 820 + int(kit.lerp(16, 0, stamp)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), stamp))
        d.text((kit.W // 2, y3 + 70), "先包一层，再当选项", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, stamp), anchor="mm")
        d.text((kit.W // 2, y3 + 140), "没过关不准进分支", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, stamp), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    """Episode 默认写成 73-long / 加长重切；本集是 NEW，改回 .abroll-cloud/73/。"""
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "73_int-input先包一层"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/73"
        status["source_note"] = "topics-batch4.md #73 / 学习基线 2026-09-09 不足第7条 / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "73_int-input先包一层"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/73"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 73 · int-input先包一层

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：`topics-batch4.md` 第 73 条；学习基线 2026-09-09 不足第 7 条
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/73/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：成片 64 空字典出生地；成片 42 append；成片 13 靠名字；#74 菜单拆函数；异常整章；C++ / ROS2

钩子：整数转换套输入会炸，先包一层。
诊断：生输入直接转整数；敲「甲」当场炸。
做法：先收字，再认数字；认不出就重问。
收束：过关后再进选项；没包一层的输入，请当成会炸。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头九条，口播十八句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")
    (ROOT / "时长.md").write_text(
        f"""# 成片 73 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 工厂短切 | 新时长 | 草稿 |
|----|------|----------|--------|------|
| 73 | `{STAGED_NAME}` | 无（首拍） | {kit.zh_sec(duration)} | `.abroll-cloud/73/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。九镜 / 十八句。禁止 `tpad=stop_mode=clone`。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    new_row = f"| 73 | 未完成 Python | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    claimed_row = "| 73 | 未完成 Python | `73-int-input先包一层.mp4` | 已认领 `.abroll-cloud/73/` |"
    old_row = "| 73 | 未完成 Python | `73-int-input会炸先包一层.mp4` | 未拍 |"
    if old_row in text:
        text = text.replace(old_row, new_row)
    elif claimed_row in text:
        text = text.replace(claimed_row, new_row)
    elif "| 73 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 73 |"):
                lines.append(new_row)
            else:
                lines.append(raw)
        text = "\n".join(lines)
        if not text.endswith("\n"):
            text += "\n"
    else:
        needle = "| 70 | 工厂知识口播 | `70-例子先于概念.mp4` | 未拍 |"
        if needle in text:
            text = text.replace(needle, needle + "\n" + new_row, 1)

    claimed = "- **状态**：已认领 · `.abroll-cloud/73/` · NEW · 目标四十到五十秒"
    verified = f"- **状态**：已核验 · `.abroll-cloud/73/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
    if claimed in text:
        text = text.replace(claimed, verified)
    elif "## 73. int(input) 会炸，先包一层" in text and verified not in text:
        text = text.replace(
            "## 73. int(input) 会炸，先包一层\n\n- **A-roll 角度**：",
            f"## 73. int(input) 会炸，先包一层\n\n{verified}\n- **A-roll 角度**：",
        )
    elif "## 73. int(input) 会炸，先包一层" not in text:
        section = f"""
## 73. int(input) 会炸，先包一层

{verified}
- **A-roll 角度**：未完成 Python。不足第 7 条：`int(input())` 遇到非数字会直接炸。空字典已进成片 64，本条不重拍容器出生地。先把输入包住，再拿去当选项。异常整章还没开始，只打这一个炸点。
- **成片名建议**：`{STAGED_NAME}`

"""
        marker = "## 对照备忘"
        if marker in text:
            text = text.replace(marker, section + marker, 1)
        else:
            text = text.rstrip() + "\n" + section
    path.write_text(text, encoding="utf-8")


def patch_delivery_new(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    new = (
        f"| `成片/{STAGED_NAME}` | 1080×1920 h264+aac 44.1k stereo | {kit.zh_sec(duration)} | "
        f"topic 73 `topics-batch4.md` 第 73 条；学习基线 2026-09-09 不足第 7 条。云端 NEW，不拷短切。 |"
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
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "整数转换套输入会炸，先包一层",
        "staged_name": STAGED_NAME,
        "episode": 73,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "topics-batch4.md #73 · 学习基线 2026-09-09 不足第7条 · 云端 NEW",
        "hooks": "钩子：整数转换套输入会炸，先包一层。\n诊断：生输入直接转整数；敲甲当场炸。\n做法：先收字，再认数字；认不出就重问。\n收束：没包一层的输入，请当成会炸。",
        "cover_lines": ("int 会炸", "先包一层"),
        "avoid": "成片 64 空字典；成片 42 append；成片 13 靠名字；#74 菜单拆函数；异常整章；C++ / ROS2",
        "factory": "topics-batch4 #73",
        "broll": {
            "S02": ("B-敲甲就炸.mp4", frame_explode),
            "S04": ("B-先包一层.mp4", frame_wrap),
            "S06": ("B-过关再进.mp4", frame_case_pass),
        },
    })


def finish_docs() -> None:
    """Write QA/docs from the already-staged cut. Does not re-render."""
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
    print("DOCS 73", staged, kit.zh_sec(dur), "ok", report.get("ok"))
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


def main() -> None:
    if "--docs-only" in sys.argv:
        finish_docs()
        return
    ep = episode()
    report = ep.produce()
    staged = Path("/workspace/成片") / STAGED_NAME
    dur = kit.probe_dur(staged) if staged.exists() else float(report.get("chengpian_duration_s") or report["video"]["duration_s"])
    rewrite_docs(dur)
    patch_topics(dur)
    patch_delivery_new(dur)
    print("NEW 73", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
