from __future__ import annotations
import random
import time
from dataclasses import dataclass

@dataclass
class OTPState:
    phone: str = ""
    name: str = ""
    code: str = ""
    sent_at: float = 0.0

def generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"

def send_otp_demo(state: OTPState) -> OTPState:
    """데모용: 실제 SMS 대신 코드만 생성(화면에 표시)"""
    state.code = generate_otp()
    state.sent_at = time.time()
    return state

def verify_otp(state: OTPState, user_code: str, ttl_sec: int = 180) -> bool:
    if not state.code:
        return False
    if time.time() - state.sent_at > ttl_sec:
        return False
    return user_code.strip() == state.code
