# -*- coding: utf-8 -*-
"""切镜、A-roll 近一点、叠圆角字幕、配音+垫乐+切镜音效。"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1080, 1920, 24
NAME = "先给场景再给方法"


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout)[-2500:])


def probe_dur(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True,
    ).strip()
    return float(out)


def cut_shot(src: Path, dur: float, dest: Path, kind: str, in_pt: float = 0.0, close: bool = False) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    src_dur = max(0.01, probe_dur(src) - in_pt)
    if kind == "A" and close:
        vf = f"scale=1380:2454,crop={W}:{H}:150:60,fps={FPS},setsar=1,format=yuv420p"
    elif kind == "A":
        vf = f"scale=1188:2112,crop={W}:{H}:54:105,fps={FPS},setsar=1,format=yuv420p"
    else:
        vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},setsar=1,format=yuv420p"
    if kind == "A" and dur > src_dur + 0.05:
        vf = f"setpts=PTS*{dur / src_dur:.6f},{vf}"
    elif dur > src_dur + 0.02:
        vf = f"{vf},tpad=stop_mode=clone:stop_duration={dur - src_dur:.3f}"
    cmd = ["ffmpeg", "-y"]
    if in_pt > 0.01:
        cmd += ["-ss", f"{in_pt:.3f}"]
    cmd += [
        "-i", str(src), "-t", f"{dur:.3f}",
        "-vf", vf, "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18", str(dest),
    ]
    run(cmd)


def main() -> None:
    os.chdir(ROOT)
    data = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
    shots_dir = ROOT / "shots"
    shots_dir.mkdir(exist_ok=True)
    parts: list[Path] = []
    for shot in data["shots"]:
        dur = float(shot["end"]) - float(shot["start"])
        src = ROOT / shot["src"]
        dest = shots_dir / f"{shot['id']}.mp4"
        in_pt = float(shot.get("in", 0) or 0)
        close = bool(shot.get("close"))
        print(shot["id"], shot["kind"], f"{dur:.2f}s", src.name)
        cut_shot(src, dur, dest, shot["kind"], in_pt, close)
        parts.append(dest)

    lst = shots_dir / "concat.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    concat = shots_dir / "video_only.mp4"
    run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
            str(concat),
        ]
    )
    caps = shots_dir / "caption_layer.mov"
    burned = shots_dir / "video_subs.mp4"
    if caps.exists():
        run(
            [
                "ffmpeg", "-y", "-i", str(concat), "-i", str(caps),
                "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p",
                "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an", str(burned),
            ]
        )
    else:
        burned = concat

    audio = ROOT / data["audio"]
    bgm = ROOT / "audio" / "bgm.wav"
    sfx = ROOT / "audio" / "sfx.wav"
    final = ROOT / "00_最终成片_先给场景再给方法.mp4"
    staged = Path("/workspace/成片") / "06-先给场景再给方法.mp4"
    (ROOT / "final").mkdir(exist_ok=True)

    inputs = ["ffmpeg", "-y", "-i", str(burned), "-i", str(audio)]
    filters = ["[1:a]loudnorm=I=-16:LRA=11:TP=-1.5,aformat=sample_rates=44100:channel_layouts=stereo[vo]"]
    mix_ins = ["[vo]"]
    idx = 2
    if bgm.exists():
        inputs += ["-i", str(bgm)]
        filters.append(f"[{idx}:a]adelay=800|800,volume=0.18,highpass=f=140[bg]")
        mix_ins.append("[bg]")
        idx += 1
    if sfx.exists():
        inputs += ["-i", str(sfx)]
        filters.append(f"[{idx}:a]volume=0.30[sfx]")
        mix_ins.append("[sfx]")
        idx += 1
    n = len(mix_ins)
    filters.append(f"{''.join(mix_ins)}amix=inputs={n}:duration=first:dropout_transition=2,alimiter=limit=0.95[a]")
    inputs += [
        "-filter_complex",
        ";".join(filters),
        "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-ar", "44100", "-ac", "2", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        str(final),
    ]
    run(inputs)
    staged.parent.mkdir(parents=True, exist_ok=True)
    run(["cp", "-f", str(final), str(staged)])
    run(["cp", "-f", str(final), str(ROOT / "final" / f"{NAME}.mp4")])
    print("FINAL", final, "dur", probe_dur(final))
    print("STAGED", staged, "dur", probe_dur(staged))


if __name__ == "__main__":
    main()
