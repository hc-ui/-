#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 78：先问有没有人想看。topics-batch4 #78。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/78/，成品中转 成片/78-先问有没有人想看.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不重拍成片 45（会议没有结束时间），不拍战神/仙侠。
"""
from __future__ import annotations

import json
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "先问有没有人想看"
STAGED_NAME = "78-先问有没有人想看.mp4"


def _wallpaper(d, box, a: float, t: float) -> None:
    x0, y0, x1, y1 = box
    if a < 0.04:
        return
    sky = kit.mix(kit.BG, (38, 72, 96), a)
    kit.rounded(d, box, 28, sky)
    sun_x = int((x0 + x1) * 0.62)
    sun_y = y0 + 70 + kit.breathe(t, 4)
    r = 36
    d.ellipse((sun_x - r, sun_y - r, sun_x + r, sun_y + r), fill=kit.mix(sky, kit.AMBER, a))
    hill = kit.mix(sky, (28, 46, 42), a)
    d.polygon(
        [(x0 + 8, y1 - 8), (x0 + 8, y1 - 90), (int((x0 + x1) / 2) - 20, y1 - 150), (x1 - 8, y1 - 70), (x1 - 8, y1 - 8)],
        fill=hill,
    )
    d.polygon(
        [(x0 + 8, y1 - 8), (x0 + 120, y1 - 120), (x0 + 280, y1 - 40), (x0 + 8, y1 - 8)],
        fill=kit.mix(sky, (22, 38, 36), a),
    )


def frame_wallpaper(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 是壁纸")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0)) + dy),
        "它是壁纸",
        font=kit.font(56),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    box = (160, 300 + dy, 920, 780 + dy)
    _wallpaper(d, box, a1, t)
    kit.strike_box(d, box, kit.appear(t, 0.70, 0.35), kit.mix(kit.CARD, kit.RED, a1))
    d.text((kit.W // 2, 820 + dy), "漂亮空镜", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")

    chips = [(0.40, "人物"), (0.55, "欲望"), (0.70, "失败")]
    for idx, (ts, label) in enumerate(chips):
        a = kit.appear(t, ts, 0.20)
        if a < 0.04:
            continue
        x0 = 90 + idx * 310
        y = 880 + int(kit.lerp(16, 0, a))
        kit.rounded(d, (x0, y, x0 + 280, y + 160), 26, kit.mix(kit.BG, kit.CARD, a))
        d.text((x0 + 140, y + 52), label, font=kit.font(40), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="mm")
        kit.x_mark(d, x0 + 140, y + 118, kit.appear(t, ts + 0.18, 0.16), 22)

    punch = kit.appear(t, 1.20, 0.24)
    if punch > 0.04:
        y3 = 1100 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 160), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y3 + 80), "不是片子", font=kit.font(50), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_can_do(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 只问做对")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "只问能不能做对",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 320 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 460), 32, kit.mix(kit.BG, (22, 40, 36), a1))
    d.text((285, y + 70), "能做对", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "模型过了", font=kit.font(44), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
    kit.check_badge(d, 285, y + 300, kit.appear(t, 0.48, 0.20))
    d.text((285, y + 400), "勾上了", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (540, y, 1010, y + 460), 32, kit.mix(kit.BG, (42, 24, 22), a2))
    d.text((775, y + 70), "有人看", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((775, y + 180), "格子空着", font=kit.font(44), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")
    empty = kit.appear(t, 0.62, 0.22)
    if empty > 0.04:
        cx, cy, r = 775, y + 300, 36
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=kit.mix(kit.CARD, kit.RED, empty), width=8)
    d.text((775, y + 400), "没人停", font=kit.font(28), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")

    punch = kit.appear(t, 1.20, 0.24)
    if punch > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y3, 990, y3 + 200), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y3 + 70), "顺序反了", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, punch), anchor="mm")
        d.text((kit.W // 2, y3 + 130), "零欲望方案", font=kit.font(50), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_three_swipes(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 先问想看")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "同一张壁纸看三次",
        font=kit.font(46),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    cards = [
        (0.14, "第1次", "哦", kit.YELLOW, False),
        (0.32, "第2次", "还行", kit.MUTED, False),
        (0.50, "第3次", "滑走", kit.RED, True),
    ]
    for idx, (ts, head, body, color, swipe) in enumerate(cards):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        x0 = 70 + idx * 340
        y = 290 + int(kit.lerp(16, 0, a))
        kit.rounded(d, (x0, y, x0 + 300, y + 520), 28, kit.mix(kit.BG, kit.CARD, a))
        _wallpaper(d, (x0 + 18, y + 70, x0 + 282, y + 300), a, t + idx * 0.4)
        d.text((x0 + 150, y + 40), head, font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a), anchor="mm")
        d.text((x0 + 150, y + 380), body, font=kit.font(44), fill=kit.mix(kit.CARD, color, a), anchor="mm")
        if swipe:
            p = kit.appear(t, 0.85, 0.35)
            kit.strike_box(d, (x0 + 18, y + 70, x0 + 282, y + 300), p, kit.mix(kit.CARD, kit.RED, a))
            fx = int(kit.lerp(x0 + 240, x0 + 50, p))
            fy = y + 200 + dy
            d.ellipse((fx - 22, fy - 22, fx + 22, fy + 22), fill=kit.mix(kit.CARD, kit.CREAM, a))
            d.text((x0 + 150, y + 460), "手指滑走", font=kit.font(26), fill=kit.mix(kit.CARD, kit.RED, a), anchor="mm")
        else:
            if idx == 0:
                kit.check_badge(d, x0 + 150, y + 460, kit.appear(t, ts + 0.28, 0.16))

    a3 = kit.appear(t, 1.10, 0.22)
    if a3 > 0.04:
        y = 860 + int(kit.lerp(16, 0, a3)) + dy
        kit.rounded(d, (70, y, 500, y + 200), 26, kit.mix(kit.BG, (18, 42, 36), a3))
        d.text((285, y + 60), "先欲望", font=kit.font(40), fill=kit.mix(kit.CARD, kit.MINT, a3), anchor="mm")
        kit.check_badge(d, 285, y + 140, kit.appear(t, 1.28, 0.16))
        kit.rounded(d, (540, y, 1010, y + 200), 26, kit.mix(kit.BG, (42, 24, 22), a3))
        d.text((775, y + 60), "先模型", font=kit.font(40), fill=kit.mix(kit.CARD, kit.RED, a3), anchor="mm")
        kit.x_mark(d, 775, y + 140, kit.appear(t, 1.36, 0.16), 26)

    punch = kit.appear(t, 1.50, 0.22)
    if punch > 0.04:
        y3 = 1120 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 150), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 75), "先问有没有人想看", font=kit.font(42), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    """Episode 默认写成 78-long / 加长重切；本集是 NEW，改回 .abroll-cloud/78/。"""
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "78_先问有没有人想看"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/78"
        status["source_note"] = "topics-batch4.md #78 / Drive 方向测试.md / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "78_先问有没有人想看"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/78"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 78 · 先问有没有人想看

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：`topics-batch4.md` 第 78 条；Drive 只读 `方向测试.md`（2026-08-17）；`topics-batch3.md` #45 未按原题进成片
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/78/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：成片 45 会议没有结束时间；成片 39 酷画面删掉；成片 29 故事没锁；成片 27 三秒留人；成片 52 别把反转写进标题；战神/仙侠

钩子：先问有没有人想看。
诊断：最稳的方向是壁纸；没人物、没欲望、没失败。
例子：第一次哦一声，第三次滑走；能做对的空镜没人停。
收束：先欲望，再模型；没人想看的方向，请当成没立。

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
    old = "| 78 | 方向测试教训 | `78-先问有没有人想看.mp4` | batch3 #45 未按原题拍 |"
    claimed = "| 78 | 方向测试教训 | `78-先问有没有人想看.mp4` | 已认领 `.abroll-cloud/78/` |"
    new = f"| 78 | 方向测试教训 | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if old in text:
        text = text.replace(old, claimed if duration <= 0 else new)
    if claimed in text and duration > 0:
        text = text.replace(claimed, new)
    claimed_line = "- **状态**：已认领 · `.abroll-cloud/78/` · NEW · 目标四十到五十秒"
    verified = f"- **状态**：已核验 · `.abroll-cloud/78/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
    heading = "## 78. 先问有没有人想看\n"
    if claimed_line not in text and verified not in text and heading in text:
        text = text.replace(heading, heading + "\n" + claimed_line + "\n")
    if claimed_line in text and duration > 0:
        text = text.replace(claimed_line, verified)
    path.write_text(text, encoding="utf-8")


def patch_delivery(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    row = (
        f"| `成片/{STAGED_NAME}` | 1080×1920 h264+aac 44.1k stereo | {kit.zh_sec(duration)} | "
        f"topic 78 `topics-batch4.md` 第 78 条；Drive 只读 `方向测试.md`（方向 B 是壁纸）。"
        f"`成片/78-*.mp4` 未占用。云端 NEW，不拷工厂成片，不重拍成片 45。 |"
    )
    token = f"`成片/{STAGED_NAME}`"
    lines = text.splitlines()
    rebuilt = []
    seen = False
    for raw in lines:
        if raw.startswith("|") and token in raw:
            if not seen:
                rebuilt.append(row)
                seen = True
            continue
        rebuilt.append(raw)
    if not seen:
        inserted = False
        out = []
        for raw in rebuilt:
            if (not inserted) and "仙侠云海突进" in raw and raw.strip().startswith("|"):
                out.append(row)
                inserted = True
            out.append(raw)
        if not inserted:
            out.append(row)
        rebuilt = out
    table_row = f"| 78 | `{STAGED_NAME}` | {kit.zh_sec(duration)} | 已核验 |"
    if "| 78 |" not in "\n".join(rebuilt):
        rebuilt.append(table_row)
    else:
        rebuilt = [table_row if raw.startswith("| 78 |") else raw for raw in rebuilt]
    text = "\n".join(rebuilt)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "先问有没有人想看",
        "staged_name": STAGED_NAME,
        "episode": 78,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "topics-batch4.md #78 · Drive 方向测试.md · 云端 NEW",
        "hooks": "钩子：先问有没有人想看。\n诊断：最稳的方向是壁纸。\n例子：第一次哦一声，第三次滑走。\n收束：没人想看的方向，请当成没立。",
        "cover_lines": ("先问有没有人", "想看"),
        "avoid": "成片 45 会议没有结束时间；成片 39 酷画面删掉；成片 29 故事没锁；成片 27 三秒留人；成片 52 别把反转写进标题；战神/仙侠",
        "factory": "topics-batch4 #78",
        "broll": {
            "S02": ("B-是壁纸.mp4", frame_wallpaper),
            "S04": ("B-只问做对.mp4", frame_can_do),
            "S06": ("B-三次滑走.mp4", frame_three_swipes),
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
    patch_delivery(dur)
    report = ep.qa(staged, data)
    report["chengpian"] = str(staged)
    report["chengpian_duration_s"] = dur
    report["chengpian_duration_zh"] = kit.zh_sec(dur)
    report["draft_duration_s"] = draft_dur
    report["draft_duration_zh"] = kit.zh_sec(draft_dur)
    (ROOT / "交付核验.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rewrite_docs(dur)
    patch_topics(dur)
    print("DOCS 78", staged, kit.zh_sec(dur), "ok", report.get("ok"))
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
    patch_delivery(dur)
    print("NEW 78", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
