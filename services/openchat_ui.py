"""
services/openchat_ui.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
롯데타워 시그니엘 오픈채팅방 UI 컴포넌트
- header_bg()   : 배경 이미지 헤더
- qr_png_bytes(): QR코드 PNG 생성
- openchat_block(): 오픈채팅 바로가기 풀 UI 블록
"""
from __future__ import annotations
import base64
from io import BytesIO
from pathlib import Path

import streamlit as st


def _img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def header_bg(
    image_path: str,
    height_px: int = 240,
    title: str = "",
    subtitle: str = "",
):
    """상단 배경 이미지 헤더 (로그인 화면 최상단)"""
    if not Path(image_path).exists():
        # 이미지 없을 때 그라디언트 폴백
        st.markdown(
            f"""
            <div style="
                width:100%; height:{height_px}px; border-radius:18px;
                background:linear-gradient(135deg,#0b1a37,#1a3a5f,#0f172a);
                display:flex; align-items:flex-end; padding:20px 24px;
                box-shadow:0 10px 30px rgba(0,0,0,.35); margin-bottom:18px;
            ">
              <div>
                <div style="color:#fcd34d; font-size:22px; font-weight:800;">{title}</div>
                <div style="color:#94a3b8; font-size:14px; margin-top:6px;">{subtitle}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    b64 = _img_to_base64(image_path)
    ext = Path(image_path).suffix.lstrip(".").lower()
    mime = "jpeg" if ext in ("jpg", "jpeg") else "png"
    st.markdown(
        f"""
        <div style="
            position:relative; width:100%; height:{height_px}px;
            border-radius:18px; overflow:hidden; margin-bottom:18px;
            box-shadow:0 10px 30px rgba(0,0,0,.35);
        ">
          <img src="data:image/{mime};base64,{b64}" style="
              width:100%; height:100%; object-fit:cover;
              filter:saturate(1.08) brightness(0.88);
          "/>
          <div style="
              position:absolute; inset:0;
              background:linear-gradient(105deg, rgba(0,0,0,.75) 0%, rgba(0,0,0,.20) 100%);
          "></div>
          <div style="
              position:absolute; left:22px; bottom:18px; right:22px;
              color:white;
          ">
            <div style="font-size:21px; font-weight:800; line-height:1.25;
                        text-shadow:0 2px 8px rgba(0,0,0,.7);">{title}</div>
            <div style="font-size:13px; opacity:.92; margin-top:7px;
                        text-shadow:0 1px 4px rgba(0,0,0,.6);">{subtitle}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def qr_png_bytes(data: str) -> bytes | None:
    """QR코드 PNG 바이트 반환 (qrcode 없으면 None)"""
    try:
        import qrcode
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1a1a2e", back_color="white")
        bio = BytesIO()
        img.save(bio, format="PNG")
        return bio.getvalue()
    except ImportError:
        return None


def openchat_block(
    openchat_url: str = "https://open.kakao.com/o/gWHRpdji",
    card_image_path: str | None = None,
    title: str = "💬 오픈채팅방 바로가기",
    desc: str = "시그니엘 레지던스 매매·임대 | 실거래 기반 상담 · 급매/급임대 우선 공유",
):
    """오픈채팅 풀 UI 블록: 카드이미지 + 버튼 + QR"""
    st.markdown(f"#### {title}")
    st.caption(desc)

    left, right = st.columns([1.3, 1.0], gap="medium")

    with left:
        # 카드 이미지
        if card_image_path and Path(card_image_path).exists():
            st.image(card_image_path, use_container_width=True)
        else:
            # 이미지 없을 때 텍스트 카드 대체
            st.markdown("""
            <div style="background:linear-gradient(135deg,#0b1a37,#1e3a5f);
                        border-radius:14px; padding:24px 20px; color:white; text-align:center;">
                <div style="font-size:1.1rem; font-weight:800; color:#fcd34d; margin-bottom:12px;">
                    🏙️ 롯데타워 시그니엘 레지던스
                </div>
                <div style="font-size:0.85rem; color:#e2e8f0; line-height:2.0;">
                    ✅ 실거래/호가 흐름 브리핑<br>
                    ✅ 급매/급임대 실매물 우선 공유<br>
                    ✅ 조건 맞춤(층·향·타입) 추천<br>
                    ✅ VIP 비공개 매물 별도 안내
                </div>
                <div style="margin-top:16px; font-size:0.78rem; color:#94a3b8;">
                    롯데타워앤강남빌딩부동산중개(주)<br>
                    대표 공인중개사 이상수<br>
                    ☎ 02-578-8285 / 010-8985-8945
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        # 카카오 오픈채팅 버튼
        st.markdown(
            f"""
            <a href="{openchat_url}" target="_blank" style="text-decoration:none;">
              <div style="
                background:#FEE500; color:#111; font-size:1rem;
                font-weight:800; text-align:center; padding:16px 12px;
                border-radius:14px; box-shadow:0 6px 18px rgba(254,229,0,.45);
                transition:all .2s;
              ">
                🟡 카카오 오픈채팅방 바로가기
              </div>
            </a>
            """,
            unsafe_allow_html=True,
        )
        st.caption("상담 · 급매·급임대 우선 공유 · VIP 비공개 매물")

    with right:
        st.markdown("**📱 QR로 바로 입장**")
        qr = qr_png_bytes(openchat_url)
        if qr:
            st.image(qr, caption="스캔 → 오픈채팅방 바로 이동", use_container_width=True)
        else:
            # qrcode 없을 때 URL 박스로 대체
            st.markdown(f"""
            <div style="background:#f8fafc; border:2px solid #FEE500;
                        border-radius:12px; padding:20px; text-align:center;">
                <div style="font-size:3rem; margin-bottom:8px;">📷</div>
                <div style="font-size:0.8rem; color:#64748b; margin-bottom:12px;">
                    QR 생성을 위해 qrcode 라이브러리 설치 필요<br>
                    <code>pip install qrcode[pil]</code>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**🔗 채팅방 URL 복사**")
        st.code(openchat_url, language="text")

        st.markdown("""
        <div style="background:#fff9c4; border-radius:10px; padding:12px 14px;
                    font-size:0.82rem; color:#78350f; margin-top:8px; border:1px solid #FEE500;">
            <b>방 이름 추천</b><br>
            ① 롯데월드타워 시그니엘 레지던스 실거래·임대상담 (공식)<br>
            ② 시그니엘 레지던스 매매·임대 | 실거래 기반 상담방<br>
            ③ 롯데타워 시그니엘 레지던스 전문 | VIP 실매물 상담
        </div>
        """, unsafe_allow_html=True)
