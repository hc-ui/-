#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 64：空字典写在循环外面。topics-batch3 #41 原文，成片号 41 已被占用，本集 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/64/，成品中转 成片/64-空字典写在循环外面.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
只打容器出生地点，不重复成片 13 / 42 / 43。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import longform_common as C  # noqa: E402

NAME = "空字典写在循环外面"
STAGED_NAME = "64-空字典写在循环外面.mp4"
ASSET_06 = Path("/workspace/.abroll-cloud/06/assets")
ASSET_25 = Path("/workspace/.abroll-cloud/25/assets")
PHRASES = [
    "大家好",
    "点一次菜单，成绩册就空了",
    "不是字典坏了，是空字典建在了循环里面",
    "空花括号写进了循环里头，每进一轮就重建一次",
    "每选一次菜单，整本成绩被揉成白纸",
    "容器的出生地点，决定它能不能活过下一轮",
    "循环外建，才能活过下一轮",
    "循环里建，每进一次门就重建一次",
    "空字典在门外建，别在门里重建",
    "门外建一次，门里只读写，不再新建",
    "先让菜单能退出，再增和列出",
    "先把出生地点写对，别急着加新语法",
    "对照只打这一点：门外建，门里不重建",
    "写循环之前，先问字典出生在哪",
    "出生在门外还能留下，出生在门里下一轮就是空的",
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
        vf = f"scale={C.W}:{C.H}:force_original_aspect_ratio=decrease,pad={C.W}:{C.H}:(ow-iw)/2:(oh-ih)/2,fps={C.FPS},setsar=1,format=yuv420p"
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


def render_b_wipe(duration: float):
    n = max(1, round(duration * C.FPS))
    menus = [("增", 0.18), ("列", 0.34), ("退", 0.50)]
    names = [("林", "88"), ("周", "91"), ("陈", "76")]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "错 · 点一次就空")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 230 + int(C.lerp(16, 0, a0))), "点一次菜单", font=C.font(48), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        d.text((C.W // 2, 300 + int(C.lerp(16, 0, a0))), "成绩册就空了", font=C.font(52), fill=C.mix(C.BG, C.YELLOW, a0), anchor="mm")
        for idx, (label, ts) in enumerate(menus):
            aa = C.appear(t, ts, 0.18)
            if aa < 0.04:
                continue
            x = 110 + idx * 300
            y = 380 + int(C.lerp(18, 0, aa))
            C.rounded(d, (x, y, x + 260, y + 150), 24, C.mix(C.BG, C.CARD, aa))
            d.text((x + 130, y + 75), label, font=C.font(56), fill=C.mix(C.CARD, C.WHITE, aa), anchor="mm")
        wipe = C.appear(t, max(1.20, duration * 0.38), 0.28)
        for idx, (name, score) in enumerate(names):
            aa = C.appear(t, 0.70 + idx * 0.10, 0.18)
            if aa < 0.04:
                continue
            y = 600 + idx * 150
            C.rounded(d, (160, y, 920, y + 130), 22, C.mix(C.BG, C.CARD, aa))
            shown = "" if wipe > 0.55 else f"{name}  {score}"
            fill = C.mix(C.CARD, C.MUTED if wipe > 0.55 else C.WHITE, aa)
            d.text((C.W // 2, y + 65), shown if shown else "——", font=C.font(44), fill=fill, anchor="mm")
            C.strike_line(d, (200, y, 880, y + 130), wipe, C.mix(C.CARD, C.RED, wipe))
        punch = C.appear(t, max(1.70, duration * 0.62), 0.22)
        if punch > 0.04:
            y = 1100 + int(C.lerp(16, 0, punch))
            C.rounded(d, (120, y, 960, y + 200), 28, C.mix(C.BG, (42, 24, 22), punch))
            d.text((C.W // 2, y + 100), "整本成绩被揉成白纸", font=C.font(40), fill=C.mix(C.BG, C.YELLOW, punch), anchor="mm")
        yield img


def render_b_inside(duration: float):
    n = max(1, round(duration * C.FPS))
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "错 · 循环里建")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 236 + int(C.lerp(16, 0, a0))), "写进循环里头", font=C.font(50), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        a1 = C.appear(t, 0.16)
        if a1 > 0.04:
            y = 340 + int(C.lerp(18, 0, a1))
            C.rounded(d, (90, y, 990, y + 620), 32, C.mix(C.BG, C.CARD, a1))
            d.text((C.W // 2, y + 80), "while 一轮", font=C.font(32), fill=C.mix(C.CARD, C.MUTED, a1), anchor="mm")
            d.text((C.W // 2, y + 200), "空花括号", font=C.font(64), fill=C.mix(C.CARD, C.RED, a1), anchor="mm")
            d.text((C.W // 2, y + 320), "建在门里", font=C.font(48), fill=C.mix(C.CARD, C.WHITE, a1), anchor="mm")
            d.text((C.W // 2, y + 430), "每进一轮就重建一次", font=C.font(36), fill=C.mix(C.CARD, C.YELLOW, a1), anchor="mm")
            C.draw_x(d, C.W // 2, y + 530, C.appear(t, 0.90, 0.20), 36)
        punch = C.appear(t, max(1.35, duration * 0.55), 0.22)
        if punch > 0.04:
            y = 1040 + int(C.lerp(16, 0, punch))
            C.rounded(d, (140, y, 940, y + 180), 28, C.mix(C.BG, (42, 24, 22), punch))
            d.text((C.W // 2, y + 90), "下一轮就是空的", font=C.font(40), fill=C.mix(C.BG, C.RED, punch), anchor="mm")
        yield img


def render_b_outside(duration: float):
    n = max(1, round(duration * C.FPS))
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "对 · 循环外建")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 236 + int(C.lerp(16, 0, a0))), "循环外建", font=C.font(56), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        d.text((C.W // 2, 310 + int(C.lerp(16, 0, a0))), "才能活过下一轮", font=C.font(40), fill=C.mix(C.BG, C.MINT, a0), anchor="mm")
        a1 = C.appear(t, 0.18)
        if a1 > 0.04:
            y = 400 + int(C.lerp(18, 0, a1))
            C.rounded(d, (90, y, 990, y + 560), 32, C.mix(C.BG, C.CARD, a1))
            d.text((C.W // 2, y + 90), "门外先建一次", font=C.font(36), fill=C.mix(C.CARD, C.MUTED, a1), anchor="mm")
            d.text((C.W // 2, y + 220), "空花括号", font=C.font(64), fill=C.mix(C.CARD, C.MINT, a1), anchor="mm")
            d.text((C.W // 2, y + 340), "门里只读写", font=C.font(48), fill=C.mix(C.CARD, C.WHITE, a1), anchor="mm")
            C.check_badge(d, C.W // 2, y + 460, C.appear(t, 0.92, 0.22))
        punch = C.appear(t, max(1.30, duration * 0.55), 0.22)
        if punch > 0.04:
            y = 1060 + int(C.lerp(16, 0, punch))
            C.rounded(d, (140, y, 940, y + 180), 28, C.mix(C.BG, (18, 42, 36), punch))
            d.text((C.W // 2, y + 90), "下一轮还在", font=C.font(48), fill=C.mix(C.BG, C.MINT, punch), anchor="mm")
        yield img


def render_b_door(duration: float):
    n = max(1, round(duration * C.FPS))
    third = duration / 3.0
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "对照 · 门外 / 门里")
        if t < third:
            a = C.appear(t, 0.02)
            d.text((C.W // 2, 240 + int(C.lerp(16, 0, a))), "循环里建", font=C.font(52), fill=C.mix(C.BG, C.WHITE, a), anchor="mm")
            C.rounded(d, (120, 360, 960, 980), 36, C.mix(C.BG, C.CARD, a))
            d.text((C.W // 2, 520), "每进一次门", font=C.font(44), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            d.text((C.W // 2, 640), "就重建一次", font=C.font(56), fill=C.mix(C.CARD, C.RED, a), anchor="mm")
            C.draw_x(d, C.W // 2, 820, C.appear(t, 0.70, 0.22), 40)
        elif t < third * 2:
            a = C.appear(t, third, 0.22)
            d.text((C.W // 2, 230), "一张对照", font=C.font(40), fill=C.mix(C.BG, C.MUTED, a), anchor="mm")
            d.text((C.W // 2, 300), "只打出生地点", font=C.font(48), fill=C.mix(C.BG, C.WHITE, a), anchor="mm")
            C.rounded(d, (70, 380, 510, 1100), 32, C.mix(C.BG, (42, 24, 22), a))
            C.rounded(d, (570, 380, 1010, 1100), 32, C.mix(C.BG, (18, 42, 36), a))
            d.text((290, 500), "门里", font=C.font(32), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            d.text((290, 680), "重建", font=C.font(64), fill=C.mix(C.CARD, C.RED, a), anchor="mm")
            C.draw_x(d, 290, 860, C.appear(t, third + 0.40, 0.20), 32)
            d.text((790, 500), "门外", font=C.font(32), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            d.text((790, 680), "建一次", font=C.font(56), fill=C.mix(C.CARD, C.MINT, a), anchor="mm")
            C.check_badge(d, 790, 860, C.appear(t, third + 0.55, 0.20))
        else:
            a = C.appear(t, third * 2, 0.22)
            d.text((C.W // 2, 240), "空字典在门外建", font=C.font(50), fill=C.mix(C.BG, C.WHITE, a), anchor="mm")
            d.text((C.W // 2, 320), "别在门里重建", font=C.font(44), fill=C.mix(C.BG, C.YELLOW, a), anchor="mm")
            C.rounded(d, (120, 420, 960, 980), 36, C.mix(C.BG, C.CARD, a))
            d.text((C.W // 2, 580), "门外建一次", font=C.font(48), fill=C.mix(C.CARD, C.MINT, a), anchor="mm")
            d.text((C.W // 2, 700), "门里只读写", font=C.font(48), fill=C.mix(C.CARD, C.WHITE, a), anchor="mm")
            d.text((C.W // 2, 820), "不再新建", font=C.font(44), fill=C.mix(C.CARD, C.YELLOW, a), anchor="mm")
            punch = C.appear(t, third * 2 + 0.70, 0.22)
            if punch > 0.04:
                y = 1080 + int(C.lerp(16, 0, punch))
                C.rounded(d, (140, y, 940, y + 180), 28, C.mix(C.BG, (18, 42, 36), punch))
                d.text((C.W // 2, y + 90), "活过下一轮", font=C.font(48), fill=C.mix(C.BG, C.MINT, punch), anchor="mm")
        yield img


def render_b_motto(duration: float):
    n = max(1, round(duration * C.FPS))
    steps = [("退出", 0.18), ("再增", 0.36), ("再列", 0.54)]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "口诀 · 门外建")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 240 + int(C.lerp(16, 0, a0))), "先问出生在哪", font=C.font(50), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        a1 = C.appear(t, 0.16)
        if a1 > 0.04:
            y = 340 + int(C.lerp(18, 0, a1))
            C.rounded(d, (90, y, 990, y + 360), 32, C.mix(C.BG, C.CARD, a1))
            d.text((C.W // 2, y + 110), "空字典在门外建", font=C.font(48), fill=C.mix(C.CARD, C.YELLOW, a1), anchor="mm")
            d.text((C.W // 2, y + 230), "别在门里重建", font=C.font(44), fill=C.mix(C.CARD, C.WHITE, a1), anchor="mm")
        for idx, (label, ts) in enumerate(steps):
            aa = C.appear(t, ts + 0.40, 0.18)
            if aa < 0.04:
                continue
            x = 90 + idx * 310
            y = 780 + int(C.lerp(16, 0, aa))
            C.rounded(d, (x, y, x + 280, y + 200), 24, C.mix(C.BG, C.CARD, aa))
            d.text((x + 140, y + 100), label, font=C.font(48), fill=C.mix(C.CARD, C.MINT, aa), anchor="mm")
        punch = C.appear(t, max(1.50, duration * 0.58), 0.22)
        if punch > 0.04:
            y = 1080 + int(C.lerp(16, 0, punch))
            C.rounded(d, (120, y, 960, y + 200), 28, C.mix(C.BG, (18, 42, 36), punch))
            d.text((C.W // 2, y + 100), "出生地点写对再往下", font=C.font(40), fill=C.mix(C.BG, C.MINT, punch), anchor="mm")
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
        {"id": "S02", "kind": "B", "start": b1, "end": b1e, "src": "broll/B-揉成白纸.mp4", "line": p[4][2], "broll": "wipe"},
        {"id": "S03", "kind": "A", "start": a3, "end": b2, "src": "assets/V-指向.mp4", "line": p[5][2]},
        {"id": "S04", "kind": "B", "start": b2, "end": b2e, "src": "broll/B-循环外建.mp4", "line": p[6][2], "broll": "outside"},
        {"id": "S05", "kind": "B", "start": b3, "end": b3e, "src": "broll/B-循环里建.mp4", "line": p[7][2], "broll": "inside"},
        {"id": "S06", "kind": "B", "start": b4, "end": b4e, "src": "broll/B-门外门里.mp4", "line": p[8][2], "broll": "door"},
        {"id": "S07", "kind": "A", "start": a7, "end": b8, "src": "assets/V-摊手.mp4", "line": p[10][2]},
        {"id": "S08", "kind": "B", "start": b8, "end": b8e, "src": "broll/B-口诀.mp4", "line": p[12][2], "broll": "motto"},
        {"id": "S09", "kind": "A", "start": b8e, "end": duration, "src": "assets/V-点赞.mp4", "line": p[14][2]},
    ]
    shots = C.close_shots(shots, duration)
    a_caps = [
        {"start": 0.0, "end": shots[0]["end"], "lines": ["大家好"]},
        {"start": shots[1]["start"], "end": shots[1]["end"], "lines": ["点一次菜单", "成绩册就空了"]},
        {"start": shots[3]["start"], "end": shots[3]["end"], "lines": C.split_caption(p[5][2])},
        {"start": shots[7]["start"], "end": shots[7]["end"], "lines": C.split_caption(p[10][2])},
        {"start": shots[9]["start"], "end": duration, "lines": ["门外还能留下", "门里下一轮空"]},
    ]
    shutters = [
        {"start": shots[1]["start"], "color": list(C.CREAM)},
        {"start": shots[2]["start"], "color": list(C.MINT)},
        {"start": shots[3]["start"], "color": list(C.CREAM)},
        {"start": shots[4]["start"], "color": list(C.MINT)},
        {"start": shots[5]["start"], "color": list(C.RED)},
        {"start": shots[6]["start"], "color": list(C.YELLOW)},
        {"start": shots[7]["start"], "color": list(C.CREAM)},
        {"start": shots[8]["start"], "color": list(C.MINT)},
        {"start": shots[9]["start"], "color": list(C.YELLOW)},
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
        "cover_title": "空字典",
        "cover_sub": "写在循环外面",
        "cover_line": "门外建 · 门里不重建",
        "cover_src": "assets/A-角色-小灯-指向.jpg",
    }
    (ROOT / "plan").mkdir(exist_ok=True)
    (ROOT / "plan" / "shot_recipe.json").write_text(json.dumps(recipe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "plan" / "broll.json").write_text(
        json.dumps(
            {
                "episode": 64,
                "cards": ["揉成白纸", "循环外建", "循环里建", "门外门里", "口诀"],
                "rule": "只打容器出生地点；不烧路径；不念文件名",
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
        "factory": "topics-batch3 #41 空字典",
        "topic": 64,
        "source_note": "topics-batch3.md #41 / 学习基线 2026-09-09 不足第5、第8条",
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
    d.text((C.W // 2, 160), "空字典", font=C.font(56), fill=C.WHITE, anchor="mm")
    d.text((C.W // 2, 250), "写在循环外面", font=C.font(58), fill=C.YELLOW, anchor="mm")
    d.text((C.W // 2, 340), "门外建 · 门里不重建", font=C.font(36), fill=C.MINT, anchor="mm")
    d.text((C.W // 2, 410), "出生地点决定下一轮还在不在", font=C.font(28), fill=C.MUTED, anchor="mm")
    dest = ROOT / f"00_封面_{NAME}.jpg"
    canvas.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    canvas.save(ROOT / "final" / "cover.jpg", quality=92)
    return dest


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
    C.frames_to_mp4(render_b_wipe(max(2.6, bmap["S02"]["end"] - bmap["S02"]["start"]) + 0.16), ROOT / "broll" / "B-揉成白纸.mp4")
    C.frames_to_mp4(render_b_outside(max(2.4, bmap["S04"]["end"] - bmap["S04"]["start"]) + 0.16), ROOT / "broll" / "B-循环外建.mp4")
    C.frames_to_mp4(render_b_inside(max(2.4, bmap["S05"]["end"] - bmap["S05"]["start"]) + 0.16), ROOT / "broll" / "B-循环里建.mp4")
    C.frames_to_mp4(render_b_door(max(2.8, bmap["S06"]["end"] - bmap["S06"]["start"]) + 0.16), ROOT / "broll" / "B-门外门里.mp4")
    C.frames_to_mp4(render_b_motto(max(2.6, bmap["S08"]["end"] - bmap["S08"]["start"]) + 0.16), ROOT / "broll" / "B-口诀.mp4")
    make_cover()
    staged = C.assemble(ROOT, data, NAME, STAGED_NAME)
    dur = C.probe_dur(staged)
    C.write_docs(
        ROOT,
        episode=64,
        name=NAME,
        staged_name=STAGED_NAME,
        duration=dur,
        data=data,
        source_note="topics-batch3.md #41 / 学习基线 2026-09-09 不足第5、第8条",
        note_body="钩子：点一次菜单，成绩册就空了。做法：空字典在门外建，别在门里重建。对照：循环外建活过下一轮，循环里建每进一门就重建。收束：写循环之前先问字典出生在哪。不讲从值找键，不用等号盖列表，不拆函数。",
    )
    C.patch_index(STAGED_NAME, dur)
    report = C.qa(ROOT, staged, data, "64_空字典写在循环外面")
    print("STAGED", staged, "dur", dur, C.zh_seconds(dur), "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
