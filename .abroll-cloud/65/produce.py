#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 65：口头同步当过结论。工厂 65_口头同步当过结论。加长到四十到五十秒。"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import longform_common as C  # noqa: E402

NAME = "口头同步当过结论"
STAGED_NAME = "65-口头同步当过结论.mp4"
ASSET_06 = Path("/workspace/.abroll-cloud/06/assets")
ASSET_25 = Path("/workspace/.abroll-cloud/25/assets")
PHRASES = [
    "大家好",
    "口头同步，被当成过结论",
    "走廊对过一句，群里回了个好",
    "这不叫定了，这叫说过",
    "说过的话，每人记住的版本不一样",
    "你以为拍了板，他以为只是聊聊",
    "第二天各做各的，才发现根本没定过",
    "口头同步最容易空的，不是话少，是没留下字",
    "同步完立刻写下三行",
    "谁同意，定了什么，没定什么",
    "写完发出去，让对方能改",
    "对方没回，就不算对齐",
    "没写成字，就不算结论",
    "别把口头同步，直接写进待办",
    "先留下字，再当结论",
]
SOURCE_NOTE = "工厂 65_口头同步当过结论 / Drive 短切 15.6秒 / 成片未进"


def render_b_spoken(duration: float):
    n = max(1, round(duration * C.FPS))
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "错 · 说过当定了")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 230 + int(C.lerp(16, 0, a0))), "走廊对过一句", font=C.font(40), fill=C.mix(C.BG, C.MUTED, a0), anchor="mm")
        d.text((C.W // 2, 300 + int(C.lerp(16, 0, a0))), "群里回了个好", font=C.font(50), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        a1 = C.appear(t, 0.18)
        if a1 > 0.04:
            y = 380 + int(C.lerp(18, 0, a1))
            C.rounded(d, (70, y, 510, y + 520), 32, C.mix(C.BG, (42, 24, 22), a1))
            d.text((290, y + 90), "错", font=C.font(30), fill=C.mix(C.CARD, C.MUTED, a1), anchor="mm")
            d.text((290, y + 220), "定了", font=C.font(72), fill=C.mix(C.CARD, C.RED, a1), anchor="mm")
            d.text((290, y + 340), "写进待办", font=C.font(36), fill=C.mix(C.CARD, C.WHITE, a1), anchor="mm")
            C.draw_x(d, 290, y + 430, C.appear(t, 0.88, 0.20), 32)
        a2 = C.appear(t, 0.30)
        if a2 > 0.04:
            y = 380 + int(C.lerp(18, 0, a2))
            C.rounded(d, (570, y, 1010, y + 520), 32, C.mix(C.BG, (18, 42, 36), a2))
            d.text((790, y + 90), "对", font=C.font(30), fill=C.mix(C.CARD, C.MUTED, a2), anchor="mm")
            d.text((790, y + 220), "说过", font=C.font(72), fill=C.mix(C.CARD, C.MINT, a2), anchor="mm")
            d.text((790, y + 340), "还没落字", font=C.font(36), fill=C.mix(C.CARD, C.WHITE, a2), anchor="mm")
            C.check_badge(d, 790, y + 430, C.appear(t, 1.00, 0.20))
        punch = C.appear(t, max(1.35, duration * 0.55), 0.22)
        if punch > 0.04:
            y = 980 + int(C.lerp(16, 0, punch))
            C.rounded(d, (120, y, 960, y + 180), 28, C.mix(C.BG, (42, 24, 22), punch))
            d.text((C.W // 2, y + 90), "这不叫定了，这叫说过", font=C.font(40), fill=C.mix(C.BG, C.YELLOW, punch), anchor="mm")
        yield img


def render_b_versions(duration: float):
    n = max(1, round(duration * C.FPS))
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "对照 · 两个版本")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 236 + int(C.lerp(16, 0, a0))), "每人记住的不一样", font=C.font(50), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        a1 = C.appear(t, 0.16)
        if a1 > 0.04:
            y = 340 + int(C.lerp(18, 0, a1))
            C.rounded(d, (70, y, 510, y + 560), 32, C.mix(C.BG, C.CARD, a1))
            d.text((290, y + 90), "你的版本", font=C.font(30), fill=C.mix(C.CARD, C.MUTED, a1), anchor="mm")
            d.text((290, y + 230), "拍了板", font=C.font(64), fill=C.mix(C.CARD, C.YELLOW, a1), anchor="mm")
            d.text((290, y + 360), "可以开工", font=C.font(36), fill=C.mix(C.CARD, C.WHITE, a1), anchor="mm")
        a2 = C.appear(t, 0.30)
        if a2 > 0.04:
            y = 340 + int(C.lerp(18, 0, a2))
            C.rounded(d, (570, y, 1010, y + 560), 32, C.mix(C.BG, C.CARD, a2))
            d.text((790, y + 90), "他的版本", font=C.font(30), fill=C.mix(C.CARD, C.MUTED, a2), anchor="mm")
            d.text((790, y + 230), "只是聊聊", font=C.font(64), fill=C.mix(C.CARD, C.RED, a2), anchor="mm")
            d.text((790, y + 360), "还没拍板", font=C.font(36), fill=C.mix(C.CARD, C.WHITE, a2), anchor="mm")
        punch = C.appear(t, max(1.20, duration * 0.52), 0.22)
        if punch > 0.04:
            y = 980 + int(C.lerp(16, 0, punch))
            C.rounded(d, (140, y, 940, y + 180), 28, C.mix(C.BG, (42, 32, 16), punch))
            d.text((C.W // 2, y + 90), "同一句口头同步", font=C.font(42), fill=C.mix(C.BG, C.YELLOW, punch), anchor="mm")
        yield img


def render_b_fork(duration: float):
    n = max(1, round(duration * C.FPS))
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "后果 · 第二天分叉")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 236 + int(C.lerp(16, 0, a0))), "各做各的", font=C.font(56), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        items = [("你", "按拍板去做"), ("他", "还在等确认")]
        for idx, (who, act) in enumerate(items):
            aa = C.appear(t, 0.20 + idx * 0.16, 0.20)
            if aa < 0.04:
                continue
            x = 80 + idx * 480
            y = 360 + int(C.lerp(20, 0, aa))
            C.rounded(d, (x, y, x + 440, y + 520), 32, C.mix(C.BG, C.CARD, aa))
            d.text((x + 220, y + 100), who, font=C.font(32), fill=C.mix(C.CARD, C.MUTED, aa), anchor="mm")
            d.text((x + 220, y + 250), act, font=C.font(44), fill=C.mix(C.CARD, C.WHITE, aa), anchor="mm")
            C.draw_x(d, x + 220, y + 400, C.appear(t, 1.05 + idx * 0.08, 0.18), 30)
        punch = C.appear(t, max(1.40, duration * 0.58), 0.22)
        if punch > 0.04:
            y = 980 + int(C.lerp(16, 0, punch))
            C.rounded(d, (120, y, 960, y + 180), 28, C.mix(C.BG, (42, 24, 22), punch))
            d.text((C.W // 2, y + 90), "才发现根本没定过", font=C.font(42), fill=C.mix(C.BG, C.RED, punch), anchor="mm")
        yield img


def render_b_blank(duration: float):
    n = max(1, round(duration * C.FPS))
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "空 · 没留下字")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 240 + int(C.lerp(16, 0, a0))), "不是话少", font=C.font(40), fill=C.mix(C.BG, C.MUTED, a0), anchor="mm")
        d.text((C.W // 2, 310 + int(C.lerp(16, 0, a0))), "是没留下字", font=C.font(56), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        a1 = C.appear(t, 0.20)
        if a1 > 0.04:
            y = 400 + int(C.lerp(20, 0, a1))
            C.rounded(d, (120, y, 960, y + 520), 36, C.mix(C.BG, C.CARD, a1))
            d.text((C.W // 2, y + 140), "口头同步", font=C.font(40), fill=C.mix(C.CARD, C.MUTED, a1), anchor="mm")
            d.text((C.W // 2, y + 270), "纸上空白", font=C.font(72), fill=C.mix(C.CARD, C.YELLOW, a1), anchor="mm")
            C.strike_line(d, (220, y + 230, 860, y + 310), C.appear(t, 0.90, 0.28), C.mix(C.CARD, C.RED, a1))
        punch = C.appear(t, 1.25, 0.22)
        if punch > 0.04:
            y = 1000 + int(C.lerp(16, 0, punch))
            C.rounded(d, (140, y, 940, y + 180), 28, C.mix(C.BG, (18, 42, 36), punch))
            d.text((C.W // 2, y + 90), "没字就没有结论", font=C.font(42), fill=C.mix(C.BG, C.MINT, punch), anchor="mm")
        yield img


def render_b_three(duration: float):
    n = max(1, round(duration * C.FPS))
    rows = [
        ("1", "谁同意", "名字写上"),
        ("2", "定了什么", "一句能执行"),
        ("3", "没定什么", "空白也写清"),
    ]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "做 · 立刻三行")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 230 + int(C.lerp(16, 0, a0))), "同步完立刻写下", font=C.font(48), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        third = duration / 3.0
        if t < third * 2.15:
            for idx, (num, head, body) in enumerate(rows):
                aa = C.appear(t, 0.16 + idx * 0.14, 0.18)
                if aa < 0.04:
                    continue
                y = 320 + idx * 200
                C.rounded(d, (90, y, 990, y + 176), 28, C.mix(C.BG, C.CARD, aa))
                d.text((180, y + 88), num, font=C.font(52), fill=C.mix(C.CARD, C.MINT, aa), anchor="mm")
                d.text((520, y + 58), head, font=C.font(44), fill=C.mix(C.CARD, C.WHITE, aa), anchor="mm")
                d.text((520, y + 122), body, font=C.font(32), fill=C.mix(C.CARD, C.MUTED, aa), anchor="mm")
        else:
            aa = C.appear(t, third * 2.15, 0.22)
            C.rounded(d, (90, 340, 990, 980), 36, C.mix(C.BG, C.CARD, aa))
            d.text((C.W // 2, 460), "写完发出去", font=C.font(36), fill=C.mix(C.CARD, C.MUTED, aa), anchor="mm")
            d.text((C.W // 2, 580), "对方没回", font=C.font(52), fill=C.mix(C.CARD, C.YELLOW, aa), anchor="mm")
            d.text((C.W // 2, 700), "就不算对齐", font=C.font(52), fill=C.mix(C.CARD, C.WHITE, aa), anchor="mm")
            d.text((C.W // 2, 840), "没写成字，就不算结论", font=C.font(36), fill=C.mix(C.CARD, C.MINT, aa), anchor="mm")
        punch = C.appear(t, max(duration * 0.78, 2.2), 0.20)
        if punch > 0.04:
            y = 1080 + int(C.lerp(16, 0, punch))
            C.rounded(d, (140, y, 940, y + 160), 28, C.mix(C.BG, (18, 42, 36), punch))
            d.text((C.W // 2, y + 80), "先留下字，再当结论", font=C.font(40), fill=C.mix(C.BG, C.MINT, punch), anchor="mm")
        yield img


def build_timeline(cues, duration: float) -> dict:
    if len(cues) != 15:
        raise SystemExit(f"need 15 phrases, got {len(cues)}")
    p = cues
    b1 = max(p[1][1] + 0.06, p[2][0] - C.LEAD)
    b1e = p[3][1]
    a3 = p[3][1]
    b2 = max(p[4][1] + 0.06, p[5][0] - C.LEAD)
    b2e = p[5][1]
    b3 = p[6][0]
    b3e = p[6][1]
    b4 = p[7][0]
    b4e = p[7][1]
    a7 = p[7][1]
    b8 = max(p[8][1] + 0.06, p[9][0] - C.LEAD)
    b8e = p[13][1]
    shots = [
        {"id": "S01a", "kind": "A", "start": 0.0, "end": p[0][1], "src": "assets/V-挥手.mp4", "line": p[0][2], "close": True},
        {"id": "S01b", "kind": "A", "start": p[0][1], "end": b1, "src": "assets/V-正对讲.mp4", "line": p[1][2]},
        {"id": "S02", "kind": "B", "start": b1, "end": b1e, "src": "broll/B-说过不当定了.mp4", "line": p[3][2], "broll": "spoken"},
        {"id": "S03", "kind": "A", "start": a3, "end": b2, "src": "assets/V-指向.mp4", "line": p[4][2]},
        {"id": "S04", "kind": "B", "start": b2, "end": b2e, "src": "broll/B-两个版本.mp4", "line": p[5][2], "broll": "versions"},
        {"id": "S05", "kind": "B", "start": b3, "end": b3e, "src": "broll/B-第二天分叉.mp4", "line": p[6][2], "broll": "fork"},
        {"id": "S06", "kind": "B", "start": b4, "end": b4e, "src": "broll/B-没留下字.mp4", "line": p[7][2], "broll": "blank"},
        {"id": "S07", "kind": "A", "start": a7, "end": b8, "src": "assets/V-摊手.mp4", "line": p[8][2]},
        {"id": "S08", "kind": "B", "start": b8, "end": b8e, "src": "broll/B-立刻三行.mp4", "line": p[12][2], "broll": "three"},
        {"id": "S09", "kind": "A", "start": b8e, "end": duration, "src": "assets/V-点赞.mp4", "line": p[14][2]},
    ]
    shots = C.close_shots(shots, duration)
    a_caps = [
        {"start": 0.0, "end": shots[0]["end"], "lines": ["大家好"]},
        {"start": shots[1]["start"], "end": shots[1]["end"], "lines": ["口头同步", "被当成过结论"]},
        {"start": shots[3]["start"], "end": shots[3]["end"], "lines": C.split_caption(p[4][2])},
        {"start": shots[7]["start"], "end": shots[7]["end"], "lines": ["立刻写下三行"]},
        {"start": shots[9]["start"], "end": duration, "lines": ["先留下字", "再当结论"]},
    ]
    shutters = [
        {"start": shots[1]["start"], "color": list(C.CREAM)},
        {"start": shots[2]["start"], "color": list(C.MINT)},
        {"start": shots[3]["start"], "color": list(C.CREAM)},
        {"start": shots[4]["start"], "color": list(C.YELLOW)},
        {"start": shots[5]["start"], "color": list(C.RED)},
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
        "cover_title": "口头同步",
        "cover_sub": "当过结论",
        "cover_line": "说过 · 不是定了",
        "cover_src": "assets/A-角色-小灯-指向.jpg",
        "video_type": "普通短视频",
        "topic_id": "65",
        "source": SOURCE_NOTE,
        "note": "知识口播。不是剧情短剧。只打说过不是定了。",
    }
    (ROOT / "plan").mkdir(exist_ok=True)
    (ROOT / "plan" / "shot_recipe.json").write_text(json.dumps(recipe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "plan" / "broll.json").write_text(
        json.dumps(
            [
                {"id": "spoken", "file": "broll/B-说过不当定了.mp4", "punch": "这叫说过"},
                {"id": "versions", "file": "broll/B-两个版本.mp4", "punch": "每人一个版本"},
                {"id": "fork", "file": "broll/B-第二天分叉.mp4", "punch": "根本没定过"},
                {"id": "blank", "file": "broll/B-没留下字.mp4", "punch": "没字没有结论"},
                {"id": "three", "file": "broll/B-立刻三行.mp4", "punch": "先留下字"},
            ],
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
        "factory": "65_口头同步当过结论",
        "topic": 65,
        "source_note": SOURCE_NOTE,
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
    d.text((C.W // 2, 160), "口头同步", font=C.font(52), fill=C.WHITE, anchor="mm")
    d.text((C.W // 2, 250), "当过结论", font=C.font(64), fill=C.YELLOW, anchor="mm")
    d.text((C.W // 2, 340), "说过 · 不是定了", font=C.font(36), fill=C.MINT, anchor="mm")
    d.text((C.W // 2, 410), "先留下字，再当结论", font=C.font(30), fill=C.MUTED, anchor="mm")
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
            shutil.copy2(src, point)
        else:
            shutil.copy2(ROOT / "assets" / "A-角色-小灯-摊手.jpg", point)
    duration, cues = C.make_voiceover(ROOT, PHRASES)
    print("VO", duration, C.zh_seconds(duration))
    for row in cues:
        print(f"  {row[0]:6.3f}-{row[1]:6.3f}  {row[2]}")
    data = build_timeline(cues, duration)
    print("timeline", [(s["id"], s["start"], s["end"], s["kind"]) for s in data["shots"]])
    bmap = {s["id"]: s for s in data["shots"]}
    C.frames_to_mp4(render_b_spoken(max(2.4, bmap["S02"]["end"] - bmap["S02"]["start"]) + 0.16), ROOT / "broll" / "B-说过不当定了.mp4")
    C.frames_to_mp4(render_b_versions(max(2.4, bmap["S04"]["end"] - bmap["S04"]["start"]) + 0.16), ROOT / "broll" / "B-两个版本.mp4")
    C.frames_to_mp4(render_b_fork(max(2.4, bmap["S05"]["end"] - bmap["S05"]["start"]) + 0.16), ROOT / "broll" / "B-第二天分叉.mp4")
    C.frames_to_mp4(render_b_blank(max(2.4, bmap["S06"]["end"] - bmap["S06"]["start"]) + 0.16), ROOT / "broll" / "B-没留下字.mp4")
    C.frames_to_mp4(render_b_three(max(2.4, bmap["S08"]["end"] - bmap["S08"]["start"]) + 0.16), ROOT / "broll" / "B-立刻三行.mp4")
    make_cover()
    staged = C.assemble(ROOT, data, NAME, STAGED_NAME)
    dur = C.probe_dur(staged)
    C.write_docs(
        ROOT,
        episode=65,
        name=NAME,
        staged_name=STAGED_NAME,
        duration=dur,
        data=data,
        source_note=SOURCE_NOTE,
        note_body="钩子：口头同步被当成过结论。对照：说过不是定了，每人一个版本。后果：第二天各做各的。做法：写下谁同意、定了什么、没定什么，发出去；对方没回就不算对齐。收束：没写成字就不算结论，先留下字再当结论。",
    )
    C.patch_index(STAGED_NAME, dur)
    dur_md = f"""# 成片 65 时长（中文秒）

云端 only。NEW 成片。无冻帧垫时长。目标四十到五十秒，硬窗口三十到六十秒。

| 号 | 成片 | 工厂短切 | 新时长 | 草稿 |
|----|------|----------|--------|------|
| 65 | `65-口头同步当过结论.mp4` | 十五秒 | {dur:.1f}秒（{C.zh_seconds(dur)}） | `.abroll-cloud/65/` |

规格：1080×1920，24 fps，H.264 + AAC 44100 stereo。十镜 / 十五句。禁止 `tpad=stop_mode=clone` 注水。已覆盖工厂短切。
"""
    (ROOT / "时长.md").write_text(dur_md, encoding="utf-8")
    (ROOT.parent / "65-DURATION.md").write_text(dur_md, encoding="utf-8")
    report = C.qa(ROOT, staged, data, "65_口头同步当过结论")
    print("STAGED", staged, "dur", dur, C.zh_seconds(dur), "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
