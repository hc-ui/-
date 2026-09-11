#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 77：零知识秒懂排前面。topics-batch4 #77。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/77/，成品中转 成片/77-零知识秒懂排前面.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不重拍成片 40，不重讲定律 001–012。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "零知识秒懂排前面"
STAGED_NAME = "77-零知识秒懂排前面.mp4"


def frame_two_lists(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "排 · 两列表")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0)) + dy),
        "先按门槛分两列",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 320 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (60, y, 510, y + 620), 32, kit.mix(kit.BG, (18, 42, 36), a1))
    d.text((285, y + 56), "秒懂", font=kit.font(40), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 150), "零知识", font=kit.font(52), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
    for idx, line in enumerate(("不用预习", "当场感到不对", "先上")):
        aa = kit.appear(t, 0.40 + idx * 0.12, 0.18)
        if aa < 0.04:
            continue
        yy = y + 250 + idx * 100
        kit.rounded(d, (90, yy, 480, yy + 84), 20, kit.mix(kit.CARD, (22, 48, 42), aa))
        d.text((285, yy + 42), line, font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, aa), anchor="mm")
    kit.check_badge(d, 285, y + 560, kit.appear(t, 0.85, 0.20))

    a2 = kit.appear(t, 0.24)
    kit.rounded(d, (570, y, 1020, y + 620), 32, kit.mix(kit.BG, (42, 24, 22), a2))
    d.text((795, y + 56), "先得关心", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((795, y + 150), "物理量", font=kit.font(52), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")
    for idx, line in enumerate(("先关心那个量", "才感到反常", "往后放")):
        aa = kit.appear(t, 0.52 + idx * 0.12, 0.18)
        if aa < 0.04:
            continue
        yy = y + 250 + idx * 100
        kit.rounded(d, (600, yy, 990, yy + 84), 20, kit.mix(kit.CARD, (48, 28, 26), aa))
        d.text((795, yy + 42), line, font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, aa), anchor="mm")
    kit.x_mark(d, 795, y + 560, kit.appear(t, 1.00, 0.20), 28)

    punch = kit.appear(t, 1.35, 0.24)
    if punch > 0.04:
        y3 = 1000 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y3, 990, y3 + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 85), "零知识秒懂的，先上", font=kit.font(42), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_two_axes(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 叠成一根")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "难度低，不等于门槛低",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(16, 0, a1))
    kit.rounded(d, (70, y, 1010, y + 430), 32, kit.mix(kit.BG, kit.CARD, a1))
    d.text((180, y + 50), "生成难度", font=kit.font(28), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="lm")
    d.text((180, y + 210), "理解门槛", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="lm")

    x0, x1 = 180, 930
    d.line([(x0, y + 110), (x1, y + 110)], fill=kit.mix(kit.CARD, kit.YELLOW, a1), width=8)
    d.line([(x0, y + 270), (x1, y + 270)], fill=kit.mix(kit.CARD, kit.MINT, a1), width=8)
    d.text((x0, y + 150), "低", font=kit.font(26), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((x1, y + 150), "高", font=kit.font(26), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((x0, y + 310), "低", font=kit.font(26), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((x1, y + 310), "高", font=kit.font(26), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")

    slide = kit.appear(t, 0.55, 0.40)
    if slide > 0.04:
        px = int(kit.lerp(x0 + 40, x1 - 80, slide))
        d.ellipse((px - 16, y + 94, px + 16, y + 126), fill=kit.mix(kit.CARD, kit.YELLOW, slide))
        d.text((px, y + 70), "好画", font=kit.font(24), fill=kit.mix(kit.CARD, kit.YELLOW, slide), anchor="mm")
        qx = int(kit.lerp(x0 + 40, x0 + 220, slide))
        d.ellipse((qx - 16, y + 254, qx + 16, y + 286), fill=kit.mix(kit.CARD, kit.MINT, slide))
        d.text((qx, y + 230), "秒懂", font=kit.font(24), fill=kit.mix(kit.CARD, kit.MINT, slide), anchor="mm")

    rows = [
        (0.70, "门槛低", "不用预习就能感到不对", kit.MINT),
        (0.92, "门槛高", "先关心那个量才看得出反常", kit.YELLOW),
    ]
    for ts, head, body, col in rows:
        a = kit.appear(t, ts, 0.20)
        if a < 0.04:
            continue
        yy = 780 + (0 if head == "门槛低" else 160) + int(kit.lerp(16, 0, a))
        kit.rounded(d, (70, yy, 1010, yy + 140), 26, kit.mix(kit.BG, kit.CARD, a))
        d.text((110, yy + 70), head, font=kit.font(40), fill=kit.mix(kit.CARD, col, a), anchor="lm")
        d.text((980, yy + 70), body, font=kit.font(28), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="rm")

    punch = kit.appear(t, 1.35, 0.24)
    if punch > 0.04:
        y3 = 1120 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 170), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y3 + 85), "两根轴别叠成一根", font=kit.font(44), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_stairs(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "收 · 先问门槛")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 220 + int(kit.lerp(16, 0, a0))),
        "理解门槛从低到高",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    steps = [
        (0.16, "极低", "秒懂", True),
        (0.32, "低", "秒懂", True),
        (0.48, "中", "先关心", False),
        (0.64, "高", "先关心", False),
        (0.80, "极高", "往后", False),
    ]
    for idx, (ts, label, mark, front) in enumerate(steps):
        a = kit.appear(t, ts, 0.20)
        if a < 0.04:
            continue
        w = 220 + idx * 70
        h = 92
        x0 = 70 + idx * 36
        y0 = 820 - idx * 92 + int(kit.lerp(18, 0, a))
        fill = (18, 42, 36) if front else (42, 32, 18)
        kit.rounded(d, (x0, y0, x0 + w, y0 + h), 20, kit.mix(kit.BG, fill, a))
        d.text((x0 + 36, y0 + 46), label, font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        col = kit.MINT if front else kit.YELLOW
        d.text((x0 + w - 36, y0 + 46), mark, font=kit.font(30), fill=kit.mix(kit.CARD, col, a), anchor="rm")

    punch = kit.appear(t, 1.20, 0.24)
    if punch > 0.04:
        y3 = 1000 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y3, 990, y3 + 220), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 70), "开局先立完播", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
        d.text((kit.W // 2, y3 + 150), "硬核等可信度立住", font=kit.font(36), fill=kit.mix(kit.CARD, kit.YELLOW, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    """Episode 默认写成 77-long / 加长重切；本集是 NEW，改回 .abroll-cloud/77/。"""
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "77_零知识秒懂排前面"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/77"
        status["source_note"] = "topics-batch4.md #77 / 选题库.md 上线顺序 / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "77_零知识秒懂排前面"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/77"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 77 · 零知识秒懂的排前面

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：`topics-batch4.md` 第 77 条；Drive `选题库.md`「上线顺序」两原则；`topics-batch3.md` #40 未按原题进成片
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/77/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：成片 40 对齐到半夜；成片 12 / 30 / 38 / 39 定律与推演题；#78 先问有没有人想看；成片 70 例子先于概念

钩子：零知识秒懂的，排前面。
诊断：第一原则是理解门槛，不是好不好画；难度低不等于门槛低。
例子：秒懂进前排；先得关心物理量的往后站；两根轴别叠成一根。
收束：排序先问门槛，再问好不好画；别让门槛高的抢开局。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。不重讲定律 001–012。

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
    old = "| 77 | 选题库排序纪律 | `77-零知识秒懂的排前面.mp4` | batch3 #40 未按原题拍 |"
    new = f"| 77 | 选题库排序纪律 | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if old in text:
        text = text.replace(old, new)
    claimed = "- **状态**：已认领 · `.abroll-cloud/77/` · NEW · 目标四十到五十秒"
    verified = f"- **状态**：已核验 · `.abroll-cloud/77/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
    if claimed in text:
        text = text.replace(claimed, verified)
    elif "- **A-roll 角度**：选题库排序纪律还没拍过。" in text and verified not in text:
        text = text.replace(
            "- **A-roll 角度**：选题库排序纪律还没拍过。",
            f"{verified}\n- **A-roll 角度**：选题库排序纪律还没拍过。",
        )
    path.write_text(text, encoding="utf-8")


def patch_delivery_new(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    line = (
        f"| `成片/{STAGED_NAME}` | 1080×1920 h264+aac 44.1k stereo | {kit.zh_sec(duration)} | "
        f"topic 77 云端 NEW（`.abroll-cloud/77/`，选题库排序纪律） |"
    )
    token = f"`成片/{STAGED_NAME}`"
    rows = []
    seen = False
    for raw in text.splitlines():
        if raw.startswith("|") and token in raw:
            if not seen:
                rows.append(line)
                seen = True
            continue
        rows.append(raw)
    if not seen:
        rebuilt = []
        inserted = False
        for raw in rows:
            if (not inserted) and "仙侠云海突进" in raw and raw.strip().startswith("|"):
                rebuilt.append(line)
                inserted = True
            rebuilt.append(raw)
        if not inserted:
            rebuilt.append(line)
        rows = rebuilt
    text = "\n".join(rows)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "零知识秒懂的排前面",
        "staged_name": STAGED_NAME,
        "episode": 77,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "topics-batch4.md #77 · 选题库.md 上线顺序 · 云端 NEW",
        "hooks": "钩子：零知识秒懂的，排前面。\n诊断：第一原则是理解门槛，不是好不好画。\n例子：两列表；两根轴；门槛阶梯。\n收束：别让门槛高的抢开局。",
        "cover_lines": ("零知识秒懂的", "排前面"),
        "avoid": "成片 40 对齐到半夜；成片 12 / 30 / 38 / 39；#78 先问有没有人想看；成片 70 例子先于概念",
        "factory": "topics-batch4 #77",
        "broll": {
            "S02": ("B-两列表.mp4", frame_two_lists),
            "S04": ("B-两根轴.mp4", frame_two_axes),
            "S06": ("B-门槛阶梯.mp4", frame_stairs),
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
    print("DOCS 77", staged, kit.zh_sec(dur), "ok", report.get("ok"))
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
    print("NEW 77", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
