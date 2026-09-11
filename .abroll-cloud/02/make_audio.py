# -*- coding: utf-8 -*-
"""One-pass Edge TTS (Yunyang) for the locked topic-02 copy + pad + later SFX."""
from __future__ import annotations

import asyncio
import subprocess
import wave
from pathlib import Path

import edge_tts
import numpy as np

ROOT = Path(__file__).resolve().parent
AUDIO = ROOT / "audio"
VOICE = "zh-CN-YunyangNeural"
RATE = "-4%"
TEXT = (ROOT / "script" / "voiceover.txt").read_text(encoding="utf-8").strip()


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout)[-2500:])


def probe(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True,
    ).strip()
    return float(out)


def make_bgm(dest: Path, seconds: float) -> None:
    sr = 44100
    t = np.linspace(0, seconds, int(sr * seconds), endpoint=False)
    a = 0.038 * np.sin(2 * np.pi * 174.61 * t)
    b = 0.028 * np.sin(2 * np.pi * 220.00 * t)
    c = 0.018 * np.sin(2 * np.pi * 261.63 * t * 1.003)
    env = np.minimum(1.0, t / 1.1) * np.minimum(1.0, (seconds - t) / 1.4)
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t)
    mix = (a + b + c) * env * (0.75 + 0.25 * lfo)
    pcm = np.clip(mix * 32767, -32767, 32767).astype(np.int16)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(dest), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def make_sfx(dest: Path, cuts: list[float]) -> None:
    sr = 44100
    total = max((cuts[-1] if cuts else 1.0) + 0.5, 1.0)
    n = int(sr * (total + 0.5))
    buf = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(5)
    for cut in cuts:
        i0 = int(cut * sr)
        length = int(0.05 * sr)
        tt = np.linspace(0, 1, length, endpoint=False)
        whoosh = np.sin(2 * np.pi * (360 + 720 * tt) * tt) * (1 - tt) ** 2
        noise = rng.normal(0, 0.16, length) * (1 - tt)
        burst = 0.20 * whoosh + 0.07 * noise
        i1 = min(n, i0 + length)
        buf[i0:i1] += burst[: i1 - i0]
    pcm = np.clip(buf * 32767, -32767, 32767).astype(np.int16)
    with wave.open(str(dest), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


async def synth() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    mp3 = AUDIO / "vo-full.mp3"
    comm = edge_tts.Communicate(TEXT, VOICE, rate=RATE)
    await comm.save(str(mp3))
    dest = AUDIO / "vo-full.wav"
    run(["ffmpeg", "-y", "-i", str(mp3), "-ac", "1", "-ar", "44100", "-c:a", "pcm_s16le", str(dest)])
    mp3.unlink(missing_ok=True)
    dur = probe(dest)
    make_bgm(AUDIO / "bgm.wav", dur + 1.4)
    print("vo", dest, f"{dur:.3f}s")


def main() -> None:
    asyncio.run(synth())


if __name__ == "__main__":
    main()
