"""
services/kakao_share.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
카카오 JavaScript SDK 기반 "진짜 공유 버튼" 컴포넌트
- 운영 시: st.secrets["KAKAO_JS_KEY"] + st.secrets["KAKAO_THUMB_URL"] 필요
- 테스트 시: 일반 링크 버튼 폴백 자동 작동
"""
import streamlit as st
import streamlit.components.v1 as components

# ── 운영값 상수 ──────────────────────────────────
OPENCHAT_URL = "https://open.kakao.com/o/gWHRpdji"
OFFICE_NAME  = "롯데타워앤강남빌딩부동산중개(주)"
CEO_NAME     = "이상수"

# GitHub Raw URL (프로젝트 push 후 사용 가능)
# 아래 값은 실제 올라간 뒤 확정 — secrets로도 덮어쓸 수 있음
_GITHUB_RAW_FALLBACK = (
    "https://raw.githubusercontent.com/peace0191/lotte-ai-app"
    "/main/assets/openchat_card.png"
)


def _get_secrets(key: str, default: str = "") -> str:
    """st.secrets 또는 환경 변수에서 값 읽기"""
    try:
        return st.secrets.get(key, default)
    except Exception:
        import os
        return os.getenv(key, default)


def kakao_share_button(
    js_key: str,
    button_id: str,
    title: str,
    description: str,
    image_url: str,
    link_url: str,
    button_title: str = "오픈채팅방 바로가기",
    height: int = 110,
):
    """
    Kakao SDK createDefaultButton() 공유 버튼
    - image_url: 반드시 외부에서 접근 가능한 이미지 URL
    - link_url: 공유 눌렀을 때 이동할 URL (오픈채팅)
    """
    html = f"""
    <div style="display:flex;justify-content:center;align-items:center;padding:8px 0;">
      <a id="{button_id}" href="javascript:;" style="
        display:inline-flex; align-items:center; gap:8px;
        background:#FEE500; color:#111; font-weight:800;
        padding:14px 22px; border-radius:14px; text-decoration:none;
        font-size:15px; box-shadow:0 6px 18px rgba(254,229,0,.45);
        cursor:pointer;
      ">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="#111">
          <path d="M12 3c-4.963 0-9 3.147-9 7.031 0 2.49 1.636 4.688 4.107 5.978L6 20l4.872-3.257C11.243 16.907 11.619 17 12 17c4.963 0 9-3.147 9-7-0-3.884-4.037-7-9-7z"/>
        </svg>
        🟡 카카오톡으로 공유하기
      </a>
    </div>

    <script src="https://t1.kakaocdn.net/kakao_js_sdk/2.7.2/kakao.min.js"
            crossorigin="anonymous"></script>
    <script>
      (function() {{
        function initShare() {{
          if (!window.Kakao) {{ return; }}
          if (!Kakao.isInitialized()) {{
            Kakao.init("{js_key}");
          }}
          Kakao.Share.createDefaultButton({{
            container: "#{button_id}",
            objectType: "feed",
            content: {{
              title: "{title}",
              description: "{description}",
              imageUrl: "{image_url}",
              link: {{
                mobileWebUrl: "{link_url}",
                webUrl: "{link_url}"
              }}
            }},
            buttons: [
              {{
                title: "{button_title}",
                link: {{
                  mobileWebUrl: "{link_url}",
                  webUrl: "{link_url}"
                }}
              }}
            ]
          }});
        }}
        // SDK 로드 완료 후 실행
        if (document.readyState === "loading") {{
          document.addEventListener("DOMContentLoaded", initShare);
        }} else {{
          initShare();
        }}
      }})();
    </script>
    """
    components.html(html, height=height)


def kakao_link_fallback(openchat_url: str = OPENCHAT_URL):
    """JS Key 없을 때 대체 버튼 (링크 방식)"""
    st.markdown(
        f"""
        <a href="{openchat_url}" target="_blank" style="
            display:block; text-decoration:none; text-align:center;">
          <div style="
            background:#FEE500; color:#111; font-weight:800;
            padding:14px 18px; border-radius:14px; font-size:0.95rem;
            box-shadow:0 6px 18px rgba(254,229,0,.45); margin:4px 0;">
            🟡 카카오 오픈채팅방 바로가기
          </div>
        </a>
        """,
        unsafe_allow_html=True,
    )
    st.caption("※ 카카오 SDK 미설정 — 링크 방식으로 동작 중")


def render_kakao_share_section(
    openchat_url: str = OPENCHAT_URL,
    thumb_fallback_url: str = _GITHUB_RAW_FALLBACK,
):
    """
    로그인 화면 등에서 호출 가능한 통합 카카오 공유 섹션.
    - secrets에 KAKAO_JS_KEY / KAKAO_THUMB_URL이 있으면 SDK 방식
    - 없으면 링크 버튼 + 체크리스트 표시
    """
    kakao_js_key   = _get_secrets("KAKAO_JS_KEY")
    kakao_thumb    = _get_secrets("KAKAO_THUMB_URL", thumb_fallback_url)

    st.markdown("#### 🟡 카카오톡으로 공유하기")

    if kakao_js_key:
        kakao_share_button(
            js_key=kakao_js_key,
            button_id="kakao-share-openchat",
            title="롯데월드타워 시그니엘 레지던스 실거래 VIP 상담",
            description="① 공개방(홍보) ② 1:1 상담방 ③ VIP 투자자 전용 | 급매/급임대 우선 공유",
            image_url=kakao_thumb,
            link_url=openchat_url,
            button_title="오픈채팅방 바로가기",
        )
    else:
        kakao_link_fallback(openchat_url)
        with st.expander("⚙️ 운영 설정 안내 (카카오 SDK 활성화)", expanded=False):
            st.markdown("""
            **카카오 SDK 공유(썸네일+버튼)를 실제로 동작시키려면:**

            **① Streamlit Secrets에 아래 2줄 추가** (Streamlit Cloud → App Settings → Secrets)
            ```toml
            KAKAO_JS_KEY = "발급받은_자바스크립트키"
            KAKAO_THUMB_URL = "https://raw.githubusercontent.com/peace0191/lotte-ai-app/main/assets/openchat_card.png"
            ```

            **② 카카오 디벨로퍼스 설정**
            1. [developers.kakao.com](https://developers.kakao.com) 접속
            2. 내 애플리케이션 → 플랫폼 → Web → 도메인 등록
            3. 예: `https://lotte-ai-app.streamlit.app`

            **③ GitHub에 이미지 Push** (썸네일 URL 활성화)
            ```
            git add assets/openchat_card.png
            git commit -m "add: openchat card image"
            git push
            ```
            """)
