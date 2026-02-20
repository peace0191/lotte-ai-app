from __future__ import annotations

import base64
import os
import random
import re
from dataclasses import dataclass
from typing import Protocol

import requests


@dataclass
class SmsSendResult:
    ok: bool
    message: str


class SmsProvider(Protocol):
    def send_otp(self, phone_e164: str, code: str) -> SmsSendResult: ...


def generate_otp_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def e164_to_kr_digits(phone_e164: str) -> str:
    """
    +821012345678 -> 01012345678
    Solapi 가이드에서 수신/발신번호는 특수문자 없이 숫자만 요청 권장.
    """
    p = re.sub(r"\D+", "", phone_e164)
    if p.startswith("82"):
        p = "0" + p[2:]
    return p


class DevConsoleProvider:
    def send_otp(self, phone_e164: str, code: str) -> SmsSendResult:
        return SmsSendResult(True, f"[DEV] OTP to {phone_e164}: {code}")


class SolapiProvider:
    """
    SOLAPI 메시지 발송: POST https://api.solapi.com/messages/v4/send
    인증: API Key/Secret 기반 Authorization 헤더 사용
    """
    def __init__(self):
        self.api_key = os.environ.get("SOLAPI_API_KEY", "").strip()
        self.api_secret = os.environ.get("SOLAPI_API_SECRET", "").strip()
        self.sender = os.environ.get("SOLAPI_SENDER", "").strip()
        self.endpoint = "https://api.solapi.com/messages/v4/send"

    def _auth_header(self) -> str:
        if not (self.api_key and self.api_secret):
            raise RuntimeError("SOLAPI_API_KEY / SOLAPI_API_SECRET 환경변수가 필요합니다.")
        token = base64.b64encode(f"{self.api_key}:{self.api_secret}".encode("utf-8")).decode("utf-8")
        return f"Basic {token}"

    def send_otp(self, phone_e164: str, code: str) -> SmsSendResult:
        if not self.sender:
            return SmsSendResult(False, "SOLAPI_SENDER(발신번호)가 설정되지 않았습니다.")
        to_digits = e164_to_kr_digits(phone_e164)
        from_digits = re.sub(r"\D+", "", self.sender)
        if not to_digits or not from_digits:
            return SmsSendResult(False, "수신/발신번호 형식이 올바르지 않습니다.")

        text = f"[롯데타워AI] 인증번호는 {code} 입니다. (5분 이내 입력)"

        payload = {
            "message": {
                "to": to_digits,
                "from": from_digits,
                "text": text,
            }
        }

        try:
            r = requests.post(
                self.endpoint,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": self._auth_header(),
                },
                json=payload,
                timeout=10,
            )
            if 200 <= r.status_code < 300:
                return SmsSendResult(True, "SMS 발송 성공")
            return SmsSendResult(False, f"SMS 발송 실패({r.status_code}): {r.text[:300]}")
        except requests.RequestException as e:
            return SmsSendResult(False, f"SMS 발송 예외: {e}")


def pick_provider() -> SmsProvider:
    # ✅ 운영: Solapi 키가 있으면 Solapi, 아니면 DEV
    if os.environ.get("SOLAPI_API_KEY") and os.environ.get("SOLAPI_API_SECRET") and os.environ.get("SOLAPI_SENDER"):
        return SolapiProvider()
    return DevConsoleProvider()
