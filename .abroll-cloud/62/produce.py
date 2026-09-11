#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 62：再优化一下没有验收。topics-batch4 #62。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/62/，成品中转 成片/62-再优化一下没有验收.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不重复 #61 试点成功却推不开。
"""
from __future__ import annotations

import json
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "再优化一下没有验收"
STAGED_NAME = "62-再优化一下没有验收.mp4"


def frame_no_end(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 没终点")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0)) + dy),
        "再优化一下",
        font=kit.font(56),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    cx, cy, r = kit.W // 2, 560, 210
    spin = (t * 70) % 360
    if a1 > 0.04:
        box = (cx - r, cy - r + dy, cx + r, cy + r + dy)
        d.ellipse(box, outline=kit.mix(kit.CARD, (48, 52, 62), a1), width=16)
        d.arc(box, start=spin, end=spin + 240, fill=kit.mix(kit.CARD, kit.AMBER, a1), width=16)
        d.text((cx, cy + dy), "再来一轮", font=kit.font(44), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")

    a2 = kit.appear(t, 0.55)
    if a2 > 0.04:
        y = 860 + int(kit.lerp(18, 0, a2))
        kit.rounded(d, (90, y, 500, y + 200), 26, kit.mix(kit.BG, kit.CARD, a2))
        d.text((295, y + 70), "验收", font=kit.font(40), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
        kit.x_mark(d, 295, y + 140, kit.appear(t, 0.78, 0.20), 28)
        kit.rounded(d, (540, y, 990, y + 200), 26, kit.mix(kit.BG, (42, 24, 22), a2))
        d.text((765, y + 100), "没有终点", font=kit.font(44), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")

    punch = kit.appear(t, 1.20, 0.24)
    if punch > 0.04:
        y3 = 1140 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 170), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y3 + 85), "感觉更好也不算过", font=kit.font(44), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_write_pass(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 先写过")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "先写下什么叫过",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    rows = [
        (0.16, "1", "能打勾", "三条标准就够"),
        (0.40, "2", "能对照", "感觉不算过"),
        (0.64, "3", "能签字", "谁来点头先写上"),
    ]
    for idx, (ts, num, head, body) in enumerate(rows):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 320 + idx * 168 + int(kit.lerp(16, 0, a))
        kit.rounded(d, (90, y, 990, y + 148), 26, kit.mix(kit.BG, kit.CARD, a))
        d.ellipse((128, y + 34, 220, y + 126), fill=kit.mix(kit.CARD, kit.MINT, a))
        d.text((174, y + 80), num, font=kit.font(36), fill=kit.mix(kit.MINT, kit.INK, a), anchor="mm")
        d.text((248, y + 50), head, font=kit.font(40), fill=kit.mix(kit.CARD, kit.MINT, a), anchor="lm")
        d.text((248, y + 108), body, font=kit.font(28), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        kit.check_badge(d, 900, y + 74, kit.appear(t, ts + 0.28, 0.18))

    punch = kit.appear(t, 1.35, 0.24)
    if punch > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y3, 990, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 70), "验收人", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, punch), anchor="mm")
        d.text((kit.W // 2, y3 + 130), "名字先写上", font=kit.font(50), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_one_round(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 一轮一条")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "一轮只改一条",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 320 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 420), 32, kit.mix(kit.BG, kit.CARD, a1))
    d.text((285, y + 56), "顺手加功能", font=kit.font(34), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "新功能", font=kit.font(44), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    kit.x_mark(d, 285, y + 300, kit.appear(t, 0.55, 0.22), 36)
    d.text((285, y + 380), "不准顺手加", font=kit.font(28), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (540, y, 1010, y + 420), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((775, y + 56), "只改没过的", font=kit.font(34), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((775, y + 180), "这一条", font=kit.font(48), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    kit.check_badge(d, 775, y + 300, kit.appear(t, 0.70, 0.22))
    d.text((775, y + 380), "过了就停手", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")

    stamp = kit.appear(t, 1.20, 0.24)
    if stamp > 0.04:
        y3 = 820 + int(kit.lerp(16, 0, stamp)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), stamp))
        d.text((kit.W // 2, y3 + 70), "验收人当场签字", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, stamp), anchor="mm")
        d.text((kit.W // 2, y3 + 140), "没人点头就不算数", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, stamp), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    """Episode 默认写成 62-long / 加长重切；本集是 NEW，改回 .abroll-cloud/62/。"""
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "62_再优化一下没有验收"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/62"
        status["source_note"] = "topics-batch4.md #62 / 工厂 62_再优化一下没有验收 / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "62_再优化一下没有验收"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/62"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 62 · 再优化一下没有验收

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：`topics-batch4.md` 第 62 条；工厂 `62_再优化一下没有验收`
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/62/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：#61 试点成功却推不开；成片 44 忙完没推进；成片 26 待办划不掉；成片 46 六十分

钩子：再优化一下，没有验收。
诊断：不是人不够认真，是标准没立；这句话没有终点。
例子：三条能打勾的标准；一轮只改一条。
收束：验收人当场签字；没有验收的优化，请当成没立。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头九条，口播十八句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    old = "| 62 | 工厂知识口播 | `62-再优化一下没有验收.mp4` | 已认领 `.abroll-cloud/62/` |"
    new = f"| 62 | 工厂知识口播 | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if old in text:
        text = text.replace(old, new)
    claimed = "- **状态**：已认领 · `.abroll-cloud/62/` · NEW · 目标四十到五十秒"
    verified = f"- **状态**：已核验 · `.abroll-cloud/62/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
    if claimed in text:
        text = text.replace(claimed, verified)
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "再优化一下，没有验收",
        "staged_name": STAGED_NAME,
        "episode": 62,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "topics-batch4.md #62 · 工厂 62_再优化一下没有验收 · 云端 NEW",
        "hooks": "钩子：再优化一下，没有验收。\n诊断：不是人不够认真，是标准没立。\n例子：三条能打勾的标准；一轮只改一条。\n收束：没有验收的优化，请当成没立。",
        "cover_lines": ("再优化一下", "没有验收"),
        "avoid": "#61 试点成功却推不开；成片 44 忙完没推进；成片 26 待办划不掉；成片 46 六十分；成片 01 没有截止日",
        "factory": "topics-batch4 #62",
        "broll": {
            "S02": ("B-没有终点.mp4", frame_no_end),
            "S04": ("B-先写过.mp4", frame_write_pass),
            "S06": ("B-一轮一条.mp4", frame_one_round),
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
    print("DOCS 62", staged, kit.zh_sec(dur), "ok", report.get("ok"))
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
    print("NEW 62", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
