#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 79：组会不是攻坚工坊。topics-batch4 #79。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/79/，成品中转 成片/79-组会不是攻坚工坊.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不重复成片 37 撞课 SOP、49 文献精读、16 只报做完。
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "组会不是攻坚工坊"
STAGED_NAME = "79-组会不是攻坚工坊.mp4"


def frame_not_workshop(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 当辅导课")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0)) + dy),
        "组会桌对考勤名单",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.14)
    y = 300 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 380), 32, kit.mix(kit.BG, kit.CARD, a1))
    d.text((285, y + 48), "组会桌", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    kit.rounded(d, (130, y + 90, 440, y + 230), 18, kit.mix(kit.CARD, (36, 40, 52), a1))
    d.ellipse((170, y + 250, 230, y + 310), outline=kit.mix(kit.CARD, kit.YELLOW, a1), width=6)
    d.ellipse((340, y + 250, 400, y + 310), outline=kit.mix(kit.CARD, kit.YELLOW, a1), width=6)
    d.text((285, y + 340), "秩序会", font=kit.font(36), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")

    a2 = kit.appear(t, 0.22)
    kit.rounded(d, (540, y, 1010, y + 380), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((775, y + 48), "考勤名单", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    for i, name in enumerate(("在", "在", "缺")):
        yy = y + 100 + i * 70
        d.text((640, yy), f"0{i + 1}", font=kit.font(28), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="lm")
        if i < 2:
            kit.check_badge(d, 900, yy, kit.appear(t, 0.50 + i * 0.12, 0.16))
        else:
            kit.x_mark(d, 900, yy, kit.appear(t, 0.74, 0.16), 22)

    a3 = kit.appear(t, 0.55)
    if a3 > 0.04:
        y2 = 720 + int(kit.lerp(16, 0, a3))
        kit.rounded(d, (90, y2, 990, y2 + 160), 26, kit.mix(kit.BG, (42, 24, 22), a3))
        d.text((kit.W // 2, y2 + 50), "技术辅导课", font=kit.font(44), fill=kit.mix(kit.CARD, kit.RED, a3), anchor="mm")
        kit.strike_box(d, (220, y2 + 20, 860, y2 + 90), kit.appear(t, 0.78, 0.28), kit.mix(kit.CARD, kit.RED, 1))
        d.text((kit.W // 2, y2 + 118), "不是手把手改算法", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a3), anchor="mm")

    for i, word in enumerate(("宏观", "比喻", "说教")):
        rise = kit.appear(t, 0.70 + i * 0.10, 0.35)
        if rise <= 0.04:
            continue
        bx = 180 + i * 280
        by = 980 - int(70 * rise) + int(8 * math.sin(t * 2 + i))
        d.ellipse((bx - 70, by - 70, bx + 70, by + 70), fill=kit.mix(kit.BG, (48, 36, 22), rise))
        d.text((bx, by), word, font=kit.font(30), fill=kit.mix(kit.CARD, kit.YELLOW, rise), anchor="mm")

    punch = kit.appear(t, 1.20, 0.24)
    if punch > 0.04:
        y3 = 1180 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 160), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y3 + 80), "说教会飘走", font=kit.font(48), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_three_metrics(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 三条表现")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "不看谁讲得更炫",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (90, y, 990, y + 200), 28, kit.mix(kit.BG, (42, 24, 22), a1))
    d.text((kit.W // 2, y + 70), "攻坚工坊", font=kit.font(52), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    kit.x_mark(d, 860, y + 100, kit.appear(t, 0.40, 0.20), 36)
    kit.strike_box(d, (220, y + 40, 860, y + 110), kit.appear(t, 0.46, 0.28), kit.mix(kit.CARD, kit.RED, 1))
    d.text((kit.W // 2, y + 150), "空等手把手", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")

    rows = [
        (0.36, "1", "按时交付", "交得出才算过", kit.MINT),
        (0.58, "2", "态度严谨", "不靠讲得炫", kit.YELLOW),
        (0.80, "3", "合规合矩", "名单对得上", (92, 176, 214)),
    ]
    for idx, (ts, num, head, body, color) in enumerate(rows):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        yy = 540 + idx * 168 + int(kit.lerp(16, 0, a))
        kit.rounded(d, (90, yy, 990, yy + 148), 26, kit.mix(kit.BG, kit.CARD, a))
        d.ellipse((128, yy + 34, 220, yy + 126), fill=kit.mix(kit.CARD, color, a))
        d.text((174, yy + 80), num, font=kit.font(36), fill=kit.mix(color, kit.INK, a), anchor="mm")
        d.text((248, yy + 50), head, font=kit.font(40), fill=kit.mix(kit.CARD, color, a), anchor="lm")
        d.text((248, yy + 108), body, font=kit.font(28), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        kit.check_badge(d, 900, yy + 74, kit.appear(t, ts + 0.28, 0.18))

    punch = kit.appear(t, 1.35, 0.24)
    if punch > 0.04:
        y3 = 1080 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y3, 990, y3 + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 85), "按时交付打勾", font=kit.font(48), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_three_steps(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "收 · 秩序会")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "听完任务就记下",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    rows = [
        (0.16, "1", "认清秩序会", "不是辅导课"),
        (0.40, "2", "会前对齐交付", "对齐能交什么"),
        (0.64, "3", "听完就记下", "任务接得住"),
    ]
    for idx, (ts, num, head, body) in enumerate(rows):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 310 + idx * 168 + int(kit.lerp(16, 0, a))
        kit.rounded(d, (90, y, 990, y + 148), 26, kit.mix(kit.BG, kit.CARD, a))
        d.ellipse((128, y + 34, 220, y + 126), fill=kit.mix(kit.CARD, kit.MINT, a))
        d.text((174, y + 80), num, font=kit.font(36), fill=kit.mix(kit.MINT, kit.INK, a), anchor="mm")
        d.text((248, y + 50), head, font=kit.font(40), fill=kit.mix(kit.CARD, kit.MINT, a), anchor="lm")
        d.text((248, y + 108), body, font=kit.font(28), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        kit.check_badge(d, 900, y + 74, kit.appear(t, ts + 0.28, 0.18))

    a2 = kit.appear(t, 0.92)
    if a2 > 0.04:
        y = 840 + int(kit.lerp(16, 0, a2))
        kit.rounded(d, (90, y, 500, y + 220), 26, kit.mix(kit.BG, kit.CARD, a2))
        d.text((295, y + 60), "名单", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
        d.text((295, y + 130), "对得上", font=kit.font(48), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
        kit.rounded(d, (540, y, 990, y + 220), 26, kit.mix(kit.BG, (22, 40, 36), a2))
        d.text((765, y + 60), "任务", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
        d.text((765, y + 130), "接得住", font=kit.font(48), fill=kit.mix(kit.CARD, kit.YELLOW, a2), anchor="mm")

    punch = kit.appear(t, 1.28, 0.24)
    if punch > 0.04:
        y3 = 1120 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 85), "请按交付来过", font=kit.font(48), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    """Episode 默认写成 79-long / 加长重切；本集是 NEW，改回 .abroll-cloud/79/。"""
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "79_组会不是攻坚工坊"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/79"
        status["source_note"] = "topics-batch4.md #79 / 备忘录第三节 1 / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status["not_duplicate_of"] = "成片37组会撞课SOP"
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "79_组会不是攻坚工坊"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        report["not_duplicate_of"] = "成片/37-组会撞课先摸惯例再书面报备.mp4"
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/79"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        data["source_note"] = "topics-batch4.md #79 / 备忘录第三节 1 / 云端 NEW"
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 79 · 组会不是攻坚工坊

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做 37。

- **选题**：`topics-batch4.md` 第 79 条；Drive 备忘录第三节 1「研一组会的本质认知」
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/79/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：成片 37 撞课 SOP；成片 49 文献精读；成片 16 只报做完 / 工位切片

钩子：组会不是攻坚工坊。
诊断：导师来统筹秩序、检视考勤、派发任务，不是手把手改算法。
例子：宏观说教像气球会飘走；表现看按时交付、态度严谨、合规合矩。
收束：名单对得上才算在，任务接得住才算过。请按交付来过。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头九条，口播十八句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")

    (ROOT / "79-DURATION.md").write_text(
        f"""# 成片 79 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 与 37 | 新时长 | 草稿 |
|----|------|-------|--------|------|
| 79 | `{STAGED_NAME}` | 37 是撞课 SOP，本条是组会本质 | {kit.zh_sec(duration)} | `.abroll-cloud/79/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。九镜 / 十八句。禁止冻帧垫时长。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    old = "| 79 | 专硕组会本质 | `79-组会不是技术攻坚工坊.mp4` | 未拍 |"
    new = f"| 79 | 专硕组会本质 | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if old in text:
        text = text.replace(old, new)
    claimed = "- **状态**：已认领 · `.abroll-cloud/79/` · NEW · 目标四十到五十秒"
    verified = f"- **状态**：已核验 · `.abroll-cloud/79/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
    if claimed in text:
        text = text.replace(claimed, verified)
    elif "## 79. 组会不是技术攻坚工坊" in text and verified not in text:
        text = text.replace(
            "## 79. 组会不是技术攻坚工坊\n",
            "## 79. 组会不是技术攻坚工坊\n\n" + verified + "\n",
        )
    path.write_text(text, encoding="utf-8")


def patch_delivery_new(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    line = (
        f"| `成片/{STAGED_NAME}` | 1080×1920 h264+aac 44.1k stereo | {kit.zh_sec(duration)} | "
        f"topic 79 `topics-batch4.md` 第 79 条；备忘录第三节 1。云端 NEW，不重拍 37。 |"
    )
    token = f"`成片/{STAGED_NAME}`"
    if token in text:
        rows = []
        for raw in text.splitlines():
            if raw.startswith("|") and token in raw:
                rows.append(line)
            else:
                rows.append(raw)
        text = "\n".join(rows)
    elif "仙侠云海突进" in text:
        text = text.replace("| `成片/仙侠云海突进.mp4`", line + "\n| `成片/仙侠云海突进.mp4`")
    else:
        if not text.endswith("\n"):
            text += "\n"
        text += line + "\n"
    if not text.endswith("\n"):
        text += "\n"
    # kit writes 加长重切; overwrite that wording if present
    text = text.replace(
        f"topic 79 加长重切（79-long，覆盖 0.0秒短切）",
        "topic 79 `topics-batch4.md` 第 79 条；备忘录第三节 1。云端 NEW，不重拍 37。",
    )
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "组会不是攻坚工坊",
        "staged_name": STAGED_NAME,
        "episode": 79,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "topics-batch4.md #79 · 备忘录第三节 1 · 云端 NEW",
        "hooks": "钩子：组会不是攻坚工坊。\n诊断：导师统筹秩序、检视考勤、派发任务，不是手把手改算法。\n例子：说教气球会飘走；表现看按时交付、态度严谨、合规合矩。\n收束：请按交付来过。",
        "cover_lines": ("组会不是", "攻坚工坊"),
        "avoid": "成片 37 撞课 SOP；成片 49 文献精读；成片 16 只报做完；成片 45 会议没有结束时间",
        "factory": "topics-batch4 #79",
        "broll": {
            "S02": ("B-秩序会不是辅导课.mp4", frame_not_workshop),
            "S04": ("B-三条表现.mp4", frame_three_metrics),
            "S06": ("B-三步记下.mp4", frame_three_steps),
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
    ep.patch_delivery(dur)
    report = ep.qa(staged, data)
    report["chengpian"] = str(staged)
    report["chengpian_duration_s"] = dur
    report["chengpian_duration_zh"] = kit.zh_sec(dur)
    report["draft_duration_s"] = draft_dur
    report["draft_duration_zh"] = kit.zh_sec(draft_dur)
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rewrite_docs(dur)
    patch_topics(dur)
    patch_delivery_new(dur)
    print("DOCS 79", staged, kit.zh_sec(dur), "ok", report.get("ok"))
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
    print("NEW 79", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
