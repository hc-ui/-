#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 67：置顶了也不看。工厂 67_置顶了也不看。云端 NEW A-roll + B-roll。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/67/，成品中转 成片/67-置顶了也不看.mp4。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
目标四十到五十秒。不定格、不慢放注水。时长用中文「秒」。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _long_kit as kit

ROOT = Path(__file__).resolve().parent


def frame_pin(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 位置")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 230 + int(kit.lerp(16, 0, a0))),
        "置顶只是位置",
        font=kit.font(54),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 330 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 420), 32, kit.mix(kit.BG, kit.CARD, a1))
    d.text((285, y + 56), "钉", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 150), "位置", font=kit.font(56), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    d.text((285, y + 240), "钉在顶上", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
    pin = kit.appear(t, 0.55, 0.20)
    if pin > 0.04:
        d.polygon([(285, y + 300), (265, y + 340), (305, y + 340)], fill=kit.mix(kit.CARD, kit.YELLOW, pin))

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (580, y, 1010, y + 420), 32, kit.mix(kit.BG, (42, 24, 22), a2))
    d.text((795, y + 56), "看", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((795, y + 150), "阅读", font=kit.font(56), fill=kit.mix(kit.CARD, kit.RED, a2), anchor="mm")
    d.text((795, y + 240), "没有打开", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
    kit.x_mark(d, 795, y + 330, kit.appear(t, 0.80, 0.22), 28)

    gone = kit.appear(t, 1.05, 0.22)
    if gone > 0.04:
        y2 = 800 + int(kit.lerp(16, 0, gone)) + dy
        kit.rounded(d, (90, y2, 990, y2 + 150), 26, kit.mix(kit.BG, kit.CARD, gone))
        d.text((kit.W // 2, y2 + 48), "红点消了", font=kit.font(40), fill=kit.mix(kit.CARD, kit.YELLOW, gone), anchor="mm")
        d.text((kit.W // 2, y2 + 108), "人已经滑走", font=kit.font(32), fill=kit.mix(kit.CARD, kit.MUTED, gone), anchor="mm")
        kit.strike_box(d, (220, y2 + 16, 860, y2 + 80), kit.appear(t, 1.28, 0.24), kit.mix(kit.CARD, kit.RED, gone))

    punch = kit.appear(t, 1.60, 0.22)
    if punch > 0.04:
        y3 = 1000 + int(kit.lerp(14, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 180), 28, kit.mix(kit.BG, (42, 28, 18), punch))
        d.text((kit.W // 2, y3 + 90), "别把钉过当成看过", font=kit.font(46), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def frame_action(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 动作")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 228 + int(kit.lerp(16, 0, a0))),
        "第一句写动作",
        font=kit.font(54),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    swipe = kit.appear(t, 0.12, 0.28)
    if swipe > 0.04:
        y = 320 + int(kit.lerp(14, 0, swipe))
        kit.rounded(d, (90, y, 990, y + 160), 26, kit.mix(kit.BG, (42, 24, 22), swipe))
        d.text((kit.W // 2, y + 50), "看见「置顶」", font=kit.font(36), fill=kit.mix(kit.CARD, kit.MUTED, swipe), anchor="mm")
        d.text((kit.W // 2, y + 112), "手已经往下划", font=kit.font(44), fill=kit.mix(kit.CARD, kit.RED, swipe), anchor="mm")
        slide = int(kit.lerp(0, 120, kit.appear(t, 0.40, 0.50)))
        d.polygon(
            [(860 + slide, y + 40), (920 + slide, y + 80), (860 + slide, y + 120)],
            fill=kit.mix(kit.CARD, kit.RED, swipe),
        )

    rows = [(0.55, "1", "谁做"), (0.72, "2", "做什么"), (0.89, "3", "做到哪天")]
    for i, (ts, num, head) in enumerate(rows):
        a = kit.appear(t, ts, 0.20)
        if a < 0.04:
            continue
        y = 520 + i * 140 + int(kit.lerp(16, 0, a))
        kit.rounded(d, (90, y, 990, y + 122), 24, kit.mix(kit.BG, kit.CARD, a))
        d.ellipse((128, y + 24, 216, y + 112), fill=kit.mix(kit.CARD, kit.MINT, a))
        d.text((172, y + 68), num, font=kit.font(34), fill=kit.mix(kit.MINT, kit.INK, a), anchor="mm")
        d.text((248, y + 61), head, font=kit.font(42), fill=kit.mix(kit.CARD, kit.WHITE, a), anchor="lm")
        kit.check_badge(d, 900, y + 61, kit.appear(t, ts + 0.22, 0.16))

    punch = kit.appear(t, 1.55, 0.22)
    if punch > 0.04:
        y3 = 980 + int(kit.lerp(14, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 170), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 85), "要他看，先写动作", font=kit.font(46), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_name(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 点名")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 230 + int(kit.lerp(16, 0, a0))),
        "点名比钉子管用",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 330 + int(kit.lerp(18, 0, a1))
    kit.rounded(d, (70, y, 500, y + 420), 32, kit.mix(kit.BG, (42, 24, 22), a1))
    d.text((285, y + 70), "错", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 180), "请看置顶", font=kit.font(44), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    d.text((285, y + 270), "只靠钉子", font=kit.font(30), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
    kit.x_mark(d, 285, y + 340, kit.appear(t, 0.70, 0.20), 28)
    kit.strike_box(d, (110, y + 140, 460, y + 220), kit.appear(t, 0.86, 0.24), kit.mix(kit.CARD, kit.RED, a1))

    a2 = kit.appear(t, 0.28)
    kit.rounded(d, (580, y, 1010, y + 420), 32, kit.mix(kit.BG, (18, 42, 36), a2))
    d.text((795, y + 70), "对", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((795, y + 180), "点一次名", font=kit.font(44), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    d.text((795, y + 270), "人要对上", font=kit.font(30), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
    kit.check_badge(d, 795, y + 340, kit.appear(t, 0.92, 0.20))

    punch = kit.appear(t, 1.45, 0.22)
    if punch > 0.04:
        y3 = 820 + int(kit.lerp(14, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 190), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 95), "先写动作，再决定钉不钉", font=kit.font(40), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def rewrite_new_docs(duration: float, data: dict) -> None:
    """kit 默认写成 n-long 加长重切；本集是云端 NEW，草稿在 67/。"""
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    status_path = ROOT / "项目状态.json"
    status = json.loads(status_path.read_text(encoding="utf-8"))
    status.update({
        "project_name": "67_置顶了也不看",
        "cut": "new-40s",
        "draft": ".abroll-cloud/67",
        "replaced_short_cut_s": 0,
        "factory_short_s": 20.667,
        "duration_zh": kit.zh_sec(duration),
        "source_note": "工厂 67_置顶了也不看 · 云端 NEW，不拷工厂成片",
    })
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    note = f"""# 67 · 置顶了也不看

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。

- **选题**：工厂 `67_置顶了也不看`（Drive 只读；工厂短切约 20.7秒，未进成片）
- **成片中转**：`成片/67-置顶了也不看.mp4`
- **本集工程成片**：`00_最终成片_置顶了也不看.mp4`
- **草稿目录**：`/workspace/.abroll-cloud/67/`
- **云端 only**：不写 `C:\\` / `D:\\` / `G:\\`，不传 Drive
- **时长**：{kit.zh_sec(duration)}，目标四十到五十秒
- **禁止冻帧垫时长**：A 镜循环，B 镜按口播重画，不用末帧克隆
- **避开**：成片 41 新人提问；成片 10 别念链接；成片 11 列表先给结果；#55 能截的那句；成片 34 别念屏上字

钩子：置顶了也不看。
诊断：置顶只是位置，不是阅读。
例子：红点消了人已滑走；第一句写谁做、做什么、哪天；再点一次名。
收束：先写动作，再决定钉不钉。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，{kit.zh_sec(duration)}。镜头 {len(data["shots"])} 条，口播 18 句，时间轴闭合。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")


def main() -> None:
    ep = kit.Episode(ROOT, {
        "name": "置顶了也不看",
        "full_title": "置顶了也不看",
        "staged_name": "67-置顶了也不看.mp4",
        "episode": 67,
        "expected_phrases": 18,
        "replaced_short": 0,
        "source_note": "工厂 67_置顶了也不看 · 云端 NEW",
        "factory": "67_置顶了也不看",
        "hooks": "钩子：置顶了也不看。\n诊断：置顶只是位置，不是阅读。\n例子：红点消了人已滑走；第一句写动作。\n再一例：点名比钉子管用。\n收束：先写动作，再决定钉不钉。",
        "cover_lines": ("置顶了", "也不看"),
        "avoid": "成片 41 新人提问；成片 10 别念链接；成片 11 列表先给结果；#55 能截的那句；成片 34 别念屏上字",
        "broll": {
            "S02": ("B-位置不是阅读.mp4", frame_pin),
            "S04": ("B-第一句写动作.mp4", frame_action),
            "S06": ("B-点名比钉子管用.mp4", frame_name),
        },
    })
    report = ep.produce()
    draft = ROOT / "00_最终成片_置顶了也不看.mp4"
    dur = kit.probe_dur(draft)
    data = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
    rewrite_new_docs(dur, data)
    qa = json.loads((ROOT / "交付核验.json").read_text(encoding="utf-8"))
    qa["project"] = "67_置顶了也不看"
    qa["cut"] = "new-40s"
    qa["draft"] = ".abroll-cloud/67"
    qa["duration_zh"] = kit.zh_sec(qa["video"]["duration_s"])
    (ROOT / "交付核验.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("NEW docs rewritten", kit.zh_sec(dur), "ok", report["ok"])


if __name__ == "__main__":
    main()
