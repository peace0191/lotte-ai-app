from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from services.assets_store import ensure_property_tree
from services.meta_ops import read_meta

def build_kakao_message(property_id: str, watch_url: str, landing_url: str = "") -> Dict[str, Any]:
    meta = read_meta(property_id)
    title = meta.get("title") or f"추천 매물 ({property_id})"
    address = meta.get("address") or ""
    gap = meta.get("market_gap_percent")
    gap_txt = f"저평가 {gap}%" if gap not in (None, "", 0) else "저평가 추천"

    # landing_url이 없으면 유튜브 링크를 CTA로 사용
    cta = landing_url or watch_url or ""

    msg_lines = [
        f"🏠 {title}",
        f"📍 {address}" if address else "",
        f"🔥 {gap_txt}",
        "",
        "상담/예약은 아래 링크에서 진행해 주세요.",
        cta
    ]
    message = "\n".join([x for x in msg_lines if x])

    return {
        "property_id": property_id,
        "message": message,
        "button": {"title": "상담/예약하기", "url": cta},
        "youtube": {"watch_url": watch_url},
    }

def write_kakao_payload(property_id: str, payload: Dict[str, Any]) -> Path:
    paths = ensure_property_tree(property_id)
    out = paths.publish_kakao / "message_payload.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
