# -*- coding: utf-8 -*-
"""用口播对齐时间轴写出 timeline.json，并生成垫乐/切镜音。"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def probe_dur(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True,
    ).strip()
    return float(out)


def parse_vtt(path: Path) -> list[tuple[float, float, str]]:
    text = path.read_text(encoding="utf-8")
    cues: list[tuple[float, float, str]] = []
    if text.lstrip().startswith("{") or '"SentenceBoundary"' in text:
        for raw in text.splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if obj.get("type") != "SentenceBoundary":
                continue
            start = obj["offset"] / 10_000_000
            end = start + obj["duration"] / 10_000_000
            cues.append((start, end, str(obj.get("text", "")).strip()))
        return cues

    def ts(s: str) -> float:
        h, m, rest = s.split(":")
        sec, *ms = rest.replace(",", ".").split(".")
        frac = float("0." + (ms[0] if ms else "0"))
        return int(h) * 3600 + int(m) * 60 + int(sec) + frac

    blocks = re.split(r"\n\s*\n", text)
    for block in blocks:
        lines = [ln.strip() for ln in block.splitlines() if ln.strip() and ln.strip() != "WEBVTT"]
        if not lines:
            continue
        timing = next((ln for ln in lines if "-->" in ln), "")
        m = re.search(r"([\d:.]+)\s+-->\s+([\d:.]+)", timing)
        if not m:
            continue
        body = " ".join(ln for ln in lines if "-->" not in ln and not ln.isdigit())
        cues.append((ts(m.group(1)), ts(m.group(2)), body))
    return cues


def split_caption(line: str) -> list[str]:
    line = line.strip("。．. ")
    if "，" in line and len(line) > 8:
        parts = [p for p in line.split("，") if p]
        if 1 < len(parts) <= 2:
            return parts
    return [line]


def main() -> None:
    recipe = json.loads((ROOT / "plan" / "shot_recipe.json").read_text(encoding="utf-8"))
    wav = ROOT / "audio" / "vo-full.wav"
    vtt = ROOT / "audio" / "vo.vtt"
    dur = probe_dur(wav)
    cues = parse_vtt(vtt)
    if not cues:
        raise SystemExit("no cues")

    align_lines = []
    for s, e, t in cues:
        align_lines.append(f"[{int(s * 1000)}ms-{int(e * 1000)}ms] {t}")
    (ROOT / "audio" / "vo-align.txt").write_text("\n".join(align_lines) + "\n", encoding="utf-8")

    shots_out = []
    a_caps = []
    shutters = []
    eyebrows = []
    cursor = 0.0
    for i, shot in enumerate(recipe["shots"]):
        phrase = shot["phrases"][0]
        cue = next((c for c in cues if phrase[:6] in c[2] or c[2][:6] in phrase), None)
        if cue:
            start, end = cue[0], cue[1]
        else:
            start = cursor
            end = min(dur, start + max(1.4, dur / len(recipe["shots"])))
        if i == 0:
            start = 0.0
        else:
            start = cursor
        if i == len(recipe["shots"]) - 1:
            end = dur
        if end <= start:
            end = start + 0.8
        cursor = end
        item = {
            "id": shot["id"],
            "kind": shot["kind"],
            "start": round(start, 3),
            "end": round(end, 3),
            "src": shot["src"],
            "line": phrase,
        }
        if shot.get("close"):
            item["close"] = True
        if shot.get("broll"):
            item["broll"] = shot["broll"]
        shots_out.append(item)
        if shot["kind"] == "A":
            a_caps.append({"start": round(start, 3), "end": round(end, 3), "lines": split_caption(phrase)})
            eyebrows.append({"start": round(start, 3), "end": round(end, 3), "text": f"A-ROLL / {shot['id'][-2:]}"})
        color = [245, 247, 250] if shot["kind"] == "A" else [126, 224, 197]
        if i == len(recipe["shots"]) - 1:
            color = [245, 193, 92]
        if i > 0:
            shutters.append({"start": round(start, 3), "color": color})

    timeline = {
        "audio": "audio/vo-full.wav",
        "duration": round(dur, 3),
        "fps": 24,
        "size": [1080, 1920],
        "title": recipe["title"],
        "bgm": "audio/bgm.wav",
        "shots": shots_out,
        "a_caps": a_caps,
        "shutters": shutters,
        "eyebrows": eyebrows,
        "cover": {
            "title": recipe["cover_title"],
            "sub": recipe["cover_sub"],
            "line": recipe["cover_line"],
            "src": recipe["cover_src"],
        },
    }
    (ROOT / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("timeline", dur, "shots", len(shots_out))

    # 垫乐：低音垫，不抢词
    bgm = ROOT / "audio" / "bgm.wav"
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"sine=frequency=196:sample_rate=44100:duration={dur + 2:.2f}",
            "-f", "lavfi",
            "-i", f"sine=frequency=247:sample_rate=44100:duration={dur + 2:.2f}",
            "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=longest,lowpass=f=420,volume=0.22,aformat=sample_rates=44100:channel_layouts=stereo",
            str(bgm),
        ],
        check=True,
        capture_output=True,
    )

    # 切镜音：每个快门一个短嘀
    sfx = ROOT / "audio" / "sfx.wav"
    delays = []
    parts = []
    for i, sh in enumerate(shutters):
        ms = int(sh["start"] * 1000)
        delays.append(f"aevalsrc=0.012*sin(2*PI*880*t):s=44100:d=0.07,adelay={ms}|{ms}[s{i}]")
        parts.append(f"[s{i}]")
    if not parts:
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", f"{dur:.2f}", str(sfx)],
            check=True,
            capture_output=True,
        )
    else:
        fc = ";".join(delays) + f";{''.join(parts)}amix=inputs={len(parts)}:duration=longest,aformat=sample_rates=44100:channel_layouts=stereo"
        subprocess.run(
            ["ffmpeg", "-y", "-filter_complex", fc, "-t", f"{dur:.2f}", str(sfx)],
            check=True,
            capture_output=True,
        )
    print("audio beds", bgm.exists(), sfx.exists())


if __name__ == "__main__":
    main()
