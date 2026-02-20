"""
services/url_builder.py
=======================
매물 상세 고정 URL 생성 유틸리티.
항상 https://도메인/p/<property_id> 형식으로 반환합니다.

사용법:
    from services.url_builder import build_property_landing_url
    url = build_property_landing_url(base_url, "P2025_000001")
    # → "https://your-domain.com/p/P2025_000001"
"""
from __future__ import annotations


def build_property_landing_url(
    base_url: str,
    pid: str,
    prefix: str = "/p",
) -> str:
    """
    매물 상세 고정 URL을 생성합니다.

    Args:
        base_url : 앱의 기본 URL (예: "https://your-domain.com")
        pid      : 매물 ID (예: "P2025_000001")
        prefix   : 상세 경로 프리픽스 (기본값: "/p")

    Returns:
        str: 완성된 URL (예: "https://your-domain.com/p/P2025_000001")
    """
    base = (base_url or "").rstrip("/")
    pref = (prefix or "/p").rstrip("/")
    pid  = (pid or "").strip()

    if not base or not pid:
        return ""

    return f"{base}{pref}/{pid}"


def extract_pid_from_landing_url(landing_url: str, prefix: str = "/p") -> str:
    """
    landing_url에서 매물 ID를 역추출합니다.

    Args:
        landing_url : 전체 URL (예: "https://your-domain.com/p/PROP_001")
        prefix      : 상세 경로 프리픽스 (기본값: "/p")

    Returns:
        str: 매물 ID (예: "PROP_001"), 파싱 실패 시 ""
    """
    url = (landing_url or "").strip()
    pref = (prefix or "/p").rstrip("/") + "/"
    idx = url.find(pref)
    if idx < 0:
        return ""
    tail = url[idx + len(pref):]
    # '/' 이후 쿼리스트링 등 제거
    return tail.split("/")[0].split("?")[0].split("#")[0].strip()
