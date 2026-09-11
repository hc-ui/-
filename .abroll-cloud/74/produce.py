#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 74：菜单拆成函数。topics-batch4 #74。云端 NEW，不重拍。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/74/，成品中转 成片/74-菜单拆成函数.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
只打「一段逻辑起名字」，不讲存盘、不讲异常整章、不跳语言。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import longform_common as C  # noqa: E402

NAME = "菜单拆成函数"
STAGED_NAME = "74-菜单拆成函数.mp4"
ASSET_06 = Path("/workspace/.abroll-cloud/06/assets")
ASSET_25 = Path("/workspace/.abroll-cloud/25/assets")
PHRASES = [
    "大家好",
    "菜单还是一整段，选项全焊在一块",
    "不是菜单坏了，是函数还没开始",
    "增、列、退各是一块逻辑，却挤在同一段选择里头",
    "改退出得翻整段，改新增还得翻整段",
    "一段逻辑不起名字，就只能整坨搬",
    "把各选项拆成函数，一块事一个名字",
    "菜单只负责点名，干活的是带名字的函数",
    "增有增的名字，列有列的名字，退有退的名字",
    "起名字盖在函数框上，这块就能单独改",
    "先消化起名字，文件读写往后排",
    "异常整章也往后，现在只拆这一层",
    "对照只打这一点：菜单拆成带名字的函数",
    "先给逻辑起名字，再往下一章走",
    "名字立住了，菜单才不是一坨焊死的字",
]


def cut_shot_loop(src: Path, dur: float, dest: Path, kind: str, close: bool = False) -> None:
    """Loop short A-roll. Never freeze last frame. Never slow-mo stretch to pad."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    src_dur = max(0.01, C.probe_dur(src))
    if kind == "A" and close:
        vf = f"scale=1380:2454,crop={C.W}:{C.H}:150:60,fps={C.FPS},setsar=1,format=yuv420p"
    elif kind == "A":
        vf = f"scale=1188:2112,crop={C.W}:{C.H}:54:105,fps={C.FPS},setsar=1,format=yuv420p"
    else:
        vf = (
            f"scale={C.W}:{C.H}:force_original_aspect_ratio=decrease,"
            f"pad={C.W}:{C.H}:(ow-iw)/2:(oh-ih)/2,fps={C.FPS},setsar=1,format=yuv420p"
        )
    cmd = ["ffmpeg", "-y"]
    if dur > src_dur + 0.02:
        cmd += ["-stream_loop", "-1"]
    cmd += [
        "-i", str(src), "-t", f"{dur:.3f}",
        "-vf", vf, "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(dest),
    ]
    C.run(cmd)
    got = C.probe_dur(dest)
    if got + 0.12 < dur:
        raise RuntimeError(f"cut short {dest.name}: {got:.3f} < {dur:.3f} (freeze-pad forbidden)")


def render_b_weld(duration: float):
    n = max(1, round(duration * C.FPS))
    rows = [("选择 增", 0.22), ("选择 列", 0.38), ("选择 退", 0.54)]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "错 · 焊成一坨")
        a0 = C.appear(t, 0.02)
        d.text(
            (C.W // 2, 230 + int(C.lerp(16, 0, a0))),
            "菜单还是一整段",
            font=C.font(48),
            fill=C.mix(C.BG, C.WHITE, a0),
            anchor="mm",
        )
        d.text(
            (C.W // 2, 300 + int(C.lerp(16, 0, a0))),
            "选项全焊在一块",
            font=C.font(44),
            fill=C.mix(C.BG, C.YELLOW, a0),
            anchor="mm",
        )
        block = C.appear(t, 0.16)
        if block > 0.04:
            y = 360 + int(C.lerp(18, 0, block))
            C.rounded(d, (110, y, 970, y + 620), 32, C.mix(C.BG, C.CARD, block))
            d.text(
                (C.W // 2, y + 70),
                "同一段选择",
                font=C.font(32),
                fill=C.mix(C.CARD, C.MUTED, block),
                anchor="mm",
            )
            for idx, (label, ts) in enumerate(rows):
                aa = C.appear(t, ts, 0.18)
                if aa < 0.04:
                    continue
                yy = y + 150 + idx * 140
                C.rounded(d, (180, yy, 900, yy + 110), 20, C.mix(C.CARD, (36, 28, 28), aa))
                d.text((C.W // 2, yy + 55), label, font=C.font(44), fill=C.mix(C.CARD, C.WHITE, aa), anchor="mm")
        cut = C.appear(t, max(1.35, duration * 0.48), 0.28)
        if cut > 0.04:
            C.strike_line(d, (160, 520, 920, 860), cut, C.mix(C.CARD, C.RED, cut))
        punch = C.appear(t, max(1.70, duration * 0.62), 0.22)
        if punch > 0.04:
            y = 1080 + int(C.lerp(16, 0, punch))
            C.rounded(d, (120, y, 960, y + 200), 28, C.mix(C.BG, (42, 24, 22), punch))
            d.text((C.W // 2, y + 100), "改一处就得翻整坨", font=C.font(42), fill=C.mix(C.BG, C.YELLOW, punch), anchor="mm")
        yield img


def render_b_cut(duration: float):
    n = max(1, round(duration * C.FPS))
    boxes = [("增", "增学生"), ("列", "列成绩"), ("退", "退出")]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "拆 · 带名字的方块")
        a0 = C.appear(t, 0.02)
        d.text(
            (C.W // 2, 236 + int(C.lerp(16, 0, a0))),
            "剪开这一整段",
            font=C.font(50),
            fill=C.mix(C.BG, C.WHITE, a0),
            anchor="mm",
        )
        d.text(
            (C.W // 2, 308 + int(C.lerp(16, 0, a0))),
            "一块事一个名字",
            font=C.font(40),
            fill=C.mix(C.BG, C.MINT, a0),
            anchor="mm",
        )
        split = C.appear(t, 0.28, 0.40)
        for idx, (short, full) in enumerate(boxes):
            aa = C.appear(t, 0.34 + idx * 0.16, 0.20)
            if aa < 0.04:
                continue
            x = 70 + idx * 340
            y = 400 + int(C.lerp(28, 0, aa)) + int((1 - split) * 40)
            C.rounded(d, (x, y, x + 300, y + 420), 28, C.mix(C.BG, C.CARD, aa))
            d.text((x + 150, y + 90), short, font=C.font(72), fill=C.mix(C.CARD, C.YELLOW, aa), anchor="mm")
            d.text((x + 150, y + 200), full, font=C.font(36), fill=C.mix(C.CARD, C.WHITE, aa), anchor="mm")
            d.text((x + 150, y + 300), "函数", font=C.font(32), fill=C.mix(C.CARD, C.MINT, aa), anchor="mm")
            C.check_badge(d, x + 150, y + 360, C.appear(t, 1.10 + idx * 0.12, 0.18))
        punch = C.appear(t, max(1.50, duration * 0.58), 0.22)
        if punch > 0.04:
            y = 1080 + int(C.lerp(16, 0, punch))
            C.rounded(d, (120, y, 960, y + 200), 28, C.mix(C.BG, (18, 42, 36), punch))
            d.text((C.W // 2, y + 100), "各选项拆成函数", font=C.font(44), fill=C.mix(C.BG, C.MINT, punch), anchor="mm")
        yield img


def render_b_name(duration: float):
    n = max(1, round(duration * C.FPS))
    boxes = [("增", 0.22), ("列", 0.40), ("退", 0.58)]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "对 · 起名字")
        a0 = C.appear(t, 0.02)
        d.text(
            (C.W // 2, 236 + int(C.lerp(16, 0, a0))),
            "起名字盖上去",
            font=C.font(52),
            fill=C.mix(C.BG, C.WHITE, a0),
            anchor="mm",
        )
        for idx, (label, ts) in enumerate(boxes):
            aa = C.appear(t, ts, 0.18)
            if aa < 0.04:
                continue
            y = 340 + idx * 200 + int(C.lerp(16, 0, aa))
            C.rounded(d, (120, y, 960, y + 170), 26, C.mix(C.BG, C.CARD, aa))
            d.text((260, y + 85), label, font=C.font(56), fill=C.mix(C.CARD, C.WHITE, aa), anchor="mm")
            stamp = C.appear(t, ts + 0.28, 0.20)
            if stamp > 0.04:
                C.rounded(d, (520, y + 30, 900, y + 140), 20, C.mix(C.CARD, (18, 48, 40), stamp))
                d.text((710, y + 85), "起名字", font=C.font(40), fill=C.mix(C.CARD, C.MINT, stamp), anchor="mm")
        punch = C.appear(t, max(1.45, duration * 0.58), 0.22)
        if punch > 0.04:
            y = 1060 + int(C.lerp(16, 0, punch))
            C.rounded(d, (140, y, 940, y + 180), 28, C.mix(C.BG, (18, 42, 36), punch))
            d.text((C.W // 2, y + 90), "这块就能单独改", font=C.font(44), fill=C.mix(C.BG, C.MINT, punch), anchor="mm")
        yield img


def render_b_road(duration: float):
    n = max(1, round(duration * C.FPS))
    steps = [
        ("函数", True, 0.20),
        ("文件", False, 0.40),
        ("异常", False, 0.60),
    ]
    later = [("class", 0.78), ("模块", 0.90)]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "顺序 · 先函数")
        a0 = C.appear(t, 0.02)
        d.text(
            (C.W // 2, 236 + int(C.lerp(16, 0, a0))),
            "现在只拆这一层",
            font=C.font(50),
            fill=C.mix(C.BG, C.WHITE, a0),
            anchor="mm",
        )
        for idx, (label, live, ts) in enumerate(steps):
            aa = C.appear(t, ts, 0.18)
            if aa < 0.04:
                continue
            x = 90 + idx * 310
            y = 380 + int(C.lerp(16, 0, aa))
            fill = (18, 42, 36) if live else (28, 30, 36)
            ink = C.MINT if live else C.MUTED
            C.rounded(d, (x, y, x + 280, y + 280), 26, C.mix(C.BG, fill, aa))
            d.text((x + 140, y + 110), label, font=C.font(52), fill=C.mix(C.CARD, ink, aa), anchor="mm")
            d.text(
                (x + 140, y + 190),
                "先做" if live else "往后排",
                font=C.font(30),
                fill=C.mix(C.CARD, C.YELLOW if live else C.MUTED, aa),
                anchor="mm",
            )
            if live:
                C.check_badge(d, x + 140, y + 240, C.appear(t, ts + 0.28, 0.18))
            else:
                C.draw_x(d, x + 140, y + 240, C.appear(t, ts + 0.28, 0.18), 22)
        for idx, (label, ts) in enumerate(later):
            aa = C.appear(t, ts, 0.16)
            if aa < 0.04:
                continue
            x = 200 + idx * 360
            y = 740 + int(C.lerp(12, 0, aa))
            C.rounded(d, (x, y, x + 300, y + 120), 20, C.mix(C.BG, (22, 24, 28), aa))
            d.text((x + 150, y + 60), f"{label} 更后", font=C.font(32), fill=C.mix(C.CARD, C.MUTED, aa), anchor="mm")
        punch = C.appear(t, max(1.55, duration * 0.60), 0.22)
        if punch > 0.04:
            y = 1060 + int(C.lerp(16, 0, punch))
            C.rounded(d, (120, y, 960, y + 200), 28, C.mix(C.BG, (18, 42, 36), punch))
            d.text((C.W // 2, y + 100), "先消化起名字", font=C.font(46), fill=C.mix(C.BG, C.MINT, punch), anchor="mm")
        yield img


def render_b_motto(duration: float):
    n = max(1, round(duration * C.FPS))
    third = duration / 3.0
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "对照 · 焊死 / 起名")
        if t < third:
            a = C.appear(t, 0.02)
            d.text((C.W // 2, 230 + int(C.lerp(16, 0, a))), "现在只拆这一层", font=C.font(48), fill=C.mix(C.BG, C.WHITE, a), anchor="mm")
            steps = [("函数", True), ("文件", False), ("异常", False)]
            for idx, (label, live) in enumerate(steps):
                x = 90 + idx * 310
                y = 360
                fill = (18, 42, 36) if live else (28, 30, 36)
                ink = C.MINT if live else C.MUTED
                C.rounded(d, (x, y, x + 280, y + 360), 26, C.mix(C.BG, fill, a))
                d.text((x + 140, y + 130), label, font=C.font(52), fill=C.mix(C.CARD, ink, a), anchor="mm")
                d.text(
                    (x + 140, y + 230),
                    "先做" if live else "往后排",
                    font=C.font(30),
                    fill=C.mix(C.CARD, C.YELLOW if live else C.MUTED, a),
                    anchor="mm",
                )
                if live:
                    C.check_badge(d, x + 140, y + 300, C.appear(t, 0.55, 0.18))
                else:
                    C.draw_x(d, x + 140, y + 300, C.appear(t, 0.70, 0.18), 22)
            d.text((C.W // 2, 820), "文件和异常先灰掉", font=C.font(36), fill=C.mix(C.BG, C.MUTED, a), anchor="mm")
        elif t < third * 2:
            a = C.appear(t, third, 0.22)
            d.text((C.W // 2, 230), "一张对照", font=C.font(40), fill=C.mix(C.BG, C.MUTED, a), anchor="mm")
            d.text((C.W // 2, 300), "只打起名字", font=C.font(48), fill=C.mix(C.BG, C.WHITE, a), anchor="mm")
            C.rounded(d, (70, 380, 510, 1100), 32, C.mix(C.BG, (42, 24, 22), a))
            C.rounded(d, (570, 380, 1010, 1100), 32, C.mix(C.BG, (18, 42, 36), a))
            d.text((290, 500), "焊死", font=C.font(32), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            d.text((290, 680), "整坨搬", font=C.font(52), fill=C.mix(C.CARD, C.RED, a), anchor="mm")
            C.draw_x(d, 290, 860, C.appear(t, third + 0.40, 0.20), 32)
            d.text((790, 500), "起名", font=C.font(32), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            d.text((790, 680), "单独改", font=C.font(52), fill=C.mix(C.CARD, C.MINT, a), anchor="mm")
            C.check_badge(d, 790, 860, C.appear(t, third + 0.55, 0.20))
        else:
            a = C.appear(t, third * 2, 0.22)
            d.text((C.W // 2, 240), "菜单拆成函数", font=C.font(50), fill=C.mix(C.BG, C.WHITE, a), anchor="mm")
            d.text((C.W // 2, 320), "一段逻辑起名字", font=C.font(44), fill=C.mix(C.BG, C.YELLOW, a), anchor="mm")
            C.rounded(d, (120, 420, 960, 980), 36, C.mix(C.BG, C.CARD, a))
            d.text((C.W // 2, 560), "菜单只负责点名", font=C.font(44), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            d.text((C.W // 2, 680), "干活的是函数", font=C.font(52), fill=C.mix(C.CARD, C.MINT, a), anchor="mm")
            d.text((C.W // 2, 800), "一块事一个名字", font=C.font(44), fill=C.mix(C.CARD, C.YELLOW, a), anchor="mm")
            punch = C.appear(t, third * 2 + 0.70, 0.22)
            if punch > 0.04:
                y = 1080 + int(C.lerp(16, 0, punch))
                C.rounded(d, (140, y, 940, y + 180), 28, C.mix(C.BG, (18, 42, 36), punch))
                d.text((C.W // 2, y + 90), "名字立住再往下", font=C.font(44), fill=C.mix(C.BG, C.MINT, punch), anchor="mm")
        yield img


def build_timeline(cues, duration: float) -> dict:
    if len(cues) != 15:
        raise SystemExit(f"need 15 phrases, got {len(cues)}")
    p = cues
    b1 = max(p[1][1] + 0.06, p[2][0] - C.LEAD)
    b1e = p[4][1]
    a3 = p[4][1]
    b2 = max(p[5][1] + 0.06, p[6][0] - C.LEAD)
    b2e = p[6][1]
    b3 = p[7][0]
    b3e = p[7][1]
    b4 = p[8][0]
    b4e = p[9][1]
    a7 = p[9][1]
    b8 = max(p[10][1] + 0.06, p[11][0] - C.LEAD)
    b8e = p[13][1]
    shots = [
        {"id": "S01a", "kind": "A", "start": 0.0, "end": p[0][1], "src": "assets/V-挥手.mp4", "line": p[0][2], "close": True},
        {"id": "S01b", "kind": "A", "start": p[0][1], "end": b1, "src": "assets/V-正对讲.mp4", "line": p[1][2]},
        {"id": "S02", "kind": "B", "start": b1, "end": b1e, "src": "broll/B-焊成一坨.mp4", "line": p[4][2], "broll": "weld"},
        {"id": "S03", "kind": "A", "start": a3, "end": b2, "src": "assets/V-指向.mp4", "line": p[5][2]},
        {"id": "S04", "kind": "B", "start": b2, "end": b2e, "src": "broll/B-剪成方块.mp4", "line": p[6][2], "broll": "cut"},
        {"id": "S05", "kind": "B", "start": b3, "end": b3e, "src": "broll/B-起名字.mp4", "line": p[7][2], "broll": "name"},
        {"id": "S06", "kind": "B", "start": b4, "end": b4e, "src": "broll/B-起名字.mp4", "line": p[8][2], "broll": "name"},
        {"id": "S07", "kind": "A", "start": a7, "end": b8, "src": "assets/V-摊手.mp4", "line": p[10][2]},
        {"id": "S08", "kind": "B", "start": b8, "end": b8e, "src": "broll/B-对照.mp4", "line": p[12][2], "broll": "motto"},
        {"id": "S09", "kind": "A", "start": b8e, "end": duration, "src": "assets/V-点赞.mp4", "line": p[14][2]},
    ]
    shots = C.close_shots(shots, duration)
    a_caps = [
        {"start": 0.0, "end": shots[0]["end"], "lines": ["大家好"]},
        {"start": shots[1]["start"], "end": shots[1]["end"], "lines": ["菜单还是一整段", "选项全焊在一块"]},
        {"start": shots[3]["start"], "end": shots[3]["end"], "lines": C.split_caption(p[5][2])},
        {"start": shots[7]["start"], "end": shots[7]["end"], "lines": C.split_caption(p[10][2])},
        {"start": shots[9]["start"], "end": duration, "lines": ["名字立住了", "菜单才不是焊死的字"]},
    ]
    shutters = [
        {"start": shots[1]["start"], "color": list(C.CREAM)},
        {"start": shots[2]["start"], "color": list(C.RED)},
        {"start": shots[3]["start"], "color": list(C.CREAM)},
        {"start": shots[4]["start"], "color": list(C.MINT)},
        {"start": shots[5]["start"], "color": list(C.YELLOW)},
        {"start": shots[6]["start"], "color": list(C.MINT)},
        {"start": shots[7]["start"], "color": list(C.CREAM)},
        {"start": shots[8]["start"], "color": list(C.YELLOW)},
        {"start": shots[9]["start"], "color": list(C.MINT)},
    ]
    eyebrows = [
        {"start": shots[0]["start"], "end": shots[0]["end"], "text": "A-ROLL / 1a"},
        {"start": shots[1]["start"], "end": shots[1]["end"], "text": "A-ROLL / 1b"},
        {"start": shots[3]["start"], "end": shots[3]["end"], "text": "A-ROLL / 03"},
        {"start": shots[7]["start"], "end": shots[7]["end"], "text": "A-ROLL / 07"},
        {"start": shots[9]["start"], "end": shots[9]["end"], "text": "A-ROLL / 09"},
    ]
    recipe = {
        "title": NAME,
        "cover_title": "菜单拆成函数",
        "cover_sub": "一段逻辑起名字",
        "cover_line": "一块事一个名字",
        "cover_src": "assets/A-角色-小灯-指向.jpg",
    }
    (ROOT / "plan").mkdir(exist_ok=True)
    (ROOT / "plan" / "shot_recipe.json").write_text(json.dumps(recipe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "plan" / "broll.json").write_text(
        json.dumps(
            {
                "episode": 74,
                "cards": ["焊成一坨", "剪成方块", "起名字", "路线条", "对照"],
                "rule": "只打菜单拆成函数；后面的章灰掉；不烧路径；不念文件名",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    data = {
        "audio": "audio/vo-full.wav",
        "duration": round(duration, 3),
        "fps": C.FPS,
        "size": [C.W, C.H],
        "title": NAME,
        "bgm": "audio/bgm.wav",
        "shots": shots,
        "a_caps": a_caps,
        "shutters": shutters,
        "eyebrows": eyebrows,
        "cover": recipe,
        "cue_map": {ph: [round(s, 3), round(e, 3)] for s, e, ph in cues},
        "b_lead_s": C.LEAD,
        "video_type": "普通短视频",
        "factory": "topics-batch4 #74 菜单拆成函数",
        "topic": 74,
        "source_note": "topics-batch4.md #74 / 学习基线 2026-09-09 下一章：函数",
    }
    (ROOT / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


def make_cover() -> Path:
    data = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
    src = ROOT / data["cover"]["cover_src"]
    if not src.exists():
        src = ROOT / "assets" / "A-角色-小灯-摊手.jpg"
    char = Image.open(src).convert("RGB")
    scale = max(C.W / char.width, C.H / char.height)
    nw, nh = int(char.width * scale), int(char.height * scale)
    char = char.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - C.W) // 2
    y = int((nh - C.H) * 0.55)
    canvas = char.crop((x, y, x + C.W, y + C.H))
    overlay = Image.new("RGBA", (C.W, C.H), (11, 13, 18, 48))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((70, 80, 1010, 470), radius=36, fill=(22, 24, 28))
    d.text((C.W // 2, 160), "菜单拆成函数", font=C.font(52), fill=C.WHITE, anchor="mm")
    d.text((C.W // 2, 250), "一段逻辑起名字", font=C.font(56), fill=C.YELLOW, anchor="mm")
    d.text((C.W // 2, 340), "一块事一个名字", font=C.font(36), fill=C.MINT, anchor="mm")
    d.text((C.W // 2, 410), "菜单点名 · 函数干活", font=C.font(28), fill=C.MUTED, anchor="mm")
    dest = ROOT / f"00_封面_{NAME}.jpg"
    canvas.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    canvas.save(ROOT / "final" / "cover.jpg", quality=92)
    return dest


def patch_batch4(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    token = "| 74 | 未完成 Python |"
    new = f"| 74 | 未完成 Python | `{STAGED_NAME}` | 已核验 {duration:.1f}秒（{C.zh_seconds(duration)}） |"
    lines = []
    hit = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith(token):
            lines.append(new)
            hit = True
        else:
            lines.append(raw)
    if hit:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def patch_delivery(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/DELIVERY.md")
    if not path.exists():
        return
    token = f"| 74 | `{STAGED_NAME}`"
    line = f"| 74 | `{STAGED_NAME}` | {duration:.1f}秒 | 已核验 |"
    text = path.read_text(encoding="utf-8")
    if token in text:
        rows = []
        for raw in text.splitlines():
            if raw.startswith("| 74 |"):
                rows.append(line)
            else:
                rows.append(raw)
        path.write_text("\n".join(rows) + "\n", encoding="utf-8")
        return
    marker = "## 本轮 61+（核验中）"
    if marker not in text:
        path.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8")
        return
    rows = []
    inserted = False
    for raw in text.splitlines():
        rows.append(raw)
        if (not inserted) and raw.startswith("| 69 |"):
            rows.append(line)
            inserted = True
    if not inserted:
        rows.append(line)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    C.cut_shot = cut_shot_loop
    mapping = {
        "V-挥手.mp4": ASSET_06,
        "V-指向.mp4": ASSET_06,
        "V-点赞.mp4": ASSET_06,
        "V-摊手.mp4": ASSET_06,
        "A-角色-小灯-摊手.jpg": ASSET_06,
        "V-正对讲.mp4": ASSET_25,
    }
    C.copy_named_assets(ROOT / "assets", mapping)
    point = ROOT / "assets" / "A-角色-小灯-指向.jpg"
    if not point.exists():
        src = ROOT / "assets" / "A-正对讲.jpg"
        if (ASSET_25 / "A-正对讲.jpg").exists() and not src.exists():
            __import__("shutil").copy2(ASSET_25 / "A-正对讲.jpg", src)
        if src.exists():
            __import__("shutil").copy2(src, point)
        else:
            __import__("shutil").copy2(ROOT / "assets" / "A-角色-小灯-摊手.jpg", point)
    han = sum(len(p.replace("，", "").replace("。", "").replace("：", "")) for p in PHRASES)
    print("phrases", len(PHRASES), "han", han)
    duration, cues = C.make_voiceover(ROOT, PHRASES)
    print("VO", duration, C.zh_seconds(duration))
    for row in cues:
        print(f"  {row[0]:6.3f}-{row[1]:6.3f}  {row[2]}")
    if not (40.0 - 0.2 <= duration <= 50.0 + 0.2):
        raise SystemExit(f"VO not in 40-50s: {duration:.3f}")
    data = build_timeline(cues, duration)
    print("timeline", [(s["id"], s["start"], s["end"], s["kind"]) for s in data["shots"]])
    bmap = {s["id"]: s for s in data["shots"]}
    C.frames_to_mp4(render_b_weld(max(2.6, bmap["S02"]["end"] - bmap["S02"]["start"]) + 0.16), ROOT / "broll" / "B-焊成一坨.mp4")
    C.frames_to_mp4(render_b_cut(max(2.4, bmap["S04"]["end"] - bmap["S04"]["start"]) + 0.16), ROOT / "broll" / "B-剪成方块.mp4")
    name_dur = max(
        bmap["S05"]["end"] - bmap["S05"]["start"],
        bmap["S06"]["end"] - bmap["S06"]["start"],
    )
    C.frames_to_mp4(render_b_name(max(2.8, name_dur) + 0.16), ROOT / "broll" / "B-起名字.mp4")
    C.frames_to_mp4(render_b_road(max(2.8, bmap["S08"]["end"] - bmap["S08"]["start"]) + 0.16), ROOT / "broll" / "B-路线条.mp4")
    C.frames_to_mp4(render_b_motto(max(2.6, bmap["S08"]["end"] - bmap["S08"]["start"]) + 0.16), ROOT / "broll" / "B-对照.mp4")
    make_cover()
    staged = C.assemble(ROOT, data, NAME, STAGED_NAME)
    dur = C.probe_dur(staged)
    C.write_docs(
        ROOT,
        episode=74,
        name=NAME,
        staged_name=STAGED_NAME,
        duration=dur,
        data=data,
        source_note="topics-batch4.md #74 / 学习基线 2026-09-09 下一章：函数",
        note_body="钩子：菜单还是一整段，选项全焊在一块。做法：把各选项拆成函数，一块事一个名字。对照：焊死整段只能整坨搬，起名字就能单独改。收束：先消化起名字，文件和异常往后排。不讲存盘写法，不讲异常整章，不跳 C++ / ROS2。",
    )
    C.patch_index(STAGED_NAME, dur)
    patch_batch4(dur)
    patch_delivery(dur)
    report = C.qa(ROOT, staged, data, "74_菜单拆成函数")
    print("STAGED", staged, "dur", dur, C.zh_seconds(dur), "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
