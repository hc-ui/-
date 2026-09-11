# -*- coding: utf-8 -*-
"""Silence-gap alignment; text stays the original phrases."""
from __future__ import annotations

import json
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
WAV = ROOT / "audio" / "vo-full.wav"
PHRASES = [ln.strip() for ln in (ROOT / "script" / "phrases.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]


def load_mono(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as w:
        sr = w.getframerate()
        n = w.getnframes()
        data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32)
        if w.getnchannels() == 2:
            data = data.reshape(-1, 2).mean(axis=1)
    return data / 32768.0, sr


def energy(x: np.ndarray, sr: int, hop_ms: float = 10.0) -> tuple[np.ndarray, np.ndarray]:
    hop = int(sr * hop_ms / 1000)
    win = max(hop * 2, 1)
    n = len(x)
    vals = []
    times = []
    for i in range(0, n - win, hop):
        sl = x[i : i + win]
        vals.append(float(np.sqrt(np.mean(sl * sl) + 1e-12)))
        times.append((i + win / 2) / sr)
    return np.array(times), np.array(vals)


def find_gaps(times: np.ndarray, rms: np.ndarray, min_gap: float = 0.12) -> list[float]:
    thr = max(0.012, float(np.median(rms) * 0.55))
    silent = rms < thr
    cuts: list[float] = []
    i = 0
    while i < len(silent):
        if not silent[i]:
            i += 1
            continue
        j = i
        while j < len(silent) and silent[j]:
            j += 1
        dur = times[min(j, len(times) - 1)] - times[i]
        if dur >= min_gap and i > 4:
            cuts.append(float(times[i] + dur / 2))
        i = j
    return cuts


def main() -> None:
    x, sr = load_mono(WAV)
    dur = len(x) / sr
    times, rms = energy(x, sr)
    cuts = find_gaps(times, rms)
    # We need n-1 cuts for n phrases
    need = len(PHRASES) - 1
    # Keep cuts that are well inside, prefer ones near expected char-proportional marks
    weights = np.array([max(1, len(p.replace("，", "").replace("。", "").replace(" ", ""))) for p in PHRASES], dtype=float)
    marks = np.cumsum(weights)[:-1] / weights.sum() * dur
    chosen: list[float] = []
    used = set()
    for m in marks:
        if not cuts:
            chosen.append(float(m))
            continue
        idx = int(np.argmin([abs(c - m) if i not in used else 1e9 for i, c in enumerate(cuts)]))
        if abs(cuts[idx] - m) < 1.15:
            chosen.append(cuts[idx])
            used.add(idx)
        else:
            chosen.append(float(m))
    chosen = sorted(chosen)
    bounds = [0.0] + chosen + [dur]
    # enforce monotonic + min 0.28s
    for i in range(1, len(bounds)):
        if bounds[i] <= bounds[i - 1] + 0.28:
            bounds[i] = min(dur, bounds[i - 1] + 0.28)
    bounds[-1] = dur
    segs = []
    for i, text in enumerate(PHRASES):
        segs.append(
            {
                "index": i,
                "text": text,
                "start_ms": int(round(bounds[i] * 1000)),
                "end_ms": int(round(bounds[i + 1] * 1000)),
            }
        )
    segs[-1]["end_ms"] = int(round(dur * 1000))
    (ROOT / "audio" / "vo-align.json").write_text(
        json.dumps({"duration": dur, "segments": segs, "cuts": cuts}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    lines = [f"[{s['start_ms']}ms-{s['end_ms']}ms] {s['text']}" for s in segs]
    (ROOT / "audio" / "vo-align.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("dur", round(dur, 3), "cuts", [round(c, 2) for c in cuts])
    for s in segs:
        print(f"{s['start_ms']/1000:6.2f}-{s['end_ms']/1000:6.2f}  {s['text']}")


if __name__ == "__main__":
    main()
