from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import datetime
from services.ui import render_bottom_nav
from services.region_compare import REGIONS, score_region, summary_comment, lease_recommendation
from services.compare_pdf import build_compare_pdf

from services.pdf_lease_offer import build_lease_offer_pdf

def compress_price(p_str):
    """ '33억' -> 33, '33억 5,000' -> 33.5 conversion helper """
    try:
        if not p_str: return 0
        p_str = str(p_str).replace("만원", "").replace(",", "")
        if "억" in p_str:
            parts = p_str.split("억")
            billions = float(parts[0].strip()) if parts[0].strip() else 0
            millions = float(parts[1].strip()) if len(parts) > 1 and parts[1].strip() else 0
            return billions + (millions / 10000)
            return float(p_str) / 100000000 # Assume raw number is won ? Unlikely, usually formatted.
    except:
        return 0

def recommend_jeonse_wolse(sale_price_str: str, area_pyeong: float, ai_grade: str, ai_score: float) -> dict:
    """
    Calculates recommend Jeonse/Wolse ranges based on sale price and AI score.
    Returns a dict with range tuples and logic notes.
    """
    # 1. Parse Sale Price (e.g. "33.5" or "33억 5000")
    sale_val = compress_price(sale_price_str)
    if sale_val <= 0:
        # Fallback default
        return {
            "jeonse_range_eok": (10.0, 12.0),
            "wolse_dep_range_eok": (1.0, 5.0),
            "wolse_month_range_manwon": (300, 450),
            "notes": ["매매가 정보 없음 - 기본값 적용"]
        }
        
    # 2. Base Jeonse Rate (50~60%) based on AI Score
    # Higher AI score -> Stronger demand -> Higher Jeonse Rate
    base_rate = 0.50
    if ai_score >= 95: base_rate = 0.58
    elif ai_score >= 90: base_rate = 0.55
    elif ai_score >= 85: base_rate = 0.52
    
    jeonse_val = sale_val * base_rate
    
    # Range +/- 5%
    j_low = round(jeonse_val * 0.95, 1)
    j_high = round(jeonse_val * 1.05, 1)
    
    # 3. Wolse Conversion (Conversion Rate ~4~5% depending on market)
    # Annual Rent = (Jeonse - Deposit) * ConversionRate
    # Let's propose a range of deposits logic:
    # Option A: Low Deposit (10% of sale) -> High Rent
    # Option B: High Deposit (40% of sale) -> Low Rent
    
    dep_low = round(sale_val * 0.1, 1) # 10% deposit
    if dep_low < 1.0: dep_low = 1.0
    
    dep_high = round(sale_val * 0.4, 1) # 40% deposit (half-jeonse)
    
    # Rent calc: (Jeonse - Deposit) * 4.5% / 12
    def calc_monthly(deposit):
        gap = jeonse_val - deposit
        if gap < 0: return 0
        annual_rent = gap * 100000000 * 0.045 # 4.5% conversion
        return int(annual_rent / 12 / 10000) # Manwon
        
    m_high = calc_monthly(dep_low)
    m_low = calc_monthly(dep_high)
    
    return {
        "jeonse_range_eok": (j_low, j_high),
        "wolse_dep_range_eok": (dep_low, dep_high),
        "wolse_month_range_manwon": (m_low, m_high),
        "notes": [f"AI 전세가율 {int(base_rate*100)}% 적용", "월세전환율 4.5% 기준"]
    }


def render(properties=None):
    # CSS injection for premium report look
    st.markdown("""
    <style>
    .report-title {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 32px;
        font-weight: 900;
        color: #d4af37;
        margin-bottom: 5px;
        letter-spacing: -1px;
    }
    .report-subtitle {
        font-size: 16px;
        color: #888;
        margin-bottom: 30px;
    }
    .kpi-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .kpi-title {
        font-size: 14px;
        color: #aaa;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 800;
        color: #fff;
    }
    .kpi-trend {
        font-size: 12px;
        color: #00d1b2; /* distinct color */
    }
    .complex-box {
        background: #1e1e1e;
        border-left: 4px solid #d4af37;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 0 8px 8px 0;
    }
    .complex-name {
        font-size: 18px;
        font-weight: bold;
        color: #eee;
    }
    .complex-desc {
        font-size: 13px;
        color: #ccc;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 0. User Interaction (Target Selection & Tweaks)
    with st.sidebar:
        st.header("🎯 AI 분석 설정")
        target_persona = st.radio("분석 관점 선택", ["학부모", "투자자", "임대인"], index=0)

        st.subheader("⚙️ 실시간 조정(슬라이더)")
        st.caption("상담 중 고객 반응에 맞춰 -10~+10 범위로 조정")
        tweaks = {
            "school": st.slider("학군 가중 체감(점수 보정)", -10, 10, 0),
            "lease":  st.slider("임대 안정성 체감(점수 보정)", -10, 10, 0),
            "defense":st.slider("시세 방어 체감(점수 보정)", -10, 10, 0),
            "brand":  st.slider("브랜드 상징 체감(점수 보정)", -10, 10, 0),
            "demand": st.slider("실수요 지속 체감(점수 보정)", -10, 10, 0),
        }
    
    # Calculate for Daechi 1-dong first
    daechi = score_region("대치1동", target_persona, tweaks)
    ai_grade, ai_score = daechi['grade'], daechi['score']

    # 1. Dynamic Header
    st.markdown('<div class="report-title">🎓 대치1동 지역 및 학군 특성 Report</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="report-subtitle">AI가 <b>{target_persona}</b> 관점에서 분석한 핵심 리포트입니다.</div>', unsafe_allow_html=True)
    
    # Badge SSS (New Style)
    badge_text = f"🏅 대치1동 학군 프리미엄 {ai_grade}  |  AI 점수 {ai_score:.1f}점 (관점: {target_persona})"
    st.markdown(
        f"""
        <div style="
            border:1px solid rgba(212,175,55,0.35);
            background: rgba(212,175,55,0.10);
            padding:10px 14px;
            border-radius:10px;
            color:#d4af37;
            font-weight:800;
            margin: 10px 0 16px 0;
            display: inline-block;
        ">{badge_text}</div>
        """,
        unsafe_allow_html=True
    )

    # ✅ 전세/월세 추천 조건(범위) 자동 제안
    sample_sale = "33억"
    sample_area = 27

    p0 = None
    if properties:
        if isinstance(properties, list) and len(properties) > 0:
            p0 = properties[0]
        elif isinstance(properties, dict):
            # Flatten or pick first value list
            for sublist in properties.values():
                if sublist and isinstance(sublist, list) and len(sublist) > 0:
                    p0 = sublist[0]
                    break
        
    if p0:
        sample_sale = p0.get("price") or p0.get("sale_price") or sample_sale
        sample_area = p0.get("area_py") or p0.get("area") or sample_area
    
    # 안전장치: "14.5 / 1700만" 같은 복합 문자열 처리
    sample_sale = str(sample_sale).split("/")[0].strip()

    lease = recommend_jeonse_wolse(
        sale_price_str=str(sample_sale),
        area_pyeong=float(sample_area or 0),
        ai_grade=str(ai_grade),
        ai_score=float(ai_score)
    )

    # Intro logic
    def get_ai_intro(target):
        if target == "학부모":
            return "**\"자녀의 12년, 대치1동이 정답입니다.\"**\n대치초-대청중-단대부고로 이어지는 **황금 학군 라인**은 자녀에게 '시간'을 선물합니다."
        elif target == "투자자":
            return "**\"불황에 더 강한 안전자산, 대치1동입니다.\"**\n대한민국 사교육 1번지의 **비탄력적 수요**는 하락장에서도 강력한 가격 방어력을 증명했습니다."
        else: # Landlord
            return "**\"공실 걱정 없는 최우량 임대처, 대치1동입니다.\"**\n학기 시즌마다 대기 수요가 넘쳐나는 이곳은, 임대인에게 **최고의 안정성**을 제공합니다."

    st.info(get_ai_intro(target_persona), icon="💡")

    # Metrics Style UI for Lease Recommendation
    st.markdown("### 💰 AI 전세/월세 추천 조건(범위)")
    cA, cB = st.columns(2)
    with cA:
        jl, jh = lease["jeonse_range_eok"]
        st.metric("전세(권장 범위)", f"{jl}억 ~ {jh}억")

    with cB:
        dl, dh = lease["wolse_dep_range_eok"]
        ml, mh = lease["wolse_month_range_manwon"]
        st.metric("월세(권장)", f"보증금 {dl}억 / 월 {ml}~{mh}만원")

    st.caption("· " + " · ".join(lease["notes"]))


    # 3. Enhanced KPIs
    total_listings = len(properties) if properties else 0
    avg_price = 0
    if properties:
        # Properties is Grouped Dict {Section: [Items]} or List
        flat_props = []
        if isinstance(properties, dict):
            for items in properties.values():
                flat_props.extend(items)
        elif isinstance(properties, list):
            flat_props = properties
            
        valid_prices = []
        for p in flat_props:
            val = compress_price(p.get("price", ""))
            if val > 0: valid_prices.append(val)
        
        if valid_prices:
            avg_price = sum(valid_prices) / len(valid_prices) 

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">지역 평단가</div>
            <div class="kpi-value">1.15억</div>
            <div class="kpi-trend">▲ 3.2% (강세)</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">학군 프리미엄 지수</div>
            <div class="kpi-value">{ai_score:.1f}점</div>
            <div class="kpi-trend">동남권 상위 1%</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">학군 배정 등급</div>
            <div class="kpi-value">{ai_grade}</div>
            <div class="kpi-trend">대치초/대청중/단대부고</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">AI 매수 추천도</div>
            <div class="kpi-value" style="color:#d4af37">강력 매수</div>
            <div class="kpi-trend">지금이 기회</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 2. Main Content Layout
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        st.subheader("📊 대치동 주요 단지 비교 분석")
        # Mock data for chart
        data = pd.DataFrame({
            "단지명": ["래미안대치팰리스", "대치SK뷰", "대치아이파크", "대치삼성", "은마아파트"],
            "평단가(천만원)": [12.5, 11.8, 10.9, 9.8, 8.5],
            "학군선호도": [98, 95, 92, 88, 90],
            "입주년도": [2015, 2017, 2008, 2000, 1979]
        })
        
        tab_a, tab_b = st.tabs(["평단가 비교", "학군 선호도"])
        with tab_a:
            fig = px.bar(data, x="단지명", y="평단가(천만원)", color="단지명", title="3.3㎡당 평균 시세 (단위: 천만원)")
            st.plotly_chart(fig, use_container_width=True)
        with tab_b:
            fig2 = px.line(data, x="단지명", y="학군선호도", markers=True, title="학부모 학군 선호도 지수")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### 💡 AI 부동산 인사이트: 대치1동의 국지적 가치")
        st.info("""
        **"수요는 폭발하지만, 공급은 비탄력적인 시장"**
        
        대치1동은 단순한 주거지가 아닙니다. **대치초, 대청중, 단대부중·고, 숙명여고**로 이어지는 명문 학군 배정권과 **대치동 학원가와의 물리적 근접성**이 결합된, 대한민국에서 가장 독특한 국지적 시장입니다.
        
        **1. 입지적 효율성 (Time Saving)**
        학원가로의 도보 접근성(라이딩 불필요)은 학부모의 시간과 비용을 획기적으로 절약해줍니다. 대장주 아파트가 경기 변동에도 흔들리지 않는 이유는 바로 이 대체 불가능한 효율성 때문입니다.

        **2. 공급의 구조적 비탄력성 (Scarcity)**
        "기다리면 매물이 나온다"는 일반 시장의 상식이 이곳에선 통하지 않습니다. 
        - **장기 거주:** 한 번 입주하면 초등부터 대학까지 약 12년을 거주하여 매물 회전이 극히 낮습니다.
        - **인근지배정:** 학교 정원에 비해, 가장 인접한 근접한 신축 대장아파트는 대치1동에 있습니다.
        
        **3. AI 저평가 매물의 선객(先客) 전략**
        
        결국, 입학 시즌에 맞춰 확실한 인근지 배정의 준공 10년 전후 매물은 신축 선호 고객에게 **'매물이 있을 때 선택하는 것이 탁월하고 안전한 전략 중 하나'**입니다.
        """)

    with c2:
        st.subheader("📍 핵심 단지 특징 요약")
        
        st.markdown("""
        <div class="complex-box">
            <div class="complex-name">1. 래미안 대치 팰리스</div>
            <div class="complex-desc">
            - 대치동의 대장주, 커뮤니티 시설 최상<br>
            - 단대부고, 중산고, 숙명여고 등 명문학군 인접<br>
            - 수영장, 조식 서비스 운영
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="complex-box">
            <div class="complex-name">2. 대치 SK뷰</div>
            <div class="complex-desc">
            - 대치역 초역세권, 신축 컨디션 우수<br>
            - 대치초등학교 배정 (선호도 최상)<br>
            - 학원가 도보 3분 거리로 ‘라이딩’ 불필요
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="complex-box">
            <div class="complex-name">3. 대치 아이파크</div>
            <div class="complex-desc">
            - 분당선 한티역 역세권<br>
            - 대도초등학교 배정, 도곡시장 인접 편리성<br>
            - 롯데백화점 슬세권, 실거주 만족도 높음
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="complex-box">
            <div class="complex-name">4. 은마 아파트</div>
            <div class="complex-desc">
            - 대한민국 재건축의 상징<br>
            - GTX-C 호재 및 정비계획안 통과 기대감<br>
            - 상대적으로 저렴한 전세가로 학군지 진입 가능
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 3. Education Map / Info Section (Connected to Education Page)
    st.subheader("🏫 학군 및 인프라")
    col_map, col_list = st.columns([2, 1])
    
    with col_map:
        # Placeholder for Map or Image
        st.markdown(
            """
            <div style="background-color: #2b2b2b; height: 300px; display: flex; align-items: center; justify-content: center; border-radius: 10px; color: #888;">
                지도/이미지 로딩 영역
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col_list:
        st.markdown("""
        **주요 배정 학교**
        - **초등:** 대치초, 대도초 (과밀학급 주의)
        - **중등:** 대청중, 단대부중, 숙명여중
        - **고등:** 휘문고, 중동고, 단대부고, 경기여고, 숙명여고
        
        **편의 시설**
        - 롯데백화점 강남점
        - 강남 세브란스 병원
        - 양재천 산책로
        """)
        if st.button("📚 교육환경 자세히 보기", use_container_width=True):
            st.session_state["redirect_to"] = "📚 교육환경"
            st.rerun()

    st.markdown("---")

    # 📄 임대차 제안서 PDF(1페이지) 자동 생성
    st.markdown("### 📄 임대차 제안서 PDF(1페이지) 자동 생성")
    if st.button("📄 전·월세 제안서 PDF 생성", use_container_width=True):
        jl, jh = lease["jeonse_range_eok"]
        dl, dh = lease["wolse_dep_range_eok"]
        ml, mh = lease["wolse_month_range_manwon"]

        landlord_pitch = (
            "대치1동은 학군 수요가 확실해 공실 리스크가 낮습니다.\\n"
            "전세는 안정·빠른 계약, 월세는 수익 구조 최적화가 가능합니다.\\n"
            "AI 추천 범위로 조건을 선점하는 방식으로 제안드리겠습니다."
        )
        consult_script = (
            "대치1동은 학군·학원가가 결합된 시장이라 의사결정이 빠릅니다.\\n"
            "도보 통학/라이딩 최소화는 체감 가치가 커서 수요가 비탄력적입니다.\\n"
            "조건만 맞으면 오늘 선점이 유리합니다."
        )
        shorts_script = (
            "0~3초: 대치1동, 학군 프리미엄 SSS\\n"
            "3~10초: 대치초–대청중–단대부 라인, 학원가 도보권\\n"
            "10~18초: 수요는 강하고 공급은 제한적—가격 방어\\n"
            "18~26초: 입학 시즌, 조건 맞으면 선점\\n"
            "26~30초: 문의 02-578-8285"
        )

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        out_pdf = f"outputs/pdfs/lease_offer_{ts}.pdf"

        pdf_path = build_lease_offer_pdf(
            out_path=out_pdf,
            title="대치1동 학군 프리미엄 제안서",
            subtitle=f"{target_persona} 관점 AI 리포트 + 전·월세 조건 자동 제안",
            badge=f"대치1동 학군 프리미엄 {ai_grade}",
            jeonse_text=f"{jl}억 ~ {jh}억",
            wolse_text=f"보증금 {dl}억 ~ {dh}억 / 월 {ml}~{mh}만원",
            landlord_pitch=landlord_pitch,
            consult_script=consult_script,
            shorts_script=shorts_script
        )

        with open(pdf_path, "rb") as f:
            st.download_button(
                "⬇️ PDF 다운로드",
                data=f,
                file_name=Path(pdf_path).name,
                mime="application/pdf",
                use_container_width=True
            )

    st.markdown("---")
    
    # 4. Footer / Call to Action
    st.markdown("#### 🚀 지금 바로 대치동 인기 매물을 확인하세요")
    if st.button("🏠 추천 매물 보러가기", type="primary", use_container_width=True):
        st.session_state["redirect_to"] = "🏠 추천매물"
        st.rerun()

    st.markdown("---")

    # --- 📊 Regional Comparison Section ---
    st.subheader("📊 강남 핵심 지역 AI 비교 (대치1동 vs 도곡 vs 압구정)")

    # Recalculate for all regions with current tweaks/persona
    rows = [score_region(r, target_persona, tweaks) for r in REGIONS]
    rows_sorted = sorted(rows, key=lambda x: x["score"], reverse=True)
    top_region = rows_sorted[0]["region"]

    df_comp = pd.DataFrame([
        {"지역": r["region"], "AI 종합점수": r["score"], "등급": r["grade"], 
         "세부": f"학군{int(r['profile']['school'])}/임대{int(r['profile']['lease'])}/방어{int(r['profile']['defense'])}"} 
        for r in rows_sorted
    ])
    st.dataframe(df_comp, use_container_width=True)

    st.info(summary_comment(top_region, target_persona), icon="💡")
    
    cbtn1, cbtn2 = st.columns(2)

    with cbtn1:
        if st.button("📄 비교 PDF 생성 (3지역)", use_container_width=True):
            pdf_bytes = build_compare_pdf(
                title="강남 핵심 지역 AI 비교 리포트 (1페이지)",
                persona=target_persona,
                rows=rows_sorted,
                highlight_region="대치1동",
            )
            st.download_button(
                "⬇️ 다운로드: compare_report.pdf",
                data=pdf_bytes,
                file_name="compare_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    with cbtn2:
        pick = st.selectbox("대치1동 vs 비교 지역 선택", ["도곡동", "압구정동"])
        if st.button("📄 대치 vs 선택지역 PDF", use_container_width=True):
            two = [score_region("대치1동", target_persona, tweaks), score_region(pick, target_persona, tweaks)]
            two_sorted = sorted(two, key=lambda x: x["score"], reverse=True)
            pdf_bytes = build_compare_pdf(
                title=f"대치1동 vs {pick} AI 비교 리포트 (1페이지)",
                persona=target_persona,
                rows=two_sorted,
                highlight_region="대치1동",
            )
            st.download_button(
                f"⬇️ 다운로드: daechi_vs_{pick}.pdf",
                data=pdf_bytes,
                file_name=f"daechi_vs_{pick}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    st.markdown("---")
    
    # Bottom Navigation
    st.markdown('<div style="text-align: center; color: #888; font-size: 12px; margin-top: 20px;">롯데타워앤강남빌딩부동산중개 (주) 02-578-8285</div>', unsafe_allow_html=True)
    render_bottom_nav("🎓 대치1동 특성")
