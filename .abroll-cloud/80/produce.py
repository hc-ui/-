#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 80：体力型杂务。topics-batch4 #80。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/80/，成品中转 成片/80-体力型杂务.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不重复成片 28 别接报销采购、成片 46 六十分及格。
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

NAME = "体力型杂务"
STAGED_NAME = "80-体力型杂务.mp4"
WORKSPACE_DRAFT = Path("/workspace/.abroll-cloud/80")


def frame_four_chores(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "认 · 四样")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0)) + dy),
        "先举手认这四样",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    cards = [
        (0.16, "1", "卫生值日", "工位扫完就停"),
        (0.34, "2", "仪器维护", "例行检查打勾"),
        (0.52, "3", "收发快递", "送到手就交"),
        (0.70, "4", "盖章跑腿", "章盖完人回"),
    ]
    for idx, (ts, num, head, body) in enumerate(cards):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        col = idx % 2
        row = idx // 2
        x0 = 70 + col * 480
        y0 = 320 + row * 280 + int(kit.lerp(16, 0, a))
        kit.rounded(d, (x0, y0, x0 + 450, y0 + 250), 28, kit.mix(kit.BG, kit.CARD, a))
        d.ellipse((x0 + 28, y0 + 78, x0 + 120, y0 + 170), fill=kit.mix(kit.CARD, kit.MINT, a))
        d.text((x0 + 74, y0 + 124), num, font=kit.font(40), fill=kit.mix(kit.MINT, kit.INK, a), anchor="mm")
        d.text((x0 + 250, y0 + 90), head, font=kit.font(40), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="mm")
        d.text((x0 + 250, y0 + 160), body, font=kit.font(26), fill=kit.mix(kit.CARD, kit.MUTED, a), anchor="mm")
        kit.check_badge(d, x0 + 390, y0 + 48, kit.appear(t, ts + 0.28, 0.18))

    punch = kit.appear(t, 1.25, 0.24)
    if punch > 0.04:
        y3 = 920 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 85), "边界清楚，做完有终点", font=kit.font(42), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_occupy(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "占 · 体力活")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "占住的是体力活",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 320 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 510, y + 520), 32, kit.mix(kit.BG, (22, 40, 36), a1))
    d.text((290, y + 56), "举手占住", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    items = [("卫生清单", 0.40), ("快递袋", 0.58), ("印章", 0.76)]
    for i, (label, ts) in enumerate(items):
        aa = kit.appear(t, ts, 0.20)
        iy = y + 130 + i * 110
        kit.rounded(d, (110, iy, 470, iy + 88), 18, kit.mix(kit.CARD, (18, 36, 32), aa))
        d.text((200, iy + 44), label, font=kit.font(34), fill=kit.mix(kit.CARD, kit.WHITE, aa), anchor="lm")
        kit.check_badge(d, 420, iy + 44, kit.appear(t, ts + 0.18, 0.16))
    d.text((290, y + 470), "勾完就停", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (540, y, 1010, y + 520), 32, kit.mix(kit.BG, (42, 24, 22), a2))
    d.text((775, y + 56), "别占这个位", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((775, y + 220), "账本", font=kit.font(64), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")
    d.text((775, y + 320), "没有终点", font=kit.font(36), fill=kit.mix(kit.CARD, kit.YELLOW, a2), anchor="mm")
    kit.x_mark(d, 775, y + 410, kit.appear(t, 0.90, 0.22), 36)

    punch = kit.appear(t, 1.30, 0.24)
    if punch > 0.04:
        y3 = 900 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 180), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 90), "不是账本", font=kit.font(52), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_endpoint(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "收 · 有终点")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "有终点才举手",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 320 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 460), 32, kit.mix(kit.BG, kit.CARD, a1))
    d.text((285, y + 56), "反复纠缠", font=kit.font(34), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    cx, cy, r = 285, y + 210, 88
    spin = (t * 90) % 360
    if a1 > 0.04:
        box = (cx - r, cy - r, cx + r, cy + r)
        d.ellipse(box, outline=kit.mix(kit.CARD, (48, 52, 62), a1), width=12)
        d.arc(box, start=spin, end=spin + 250, fill=kit.mix(kit.CARD, kit.RED, a1), width=12)
    kit.x_mark(d, 285, y + 370, kit.appear(t, 0.70, 0.20), 30)
    d.text((285, y + 420), "没终点别接", font=kit.font(28), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (540, y, 1010, y + 460), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((775, y + 56), "做完即止", font=kit.font(34), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    stamp = kit.appear(t, 0.55, 0.28)
    if stamp > 0.04:
        sx, sy = 775, y + 210
        col = kit.mix(kit.CARD, kit.MINT, stamp)
        d.ellipse((sx - 92, sy - 92, sx + 92, sy + 92), outline=col, width=10)
        d.text((sx, sy), "停", font=kit.font(72), fill=col, anchor="mm")
    kit.check_badge(d, 775, y + 370, kit.appear(t, 0.88, 0.18))
    d.text((775, y + 420), "勾上就走", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")

    q = 0.45 + 0.55 * abs(math.sin(t * 2.2))
    d.text((kit.W // 2, 860 + dy), "做完有没有终点？", font=kit.font(40), fill=kit.mix(kit.CARD, kit.YELLOW, q), anchor="mm")

    punch = kit.appear(t, 1.20, 0.24)
    if punch > 0.04:
        y3 = 940 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 180), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 90), "做完就停", font=kit.font(52), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    """Episode 默认写成 80-long / 加长重切；本集是 NEW，改回 .abroll-cloud/80/。"""
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "80_体力型杂务"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/80"
        status["source_note"] = "topics-batch4.md #80 / 备忘录第二节 1 主动认领体力型杂务 / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "80_体力型杂务"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/80"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 80 · 主动认领体力型杂务

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：`topics-batch4.md` 第 80 条；Drive 备忘录第二节 1「主动认领体力型杂务」
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/80/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：成片 28 别接报销采购；成片 46 六十分 / 评优 / 租金；成片 16 秒回
- **时长**：{kit.zh_sec(duration)}（目标四十到五十秒）

钩子：开学先认领体力型杂务。
诊断：不是等人派活，是自己举手占住四样有终点的体力活。
例子：卫生值日、仪器维护、收发快递、盖章跑腿；勾完就停。
收束：有终点才举手；体力型杂务，请主动认领。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头九条，口播十八句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")
    (ROOT / "80-DURATION.md").write_text(
        f"""# 成片 80 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 工厂短切 | 新时长 | 草稿 |
|----|------|----------|--------|------|
| 80 | `{STAGED_NAME}` | 无（本号未进成片） | {kit.zh_sec(duration)} | `.abroll-cloud/80/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。九镜 / 十八句。禁止 `tpad=stop_mode=clone`。
不重做 28（别接报销）、46（六十分及格）。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    old_row = "| 80 | 专硕杂务认领 | `80-主动认领体力型杂务.mp4` | 未拍 |"
    claimed_row = "| 80 | 专硕杂务认领 | `80-体力型杂务.mp4` | 已认领 `.abroll-cloud/80/` |"
    new_row = f"| 80 | 专硕杂务认领 | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if old_row in text:
        text = text.replace(old_row, new_row)
    elif claimed_row in text:
        text = text.replace(claimed_row, new_row)
    elif f"`{STAGED_NAME}`" in text and "| 80 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 80 |"):
                lines.append(new_row)
            else:
                lines.append(raw)
        text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    suggest = "- **成片名建议**：`80-主动认领体力型杂务.mp4`"
    locked = f"- **成片名**：`{STAGED_NAME}`"
    if suggest in text:
        text = text.replace(suggest, locked)
    claimed = "- **状态**：已认领 · `.abroll-cloud/80/` · NEW · 目标四十到五十秒"
    verified = f"- **状态**：已核验 · `.abroll-cloud/80/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
    if claimed in text:
        text = text.replace(claimed, verified)
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def patch_delivery_new(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    new = (
        f"| `成片/{STAGED_NAME}` | 1080×1920 h264+aac 44.1k stereo | {kit.zh_sec(duration)} | "
        f"topic 80 云端 NEW（备忘录第二节 1 主动认领体力型杂务；不重做 28/46） |"
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


def sync_workspace_draft() -> None:
    """Keep /workspace/.abroll-cloud/80/ in sync when producing from a worktree."""
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
        "full_title": "主动认领体力型杂务",
        "staged_name": STAGED_NAME,
        "episode": 80,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "topics-batch4.md #80 · 备忘录第二节 1 主动认领体力型杂务 · 云端 NEW",
        "hooks": "钩子：开学先认领体力型杂务。\n诊断：自己举手占住四样有终点的体力活。\n例子：卫生、仪器、快递、盖章；勾完就停。\n收束：有终点才举手。",
        "cover_lines": ("开学先认领", "体力型杂务"),
        "avoid": "成片 28 别接报销采购；成片 46 六十分 / 评优 / 租金；成片 16 秒回",
        "factory": "topics-batch4 #80",
        "broll": {
            "S02": ("B-四样体力活.mp4", frame_four_chores),
            "S04": ("B-占住体力活.mp4", frame_occupy),
            "S06": ("B-有终点才接.mp4", frame_endpoint),
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
    sync_workspace_draft()
    print("DOCS 80", staged, kit.zh_sec(dur), "ok", report.get("ok"))
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
    sync_workspace_draft()
    print("NEW 80", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
