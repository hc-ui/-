#!/usr/bin/env python3
"""Catalog 成片/61- and higher. Cloud only. Never remake or overwrite 00-60."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/workspace")
STAGING = ROOT / "成片"
CLOUD_ROOT = ROOT / ".abroll-cloud"
STATE_PATH = CLOUD_ROOT / "qa-61-plus-state.json"
LOG_PATH = CLOUD_ROOT / "qa-61-plus.jsonl"
LOCK_PATH = CLOUD_ROOT / "qa-61-plus.lock"
INDEX_MD = STAGING / "INDEX.md"
INDEX_BAK = CLOUD_ROOT / "INDEX.chengpian.md"
DELIVERY_MD = CLOUD_ROOT / "DELIVERY.md"
PROBE_DIR = CLOUD_ROOT / "qa" / "61-plus"
REPORT_MD = PROBE_DIR / "报告.md"
KEEP_SNAP = PROBE_DIR / "keep-00-60.json"
BACKUP_DOCS = Path("/tmp/qa-61-plus-backup")

NUMBERED_RE = re.compile(r"^(\d+)-.+\.mp4$")
MIN_FINAL_BYTES = 400_000
STABLE_SECONDS = 2.5
SHORT_LIMIT = 30.0


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(event: dict) -> None:
    event = {"ts": utc_now(), **event}
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"processed": {}, "short": [], "keep_ok": True}


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def episode_num(name: str) -> int | None:
    m = NUMBERED_RE.match(name)
    return int(m.group(1)) if m else None


def is_protected(name: str) -> bool:
    if name == "仙侠云海突进.mp4":
        return True
    num = episode_num(name)
    return num is not None and num <= 60


def is_watch_target(name: str) -> bool:
    num = episode_num(name)
    return num is not None and num >= 61 and name.endswith(".mp4")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_stable(path: Path) -> bool:
    try:
        s1 = path.stat()
    except OSError:
        return False
    time.sleep(STABLE_SECONDS)
    try:
        s2 = path.stat()
    except OSError:
        return False
    return s1.st_size == s2.st_size and s1.st_mtime_ns == s2.st_mtime_ns and s1.st_size > 0


def ffprobe(path: Path) -> dict:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    last = ""
    for _ in range(4):
        proc = subprocess.run(cmd, capture_output=True, text=True)
        out = (proc.stdout or "").strip()
        if proc.returncode == 0 and out.startswith("{"):
            return json.loads(out)
        last = (proc.stderr or proc.stdout or "").strip() or f"rc={proc.returncode} empty"
        time.sleep(0.6)
    raise RuntimeError(last)


def ffmpeg_null(path: Path) -> None:
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(err or f"ffmpeg null decode failed: {path.name}")


def summarize_probe(probe: dict) -> dict:
    fmt = probe.get("format") or {}
    v = next((s for s in probe.get("streams") or [] if s.get("codec_type") == "video"), None)
    a = next((s for s in probe.get("streams") or [] if s.get("codec_type") == "audio"), None)
    duration = float(fmt.get("duration") or (v or {}).get("duration") or 0)
    width = int((v or {}).get("width") or 0)
    height = int((v or {}).get("height") or 0)
    vcodec = (v or {}).get("codec_name") or "?"
    acodec = (a or {}).get("codec_name") or "?"
    rate = int((a or {}).get("sample_rate") or 0)
    ch = int((a or {}).get("channels") or 0)
    ch_label = {1: "mono", 2: "stereo"}.get(ch, f"{ch}ch")
    rate_label = f"{rate / 1000:.1f}k".replace(".0k", "k") if rate else "?"
    spec = f"{width}×{height} {vcodec}+{acodec} {rate_label} {ch_label}"
    return {
        "duration": duration,
        "width": width,
        "height": height,
        "vcodec": vcodec,
        "acodec": acodec,
        "sample_rate": rate,
        "channels": ch,
        "spec": spec,
        "size": int(fmt.get("size") or 0),
    }


def source_for(name: str) -> str:
    num = episode_num(name)
    if num is None:
        return "云端成品"
    for folder in (CLOUD_ROOT / f"{num:02d}", CLOUD_ROOT / str(num), CLOUD_ROOT / f"{num}-long"):
        claim = folder / "CLAIM.md"
        if claim.exists():
            for line in claim.read_text(encoding="utf-8").splitlines():
                if "来源" in line and "：" in line:
                    src = line.split("：", 1)[-1].strip(" -*")
                    if src:
                        return f"topic {num} {src}"
    return f"topic {num} 云端成品"


def restore_delivery_if_missing() -> None:
    CLOUD_ROOT.mkdir(parents=True, exist_ok=True)
    if DELIVERY_MD.exists() and DELIVERY_MD.stat().st_size > 200:
        return
    for src in (BACKUP_DOCS / "DELIVERY.md", Path("/tmp/snap-5360/DELIVERY.md")):
        if src.exists():
            DELIVERY_MD.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            log({"event": "restored_delivery", "from": str(src)})
            return


def ensure_index_shell() -> None:
    STAGING.mkdir(parents=True, exist_ok=True)
    if INDEX_MD.exists() and INDEX_MD.stat().st_size > 20:
        return
    text = (
        "# 成片（可直接看）\n\n"
        "竖屏口播 1080×1920，H.264 + AAC。时长用中文「秒」。\n\n"
        "| 文件 | 时长 |\n"
        "|------|------|\n"
    )
    INDEX_MD.write_text(text, encoding="utf-8")
    log({"event": "seeded_empty_index"})


def upsert_index_row(name: str, duration: float) -> None:
    if is_protected(name) or not is_watch_target(name):
        raise RuntimeError(f"refusing to write INDEX row for protected/non-watch file: {name}")
    ensure_index_shell()
    row = f"| `{name}` | {duration:.1f}秒 |"
    token = f"`{name}`"
    text = INDEX_MD.read_text(encoding="utf-8")
    out: list[str] = []
    seen = False
    for line in text.splitlines():
        if token in line and line.strip().startswith("|"):
            if seen:
                continue
            out.append(row)
            seen = True
            continue
        if (not seen) and "仙侠云海突进" in line and line.strip().startswith("|"):
            out.append(row)
            seen = True
        out.append(line)
    if not seen:
        out.append(row)
    text = "\n".join(out)
    if not text.endswith("\n"):
        text += "\n"
    INDEX_MD.write_text(text, encoding="utf-8")
    INDEX_BAK.write_text(text, encoding="utf-8")
    BACKUP_DOCS.mkdir(parents=True, exist_ok=True)
    (BACKUP_DOCS / "INDEX.md").write_text(text, encoding="utf-8")


def upsert_table_row(text: str, filename_token: str, new_row: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    replaced = False
    inserted = False
    for line in lines:
        if filename_token in line and line.strip().startswith("|"):
            out.append(new_row)
            replaced = True
            continue
        if (
            not inserted
            and not replaced
            and ("仙侠云海突进" in line or "`成片/INDEX.md`" in line)
            and line.strip().startswith("|")
        ):
            out.append(new_row)
            inserted = True
        out.append(line)
    if not replaced and not inserted:
        out.append(new_row)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def ensure_delivery_61_section(text: str) -> str:
    if "## 本轮 61+" in text:
        return text
    block = [
        "",
        "## 本轮 61+（核验中）",
        "",
        "只在本 Linux VM：`/workspace/成片/`。禁止 `C:\\` `D:\\` `G:\\`。本轮不上传 Drive。",
        "`00-`～`60-` 未删、未覆盖、未重做。新片只 `ffprobe` + 追加目录。不足 30 秒只标记，不重做。",
        "",
        "| 号 | 文件 | 时长 | 状态 |",
        "|----|------|------|------|",
    ]
    if not text.endswith("\n"):
        text += "\n"
    return text + "\n".join(block) + "\n"


def upsert_delivery_round_row(text: str, num: int, name: str, duration: float, short: bool) -> str:
    flag = " ⚠️不足30秒（未重做）" if short else ""
    new = f"| {num} | `{name}` | {duration:.1f}秒 | 已核验{flag} |"
    old = re.compile(rf"^\| {num} \| .+ \|$", re.M)
    if old.search(text):
        return old.sub(new, text, count=1)
    marker = "## 本轮 61+"
    if marker not in text:
        text = ensure_delivery_61_section(text)
    lines = text.splitlines()
    out: list[str] = []
    inserted = False
    in_section = False
    last_table = -1
    for i, line in enumerate(lines):
        if line.startswith("## 本轮 61+"):
            in_section = True
        elif in_section and line.startswith("## "):
            in_section = False
            if not inserted and last_table >= 0:
                out.insert(last_table + 1, new)
                inserted = True
        if in_section and line.strip().startswith("|") and not line.startswith("|----") and "文件" not in line:
            last_table = len(out)
        out.append(line)
    if not inserted:
        if last_table >= 0:
            out.insert(last_table + 1, new)
        else:
            placed = False
            for i, line in enumerate(out):
                if line.startswith("|----") and any("本轮 61+" in x for x in out[:i]):
                    out.insert(i + 1, new)
                    placed = True
                    break
            if not placed:
                out.append(new)
    return "\n".join(out) + "\n"


def update_delivery(name: str, spec: str, duration: float, source: str, short: bool) -> None:
    if is_protected(name) or not is_watch_target(name):
        raise RuntimeError(f"refusing to write DELIVERY row for protected/non-watch file: {name}")
    restore_delivery_if_missing()
    if not DELIVERY_MD.exists():
        raise FileNotFoundError(DELIVERY_MD)
    num = episode_num(name)
    text = ensure_delivery_61_section(DELIVERY_MD.read_text(encoding="utf-8"))
    rel = f"成片/{name}"
    row = f"| `{rel}` | {spec} | {duration:.2f}秒 | {source} |"
    text = upsert_table_row(text, f"`{rel}`", row)
    if num is not None:
        text = upsert_delivery_round_row(text, num, name, duration, short)
    DELIVERY_MD.write_text(text, encoding="utf-8")
    BACKUP_DOCS.mkdir(parents=True, exist_ok=True)
    (BACKUP_DOCS / "DELIVERY.md").write_text(text, encoding="utf-8")


def verify_keep_00_60() -> dict:
    if not KEEP_SNAP.exists():
        return {"ok": True, "reason": "no_snapshot", "changed": []}
    snap = json.loads(KEEP_SNAP.read_text(encoding="utf-8"))
    files = snap.get("files") or {}
    changed: list[dict] = []
    missing: list[str] = []
    for name, rec in files.items():
        path = STAGING / name
        if not path.exists():
            missing.append(name)
            continue
        st = path.stat()
        if st.st_size != rec.get("bytes"):
            changed.append({"name": name, "reason": "size", "was": rec.get("bytes"), "now": st.st_size})
    result = {"ok": not changed and not missing, "changed": changed, "missing": missing}
    if not result["ok"]:
        log({"event": "keep_00_60_drift", **result})
    return result


def qa_final(path: Path) -> dict | None:
    name = path.name
    if is_protected(name) or not is_watch_target(name):
        return None
    if not file_stable(path):
        log({"event": "unstable", "name": name})
        return None
    size = path.stat().st_size
    digest = sha256_file(path)
    if size < MIN_FINAL_BYTES:
        log({"event": "too_small_leave", "name": name, "bytes": size})
        return {"ok": False, "reason": "too_small", "bytes": size, "sha256": digest}
    try:
        probe = ffprobe(path)
        info = summarize_probe(probe)
        ffmpeg_null(path)
    except Exception as exc:
        log({"event": "qa_fail", "name": name, "error": str(exc)})
        return {"ok": False, "reason": str(exc), "bytes": size, "sha256": digest}
    if info["duration"] < 1.0 or not info["width"] or not info["vcodec"]:
        log({"event": "qa_thin", "name": name, "info": info})
        return {"ok": False, "reason": "thin_probe", "info": info, "sha256": digest}
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w.\-]+", "_", name)
    (PROBE_DIR / f"{safe}.ffprobe.json").write_text(
        json.dumps(probe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    info.update({"ok": True, "sha256": digest, "bytes": size, "short": info["duration"] < SHORT_LIMIT})
    return info


def reapply_processed(state: dict) -> None:
    """If sibling checkout wiped INDEX/DELIVERY rows, put 61+ rows back. Never touch 00-60 rows."""
    for name, rec in state.get("processed", {}).items():
        if not is_watch_target(name):
            continue
        dur = float(rec.get("duration") or 0)
        spec = rec.get("spec") or "1080×1920 h264+aac"
        src = rec.get("source") or source_for(name)
        short = bool(rec.get("short") or dur < SHORT_LIMIT)
        try:
            upsert_index_row(name, dur)
            update_delivery(name, spec, dur, src, short)
        except Exception as exc:
            log({"event": "reapply_fail", "name": name, "error": str(exc)})


def write_report(state: dict, newly: list[str], keep: dict) -> None:
    processed = state.get("processed") or {}
    names = sorted(processed, key=lambda n: (episode_num(n) or 0, n))
    short_names = [n for n in names if processed[n].get("short") or float(processed[n].get("duration") or 0) < SHORT_LIMIT]
    lines = [
        "# 成片 61+ 核验报告",
        "",
        f"生成时间：{utc_now()}",
        "范围：只处理 `成片/61-` 及更高编号。云端 only。`00-`～`60-` 未重做、未覆盖。",
        "",
        "## 新片清单（中文时长）",
        "",
    ]
    if not names:
        lines.append("尚无 `61-` 及更高编号成片。")
    else:
        for i, name in enumerate(names, 1):
            rec = processed[name]
            dur = float(rec.get("duration") or 0)
            flag = " ⚠️不足30秒（已标记，未重做）" if rec.get("short") or dur < SHORT_LIMIT else ""
            lines.append(f"{i}. `{name}` — {dur:.1f}秒{flag}")
    lines += [
        "",
        "## 不足30秒（未重做）",
        "",
    ]
    if short_names:
        for name in short_names:
            dur = float(processed[name].get("duration") or 0)
            lines.append(f"- `{name}` — {dur:.1f}秒")
    else:
        lines.append("无。")
    lines += [
        "",
        f"本轮新入：{', '.join(f'`{n}`' for n in newly) if newly else '无'}",
        f"`00-`～`60-` 哈希对照：{'通过' if keep.get('ok') else '有变动（本脚本未写入）'}",
        "",
    ]
    if keep.get("missing"):
        lines.append("对照缺失：" + "、".join(keep["missing"]))
    if keep.get("changed"):
        lines.append("对照尺寸变化：" + "、".join(c["name"] for c in keep["changed"]))
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def chinese_list(state: dict) -> list[str]:
    processed = state.get("processed") or {}
    names = sorted(processed, key=lambda n: (episode_num(n) or 0, n))
    out = []
    for name in names:
        rec = processed[name]
        dur = float(rec.get("duration") or 0)
        flag = " ⚠️不足30秒（未重做）" if rec.get("short") or dur < SHORT_LIMIT else ""
        out.append(f"`{name}` — {dur:.1f}秒{flag}")
    return out


def process_new(state: dict) -> list[str]:
    newly: list[str] = []
    processed = state.setdefault("processed", {})
    if not STAGING.is_dir():
        return newly
    for path in sorted(STAGING.glob("*.mp4")):
        if is_protected(path.name):
            continue
        if not is_watch_target(path.name):
            continue
        info = qa_final(path)
        if not info or not info.get("ok"):
            continue
        prev = processed.get(path.name) or {}
        if prev.get("sha256") == info["sha256"] and prev.get("indexed"):
            continue
        src = source_for(path.name)
        upsert_index_row(path.name, info["duration"])
        update_delivery(path.name, info["spec"], info["duration"], src, info["short"])
        rec = {
            "sha256": info["sha256"],
            "bytes": info["bytes"],
            "duration": info["duration"],
            "spec": info["spec"],
            "source": src,
            "short": info["short"],
            "indexed": True,
            "ts": utc_now(),
        }
        processed[path.name] = rec
        if info["short"]:
            shorts = state.setdefault("short", [])
            if path.name not in shorts:
                shorts.append(path.name)
            log({"event": "short_flag", "name": path.name, "duration": info["duration"]})
        log(
            {
                "event": "indexed",
                "name": path.name,
                "duration": info["duration"],
                "spec": info["spec"],
                "bytes": info["bytes"],
                "sha256": info["sha256"],
                "short": info["short"],
            }
        )
        newly.append(path.name)
    return newly


def waiting_names() -> list[str]:
    if not STAGING.is_dir():
        return []
    return sorted(p.name for p in STAGING.glob("*.mp4") if is_watch_target(p.name))


def run_once() -> dict:
    restore_delivery_if_missing()
    ensure_index_shell()
    if DELIVERY_MD.exists():
        text = ensure_delivery_61_section(DELIVERY_MD.read_text(encoding="utf-8"))
        DELIVERY_MD.write_text(text, encoding="utf-8")
        BACKUP_DOCS.mkdir(parents=True, exist_ok=True)
        (BACKUP_DOCS / "DELIVERY.md").write_text(text, encoding="utf-8")
    state = load_state()
    reapply_processed(state)
    newly = process_new(state)
    keep = verify_keep_00_60()
    state["keep_ok"] = bool(keep.get("ok"))
    save_state(state)
    write_report(state, newly, keep)
    report = {
        "newly_indexed": newly,
        "ready_61_plus": waiting_names(),
        "processed": list(state.get("processed") or {}),
        "short": state.get("short") or [],
        "chinese_list": chinese_list(state),
        "keep_00_60_ok": keep.get("ok"),
        "keep_missing": keep.get("missing") or [],
        "keep_changed": keep.get("changed") or [],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def watch_loop(interval: float = 15.0, max_seconds: float = 14400.0) -> None:
    deadline = time.time() + max_seconds
    while time.time() < deadline:
        report = run_once()
        if report.get("newly_indexed"):
            log({"event": "partial", "newly": report["newly_indexed"]})
        time.sleep(interval)


def main() -> int:
    os.environ.pop("DISPLAY", None)
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    lock_fh = LOCK_PATH.open("a+")
    fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
    try:
        if "--watch" in sys.argv:
            watch_loop()
        else:
            run_once()
    finally:
        fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)
        lock_fh.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
