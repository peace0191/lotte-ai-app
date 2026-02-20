from __future__ import annotations

from pathlib import Path
import json

import streamlit as st

from services.assets_store import ensure_property_tree, list_property_ids
from services.publish_payloads import run_all_publish_payloads
from services.auth_helper import require_role
from services.db import set_workflow, audit

st.set_page_config(page_title="🚀 광고 발행 센터", layout="wide")
auth = require_role("supplier", "admin")

st.title("🚀 광고 발행 센터 (Payload 생성)")
st.caption(
    "유튜브/카카오/SNS 자동 광고를 위한 ‘업로드/발송 정보(payload)’를 자동 생성합니다. "
    "실제 업로드는 'YouTube 업로드' 메뉴에서 진행합니다."
)

ids = list_property_ids()
if not ids:
    st.warning("매물이 없습니다. 먼저 업로드/자동생성을 진행하세요.")
    st.stop()

# 가장 최근에 수정한 매물 선택
idx = len(ids) - 1
if "selected_property_id" in st.session_state and st.session_state.selected_property_id in ids:
    idx = ids.index(st.session_state.selected_property_id)

pid = st.selectbox("매물 선택", ids, index=idx)
st.session_state.selected_property_id = pid
paths = ensure_property_tree(pid)

st.info(f"선택 매물: **{pid}**  |  publish 폴더: `{(paths.base / 'publish').as_posix()}`")

# 카카오 공유 버튼
def kakao_share_button(message_payload_path: Path):
    if not message_payload_path.exists():
        return

    payload = json.loads(message_payload_path.read_text(encoding="utf-8"))
    msg = payload.get("message", "")
    btn_url = (payload.get("button") or {}).get("url", "")

    kakao_js_key = st.secrets.get("KAKAO_JS_KEY", "")
    # KAKAO_JS_KEY가 없어도 UI는 보여주되 경고 only for admin/debug
    
    html = f"""
    <script src="https://t1.kakaocdn.net/kakao_js_sdk/2.7.2/kakao.min.js"></script>
    <script>
      try {{
          Kakao.init("{kakao_js_key}");
      }} catch(e) {{ console.log(e); }}
      
      function sendKakao() {{
        if (!"{kakao_js_key}") {{ alert("KAKAO_JS_KEY 설정이 필요합니다."); return; }}
        Kakao.Share.sendDefault({{
          objectType: 'text',
          text: {json.dumps(msg)},
          link: {{
            mobileWebUrl: {json.dumps(btn_url)},
            webUrl: {json.dumps(btn_url)}
          }},
          buttons: [
            {{
              title: '상담/예약하기',
              link: {{
                mobileWebUrl: {json.dumps(btn_url)},
                webUrl: {json.dumps(btn_url)}
              }}
            }}
          ]
        }});
      }}
    </script>
    <button style="width:100%;padding:12px 14px;border-radius:12px;border:1px solid #ddd;
                   font-weight:700;cursor:pointer;background-color:#FEE500;color:#000;"
            onclick="sendKakao()">
      💬 카카오톡으로 공유/발송
    </button>
    """
    st.components.v1.html(html, height=60)


left, right = st.columns([1, 1], vertical_alignment="top")

with left:
    st.subheader("1) Payload 자동 생성")
    if st.button("🧾 유튜브/카카오/SNS payload 생성", use_container_width=True):
        with st.spinner("payload 생성 중..."):
            res = run_all_publish_payloads(paths)
        if res.ok:
            st.success("payload 생성 완료 ✅")
            set_workflow(pid, "generated", supplier_id=auth["user_id"]) # 상태 유지 or 'ready_to_publish'?
            audit(auth["user_id"], auth["role"], "CREATE_PAYLOADS", pid, "ok")
        else:
            st.error("일부 payload 생성 실패/경고가 있습니다.")
        st.session_state["pub_msgs"] = res.messages

    if "pub_msgs" in st.session_state:
        with st.expander("📋 생성 로그", expanded=True):
            for m in st.session_state["pub_msgs"]:
                st.write(m)

with right:
    st.subheader("2) 생성된 파일 미리보기")
    # show files if exist
    y = paths.publish_youtube / "upload_payload.json"
    k = paths.publish_kakao / "message_payload.json"
    i = paths.publish_sns / "insta_payload.json"
    b = paths.publish_sns / "naverblog_payload.html"

    def show_json(p: Path, title: str):
        st.markdown(f"**{title}**  ·  `{p.name}`")
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                st.json(data)
            except Exception as e:
                st.error(f"JSON 읽기 실패: {e}")
        else:
            st.info("아직 생성되지 않았습니다.")

    def show_html(p: Path, title: str):
        st.markdown(f"**{title}**  ·  `{p.name}`")
        if p.exists():
            html = p.read_text(encoding="utf-8")
            st.code(html, language="html")
            st.markdown("미리보기(간단):", help="블로그에 붙여넣기 전 확인용")
            st.components.v1.html(html, height=260, scrolling=True)
        else:
            st.info("아직 생성되지 않았습니다.")

    show_json(y, "YouTube 업로드 payload")
    st.divider()
    
    st.markdown("**Kakao 공유 payload**")
    if k.exists():
         show_json(k, "")
         kakao_share_button(k)
    else:
        st.info("카카오 payload 없음")

    st.divider()
    show_json(i, "SNS(인스타) payload")
    st.divider()
    show_html(b, "Naver Blog HTML")

