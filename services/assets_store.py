from __future__ import annotations

import re
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


ASSETS_DIR = Path("assets")
PROPERTIES_DIR = ASSETS_DIR / "properties"

PROPERTY_ID_RE = re.compile(r"^P(\d{4})_(\d{6})$")


@dataclass(frozen=True)
class PropertyPaths:
    property_id: str
    base: Path
    meta_json: Path
    raw_photos: Path
    raw_videos: Path
    raw_docs: Path
    processed_photos: Path
    processed_videos: Path
    processed_thumbs: Path
    publish_youtube: Path
    publish_kakao: Path
    publish_sns: Path
    logs: Path


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_property_paths(property_id: str) -> PropertyPaths:
    base = PROPERTIES_DIR / property_id
    return PropertyPaths(
        property_id=property_id,
        base=base,
        meta_json=base / "meta.json",
        raw_photos=base / "raw" / "photos",
        raw_videos=base / "raw" / "videos",
        raw_docs=base / "raw" / "docs",
        processed_photos=base / "processed" / "photos",
        processed_videos=base / "processed" / "videos",
        processed_thumbs=base / "processed" / "thumbs",
        publish_youtube=base / "publish" / "youtube",
        publish_kakao=base / "publish" / "kakao",
        publish_sns=base / "publish" / "sns",
        logs=base / "logs",
    )


def ensure_property_tree(property_id: str) -> PropertyPaths:
    paths = get_property_paths(property_id)
    ensure_dir(paths.base)
    ensure_dir(paths.raw_photos)
    ensure_dir(paths.raw_videos)
    ensure_dir(paths.raw_docs)
    ensure_dir(paths.processed_photos)
    ensure_dir(paths.processed_videos)
    ensure_dir(paths.processed_thumbs)
    ensure_dir(paths.publish_youtube)
    ensure_dir(paths.publish_kakao)
    ensure_dir(paths.publish_sns)
    ensure_dir(paths.logs)
    return paths


def list_property_ids() -> List[str]:
    if not PROPERTIES_DIR.exists():
        return []
    ids = []
    for d in PROPERTIES_DIR.iterdir():
        if d.is_dir() and PROPERTY_ID_RE.match(d.name):
            ids.append(d.name)
    return sorted(ids)


def _parse_property_id(pid: str) -> Optional[Tuple[int, int]]:
    m = PROPERTY_ID_RE.match(pid)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def generate_new_property_id(year: Optional[int] = None) -> str:
    if year is None:
        year = datetime.now().year
    ensure_dir(PROPERTIES_DIR)

    max_seq = 0
    for pid in list_property_ids():
        parsed = _parse_property_id(pid)
        if not parsed:
            continue
        y, seq = parsed
        if y == year:
            max_seq = max(max_seq, seq)

    next_seq = max_seq + 1
    return f"P{year}_{next_seq:06d}"


def safe_filename(name: str) -> str:
    # Windows/Unix safe: keep alnum, dot, dash, underscore; replace others with underscore
    name = name.strip().replace(" ", "_")
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    name = re.sub(r"_+", "_", name)
    return name[:180] if len(name) > 180 else name


def save_uploaded_bytes(dst_path: Path, data: bytes, overwrite: bool = False) -> Path:
    ensure_dir(dst_path.parent)
    if dst_path.exists() and not overwrite:
        # dedupe by adding _001 style suffix
        stem = dst_path.stem
        suffix = dst_path.suffix
        i = 1
        while True:
            candidate = dst_path.with_name(f"{stem}_{i:03d}{suffix}")
            if not candidate.exists():
                dst_path = candidate
                break
            i += 1
    dst_path.write_bytes(data)
    return dst_path


def read_meta(paths: PropertyPaths) -> dict:
    if paths.meta_json.exists():
        try:
            return json.loads(paths.meta_json.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def write_meta(paths: PropertyPaths, meta: dict) -> None:
    meta = dict(meta or {})
    meta.setdefault("property_id", paths.property_id)
    paths.meta_json.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
