#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""成片 47 加长：研一别脱产离校实习。47-long，无 freeze-pad。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import ImageDraw

sys.path.insert(0, "/workspace/.abroll-cloud")
import _longcut as L

ROOT = Path(__file__).resolve().parent
NAME = "研一别脱产离校实习"
STAGED_NAME = "47-研一别脱产离校实习.mp4"
W, H, FPS = L.W, L.H, L.FPS
BG, CARD, MINT, YELLOW, WHITE, MUTED, CREAM, RED, INK, AMBER = (
    L.BG, L.CARD, L.MINT, L.YELLOW, L.WHITE, L.MUTED, L.CREAM, L.RED, L.INK, L.AMBER,
)
font, appear, lerp, mix, rounded, tag = L.font, L.appear, L.lerp, L.mix, L.rounded, L.tag
bob, strike_line, check_badge, frames_to_mp4 = L.bob, L.strike_line, L.check_badge, L.frames_to_mp4
text_wh = L.text_wh


def new_bg():
    return L.new_bg("teal")


def strike_text(draw, x: int, y: int, text: str, fnt, t: float, start: float) -> None:
    st = appear(t, start, 0.28)
    if st <= 0.04:
        return
    tw, _ = text_wh(draw, text, fnt)
    x0, x1 = x - 8, x + tw + 8
    draw.line([(x0, y), (int(lerp(x0, x1, st)), y)], fill=mix(CARD, RED, st), width=8)


def draw_empty_desk(draw, cx: int, cy: int, scale: float, a: float) -> None:
    if a <= 0.04:
        return
    w, h = int(260 * scale), int(170 * scale)
    x0, y0 = cx - w // 2, cy - h // 2
    rounded(draw, (x0, y0, x0 + w, y0 + h), 18, mix(BG, CARD, a))
    top = y0 + int(28 * scale)
    draw.rectangle((x0 + 16, top, x0 + w - 16, top + 8), fill=mix(CARD, MUTED, a))
    cw, ch = int(88 * scale), int(70 * scale)
    cx0, cy0 = cx - cw // 2, y0 + h - 8
    rounded(draw, (cx0, cy0, cx0 + cw, cy0 + ch), 12, mix(CARD, (36, 40, 48), a))
    draw.text((cx, y0 + int(18 * scale)), "工位", font=font(22), fill=mix(CARD, MUTED, a), anchor="mm")
    draw.text((cx, cy0 + ch + int(22 * scale)), "空着", font=font(22), fill=mix(BG, RED, a), anchor="mm")


def draw_roster(draw, cx: int, cy: int, scale: float, a: float, marked: bool) -> None:
    if a <= 0.04:
        return
    w, h = int(220 * scale), int(260 * scale)
    x0, y0 = cx - w // 2, cy - h // 2
    rounded(draw, (x0, y0, x0 + w, y0 + h), 20, mix(BG, CARD, a))
    rounded(draw, (x0, y0, x0 + w, y0 + int(48 * scale)), 20, mix(CARD, YELLOW, a))
    draw.rectangle((x0, y0 + int(32 * scale), x0 + w, y0 + int(48 * scale)), fill=mix(CARD, YELLOW, a))
    draw.text((cx, y0 + int(24 * scale)), "组会名单", font=font(22), fill=mix(YELLOW, INK, a), anchor="mm")
    names = ["甲", "乙", "丙", "丁"]
    row_f = font(26)
    for i, name in enumerate(names):
        yy = y0 + int(72 * scale) + i * int(42 * scale)
        draw.text((x0 + int(36 * scale), yy), name, font=row_f, fill=mix(CARD, WHITE, a), anchor="lm")
        if marked and i == 2:
            strike_text(draw, x0 + int(36 * scale), yy, name, row_f, 10.0, 0.0)
            draw.text((x0 + w - int(36 * scale), yy), "缺", font=row_f, fill=mix(CARD, RED, a), anchor="rm")


def draw_ticket(draw, cx: int, cy: int, scale: float, a: float, stamped: bool) -> None:
    if a <= 0.04:
        return
    w, h = int(420 * scale), int(220 * scale)
    x0, y0 = cx - w // 2, cy - h // 2
    rounded(draw, (x0, y0, x0 + w, y0 + h), 22, mix(BG, CARD, a))
    draw.rectangle((x0, y0, x0 + int(18 * scale), y0 + h), fill=mix(CARD, YELLOW, a))
    draw.text((cx, y0 + int(48 * scale)), "合肥  →  外地", font=font(28), fill=mix(CARD, WHITE, a), anchor="mm")
    draw.text((cx, y0 + int(110 * scale)), "全职离校", font=font(26), fill=mix(CARD, MUTED, a), anchor="mm")
    if stamped:
        rx0, ry0 = cx + int(40 * scale), y0 + int(70 * scale)
        draw.ellipse((rx0, ry0, rx0 + int(120 * scale), ry0 + int(120 * scale)), outline=mix(CARD, RED, a), width=8)
        draw.text((rx0 + int(60 * scale), ry0 + int(60 * scale)), "先别", font=font(28), fill=mix(CARD, RED, a), anchor="mm")


def render_b_risk(duration: float) -> list:
    n = max(1, round(duration * FPS))
    rows = [
        (0.16, "离", "全职离校", "人整段不在", RED),
        (0.34, "会", "临时组会", "说开就开", YELLOW),
        (0.52, "场", "要人在场", "导师随时叫", MINT),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "脱产风险", MINT)
        a0 = appear(t, 0.02)
        d.text((W // 2, 230 + bob(t, 3)), "风险极高", font=font(56), fill=mix(BG, WHITE, a0), anchor="mm")
        for idx, (frac, num, head, body, color) in enumerate(rows):
            a = appear(t, duration * frac, 0.24)
            if a < 0.04:
                continue
            y = 380 + idx * 176 + int(lerp(22, 0, a)) + bob(t + idx, 3, 1.3)
            rounded(d, (90, y, 990, y + 158), 28, mix(BG, CARD, a))
            d.ellipse((128, y + 36, 220, y + 128), fill=mix(CARD, color, a))
            d.text((174, y + 82), num, font=font(36), fill=mix(color, INK, a), anchor="mm")
            d.text((248, y + 50), head, font=font(42), fill=mix(CARD, color, a), anchor="lm")
            d.text((248, y + 114), body, font=font(30), fill=mix(CARD, WHITE, a), anchor="lm")
        punch = appear(t, duration * 0.74, 0.22)
        if punch > 0.04:
            y = 980 + int(lerp(16, 0, punch))
            rounded(d, (140, y, 940, y + 150), 26, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y + 75), "人一走就对不上", font=font(48), fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_b_empty(duration: float) -> list:
    n = max(1, round(duration * FPS))
    rows = [
        (0.28, "腿", "派跑腿", "要人在场", YELLOW),
        (0.44, "名", "组会名单", "对不上", RED),
        (0.60, "空", "工位空了", "就是把柄", CREAM),
    ]
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "空工位", MINT)
        a0 = appear(t, 0.02)
        d.text((W // 2, 220 + bob(t, 3)), "人一走", font=font(56), fill=mix(BG, WHITE, a0), anchor="mm")
        draw_empty_desk(d, 300, 420 + bob(t, 4), 1.05, appear(t, 0.04, 0.22))
        draw_roster(d, 780, 420, 1.0, appear(t, 0.10, 0.22), marked=t > duration * 0.22)
        for idx, (frac, num, head, body, color) in enumerate(rows):
            a = appear(t, duration * frac, 0.24)
            if a < 0.04:
                continue
            y = 640 + idx * 160 + int(lerp(18, 0, a)) + bob(t + idx, 3, 1.2)
            rounded(d, (90, y, 990, y + 146), 26, mix(BG, CARD, a))
            d.ellipse((128, y + 30, 214, y + 116), fill=mix(CARD, color, a))
            d.text((171, y + 73), num, font=font(34), fill=mix(color, INK, a), anchor="mm")
            d.text((248, y + 46), head, font=font(38), fill=mix(CARD, color, a), anchor="lm")
            d.text((248, y + 104), body, font=font(28), fill=mix(CARD, WHITE, a), anchor="lm")
        punch = appear(t, duration * 0.80, 0.22)
        if punch > 0.04:
            y = 1180 + int(lerp(14, 0, punch))
            rounded(d, (140, y, 940, y + 140), 26, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y + 70), "空座位就是把柄", font=font(46), fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_b_checkpoint(duration: float) -> list:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "查岗", MINT)
        a0 = appear(t, 0.02)
        d.text((W // 2, 220 + bob(t, 3)), "先别走", font=font(56), fill=mix(BG, WHITE, a0), anchor="mm")
        draw_ticket(d, W // 2, 470 + bob(t, 3, 1.1), 1.12, appear(t, 0.08, 0.24), stamped=t > duration * 0.28)
        bad = appear(t, duration * 0.36, 0.22)
        if bad > 0.04:
            y = 680 + int(lerp(16, 0, bad))
            rounded(d, (90, y, 990, y + 160), 26, mix(BG, CARD, bad))
            d.text((160, y + 70), "查岗对上空座位", font=font(38), fill=mix(CARD, WHITE, bad), anchor="lm")
            d.text((160, y + 122), "空座位解释不清", font=font(28), fill=mix(CARD, RED, bad), anchor="lm")
        good = appear(t, duration * 0.56, 0.22)
        if good > 0.04:
            y = 880 + int(lerp(16, 0, good))
            rounded(d, (90, y, 990, y + 160), 26, mix(BG, (22, 40, 36), good))
            d.text((160, y + 80), "师生矛盾，从这里起", font=font(36), fill=mix(CARD, YELLOW, good), anchor="lm")
        punch = appear(t, duration * 0.76, 0.22)
        if punch > 0.04:
            y = 1100 + int(lerp(16, 0, punch))
            rounded(d, (140, y, 940, y + 150), 26, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y + 75), "空座位解释不清", font=font(46), fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def render_b_stay(duration: float) -> list:
    n = max(1, round(duration * FPS))
    out = []
    for i in range(n):
        t = i / FPS
        img = new_bg()
        d = ImageDraw.Draw(img)
        tag(d, t, "人留下", MINT)
        a0 = appear(t, 0.02)
        d.text((W // 2, 220 + bob(t, 3)), "人先留在工位", font=font(50), fill=mix(BG, WHITE, a0), anchor="mm")
        bad = appear(t, duration * 0.12)
        if bad > 0.04:
            y = 380 + int(lerp(16, 0, bad)) + bob(t, 3)
            rounded(d, (90, y, 990, y + 200), 28, mix(BG, CARD, bad))
            d.text((W // 2, y + 60), "错", font=font(28), fill=mix(CARD, RED, bad), anchor="mm")
            d.text((W // 2, y + 130), "把人挪出工位", font=font(42), fill=mix(CARD, WHITE, bad), anchor="mm")
            strike_line(d, (180, y + 150, 900, y + 170), appear(t, duration * 0.26, 0.3), mix(CARD, RED, bad))
        good = appear(t, duration * 0.36)
        if good > 0.04:
            y = 640 + int(lerp(16, 0, good)) + bob(t + 0.5, 3)
            rounded(d, (90, y, 990, y + 200), 28, mix(BG, (22, 40, 36), good))
            d.text((W // 2, y + 60), "对", font=font(28), fill=mix(CARD, MINT, good), anchor="mm")
            d.text((W // 2, y + 130), "人留在工位 · 活再谈", font=font(40), fill=mix(CARD, YELLOW, good), anchor="mm")
            check_badge(d, 900, y + 100, appear(t, duration * 0.48, 0.2))
        mid = appear(t, duration * 0.56)
        if mid > 0.04:
            y = 880 + int(lerp(12, 0, mid))
            rounded(d, (90, y, 990, y + 150), 26, mix(BG, CARD, mid))
            d.text((W // 2, y + 75), "不要把人整段挪出合肥", font=font(36), fill=mix(CARD, WHITE, mid), anchor="mm")
        punch = appear(t, duration * 0.74, 0.22)
        if punch > 0.04:
            y = 1080 + int(lerp(16, 0, punch))
            rounded(d, (140, y, 940, y + 150), 26, mix(BG, (42, 28, 18), punch))
            d.text((W // 2, y + 75), "人不能先空", font=font(50), fill=mix(BG, YELLOW, punch), anchor="mm")
        out.append(img)
    return out


def make_cover() -> Path:
    data = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
    cover = data["cover"]
    from PIL import Image
    char = Image.open(ROOT / cover["src"]).convert("RGB")
    scale = max(W / char.width, H / char.height)
    nw, nh = int(char.width * scale), int(char.height * scale)
    char = char.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - W) // 2
    y = int((nh - H) * 0.62)
    canvas = char.crop((x, y, x + W, y + H))
    overlay = Image.new("RGBA", (W, H), (11, 13, 18, 48))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((70, 80, 1010, 470), radius=36, fill=(22, 24, 28))
    d.text((W // 2, 160), "研一别脱产", font=font(58), fill=WHITE, anchor="mm")
    d.text((W // 2, 250), "离校实习", font=font(52), fill=YELLOW, anchor="mm")
    d.text((W // 2, 340), cover["sub"], font=font(36), fill=MINT, anchor="mm")
    d.text((W // 2, 410), cover["line"], font=font(30), fill=MUTED, anchor="mm")
    dest = ROOT / f"00_封面_{NAME}.jpg"
    canvas.save(dest, quality=92)
    (ROOT / "final").mkdir(exist_ok=True)
    canvas.save(ROOT / "final" / "cover.jpg", quality=92)
    return dest


def main() -> None:
    L.copy_assets(ROOT, [
        "V-挥手.mp4", "V-摊手.mp4", "V-指向.mp4", "V-点赞.mp4",
        "V-正对讲.mp4", "V-侧对讲.mp4", "A-角色-小灯-摊手.jpg",
    ])
    duration, cues = L.ensure_vo_window(ROOT)
    print("VO", duration)
    for row in cues:
        print(f"  {row[0]:6.3f}-{row[1]:6.3f}  {row[2]}")
    L.make_bgm(ROOT, duration, (196, 247, 294))
    data = L.build_timeline(ROOT, cues, duration)
    print("timeline", [(s["id"], s["start"], s["end"], s["kind"]) for s in data["shots"]])

    mapping = {
        "risk": ("B-风险极高.mp4", render_b_risk),
        "empty_desk": ("B-空工位.mp4", render_b_empty),
        "checkpoint": ("B-查岗.mp4", render_b_checkpoint),
        "stay": ("B-人留下.mp4", render_b_stay),
    }
    for shot in data["shots"]:
        key = shot.get("broll")
        if not key:
            continue
        fname, renderer = mapping[key]
        d = max(2.4, float(shot["end"]) - float(shot["start"]))
        print("render", fname, d)
        frames_to_mp4(renderer(d + 0.12), ROOT / "broll" / fname)

    make_cover()
    staged = L.assemble(ROOT, data, NAME, STAGED_NAME, accent=MINT)
    dur = L.probe_dur(staged)
    note = """# 47 · 研一别脱产离校实习（加长）

普通短视频 / 知识口播。草稿 `{draft}`。覆盖 12.7s 短切。

- **选题**：topics-batch3.md #47
- **成片**：`成片/{staged}`
- **不用**：远程实习讲法、下一期、真名
- **云端 only**：不写盘符，不传 Drive，无 freeze-pad

## 口播

{vo}

## 规格

1080×1920，24 fps，H.264 + AAC 44100 stereo，约 {duration:.2f} 秒。镜头 {nshots} 条。
"""
    L.write_docs(ROOT, dur, staged, data, {
        "project_name": "47_研一别脱产离校实习_long",
        "episode": 47,
        "title": NAME,
        "source_note": "topics-batch3.md #47 / 47-long 加长重切 / 备忘录第二节 3",
        "unused_of": "16切片 / 28报销 / 37撞课 / 46六十分 / 48远程",
        "staged_name": STAGED_NAME,
        "note_md": note,
    })
    L.patch_index(STAGED_NAME, dur)
    L.patch_delivery_row("47", STAGED_NAME, dur)
    report = L.qa(ROOT, staged, data, "47_研一别脱产离校实习_long")
    print("STAGED", staged, "dur", dur, "ok", report["ok"], "target", report["in_target_window"])
    if not report["ok"]:
        raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
