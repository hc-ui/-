#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 75：嵌套字典。topics-batch4 #75。本集 NEW。

普通短视频 / 知识口播。草稿只写 .abroll-cloud/75/，成品中转 成片/75-嵌套字典.mp4。
目标四十到五十秒。A 镜短则往返循环，不定格、不慢放注水。
禁止 C:\\ D:\\ G:\\，禁止 Drive 上传，不走 drama-pipeline。
只打嵌套，不重复成片 13 / 42 / 64。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import longform_common as C  # noqa: E402

NAME = "嵌套字典"
STAGED_NAME = "75-嵌套字典.mp4"
ASSET_06 = Path("/workspace/.abroll-cloud/06/assets")
ASSET_25 = Path("/workspace/.abroll-cloud/25/assets")
PHRASES = [
    "大家好",
    "成绩册看起来像一张表，其实是两层抽屉",
    "一层抽屉硬塞两层标签，门就关不上",
    "左边写名字当钥匙，右边再塞一本小字典",
    "只开一层，拿到的是整本小册子，不是那个数",
    "名字是第一层，科目才是第二层",
    "名字指向科目，科目指向分数",
    "要拿分数，得先开名字，再开科目",
    "库存也一样，名字在外，库存在里",
    "两层中括号，才能取到里面的字段",
    "别把里面那一整层，当成一个值来用",
    "外层只认名字，里层才认科目和库存",
    "对照只打这一点：两层走，一层走不通",
    "写字典之前，先数它有几层",
    "两层就两层走，别当一层用",
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


def render_b_jam(duration: float):
    n = max(1, round(duration * C.FPS))
    labels = [("名字", "林"), ("科目", "语文"), ("库存", "十二")]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "错 · 一层硬塞")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 230 + int(C.lerp(16, 0, a0))), "一层抽屉", font=C.font(50), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        d.text((C.W // 2, 300 + int(C.lerp(16, 0, a0))), "硬塞两层标签", font=C.font(46), fill=C.mix(C.BG, C.YELLOW, a0), anchor="mm")
        a1 = C.appear(t, 0.18)
        if a1 > 0.04:
            y = 360 + int(C.lerp(18, 0, a1))
            C.rounded(d, (110, y, 970, y + 520), 32, C.mix(C.BG, C.CARD, a1))
            d.text((C.W // 2, y + 70), "只开一扇门", font=C.font(32), fill=C.mix(C.CARD, C.MUTED, a1), anchor="mm")
            for idx, (kind, val) in enumerate(labels):
                aa = C.appear(t, 0.40 + idx * 0.12, 0.18)
                if aa < 0.04:
                    continue
                x = 160 + idx * 250
                yy = y + 160 + int(C.lerp(14, 0, aa))
                C.rounded(d, (x, yy, x + 220, yy + 220), 22, C.mix(C.CARD, (42, 24, 22), aa))
                d.text((x + 110, yy + 70), kind, font=C.font(30), fill=C.mix(C.CARD, C.MUTED, aa), anchor="mm")
                d.text((x + 110, yy + 140), val, font=C.font(44), fill=C.mix(C.CARD, C.WHITE, aa), anchor="mm")
            C.draw_x(d, C.W // 2, y + 430, C.appear(t, 1.10, 0.22), 40)
        punch = C.appear(t, max(1.50, duration * 0.58), 0.22)
        if punch > 0.04:
            y = 1100 + int(C.lerp(16, 0, punch))
            C.rounded(d, (120, y, 960, y + 200), 28, C.mix(C.BG, (42, 24, 22), punch))
            d.text((C.W // 2, y + 100), "门关不上", font=C.font(52), fill=C.mix(C.BG, C.RED, punch), anchor="mm")
        yield img


def render_b_path(duration: float):
    n = max(1, round(duration * C.FPS))
    steps = [("名字", "林", 0.18), ("科目", "语文", 0.48), ("分数", "九十二", 0.78)]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "对 · 两层走")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 236 + int(C.lerp(16, 0, a0))), "名字指向科目", font=C.font(48), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        d.text((C.W // 2, 306 + int(C.lerp(16, 0, a0))), "科目指向分数", font=C.font(42), fill=C.mix(C.BG, C.MINT, a0), anchor="mm")
        for idx, (kind, val, ts) in enumerate(steps):
            aa = C.appear(t, ts, 0.20)
            if aa < 0.04:
                continue
            x = 90 + idx * 310
            y = 420 + int(C.lerp(18, 0, aa))
            C.rounded(d, (x, y, x + 280, y + 360), 28, C.mix(C.BG, C.CARD, aa))
            d.text((x + 140, y + 90), kind, font=C.font(32), fill=C.mix(C.CARD, C.MUTED, aa), anchor="mm")
            d.text((x + 140, y + 200), val, font=C.font(52), fill=C.mix(C.CARD, C.WHITE if idx < 2 else C.YELLOW, aa), anchor="mm")
            if idx < 2:
                arr = C.appear(t, ts + 0.22, 0.16)
                if arr > 0.04:
                    d.text((x + 300, y + 180), "→", font=C.font(48), fill=C.mix(C.BG, C.MINT, arr), anchor="mm")
        punch = C.appear(t, max(1.40, duration * 0.58), 0.22)
        if punch > 0.04:
            y = 1080 + int(C.lerp(16, 0, punch))
            C.rounded(d, (120, y, 960, y + 200), 28, C.mix(C.BG, (18, 42, 36), punch))
            d.text((C.W // 2, y + 100), "先开名字，再开科目", font=C.font(42), fill=C.mix(C.BG, C.MINT, punch), anchor="mm")
        yield img


def render_b_stock(duration: float):
    n = max(1, round(duration * C.FPS))
    cards = [("名字", "茶"), ("单价", "八"), ("库存", "十二")]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "对 · 库存也两层")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 236 + int(C.lerp(16, 0, a0))), "库存也一样", font=C.font(52), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        d.text((C.W // 2, 310 + int(C.lerp(16, 0, a0))), "名字在外，库存在里", font=C.font(40), fill=C.mix(C.BG, C.YELLOW, a0), anchor="mm")
        for idx, (kind, val) in enumerate(cards):
            aa = C.appear(t, 0.22 + idx * 0.16, 0.18)
            if aa < 0.04:
                continue
            x = 90 + idx * 310
            y = 420 + int(C.lerp(16, 0, aa))
            C.rounded(d, (x, y, x + 280, y + 320), 26, C.mix(C.BG, C.CARD, aa))
            d.text((x + 140, y + 90), kind, font=C.font(32), fill=C.mix(C.CARD, C.MUTED, aa), anchor="mm")
            d.text((x + 140, y + 190), val, font=C.font(56), fill=C.mix(C.CARD, C.MINT if idx == 0 else C.WHITE, aa), anchor="mm")
        C.check_badge(d, C.W // 2, 880, C.appear(t, 1.00, 0.22))
        punch = C.appear(t, max(1.30, duration * 0.55), 0.22)
        if punch > 0.04:
            y = 1080 + int(C.lerp(16, 0, punch))
            C.rounded(d, (120, y, 960, y + 180), 28, C.mix(C.BG, (18, 42, 36), punch))
            d.text((C.W // 2, y + 90), "外层名字，里层字段", font=C.font(42), fill=C.mix(C.BG, C.MINT, punch), anchor="mm")
        yield img


def render_b_brackets(duration: float):
    n = max(1, round(duration * C.FPS))
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "错 · 整层当值")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 230 + int(C.lerp(16, 0, a0))), "两层中括号", font=C.font(52), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        d.text((C.W // 2, 300 + int(C.lerp(16, 0, a0))), "才能取到里面的字段", font=C.font(38), fill=C.mix(C.BG, C.MUTED, a0), anchor="mm")
        a1 = C.appear(t, 0.20)
        if a1 > 0.04:
            y = 360 + int(C.lerp(16, 0, a1))
            C.rounded(d, (80, y, 500, y + 280), 26, C.mix(C.BG, C.CARD, a1))
            d.text((290, y + 80), "第一层", font=C.font(28), fill=C.mix(C.CARD, C.MUTED, a1), anchor="mm")
            d.text((290, y + 170), "[ 名字 ]", font=C.font(48), fill=C.mix(C.CARD, C.MINT, a1), anchor="mm")
            C.rounded(d, (580, y, 1000, y + 280), 26, C.mix(C.BG, C.CARD, a1))
            d.text((790, y + 80), "第二层", font=C.font(28), fill=C.mix(C.CARD, C.MUTED, a1), anchor="mm")
            d.text((790, y + 170), "[ 科目 ]", font=C.font(48), fill=C.mix(C.CARD, C.YELLOW, a1), anchor="mm")
        a2 = C.appear(t, 0.70)
        if a2 > 0.04:
            y = 700 + int(C.lerp(16, 0, a2))
            C.rounded(d, (110, y, 970, y + 280), 28, C.mix(C.BG, (42, 24, 22), a2))
            d.text((C.W // 2, y + 80), "把整层当成一个数", font=C.font(40), fill=C.mix(C.CARD, C.WHITE, a2), anchor="mm")
            d.text((C.W // 2, y + 170), "对不上", font=C.font(52), fill=C.mix(C.CARD, C.RED, a2), anchor="mm")
            C.strike_line(d, (180, y, 900, y + 280), C.appear(t, 1.00, 0.24), C.mix(C.CARD, C.RED, a2))
        punch = C.appear(t, max(1.45, duration * 0.60), 0.22)
        if punch > 0.04:
            y = 1100 + int(C.lerp(16, 0, punch))
            C.rounded(d, (120, y, 960, y + 180), 28, C.mix(C.BG, (42, 24, 22), punch))
            d.text((C.W // 2, y + 90), "整层不是一个值", font=C.font(44), fill=C.mix(C.BG, C.RED, punch), anchor="mm")
        yield img


def render_b_contrast(duration: float):
    n = max(1, round(duration * C.FPS))
    third = duration / 3.0
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "对照 · 一层 / 两层")
        if t < third:
            a = C.appear(t, 0.02)
            d.text((C.W // 2, 240 + int(C.lerp(16, 0, a))), "一层走不通", font=C.font(52), fill=C.mix(C.BG, C.WHITE, a), anchor="mm")
            C.rounded(d, (120, 360, 960, 980), 36, C.mix(C.BG, C.CARD, a))
            d.text((C.W // 2, 520), "只开一扇门", font=C.font(44), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            d.text((C.W // 2, 660), "拿到整本小册子", font=C.font(48), fill=C.mix(C.CARD, C.RED, a), anchor="mm")
            C.draw_x(d, C.W // 2, 820, C.appear(t, 0.70, 0.22), 40)
        elif t < third * 2:
            a = C.appear(t, third, 0.22)
            d.text((C.W // 2, 230), "一张对照", font=C.font(40), fill=C.mix(C.BG, C.MUTED, a), anchor="mm")
            d.text((C.W // 2, 300), "只打有几层", font=C.font(48), fill=C.mix(C.BG, C.WHITE, a), anchor="mm")
            C.rounded(d, (70, 380, 510, 1100), 32, C.mix(C.BG, (42, 24, 22), a))
            C.rounded(d, (570, 380, 1010, 1100), 32, C.mix(C.BG, (18, 42, 36), a))
            d.text((290, 500), "一层", font=C.font(32), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            d.text((290, 680), "走不通", font=C.font(56), fill=C.mix(C.CARD, C.RED, a), anchor="mm")
            C.draw_x(d, 290, 860, C.appear(t, third + 0.40, 0.20), 32)
            d.text((790, 500), "两层", font=C.font(32), fill=C.mix(C.CARD, C.MUTED, a), anchor="mm")
            d.text((790, 680), "走得通", font=C.font(56), fill=C.mix(C.CARD, C.MINT, a), anchor="mm")
            C.check_badge(d, 790, 860, C.appear(t, third + 0.55, 0.20))
        else:
            a = C.appear(t, third * 2, 0.22)
            d.text((C.W // 2, 240), "写字典之前", font=C.font(44), fill=C.mix(C.BG, C.MUTED, a), anchor="mm")
            d.text((C.W // 2, 320), "先数它有几层", font=C.font(52), fill=C.mix(C.BG, C.WHITE, a), anchor="mm")
            C.rounded(d, (120, 420, 960, 980), 36, C.mix(C.BG, C.CARD, a))
            d.text((C.W // 2, 560), "两层就两层走", font=C.font(48), fill=C.mix(C.CARD, C.MINT, a), anchor="mm")
            d.text((C.W // 2, 700), "别当一层用", font=C.font(52), fill=C.mix(C.CARD, C.YELLOW, a), anchor="mm")
            d.text((C.W // 2, 840), "外层名字，里层字段", font=C.font(36), fill=C.mix(C.CARD, C.WHITE, a), anchor="mm")
            punch = C.appear(t, third * 2 + 0.70, 0.22)
            if punch > 0.04:
                y = 1080 + int(C.lerp(16, 0, punch))
                C.rounded(d, (140, y, 940, y + 180), 28, C.mix(C.BG, (18, 42, 36), punch))
                d.text((C.W // 2, y + 90), "两层走", font=C.font(52), fill=C.mix(C.BG, C.MINT, punch), anchor="mm")
        yield img


def build_timeline(cues, duration: float) -> dict:
    if len(cues) != 15:
        raise SystemExit(f"need 15 phrases, got {len(cues)}")
    p = cues
    b1 = max(p[1][1] + 0.06, p[2][0] - C.LEAD)
    b1e = p[4][1]
    a3 = p[4][1]
    b2 = max(p[5][1] + 0.06, p[6][0] - C.LEAD)
    b2e = p[7][1]
    b3 = p[8][0]
    b3e = p[8][1]
    b4 = p[9][0]
    b4e = p[10][1]
    a7 = p[10][1]
    b8 = max(p[11][1] + 0.06, p[12][0] - C.LEAD)
    b8e = p[13][1]
    shots = [
        {"id": "S01a", "kind": "A", "start": 0.0, "end": p[0][1], "src": "assets/V-挥手.mp4", "line": p[0][2], "close": True},
        {"id": "S01b", "kind": "A", "start": p[0][1], "end": b1, "src": "assets/V-正对讲.mp4", "line": p[1][2]},
        {"id": "S02", "kind": "B", "start": b1, "end": b1e, "src": "broll/B-一层硬塞.mp4", "line": p[2][2], "broll": "jam"},
        {"id": "S03", "kind": "A", "start": a3, "end": b2, "src": "assets/V-指向.mp4", "line": p[5][2]},
        {"id": "S04", "kind": "B", "start": b2, "end": b2e, "src": "broll/B-两层走.mp4", "line": p[6][2], "broll": "path"},
        {"id": "S05", "kind": "B", "start": b3, "end": b3e, "src": "broll/B-库存两层.mp4", "line": p[8][2], "broll": "stock"},
        {"id": "S06", "kind": "B", "start": b4, "end": b4e, "src": "broll/B-整层当值.mp4", "line": p[10][2], "broll": "brackets"},
        {"id": "S07", "kind": "A", "start": a7, "end": b8, "src": "assets/V-摊手.mp4", "line": p[11][2]},
        {"id": "S08", "kind": "B", "start": b8, "end": b8e, "src": "broll/B-一层两层.mp4", "line": p[12][2], "broll": "contrast"},
        {"id": "S09", "kind": "A", "start": b8e, "end": duration, "src": "assets/V-点赞.mp4", "line": p[14][2]},
    ]
    shots = C.close_shots(shots, duration)
    a_caps = [
        {"start": 0.0, "end": shots[0]["end"], "lines": ["大家好"]},
        {"start": shots[1]["start"], "end": shots[1]["end"], "lines": ["成绩册像一张表", "其实是两层抽屉"]},
        {"start": shots[3]["start"], "end": shots[3]["end"], "lines": C.split_caption(p[5][2])},
        {"start": shots[7]["start"], "end": shots[7]["end"], "lines": C.split_caption(p[11][2])},
        {"start": shots[9]["start"], "end": duration, "lines": ["两层就两层走", "别当一层用"]},
    ]
    shutters = [
        {"start": shots[1]["start"], "color": list(C.CREAM)},
        {"start": shots[2]["start"], "color": list(C.RED)},
        {"start": shots[3]["start"], "color": list(C.CREAM)},
        {"start": shots[4]["start"], "color": list(C.MINT)},
        {"start": shots[5]["start"], "color": list(C.YELLOW)},
        {"start": shots[6]["start"], "color": list(C.RED)},
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
        "cover_title": "嵌套字典",
        "cover_sub": "别当一层用",
        "cover_line": "两层走 · 一层走不通",
        "cover_src": "assets/A-角色-小灯-指向.jpg",
    }
    (ROOT / "plan").mkdir(exist_ok=True)
    (ROOT / "plan" / "shot_recipe.json").write_text(json.dumps(recipe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "plan" / "broll.json").write_text(
        json.dumps(
            {
                "episode": 75,
                "cards": ["一层硬塞", "两层走", "库存两层", "整层当值", "一层两层"],
                "rule": "只打嵌套；不讲 append；不讲从值找键；不烧路径；不念文件名",
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
        "factory": "topics-batch4 #75 嵌套字典",
        "topic": 75,
        "source_note": "topics-batch4.md #75 / 学习基线 2026-09-09 不足第3条",
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
    d.text((C.W // 2, 160), "嵌套字典", font=C.font(56), fill=C.WHITE, anchor="mm")
    d.text((C.W // 2, 250), "别当一层用", font=C.font(58), fill=C.YELLOW, anchor="mm")
    d.text((C.W // 2, 340), "两层走 · 一层走不通", font=C.font(36), fill=C.MINT, anchor="mm")
    d.text((C.W // 2, 410), "名字 → 科目 → 分数", font=C.font(28), fill=C.MUTED, anchor="mm")
    dest = ROOT / f"00_封面_{NAME}.jpg"
    canvas.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    canvas.save(ROOT / "final" / "cover.jpg", quality=92)
    return dest


def patch_topics_batch4(duration: float) -> None:
    path = Path("/workspace/.abroll-cloud/topics-batch4.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    new = f"| 75 | 未完成 Python | `{STAGED_NAME}` | 已核验 {duration:.1f}秒（{C.zh_seconds(duration)}） |"
    lines = []
    hit = False
    for raw in text.splitlines():
        if raw.startswith("| 75 |"):
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
    text = path.read_text(encoding="utf-8")
    token = f"`成片/{STAGED_NAME}`"
    row = (
        f"| {token} | 1080×1920 h264+aac 44.1k stereo | "
        f"{duration:.2f}秒（{C.zh_seconds(duration)}） | "
        f"topic 75 `topics-batch4.md` 第 75 条；Drive 只读 `学习与职业规划基线.md` 2026-09-09 不足第 3 条。云端 NEW，不拷短切。 |"
    )
    plus = f"| 75 | `{STAGED_NAME}` | {duration:.1f}秒 | 已核验 |"
    lines = []
    seen_final = seen_plus = False
    for raw in text.splitlines():
        if raw.startswith("|") and token in raw:
            if not seen_final:
                lines.append(row)
                seen_final = True
            continue
        if raw.startswith("| 75 |") and "嵌套字典" in raw:
            if not seen_plus:
                lines.append(plus)
                seen_plus = True
            continue
        lines.append(raw)
    rebuilt = []
    for raw in lines:
        if (not seen_final) and "仙侠云海突进" in raw and raw.strip().startswith("|"):
            rebuilt.append(row)
            seen_final = True
        rebuilt.append(raw)
    if not seen_plus:
        out = []
        for raw in rebuilt:
            if raw.startswith("| 69 |") or raw.startswith("| 70 |"):
                out.append(raw)
                if not seen_plus:
                    out.append(plus)
                    seen_plus = True
                continue
            out.append(raw)
        rebuilt = out
    text = "\n".join(rebuilt)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


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
    C.frames_to_mp4(render_b_jam(max(2.6, bmap["S02"]["end"] - bmap["S02"]["start"]) + 0.16), ROOT / "broll" / "B-一层硬塞.mp4")
    C.frames_to_mp4(render_b_path(max(2.4, bmap["S04"]["end"] - bmap["S04"]["start"]) + 0.16), ROOT / "broll" / "B-两层走.mp4")
    C.frames_to_mp4(render_b_stock(max(2.4, bmap["S05"]["end"] - bmap["S05"]["start"]) + 0.16), ROOT / "broll" / "B-库存两层.mp4")
    C.frames_to_mp4(render_b_brackets(max(2.8, bmap["S06"]["end"] - bmap["S06"]["start"]) + 0.16), ROOT / "broll" / "B-整层当值.mp4")
    C.frames_to_mp4(render_b_contrast(max(2.6, bmap["S08"]["end"] - bmap["S08"]["start"]) + 0.16), ROOT / "broll" / "B-一层两层.mp4")
    make_cover()
    staged = C.assemble(ROOT, data, NAME, STAGED_NAME)
    dur = C.probe_dur(staged)
    C.write_docs(
        ROOT,
        episode=75,
        name=NAME,
        staged_name=STAGED_NAME,
        duration=dur,
        data=data,
        source_note="topics-batch4.md #75 / 学习基线 2026-09-09 不足第3条",
        note_body="钩子：成绩册看起来像一张表，其实是两层抽屉。做法：名字是第一层，科目或库存是第二层；两层中括号才取到里面的字段。对照：一层硬塞关不上，两层走才拿得到数。收束：写字典之前先数它有几层，两层就两层走，别当一层用。不讲 append，不讲从值找键，不拆函数。",
    )
    C.patch_index(STAGED_NAME, dur)
    patch_topics_batch4(dur)
    patch_delivery(dur)
    report = C.qa(ROOT, staged, data, "75_嵌套字典")
    print("STAGED", staged, "dur", dur, C.zh_seconds(dur), "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
