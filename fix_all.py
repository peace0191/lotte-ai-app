import os, sys

BASE = r"C:\Users\PEACE\5차_AI\Lotte_AI_Browser_RunBAT_Demo\LotteTower_AI_SalesApp_Python"
APP  = os.path.join(BASE, "app.py")

src = open(APP, "r", encoding="utf-8").read()
print(f"읽기 완료: {len(src):,} 글자")

# ── 1. CSS 가독성 개선 (밝은 배경 → 흰 배경 + 진한 글씨)
OLD_CSS = """.stApp {
    background: linear-gradient(150deg, #f0f2f5 0%, #e8edf3 50%, #edf0f5 100%) !important;
}"""
NEW_CSS = """.stApp {
    background: #ffffff !important;
}"""
if OLD_CSS in src:
    src = src.replace(OLD_CSS, NEW_CSS)
    print("✅ CSS1: 배경색 흰색으로 변경")

OLD_LABEL = """label {
    font-size: 13px !important;
    font-weight: 700 !important;
    color: #374151 !important;
}"""
NEW_LABEL = """label {
    font-size: 13px !important;
    font-weight: 700 !important;
    color: #111827 !important;
}"""
if OLD_LABEL in src:
    src = src.replace(OLD_LABEL, NEW_LABEL)
    print("✅ CSS2: 라벨 글씨 진하게")

# markdown 일반 텍스트 가독성
OLD_BLOCK = """.block-container {
    background: transparent !important;
    padding-top: 0.5rem !important;
    padding-bottom: 90px !important;
    max-width: 1100px !important;
}"""
NEW_BLOCK = """.block-container {
    background: #ffffff !important;
    padding-top: 0.5rem !important;
    padding-bottom: 90px !important;
    max-width: 1100px !important;
}
/* 기본 텍스트 가독성 */
p, span, div, li, td, th {
    color: #111827;
}
h1, h2, h3, h4, h5, h6 {
    color: #0f172a !important;
}
.stMarkdown p {
    color: #1e293b !important;
    font-size: 14px !important;
}"""
if OLD_BLOCK in src:
    src = src.replace(OLD_BLOCK, NEW_BLOCK)
    print("✅ CSS3: 본문 텍스트 가독성 개선")

# ── 2. 고객관리 함수 추가
FUNC = r'''
def _render_customer_management_panel():
    import pandas as _pd, random as _rnd
    from datetime import datetime as _dt, timedelta as _td

    # 통계 카드
    _kc = st.columns(5)
    for _i, (_num, _label, _color, _bg) in enumerate([
        ("4,218", "전체 고객",  "#1d4ed8", "#eff6ff"),
        ("1,847", "매수 희망",  "#065f46", "#ecfdf5"),
        ("1,203", "임차 희망",  "#6b21a8", "#faf5ff"),
        ("891",   "매도/임대",  "#92400e", "#fffbeb"),
        ("277",   "계약 완료",  "#991b1b", "#fef2f2"),
    ]):
        _kc[_i].markdown(
            f'<div style="background:{_bg};border:1px solid {_color}33;border-radius:10px;'
            f'padding:12px;text-align:center;">'
            f'<div style="font-size:1.6rem;font-weight:800;color:{_color};">{_num}</div>'
            f'<div style="font-size:0.75rem;color:#374151;font-weight:600;">{_label}</div></div>',
            unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # 검색
    c1, c2, c3, c4 = st.columns([2, 2, 3, 1.5])
    _ct = c1.selectbox("고객유형", ["전체","매수희망","임차희망","매도/임대","계약완료"], key="cm_type")
    _cd = c2.selectbox("거래유형", ["전체","매매","전세","월세"], key="cm_deal")
    _kw = c3.text_input("검색어", placeholder="이름, 연락처, 단지명...", key="cm_kw")
    c4.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
    c4.button("🔍 검색", use_container_width=True, type="primary", key="cm_search")

    # 샘플 데이터
    _rnd.seed(7); _base = _dt(2026, 1, 1)
    _nm = ["이상수","김민준","박서연","최도윤","정유진","강민지","윤하은","장현우",
           "김은경","이지은","박준혁","최수아","정시우","강지호"]
    _dl = ["매수희망","임차희망","매도/임대","계약완료"]
    _cx = ["래미안대치팰리스","대치SK뷰","대치아이파크","은마아파트","시그니엘레지던스"]
    _rows = []
    for _i in range(50):
        _tp = _rnd.choice(_dl); _b = _rnd.randint(8, 65)
        _rows.append({
            "등록일":       (_base + _td(days=_rnd.randint(0,60))).strftime("%Y-%m-%d"),
            "이름":         _rnd.choice(_nm),
            "연락처":       f"010-{_rnd.randint(1000,9999)}-{_rnd.randint(1000,9999)}",
            "고객유형":     _tp,
            "희망단지":     _rnd.choice(_cx),
            "거래유형":     _rnd.choice(["매매","전세","월세"]),
            "희망예산(억)": f"{_b}~{_b+5}",
            "입주희망일":   (_base + _td(days=_rnd.randint(30,180))).strftime("%Y-%m-%d"),
            "AI매칭점수":   f"{_rnd.randint(72,99)}%",
            "상태":         _rnd.choice(["대기중","상담완료","매칭완료","계약진행","완료"]),
            "메모":         _rnd.choice(["학군 중요","즉시입주","주차필수","대출활용","급함"]),
        })
    _df = _pd.DataFrame(_rows)

    if _kw:
        _df = _df[_df["이름"].str.contains(_kw, na=False) |
                  _df["희망단지"].str.contains(_kw, na=False)]
    if _ct != "전체": _df = _df[_df["고객유형"] == _ct]
    if _cd != "전체": _df = _df[_df["거래유형"] == _cd]

    ab1, ab2 = st.columns([2, 6])
    with ab1:
        if st.button("➕ 고객 등록", use_container_width=True, key="cm_add"):
            st.session_state["cm_show_form"] = True
    _csv = _df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    ab2.download_button("📥 엑셀저장", data=_csv, file_name="고객목록.csv",
                        mime="text/csv", key="cm_dl")

    st.caption(f"총 {len(_df):,}명 조회")

    def _sc(v):
        m = {"대기중":   "background-color:#dbeafe;color:#1d4ed8;font-weight:600;",
             "상담완료": "background-color:#d1fae5;color:#065f46;font-weight:600;",
             "매칭완료": "background-color:#fef9c3;color:#854d0e;font-weight:600;",
             "계약진행": "background-color:#ffedd5;color:#9a3412;font-weight:600;",
             "완료":     "background-color:#f3f4f6;color:#6b7280;"}
        return m.get(v, "")

    st.dataframe(
        _df.style.map(_sc, subset=["상태"]),
        use_container_width=True, height=420,
        column_config={
            "이름":          st.column_config.TextColumn("이름", width=75),
            "연락처":        st.column_config.TextColumn("연락처", width=130),
            "고객유형":      st.column_config.TextColumn("고객유형", width=90),
            "희망단지":      st.column_config.TextColumn("희망단지", width=150),
            "거래유형":      st.column_config.TextColumn("거래유형", width=75),
            "희망예산(억)":  st.column_config.TextColumn("예산(억)", width=90),
            "AI매칭점수":    st.column_config.TextColumn("AI매칭", width=75),
            "상태":          st.column_config.TextColumn("상태", width=80),
            "메모":          st.column_config.TextColumn("메모", width=100),
        }
    )

    if st.session_state.get("cm_show_form"):
        st.markdown("---")
        st.markdown("#### ➕ 신규 고객 등록")
        with st.form("cm_form"):
            r1, r2, r3 = st.columns(3)
            _fn = r1.text_input("이름")
            r2.text_input("연락처", placeholder="010-0000-0000")
            r3.selectbox("고객유형", ["매수희망","임차희망","매도/임대"])
            r4, r5, r6 = st.columns(3)
            r4.text_input("희망단지")
            r5.selectbox("거래유형", ["매매","전세","월세"])
            r6.text_input("희망예산(억)", placeholder="30~35")
            st.text_area("메모", height=70)
            if st.form_submit_button("💾 저장", type="primary", use_container_width=True):
                st.success(f"✅ {_fn} 고객 등록 완료!")
                st.session_state["cm_show_form"] = False

'''

if "_render_customer_management_panel" not in src:
    src = src.replace(
        "def _render_property_management_panel():",
        FUNC + "def _render_property_management_panel():",
        1
    )
    print("✅ 고객관리 함수 추가 완료")
else:
    print("ℹ️  고객관리 함수 이미 존재")

# 백업 후 저장
open(os.path.join(BASE, "app_backup2.py"), "w", encoding="utf-8").write(
    open(APP, "r", encoding="utf-8").read()
)
open(APP, "w", encoding="utf-8").write(src)
print(f"\n🎉 완료! app.py 저장됨 ({len(src):,} 글자)")
print("브라우저를 새로고침(F5)하세요!")
