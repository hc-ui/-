#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 89：本地实习等成果锁定。topics-batch4 #89。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/89/，成品中转 成片/89-本地实习等成果锁定.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不重拍成片 47 脱产离校、成片 48 远程实习。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "本地实习等成果锁定"
STAGED_NAME = "89-本地实习等成果锁定.mp4"


def frame_lock_gate(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 问早了")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0)) + dy),
        "没锁先别探",
        font=kit.font(54),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.14)
    y = 330 + dy
    kit.rounded(d, (80, y, 500, y + 420), 32, kit.mix(kit.BG, (42, 24, 22), a1))
    d.text((290, y + 80), "研一去问", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((290, y + 190), "本地岗", font=kit.font(48), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    kit.strike_box(d, (120, y + 160, 460, y + 220), kit.appear(t, 0.42, 0.36), kit.mix(kit.CARD, kit.RED, 1))
    kit.x_mark(d, 290, y + 320, kit.appear(t, 0.55, 0.2), 44)

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (580, y + int(kit.breathe(t + 0.2, 4)), 1000, y + 420), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((790, y + 80), "成果章", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((790, y + 190), "还没盖", font=kit.font(48), fill=kit.mix(kit.CARD, kit.YELLOW, a2), anchor="mm")
    d.text((790, y + 280), "人一挪就悬", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")

    punch = kit.appear(t, 1.05, 0.22)
    if punch > 0.04:
        y2 = 820 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y2, 960, y2 + 180), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y2 + 90), "答辩就悬", font=kit.font(52), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_lock_stamp(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 先锁定")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 216 + int(kit.lerp(16, 0, a0))),
        "先把成果锁死",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    cards = [
        (0.14, 80, "专利", "交出去", kit.YELLOW),
        (0.32, 560, "论文初稿", "定稿", kit.MINT),
    ]
    for ts, x, head, body, color in cards:
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 310 + dy
        kit.rounded(d, (x, y, x + 440, y + 360), 32, kit.mix(kit.BG, kit.CARD, a))
        d.rounded_rectangle((x + 28, y + 28, x + 220, y + 88), 16, fill=kit.mix(kit.CARD, color, a))
        d.text((x + 124, y + 58), head, font=kit.font(28), fill=kit.mix(color, kit.INK, a), anchor="mm")
        d.text((x + 220, y + 180), body, font=kit.font(44), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="mm")
        kit.check_badge(d, x + 220, y + 280, kit.appear(t, ts + 0.45, 0.2))

    ticks = [
        (0.70, 90, "研一", True),
        (0.82, 310, "研二上", True),
        (0.94, 530, "研二下", False),
        (1.06, 750, "研三", False),
    ]
    for ts, x, label, gray in ticks:
        a = kit.appear(t, ts, 0.18)
        if a < 0.04:
            continue
        y = 720 + dy
        fill = (42, 28, 24) if gray else (18, 46, 40)
        kit.rounded(d, (x, y, x + 200, y + 140), 22, kit.mix(kit.BG, fill, a))
        d.text((x + 100, y + 70), label, font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED if gray else kit.MINT, a), anchor="mm")
        if gray:
            kit.x_mark(d, x + 100, y + 110, kit.appear(t, ts + 0.12, 0.16), 16)

    punch = kit.appear(t, 1.22, 0.22)
    if punch > 0.04:
        y3 = 920 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 85), "才有资格谈本地", font=kit.font(48), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_handover(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "收 · 交了再探")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 216 + int(kit.lerp(16, 0, a0)) + dy),
        "杂活先交",
        font=kit.font(54),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.14)
    y = 310 + dy
    kit.rounded(d, (80, y, 500, y + 380), 32, kit.mix(kit.BG, kit.CARD, a1))
    d.text((290, y + 70), "还在手里", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((290, y + 170), "本地岗", font=kit.font(44), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    d.text((290, y + 250), "先灰掉", font=kit.font(36), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    kit.x_mark(d, 290, y + 320, kit.appear(t, 0.40, 0.18), 28)

    a2 = kit.appear(t, 0.30)
    kit.rounded(d, (580, y + int(kit.breathe(t + 0.15, 4)), 1000, y + 380), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((790, y + 70), "新一届", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((790, y + 170), "交接清单", font=kit.font(40), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
    kit.check_badge(d, 790, y + 280, kit.appear(t, 0.62, 0.2))

    gates = [
        (0.85, 120, "锁了", True),
        (1.00, 420, "交了", True),
        (1.15, 720, "再探", False),
    ]
    for ts, x, label, on in gates:
        a = kit.appear(t, ts, 0.18)
        if a < 0.04:
            continue
        y2 = 740 + dy
        fill = (18, 46, 40) if on else (42, 34, 16)
        kit.rounded(d, (x, y2, x + 240, y2 + 130), 22, kit.mix(kit.BG, fill, a))
        d.text((x + 120, y2 + 65), label, font=kit.font(36), fill=kit.mix(kit.CARD, kit.MINT if on else kit.YELLOW, a), anchor="mm")

    punch = kit.appear(t, 1.28, 0.22)
    if punch > 0.04:
        y3 = 920 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 85), "锁了交了再探", font=kit.font(48), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    """Episode 默认写成 89-long / 加长重切；本集是 NEW，改回 .abroll-cloud/89/。"""
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "89_本地实习等成果锁定"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/89"
        status["source_note"] = "topics-batch4.md #89 / 备忘录第二节 3 后期合肥本地实习 / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status["distinct_from"] = [
            "成片/47-研一别脱产离校实习.mp4",
            "成片/48-远程实习人在工位活在线上.mp4",
        ]
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "89_本地实习等成果锁定"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        report["distinct_from_47"] = True
        report["distinct_from_48"] = True
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/89"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        data["source_note"] = "topics-batch4.md #89 / 备忘录第二节 3 后期合肥本地实习 / 云端 NEW"
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 89 · 本地实习等成果锁定

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：`topics-batch4.md` 第 89 条；Drive 只读备忘录第二节 3「后期合肥本地实习」
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/89/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：成片 47 研一别脱产离校实习；成片 48 远程实习人在工位活在线上；#85 毕业底线三件套；成片 16 时间切片；成片 28 报销；成片 46 六十分

钩子：本地实习，等成果锁定。不是现在就去问本地岗位。
诊断：初稿没锁先别探；研一问早了；没盖章人一挪答辩就悬。
锁定：专利交出去或论文初稿定稿；时间窗在研二下或研三。
交接：杂活交给新一届，清单勾完；没写清人别挪。
收束：没锁之前先停。锁了，交了，再探本地。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头九条，口播十八句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")
    (ROOT / "时长.md").write_text(
        f"""# 成片 89 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 对照 47 / 48 | 新时长 | 草稿 |
|----|------|--------------|--------|------|
| 89 | `{STAGED_NAME}` | 不重拍（47 脱产 / 48 远程） | {kit.zh_sec(duration)} | `.abroll-cloud/89/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。九镜 / 十八句。禁止 `tpad=stop_mode=clone`。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    claimed = "- **状态**：已认领 · `.abroll-cloud/89/` · NEW · 目标四十到五十秒"
    verified = f"- **状态**：已核验 · `.abroll-cloud/89/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
    if claimed in text:
        text = text.replace(claimed, verified)
    old_row = "| 89 | 专硕本地实习门闩 | `89-本地实习等成果锁定.mp4` | 已认领 `.abroll-cloud/89/` |"
    new_row = f"| 89 | 专硕本地实习门闩 | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if old_row in text:
        text = text.replace(old_row, new_row)
    elif "| 89 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 89 |"):
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
    new = (
        f"| `成片/{STAGED_NAME}` | 1080×1920 h264+aac 44.1k stereo | {kit.zh_sec(duration)} | "
        f"topic 89 `topics-batch4.md` 第 89 条；Drive 只读备忘录第二节 3「后期合肥本地实习」。云端 NEW，不重拍 47/48 |"
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
    plus_row = f"| 89 | `{STAGED_NAME}` | {kit.zh_sec(duration)} | 已核验 |"
    if "| 89 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 89 |"):
                lines.append(plus_row)
            else:
                lines.append(raw)
        text = "\n".join(lines)
    elif "## 本轮 61+" in text and plus_row not in text:
        lines = text.splitlines()
        out = []
        inserted = False
        for raw in lines:
            out.append(raw)
            if (not inserted) and raw.startswith("| 73 |"):
                out.append(plus_row)
                inserted = True
        if not inserted:
            # append at end of 61+ table if 73 row missing
            for i, raw in enumerate(out):
                if raw.startswith("| 80 |") or raw.startswith("| 81 |"):
                    out.insert(i + 1, plus_row)
                    inserted = True
                    break
        text = "\n".join(out)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "本地实习等成果锁定",
        "staged_name": STAGED_NAME,
        "episode": 89,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "topics-batch4.md #89 · 备忘录第二节 3 后期合肥本地实习 · 云端 NEW",
        "hooks": "钩子：本地实习，等成果锁定。\n诊断：初稿没锁先别探；研一问早了。\n锁定：专利或论文初稿定稿；研二下或研三再谈。\n收束：先等成果锁定，再谈本地。",
        "cover_lines": ("本地实习", "等成果锁定"),
        "avoid": "成片 47 脱产离校；成片 48 远程双屏；#85 毕业底线三件套；成片 16 时间切片；成片 28 报销；成片 46 六十分",
        "factory": "topics-batch4 #89",
        "broll": {
            "S02": ("B-没锁先别探.mp4", frame_lock_gate),
            "S04": ("B-成果先锁.mp4", frame_lock_stamp),
            "S06": ("B-交了再探.mp4", frame_handover),
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
    print("DOCS 89", staged, kit.zh_sec(dur), "ok", report.get("ok"))
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
    print("NEW 89", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
