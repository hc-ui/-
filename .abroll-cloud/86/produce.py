#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 86：成绩存盘。topics-batch4 #86。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/86/，成品中转 成片/86-成绩存盘.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不重拍成片 35 口播别报文件名。不重拍成片 64 循环出生地。
只打成绩先存盘才能过夜。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "成绩存盘"
STAGED_NAME = "86-成绩存盘.mp4"


def frame_vanish(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 关了就散")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0)) + dy),
        "成绩加完了",
        font=kit.font(54),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    win = kit.appear(t, 0.14, 0.22)
    if win > 0.04:
        y = 280 + int(kit.lerp(18, 0, win))
        kit.rounded(d, (130, y, 950, y + 520), 28, kit.mix(kit.BG, kit.CARD, win))
        kit.rounded(d, (130, y, 950, y + 72), 28, kit.mix(kit.CARD, (36, 30, 28), win))
        d.text((180, y + 36), "内存里的本", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, win), anchor="lm")
        close_a = kit.appear(t, 0.72, 0.20)
        kit.rounded(d, (850, y + 16, 922, y + 56), 12, kit.mix(kit.CARD, (58, 28, 24), win))
        d.text((886, y + 36), "关", font=kit.font(26), fill=kit.mix(kit.CARD, kit.RED, max(win, close_a)), anchor="mm")

        rows = [("甲", "92", 0.28), ("乙", "88", 0.40), ("丙", "95", 0.52)]
        gone = kit.appear(t, 0.95, 0.28)
        for idx, (who, score, ts) in enumerate(rows):
            a = kit.appear(t, ts, 0.18)
            if a < 0.04:
                continue
            yy = y + 110 + idx * 120
            fade = max(0.08, 1.0 - gone)
            kit.rounded(d, (190, yy, 890, yy + 100), 20, kit.mix(kit.CARD, (32, 28, 26), a * fade))
            ink = kit.mix(kit.CARD, kit.WHITE, a * fade)
            d.text((280, yy + 50), who, font=kit.font(40), fill=ink, anchor="mm")
            d.text((540, yy + 50), score, font=kit.font(44), fill=kit.mix(kit.CARD, kit.YELLOW, a * fade), anchor="mm")
            if gone > 0.2:
                kit.x_mark(d, 780, yy + 50, gone, 22)

    punch = kit.appear(t, 1.28, 0.22)
    if punch > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 220), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y3 + 70), "窗口一关就散", font=kit.font(48), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
        d.text((kit.W // 2, y3 + 150), "不是这一轮菜单清空", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, punch), anchor="mm")
        kit.x_mark(d, 200, y3 + 110, kit.appear(t, 1.45, 0.16), 24)
        kit.x_mark(d, 880, y3 + 110, kit.appear(t, 1.50, 0.16), 24)
    return img


def frame_write(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 退出先写")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "打开先读，退出先写",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    rows = [
        (0.16, "1", "打开先读", "下次先从盘上取回"),
        (0.40, "2", "用的时候改", "菜单里照常增和列"),
        (0.64, "3", "退出先写", "关之前先落到盘上"),
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
        d.text((kit.W // 2, y3 + 70), "盘上有本", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, punch), anchor="mm")
        d.text((kit.W // 2, y3 + 130), "关了还能回来", font=kit.font(50), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_compare(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对照 · 内存 / 盘")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "先问成绩落没落盘",
        font=kit.font(46),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 500), 32, kit.mix(kit.BG, (42, 24, 22), a1))
    d.text((285, y + 56), "内存里的本", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "关了", font=kit.font(64), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    d.text((285, y + 270), "就没了", font=kit.font(48), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    kit.x_mark(d, 285, y + 380, kit.appear(t, 0.55, 0.22), 36)

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (580, y, 1010, y + 500), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((795, y + 56), "盘上的本", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((795, y + 180), "关了", font=kit.font(64), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    d.text((795, y + 270), "还在", font=kit.font(48), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    kit.check_badge(d, 795, y + 380, kit.appear(t, 0.70, 0.22))

    stamp = kit.appear(t, 1.20, 0.24)
    if stamp > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, stamp)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), stamp))
        d.text((kit.W // 2, y3 + 70), "先存盘，再关程序", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, stamp), anchor="mm")
        d.text((kit.W // 2, y3 + 140), "没落盘等于没记下", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, stamp), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    """Episode 默认写成 86-long / 加长重切；本集是 NEW，改回 .abroll-cloud/86/。"""
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "86_成绩存盘"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/86"
        status["source_note"] = "topics-batch4.md #86 / 学习基线 2026-09-09 成绩存盘 / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "86_成绩存盘"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/86"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 86 · 成绩存盘

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：`topics-batch4.md` 第 86 条；学习基线 2026-09-09 文件读写（成绩存盘）
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/86/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：成片 35 口播别报文件名；成片 64 空字典出生地；成片 42 append；成片 74 菜单拆函数；成片 73 先包一层；异常整章；C++ / ROS2

钩子：成绩加完了，关程序就没了。
诊断：只活在内存里；窗口一关就散。不是这一轮菜单清空。
做法：退出前写到盘上；下次打开先读回来。
收束：落了盘再退出才能过夜；没存盘的成绩请当成会丢。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。口播和画面都不报文件名。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头九条，口播十八句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")
    (ROOT / "时长.md").write_text(
        f"""# 成片 86 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 工厂短切 | 新时长 | 草稿 |
|----|------|----------|--------|------|
| 86 | `{STAGED_NAME}` | 无（首拍） | {kit.zh_sec(duration)} | `.abroll-cloud/86/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。九镜 / 十八句。禁止 `tpad=stop_mode=clone`。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    verified = f"- **状态**：已核验 · `.abroll-cloud/86/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
    claimed = "- **状态**：已认领 · `.abroll-cloud/86/` · NEW · 目标四十到五十秒"
    heading = "## 86. 成绩存盘"
    if claimed in text:
        text = text.replace(claimed, verified)
    elif verified not in text and heading in text:
        text = text.replace(
            heading + "\n\n- **A-roll 角度**：",
            heading + f"\n\n{verified}\n- **A-roll 角度**：",
        )

    new_row = f"| 86 | 未完成 Python | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    claimed_row = "| 86 | 未完成 Python | `86-成绩存盘.mp4` | 已认领 `.abroll-cloud/86/` |"
    old_row = "| 86 | 未完成 Python | `86-成绩存盘.mp4` | 未拍 |"
    if old_row in text:
        text = text.replace(old_row, new_row)
    elif claimed_row in text:
        text = text.replace(claimed_row, new_row)
    elif "| 86 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 86 |") and "成绩存盘" in raw:
                lines.append(new_row)
            else:
                lines.append(raw)
        text = "\n".join(lines)
        if not text.endswith("\n"):
            text += "\n"
    elif "| 85 |" in text:
        lines = []
        inserted = False
        for raw in text.splitlines():
            lines.append(raw)
            if (not inserted) and raw.startswith("| 85 |"):
                lines.append(new_row)
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
        f"topic 86 `topics-batch4.md` 第 86 条；Drive 只读 `学习与职业规划基线.md`（2026-09-09：文件读写（成绩存盘））。"
        f"云端 NEW，不拷成片 35。 |"
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

    table_line = f"| 86 | `{STAGED_NAME}` | {kit.zh_sec(duration)} | 已核验 |"
    if "| 86 |" in text and STAGED_NAME in text:
        rows = []
        for raw in text.splitlines():
            if raw.startswith("| 86 |") and STAGED_NAME in raw:
                rows.append(table_line)
            else:
                rows.append(raw)
        text = "\n".join(rows)
    elif "## 本轮 61+（核验中）" in text:
        rows = []
        inserted = False
        for raw in text.splitlines():
            rows.append(raw)
            if (not inserted) and raw.startswith("| 73 |"):
                rows.append(table_line)
                inserted = True
        if not inserted:
            rows.append(table_line)
        text = "\n".join(rows)

    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "成绩加完了，关程序就没了。先存盘。",
        "staged_name": STAGED_NAME,
        "episode": 86,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "topics-batch4.md #86 · 学习基线 2026-09-09 成绩存盘 · 云端 NEW",
        "hooks": "钩子：成绩加完了，关程序就没了。\n诊断：只活在内存里；窗口一关就散。\n做法：退出前写到盘上；下次打开先读回来。\n收束：没存盘的成绩，请当成会丢。",
        "cover_lines": ("成绩存盘", "关了还能回来"),
        "avoid": "成片 35 口播别报文件名；成片 64 空字典；成片 42 append；成片 74 拆函数；成片 73 先包一层；异常整章；C++ / ROS2",
        "factory": "topics-batch4 #86",
        "broll": {
            "S02": ("B-关了就散.mp4", frame_vanish),
            "S04": ("B-退出先写.mp4", frame_write),
            "S06": ("B-内存对盘.mp4", frame_compare),
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
    print("DOCS 86", staged, kit.zh_sec(dur), "ok", report.get("ok"))
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
    print("NEW 86", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
