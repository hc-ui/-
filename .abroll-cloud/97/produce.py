#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 97：环境变量写在聊天里。Drive 工厂 97。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/97/，成品中转 成片/97-环境变量写在聊天里.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不重复成片 84 接口变更口头说一声，不重复 96 密钥轮转，不拷工厂短切。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "环境变量写在聊天里"
STAGED_NAME = "97-环境变量写在聊天里.mp4"
BANNED = (
    "密钥",
    "轮转",
    "过期",
    "发布说明",
    "流水账",
    "回退",
    "副本",
    "临时方案",
    "口头说一声",
    "口头同步",
    "下一期",
    "文件名",
    "C++",
    "ROS",
)


def frame_chat_mess(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 靠翻记录")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0)) + dy),
        "上线靠翻聊天",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    cards = [
        (0.16, 80, 320, "谁改过", "对不上"),
        (0.34, 405, 350, "哪套环境", "对不上"),
        (0.52, 730, 320, "以谁为准", "对不上"),
    ]
    for ts, x, y0, head, body in cards:
        a = kit.appear(t, ts, 0.22)
        if a < 0.04:
            continue
        y = y0 + int(kit.lerp(18, 0, a)) + dy
        kit.rounded(d, (x, y, x + 270, y + 280), 26, kit.mix(kit.BG, kit.CARD, a))
        d.text((x + 135, y + 70), head, font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, a), anchor="mm")
        d.text((x + 135, y + 150), body, font=kit.font(36), fill=kit.mix(kit.CARD, kit.YELLOW, a), anchor="mm")
        kit.x_mark(d, x + 135, y + 220, kit.appear(t, ts + 0.40, 0.18), 22)
    punch = kit.appear(t, 1.18, 0.22)
    if punch > 0.04:
        y = 860 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y, 990, y + 200), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 70), "三条记录三个数", font=kit.font(44), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
        d.text((kit.W // 2, y + 140), "全对不上", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, punch), anchor="mm")
    return img


def frame_wrong_env(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 连错 / 旧值")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "消息当配置",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.16)
    if a1 > 0.04:
        y = 300 + int(kit.lerp(14, 0, a1)) + dy
        kit.rounded(d, (70, y, 500, y + 460), 32, kit.mix(kit.BG, (42, 24, 22), a1))
        d.text((285, y + 70), "预发", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
        d.text((285, y + 190), "连了生产库", font=kit.font(44), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
        d.text((285, y + 280), "还以为没动", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.x_mark(d, 285, y + 370, kit.appear(t, 0.70, 0.20), 30)
    a2 = kit.appear(t, 0.30)
    if a2 > 0.04:
        y = 300 + int(kit.lerp(14, 0, a2)) + dy
        kit.rounded(d, (580, y, 1010, y + 460), 32, kit.mix(kit.BG, kit.CARD, a2))
        d.text((795, y + 70), "新人", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
        d.text((795, y + 190), "上周那条", font=kit.font(44), fill=kit.mix(kit.CARD, kit.YELLOW, a2), anchor="mm")
        d.text((795, y + 280), "配出来是旧值", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
        kit.x_mark(d, 795, y + 370, kit.appear(t, 0.88, 0.20), 30)
    punch = kit.appear(t, 1.18, 0.22)
    if punch > 0.04:
        y = 830 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 180), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y + 90), "对话里的数，现场接不住", font=kit.font(40), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_three_places(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 配置要进")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "配置要进三处",
        font=kit.font(50),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    rows = [
        (0.16, "1", "进仓库", "能搜到、能对照"),
        (0.40, "2", "进清单", "哪套环境写清"),
        (0.64, "3", "进发布步骤", "跟谁对齐写清"),
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
        d.text((kit.W // 2, y + 70), "改一条，写三处", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
        d.text((kit.W // 2, y + 140), "环境 · 键名 · 跟谁对齐", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, punch), anchor="mm")
    return img


def frame_repo_vs_chat(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对照 · 仓库 / 群消息")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "以谁为准",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 500), 32, kit.mix(kit.BG, (42, 24, 22), a1))
    d.text((285, y + 56), "群消息", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "翻得到", font=kit.font(52), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    d.text((285, y + 270), "对不上现场", font=kit.font(36), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    kit.x_mark(d, 285, y + 380, kit.appear(t, 0.55, 0.22), 36)
    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (580, y, 1010, y + 500), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((795, y + 56), "仓库", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((795, y + 180), "找得到", font=kit.font(52), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    d.text((795, y + 270), "对得上才算", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    kit.check_badge(d, 795, y + 380, kit.appear(t, 0.70, 0.22))
    stamp = kit.appear(t, 1.20, 0.24)
    if stamp > 0.04:
        y3 = 860 + int(kit.lerp(16, 0, stamp)) + dy
        kit.rounded(d, (140, y3, 940, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), stamp))
        d.text((kit.W // 2, y3 + 70), "上线以仓库为准", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, stamp), anchor="mm")
        d.text((kit.W // 2, y3 + 140), "不以群消息为准", font=kit.font(32), fill=kit.mix(kit.CARD, kit.YELLOW, stamp), anchor="mm")
    return img


def frame_stamp(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "收 · 才叫环境")
    dy = kit.breathe(t, 6)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 230 + int(kit.lerp(16, 0, a0))),
        "找得到，对得上",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )
    a1 = kit.appear(t, 0.18)
    if a1 > 0.04:
        cx, cy = 540, 620 + dy
        r = 230
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=kit.mix(kit.BG, (18, 42, 36), a1))
        d.text((cx, cy - 40), "才叫环境", font=kit.font(56), fill=kit.mix(kit.CARD, kit.MINT, a1), anchor="mm")
        d.text((cx, cy + 50), "写进仓库才算", font=kit.font(36), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
        kit.check_badge(d, cx, cy + 140, kit.appear(t, 0.70, 0.22))
    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y = 960 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (120, y, 960, y + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y + 85), "聊天里的环境，请当成没配", font=kit.font(38), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "97_环境变量写在聊天里"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/97"
        status["source_note"] = "Drive 工厂 97_环境变量写在聊天里 / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status["distinct_from"] = ["96-密钥轮转拖到过期", "84-接口变更口头说一声", "65-口头同步当过结论", "100-临时方案住进主干"]
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "97_环境变量写在聊天里"
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
        data["draft"] = ".abroll-cloud/97"
        data["source_note"] = "Drive 工厂 97_环境变量写在聊天里 / 云端 NEW"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 97 · 环境变量写在聊天里

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：Drive 只读工厂 `97_环境变量写在聊天里`
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/97/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：#96 密钥轮转拖到过期；成片 84 接口变更口头说一声；成片 65 口头同步当过结论；#100 临时方案住进主干

钩子：环境变量写在聊天里。
诊断：上线靠翻记录；谁改过、哪套、以谁为准对不上。
做法：配置进仓库、进清单、进发布步骤。
收束：聊天记录不是配置源。聊天里的环境，请当成没配。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头十二条，口播十八句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")
    (ROOT / "时长.md").write_text(
        f"""# 成片 97 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 工厂短切 | 新时长 | 草稿 |
|----|------|----------|--------|------|
| 97 | `{STAGED_NAME}` | 工厂 97 号短切（未进成片） | {kit.zh_sec(duration)} | `.abroll-cloud/97/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。十二镜 / 十八句。禁止 `tpad=stop_mode=clone`。
不重做 00–95，不抢 96 / 98 / 99 / 100，不拷工厂成片。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    section = f"""## 97. 环境变量写在聊天里

- **状态**：已核验 · `.abroll-cloud/97/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}
- **A-roll 角度**：工厂 `97_环境变量写在聊天里` 短切。只打「环境变量写在聊天里」：上线靠翻记录，谁改过、哪套、以谁为准对不上。配置进仓库、进清单、进发布步骤。不讲密钥轮转，不讲发布说明。
- **B-roll 想法**：翻聊天三条对不上；预发连生产库 / 旧消息旧值；仓库、清单、发布步骤；仓库对群消息；找得到对得上才叫环境。
- **来源笔记**：Drive 只读工厂 `97_环境变量写在聊天里`（claim：白底小灯 A-roll + 黑底信息图 B-roll；`/workspace/成片/` 无本条）
- **成片名**：`{STAGED_NAME}`
- **避开**：#96 密钥轮转拖到过期；成片 84 接口变更口头说一声；成片 65 口头同步当过结论
"""
    text = path.read_text(encoding="utf-8")
    if "## 97. 环境变量写在聊天里" in text:
        return
    text = text.rstrip() + "\n\n" + section
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "环境变量写在聊天里",
        "staged_name": STAGED_NAME,
        "episode": 97,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "Drive 工厂 97_环境变量写在聊天里 · 云端 NEW",
        "hooks": "钩子：环境变量写在聊天里。\n诊断：上线靠翻记录，三问对不上。\n做法：配置进仓库、进清单、进发布步骤。\n收束：聊天里的环境，请当成没配。",
        "cover_lines": ("环境变量", "写在聊天里"),
        "avoid": "#96 密钥轮转；成片 84 接口口头变更；成片 65 口头同步当过结论",
        "factory": "Drive 工厂 97_环境变量写在聊天里",
        "broll": {
            "S02": ("B-翻记录对不上.mp4", frame_chat_mess),
            "S04": ("B-连错库旧值.mp4", frame_wrong_env),
            "S06": ("B-三处入库.mp4", frame_three_places),
            "S08": ("B-仓库对群消息.mp4", frame_repo_vs_chat),
            "S10": ("B-才叫环境.mp4", frame_stamp),
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
    print("NEW 97", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
