#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 82：if-not。topics-batch4 #82。云端 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/82/，成品中转 成片/82-if-not.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
不重复成片 64 空字典出生地。只打空容器先用 if not 拦住。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import _long_kit as kit

NAME = "if-not"
STAGED_NAME = "82-if-not.mp4"
BANNED = (
    "循环外面",
    "出生地",
    "append",
    "第几个",
    "拆成函数",
    "嵌套字典",
    "异常整章",
    "下一期",
    "C++",
    "ROS2",
    "赵老师",
)


def frame_explode(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "错 · 空了硬算")
    dy = kit.breathe(t)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0)) + dy),
        "空班级直接求最高分",
        font=kit.font(48),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.14)
    y = 300 + int(kit.lerp(18, 0, a1)) + dy
    kit.rounded(d, (80, y, 500, y + 360), 30, kit.mix(kit.BG, kit.CARD, a1))
    d.text((290, y + 56), "名册", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((290, y + 150), "{}", font=kit.font(72), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    d.text((290, y + 250), "0 人", font=kit.font(40), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    d.text((290, y + 310), "空容器", font=kit.font(26), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")

    boom = kit.appear(t, 0.42, 0.28)
    kit.rounded(d, (560, y, 1000, y + 360), 30, kit.mix(kit.BG, (42, 24, 22), boom))
    d.text((780, y + 56), "硬算", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, boom), anchor="mm")
    d.text((780, y + 150), "max([])", font=kit.font(52), fill=kit.mix(kit.CARD, kit.YELLOW, boom), anchor="mm")
    d.text((780, y + 230), "总分 ÷ 0", font=kit.font(36), fill=kit.mix(kit.CARD, kit.RED, boom), anchor="mm")
    kit.x_mark(d, 780, y + 300, kit.appear(t, 0.72, 0.2), 30)

    punch = kit.appear(t, 1.10, 0.22)
    if punch > 0.04:
        y3 = 720 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y3, 990, y3 + 200), 28, kit.mix(kit.BG, (42, 24, 22), punch))
        d.text((kit.W // 2, y3 + 70), "不是写错地方", font=kit.font(30), fill=kit.mix(kit.CARD, kit.MUTED, punch), anchor="mm")
        d.text((kit.W // 2, y3 + 136), "空了还硬算会炸", font=kit.font(48), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")

    habit = kit.appear(t, 1.45, 0.22)
    if habit > 0.04:
        y4 = 960 + int(kit.lerp(14, 0, habit)) + dy
        kit.rounded(d, (140, y4, 940, y4 + 160), 26, kit.mix(kit.BG, (32, 30, 20), habit))
        d.text((kit.W // 2, y4 + 80), "现在只会写长度等于零", font=kit.font(36), fill=kit.mix(kit.BG, kit.AMBER, habit), anchor="mm")
    return img


def frame_gate(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · if not")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "先问是不是空的",
        font=kit.font(52),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(16, 0, a1))
    kit.rounded(d, (70, y, 500, y + 420), 32, kit.mix(kit.BG, kit.CARD, a1))
    d.text((285, y + 56), "现用", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 160), "长度 = 0", font=kit.font(44), fill=kit.mix(kit.CARD, kit.AMBER, a1), anchor="mm")
    d.text((285, y + 250), "能用", font=kit.font(32), fill=kit.mix(kit.CARD, kit.WHITE, a1), anchor="mm")
    d.text((285, y + 330), "还不是正式句", font=kit.font(26), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")

    a2 = kit.appear(t, 0.32)
    kit.rounded(d, (540, y, 1010, y + 420), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((775, y + 56), "正式闸", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    d.text((775, y + 160), "if not d", font=kit.font(48), fill=kit.mix(kit.CARD, kit.MINT, a2), anchor="mm")
    d.text((775, y + 250), "空了就停", font=kit.font(36), fill=kit.mix(kit.CARD, kit.WHITE, a2), anchor="mm")
    kit.check_badge(d, 775, y + 340, kit.appear(t, 0.70, 0.2))

    chips = [
        (0.70, 90, "{}", "空字典"),
        (0.82, 390, "[]", "空列表"),
        (0.94, 690, '""', "空字符串"),
    ]
    for ts, x, code, label in chips:
        a = kit.appear(t, ts, 0.18)
        if a < 0.04:
            continue
        yy = 760 + dy
        kit.rounded(d, (x, yy, x + 280, yy + 160), 22, kit.mix(kit.BG, kit.CARD, a))
        d.text((x + 140, yy + 58), code, font=kit.font(40), fill=kit.mix(kit.CARD, kit.YELLOW, a), anchor="mm")
        d.text((x + 140, yy + 118), label, font=kit.font(24), fill=kit.mix(kit.CARD, kit.MUTED, a), anchor="mm")

    punch = kit.appear(t, 1.25, 0.22)
    if punch > 0.04:
        y3 = 980 + int(kit.lerp(14, 0, punch)) + dy
        kit.rounded(d, (120, y3, 960, y3 + 160), 26, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 80), "碰到 not 都算空", font=kit.font(44), fill=kit.mix(kit.BG, kit.MINT, punch), anchor="mm")
    return img


def frame_then_stat(t: float):
    img = kit.new_bg()
    d = kit.ImageDraw.Draw(img)
    kit.tag(d, t, "对 · 有人再算")
    dy = kit.breathe(t, 4)
    a0 = kit.appear(t, 0.02)
    d.text(
        (kit.W // 2, 210 + int(kit.lerp(16, 0, a0))),
        "空了先拦住",
        font=kit.font(54),
        fill=kit.mix(kit.BG, kit.WHITE, a0),
        anchor="mm",
    )

    a1 = kit.appear(t, 0.16)
    y = 300 + int(kit.lerp(16, 0, a1))
    kit.rounded(d, (70, y, 500, y + 400), 32, kit.mix(kit.BG, (42, 24, 22), a1))
    d.text((285, y + 56), "空班级", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")
    d.text((285, y + 160), "if not", font=kit.font(48), fill=kit.mix(kit.CARD, kit.YELLOW, a1), anchor="mm")
    d.text((285, y + 250), "停", font=kit.font(64), fill=kit.mix(kit.CARD, kit.RED, a1), anchor="mm")
    d.text((285, y + 330), "别往下算", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a1), anchor="mm")

    a2 = kit.appear(t, 0.34)
    kit.rounded(d, (540, y, 1010, y + 400), 32, kit.mix(kit.BG, (22, 40, 36), a2))
    d.text((775, y + 48), "有人了", font=kit.font(28), fill=kit.mix(kit.CARD, kit.MUTED, a2), anchor="mm")
    for i, (label, ts) in enumerate((("最高", 0.50), ("最低", 0.62), ("平均", 0.74))):
        aa = kit.appear(t, ts, 0.16)
        yy = y + 120 + i * 80
        kit.rounded(d, (590, yy, 960, yy + 64), 16, kit.mix(kit.CARD, (18, 36, 32), aa))
        d.text((775, yy + 32), label, font=kit.font(32), fill=kit.mix(kit.CARD, kit.MINT, aa), anchor="mm")
        kit.check_badge(d, 930, yy + 32, kit.appear(t, ts + 0.12, 0.14) * 0.7)

    punch = kit.appear(t, 1.15, 0.22)
    if punch > 0.04:
        y3 = 760 + int(kit.lerp(16, 0, punch)) + dy
        kit.rounded(d, (90, y3, 990, y3 + 200), 28, kit.mix(kit.BG, (18, 42, 36), punch))
        d.text((kit.W // 2, y3 + 70), "写统计之前先问空不空", font=kit.font(36), fill=kit.mix(kit.CARD, kit.WHITE, punch), anchor="mm")
        d.text((kit.W // 2, y3 + 140), "没拦，请当成会炸", font=kit.font(44), fill=kit.mix(kit.BG, kit.YELLOW, punch), anchor="mm")
    return img


def rewrite_docs(duration: float) -> None:
    status_path = ROOT / "项目状态.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        status["project_name"] = "82_if-not"
        status["cut"] = "new-40s"
        status["draft"] = ".abroll-cloud/82"
        status["source_note"] = "topics-batch4.md #82 / 学习基线 2026-09-09 不足第6条 / 云端 NEW"
        status["replaced_short_cut_s"] = 0
        status["distinct_from"] = "成片/64-空字典写在循环外面.mp4"
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa_path = ROOT / "交付核验.json"
    if qa_path.exists():
        report = json.loads(qa_path.read_text(encoding="utf-8"))
        report["project"] = "82_if-not"
        report["cut"] = "new-40s"
        report["replaced_short_cut_s"] = 0
        report["distinct_from_64"] = True
        qa_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tl_path = ROOT / "timeline.json"
    if tl_path.exists():
        data = json.loads(tl_path.read_text(encoding="utf-8"))
        data["cut"] = "new-40s"
        data["draft"] = ".abroll-cloud/82"
        data["duration_zh"] = kit.zh_sec(float(data.get("duration") or duration))
        data["source_note"] = "topics-batch4.md #82 / 学习基线不足第6条 / 云端 NEW"
        tl_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()
    note = f"""# 82 · if-not

普通短视频 / 知识口播。不是剧情短剧，不走 drama-pipeline。NEW，不是重做。

- **选题**：`topics-batch4.md` 第 82 条；学习基线 2026-09-09 不足第 6 条
- **成片中转**：`成片/{STAGED_NAME}`
- **本集工程成片**：`00_最终成片_{NAME}.mp4`
- **草稿根**：`/workspace/.abroll-cloud/82/`
- **云端 only**：不写 `C:\\\\` / `D:\\\\` / `G:\\\\`，不传 Drive
- **避开**：成片 64 空字典出生地；成片 42 append；成片 13 靠名字；成片 73 先包一层；#74 菜单拆函数；异常整章；C++ / ROS2

钩子：空容器别直接算，先用 if not 拦住。
诊断：空班级求最高分会炸；空列表喂最大值或除以零都会崩。
做法：if not 当正式闸；空了就停，有人再统计。
收束：没拦住的空容器，请当成会炸。

白底小灯 A-roll + 黑底对照卡 B-roll。中文在代码绘制 / 组装叠加，生图不烧字。

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {kit.zh_sec(duration)}。镜头九条，口播十六句，时间轴闭合。不定格、不慢放注水。
"""
    (ROOT / "项目说明.md").write_text(note, encoding="utf-8")
    (ROOT / "时长.md").write_text(
        f"""# 成片 82 时长（中文秒）

云端 only。NEW。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 工厂短切 | 新时长 | 草稿 |
|----|------|----------|--------|------|
| 82 | `{STAGED_NAME}` | 无（首拍） | {kit.zh_sec(duration)} | `.abroll-cloud/82/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。九镜 / 十六句。禁止 `tpad=stop_mode=clone`。
""",
        encoding="utf-8",
    )


def patch_topics(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    heading = "## 82. if not 拦住空容器"
    body = f"""## 82. if not 拦住空容器

- **状态**：已核验 · `.abroll-cloud/82/` · `成片/{STAGED_NAME}` · {kit.zh_sec(duration)}
- **A-roll 角度**：未完成 Python。不足第 6 条：`if not d` 尚未作为正式语法；当前应用长度等于零。空班级直接求最高分或除以 0 会崩。不重拍成片 64 空字典出生地。只打空了还硬算，先用 if not 拦住。
- **B-roll 想法**：空名册喂进最大值和除以零炸掉；长度等于零对照 if not 闸门；空了停、有人再统计。
- **来源笔记**：Drive `学习与职业规划基线.md`（2026-09-09 不足第 6 条）
- **成片名**：`{STAGED_NAME}`
- **避开**：成片 64 空字典出生地；成片 42 append；成片 13 靠名字；成片 73 先包一层；#74 菜单拆函数；#75 嵌套字典
"""
    if heading in text:
        start = text.index(heading)
        nxt = text.find("\n## ", start + 4)
        if nxt == -1:
            nxt = text.find("\n---", start + 4)
        if nxt == -1:
            text = text[:start] + body
        else:
            text = text[:start] + body + text[nxt:]
    else:
        marker = "---\n\n## 对照备忘"
        if marker in text:
            text = text.replace(marker, body + "\n---\n\n## 对照备忘")
        else:
            if not text.endswith("\n"):
                text += "\n"
            text += "\n" + body

    row = f"| 82 | 未完成 Python | `{STAGED_NAME}` | 已核验 {kit.zh_sec(duration)} |"
    if "| 82 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 82 |"):
                lines.append(row)
            else:
                lines.append(raw)
        text = "\n".join(lines)
    elif "| 70 |" in text:
        lines = []
        inserted = False
        for raw in text.splitlines():
            lines.append(raw)
            if raw.startswith("| 70 |") and not inserted:
                lines.append(row)
                inserted = True
        text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def patch_delivery_new(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    new = (
        f"| `成片/{STAGED_NAME}` | 1080×1920 h264+aac 44.1k stereo | {kit.zh_sec(duration)} | "
        f"topic 82 `topics-batch4.md` 第 82 条；学习基线 2026-09-09 不足第 6 条。云端 NEW，不拷短切。 |"
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

    plus_row = f"| 82 | `{STAGED_NAME}` | {kit.zh_sec(duration)} | 已核验 |"
    if "| 82 |" in text:
        lines = []
        for raw in text.splitlines():
            if raw.startswith("| 82 |"):
                lines.append(plus_row)
            else:
                lines.append(raw)
        text = "\n".join(lines)
    else:
        lines = text.splitlines()
        rebuilt = []
        inserted = False
        for raw in lines:
            rebuilt.append(raw)
            if (not inserted) and raw.startswith("| 81 |"):
                rebuilt.append(plus_row)
                inserted = True
        if not inserted:
            rebuilt.append(plus_row)
        text = "\n".join(rebuilt)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def episode() -> kit.Episode:
    return kit.Episode(ROOT, {
        "name": NAME,
        "full_title": "空容器先用 if not 拦住",
        "staged_name": STAGED_NAME,
        "episode": 82,
        "expected_phrases": 16,
        "replaced_short": 0,
        "source_note": "topics-batch4.md #82 · 学习基线 2026-09-09 不足第6条 · 云端 NEW",
        "hooks": "钩子：空容器别直接算，先用 if not 拦住。\n诊断：空班级求最高分会炸；空列表喂最大值或除以零都会崩。\n做法：if not 当正式闸；空了就停。\n收束：没拦住的空容器，请当成会炸。",
        "cover_lines": ("空了先拦住", "if not"),
        "avoid": "成片 64 空字典；成片 42 append；成片 13 靠名字；成片 73 先包一层；#74 菜单拆函数；异常整章；C++ / ROS2",
        "factory": "topics-batch4 #82",
        "broll": {
            "S02": ("B-空了硬算.mp4", frame_explode),
            "S04": ("B-先问空不空.mp4", frame_gate),
            "S06": ("B-拦过再算.mp4", frame_then_stat),
        },
    })


def guard_script() -> None:
    vo = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8")
    hit = [w for w in BANNED if w in vo]
    if hit:
        raise SystemExit(f"banned words in VO: {hit}")


def main() -> None:
    guard_script()
    ep = episode()
    report = ep.produce()
    staged = Path("/workspace/成片") / STAGED_NAME
    dur = kit.probe_dur(staged) if staged.exists() else float(report.get("chengpian_duration_s") or report["video"]["duration_s"])
    rewrite_docs(dur)
    patch_topics(dur)
    patch_delivery_new(dur)
    if qa_path := (ROOT / "交付核验.json"):
        data = json.loads(qa_path.read_text(encoding="utf-8"))
        data["script_guard"] = {w: (w not in (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8")) for w in BANNED}
        data["project"] = "82_if-not"
        data["cut"] = "new-40s"
        qa_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if not data.get("ok"):
            raise SystemExit(json.dumps(data, ensure_ascii=False, indent=2))
    print("NEW 82", staged, kit.zh_sec(dur), "ok", report.get("ok"))


if __name__ == "__main__":
    main()
