from __future__ import annotations
from pathlib import Path
import pandas as pd

# Define path relative to where this script is run (likely root or pages)
# We assume this file is in services/excel_loader.py, so we look for ../data/properties.xlsx if run from services
# But typically we run from root. Let's use absolute path logic or relative to project root.
import os

# Robust path finding
BASE_DIR = Path(__file__).resolve().parent.parent
EXCEL_PATH = BASE_DIR / "data" / "properties.xlsx"

REQUIRED_COLS = [
    "id", "section", "title", "price", "area_py",
    "tags", "video_url", "description",
    "active", "rank"
]

def _split_semicolon(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return []
    s = str(v).strip()
    if not s:
        return []
    return [x.strip() for x in s.split(";") if x.strip()]


def _normalize_youtube_url(url: str) -> str:
    if not url: return ""
    # 1. Shorts -> Watch
    if "/shorts/" in url:
        return url.replace("/shorts/", "/watch?v=")
    # 2. youtu.be -> Watch (Standardization)
    if "youtu.be/" in url:
        # https://youtu.be/ID -> https://www.youtube.com/watch?v=ID
        vid_id = url.split("youtu.be/")[1].split("?")[0]
        return f"https://www.youtube.com/watch?v={vid_id}"
    return url

def load_properties_from_excel(path: Path = EXCEL_PATH) -> list[dict]:
    if not path.exists():
        # Fallback to empty list or verify if json exists? 
        # For now, just raise if missing as per instructions
        raise FileNotFoundError(f"엑셀 파일이 없습니다: {path}")

    df = pd.read_excel(path, sheet_name=0)
    # Normalize column names
    df.columns = [str(c).strip() for c in df.columns]

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"엑셀 필수 컬럼 누락: {missing}")

    df = df.fillna("")

    items: list[dict] = []
    for _, r in df.iterrows():
        # Basic validation
        rid = str(r["id"]).strip()
        if not rid: 
            continue
            
        item = {
            "id": rid,
            "section": str(r["section"]).strip() or "기타",
            "title": str(r["title"]).strip(),
            "price": str(r["price"]).strip(),
            "area_py": str(r["area_py"]).strip(),

# ...

            "tags": _split_semicolon(r["tags"]),
            "video_url": _normalize_youtube_url(str(r["video_url"]).strip()),
            "description": str(r["description"]).strip(),
            "active": str(r["active"]).strip().upper(),
            "rank": float(r["rank"]) if pd.notna(r["rank"]) and str(r["rank"]).strip() else 999.0
        }
        # Copy 'title' to 'name' for backward compatibility if needed, but dashboard uses 'title' now.
        # Actually existing code uses 'name'. The new dashboard code provided uses 'title'.
        # Let's ensure compatibility just in case.
        item["name"] = item["title"] 
        # Also 'spec' was used in old code. New code uses 'area_py' string in meta.
        # Let's create 'spec' for legacy compatibility? 
        # Old spec: "89평 · 1억 / 1,700만 · 프리미엄"
        # New dashboard constructs it from area_py. 
        # But other pages might use 'spec'.
        item["spec"] = f"{item['area_py']}평 · {item['price']}"

        items.append(item)
    return items
