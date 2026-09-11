#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 68：评审变成找茬会。工厂 68_评审变成找茬会。云端 NEW A-roll + B-roll。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/68/，成品中转 成片/68-评审变成找茬会.mp4。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
目标四十到五十秒。不定格、不慢放注水。时长用中文「秒」。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import longform_common as C  # noqa: E402

NAME = "评审变成找茬会"
STAGED_NAME = "68-评审变成找茬会.mp4"
ASSET_06 = Path("/workspace/.abroll-cloud/06/assets")
ASSET_25 = Path("/workspace/.abroll-cloud/25/assets")
PHRASES = [
    "大家好",
    "评审变成找茬会",
    "本来该看能不能过，却在抠标点、抠用词",
    "一条能过的方案，被十条口味意见按住",
    "不是意见太多，是评审忘了自己在审什么",
    "找茬会只证明谁更细，不证明方案能不能走",
    "被找茬的人下次少讲，问题被藏进抽屉",
    "评审该盯风险，不该盯口味",
    "先问这一条拦不拦过",
    "拦过的写成必须改",
    "口味写成可选，别和风险绑在一起",
    "对照一下：找茬是把人按住，评审是把路铺开",
    "会前先写三条必须看的点",
    "会上只打这三条，其余会后纸条",
    "散会时只带走必须改和谁改",
    "评审要能过，不要变成找茬会",
]


def render_b_nitpick(duration: float):
    n = max(1, round(duration * C.FPS))
    marks = [("标点", 0.18), ("用词", 0.38), ("空格", 0.58)]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "错 · 在抠标点")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 236 + int(C.lerp(16, 0, a0))), "该看能不能过", font=C.font(48), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        a1 = C.appear(t, 0.16)
        if a1 > 0.04:
            y = 340 + int(C.lerp(18, 0, a1))
            C.rounded(d, (110, y, 970, y + 280), 32, C.mix(C.BG, C.CARD, a1))
            d.text((C.W // 2, y + 90), "方案能过", font=C.font(56), fill=C.mix(C.CARD, C.MINT, a1), anchor="mm")
            d.text((C.W // 2, y + 190), "本该只审这一句", font=C.font(36), fill=C.mix(C.CARD, C.MUTED, a1), anchor="mm")
        for idx, (label, ts) in enumerate(marks):
            aa = C.appear(t, ts, 0.20)
            if aa < 0.04:
                continue
            x = 90 + idx * 310
            y = 700 + int(C.lerp(20, 0, aa))
            C.rounded(d, (x, y, x + 290, y + 240), 28, C.mix(C.BG, (42, 24, 22), aa))
            d.text((x + 145, y + 80), label, font=C.font(48), fill=C.mix(C.CARD, C.WHITE, aa), anchor="mm")
            C.draw_x(d, x + 145, y + 170, C.appear(t, ts + 0.22, 0.18), 28)
        punch = C.appear(t, max(1.35, duration * 0.55), 0.22)
        if punch > 0.04:
            y = 1020 + int(C.lerp(16, 0, punch))
            C.rounded(d, (120, y, 960, y + 180), 28, C.mix(C.BG, (42, 24, 22), punch))
            d.text((C.W // 2, y + 90), "却在抠标点、抠用词", font=C.font(40), fill=C.mix(C.BG, C.YELLOW, punch), anchor="mm")
        yield img


def render_b_taste(duration: float):
    n = max(1, round(duration * C.FPS))
    notes = ["我喜欢", "换个词", "我不会这么写", "再润色", "感觉不对"]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "后果 · 十条口味")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 230 + int(C.lerp(16, 0, a0))), "一条能过的方案", font=C.font(48), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        a1 = C.appear(t, 0.14)
        if a1 > 0.04:
            y = 320 + int(C.lerp(16, 0, a1))
            C.rounded(d, (160, y, 920, y + 220), 32, C.mix(C.BG, (18, 42, 36), a1))
            d.text((C.W // 2, y + 110), "能过", font=C.font(72), fill=C.mix(C.CARD, C.MINT, a1), anchor="mm")
        crush = C.appear(t, 0.55, 0.36)
        for idx, name in enumerate(notes):
            aa = C.appear(t, 0.48 + idx * 0.08, 0.16)
            if aa < 0.04:
                continue
            y = 600 + idx * 118 + int(C.lerp(14, 0, aa))
            C.rounded(d, (130, y, 950, y + 100), 22, C.mix(C.BG, C.CARD, aa))
            d.text((C.W // 2, y + 50), f"口味 {idx + 1}  {name}", font=C.font(36), fill=C.mix(C.CARD, C.WHITE, aa), anchor="mm")
        if crush > 0.04:
            C.strike_line(d, (180, 360, 900, 500), crush, C.mix(C.CARD, C.RED, crush))
        punch = C.appear(t, max(1.40, duration * 0.58), 0.22)
        if punch > 0.04:
            y = 1240 + int(C.lerp(16, 0, punch))
            C.rounded(d, (120, y, 960, y + 180), 28, C.mix(C.BG, (42, 24, 22), punch))
            d.text((C.W // 2, y + 90), "被十条口味按住", font=C.font(44), fill=C.mix(C.BG, C.YELLOW, punch), anchor="mm")
        yield img


def render_b_drawer(duration: float):
    n = max(1, round(duration * C.FPS))
    split = max(1.55, duration * 0.42)
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "后果 · 下次少讲")
        if t < split:
            a0 = C.appear(t, 0.02)
            d.text((C.W // 2, 240 + int(C.lerp(16, 0, a0))), "找茬会只证明", font=C.font(40), fill=C.mix(C.BG, C.MUTED, a0), anchor="mm")
            a1 = C.appear(t, 0.16)
            if a1 > 0.04:
                y = 340 + int(C.lerp(18, 0, a1))
                C.rounded(d, (80, y, 500, y + 520), 32, C.mix(C.BG, (42, 24, 22), a1))
                d.text((290, y + 140), "谁更细", font=C.font(56), fill=C.mix(C.CARD, C.RED, a1), anchor="mm")
                C.draw_x(d, 290, y + 360, C.appear(t, 0.70, 0.20), 36)
                C.rounded(d, (580, y, 1000, y + 520), 32, C.mix(C.BG, (18, 42, 36), a1))
                d.text((790, y + 140), "能不能走", font=C.font(48), fill=C.mix(C.CARD, C.MINT, a1), anchor="mm")
                C.check_badge(d, 790, y + 360, C.appear(t, 0.88, 0.20))
            d.text((C.W // 2, 980), "不证明方案能不能走", font=C.font(36), fill=C.mix(C.BG, C.WHITE, C.appear(t, 1.05)), anchor="mm")
        else:
            a = C.appear(t, split, 0.24)
            d.text((C.W // 2, 240), "下次少讲", font=C.font(52), fill=C.mix(C.BG, C.WHITE, a), anchor="mm")
            y = 360 + int(C.lerp(20, 0, a))
            C.rounded(d, (140, y, 940, y + 280), 32, C.mix(C.BG, C.CARD, a))
            d.text((C.W // 2, y + 90), "问题", font=C.font(36), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            d.text((C.W // 2, y + 180), "藏进抽屉", font=C.font(64), fill=C.mix(C.CARD, C.YELLOW, a), anchor="mm")
            C.rounded(d, (200, y + 360, 880, y + 620), 28, C.mix(C.BG, (28, 24, 20), a))
            d.text((C.W // 2, y + 490), "抽屉关上了", font=C.font(40), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            punch = C.appear(t, split + 0.70, 0.22)
            if punch > 0.04:
                yy = 1240 + int(C.lerp(16, 0, punch))
                C.rounded(d, (120, yy, 960, yy + 180), 28, C.mix(C.BG, (42, 24, 22), punch))
                d.text((C.W // 2, yy + 90), "被找茬的人下次少讲", font=C.font(40), fill=C.mix(C.BG, C.YELLOW, punch), anchor="mm")
        yield img


def render_b_gate(duration: float):
    n = max(1, round(duration * C.FPS))
    third = duration / 3.0
    rows = [
        ("拦不拦过", "先问这一条", C.YELLOW),
        ("必须改", "拦过的才写", C.MINT),
        ("可选", "口味不绑风险", C.MUTED),
    ]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "做法 · 拦不拦过")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 230 + int(C.lerp(16, 0, a0))), "先问拦不拦过", font=C.font(50), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        if t < third:
            a = C.appear(t, 0.14)
            if a > 0.04:
                y = 380 + int(C.lerp(18, 0, a))
                C.rounded(d, (110, y, 970, y + 520), 36, C.mix(C.BG, C.CARD, a))
                d.text((C.W // 2, y + 160), "这一条", font=C.font(36), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
                d.text((C.W // 2, y + 300), "拦不拦过", font=C.font(68), fill=C.mix(C.CARD, C.YELLOW, a), anchor="mm")
        elif t < third * 2:
            a = C.appear(t, third, 0.22)
            y = 360 + int(C.lerp(16, 0, a))
            C.rounded(d, (110, y, 970, y + 420), 36, C.mix(C.BG, (18, 42, 36), a))
            d.text((C.W // 2, y + 140), "拦过的", font=C.font(36), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            d.text((C.W // 2, y + 260), "写成必须改", font=C.font(64), fill=C.mix(C.CARD, C.MINT, a), anchor="mm")
            C.check_badge(d, C.W // 2, y + 360, C.appear(t, third + 0.55, 0.20))
        else:
            a = C.appear(t, third * 2, 0.22)
            for idx, (head, body, col) in enumerate(rows):
                aa = C.appear(t, third * 2 + idx * 0.10, 0.18)
                if aa < 0.04:
                    continue
                y = 340 + idx * 230 + int(C.lerp(16, 0, aa))
                C.rounded(d, (100, y, 980, y + 200), 28, C.mix(C.BG, C.CARD, aa))
                d.text((200, y + 100), head, font=C.font(44), fill=C.mix(C.CARD, col, aa), anchor="lm")
                d.text((780, y + 100), body, font=C.font(32), fill=C.mix(C.CARD, C.WHITE, aa), anchor="rm")
            punch = C.appear(t, third * 2 + 0.70, 0.22)
            if punch > 0.04:
                y = 1080 + int(C.lerp(16, 0, punch))
                C.rounded(d, (120, y, 960, y + 180), 28, C.mix(C.BG, (18, 42, 36), punch))
                d.text((C.W // 2, y + 90), "口味不和风险绑在一起", font=C.font(38), fill=C.mix(C.BG, C.MINT, punch), anchor="mm")
        yield img


def render_b_three(duration: float):
    n = max(1, round(duration * C.FPS))
    third = duration / 3.0
    cards = [("一", "风险"), ("二", "口径"), ("三", "谁改")]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "收束 · 三条必须看")
        if t < third:
            a0 = C.appear(t, 0.02)
            d.text((C.W // 2, 236 + int(C.lerp(16, 0, a0))), "会前先写三条", font=C.font(50), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
            for idx, (num, label) in enumerate(cards):
                aa = C.appear(t, 0.16 + idx * 0.10, 0.18)
                if aa < 0.04:
                    continue
                x = 80 + idx * 320
                y = 380 + int(C.lerp(18, 0, aa))
                C.rounded(d, (x, y, x + 300, y + 420), 32, C.mix(C.BG, C.CARD, aa))
                d.text((x + 150, y + 120), num, font=C.font(56), fill=C.mix(C.CARD, C.YELLOW, aa), anchor="mm")
                d.text((x + 150, y + 250), label, font=C.font(48), fill=C.mix(C.CARD, C.WHITE, aa), anchor="mm")
        elif t < third * 2:
            a = C.appear(t, third, 0.22)
            d.text((C.W // 2, 240), "会上只打这三条", font=C.font(48), fill=C.mix(C.BG, C.WHITE, a), anchor="mm")
            C.rounded(d, (100, 360, 980, 780), 36, C.mix(C.BG, (18, 42, 36), a))
            d.text((C.W // 2, 500), "三条", font=C.font(72), fill=C.mix(C.CARD, C.MINT, a), anchor="mm")
            d.text((C.W // 2, 640), "其余会后纸条", font=C.font(40), fill=C.mix(C.CARD, C.WHITE, a), anchor="mm")
            extra = C.appear(t, third + 0.55, 0.22)
            if extra > 0.04:
                y = 860 + int(C.lerp(16, 0, extra))
                C.rounded(d, (160, y, 920, y + 200), 28, C.mix(C.BG, C.CARD, extra))
                d.text((C.W // 2, y + 100), "口味会后再说", font=C.font(40), fill=C.mix(C.CARD, C.MUTED, extra), anchor="mm")
                C.strike_line(d, (220, y + 40, 860, y + 160), C.appear(t, third + 0.85, 0.28), C.mix(C.CARD, C.RED, extra))
        else:
            a = C.appear(t, third * 2, 0.22)
            d.text((C.W // 2, 240), "散会只带走", font=C.font(48), fill=C.mix(C.BG, C.WHITE, a), anchor="mm")
            C.rounded(d, (80, 360, 500, 980), 32, C.mix(C.BG, (18, 42, 36), a))
            C.rounded(d, (580, 360, 1000, 980), 32, C.mix(C.BG, C.CARD, a))
            d.text((290, 520), "必须改", font=C.font(52), fill=C.mix(C.CARD, C.MINT, a), anchor="mm")
            d.text((290, 680), "拦过的点", font=C.font(36), fill=C.mix(C.CARD, C.WHITE, a), anchor="mm")
            d.text((790, 520), "谁改", font=C.font(52), fill=C.mix(C.CARD, C.YELLOW, a), anchor="mm")
            d.text((790, 680), "写上名字", font=C.font(36), fill=C.mix(C.CARD, C.WHITE, a), anchor="mm")
            C.check_badge(d, 290, 820, C.appear(t, third * 2 + 0.45, 0.20))
            C.check_badge(d, 790, 820, C.appear(t, third * 2 + 0.60, 0.20))
            punch = C.appear(t, third * 2 + 0.80, 0.22)
            if punch > 0.04:
                y = 1100 + int(C.lerp(16, 0, punch))
                C.rounded(d, (120, y, 960, y + 180), 28, C.mix(C.BG, (18, 42, 36), punch))
                d.text((C.W // 2, y + 90), "只带走必须改和谁改", font=C.font(40), fill=C.mix(C.BG, C.MINT, punch), anchor="mm")
        yield img


def build_timeline(cues, duration: float) -> dict:
    if len(cues) != 16:
        raise SystemExit(f"need 16 phrases, got {len(cues)}")
    p = cues
    b1 = max(p[1][1] + 0.06, p[2][0] - C.LEAD)
    b4 = max(p[4][1] + 0.06, p[5][0] - C.LEAD)
    shots = [
        {"id": "S01a", "kind": "A", "start": 0.0, "end": p[0][1], "src": "assets/V-挥手.mp4", "line": p[0][2], "close": True},
        {"id": "S01b", "kind": "A", "start": p[0][1], "end": b1, "src": "assets/V-摊手.mp4", "line": p[1][2]},
        {"id": "S02", "kind": "B", "start": b1, "end": p[2][1], "src": "broll/B-抠标点.mp4", "line": p[2][2], "broll": "nitpick"},
        {"id": "S03", "kind": "B", "start": p[2][1], "end": p[3][1], "src": "broll/B-十条口味.mp4", "line": p[3][2], "broll": "taste"},
        {"id": "S04", "kind": "A", "start": p[3][1], "end": b4, "src": "assets/V-指向.mp4", "line": p[4][2]},
        {"id": "S05", "kind": "B", "start": b4, "end": p[6][1], "src": "broll/B-藏进抽屉.mp4", "line": p[6][2], "broll": "drawer"},
        {"id": "S06", "kind": "A", "start": p[6][1], "end": p[7][1], "src": "assets/V-指向.mp4", "line": p[7][2]},
        {"id": "S07", "kind": "B", "start": p[7][1], "end": p[10][1], "src": "broll/B-拦过必须改.mp4", "line": p[10][2], "broll": "gate"},
        {"id": "S08", "kind": "A", "start": p[10][1], "end": p[11][1], "src": "assets/V-正对讲.mp4", "line": p[11][2]},
        {"id": "S09", "kind": "B", "start": p[11][1], "end": p[14][1], "src": "broll/B-三条必须看.mp4", "line": p[14][2], "broll": "three"},
        {"id": "S10", "kind": "A", "start": p[14][1], "end": duration, "src": "assets/V-点赞.mp4", "line": p[15][2]},
    ]
    shots = C.close_shots(shots, duration)
    a_caps = [
        {"start": 0.0, "end": shots[0]["end"], "lines": ["大家好"]},
        {"start": shots[1]["start"], "end": shots[1]["end"], "lines": ["评审变成找茬会"]},
        {"start": shots[4]["start"], "end": shots[4]["end"], "lines": ["评审忘了", "自己在审什么"]},
        {"start": shots[6]["start"], "end": shots[6]["end"], "lines": ["盯风险", "不盯口味"]},
        {"start": shots[8]["start"], "end": shots[8]["end"], "lines": ["找茬按住人", "评审把路铺开"]},
        {"start": shots[10]["start"], "end": duration, "lines": ["要能过", "不要找茬会"]},
    ]
    shutters = [
        {"start": shots[1]["start"], "color": list(C.CREAM)},
        {"start": shots[2]["start"], "color": list(C.MINT)},
        {"start": shots[3]["start"], "color": list(C.YELLOW)},
        {"start": shots[4]["start"], "color": list(C.CREAM)},
        {"start": shots[5]["start"], "color": list(C.MINT)},
        {"start": shots[6]["start"], "color": list(C.CREAM)},
        {"start": shots[7]["start"], "color": list(C.MINT)},
        {"start": shots[8]["start"], "color": list(C.CREAM)},
        {"start": shots[9]["start"], "color": list(C.YELLOW)},
        {"start": shots[10]["start"], "color": list(C.MINT)},
    ]
    eyebrows = [
        {"start": shots[0]["start"], "end": shots[0]["end"], "text": "A-ROLL / 1a"},
        {"start": shots[1]["start"], "end": shots[1]["end"], "text": "A-ROLL / 1b"},
        {"start": shots[4]["start"], "end": shots[4]["end"], "text": "A-ROLL / 04"},
        {"start": shots[6]["start"], "end": shots[6]["end"], "text": "A-ROLL / 06"},
        {"start": shots[8]["start"], "end": shots[8]["end"], "text": "A-ROLL / 08"},
        {"start": shots[10]["start"], "end": shots[10]["end"], "text": "A-ROLL / 10"},
    ]
    recipe = {
        "title": NAME,
        "cover_title": "评审变成找茬会",
        "cover_sub": "该盯风险，不该盯口味",
        "cover_line": "拦过的才必须改",
        "cover_src": "assets/A-角色-小灯-摊手.jpg",
    }
    (ROOT / "plan").mkdir(exist_ok=True)
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
        "factory": "68_评审变成找茬会",
        "topic": 68,
        "source_note": "工厂 68_评审变成找茬会 / 云端 NEW",
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
    d.text((C.W // 2, 160), "评审变成找茬会", font=C.font(52), fill=C.WHITE, anchor="mm")
    d.text((C.W // 2, 250), "盯风险，不盯口味", font=C.font(56), fill=C.YELLOW, anchor="mm")
    d.text((C.W // 2, 340), "拦过的才必须改", font=C.font(36), fill=C.MINT, anchor="mm")
    d.text((C.W // 2, 410), "散会只带走必须改和谁改", font=C.font(30), fill=C.MUTED, anchor="mm")
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
    C.copy_named_assets(ROOT / "assets", mapping)
    duration, cues = C.make_voiceover(ROOT, PHRASES)
    print("VO", duration, C.zh_seconds(duration))
    if not (C.TARGET_MIN - 0.2 <= duration <= C.TARGET_MAX + 0.2):
        raise SystemExit(f"VO {duration:.2f}s ({C.zh_seconds(duration)}) outside 四十到五十秒")
    for row in cues:
        print(f"  {row[0]:6.3f}-{row[1]:6.3f}  {row[2]}")
    data = build_timeline(cues, duration)
    print("timeline", [(s["id"], s["start"], s["end"], s["kind"]) for s in data["shots"]])
    bmap = {s["id"]: s for s in data["shots"]}
    C.frames_to_mp4(render_b_nitpick(max(2.4, bmap["S02"]["end"] - bmap["S02"]["start"]) + 0.12), ROOT / "broll" / "B-抠标点.mp4")
    C.frames_to_mp4(render_b_taste(max(2.4, bmap["S03"]["end"] - bmap["S03"]["start"]) + 0.12), ROOT / "broll" / "B-十条口味.mp4")
    C.frames_to_mp4(render_b_drawer(max(2.6, bmap["S05"]["end"] - bmap["S05"]["start"]) + 0.12), ROOT / "broll" / "B-藏进抽屉.mp4")
    C.frames_to_mp4(render_b_gate(max(2.8, bmap["S07"]["end"] - bmap["S07"]["start"]) + 0.12), ROOT / "broll" / "B-拦过必须改.mp4")
    C.frames_to_mp4(render_b_three(max(2.8, bmap["S09"]["end"] - bmap["S09"]["start"]) + 0.12), ROOT / "broll" / "B-三条必须看.mp4")
    make_cover()
    staged = C.assemble(ROOT, data, NAME, STAGED_NAME)
    dur = C.probe_dur(staged)
    C.write_docs(
        ROOT,
        episode=68,
        name=NAME,
        staged_name=STAGED_NAME,
        duration=dur,
        data=data,
        source_note="工厂 68_评审变成找茬会 / 云端 NEW",
        note_body="钩子：评审变成找茬会。后果：抠标点、十条口味按住能过的方案、只证明谁更细、问题藏进抽屉。做法：先问拦不拦过，拦过写成必须改，口味写成可选。收束：会前三条必须看，散会只带走必须改和谁改。评审要能过，不要变成找茬会。",
    )
    C.patch_index(STAGED_NAME, dur)
    report = C.qa(ROOT, staged, data, "68_评审变成找茬会")
    print("STAGED", staged, "dur", dur, C.zh_seconds(dur), "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
