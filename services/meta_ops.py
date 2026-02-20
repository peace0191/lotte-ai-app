"""
services/meta_ops.py
====================
매물 meta.json 읽기/쓰기 + landing_url 자동 주입.

표준 경로: assets/properties/<property_id>/meta.json
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

# ── 내부 서비스 ──────────────────────────────────────────
try:
    from services.config_loader import get_config
except ImportError:
    def get_config():  # type: ignore
        return {}

from services.url_builder import build_property_landing_url

# ── 경로 설정 ─────────────────────────────────────────────
PROPERTIES_ROOT = Path("assets") / "properties"


# ─────────────────────────────────────────────────────────
# 기본 IO
# ─────────────────────────────────────────────────────────

def _meta_path(property_id: str) -> Path:
    return PROPERTIES_ROOT / property_id / "meta.json"


def read_meta(property_id: str) -> Optional[Dict[str, Any]]:
    """meta.json 읽기. 없으면 None 반환."""
    p = _meta_path(property_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_meta(property_id: str, meta: Dict[str, Any]) -> bool:
    """meta.json 저장. 성공 여부 반환."""
    p = _meta_path(property_id)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception as e:
        print(f"[meta_ops] write_meta 실패 ({property_id}): {e}")
        return False


def create_meta(property_id: str, initial: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    새 매물 meta.json 생성 (없을 경우).
    이미 있으면 기존 meta 반환.
    """
    existing = read_meta(property_id)
    if existing is not None:
        return existing

    meta: Dict[str, Any] = {
        "property_id": property_id,
        "created_at": int(time.time()),
        "status": "draft",
    }
    if initial:
        meta.update(initial)

    meta = ensure_landing_url(property_id, meta)
    write_meta(property_id, meta)
    return meta


# ─────────────────────────────────────────────────────────
# landing_url 자동 주입
# ─────────────────────────────────────────────────────────

def ensure_landing_url(property_id: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    meta에 landing_url이 없으면 secrets.toml 설정 기반으로 자동 생성합니다.
    항상 https://도메인/p/<id> 형식.

    secrets.toml 권장 설정:
        [app]
        base_url = "https://your-domain.com"
        detail_path_prefix = "/p"
    """
    if meta.get("landing_url"):
        return meta  # 이미 있으면 그대로

    cfg = get_config()
    # Support both dict styles (flat or nested via app.get)
    # The config_loader likely returns a wrapper or dict
    if hasattr(cfg, "get"):
        app_cfg = cfg.get("app", {})
        if isinstance(app_cfg, dict):
             base_url = app_cfg.get("base_url", "")
             prefix = app_cfg.get("detail_path_prefix", "/p")
        else:
             # Fallback if config isn't nested as expected
             base_url = cfg.get("app.base_url", "")
             prefix = cfg.get("app.detail_path_prefix", "/p")
    else:
        base_url = ""
        prefix = "/p"

    # Also check direct os.environ if needed, but config_loader should handle it.
    
    if not base_url:
        return meta  # base_url 미설정이면 스킵

    url = build_property_landing_url(base_url, property_id, prefix)
    if url:
        meta["landing_url"] = url

    return meta


def refresh_landing_url(property_id: str) -> Optional[str]:
    """
    meta.json을 읽어 landing_url을 재생성하고 저장합니다.
    워커 등에서 발행 후 호출용.

    Returns:
        갱신된 landing_url (문자열) 또는 None
    """
    meta = read_meta(property_id)
    if meta is None:
        return None

    # 강제 재생성: 기존 값 삭제 후 다시 주입
    meta.pop("landing_url", None)
    meta = ensure_landing_url(property_id, meta)

    if meta.get("landing_url"):
        write_meta(property_id, meta)
        return meta["landing_url"]
    return None


# ─────────────────────────────────────────────────────────
# 상태/필드 헬퍼
# ─────────────────────────────────────────────────────────

def update_meta_field(property_id: str, key: str, value: Any) -> bool:
    """특정 필드 하나만 업데이트."""
    meta = read_meta(property_id) or {}
    meta[key] = value
    return write_meta(property_id, meta)


def get_meta_field(property_id: str, key: str, default: Any = None) -> Any:
    """특정 필드 값만 반환."""
    meta = read_meta(property_id) or {}
    return meta.get(key, default)


def list_all_property_ids() -> list[str]:
    """assets/properties/ 아래 모든 매물 ID 목록 반환."""
    root = PROPERTIES_ROOT
    if not root.exists():
        return []
    ids = [d.name for d in root.iterdir() if d.is_dir() and (d / "meta.json").exists()]
    return sorted(ids)
