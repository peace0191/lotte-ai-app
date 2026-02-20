from __future__ import annotations

import os
import re
import streamlit as st

from services.otp_store import can_send, upsert_challenge, verify_code
from services.sms_provider import pick_provider, generate_otp_code
from services.db import upsert_user, audit

st.set_page_config(page_title="📱 휴대폰 인증 로그인", layout="centered")

PHONE_RE = re.compile(r"^\+82\d{9,10}$")  # 예: +821012345678

def normalize_korea_to_e164(raw: str) -> str:
    # 010-1234-5678 / 01012345678 -> +8210...
    digits = re.sub(r"\D+", "", raw)
    if digits.startswith("82"):
        return "+" + digits
    if digits.startswith("0"):
        return "+82" + digits[1:]
    return "+" + digits

st.title("📱 휴대폰 인증 로그인")
st.caption("공급자/관리자 운영모드 로그인(OTP). 운영 전환 시 SMS 공급자(Solapi)를 연결합니다.")

# 세션
if "auth" not in st.session_state:
    st.session_state["auth"] = None

if st.session_state["auth"]:
    st.success(f"로그인됨: {st.session_state['auth']['name']} ({st.session_state['auth']['role']})")
    st.info("사이드바 메뉴로 이동하세요.")
    st.stop()

phone_raw = st.text_input("휴대폰 번호", placeholder="010-1234-5678")
phone = normalize_korea_to_e164(phone_raw) if phone_raw else ""

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("📨 인증번호 발송", use_container_width=True):
        if not phone_raw:
            st.error("휴대폰 번호를 입력해 주세요.")
            st.stop()
        if not PHONE_RE.match(phone):
            st.error("휴대폰 형식이 올바르지 않습니다. 예: 010-1234-5678")
            st.stop()

        ok, reason = can_send(phone)
        if not ok:
            st.warning(reason)
            st.stop()

        code = generate_otp_code()
        upsert_challenge(phone, code)

        provider = pick_provider()
        res = provider.send_otp(phone, code)
        if res.ok:
            st.success("인증번호를 발송했습니다.")
            # DEV 모드에서는 화면에 보여줌 (운영에서는 제거)
            if res.message.startswith("[DEV]"):
                st.info(res.message)
        else:
            st.error(f"발송 실패: {res.message}")

with col2:
    code_in = st.text_input("인증번호(6자리)", placeholder="123456")
    if st.button("✅ 인증하고 로그인", use_container_width=True):
        if not PHONE_RE.match(phone):
            st.error("휴대폰 번호를 먼저 올바르게 입력해 주세요.")
            st.stop()
        if not code_in or len(re.sub(r"\D+", "", code_in)) != 6:
            st.error("인증번호 6자리를 입력해 주세요.")
            st.stop()

        ok, msg = verify_code(phone, re.sub(r"\D+", "", code_in))
        if not ok:
            st.error(msg)
            st.stop()

        # ✅ 역할 부여 정책(운영 기본값)
        # - 관리자 번호는 환경변수로 고정 등록(실서비스에서 관리자 임의가입 방지)
        admin_phones = set(filter(None, (os.environ.get("ADMIN_PHONES", "")).split(",")))
        role = "admin" if phone in admin_phones else "supplier"

        user_id = phone  # phone 자체를 user_id로 사용(중복방지)
        name = "관리자" if role == "admin" else "공급자"
        upsert_user(user_id, name, role)
        audit(user_id, role, "LOGIN_PHONE_OK", property_id="", detail="")

        st.session_state["auth"] = {"user_id": user_id, "name": name, "role": role, "phone": phone}
        st.success("로그인 성공 ✅")
        st.rerun()

st.divider()
st.caption("운영 전환: 환경변수에 SOLAPI_API_KEY, SOLAPI_API_SECRET, SOLAPI_SENDER, OTP_PEPPER, ADMIN_PHONES 설정 필요.")
