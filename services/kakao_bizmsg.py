"""
services/kakao_bizmsg.py
========================
카카오 BizMessage(알림톡) 발송 서비스.

흐름: OAuth 2.0 토큰 발급(캐시) → 알림톡 발송
      ※ 정보성 메시지 가이드 준수 필수

secrets.toml 설정:
    [kakao_bizmsg]
    base_url      = "bizmsg-web.kakaoenterprise.com"
    client_id     = "..."
    client_secret = "..."
    sender_key    = "..."           # 발신 프로필 키
    sender_no     = "021112222"     # 발신 대표번호
    template_review  = "TPL_REVIEW_001"
    template_approve = "TPL_APPROVE_001"
    template_reserve = "TPL_RESERVE_001"
    fallback_yn   = false           # SMS 대체발송 여부
"""
from __future__ import annotations

import base64
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests

try:
    from services.config_loader import get_config
except ImportError:
    def get_config():  # type: ignore
        return {}

# ── 토큰 캐시 경로 ────────────────────────────────────────
TOKEN_CACHE = Path("assets/system/keys/kakao_bizmsg_token.json")

# ── 전화번호 정규화 ───────────────────────────────────────
_PHONE_DIGITS = re.compile(r"\D+")


def _digits(phone: str) -> str:
    """전화번호에서 숫자만 추출."""
    return _PHONE_DIGITS.sub("", phone or "")


def _to_82(phone: str) -> str:
    """
    국내 전화번호를 카카오 API 요구 형식(82 시작)으로 변환.
    예) "010-1234-5678" → "821012345678"
    """
    d = _digits(phone)
    if d.startswith("82"):
        return d
    if d.startswith("0"):
        return "82" + d[1:]
    return "82" + d


# ─────────────────────────────────────────────────────────
# 설정 로더
# ─────────────────────────────────────────────────────────

def _cfg() -> Dict[str, Any]:
    cfg = get_config()
    # secrets.toml의 [kakao_bizmsg] 섹션 읽기 (dot notation 또는 dict)
    def _get(key: str, default: Any = "") -> Any:
        dot_key = f"kakao_bizmsg.{key}"
        # Only try dot access if cfg behaves that way, otherwise manually dig
        val = cfg.get(dot_key)
        if val is not None:
             return val

        section = cfg.get("kakao_bizmsg", {})
        if isinstance(section, dict):
            return section.get(key, default)
        
        # Fallback if config isn't loaded correctly
        return default

    return {
        "base_url":      _get("base_url",      "bizmsg-web.kakaoenterprise.com"),
        "client_id":     _get("client_id",     ""),
        "client_secret": _get("client_secret", ""),
        "sender_key":    _get("sender_key",    ""),
        "sender_no":     _get("sender_no",     ""),
        "fallback_yn":   bool(_get("fallback_yn", False)),
        # 템플릿 코드들
        "template_review":  _get("template_review",  ""),
        "template_approve": _get("template_approve", ""),
        "template_reserve": _get("template_reserve", ""),
    }


# ─────────────────────────────────────────────────────────
# 토큰 캐시 (파일 기반)
# ─────────────────────────────────────────────────────────

def _load_token() -> Optional[Dict[str, Any]]:
    if not TOKEN_CACHE.exists():
        return None
    try:
        return json.loads(TOKEN_CACHE.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save_token(tok: Dict[str, Any]) -> None:
    TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_CACHE.write_text(
        json.dumps(tok, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ─────────────────────────────────────────────────────────
# OAuth 2.0 토큰 발급
# ─────────────────────────────────────────────────────────

def get_access_token(force_refresh: bool = False) -> str:
    """
    OAuth 2.0 client_credentials 방식으로 액세스 토큰을 발급합니다.
    유효한 캐시가 있으면 재사용합니다.

    Args:
        force_refresh: True이면 캐시 무시하고 강제 재발급

    Returns:
        str: access_token

    Raises:
        RuntimeError: 키 미설정 또는 API 오류
    """
    cfg = _cfg()
    if not cfg["client_id"] or not cfg["client_secret"]:
        raise RuntimeError(
            "[kakao_bizmsg] secrets.toml의 kakao_bizmsg.client_id / client_secret이 설정되지 않았습니다."
        )

    # 캐시 확인
    if not force_refresh:
        cached = _load_token()
        now = int(time.time())
        if cached and cached.get("access_token") and int(cached.get("expires_at", 0)) > now + 60:
            return cached["access_token"]

    # 신규 발급
    url = f"https://{cfg['base_url']}/v2/oauth/token"
    basic = base64.b64encode(
        f"{cfg['client_id']}:{cfg['client_secret']}".encode("utf-8")
    ).decode("utf-8")

    resp = requests.post(
        url,
        headers={
            "accept": "*/*",
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
        timeout=10,
    )

    if resp.status_code >= 300:
        raise RuntimeError(
            f"[kakao_bizmsg] OAuth 토큰 발급 실패 (HTTP {resp.status_code}): {resp.text[:300]}"
        )

    data = resp.json()
    access_token = data.get("access_token")
    expires_in   = int(data.get("expires_in", 3600))

    if not access_token:
        raise RuntimeError(f"[kakao_bizmsg] 응답에 access_token 없음: {data}")

    _save_token({
        "access_token": access_token,
        "expires_at": int(time.time()) + expires_in,
    })
    return access_token


# ─────────────────────────────────────────────────────────
# 알림톡 발송
# ─────────────────────────────────────────────────────────

def send_alimtalk(
    template_code: str,
    phone: str,
    message: str,
    cid: str,
) -> Dict[str, Any]:
    """
    카카오 알림톡을 발송합니다.

    ⚠️  정보성 메시지 범위 준수 필수:
        예약확인 / 검수결과 / 승인알림 / 결제완료 등 즉시성 정보만 허용.
        광고·홍보성 메시지는 사용 불가.

    Args:
        template_code : 카카오 채널에서 승인된 템플릿 코드
        phone         : 수신자 전화번호 (국내 형식 모두 허용)
        message       : 템플릿에 맞는 메시지 본문
        cid           : 요청 고유 ID (중복 발송 방지용)

    Returns:
        dict: 카카오 API 응답 JSON

    Raises:
        RuntimeError: 토큰 오류 또는 발송 실패
    """
    cfg   = _cfg()
    token = get_access_token()

    url = f"https://{cfg['base_url']}/v2/send/kakao"
    payload = {
        "message_type": "AT",
        "sender_key":   cfg["sender_key"],
        "cid":          cid,
        "template_code": template_code,
        "phone_number": _to_82(phone),
        "sender_no":    cfg["sender_no"],
        "message":      message,
        "fall_back_yn": cfg["fallback_yn"],
    }

    resp = requests.post(
        url,
        headers={
            "accept": "*/*",
            "authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=10,
    )

    if resp.status_code >= 300:
        raise RuntimeError(
            f"[kakao_bizmsg] 알림톡 발송 실패 (HTTP {resp.status_code}): {resp.text[:300]}"
        )

    return resp.json()


# ─────────────────────────────────────────────────────────
# 이벤트별 편의 함수 (정보성 메시지만)
# ─────────────────────────────────────────────────────────

def notify_review_requested(
    admin_phone: str,
    property_id: str,
    supplier_id: str,
    landing_url: str = "",
) -> Optional[Dict[str, Any]]:
    """검수 요청 → 관리자에게 알림톡 발송."""
    cfg = _cfg()
    tpl = cfg.get("template_review", "")
    if not tpl:
        # print("[kakao_bizmsg] template_review 미설정, 알림톡 스킵")
        return None

    msg = (
        f"[검수 요청]\n"
        f"매물ID: {property_id}\n"
        f"공급자: {supplier_id}\n"
        f"확인: {landing_url}"
    )
    cid = f"review-{property_id}-{int(time.time())}"
    return send_alimtalk(tpl, admin_phone, msg, cid)


def notify_approved(
    supplier_phone: str,
    property_id: str,
    landing_url: str = "",
) -> Optional[Dict[str, Any]]:
    """승인 완료 → 공급자에게 알림톡 발송."""
    cfg = _cfg()
    tpl = cfg.get("template_approve", "")
    if not tpl:
        # print("[kakao_bizmsg] template_approve 미설정, 알림톡 스킵")
        return None

    msg = (
        f"[승인 완료]\n"
        f"매물ID: {property_id}\n"
        f"승인 처리가 완료되어 발행 큐에 등록되었습니다.\n"
        f"상세 확인: {landing_url}"
    )
    cid = f"approve-{property_id}-{int(time.time())}"
    return send_alimtalk(tpl, supplier_phone, msg, cid)


def notify_reservation_confirmed(
    customer_phone: str,
    property_id: str,
    visit_datetime: str = "",
    landing_url: str = "",
) -> Optional[Dict[str, Any]]:
    """예약 확정 → 고객에게 알림톡 발송 (정보성)."""
    cfg = _cfg()
    tpl = cfg.get("template_reserve", "")
    if not tpl:
        # print("[kakao_bizmsg] template_reserve 미설정, 알림톡 스킵")
        return None

    msg = (
        f"[예약 확정]\n"
        f"매물ID: {property_id}\n"
        f"방문 일시: {visit_datetime}\n"
        f"상세 확인: {landing_url}"
    )
    cid = f"reserve-{property_id}-{int(time.time())}"
    return send_alimtalk(tpl, customer_phone, msg, cid)
