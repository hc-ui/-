#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 66：点头不等于确认。工厂 66_点头不等于确认。加长到四十到五十秒。云端 NEW。"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
import longform_common as C  # noqa: E402

NAME = "点头不等于确认"
STAGED_NAME = "66-点头不等于确认.mp4"
ASSET_06 = Path("/workspace/.abroll-cloud/06/assets")
ASSET_25 = Path("/workspace/.abroll-cloud/25/assets")
PHRASES = [
    "大家好",
    "会上人人点头，散会各走各的",
    "你以为对齐了，其实一句话都没确认",
    "点头不等于确认",
    "有人点头，是没听懂，不好意思问",
    "有人点头，是不想当场反驳",
    "还有人点头，只是想早点散会",
    "三种点头叠在一起，看起来像全体同意",
    "下周一对进度，才发现各想各的",
    "散会前要听到一句完整的话",
    "谁来做，做到哪，什么时候交",
    "听不到这句，就当没对齐",
    "别把礼貌当成拍板",
    "点头可以记气氛，不能记结论",
    "没写下的点头，只是礼貌",
]


def render_b_nodwall(duration: float):
    math = __import__("math")
    n = max(1, round(duration * C.FPS))
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "错 · 人人点头")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 230 + int(C.lerp(16, 0, a0))), "会上人人点头", font=C.font(50), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        d.text((C.W // 2, 300), "散会各走各的", font=C.font(40), fill=C.mix(C.BG, C.MUTED, a0), anchor="mm")
        cols = [(220, 520), (540, 500), (860, 520)]
        for idx, (cx, cy) in enumerate(cols):
            aa = C.appear(t, 0.18 + idx * 0.10, 0.20)
            if aa < 0.04:
                continue
            nod = int(14 * math.sin(t * 5.2 + idx * 1.3))
            y = cy + nod
            C.rounded(d, (cx - 140, y - 160, cx + 140, y + 220), 32, C.mix(C.BG, C.CARD, aa))
            d.ellipse((cx - 38, y - 110, cx + 38, y - 34), outline=C.mix(C.CARD, C.MINT, aa), width=6)
            d.arc((cx - 52, y - 28, cx + 52, y + 50), 200, 340, fill=C.mix(C.CARD, C.MINT, aa), width=6)
            d.text((cx, y + 120), "点头", font=C.font(36), fill=C.mix(C.CARD, C.WHITE, aa), anchor="mm")
        punch = C.appear(t, max(1.35, duration * 0.55), 0.22)
        if punch > 0.04:
            y = 1180 + int(C.lerp(16, 0, punch))
            C.rounded(d, (100, y, 980, y + 200), 28, C.mix(C.BG, (42, 24, 22), punch))
            d.text((C.W // 2, y + 100), "一句话都没确认", font=C.font(44), fill=C.mix(C.BG, C.YELLOW, punch), anchor="mm")
        yield img


def render_b_three(duration: float):
    n = max(1, round(duration * C.FPS))
    kinds = [
        ("没听懂", "不好意思问", 0.14),
        ("不反驳", "当场忍住", 0.36),
        ("想散会", "先点头再说", 0.58),
    ]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "点 · 三种点头")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 236 + int(C.lerp(16, 0, a0))), "点头不等于确认", font=C.font(52), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        for idx, (title, sub, ts) in enumerate(kinds):
            aa = C.appear(t, ts, 0.20)
            if aa < 0.04:
                continue
            y = 360 + idx * 280
            C.rounded(d, (90, y, 990, y + 250), 32, C.mix(C.BG, C.CARD, aa))
            d.text((160, y + 125), f"{idx + 1}", font=C.font(56), fill=C.mix(C.CARD, C.YELLOW, aa), anchor="mm")
            d.text((620, y + 90), title, font=C.font(52), fill=C.mix(C.CARD, C.WHITE, aa), anchor="mm")
            d.text((620, y + 170), sub, font=C.font(34), fill=C.mix(C.CARD, C.MUTED, aa), anchor="mm")
        yield img


def render_b_mismatch(duration: float):
    n = max(1, round(duration * C.FPS))
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "后果 · 各想各的")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 230 + int(C.lerp(16, 0, a0))), "看起来全体同意", font=C.font(48), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        split = max(1.20, duration * 0.40)
        if t < split:
            aa = C.appear(t, 0.16)
            C.rounded(d, (120, 360, 960, 980), 36, C.mix(C.BG, C.CARD, aa))
            d.text((C.W // 2, 560), "三种点头叠一起", font=C.font(48), fill=C.mix(C.CARD, C.WHITE, aa), anchor="mm")
            d.text((C.W // 2, 720), "像已经拍板", font=C.font(44), fill=C.mix(C.CARD, C.YELLOW, aa), anchor="mm")
        else:
            aa = C.appear(t, split, 0.22)
            C.rounded(d, (70, 360, 500, 1100), 32, C.mix(C.BG, (42, 24, 22), aa))
            C.rounded(d, (580, 360, 1010, 1100), 32, C.mix(C.BG, (22, 36, 48), aa))
            d.text((285, 460), "他以为", font=C.font(30), fill=C.mix(C.CARD, C.MUTED, aa), anchor="mm")
            d.text((285, 640), "下周再谈", font=C.font(44), fill=C.mix(C.CARD, C.RED, aa), anchor="mm")
            d.text((795, 460), "你以为", font=C.font(30), fill=C.mix(C.CARD, C.MUTED, aa), anchor="mm")
            d.text((795, 640), "已经定了", font=C.font(44), fill=C.mix(C.CARD, C.YELLOW, aa), anchor="mm")
            d.text((C.W // 2, 1220), "一对进度才露馅", font=C.font(40), fill=C.mix(C.BG, C.WHITE, aa), anchor="mm")
        yield img


def render_b_threeq(duration: float):
    n = max(1, round(duration * C.FPS))
    qs = [("谁来做", 0.14), ("做到哪", 0.32), ("什么时候交", 0.50)]
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "做法 · 一句完整的话")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 236 + int(C.lerp(16, 0, a0))), "散会前要听到", font=C.font(44), fill=C.mix(C.BG, C.MUTED, a0), anchor="mm")
        d.text((C.W // 2, 310), "一句完整的话", font=C.font(52), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        for idx, (label, ts) in enumerate(qs):
            aa = C.appear(t, ts, 0.20)
            if aa < 0.04:
                continue
            y = 420 + idx * 260
            C.rounded(d, (110, y, 970, y + 230), 32, C.mix(C.BG, C.CARD, aa))
            d.text((C.W // 2, y + 115), label, font=C.font(58), fill=C.mix(C.CARD, C.MINT, aa), anchor="mm")
            C.check_badge(d, 200, y + 115, C.appear(t, ts + 0.28, 0.18))
        punch = C.appear(t, max(1.55, duration * 0.62), 0.22)
        if punch > 0.04:
            y = 1280 + int(C.lerp(16, 0, punch))
            C.rounded(d, (120, y, 960, y + 180), 28, C.mix(C.BG, (18, 42, 36), punch))
            d.text((C.W // 2, y + 90), "听不到这句，就当没对齐", font=C.font(36), fill=C.mix(C.BG, C.YELLOW, punch), anchor="mm")
        yield img


def render_b_polite(duration: float):
    n = max(1, round(duration * C.FPS))
    for i in range(n):
        t = i / C.FPS
        img = C.new_bg()
        d = ImageDraw.Draw(img)
        C.tag(d, t, "收束 · 别当拍板")
        a0 = C.appear(t, 0.02)
        d.text((C.W // 2, 240 + int(C.lerp(16, 0, a0))), "别把礼貌当成拍板", font=C.font(48), fill=C.mix(C.BG, C.WHITE, a0), anchor="mm")
        a1 = C.appear(t, 0.16)
        if a1 > 0.04:
            y = 360 + int(C.lerp(18, 0, a1))
            C.rounded(d, (70, y, 510, y + 520), 32, C.mix(C.BG, (42, 24, 22), a1))
            d.text((290, y + 120), "点头", font=C.font(56), fill=C.mix(C.CARD, C.WHITE, a1), anchor="mm")
            d.text((290, y + 230), "只记气氛", font=C.font(36), fill=C.mix(C.CARD, C.MUTED, a1), anchor="mm")
            C.draw_x(d, 290, y + 380, C.appear(t, 0.70, 0.20), 34)
            C.strike_line(d, (110, y + 80, 470, y + 180), C.appear(t, 0.78, 0.24), C.mix(C.CARD, C.RED, a1))
        a2 = C.appear(t, 0.28)
        if a2 > 0.04:
            y = 360 + int(C.lerp(18, 0, a2))
            C.rounded(d, (570, y, 1010, y + 520), 32, C.mix(C.BG, (18, 42, 36), a2))
            d.text((790, y + 120), "写下", font=C.font(56), fill=C.mix(C.CARD, C.MINT, a2), anchor="mm")
            d.text((790, y + 230), "才记结论", font=C.font(36), fill=C.mix(C.CARD, C.WHITE, a2), anchor="mm")
            C.check_badge(d, 790, y + 380, C.appear(t, 0.88, 0.20))
        punch = C.appear(t, max(1.40, duration * 0.58), 0.22)
        if punch > 0.04:
            y = 1000 + int(C.lerp(16, 0, punch))
            C.rounded(d, (120, y, 960, y + 220), 28, C.mix(C.BG, C.CARD, punch))
            d.text((C.W // 2, y + 110), "没写下的点头，只是礼貌", font=C.font(38), fill=C.mix(C.CARD, C.YELLOW, punch), anchor="mm")
        yield img


def build_timeline(cues, duration: float) -> dict:
    if len(cues) != 15:
        raise SystemExit(f"need 15 phrases, got {len(cues)}")
    p = cues
    b1 = max(p[1][1] + 0.06, p[2][0] - C.LEAD)
    b1e = p[2][1]
    a3 = p[2][1]
    b2 = max(p[3][1] + 0.06, p[4][0] - C.LEAD)
    b2e = p[6][1]
    b5 = p[7][0]
    b5e = p[8][1]
    b6 = p[9][0]
    b6e = p[11][1]
    a7 = p[11][1]
    b8 = max(p[12][1] + 0.06, p[13][0] - C.LEAD)
    b8e = p[13][1]
    shots = [
        {"id": "S01a", "kind": "A", "start": 0.0, "end": p[0][1], "src": "assets/V-挥手.mp4", "line": p[0][2], "close": True},
        {"id": "S01b", "kind": "A", "start": p[0][1], "end": b1, "src": "assets/V-正对讲.mp4", "line": p[1][2]},
        {"id": "S02", "kind": "B", "start": b1, "end": b1e, "src": "broll/B-点头墙.mp4", "line": p[2][2], "broll": "nodwall"},
        {"id": "S03", "kind": "A", "start": a3, "end": b2, "src": "assets/V-指向.mp4", "line": p[3][2]},
        {"id": "S04", "kind": "B", "start": b2, "end": b2e, "src": "broll/B-三种点头.mp4", "line": p[6][2], "broll": "three"},
        {"id": "S05", "kind": "B", "start": b5, "end": b5e, "src": "broll/B-各想各的.mp4", "line": p[8][2], "broll": "mismatch"},
        {"id": "S06", "kind": "B", "start": b6, "end": b6e, "src": "broll/B-三问.mp4", "line": p[10][2], "broll": "threeq"},
        {"id": "S07", "kind": "A", "start": a7, "end": b8, "src": "assets/V-摊手.mp4", "line": p[12][2]},
        {"id": "S08", "kind": "B", "start": b8, "end": b8e, "src": "broll/B-礼貌不是拍板.mp4", "line": p[13][2], "broll": "polite"},
        {"id": "S09", "kind": "A", "start": b8e, "end": duration, "src": "assets/V-点赞.mp4", "line": p[14][2]},
    ]
    shots = C.close_shots(shots, duration)
    a_caps = [
        {"start": 0.0, "end": shots[0]["end"], "lines": ["大家好"]},
        {"start": shots[1]["start"], "end": shots[1]["end"], "lines": C.split_caption(p[1][2])},
        {"start": shots[3]["start"], "end": shots[3]["end"], "lines": ["点头不等于确认"]},
        {"start": shots[7]["start"], "end": shots[7]["end"], "lines": C.split_caption(p[12][2])},
        {"start": shots[9]["start"], "end": duration, "lines": ["没写下的点头", "只是礼貌"]},
    ]
    shutters = [
        {"start": shots[1]["start"], "color": list(C.CREAM)},
        {"start": shots[2]["start"], "color": list(C.MINT)},
        {"start": shots[3]["start"], "color": list(C.CREAM)},
        {"start": shots[4]["start"], "color": list(C.YELLOW)},
        {"start": shots[5]["start"], "color": list(C.MINT)},
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
        "cover_title": "点头",
        "cover_sub": "不等于确认",
        "cover_line": "谁来做 · 做到哪 · 何时交",
        "cover_src": "assets/A-角色-小灯-指向.jpg",
    }
    (ROOT / "plan").mkdir(exist_ok=True)
    (ROOT / "plan" / "shot_recipe.json").write_text(json.dumps(recipe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "plan" / "broll.json").write_text(
        json.dumps(
            {
                "clips": [
                    {"id": "nodwall", "file": "broll/B-点头墙.mp4", "note": "人人点头，一句话没确认"},
                    {"id": "three", "file": "broll/B-三种点头.mp4", "note": "没听懂 / 不反驳 / 想散会"},
                    {"id": "mismatch", "file": "broll/B-各想各的.mp4", "note": "全体同意对照各想各的"},
                    {"id": "threeq", "file": "broll/B-三问.mp4", "note": "谁来做做到哪何时交"},
                    {"id": "polite", "file": "broll/B-礼貌不是拍板.mp4", "note": "点头划掉，写下打勾"},
                ]
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
        "factory": "66_点头不等于确认",
        "topic": 66,
        "source_note": "工厂 66_点头不等于确认 / 云端 NEW",
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
    d.text((C.W // 2, 160), "点头", font=C.font(52), fill=C.WHITE, anchor="mm")
    d.text((C.W // 2, 250), "不等于确认", font=C.font(64), fill=C.YELLOW, anchor="mm")
    d.text((C.W // 2, 340), "谁来做 · 做到哪 · 何时交", font=C.font(34), fill=C.MINT, anchor="mm")
    d.text((C.W // 2, 410), "没写下的点头，只是礼貌", font=C.font(30), fill=C.MUTED, anchor="mm")
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
    C.frames_to_mp4(render_b_nodwall(max(2.4, bmap["S02"]["end"] - bmap["S02"]["start"]) + 0.12), ROOT / "broll" / "B-点头墙.mp4")
    C.frames_to_mp4(render_b_three(max(2.4, bmap["S04"]["end"] - bmap["S04"]["start"]) + 0.12), ROOT / "broll" / "B-三种点头.mp4")
    C.frames_to_mp4(render_b_mismatch(max(2.4, bmap["S05"]["end"] - bmap["S05"]["start"]) + 0.12), ROOT / "broll" / "B-各想各的.mp4")
    C.frames_to_mp4(render_b_threeq(max(2.4, bmap["S06"]["end"] - bmap["S06"]["start"]) + 0.12), ROOT / "broll" / "B-三问.mp4")
    C.frames_to_mp4(render_b_polite(max(2.4, bmap["S08"]["end"] - bmap["S08"]["start"]) + 0.12), ROOT / "broll" / "B-礼貌不是拍板.mp4")
    make_cover()
    staged = C.assemble(ROOT, data, NAME, STAGED_NAME)
    dur = C.probe_dur(staged)
    C.write_docs(
        ROOT,
        episode=66,
        name=NAME,
        staged_name=STAGED_NAME,
        duration=dur,
        data=data,
        source_note="工厂 66_点头不等于确认 / 云端 NEW",
        note_body="钩子：会上人人点头，散会各走各的。点：点头可能是没听懂、不反驳、或只想散会。做法：散会前听到谁来做、做到哪、什么时候交。收束：没写下的点头，只是礼貌。不跟成片 45 会议结束时间重复。",
    )
    C.patch_index(STAGED_NAME, dur)
    report = C.qa(ROOT, staged, data, "66_点头不等于确认")
    print("STAGED", staged, "dur", dur, C.zh_seconds(dur), "ok", report["ok"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
