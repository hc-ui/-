#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 104：金句要能截图。Drive 工厂 104。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/104/，成品中转 成片/104-金句要能截图.mp4。
工程成品名 00_最终成片_金句要能截图.mp4（记忆库命名）。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
不写 C/D。不拷工厂十六秒短切。不走 drama-pipeline。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "金句要能截图"
STAGED_NAME = "104-金句要能截图.mp4"
BANNED = (
    "一句只讲一件事",
    "问句比陈述",
    "收束要落回",
    "重复不是啰嗦",
    "停顿也是",
    "下一期",
    "文件名",
    "C++",
    "ROS",
    "密钥",
    "环境变量",
    "流水账",
    "人锅",
    "临时方案",
    "行动指令",
)


def frame_three_seconds(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 截不清")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0)) + dy),
        "截图看不清",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    cards = [
        (0.16, 80, 320, "字挤成一团", "滑过去了"),
        (0.34, 405, 350, "满屏都是字", "金句被埋"),
        (0.52, 730, 320, "只待三秒", "耳朵里没了"),
    ]
    for ts, x, y0, head, body in cards:
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = y0 + int(kit.lerp(18, 0, a)) + dy
        kit.rounded(d, (x, y, x + 270, y + 280), 26, kit.mix(kit.BG, kit.CARD, a))
        d.text((x + 135, y + 70), head, font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a), anchor="mm")
        d.text((x + 135, y + 150), body, font=kit.font(34), fill=kit.mix(kit.CARD, kit.YELLOW, a), anchor="mm")
        kit.x_mark(d, x + 135, y + 220, kit.appear(t, ts + 0.40, 0.18), 22)
    punch = kit.appear(t, 1.18, 0.22)
    if punch > 0.04:
        y = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y, 990, y + 200), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 70), "只在耳朵里待三秒", font=kit.font(44), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
        d.text((kit.W // 2, y + 140), "这一帧站不住", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, punch), anchor="mm")
    return img


def frame_three_rules(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 能截图")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "能截图的金句",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    rows = [
        (0.16, "1", "字少", "一眼能看完"),
        (0.40, "2", "对比强", "远了也分得清"),
        (0.64, "3", "一句站得住", "不靠上下文"),
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
        d.text((kit.W // 2, y + 70), "讲解可以长", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
        d.text((kit.W // 2, y + 140), "金句必须短", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, punch), anchor="mm")
    return img


def frame_blur_vs_clear(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对照 · 糊 / 清")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "一屏只留一句",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 500), 32, kit.mix(kit.BG, (42, 24, 22), a1))
    d.text((285, y + 56), "浅底糊字", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "白字浅底", font=kit.font(48), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    d.text((285, y + 270), "远了就糊", font=kit.font(36), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    kit.x_mark(d, 285, y + 380, kit.appear(t, 0.55, 0.22), 36)
    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (580, y, 1010, y + 500), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((795, y + 56), "深底大字", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((795, y + 180), "对比够强", font=kit.font(48), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    d.text((795, y + 270), "才截得清", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    kit.check_badge(d, 795, y + 380, kit.appear(t, 0.70, 0.22))
    stamp = kit.appear(t, 1.20, 0.24)
    if stamp > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, stamp)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), stamp))
        d.text((kit.W // 2, y3 + 70), "留下能截的那一句", font=kit.font(42), fill=kit.mix(kit.BG, kit.MINT, stamp), anchor="mm")
        d.text((kit.W // 2, y3 + 140), "别把解释也糊上去", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, stamp), anchor="mm")
    return img


def frame_moments(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "验 · 朋友圈")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "这一帧发朋友圈",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.16)
    if a1 > 0.04:
        y = 300 + int(kit.lerp(14, 0, a1)) + dy
        kit.rounded(d, (160, y, 920, y + 520), 36, kit.mix(kit.BG, kit.CARD, a1))
        d.rounded_rectangle((210, y + 40, 870, y + 120), radius=20, fill=kit.mix(kit.CARD, (36, 40, 52), a1))
        d.text((540, y + 80), "朋友圈", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
        d.text((540, y + 220), "他看得懂吗", font=kit.font(56), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
        d.text((540, y + 320), "看不懂，就不算金句", font=kit.font(34), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.check_badge(d, 540, y + 420, kit.appear(t, 0.80, 0.20))
    punch = kit.appear(t, 1.18, 0.22)
    if punch > 0.04:
        y = 880 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 180), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 90), "先问这一帧站不站得住", font=kit.font(40), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_stamp(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "收 · 截得清")
    dy = kit.breathe(t, 6)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 230 + int(kit.lerp(16, 0, a0))),
        "截得清，才留得住",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.18)
    if a1 > 0.04:
        cx, cy = 540, 620 + dy
        r = 230
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=kit.mix(kit.BG, (18, 42, 36), a1))
        d.text((cx, cy - 40), "截得清", font=kit.font(56), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
        d.text((cx, cy + 50), "才留得住", font=kit.font(36), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.check_badge(d, cx, cy + 140, kit.appear(t, 0.70, 0.22))
    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y = 960 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 85), "截不清，请当成没写过", font=kit.font(40), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status.update({
            "project_name": "104_金句要能截图",
            "cut": "new-40s",
            "draft": ".abroll-cloud/104",
            "source_note": "Drive 工厂 104_金句要能截图 / 云端 NEW",
            "replaced_short_cut_s": 0,
            "duration": round(duration, 3),
            "duration_zh": kit.zh_sec(duration),
            "windows_paths": False,
            "drive_upload": False,
            "path_basis": "共享记忆库 本机公共路径与强制约束 · 新片进 AI视频项目/NN_中文项目名 · 成品 00_最终成片_* · 云端中转 成片/",
            "distinct_from": [
                "103-一句只讲一件事",
                "85-问句比陈述狠",
                "86-收束要落回钩子",
                "87-重复不是啰嗦",
                "12-三秒留人",
                "25-行动指令",
            ],
        })
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "104_金句要能截图"
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
        data["draft"] = ".abroll-cloud/104"
        data["source_note"] = "Drive 工厂 104_金句要能截图 / 云端 NEW"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 104 · 金句要能截图

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：Drive 只读工厂 `104_金句要能截图`
- **路径依据**：`.abroll-cloud/G-DRIVE-LAYOUT.md`；记忆库项目根 `我的云端硬盘/AI视频项目/104_金句要能截图/`
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/104/`
- **云端 only**：不写 C/D，不覆盖工厂十六秒短切
- **避开**：#103 一句只讲一件事；工厂 85 问句比陈述狠；工厂 86 收束要落回钩子；工厂 87 重复不是啰嗦；成片 12 三秒留人；成片 25 行动指令

钩子：金句要能截图。
诊断：截图看不清，只在耳朵里待三秒。
做法：字少、对比强、一句站得住。
收束：截得清才留得住。截不清，请当成没写过。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头十二条，口播十八句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")
    (ROOT / "时长.md").write_text(
        f"""# 成片 104 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 工厂短切 | 新时长 | 草稿 |
|----|------|----------|--------|------|
| 104 | `{STAGED_NAME}` | 工厂 104 号约十六秒（未进成片） | {kit.zh_sec(duration)} | `.abroll-cloud/104/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。十二镜 / 十八句。禁止冻帧垫时长。
路径依据见 `路径依据.md` 与 `.abroll-cloud/G-DRIVE-LAYOUT.md`。
不重做 00–103，不抢 100–103，不拷工厂成片。不写本机系统盘与数据盘盘符。
""",
        encoding="utf-8",
    )
    (ROOT / "路径依据.md").write_text(
        f"""# 104 路径依据（中文）

先读 `.abroll-cloud/G-DRIVE-LAYOUT.md`。Drive 上没有同名文件；G 盘怎么放，以记忆库现行页为准。

## 读过的依据

1. `.abroll-cloud/G-DRIVE-LAYOUT.md`：云端只写相对路径，不写盘符。新视频进 `AI视频项目/<NN_中文项目名>/`，成品名 `00_最终成片_*`，封面 `00_封面_*`。草稿只在 `.abroll-cloud/<NN>/`。可看中转仅成品进已有 `成片/<NN>-<中文名>.mp4`。
2. 共享记忆库《本机公共路径与强制约束》「所有视频统一落盘（2026-09-12）」：新视频项目统一进 `我的云端硬盘/AI视频项目/<NN_中文项目名>/`；渲染临时只进 `AI视频项目/_scratch/`。
3. 同页「G 盘根目录归类（2026-09-14）」：项目素材、工程、中间文件、封面和成片仍进 `AI视频项目/`，不得用 `01_视频素材与成片` 替代项目工作区。
4. Drive 根《【分类与同步规则说明】》（2026-09-14）：`AI视频项目` 是所有新视频项目和临时渲染的固定入口，请勿移动或改名。

## 本集记忆库路径

| 用途 | 路径 |
|------|------|
| 项目根 | `我的云端硬盘/AI视频项目/104_金句要能截图/` |
| 工程成片 | `00_最终成片_金句要能截图.mp4` |
| 封面 | `00_封面_金句要能截图.jpg` |
| 渲染临时 | `我的云端硬盘/AI视频项目/_scratch/104_金句要能截图/` |
| 不进 | `01_视频素材与成片`（非项目工作区） |
| 不覆盖 | 工厂短切 `AI自动剪辑/104_金句要能截图/`（约十六秒，只读） |

## 本云端会话实际落盘

本机网盘未挂载，按记忆库「目标根不可用时不回退」：草稿只写仓库，不写本机系统盘与数据盘盘符，不传 Drive。

| 用途 | 路径 | 时长 |
|------|------|------|
| 草稿根 | `.abroll-cloud/104/` | — |
| 成片中转 | `成片/{STAGED_NAME}` | {kit.zh_sec(duration)} |
| 工程成片 | `.abroll-cloud/104/00_最终成片_{NAME}.mp4` | {kit.zh_sec(duration)} |

工厂短切约十六秒，只读对照，不重做、不覆盖。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    row = f"| 104 | 工厂知识口播 | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if "| 104 |" in text:
        lines = [row if raw.startswith("| 104 |") else raw for raw in text.splitlines()]
        text = "\n".join(lines)
    else:
        if "| 99 |" in text:
            rebuilt = []
            for raw in text.splitlines():
                rebuilt.append(raw)
                if raw.startswith("| 99 |"):
                    rebuilt.append(row)
            text = "\n".join(rebuilt)
        else:
            text = text.rstrip() + "\n" + row + "\n"
    section = f"""## 104. 金句要能截图

- **状态**：已核验 · `.abroll-cloud/104/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}
- **A-roll 角度**：工厂 `104_金句要能截图` 短切。只打「金句要能截图」：截图看不清，只在耳朵里待三秒。字少、对比强、一句站得住。讲解可以长，金句必须短。不讲一句只讲一件事，不讲问句比陈述，不讲收束回钩子。
- **B-roll 想法**：截不清只待三秒；字少 / 对比强 / 一句站得住；浅底糊对深底清；朋友圈看得懂吗；截得清才留得住。
- **来源笔记**：Drive 只读工厂 `104_金句要能截图`（claim：白底小灯 A-roll + 黑底信息图 B-roll；`/workspace/成片/` 无本条）
- **成片名**：`{STAGED_NAME}`
- **避开**：#103 一句只讲一件事；工厂 85 问句比陈述狠；工厂 86 收束要落回钩子；工厂 87 重复不是啰嗦；成片 12 三秒留人；成片 25 行动指令
"""
    if "## 104. 金句要能截图" in text:
        verified = f"- **状态**：已核验 · `.abroll-cloud/104/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}"
        text = text.replace("- **状态**：已认领 · `.abroll-cloud/104/` · NEW · 目标四十到五十秒", verified)
    else:
        text = text.rstrip() + "\n\n" + section
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": NAME,
        "staged_name": STAGED_NAME,
        "episode": 104,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "Drive 工厂 104_金句要能截图 · 云端 NEW",
        "hooks": "钩子：金句要能截图。\n诊断：截图看不清，只在耳朵里待三秒。\n做法：字少、对比强、一句站得住。\n收束：截得清才留得住。截不清，请当成没写过。",
        "cover_lines": ("金句要能", "截图"),
        "avoid": "#103 一句一件事；85 问句；86 收束；87 重复；12 三秒留人；25 行动指令",
        "factory": "Drive 工厂 104_金句要能截图",
        "broll": {
            "S02": ("B-截不清只待三秒.mp4", frame_three_seconds),
            "S04": ("B-字少对比强站得住.mp4", frame_three_rules),
            "S06": ("B-糊底对深底.mp4", frame_blur_vs_clear),
            "S08": ("B-朋友圈看得懂吗.mp4", frame_moments),
            "S10": ("B-截得清才留得住.mp4", frame_stamp),
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
    print("NEW 104", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
