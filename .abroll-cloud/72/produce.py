#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 72：先给结论再展开。topics-batch4 #72。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/72/，成品中转 成片/72-先给结论再展开.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不重复成片 11 列表项先给结果，不重拍成片 70 例子先于概念。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "先给结论再展开"
STAGED_NAME = "72-先给结论再展开.mp4"


def frame_tail_last(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 结论在尾")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0)) + dy),
        "结论还在最后一句",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    rows = [
        (0.14, "1", "背景", "从哪来先铺完"),
        (0.34, "2", "过程", "还在交代来历"),
        (0.54, "3", "结论", "压在最后一句"),
    ]
    for idx, (ts, num, head, body) in enumerate(rows):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 310 + idx * 168 + int(kit.lerp(16, 0, a))
        fill = kit.CARD if idx < 2 else (42, 24, 22)
        kit.rounded(d, (90, y, 990, y + 148), 26, kit.mix(kit.BG, fill, a))
        color = kit.MUTED if idx < 2 else kit.YELLOW
        d.ellipse((128, y + 34, 220, y + 126), fill=kit.mix(fill, color, a))
        d.text((174, y + 80), num, font=kit.font(36), fill=kit.mix(color, kit.INK, a), anchor="mm")
        d.text((248, y + 50), head, font=kit.font(40), fill=kit.mix(fill, color, a), anchor="lm")
        d.text((248, y + 108), body, font=kit.font(28), fill=kit.mix(fill, kit.WHITE, a), anchor="lm")
        if idx == 2:
            kit.x_mark(d, 900, y + 74, kit.appear(t, 0.78, 0.20), 28)

    punch = kit.appear(t, 1.20, 0.24)
    if punch > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 170), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y3 + 85), "听众已经走了", font=kit.font(48), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_why_after(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 为什么在后")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "能复述的先扔出去",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 320 + int(kit.lerp(18, 0, a1)) + dy
    kit.rounded(d, (70, y, 1010, y + 280), 32, kit.mix(kit.BG, (22, 40, 36), a1))
    d.text((kit.W // 2, y + 70), "第一屏", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((kit.W // 2, y + 160), "能带走的那句", font=kit.font(52), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
    kit.check_badge(d, 930, y + 140, kit.appear(t, 0.48, 0.18))

    stack = [
        (0.48, "为什么", "叠在后面"),
        (0.68, "从哪来", "不抢第一屏"),
    ]
    for idx, (ts, head, body) in enumerate(stack):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        yy = 640 + idx * 150 + int(kit.lerp(14, 0, a))
        kit.rounded(d, (110, yy, 970, yy + 130), 24, kit.mix(kit.BG, kit.CARD, a))
        d.text((kit.W // 2, yy + 44), head, font=kit.font(36), fill=kit.mix(kit.CARD, kit.YELLOW, a), anchor="mm")
        d.text((kit.W // 2, yy + 96), body, font=kit.font(28), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="mm")

    punch = kit.appear(t, 1.20, 0.24)
    if punch > 0.04:
        y3 = 960 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 85), "不抢第一屏", font=kit.font(50), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_head_first(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 结论在头")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "结论拎到开头",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 320 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 420), 32, kit.mix(kit.BG, kit.CARD, a1))
    d.text((285, y + 56), "结论在尾", font=kit.font(34), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "最后一句", font=kit.font(44), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    kit.strike_box(d, (110, y + 150, 460, y + 220), kit.appear(t, 0.50, 0.35), kit.mix(kit.CARD, kit.RED, 1))
    kit.x_mark(d, 285, y + 300, kit.appear(t, 0.55, 0.22), 36)
    d.text((285, y + 380), "听众已走", font=kit.font(28), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (540, y, 1010, y + 420), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((775, y + 56), "结论在头", font=kit.font(34), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((775, y + 180), "第一屏", font=kit.font(48), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    kit.check_badge(d, 775, y + 300, kit.appear(t, 0.70, 0.22))
    d.text((775, y + 380), "能带走", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")

    stamp = kit.appear(t, 1.15, 0.24)
    if stamp > 0.04:
        y3 = 820 + int(kit.lerp(16, 0, stamp)) + dy
        kit.rounded(d, (90, y3, 990, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), stamp))
        d.text((kit.W // 2, y3 + 70), "长铺垫先划掉", font=kit.font(36), fill=kit.mix(kit.CARD, kit.YELLOW, stamp), anchor="mm")
        d.text((kit.W // 2, y3 + 140), "结论先落地", font=kit.font(50), fill=kit.mix(kit.BG, kit.MINT, stamp), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    """Episode 默认写成 72-long / 加长重切；本集是 NEW，改回 .abroll-cloud/72/。"""
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "72_先给结论再展开"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/72"
        status["source_note"] = "topics-batch4.md #72 / 工厂 72_先给结论再展开 / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "72_先给结论再展开"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/72"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        data["source_note"] = "工厂 72_先给结论再展开 / 云端 NEW"
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 72 · 先给结论再展开

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：`topics-batch4.md` 第 72 条；工厂 `72_先给结论再展开`
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/72/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：成片 11 列表项先给结果；成片 70 例子先于概念；#55 先给能截的那句；成片 65 口头同步当过结论

钩子：先给结论再展开。
诊断：背景铺完，结论还在最后一句；听众已经走了。
例子：能带走的那句放最前；为什么叠在后面。
收束：对照结论在尾还是在头；长铺垫划掉，结论先落地。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头九条，口播十八句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")

    (ROOT / "72-DURATION.md").write_text(
        f"""# 成片 72 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 工厂短切 | 新时长 | 草稿 |
|----|------|----------|--------|------|
| 72 | `{STAGED_NAME}` | 未进成片 | {kit.zh_sec(duration)} | `.abroll-cloud/72/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。九镜 / 十八句。禁止 `tpad=stop_mode=clone`。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    old = "| 72 | 剩余口播工艺 | `72-先给结论再展开.mp4` | 未拍（工厂有短切，云端加长） |"
    new = f"| 72 | 剩余口播工艺 | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if old in text:
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def patch_delivery_new(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    line = (
        f"| `成片/{STAGED_NAME}` | 1080×1920 h264+aac 44.1k stereo | {kit.zh_sec(duration)} | "
        f"topic 72 Drive 只读工厂 `72_先给结论再展开`（claim：60–62 撞号后改认；工厂有短切，未进 `/workspace/成片/`）。"
        f"`成片/72-*.mp4` 未占用。云端 NEW，不拷工厂成片。 |"
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
    else:
        if "仙侠云海突进" in text:
            text = text.replace("| `成片/仙侠云海突进.mp4`", line + "\n| `成片/仙侠云海突进.mp4`")
        else:
            if not text.endswith("\n"):
                text += "\n"
            text += line + "\n"
    if not text.endswith("\n"):
        text += "\n"
    # 61+ 表
    row61 = "| 72 | `72-先给结论再展开.mp4` |"
    if row61 not in text and "## 本轮 61+" in text:
        add = f"| 72 | `{STAGED_NAME}` | {kit.zh_sec(duration)} | 已核验 |"
        marker = "| 69 | `69-值班手册是空的.mp4`"
        if marker in text:
            rebuilt = []
            inserted = False
            for raw in text.splitlines():
                rebuilt.append(raw)
                if (not inserted) and raw.startswith(marker):
                    rebuilt.append(add)
                    inserted = True
            if inserted:
                text = "\n".join(rebuilt)
                if not text.endswith("\n"):
                    text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "先给结论再展开",
        "staged_name": STAGED_NAME,
        "episode": 72,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "topics-batch4.md #72 · 工厂 72_先给结论再展开 · 云端 NEW",
        "hooks": "钩子：先给结论再展开。\n诊断：背景铺完，结论还在最后一句。\n例子：能带走的那句放最前；为什么叠在后面。\n收束：长铺垫划掉，结论先落地。",
        "cover_lines": ("先给结论", "再展开"),
        "avoid": "成片 11 列表项先给结果；成片 70 例子先于概念；#55 先给能截的那句；成片 65 口头同步当过结论；成片 27 三秒留人",
        "factory": "topics-batch4 #72",
        "broll": {
            "S02": ("B-结论在尾.mp4", frame_tail_last),
            "S04": ("B-为什么在后.mp4", frame_why_after),
            "S06": ("B-结论在头.mp4", frame_head_first),
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
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rewrite_docs(dur)
    patch_topics(dur)
    patch_delivery_new(dur)
    print("DOCS 72", staged, kit.zh_sec(dur), "ok", report.get("ok"))
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
    print("NEW 72", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
