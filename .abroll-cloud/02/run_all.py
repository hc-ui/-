# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_py(name: str) -> None:
    print("==>", name)
    subprocess.check_call([sys.executable, str(ROOT / name)], cwd=str(ROOT))


def make_sfx_from_timeline() -> None:
    from make_audio import make_sfx

    data = json.loads((ROOT / "timeline.json").read_text(encoding="utf-8"))
    cuts = [float(s["start"]) for s in data["shots"][1:]]
    make_sfx(ROOT / "audio" / "sfx.wav", cuts)
    print("sfx", cuts)


def main() -> None:
    run_py("make_audio.py")
    run_py("align_vo.py")
    run_py("build_timeline.py")
    make_sfx_from_timeline()
    run_py("render_broll.py")
    run_py("render_caps.py")
    run_py("make_cover.py")
    run_py("assemble.py")


if __name__ == "__main__":
    main()
