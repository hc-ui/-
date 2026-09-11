#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 57：一张对照卡只打一个点。topics-batch3 #57。加长到四十到五十秒。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import longform_common as C  # noqa: E402

NAME = "一张对照卡只打一个点"
STAGED_NAME = "57-一张对照卡只打一个点.mp4"
ASSET_06 = Path("/workspace/.abroll-cloud/06/assets")
ASSET_25 = Path("/workspace/.abroll-cloud/25/assets")
PHRASES = [
    "大家好",
    "知识口播最容易胖的，不是字多，是一屏同时打三枪",
    "三枪一起出，一枪都没进",
    "观众眼睛只能停在一个对照上",
    "左边是错法，右边是做法",
    "一张对照卡，只打一个点",
    "信息图不是目录墙，是反差",
    "目录墙像五条建议叠在一起，他一张都带不走",
    "你要他记住的，不是五条建议，是那一对对错",
    "多出来的点，先别上这张卡",
    "一屏只留一对",
    "第二对会把第一对冲掉",
    "多的点，下一张再打",
    "先画左右两边，再写要他带走的那一句",
    "下回做卡片，先画对照，再写金句",
]


def render_b_three(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * C.FPS))
    guns = [("建议一", 0.16), ("建议二", 0.34), ("建议三", 0.52)]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "错 · 一屏三枪")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 230 + int(C.lerp(16, 0, a0))), "不是字多", font=C.font(40), fill=C.mix(C.BG, C.MUTED, a0), anchor="mm")
        d.text((C.W // 2, 300 + int(C.lerp(16, 0, a0))), "是一屏同时打三枪", font=C.font(50), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        for idx, (label, ts) in enumerate(guns):
            aa = C.appear(t, ts, 0.20)
            if aa < 0.04:
                continue
            x = 90 + idx * 310
            y = 420 + int(C.lerp(20, 0, aa))
            C.rounded(d, (x, y, x + 290, y + 280), 28, C.mix(C.BG, C.CARD, aa))
            d.text((x + 145, y + 90), f"{idx + 1}", font=C.font(56), fill=C.mix(C.CARD, C.YELLOW, aa), anchor="mm")
            d.text((x + 145, y + 180), label, font=C.font(36), fill=C.mix(C.CARD, C.WHITE, aa), anchor="mm")
            miss = C.appear(t, 1.15 + idx * 0.08, 0.18)
            C.draw_x(d, x + 145, y + 230, miss, 28)
        punch = C.appear(t, max(1.55, duration * 0.58), 0.22)
        if punch > 0.04:
            y = 820 + int(C.lerp(16, 0, punch))
            C.rounded(d, (120, y, 960, y + 200), 28, C.mix(C.BG, (42, 24, 22), punch))
            d.text((C.W // 2, y + 100), "三枪一起出，一枪都没进", font=C.font(40), fill=C.mix(C.BG, C.YELLOW, punch), anchor="mm")
        yield img


def render_b_sides(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * C.FPS))
    out = []
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "对照 · 左右一眼")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 236 + int(C.lerp(16, 0, a0))), "只停一个对照", font=C.font(52), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        a1 = C.appear(t, 0.16)
        if a1 > 0.04:
            y = 340 + int(C.lerp(18, 0, a1))
            C.rounded(d, (70, y, 510, y + 520), 32, C.mix(C.BG, (42, 24, 22), a1))
            d.text((290, y + 90), "左", font=C.font(30), fill=C.mix(C.CARD, C.MUTED, a1), anchor="mm")
            d.text((290, y + 200), "错法", font=C.font(64), fill=C.mix(C.CARD, C.RED, a1), anchor="mm")
            d.text((290, y + 320), "一屏三枪", font=C.font(36), fill=C.mix(C.CARD, C.WHITE, a1), anchor="mm")
            C.draw_x(d, 290, y + 420, C.appear(t, 0.80, 0.20), 32)
        a2 = C.appear(t, 0.28)
        if a2 > 0.04:
            y = 340 + int(C.lerp(18, 0, a2))
            C.rounded(d, (570, y, 1010, y + 520), 32, C.mix(C.BG, (18, 42, 36), a2))
            d.text((790, y + 90), "右", font=C.font(30), fill=C.mix(C.CARD, C.MUTED, a2), anchor="mm")
            d.text((790, y + 200), "做法", font=C.font(64), fill=C.mix(C.CARD, C.MINT, a2), anchor="mm")
            d.text((790, y + 320), "一对对错", font=C.font(36), fill=C.mix(C.CARD, C.WHITE, a2), anchor="mm")
            C.check_badge(d, 790, y + 420, C.appear(t, 0.92, 0.20))
        yield img


def render_b_one(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * C.FPS))
    out = []
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "规则 · 一张一点")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 240 + int(C.lerp(16, 0, a0))), "一张对照卡", font=C.font(54), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        a1 = C.appear(t, 0.18)
        if a1 > 0.04:
            y = 360 + int(C.lerp(20, 0, a1))
            C.rounded(d, (120, y, 960, y + 520), 36, C.mix(C.BG, C.CARD, a1))
            d.text((C.W // 2, y + 120), "只打", font=C.font(40), fill=C.mix(C.CARD, C.MUTED, a1), anchor="mm")
            d.text((C.W // 2, y + 250), "一个点", font=C.font(72), fill=C.mix(C.CARD, C.YELLOW, a1), anchor="mm")
            C.check_badge(d, C.W // 2, y + 400, C.appear(t, 0.90, 0.22))
        punch = C.appear(t, 1.30, 0.22)
        if punch > 0.04:
            y = 980 + int(C.lerp(16, 0, punch))
            C.rounded(d, (140, y, 940, y + 180), 28, C.mix(C.BG, (18, 42, 36), punch))
            d.text((C.W // 2, y + 90), "多出来的点，下一张再打", font=C.font(36), fill=C.mix(C.BG, C.MINT, punch), anchor="mm")
        yield img


def render_b_contrast(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * C.FPS))
    wall = ["建议一", "建议二", "建议三", "建议四", "建议五"]
    out = []
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "信息图 · 是反差")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 230 + int(C.lerp(16, 0, a0))), "不是目录墙", font=C.font(52), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        split = max(1.35, duration * 0.42)
        if t < split:
            for idx, name in enumerate(wall):
                aa = C.appear(t, 0.16 + idx * 0.08, 0.16)
                if aa < 0.04:
                    continue
                y = 340 + idx * 130
                C.rounded(d, (140, y, 940, y + 110), 22, C.mix(C.BG, C.CARD, aa))
                d.text((C.W // 2, y + 55), name, font=C.font(40), fill=C.mix(C.CARD, C.WHITE, aa), anchor="mm")
        else:
            aa = C.appear(t, split, 0.24)
            C.rounded(d, (120, 360, 960, 980), 36, C.mix(C.BG, C.CARD, aa))
            d.text((C.W // 2, 460), "撕成一张卡", font=C.font(32), fill=C.mix(C.CARD, C.MUTED, aa), anchor="mm")
            d.text((340, 640), "错", font=C.font(72), fill=C.mix(C.CARD, C.RED, aa), anchor="mm")
            d.text((740, 640), "对", font=C.font(72), fill=C.mix(C.CARD, C.MINT, aa), anchor="mm")
            d.text((C.W // 2, 820), "记住那一对对错", font=C.font(40), fill=C.mix(C.CARD, C.YELLOW, aa), anchor="mm")
        yield img


def render_b_next(duration: float) -> list[Image.Image]:
    n = max(1, round(duration * C.FPS))
    out = []
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "规则 · 多的点下一张")
        third = duration / 3.0
        if t < third:
            a = C.appear(t, 0.02)
            d.text((C.W // 2, 250 + int(C.lerp(16, 0, a))), "一屏只留一对", font=C.font(52), fill=C.mix(C.BG, C.WHITE, a), anchor="mm")
            left = int(C.lerp(-20, 80, a))
            right = int(C.lerp(C.W + 20, 560, a))
            C.rounded(d, (left, 360, left + 430, 1100), 32, C.mix(C.BG, C.CARD, a))
            C.rounded(d, (right, 360, right + 430, 1100), 32, C.mix(C.BG, C.CARD, a))
            d.text((left + 215, 520), "第一对", font=C.font(32), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            d.text((left + 215, 700), "对 / 错", font=C.font(56), fill=C.mix(C.CARD, C.YELLOW, a), anchor="mm")
            d.text((right + 215, 520), "第二对", font=C.font(32), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            d.text((right + 215, 700), "又一对", font=C.font(56), fill=C.mix(C.CARD, C.RED, a), anchor="mm")
            wash = C.appear(t, third * 0.42, 0.36)
            if wash > 0.04:
                C.strike_line(d, (left + 40, 640, left + 390, 760), wash, C.mix(C.CARD, C.RED, wash))
                d.text((C.W // 2, 1220), "第二对冲掉第一对", font=C.font(40), fill=C.mix(C.BG, C.RED, wash), anchor="mm")
        elif t < third * 2:
            a = C.appear(t, third, 0.22)
            d.text((C.W // 2, 250), "两对叠在一起", font=C.font(50), fill=C.mix(C.BG, C.WHITE, a), anchor="mm")
            d.text((C.W // 2, 330), "一张都记不住", font=C.font(40), fill=C.mix(C.BG, C.RED, a), anchor="mm")
            C.rounded(d, (90, 420, 990, 1100), 36, C.mix(C.BG, C.CARD, a))
            d.text((C.W // 2, 620), "对错 + 对错", font=C.font(52), fill=C.mix(C.CARD, C.WHITE, a), anchor="mm")
            d.text((C.W // 2, 800), "眼睛不知道停哪", font=C.font(44), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            C.strike_line(d, (180, 560, 900, 680), C.appear(t, third + 0.55, 0.28), C.mix(C.CARD, C.RED, a))
        else:
            a = C.appear(t, third * 2, 0.22)
            d.text((C.W // 2, 240), "这张只留一对", font=C.font(50), fill=C.mix(C.BG, C.WHITE, a), anchor="mm")
            C.rounded(d, (80, 340, 500, 980), 32, C.mix(C.BG, (22, 40, 36), a))
            C.rounded(d, (580, 340, 1000, 980), 32, C.mix(C.BG, C.CARD, a))
            d.text((290, 480), "这张", font=C.font(30), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            d.text((290, 640), "一对对错", font=C.font(44), fill=C.mix(C.CARD, C.MINT, a), anchor="mm")
            d.text((790, 480), "下一张", font=C.font(30), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            d.text((790, 640), "多的点", font=C.font(44), fill=C.mix(C.CARD, C.YELLOW, a), anchor="mm")
            punch = C.appear(t, third * 2 + 0.70, 0.24)
            if punch > 0.04:
                y = 1080 + int(C.lerp(20, 0, punch))
                C.rounded(d, (140, y, 940, y + 200), 28, C.mix(C.BG, (18, 42, 36), punch))
                d.text((C.W // 2, y + 100), "下一张再打", font=C.font(52), fill=C.mix(C.BG, C.MINT, punch), anchor="mm")
        yield img


def build_timeline(cues, duration: float) -> dict:
    if len(cues) != 15:
        raise SystemExit(f"need 15 phrases, got {len(cues)}")
    p = cues
    b1 = max(p[1][1] + 0.06, p[2][0] - C.LEAD)
    b1e = p[2][1]
    a3 = p[2][1]
    b2 = max(p[3][1] + 0.06, p[4][0] - C.LEAD)
    b2e = p[4][1]
    b3 = p[5][0]
    b3e = p[5][1]
    b4 = p[6][0]
    b4e = p[8][1]
    a7 = p[8][1]
    b8 = max(p[9][1] + 0.06, p[10][0] - C.LEAD)
    b8e = p[13][1]
    shots = [
        {"id": "S01a", "kind": "A", "start": 0.0, "end": p[0][1], "src": "assets/V-挥手.mp4", "line": p[0][2], "close": True},
        {"id": "S01b", "kind": "A", "start": p[0][1], "end": b1, "src": "assets/V-正对讲.mp4", "line": p[1][2]},
        {"id": "S02", "kind": "B", "start": b1, "end": b1e, "src": "broll/B-一屏三枪.mp4", "line": p[2][2], "broll": "three"},
        {"id": "S03", "kind": "A", "start": a3, "end": b2, "src": "assets/V-指向.mp4", "line": p[3][2]},
        {"id": "S04", "kind": "B", "start": b2, "end": b2e, "src": "broll/B-左右对照.mp4", "line": p[4][2], "broll": "sides"},
        {"id": "S05", "kind": "B", "start": b3, "end": b3e, "src": "broll/B-一张一点.mp4", "line": p[5][2], "broll": "one"},
        {"id": "S06", "kind": "B", "start": b4, "end": b4e, "src": "broll/B-反差.mp4", "line": p[8][2], "broll": "contrast"},
        {"id": "S07", "kind": "A", "start": a7, "end": b8, "src": "assets/V-摊手.mp4", "line": p[9][2]},
        {"id": "S08", "kind": "B", "start": b8, "end": b8e, "src": "broll/B-下一张再打.mp4", "line": p[12][2], "broll": "next_card"},
        {"id": "S09", "kind": "A", "start": b8e, "end": duration, "src": "assets/V-点赞.mp4", "line": p[14][2]},
    ]
    shots = C.close_shots(shots, duration)
    a_caps = [
        {"start": 0.0, "end": shots[0]["end"], "lines": ["大家好"]},
        {"start": shots[1]["start"], "end": shots[1]["end"], "lines": ["知识口播最容易胖的"]},
        {"start": shots[3]["start"], "end": shots[3]["end"], "lines": ["只能停在", "一个对照上"]},
        {"start": shots[7]["start"], "end": shots[7]["end"], "lines": C.split_caption(p[9][2])},
        {"start": shots[9]["start"], "end": duration, "lines": ["先画对照", "再写金句"]},
    ]
    shutters = [
        {"start": shots[1]["start"], "color": list(C.CREAM)},
        {"start": shots[2]["start"], "color": list(C.MINT)},
        {"start": shots[3]["start"], "color": list(C.CREAM)},
        {"start": shots[4]["start"], "color": list(C.MINT)},
        {"start": shots[5]["start"], "color": list(C.YELLOW)},
        {"start": shots[6]["start"], "color": list(C.MINT)},
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
        "cover_title": "一张对照卡",
        "cover_sub": "只打一个点",
        "cover_line": "错法 · 做法 · 反差",
        "cover_src": "assets/A-角色-小灯-指向.jpg",
    }
    (ROOT / "plan").mkdir(exist_ok=True)
    (ROOT / "plan" / "shot_recipe.json").write_text(json.dumps(recipe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
        "factory": "13_对照卡",
        "topic": 57,
        "source_note": "topics-batch3.md #57 / 工厂 13_对照卡",
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
    d.text((C.W // 2, 160), "一张对照卡", font=C.font(52), fill=C.WHITE, anchor="mm")
    d.text((C.W // 2, 250), "只打一个点", font=C.font(64), fill=C.YELLOW, anchor="mm")
    d.text((C.W // 2, 340), "错法 · 做法 · 反差", font=C.font(36), fill=C.MINT, anchor="mm")
    d.text((C.W // 2, 410), "先画对照，再写金句", font=C.font(30), fill=C.MUTED, anchor="mm")
    dest = ROOT / f"00_封面_{NAME}.jpg"
    canvas.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    canvas.save(ROOT / "final" / "cover.jpg", quality=92)
    return dest


def main() -> None:
    mapping = {
        "V-挥手.mp4": ASSET_06,
        "V-指向.mp4": ASSET_06,
        "V-点赞.mp4": ASSET_06,
        "V-摊手.mp4": ASSET_06,
        "A-角色-小灯-摊手.jpg": ASSET_06,
        "V-正对讲.mp4": ASSET_25,
    }
    if (ASSET_25 / "A-正对讲.jpg").exists():
        mapping["A-正对讲.jpg"] = ASSET_25
    C.copy_named_assets(ROOT / "assets", mapping)
    point = ROOT / "assets" / "A-角色-小灯-指向.jpg"
    if not point.exists():
        src = ROOT / "assets" / "A-正对讲.jpg"
        if src.exists():
            src.replace(point) if False else __import__("shutil").copy2(src, point)
        else:
            __import__("shutil").copy2(ROOT / "assets" / "A-角色-小灯-摊手.jpg", point)
    duration, cues = C.make_voiceover(ROOT, PHRASES)
    print("VO", duration, C.zh_seconds(duration))
    for row in cues:
        print(f"  {row[0]:6.3f}-{row[1]:6.3f}  {row[2]}")
    data = build_timeline(cues, duration)
    print("timeline", [(s["id"], s["start"], s["end"], s["kind"]) for s in data["shots"]])
    bmap = {s["id"]: s for s in data["shots"]}
    C.frames_to_mp4(render_b_three(max(2.4, bmap["S02"]["end"] - bmap["S02"]["start"]) + 0.12), ROOT / "broll" / "B-一屏三枪.mp4")
    C.frames_to_mp4(render_b_sides(max(2.4, bmap["S04"]["end"] - bmap["S04"]["start"]) + 0.12), ROOT / "broll" / "B-左右对照.mp4")
    C.frames_to_mp4(render_b_one(max(2.4, bmap["S05"]["end"] - bmap["S05"]["start"]) + 0.12), ROOT / "broll" / "B-一张一点.mp4")
    C.frames_to_mp4(render_b_contrast(max(2.4, bmap["S06"]["end"] - bmap["S06"]["start"]) + 0.12), ROOT / "broll" / "B-反差.mp4")
    C.frames_to_mp4(render_b_next(max(2.4, bmap["S08"]["end"] - bmap["S08"]["start"]) + 0.12), ROOT / "broll" / "B-下一张再打.mp4")
    make_cover()
    staged = C.assemble(ROOT, data, NAME, STAGED_NAME)
    dur = C.probe_dur(staged)
    C.write_docs(
        ROOT, episode=57, name=NAME, staged_name=STAGED_NAME, duration=dur, data=data,
        source_note="topics-batch3.md #57 / 工厂 13_对照卡",
        note_body="钩子：一屏同时打三枪。做法：左边错法，右边做法，一张只打一个点。补镜：多出来的点先别上这张卡，第二对会冲掉第一对，多的点下一张再打。收束：先画对照，再写金句。下回做卡片是做法口令，不是预告下一期。",
    )
    C.patch_index(STAGED_NAME, dur)
    C.patch_topics_row(57, STAGED_NAME, dur, "未完成知识口播")
    report = C.qa(ROOT, staged, data, "57_一张对照卡只打一个点")
    print("STAGED", staged, "dur", dur, C.zh_seconds(dur), "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
