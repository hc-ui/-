#!/usr/bin/env python3
"""Watch /workspace/成片 for 38-53 finals. Cloud only. Keep 00-37. No Drive."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/workspace")
STAGING = ROOT / "成片"
CLOUD_ROOT = ROOT / ".abroll-cloud"
SIDECARS = CLOUD_ROOT / "_sidecars"
STATE_PATH = CLOUD_ROOT / "qa-38-53-state.json"
LOG_PATH = CLOUD_ROOT / "qa-38-53.jsonl"
LOCK_PATH = CLOUD_ROOT / "qa-38-53.lock"
INDEX_MD = STAGING / "INDEX.md"
INDEX_BAK = CLOUD_ROOT / "INDEX.chengpian.md"
DELIVERY_MD = CLOUD_ROOT / "DELIVERY.md"
SCRATCH_DIR = CLOUD_ROOT / "aroll" / "_scratch"
PROBE_DIR = CLOUD_ROOT / "qa" / "38-53"
KEEP_00_19 = SIDECARS / "keep-00-19"
KEEP_20_PLUS = SIDECARS / "keep-20-plus"
KEEP_00_37 = SIDECARS / "keep-00-37"
KEEP_38_53 = SIDECARS / "keep-38-53"
CHENGPIAN_BAK = SIDECARS / "chengpian-bak"
BACKUP_DOCS = Path("/tmp/qa-38-53-backup")

PROTECTED_PREFIXES = tuple(f"{i:02d}-" for i in range(38))
WATCH_RE = re.compile(r"^(3[8-9]|4\d|5[0-3])-.+\.mp4$")
NUMBERED_HYPHEN_RE = re.compile(r"^(\d{2})-.+\.mp4$")
KEEP_EXACT = {"INDEX.md", "仙侠云海突进.mp4"}
MIN_FINAL_BYTES = 550_000
STABLE_SECONDS = 2.5
EXPECTED_NUMS = [f"{i}" for i in range(38, 54)]

KNOWN_00_37 = [
    ("00-深度工作总被打断.mp4", 17.0),
    ("01-口头答应没有截止日.mp4", 12.1),
    ("02-树叶掉了二十秒还没落地.mp4", 14.9),
    ("03-打翻水杯水往天花板流.mp4", 16.5),
    ("04-咖啡自己滑向桌边.mp4", 17.5),
    ("05-先给选项再要决定.mp4", 10.2),
    ("06-先给场景再给方法.mp4", 12.8),
    ("07-演练脚本没有中止口令.mp4", 14.7),
    ("08-工单升级没有时限.mp4", 14.2),
    ("09-值班手机没有备机号.mp4", 14.5),
    ("10-口播别念链接.mp4", 12.1),
    ("11-列表项先给结果.mp4", 13.5),
    ("12-灯亮了房间还是黑的.mp4", 16.4),
    ("13-字典靠名字不是第几个.mp4", 13.7),
    ("14-导师课题毕业就业技术栈自己建.mp4", 14.1),
    ("15-在生医实验室抢测控生态位.mp4", 15.3),
    ("16-工位时间切片15-15-70.mp4", 11.6),
    ("17-从窗台纸鹤拉到地球夜侧.mp4", 12.5),
    ("18-开源小工具涨星靠外发.mp4", 14.7),
    ("19-十二节气先锁十二张首帧.mp4", 11.1),
    ("20-凉咖啡重新冒热气杯壁却结霜.mp4", 16.3),
    ("21-钟指十二东西往上落.mp4", 18.2),
    ("22-松油门车子瞬间停住.mp4", 18.4),
    ("23-说话时嘴前有涟漪.mp4", 19.6),
    ("24-口播结尾别报时长.mp4", 12.0),
    ("25-切镜不要白闪.mp4", 31.1),
    ("26-待办为什么划不掉.mp4", 22.5),
    ("27-三秒留人.mp4", 30.9),
    ("28-杂务别接报销采购.mp4", 11.4),
    ("29-故事没锁不准出提示词.mp4", 12.7),
    ("30-雨滴弹回.mp4", 23.6),
    ("31-贴地冻雨.mp4", 19.2),
    ("32-注视增重.mp4", 22.0),
    ("33-自行车比光快.mp4", 19.8),
    ("34-口播别念屏幕上的字.mp4", 12.8),
    ("34-口播别报时长.mp4", 12.5),
    ("34-口播结尾别报时长.mp4", 12.5),
    ("35-口播别报文件名.mp4", 12.5),
    ("36-别说下一期.mp4", 12.3),
    ("37-组会撞课先摸惯例再书面报备.mp4", 13.2),
]


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
    return {"processed": {}, "moved": [], "protected": {}, "restored": []}


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def scratch_hashes() -> set[str]:
    out: set[str] = set()
    if not SCRATCH_DIR.is_dir():
        return out
    for p in SCRATCH_DIR.glob("*.mp4"):
        try:
            out.add(sha256_file(p))
        except OSError:
            continue
    return out


def unique_dest(name: str) -> Path:
    dest = SIDECARS / name
    if not dest.exists():
        return dest
    stem = Path(name).stem
    suffix = Path(name).suffix
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return SIDECARS / f"{stem}.{stamp}{suffix}"


def is_protected(name: str) -> bool:
    if name in KEEP_EXACT:
        return True
    return name.startswith(PROTECTED_PREFIXES) and name.endswith(".mp4")


def watch_num(name: str) -> str | None:
    m = WATCH_RE.match(name)
    return m.group(1) if m else None


def is_draft(path: Path, scratch: set[str]) -> bool:
    name = path.name
    if is_protected(name) or WATCH_RE.match(name):
        return False
    low = name.lower()
    if path.suffix.lower() in {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".wav",
        ".mp3",
        ".json",
        ".txt",
        ".part",
        ".tmp",
        ".partial",
        ".bak",
        ".ass",
        ".srt",
        ".vtt",
        ".py",
        ".md",
    } and name != "INDEX.md":
        return True
    if any(tok in name for tok in ("封面", "草稿", "preview", "scratch", "concat", "最终成片", "00_封面", "CLAIM")):
        return True
    if re.match(r"^\d{2}_.+\.mp4$", name):
        return True
    if name.endswith(".mp4") and not NUMBERED_HYPHEN_RE.match(name) and name not in KEEP_EXACT:
        return True
    if name.endswith(".mp4"):
        try:
            digest = sha256_file(path)
        except OSError:
            return False
        if digest in scratch:
            return True
    if low.endswith((".mp4.part", ".mp4.tmp")):
        return True
    return False


def file_stable(path: Path) -> bool:
    try:
        s1 = path.stat()
        time.sleep(STABLE_SECONDS)
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
    cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
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


def claim_source(num: str) -> str | None:
    for folder in (CLOUD_ROOT / num, CLOUD_ROOT / f"{num}b"):
        claim = folder / "CLAIM.md"
        if not claim.exists():
            continue
        text = claim.read_text(encoding="utf-8")
        src = ""
        for line in text.splitlines():
            if line.lstrip().startswith("#"):
                continue
            if "来源" in line and "：" in line:
                src = line.split("：", 1)[-1].strip(" -*")
                if src:
                    break
        if not src:
            for line in text.splitlines():
                if line.lstrip().startswith("#"):
                    continue
                if "成片名" in line and "：" in line:
                    src = line.split("：", 1)[-1].strip(" -*`")
                    break
        return f"topic {num} {src}".strip() if src else f"topic {num}"
    return None


def source_for(name: str) -> str:
    num = name[:2] if name[:2].isdigit() else ""
    claim = claim_source(num) if num else None
    return claim or f"topic {num} sibling 成品".strip()


def hardlink_or_copy(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return
    try:
        os.link(src, dest)
    except OSError:
        shutil.copy2(src, dest)


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


def refresh_index_header(text: str, processed: dict) -> str:
    names = sorted(n for n in processed if WATCH_RE.match(n))
    if names:
        first = names[0][:2]
        last = names[-1][:2]
        extra = f"`00-`～`37-` 均已在本目录（未删）。本轮新入 `{first}-`～`{last}-`。"
    else:
        extra = "`00-`～`37-` 均已在本目录（未删）。等待本轮 `38-`～`53-`。"
    if re.search(r"`00-`～`\d{2}-` 均已在本目录[^\n]*", text):
        return re.sub(r"`00-`～`\d{2}-` 均已在本目录[^\n]*", extra, text, count=1)
    return text


def normalize_index_table(text: str) -> str:
    lines = text.splitlines()
    pre: list[str] = []
    file_header = ""
    sep = ""
    rows_00_37: list[str] = []
    rows_38: list[str] = []
    xianxia = ""
    other_rows: list[str] = []
    post: list[str] = []
    stage = "pre"
    seen: set[str] = set()
    for line in lines:
        if stage == "pre":
            if line.startswith("| 文件"):
                file_header = line
                stage = "sep"
            else:
                pre.append(line)
            continue
        if stage == "sep":
            sep = line
            stage = "rows"
            continue
        if stage == "rows":
            if not line.strip().startswith("|"):
                stage = "post"
                post.append(line)
                continue
            token_m = re.search(r"`([^`]+)`", line)
            token = token_m.group(1) if token_m else line
            if token in seen:
                continue
            seen.add(token)
            if "仙侠云海突进" in line:
                xianxia = line
                continue
            num_m = re.search(r"`(\d{2})-", line)
            if num_m and int(num_m.group(1)) < 38:
                rows_00_37.append(line)
            elif num_m:
                rows_38.append(line)
            else:
                other_rows.append(line)
            continue
        post.append(line)
    rows_00_37.sort()
    rows_38.sort()
    out = pre + [file_header, sep] + rows_00_37 + rows_38 + other_rows
    if xianxia:
        out.append(xianxia)
    out.extend(post)
    return "\n".join(out) + "\n"


def upsert_index_row(text: str, name: str, duration: float) -> str:
    row = f"| `{name}` | {duration:.1f}s |"
    token = f"`{name}`"
    out: list[str] = []
    seen = False
    for line in text.splitlines():
        if token in line and line.strip().startswith("|"):
            if seen:
                continue
            out.append(row)
            seen = True
            continue
        if not seen and ("仙侠云海突进" in line) and line.strip().startswith("|"):
            out.append(row)
            seen = True
        out.append(line)
    if not seen:
        out.append(row)
    return normalize_index_table("\n".join(out) + "\n")


def seed_index(processed: dict | None = None) -> None:
    processed = processed or {}
    lines = [
        "# 成片（可直接看）",
        "",
        "竖屏口播 1080×1920，H.264 + AAC。`仙侠云海突进.mp4` 是横屏剧情成片。`00-`～`37-` 均已在本目录（未删）。等待本轮 `38-`～`53-`。",
        "",
        "| 文件 | 时长 |",
        "|------|------|",
    ]
    for name, dur in KNOWN_00_37:
        lines.append(f"| `{name}` | {dur:.1f}s |")
    extra: dict[str, float] = {}
    if INDEX_MD.exists():
        for line in INDEX_MD.read_text(encoding="utf-8").splitlines():
            m = re.search(r"`(\d{2}-.+\.mp4)` \| ([\d.]+)s", line)
            if m and int(m.group(1)[:2]) >= 38:
                extra.setdefault(m.group(1), float(m.group(2)))
    for name, rec in processed.items():
        if WATCH_RE.match(name):
            dur = rec.get("duration") if isinstance(rec, dict) else rec
            if dur is not None:
                extra[name] = float(dur)
    for name in sorted(extra):
        lines.append(f"| `{name}` | {extra[name]:.1f}s |")
    lines.append("| `仙侠云海突进.mp4` | 43.0s |")
    text = refresh_index_header("\n".join(lines) + "\n", {k: True for k in extra})
    STAGING.mkdir(parents=True, exist_ok=True)
    INDEX_MD.write_text(normalize_index_table(text), encoding="utf-8")
    INDEX_BAK.parent.mkdir(parents=True, exist_ok=True)
    INDEX_BAK.write_text(INDEX_MD.read_text(encoding="utf-8"), encoding="utf-8")
    if BACKUP_DOCS.is_dir():
        (BACKUP_DOCS / "INDEX.md").write_text(INDEX_MD.read_text(encoding="utf-8"), encoding="utf-8")


def restore_docs_from_backup() -> None:
    """Sibling git checkout often deletes untracked INDEX/DELIVERY. Put them back."""
    STAGING.mkdir(parents=True, exist_ok=True)
    CLOUD_ROOT.mkdir(parents=True, exist_ok=True)
    if (not INDEX_MD.exists() or "00-深度工作总被打断" not in INDEX_MD.read_text(encoding="utf-8")):
        for src in (INDEX_BAK, BACKUP_DOCS / "INDEX.md"):
            if src.exists() and "00-深度工作总被打断" in src.read_text(encoding="utf-8"):
                INDEX_MD.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
                log({"event": "restored_index_doc", "from": str(src)})
                break
    if not DELIVERY_MD.exists():
        for src in (BACKUP_DOCS / "DELIVERY.md",):
            if src.exists():
                DELIVERY_MD.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
                log({"event": "restored_delivery_doc", "from": str(src)})
                break


def update_index(name: str, duration: float, processed: dict) -> None:
    restore_docs_from_backup()
    if (not INDEX_MD.exists()) or "00-深度工作总被打断" not in INDEX_MD.read_text(encoding="utf-8"):
        seed_index({**processed, name: {"duration": duration}})
    text = INDEX_MD.read_text(encoding="utf-8")
    text = refresh_index_header(text, {**processed, name: True})
    INDEX_MD.write_text(upsert_index_row(text, name, duration), encoding="utf-8")
    INDEX_BAK.write_text(INDEX_MD.read_text(encoding="utf-8"), encoding="utf-8")
    if BACKUP_DOCS.is_dir():
        (BACKUP_DOCS / "INDEX.md").write_text(INDEX_MD.read_text(encoding="utf-8"), encoding="utf-8")


def ensure_delivery_pending(text: str) -> str:
    if "## 本轮 38–53" in text:
        return text
    block = [
        "",
        "## 本轮 38–53（核验中）",
        "",
        "只在本 Linux VM：`/workspace/成片/`。禁止 `C:\\` `D:\\` `G:\\`。本轮不上传 Drive。`00-`～`37-` 未删。",
        "",
        "| 号 | 文件 | 状态 |",
        "|----|------|------|",
    ]
    for num in EXPECTED_NUMS:
        block.append(f"| {num} | — | 待收 |")
    if not text.endswith("\n"):
        text += "\n"
    return text + "\n".join(block) + "\n"


def mark_pending_row(text: str, num: str, name: str, duration: float) -> str:
    old = re.compile(rf"^\| {num} \| .+ \| 待收 \|$", re.M)
    new = f"| {num} | `{name}` | 已核验 {duration:.1f}s |"
    if old.search(text):
        return old.sub(new, text, count=1)
    old2 = re.compile(rf"^\| {num} \| .+ \| 已核验 .+\|$", re.M)
    if old2.search(text):
        return old2.sub(new, text, count=1)
    return text


def update_delivery(name: str, spec: str, duration: float, source: str) -> None:
    restore_docs_from_backup()
    if not DELIVERY_MD.exists():
        raise FileNotFoundError(DELIVERY_MD)
    text = DELIVERY_MD.read_text(encoding="utf-8")
    text = ensure_delivery_pending(text)
    rel = f"成片/{name}"
    row = f"| `{rel}` | {spec} | {duration:.2f}s | {source} |"
    text = upsert_table_row(text, f"`{rel}`", row)
    num = watch_num(name)
    if num:
        text = mark_pending_row(text, num, name, duration)
    verified = len(re.findall(r"\| (?:3[8-9]|4\d|5[0-3]) \| `.+` \| 已核验", text))
    if verified >= 16:
        text = text.replace("## 本轮 38–53（核验中）", "## 本轮 38–53（已核验）")
    DELIVERY_MD.write_text(text, encoding="utf-8")
    if BACKUP_DOCS.is_dir():
        (BACKUP_DOCS / "DELIVERY.md").write_text(text, encoding="utf-8")


def move_draft(path: Path, reason: str) -> Path | None:
    if is_protected(path.name) or WATCH_RE.match(path.name):
        log({"event": "skip_protected", "name": path.name, "reason": reason})
        return None
    SIDECARS.mkdir(parents=True, exist_ok=True)
    dest = unique_dest(path.name)
    shutil.move(str(path), str(dest))
    log({"event": "moved_draft", "from": str(path), "to": str(dest), "reason": reason})
    return dest


def qa_final(path: Path, scratch: set[str]) -> dict | None:
    name = path.name
    if not file_stable(path):
        log({"event": "unstable", "name": name})
        return None
    size = path.stat().st_size
    digest = sha256_file(path)
    if digest in scratch:
        move_draft(path, "identical_to_aroll_scratch")
        return None
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
    if info["duration"] < 3.0 or not info["width"] or not info["vcodec"]:
        log({"event": "qa_thin", "name": name, "info": info})
        return {"ok": False, "reason": "thin_probe", "info": info, "sha256": digest}
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    (PROBE_DIR / f"{name}.ffprobe.json").write_text(
        json.dumps(probe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    info.update({"ok": True, "sha256": digest, "bytes": size})
    return info


def sweep_drafts(scratch: set[str], state: dict) -> list[str]:
    moved: list[str] = []
    if not STAGING.is_dir():
        return moved
    for path in sorted(STAGING.iterdir(), key=lambda p: p.name):
        if not path.is_file():
            continue
        if is_protected(path.name) or WATCH_RE.match(path.name):
            continue
        if is_draft(path, scratch):
            dest = move_draft(path, "accidental_draft_in_staging")
            if dest:
                moved.append(f"{path.name} → {dest.name}")
                state.setdefault("moved", []).append(
                    {"name": path.name, "dest": str(dest), "ts": utc_now()}
                )
    return moved


def restore_from_dir(src_dir: Path, restored: list[str]) -> None:
    if not src_dir.is_dir():
        return
    STAGING.mkdir(parents=True, exist_ok=True)
    for src in sorted(src_dir.iterdir()):
        if not src.is_file() or src.name == "INDEX.md":
            continue
        if not (src.name.endswith(".mp4") or src.name in KEEP_EXACT):
            continue
        dest = STAGING / src.name
        if dest.exists():
            continue
        hardlink_or_copy(src, dest)
        restored.append(src.name)
        log({"event": "restored_sidecar", "name": src.name, "from": str(src)})


def restore_from_projects(restored: list[str]) -> None:
    STAGING.mkdir(parents=True, exist_ok=True)
    if not CLOUD_ROOT.is_dir():
        return
    for folder in sorted(CLOUD_ROOT.iterdir()):
        if not folder.is_dir():
            continue
        m = re.fullmatch(r"(\d{2})b?", folder.name)
        if not m:
            continue
        num = m.group(1)
        for src in folder.glob("00_最终成片_*.mp4"):
            title = src.name[len("00_最终成片_") :]
            dest_name = f"{num}-{title}"
            dest = STAGING / dest_name
            if dest.exists():
                continue
            try:
                digest = sha256_file(src)
                already = False
                for existing in STAGING.glob(f"{num}-*.mp4"):
                    if sha256_file(existing) == digest:
                        already = True
                        break
                if already:
                    continue
            except OSError:
                pass
            hardlink_or_copy(src, dest)
            restored.append(dest_name)
            log({"event": "restored_project_final", "name": dest_name, "from": str(src)})


def restore_protected() -> list[str]:
    restored: list[str] = []
    for src_dir in (KEEP_00_37, KEEP_00_19, KEEP_20_PLUS, KEEP_38_53, CHENGPIAN_BAK):
        restore_from_dir(src_dir, restored)
    restore_from_projects(restored)
    restore_docs_from_backup()
    if INDEX_BAK.exists() and (
        (not INDEX_MD.exists()) or "00-深度工作总被打断" not in INDEX_MD.read_text(encoding="utf-8")
    ):
        STAGING.mkdir(parents=True, exist_ok=True)
        INDEX_MD.write_text(INDEX_BAK.read_text(encoding="utf-8"), encoding="utf-8")
        restored.append("INDEX.md")
        log({"event": "restored_index", "from": str(INDEX_BAK)})
    return restored


def snapshot_keep() -> None:
    KEEP_00_37.mkdir(parents=True, exist_ok=True)
    KEEP_38_53.mkdir(parents=True, exist_ok=True)
    if not STAGING.is_dir():
        return
    for path in STAGING.iterdir():
        if not path.is_file() or not path.name.endswith(".mp4"):
            continue
        if is_protected(path.name):
            dest = KEEP_00_37 / path.name
            if not dest.exists():
                hardlink_or_copy(path, dest)
        elif WATCH_RE.match(path.name):
            dest = KEEP_38_53 / path.name
            if not dest.exists():
                hardlink_or_copy(path, dest)


def snapshot_protected(state: dict) -> None:
    prot: dict[str, dict] = {}
    if STAGING.is_dir():
        for path in STAGING.iterdir():
            if path.is_file() and is_protected(path.name):
                st = path.stat()
                prot[path.name] = {"bytes": st.st_size, "mtime": int(st.st_mtime)}
    state["protected"] = prot
    missing = [f"{i:02d}-" for i in range(38)]
    present_prefixes = {name[:3] for name in prot if name.endswith(".mp4")}
    lost = [p for p in missing if p not in present_prefixes]
    if lost:
        log({"event": "protected_missing", "prefixes": lost})
        state["protected_missing"] = lost
    else:
        state.pop("protected_missing", None)


def process_watch_targets(scratch: set[str], state: dict) -> list[str]:
    newly: list[str] = []
    processed = state.setdefault("processed", {})
    if not STAGING.is_dir():
        return newly
    for path in sorted(STAGING.glob("*.mp4")):
        if not WATCH_RE.match(path.name):
            continue
        info = qa_final(path, scratch)
        if not info or not info.get("ok"):
            continue
        prev = processed.get(path.name) or {}
        if prev.get("sha256") == info["sha256"] and prev.get("indexed"):
            continue
        update_index(path.name, info["duration"], processed)
        update_delivery(path.name, info["spec"], info["duration"], source_for(path.name))
        processed[path.name] = {
            "sha256": info["sha256"],
            "bytes": info["bytes"],
            "duration": info["duration"],
            "spec": info["spec"],
            "indexed": True,
            "ts": utc_now(),
        }
        log(
            {
                "event": "indexed",
                "name": path.name,
                **{k: info[k] for k in ("duration", "spec", "bytes", "sha256")},
            }
        )
        newly.append(path.name)
    return newly


def ready_38_53() -> list[str]:
    names = []
    if not STAGING.is_dir():
        return names
    for path in sorted(STAGING.glob("*.mp4")):
        if WATCH_RE.match(path.name):
            names.append(path.name)
    return names


def ready_kept() -> list[str]:
    names = []
    if not STAGING.is_dir():
        return names
    for path in sorted(STAGING.glob("*.mp4")):
        if NUMBERED_HYPHEN_RE.match(path.name) or path.name == "仙侠云海突进.mp4":
            names.append(path.name)
    return names


def waiting_nums(state: dict) -> list[str]:
    have = {name[:2] for name in state.get("processed", {}) if WATCH_RE.match(name)}
    return [n for n in EXPECTED_NUMS if n not in have]


def run_once() -> dict:
    SIDECARS.mkdir(parents=True, exist_ok=True)
    restore_docs_from_backup()
    scratch = scratch_hashes()
    state = load_state()
    if DELIVERY_MD.exists():
        text = ensure_delivery_pending(DELIVERY_MD.read_text(encoding="utf-8"))
        DELIVERY_MD.write_text(text, encoding="utf-8")
    if (not INDEX_MD.exists()) or "00-深度工作总被打断" not in INDEX_MD.read_text(encoding="utf-8"):
        seed_index(state.get("processed") or {})
    else:
        text = refresh_index_header(INDEX_MD.read_text(encoding="utf-8"), state.get("processed") or {})
        INDEX_MD.write_text(normalize_index_table(text), encoding="utf-8")
        INDEX_BAK.write_text(INDEX_MD.read_text(encoding="utf-8"), encoding="utf-8")
    restored = restore_protected()
    if restored:
        state.setdefault("restored", []).extend({"name": n, "ts": utc_now()} for n in restored)
    snapshot_keep()
    snapshot_protected(state)
    moved = sweep_drafts(scratch, state)
    newly = process_watch_targets(scratch, state)
    snapshot_keep()
    snapshot_protected(state)
    save_state(state)
    waiting = waiting_nums(state)
    report = {
        "newly_indexed": newly,
        "ready_38_53": ready_38_53(),
        "kept_00_37_ok": not state.get("protected_missing"),
        "protected_missing": state.get("protected_missing") or [],
        "waiting_38_53": waiting,
        "moved": moved,
        "restored": restored,
        "all_ready": ready_kept(),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def watch_loop(interval: float = 10.0, max_seconds: float = 7200.0) -> None:
    deadline = time.time() + max_seconds
    while time.time() < deadline:
        report = run_once()
        if not waiting_nums(load_state()):
            log({"event": "watch_complete", "count": 16})
            return
        if report.get("newly_indexed"):
            log({"event": "partial", "newly": report["newly_indexed"]})
        time.sleep(interval)
    log({"event": "watch_timeout", "processed": list(load_state().get("processed", {}))})


def main() -> int:
    os.environ.pop("DISPLAY", None)
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
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
