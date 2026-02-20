from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Tuple, Dict, Any

from services.assets_store import ensure_property_tree
from services.meta_ops import read_meta, write_meta, ensure_landing_url

def pick_variant(property_id: str) -> str:
    h = hashlib.sha256(property_id.encode("utf-8")).hexdigest()
    return "A" if int(h[-1], 16) % 2 == 0 else "B"

def build_title(property_id: str, meta: Dict[str, Any], variant: str) -> str:
    title = meta.get("title") or f"추천 매물 {property_id}"
    gap = meta.get("market_gap_percent")
    gap_txt = f"{gap}% 저평가" if gap not in (None, "", 0) else "저평가 추천"
    area = meta.get("area_name") or "강남"

    if variant == "A":
        return f"[{area}] {title} | 실거래가 대비 {gap_txt}"
    else:
        return f"{gap_txt} 매물 공개 🔥 | {title} | {area}"

def pick_thumbnail(property_id: str, variant: str) -> str | None:
    paths = ensure_property_tree(property_id)
    # processed_thumbs folder usually created by auto generator
    # We might need to ensure this path exists or check where thumbs actually are.
    # Assuming standard structure: assets/properties/<id>/processed/thumbs/
    thumb_dir = paths.base / "processed" / "thumbs"
    if not thumb_dir.exists():
        # Fallback to base uploads if no processed thumbs
        pass
        
    thumbs = sorted(list(thumb_dir.glob("*.jpg")))
    if not thumbs:
        return None
    # A: 1번, B: 2번(없으면 1번)
    if variant == "B" and len(thumbs) >= 2:
        return str(thumbs[1])
    return str(thumbs[0])

def apply_ab_and_update_meta(property_id: str) -> Dict[str, Any]:
    meta = read_meta(property_id)
    meta = ensure_landing_url(property_id, meta)
    variant = meta.get("yt_variant") or pick_variant(property_id)
    meta["yt_variant"] = variant
    meta["yt_title"] = build_title(property_id, meta, variant)
    write_meta(property_id, meta)
    return meta
