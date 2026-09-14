#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 103：一句只讲一件事。Drive 工厂 103。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/103/，成品中转 成片/103-一句只讲一件事.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
不写本机系统盘与数据盘盘符，不传 Drive，不走 drama-pipeline。
不重做工厂十六秒短切，不重复成片 70 / 71 / 72。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "一句只讲一件事"
STAGED_NAME = "103-一句只讲一件事.mp4"
BANNED = (
    "口头禅",
    "例子先于",
    "先给结论",
    "环境变量",
    "人锅",
    "流水账",
    "目录名",
    "密钥",
    "临时方案",
    "下一期",
    "文件名",
    "C++",
    "ROS",
    "链接",
)


def frame_two_stuffed(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 一句塞两件")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0)) + dy),
        "一句口播里塞两件事",
        font=kit.font(44),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    cards = [
        (0.16, 80, 320, "第一件", "先说了"),
        (0.34, 405, 350, "第二件", "后落下"),
    ]
    for ts, x, y0, head, body in cards:
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = y0 + int(kit.lerp(18, 0, a)) + dy
        kit.rounded(d, (x, y, x + 270, y + 300), 26, kit.mix(kit.BG, kit.CARD, a))
        d.text((x + 135, y + 70), head, font=kit.font(36), fill=kit.mix(kit.CARD, kit.MUTED, a), anchor="mm")
        d.text((x + 135, y + 160), body, font=kit.font(40), fill=kit.mix(kit.CARD, kit.YELLOW, a), anchor="mm")
        if head == "第一件":
            kit.x_mark(d, x + 135, y + 230, kit.appear(t, ts + 0.40, 0.18), 24)
        else:
            kit.check_badge(d, x + 135, y + 230, kit.appear(t, ts + 0.40, 0.18))
    punch = kit.appear(t, 1.10, 0.22)
    if punch > 0.04:
        y = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y, 990, y + 200), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 70), "只记住后一件", font=kit.font(46), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
        d.text((kit.W // 2, y + 140), "前一件当没说", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, punch), anchor="mm")
    return img


def frame_comma_hide(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 逗号藏第二点")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "不是记性差",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.16)
    if a1 > 0.04:
        y = 300 + int(kit.lerp(14, 0, a1)) + dy
        kit.rounded(d, (70, y, 1010, y + 220), 32, kit.mix(kit.BG, kit.CARD, a1))
        d.text((kit.W // 2, y + 70), "两个意思挤在同一句", font=kit.font(42), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
        d.text((kit.W // 2, y + 150), "逗号后面还藏着第二点", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
    a2 = kit.appear(t, 0.42)
    if a2 > 0.04:
        y = 560 + int(kit.lerp(14, 0, a2)) + dy
        kit.rounded(d, (70, y, 500, y + 280), 32, kit.mix(kit.BG, (42, 24, 22), a2))
        d.text((285, y + 80), "前半句", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
        d.text((285, y + 160), "被吃掉", font=kit.font(48), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")
        kit.x_mark(d, 285, y + 230, kit.appear(t, 0.70, 0.20), 26)
        kit.rounded(d, (580, y, 1010, y + 280), 32, kit.mix(kit.BG, kit.CARD, a2))
        d.text((795, y + 80), "后半刀", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
        d.text((795, y + 160), "被抓住", font=kit.font(48), fill=kit.mix(kit.CARD, kit.YELLOW, a2), anchor="mm")
    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y = 900 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 160), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 80), "听的人只能抓住后半刀", font=kit.font(40), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_one_cut(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 一句只办一件")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "一句只办一件事",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    rows = [
        (0.16, "1", "一个意思", "先说清楚"),
        (0.40, "2", "一个动作", "只留一件"),
        (0.64, "3", "下一件", "先切一刀"),
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
    punch = kit.appear(t, 1.28, 0.22)
    if punch > 0.04:
        y = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y, 990, y + 200), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 70), "要讲下一件", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
        d.text((kit.W // 2, y + 140), "先切一刀", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, punch), anchor="mm")
    return img


def frame_count_points(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 写稿先数点")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "下次写稿先数点",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 500), 32, kit.mix(kit.BG, (42, 24, 22), a1))
    d.text((285, y + 56), "挤在一句", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "两个动作", font=kit.font(48), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    d.text((285, y + 270), "听不清", font=kit.font(36), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    kit.x_mark(d, 285, y + 380, kit.appear(t, 0.55, 0.22), 36)
    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (580, y, 1010, y + 500), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((795, y + 56), "拆开写", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((795, y + 180), "一个动作", font=kit.font(48), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    d.text((795, y + 270), "一句说完", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    kit.check_badge(d, 795, y + 380, kit.appear(t, 0.70, 0.22))
    stamp = kit.appear(t, 1.20, 0.24)
    if stamp > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, stamp)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), stamp))
        d.text((kit.W // 2, y3 + 70), "一句里只留一个动作", font=kit.font(40), fill=kit.mix(kit.BG, kit.MINT, stamp), anchor="mm")
        d.text((kit.W // 2, y3 + 140), "再说下一句", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, stamp), anchor="mm")
    return img


def frame_stamp(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "收 · 拆开才算")
    dy = kit.breathe(t, 6)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 230 + int(kit.lerp(16, 0, a0))),
        "看见第二点，就拆开",
        font=kit.font(44),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.18)
    if a1 > 0.04:
        cx, cy = 540, 620 + dy
        r = 230
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=kit.mix(kit.BG, (18, 42, 36), a1))
        d.text((cx, cy - 40), "拆开才算讲过", font=kit.font(48), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
        d.text((cx, cy + 50), "对照只打这一点", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.check_badge(d, cx, cy + 140, kit.appear(t, 0.70, 0.22))
    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y = 960 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 85), "前一件请当成没说", font=kit.font(40), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status.update({
            "project_name": "103_一句只讲一件事",
            "cut": "new-40s",
            "draft": ".abroll-cloud/103",
            "memory_root": "我的云端硬盘/AI视频项目/103_一句只讲一件事/",
            "duration": round(duration, 3),
            "duration_zh": kit.zh_sec(duration),
            "not": "drama-pipeline / 仙侠连载 / 本机系统盘与数据盘盘符 / Drive 上传 / freeze-pad",
        })
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    (ROOT / "项目说明.md").write_text(
        f"""# 103 · 一句只讲一件事

普通短视频 / 知识口播。NEW，不是重做。

- **选题**：Drive 只读工厂 `103_一句只讲一件事`
- **记忆库项目根**：`我的云端硬盘/AI视频项目/103_一句只讲一件事/`
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`.abroll-cloud/103/`
- **云端 only**：不写本机系统盘与数据盘盘符，不传 Drive
- **避开**：成片 70 / 71 / 72；兄弟 96 / 97 / 98 / 99 / 100
- **时长**：约 {kit.zh_sec(duration)}

钩子：一句只讲一件事。
诊断：一句里塞两件事，听众只记住后一件。
做法：一句只办一件事。一个意思，一个动作。先切一刀。
收束：塞在一句里的前一件，请当成没说。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头十二条，口播十八句，时间轴闭合。不定格、不慢放注水。
""",
        encoding="utf-8",
    )
    (ROOT / "时长.md").write_text(
        f"""# 成片 103 时长（中文秒）

云端 NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 工厂短切 | 新时长 | 草稿 |
|----|------|----------|--------|------|
| 103 | `{STAGED_NAME}` | 工厂 103 号约十六秒（不重做） | {kit.zh_sec(duration)} | `.abroll-cloud/103/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。十二镜 / 十八句。
不重做 00–102，不拷工厂成片。
""",
        encoding="utf-8",
    )
    (ROOT / "路径依据.md").write_text(
        f"""# 103 路径依据（中文）

Drive 上没有名为 `G-DRIVE-LAYOUT.md` 的文件。G 盘怎么放，以记忆库现行页为准。

## 读过的依据

1. 共享记忆库《本机公共路径与强制约束》「所有视频统一落盘（2026-09-12）」：新视频项目统一进 `我的云端硬盘/AI视频项目/<NN_中文项目名>/`；成品名 `00_最终成片_*`，封面名 `00_封面_*`；渲染临时只进 `AI视频项目/_scratch/`。
2. 同页「G 盘根目录归类（2026-09-14）」：项目素材、工程、中间文件、封面和成片仍进 `AI视频项目/`，不得用 `01_视频素材与成片` 替代项目工作区。
3. Drive 根《【分类与同步规则说明】》（2026-09-14）：`AI视频项目` 是所有新视频项目和临时渲染的固定入口，请勿移动或改名。

## 本集记忆库路径

| 用途 | 路径 |
|------|------|
| 项目根 | `我的云端硬盘/AI视频项目/103_一句只讲一件事/` |
| 工程成片 | `00_最终成片_一句只讲一件事.mp4` |
| 封面 | `00_封面_一句只讲一件事.jpg` |
| 渲染临时 | `我的云端硬盘/AI视频项目/_scratch/103_一句只讲一件事/` |
| 不进 | `01_视频素材与成片`（非项目素材区） |

## 本云端会话实际落盘

本机网盘未挂载，按记忆库「目标根不可用时不回退系统盘 / 数据盘」：草稿只写仓库，不写本机系统盘与数据盘盘符，不传 Drive。

| 用途 | 路径 |
|------|------|
| 草稿根 | `.abroll-cloud/103/` |
| 成片中转 | `成片/{STAGED_NAME}` |
| 工程成片 | `.abroll-cloud/103/00_最终成片_{NAME}.mp4` |
| 核验时长 | {kit.zh_sec(duration)} |

工厂短切约十六秒，只读对照，不重做、不覆盖。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    section = f"""## 103. 一句只讲一件事

- **状态**：已核验 · `.abroll-cloud/103/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}
- **A-roll 角度**：工厂 `103_一句只讲一件事` 短切。成片号 103 空着。只打「一句只讲一件事」：一句里塞两件事，听众只记住后一件，前一件当没说。一句只办一件事。一个意思，一个动作。要讲下一件，先切一刀。不讲口头禅，不讲例子先于概念，不讲先给结论。
- **B-roll 想法**：两件事只剩后一件；逗号藏第二点；一个意思一个动作先切一刀；写稿先数点；拆开才算讲过。
- **来源笔记**：Drive 只读工厂 `103_一句只讲一件事`（claim：白底小灯 A-roll + 黑底信息图 B-roll；工厂成片约十六秒，本集不拷）
- **成片名**：`{STAGED_NAME}`
- **避开**：成片 70 例子先于概念；成片 71 口头禅在偷时长；成片 72 先给结论再展开；兄弟 96/97/98/99/100
"""
    text = path.read_text(encoding="utf-8")
    row = f"| 103 | 工厂知识口播 | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if "| 103 |" not in text and "| 99 |" in text:
        lines = []
        for raw in text.splitlines():
            lines.append(raw)
            if raw.startswith("| 99 |"):
                lines.append(row)
        text = "\n".join(lines)
    if "## 103. 一句只讲一件事" not in text:
        text = text.rstrip() + "\n\n" + section
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "一句只讲一件事",
        "staged_name": STAGED_NAME,
        "episode": 103,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "Drive 工厂 103_一句只讲一件事 · 云端 NEW",
        "hooks": "钩子：一句只讲一件事。\n诊断：一句里塞两件事，只记住后一件。\n做法：一句只办一件事。一个意思，一个动作。先切一刀。\n收束：塞在一句里的前一件，请当成没说。",
        "cover_lines": ("一句只讲", "一件事"),
        "avoid": "成片 70 / 71 / 72；兄弟 96-100",
        "factory": "Drive 工厂 103_一句只讲一件事",
        "broll": {
            "S02": ("B-塞两件只记后一件.mp4", frame_two_stuffed),
            "S04": ("B-逗号藏第二点.mp4", frame_comma_hide),
            "S06": ("B-一个意思先切一刀.mp4", frame_one_cut),
            "S08": ("B-写稿先数点.mp4", frame_count_points),
            "S10": ("B-拆开才算讲过.mp4", frame_stamp),
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
    print("NEW 103", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
