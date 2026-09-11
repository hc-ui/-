# -*- coding: utf-8 -*-
"""Emit markdown + voiceover.txt from aroll catalogs."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/workspace/.abroll-cloud/aroll")
OUT = ROOT / "scripts"


def emit(catalog_path: Path) -> None:
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    for t in data["topics"]:
        slug = t["slug"]
        rows = "\n".join(
            f"| {p['kind']} | {p['line']} | {p.get('shot', '对照卡/口播')} |"
            for p in t["phrases"]
        )
        md = f"""# {t['title']}

- slug: `{slug}`
- 类型: 普通短视频 / 知识口播
- 选题号: {t.get('n', '-')}
- 封面副题: {t['cover_sub']}
- 封面收束: {t['cover_line']}
- 音频: `.abroll-cloud/aroll/audio/{slug}.wav`

## 口播全文

{t['voiceover']}

## 短语切分（A/B）

| kind | line | 画面任务 |
|------|------|----------|
{rows}

A-roll 只说场景、判断和收束。B-roll 用对照卡。不演人物冲突，不念链接，不报时长。
"""
        (OUT / f"{slug}.md").write_text(md, encoding="utf-8")
        (OUT / f"{slug}.voiceover.txt").write_text(t["voiceover"].rstrip() + "\n", encoding="utf-8")
        print("wrote", slug)


if __name__ == "__main__":
    emit(ROOT / "scout_catalog.json")
    emit(ROOT / "catalog.json")
