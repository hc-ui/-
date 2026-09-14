#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 105：对比比罗列狠。Drive 工厂 105。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/105/，成品中转 成片/105-对比比罗列狠.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
不写 C/D，禁止 Drive 上传，不走 drama-pipeline。
不重复成片 13 对照卡，不拷工厂十五秒短切。本轮最后号，不开 106。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "对比比罗列狠"
STAGED_NAME = "105-对比比罗列狠.mp4"
BANNED = (
    "对照卡",
    "形容词",
    "问句",
    "金句",
    "截图",
    "例子先于",
    "下一期",
    "文件名",
    "C++",
    "ROS",
    "人锅",
    "环境变量",
    "流水账",
    "密钥",
    "临时方案",
)


def frame_list_skip(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 一条都没进")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0)) + dy),
        "列三条优点",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    cards = [
        (0.16, 80, 320, "优点一", "扫过了"),
        (0.34, 405, 350, "优点二", "没停住"),
        (0.52, 730, 320, "优点三", "也散了"),
    ]
    for ts, x, y0, head, body in cards:
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = y0 + int(kit.lerp(18, 0, a)) + dy
        kit.rounded(d, (x, y, x + 270, y + 280), 26, kit.mix(kit.BG, kit.CARD, a))
        d.text((x + 135, y + 70), head, font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a), anchor="mm")
        d.text((x + 135, y + 150), body, font=kit.font(34), fill=kit.mix(kit.CARD, kit.YELLOW, a), anchor="mm")
        kit.x_mark(d, x + 135, y + 220, kit.appear(t, ts + 0.40, 0.18), 22)
    punch = kit.appear(t, 1.18, 0.22)
    if punch > 0.04:
        y = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y, 990, y + 200), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 70), "听众一条都没进", font=kit.font(44), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
        d.text((kit.W // 2, y + 140), "往下堆，上面先散", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, punch), anchor="mm")
    return img


def frame_before_after(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 丢一个对照")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "以前这样，现在那样",
        font=kit.font(46),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.16)
    if a1 > 0.04:
        y = 300 + int(kit.lerp(14, 0, a1)) + dy
        kit.rounded(d, (70, y, 500, y + 460), 32, kit.mix(kit.BG, (42, 24, 22), a1))
        d.text((285, y + 70), "以前", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
        d.text((285, y + 190), "这样", font=kit.font(56), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
        d.text((285, y + 280), "旧做法", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.x_mark(d, 285, y + 370, kit.appear(t, 0.70, 0.20), 30)
    a2 = kit.appear(t, 0.30)
    if a2 > 0.04:
        y = 300 + int(kit.lerp(14, 0, a2)) + dy
        kit.rounded(d, (580, y, 1010, y + 460), 32, kit.mix(kit.BG, (22, 40, 36), a2))
        d.text((795, y + 70), "现在", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
        d.text((795, y + 190), "那样", font=kit.font(56), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
        d.text((795, y + 280), "新结果", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
        kit.check_badge(d, 795, y + 370, kit.appear(t, 0.88, 0.20))
    punch = kit.appear(t, 1.18, 0.22)
    if punch > 0.04:
        y = 830 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 180), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 90), "差别自己站出来", font=kit.font(42), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_contrast_speaks(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对照 · 罗列 / 对比")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "对比让差别自己说话",
        font=kit.font(42),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 500), 32, kit.mix(kit.BG, (42, 24, 22), a1))
    d.text((285, y + 56), "罗列", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "让人跳过", font=kit.font(48), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    d.text((285, y + 270), "清单越长越空", font=kit.font(32), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    kit.x_mark(d, 285, y + 380, kit.appear(t, 0.55, 0.22), 36)
    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (580, y, 1010, y + 500), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((795, y + 56), "对比", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((795, y + 180), "自己说话", font=kit.font(48), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    d.text((795, y + 270), "两栏一对就看见", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    kit.check_badge(d, 795, y + 380, kit.appear(t, 0.70, 0.22))
    stamp = kit.appear(t, 1.20, 0.24)
    if stamp > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, stamp)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), stamp))
        d.text((kit.W // 2, y3 + 70), "哪边该删立刻看见", font=kit.font(42), fill=kit.mix(kit.BG, kit.MINT, stamp), anchor="mm")
        d.text((kit.W // 2, y3 + 140), "不用再解释一遍", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, stamp), anchor="mm")
    return img


def frame_two_columns(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 先画两栏")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "先画左右两栏",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    rows = [
        (0.16, "左", "旧做法", "写清以前怎样"),
        (0.40, "右", "新结果", "写清现在怎样"),
        (0.64, "删", "再决定", "哪边先拿掉"),
    ]
    for idx, (ts, num, head, body) in enumerate(rows):
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = 300 + idx * 168 + int(kit.lerp(16, 0, a))
        kit.rounded(d, (90, y, 990, y + 148), 26, kit.mix(kit.BG, kit.CARD, a))
        d.ellipse((128, y + 34, 220, y + 126), fill=kit.mix(kit.CARD, kit.MINT, a))
        d.text((174, y + 80), num, font=kit.font(32), fill=kit.mix(kit.MINT, kit.INK, a), anchor="mm")
        d.text((248, y + 50), head, font=kit.font(40), fill=kit.mix(kit.CARD, kit.MINT, a), anchor="lm")
        d.text((248, y + 108), body, font=kit.font(28), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        kit.check_badge(d, 900, y + 74, kit.appear(t, ts + 0.28, 0.18))
    punch = kit.appear(t, 1.28, 0.22)
    if punch > 0.04:
        y = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y, 990, y + 200), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 70), "再决定删哪边", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
        d.text((kit.W // 2, y + 140), "删不掉的，才该讲", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, punch), anchor="mm")
    return img


def frame_stamp(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "收 · 还没讲完")
    dy = kit.breathe(t, 6)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 230 + int(kit.lerp(16, 0, a0))),
        "别再开一张优点清单",
        font=kit.font(44),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.18)
    if a1 > 0.04:
        cx, cy = 540, 620 + dy
        r = 230
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=kit.mix(kit.BG, (18, 42, 36), a1))
        d.text((cx, cy - 40), "清单还在堆", font=kit.font(50), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
        d.text((cx, cy + 50), "请当成没讲完", font=kit.font(34), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.check_badge(d, cx, cy + 140, kit.appear(t, 0.70, 0.22))
    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y = 960 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 85), "清单请当成还没讲完", font=kit.font(40), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "105_对比比罗列狠"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/105"
        status["memory_dir"] = "AI视频项目/105_对比比罗列狠"
        status["source_note"] = "Drive 工厂 105_对比比罗列狠 / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status["duration"] = round(duration, 3)
        status["duration_zh"] = kit.zh_sec(duration)
        status["distinct_from"] = [
            "13-对照卡",
            "35-数字比形容词狠",
            "70-例子先于概念",
            "102-评审只看格式",
        ]
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "105_对比比罗列狠"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8")
        report["script_guard"] = {w: (w not in vo) for w in BANNED}
        report["ok"] = bool(report.get("ok")) and all(report["script_guard"].values())
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/105"
        data["source_note"] = "Drive 工厂 105_对比比罗列狠 / 云端 NEW"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 105 · 对比比罗列狠

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。本轮最后号，不开 106。

- **选题**：Drive 只读工厂 `105_对比比罗列狠`
- **路径依据**：先读 `.abroll-cloud/G-DRIVE-LAYOUT.md`。记忆库新视频进 `AI视频项目/105_对比比罗列狠/`，成品名 `00_最终成片_*`。云端草稿 `.abroll-cloud/105/`，可看中转 `成片/{STAGED_NAME}`。不写盘符，不写 C/D。
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/105/`
- **云端 only**：不写 C/D，不传 Drive
- **避开**：成片 13 对照卡；成片 35 数字比形容词狠；成片 70 例子先于概念；#102 评审只看格式

钩子：对比比罗列狠。
诊断：列三条优点，听众一条都没进。
做法：丢一个对照。先画左右两栏，再决定删哪边。
收束：清单请当成还没讲完。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头十二条，口播十八句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")
    (ROOT / "时长.md").write_text(
        f"""# 成片 105 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 工厂短切 | 新时长 | 草稿 |
|----|------|----------|--------|------|
| 105 | `{STAGED_NAME}` | 工厂 105 号短切约十五秒（未进成片） | {kit.zh_sec(duration)} | `.abroll-cloud/105/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。十二镜 / 十八句。禁止冻帧垫时长。
路径依据：`.abroll-cloud/G-DRIVE-LAYOUT.md` → `AI视频项目/105_对比比罗列狠/`；本轮中转 `成片/{STAGED_NAME}`。不写 C/D。
不重做 00–104，不拷工厂成片，不开 106。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    section = f"""## 105. 对比比罗列狠

- **状态**：已核验 · `.abroll-cloud/105/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}
- **A-roll 角度**：工厂 `105_对比比罗列狠` 短切。只打「对比比罗列狠」：列三条优点听众一条都没进；丢一个对照，差别自己说话。先画左右两栏，再决定删哪边。不讲对照卡只打一点，不讲问句比陈述，不讲金句截图。本轮最后号，不开 106。
- **B-roll 想法**：三条优点全打叉；以前 / 现在两栏；罗列跳过对对比说话；左右两栏再删边；清单请当成还没讲完。
- **来源笔记**：Drive 只读工厂 `105_对比比罗列狠`（claim：白底小灯 A-roll + 黑底信息图 B-roll；`/workspace/成片/` 无本条）
- **成片名**：`{STAGED_NAME}`
- **避开**：成片 13 对照卡；成片 35 数字比形容词狠；成片 70 例子先于概念；#102 评审只看格式
"""
    text = path.read_text(encoding="utf-8")
    if "## 105. 对比比罗列狠" in text:
        verified = f"- **状态**：已核验 · `.abroll-cloud/105/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
        lines = []
        for raw in text.splitlines():
            if raw.startswith("- **状态**：") and "105" in text[max(0, text.find(raw) - 80):text.find(raw) + 20]:
                lines.append(verified)
            else:
                lines.append(raw)
        text = "\n".join(lines)
        if not text.endswith("\n"):
            text += "\n"
        path.write_text(text, encoding="utf-8")
        return
    text = text.rstrip() + "\n\n" + section
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "对比比罗列狠",
        "staged_name": STAGED_NAME,
        "episode": 105,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "Drive 工厂 105_对比比罗列狠 · 云端 NEW",
        "hooks": "钩子：对比比罗列狠。\n诊断：列三条优点，一条都没进。\n做法：丢一个对照，先画左右两栏。\n收束：清单请当成还没讲完。",
        "cover_lines": ("对比", "比罗列狠"),
        "avoid": "成片 13 对照卡；成片 35 数字比形容词狠；成片 70 例子先于概念；#102 评审只看格式",
        "factory": "Drive 工厂 105_对比比罗列狠",
        "broll": {
            "S02": ("B-一条都没进.mp4", frame_list_skip),
            "S04": ("B-以前现在.mp4", frame_before_after),
            "S06": ("B-对比自己说话.mp4", frame_contrast_speaks),
            "S08": ("B-左右两栏.mp4", frame_two_columns),
            "S10": ("B-清单还没讲完.mp4", frame_stamp),
        },
    })


def main() -> None:
    if "--docs-only" in sys.argv:
        ep = episode()
        staged = Path("/workspace/成片") / STAGED_NAME
        draft = ROOT / f"00_最终成片_{NAME}.mp4"
        data = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
        dur = kit.probe_dur(staged if staged.exists() else draft)
        ep.write_docs(dur, staged if staged.exists() else draft, data)
        rewrite_docs(dur)
        patch_topics(dur)
        return
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8")
    hit = [w for w in BANNED if w in vo]
    if hit:
        raise SystemExit(f"banned phrases in VO: {hit}")
    phrases = [ln.strip() for ln in (ROOT / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(phrases) != 18:
        raise SystemExit(f"need 18 phrases, got {len(phrases)}")
    ep = episode()
    report = ep.produce()
    staged = Path("/workspace/成片") / STAGED_NAME
    dur = kit.probe_dur(staged) if staged.exists() else float(report.get("chengpian_duration_s") or report["video"]["duration_s"])
    rewrite_docs(dur)
    patch_topics(dur)
    print("NEW 105", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
