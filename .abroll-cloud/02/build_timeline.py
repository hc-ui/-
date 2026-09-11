# -*- coding: utf-8 -*-
"""A/B shots from locked phrases. B-roll starts a half-beat early."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALIGN = json.loads((ROOT / "audio" / "vo-align.json").read_text(encoding="utf-8"))
LEAD = 0.12  # B 卷早切半拍


def t(seg: dict) -> tuple[float, float]:
    return seg["start_ms"] / 1000.0, seg["end_ms"] / 1000.0


def main() -> None:
    segs = ALIGN["segments"]
    dur = float(ALIGN["duration"])
    # 0 大家好 / 1 黏度 / 2 叶子 / 3 灰尘 / 4 旗子 / 5 声音 / 6 整条街
    s0s, s0e = t(segs[0])
    s1s, s1e = t(segs[1])
    s2s, s2e = t(segs[2])
    s3s, s3e = t(segs[3])
    s4s, s4e = t(segs[4])
    s5s, s5e = t(segs[5])
    s6s, s6e = t(segs[6])

    b1 = max(s1e - LEAD, s1s + 0.2)
    b2 = max(s3e - LEAD, s3s + 0.15)

    shots = [
        {"id": "S01a", "kind": "A", "start": 0.0, "end": s0e, "src": "assets/V-挥手.mp4", "line": segs[0]["text"], "close": True},
        {"id": "S01b", "kind": "A", "start": s0e, "end": b1, "src": "assets/V-摊手.mp4", "line": segs[1]["text"]},
        {"id": "S02", "kind": "B", "start": b1, "end": b2, "src": "broll/B-叶子还没落地.mp4", "line": segs[2]["text"] + " " + segs[3]["text"], "broll": "leaf"},
        {"id": "S03", "kind": "B", "start": b2, "end": s6s, "src": "broll/B-旗子慢慢弯.mp4", "line": segs[4]["text"] + " " + segs[5]["text"], "broll": "syrup"},
        {"id": "S04", "kind": "A", "start": s6s, "end": dur, "src": "assets/V-点赞.mp4", "line": segs[6]["text"]},
    ]
    shots[0]["start"] = 0.0
    for i in range(1, len(shots)):
        shots[i]["start"] = shots[i - 1]["end"]
    shots[-1]["end"] = dur

    data = {
        "audio": "audio/vo-full.wav",
        "duration": dur,
        "fps": 24,
        "size": [1080, 1920],
        "title": "树叶掉了二十秒还没落地",
        "bgm": "audio/bgm.wav",
        "bgm_credit": "synthesized pad in-repo",
        "shots": shots,
        "a_caps": [
            {"start": 0.0, "end": s0e, "lines": ["大家好"]},
            {"start": s0e, "end": b1, "lines": ["空气黏度", "乘上一万"]},
            {"start": s6s, "end": (s6s + s6e) / 2, "lines": ["整条街的雨和鸟"]},
            {"start": (s6s + s6e) / 2, "end": dur, "lines": ["都悬着慢移"]},
        ],
        "shutters": [
            {"start": b1, "color": [126, 224, 197]},
            {"start": b2, "color": [245, 193, 92]},
            {"start": s6s, "color": [245, 247, 250]},
        ],
        "eyebrows": [
            {"start": 0.0, "end": b1, "text": "A-ROLL / 01"},
            {"start": s6s, "end": dur, "text": "A-ROLL / 04"},
        ],
        "cover": {
            "title": "树叶掉了二十秒还没落地",
            "sub": "空气黏度乘上一万",
            "line": "雨和鸟都悬着慢移",
            "src": "assets/A-角色-小灯-摊手.jpg",
        },
    }
    (ROOT / "timeline.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "plan" / "shot_recipe.json").write_text(
        json.dumps(
            {
                "title": data["title"],
                "cover": data["cover"],
                "shots": [{"id": s["id"], "kind": s["kind"], "src": s["src"], "line": s["line"]} for s in shots],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (ROOT / "plan" / "broll.json").write_text(
        json.dumps(
            [
                {
                    "file": "broll/B-叶子还没落地.mp4",
                    "tag": "现象 超慢坠落",
                    "title": "叶子掉了二十秒",
                    "cards": [["还没落地", "不是慢镜头"], ["灰尘永不落", "黏在空气里"]],
                    "punch": "空气黏度 ×10000",
                    "phrases": [segs[2]["text"], segs[3]["text"]],
                },
                {
                    "file": "broll/B-旗子慢慢弯.mp4",
                    "tag": "后果 糖浆空气",
                    "title": "旗子不飘",
                    "cards": [["只慢慢弯", "像浸在糖浆"], ["声音变闷", "空气太稠"]],
                    "punch": "雨和鸟都悬着",
                    "phrases": [segs[4]["text"], segs[5]["text"]],
                },
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"duration": dur, "shots": [(s["id"], s["kind"], round(s["end"] - s["start"], 2)) for s in shots]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
