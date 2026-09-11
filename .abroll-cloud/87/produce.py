#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 87：大案例先拆到能退出。topics-batch4 #87。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/87/，成品中转 成片/87-大案例先拆到能退出.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不重复成片 43 三道短题，不重复成片 74 菜单拆函数。只打退门这一刀。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "大案例先拆到能退出"
STAGED_NAME = "87-大案例先拆到能退出.mp4"


def draw_door(d, x: int, y: int, w: int, h: int, a: float, open_amt: float = 0.0, locked: bool = True) -> None:
    if a <= 0.04:
        return
    frame = kit.mix(kit.BG, (36, 32, 28), a)
    kit.rounded(d, (x, y, x + w, y + h), 18, frame)
    inset = 16
    panel_w = w - inset * 2
    shift = int(panel_w * 0.42 * max(0.0, min(1.0, open_amt)))
    panel = kit.mix(kit.CARD, (58, 42, 32) if locked else (22, 52, 44), a)
    kit.rounded(
        d,
        (x + inset + shift, y + inset, x + w - inset + shift, y + h - inset),
        12,
        panel,
    )
    knob_x = x + w - inset - 36 + shift
    knob_y = y + h // 2
    d.ellipse((knob_x - 14, knob_y - 14, knob_x + 14, knob_y + 14), fill=kit.mix(panel, kit.YELLOW if locked else kit.MINT, a))
    d.text((x + w // 2 + shift // 2, y + 56), "退", font=kit.font(44), fill=kit.mix(panel, kit.WHITE, a), anchor="mm")
    if locked:
        kit.x_mark(d, x + w // 2, y + h // 2 + 40, kit.appear(1.0, 0.0, 0.01) * a, 28)
    else:
        kit.check_badge(d, x + w // 2 + shift // 2, y + h // 2 + 40, a)


def frame_locked(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 退门焊死")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0)) + dy),
        "四件事焊住退门",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    chips = [("增", 0.14), ("列", 0.22), ("统", 0.30), ("退", 0.38)]
    for idx, (label, ts) in enumerate(chips):
        a = kit.appear(t, ts, 0.18)
        if a < 0.04:
            continue
        x = 90 + (idx % 2) * 280
        y = 300 + (idx // 2) * 200 + int(kit.lerp(14, 0, a))
        hot = label == "退"
        fill = (42, 24, 22) if hot else kit.CARD
        kit.rounded(d, (x, y, x + 250, y + 170), 24, kit.mix(kit.BG, fill, a))
        d.text((x + 125, y + 85), label, font=kit.font(56), fill=kit.mix(kit.CARD, kit.YELLOW if hot else kit.WHITE, a), anchor="mm")
        if hot:
            kit.x_mark(d, x + 200, y + 40, kit.appear(t, 0.70, 0.18), 18)

    a_door = kit.appear(t, 0.28, 0.22)
    if a_door > 0.04:
        draw_door(d, 700, 320 + dy, 300, 380, a_door, open_amt=0.0, locked=True)

    weld = kit.appear(t, 0.85, 0.28)
    if weld > 0.04:
        kit.strike_box(d, (90, 300, 630, 680), weld, kit.mix(kit.CARD, kit.RED, weld))

    punch = kit.appear(t, 1.20, 0.22)
    if punch > 0.04:
        y3 = 980 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 180), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y3 + 90), "菜单卡死出不去", font=kit.font(48), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_steps(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 先让退出通")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 200 + int(kit.lerp(16, 0, a0))),
        "先有门，再往里装",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    rows = [
        (0.16, "1", "退出", "先让退门通", True),
        (0.44, "2", "增列出", "成绩才能进出", False),
        (0.72, "3", "统计", "最高最低平均往后", False),
    ]
    for ts, num, head, body, live in rows:
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 280 + int(num) * 168 - 168 + int(kit.lerp(16, 0, a))
        fill = (18, 42, 36) if live else kit.CARD
        kit.rounded(d, (80, y, 720, y + 148), 26, kit.mix(kit.BG, fill, a))
        d.ellipse((118, y + 34, 210, y + 126), fill=kit.mix(kit.CARD, kit.MINT if live else kit.MUTED, a))
        d.text((164, y + 80), num, font=kit.font(36), fill=kit.mix(kit.MINT if live else kit.MUTED, kit.INK, a), anchor="mm")
        d.text((238, y + 50), head, font=kit.font(40), fill=kit.mix(kit.CARD, kit.MINT if live else kit.WHITE, a), anchor="lm")
        d.text((238, y + 108), body, font=kit.font(26), fill=kit.mix(kit.CARD, kit.YELLOW if live else kit.MUTED, a), anchor="lm")
        if live:
            kit.check_badge(d, 650, y + 74, kit.appear(t, ts + 0.28, 0.18))
        else:
            kit.x_mark(d, 650, y + 74, kit.appear(t, ts + 0.28, 0.18), 18)

    open_amt = kit.appear(t, 0.36, 0.40)
    draw_door(d, 760, 300 + dy, 250, 460, kit.appear(t, 0.20, 0.20), open_amt=open_amt, locked=False)

    punch = kit.appear(t, 1.30, 0.24)
    if punch > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y3, 990, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 70), "门开了", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, punch), anchor="mm")
        d.text((kit.W // 2, y3 + 130), "统计放最后", font=kit.font(50), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_contrast(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对照 · 焊死 / 先退")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "一张对照只打退门",
        font=kit.font(46),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 520), 32, kit.mix(kit.BG, (42, 24, 22), a1))
    d.text((285, y + 56), "整坨开工", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "退门锁死", font=kit.font(52), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    kit.x_mark(d, 285, y + 320, kit.appear(t, 0.55, 0.22), 36)
    d.text((285, y + 430), "一改就炸", font=kit.font(30), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (540, y, 1010, y + 520), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((775, y + 56), "先拆到退出", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((775, y + 180), "门开了", font=kit.font(52), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    kit.check_badge(d, 775, y + 320, kit.appear(t, 0.70, 0.22))
    d.text((775, y + 430), "才能停得住", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")

    stamp = kit.appear(t, 1.20, 0.24)
    if stamp > 0.04:
        y3 = 900 + int(kit.lerp(16, 0, stamp)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), stamp))
        d.text((kit.W // 2, y3 + 70), "先拆到能退出", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, stamp), anchor="mm")
        d.text((kit.W // 2, y3 + 140), "这盘才算站住", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, stamp), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    """Episode 默认写成 87-long / 加长重切；本集是 NEW，改回 .abroll-cloud/87/。"""
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "87_大案例先拆到能退出"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/87"
        status["source_note"] = "topics-batch4.md #87 / 学习基线 2026-09-09 不足第8条 / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "87_大案例先拆到能退出"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/87"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 87 · 大案例先拆到能退出

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：`topics-batch4.md` 第 87 条；学习基线 2026-09-09 不足第 8 条
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/87/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：成片 43 三道短题；成片 74 菜单拆函数；成片 64 空字典；成片 73 先包一层；#86 成绩存盘；C++ / ROS2

钩子：大案例先拆到能退出。
诊断：增列统计焊死退门；四件事一起上，菜单卡死出不去。
做法：先让退出通；再增和列出；统计放最后。
收束：退出通了，这盘才算站住。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头九条，口播十八句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")
    (ROOT / "时长.md").write_text(
        f"""# 成片 87 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 工厂短切 | 新时长 | 草稿 |
|----|------|----------|--------|------|
| 87 | `{STAGED_NAME}` | 无（首拍） | {kit.zh_sec(duration)} | `.abroll-cloud/87/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。九镜 / 十八句。禁止 `tpad=stop_mode=clone`。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    heading = "## 87. 大案例先拆到能退出"
    claimed = "- **状态**：已认领 · `.abroll-cloud/87/` · NEW · 目标四十到五十秒"
    verified = f"- **状态**：已核验 · `.abroll-cloud/87/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
    if heading not in text:
        block = f"""{heading}

{verified}
- **A-roll 角度**：未完成 Python。不足第 8 条：综合题难在焊在一起，不是新知识点。大案例要拆到第一刀能退出。成片 43 只打短题交卷，成片 74 只打起名字，本条只打退门。
- **B-roll 想法**：四件事焊死退门；三步条只亮退出；对照卡整坨开工 / 先拆到退出。
- **来源笔记**：Drive `学习与职业规划基线.md`（2026-09-09 不足第 8 条）
- **成片名**：`{STAGED_NAME}`
- **避开**：成片 43 三道短题；成片 74 菜单拆函数；成片 64 空字典；成片 73 先包一层

"""
        marker = "## 对照备忘"
        if marker in text:
            text = text.replace(marker, block + marker)
        else:
            text = text.rstrip() + "\n\n" + block
    elif claimed in text:
        text = text.replace(claimed, verified)
    elif verified not in text:
        text = text.replace(
            f"{heading}\n\n- **A-roll 角度**：",
            f"{heading}\n\n{verified}\n- **A-roll 角度**：",
        )

    old = "| 87 | 未完成 Python | `87-大案例先拆到能退出.mp4` | 未拍 |"
    claimed_row = "| 87 | 未完成 Python | `87-大案例先拆到能退出.mp4` | 已认领 `.abroll-cloud/87/` |"
    new = f"| 87 | 未完成 Python | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if old in text:
        text = text.replace(old, new)
    elif claimed_row in text:
        text = text.replace(claimed_row, new)
    elif f"`{STAGED_NAME}`" in text and "| 87 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 87 |") and STAGED_NAME in raw:
                lines.append(new)
            else:
                lines.append(raw)
        text = "\n".join(lines)
        if not text.endswith("\n"):
            text += "\n"
    else:
        table_end = "本批含"
        row = new + "\n"
        if "| 85 |" in text and "| 87 |" not in text:
            rebuilt = []
            inserted = False
            for raw in text.splitlines():
                rebuilt.append(raw)
                if (not inserted) and raw.startswith("| 85 |"):
                    rebuilt.append(new)
                    inserted = True
            text = "\n".join(rebuilt)
            if not text.endswith("\n"):
                text += "\n"
        elif table_end in text and "| 87 |" not in text:
            text = text.replace(table_end, row + table_end)

    if "本批含 85" in text and "87" not in text.split("本批含 85", 1)[1][:80]:
        text = text.replace("本批含 85（毕业底线三件套）。", "本批含 85、87。时长用中文「秒」。\n")
        if "本批含 85、87" not in text:
            text = text.replace("本批含 85（毕业底线三件套）。时长用中文「秒」。", "本批含 85、87。时长用中文「秒」。")
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def patch_delivery_new(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    new = (
        f"| `成片/{STAGED_NAME}` | 1080×1920 h264+aac 44.1k stereo | {kit.zh_sec(duration)} | "
        f"topic 87 `topics-batch4.md` 第 87 条；学习基线 2026-09-09 不足第 8 条。云端 NEW，不拷成片 43/74。 |"
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

    round_row = f"| 87 | `{STAGED_NAME}` | {kit.zh_sec(duration)} | 已核验 |"
    if "| 87 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 87 |") and STAGED_NAME in raw:
                lines.append(round_row)
            else:
                lines.append(raw)
        text = "\n".join(lines)
        if not text.endswith("\n"):
            text += "\n"
    elif "## 本轮 61+" in text:
        lines = text.splitlines()
        rebuilt = []
        inserted = False
        for raw in lines:
            rebuilt.append(raw)
            if (not inserted) and raw.startswith("| 73 |"):
                rebuilt.append(round_row)
                inserted = True
        if not inserted:
            rebuilt.append(round_row)
        text = "\n".join(rebuilt) + "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "大案例先拆到能退出",
        "staged_name": STAGED_NAME,
        "episode": 87,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "topics-batch4.md #87 · 学习基线 2026-09-09 不足第8条 · 云端 NEW",
        "hooks": "钩子：大案例先拆到能退出。\n诊断：增列统计焊死退门；四件事一起上。\n做法：先让退出通；再增和列出；统计放最后。\n收束：退出通了，这盘才算站住。",
        "cover_lines": ("先拆到退出", "退门通了再装"),
        "avoid": "成片 43 三道短题；成片 74 菜单拆函数；成片 64 空字典；成片 73 先包一层；#86 成绩存盘；C++ / ROS2",
        "factory": "topics-batch4 #87",
        "broll": {
            "S02": ("B-退门焊死.mp4", frame_locked),
            "S04": ("B-先让退出通.mp4", frame_steps),
            "S06": ("B-拆到能停.mp4", frame_contrast),
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
    print("DOCS 87", staged, kit.zh_sec(dur), "ok", report.get("ok"))
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
    print("NEW 87", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
