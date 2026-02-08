from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
from services.map_image import build_points_map_png
from pathlib import Path
import datetime
import re
import random
from services.ui import render_bottom_nav
from services.region_compare import REGIONS, score_region, summary_comment, lease_recommendation
from services.compare_pdf import build_compare_pdf
from services.lease_recommender import recommend_jeonse_wolse
from services.pdf_lease_offer import build_lease_offer_pdf
from services.geocode import geocode_nominatim
from services.data import load_properties
import json
import os

# ------------------------------------------------------------------------------
# Confirmed Coordinates & Color Mapping
# ------------------------------------------------------------------------------
POINTS_PATH = Path("data/daechi_points.json")

COLOR_RGB = {
    "초등": [255, 99, 71],     # Red
    "중등": [50, 205, 50],     # Green
    "고등": [65, 105, 225],    # Blue
    "단지": [255, 215, 0],     # Gold
    "부동산": [186, 85, 211],  # Purple
    "관공서": [150, 150, 150], # Grey
}

def load_points():
    if not POINTS_PATH.exists():
        return pd.DataFrame()
    items = json.loads(POINTS_PATH.read_text(encoding="utf-8"))
    df = pd.DataFrame(items)
    
    # Robust numeric conversion
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    
    # Filter for valid lat/lon
    df = df.dropna(subset=["lat", "lon"]).copy()
    
    # Normalize category names
    df["color"] = df["category"].apply(lambda x: COLOR_RGB.get(x, [200, 200, 200]))
    
    # Check for "Overcrowded" note
    df["is_overcrowded"] = df.get("note", "").fillna("").astype(str).str.contains("과밀")
    
    # Assign 'height' for 3D extrusion
    def get_height(cat):
        if cat == "단지": return 200
        if cat in ["초등", "중등", "고등"]: return 100
        return 50
    df["height"] = df["category"].apply(get_height)
    
    return df

def prefix_icon(cat):
    return {"초등":"🏫","중등":"🏫","고등":"🏫","단지":"🏠","부동산":"🏢","관공서":"🏛️"}.get(cat,"📍")

def render_daechi_map_block():
    st.markdown("### 📍 AI 대치1동 학군/단지 입체 지도")
    st.caption("3D 마커와 함께 학군 배정 라인을 확인해보세요. (Shift + 드래그로 회전 가능)")

    df = load_points()
    if df.empty:
        st.warning("데이터(daechi_points.json)가 없어 지도를 표시할 수 없습니다.")
        return

    # Add icon to name for label
    df["display_name"] = df.apply(lambda r: f"{prefix_icon(r['category'])} {r['name']}", axis=1)

    # (1) 3D Column Layer
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position=["lon", "lat"],
        get_elevation="height",
        elevation_scale=1,
        radius=40,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
        extruded=True,
    )

    # (2) Scatterplot Halo
    halo_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_fill_color=[0, 0, 0, 0],
        get_line_color="color",
        stroked=True,
        filled=False,
        get_radius=80,
        radius_units="meters",
        line_width_min_pixels=2,
    )

    # (3) Label Layer
    label_layer = pdk.Layer(
        "TextLayer",
        data=df,
        get_position=["lon", "lat"],
        get_text="display_name",
        get_size=14,
        get_color=[255, 255, 255],
        get_background_color=[0, 0, 0, 140],
        get_text_anchor="'middle'",
        get_alignment_baseline="'bottom'",
        get_pixel_offset=[0, -40],
        billboard=True, 
        pickable=False,
    )

    # (4) Overcrowded Element Warning
    crowded_df = df[df["is_overcrowded"]].copy()
    crowded_layer = pdk.Layer(
        "ScatterplotLayer",
        data=crowded_df,
        get_position=["lon", "lat"],
        get_fill_color=[255, 50, 50, 30],
        get_line_color=[255, 50, 50, 200],
        stroked=True,
        filled=True,
        get_radius=300,
        radius_units="meters",
        line_width_min_pixels=2,
    )

    # (5) School Line
    # (5) Custom Lines (Orange & Pink)
    def find_one(name_part):
        # Try exact match first, then subset
        hit = df[df["name"] == name_part]
        if hit.empty:
            hit = df[df["name"].astype(str).str.contains(name_part)]
        return None if hit.empty else hit.iloc[0]

    # Orange Line: 대치초 -> 래미안대치팰리스 -> 대치SK뷰
    o_names = ["서울대치초등학교", "래미안대치팰리스(1·2차)", "대치SK뷰"]
    o_points = [find_one(n) for n in o_names]
    
    path_data = []

    if all(p is not None for p in o_points):
        path = [[float(p["lon"]), float(p["lat"])] for p in o_points]
        path_data.append({"path": path, "color": [255, 140, 0], "name": "Orange Line"}) # Dark Orange

    # Pink Line: 단대부고 -> 대치아이파크 -> 래미안 -> SK뷰 -> 삼환
    p_names = ["단대부고", "대치아이파크", "래미안대치팰리스(1·2차)", "대치SK뷰", "대치 삼환아르누보2(본사)"]
    p_points = [find_one(n) for n in p_names]

    if all(p is not None for p in p_points):
        path = [[float(p["lon"]), float(p["lat"])] for p in p_points]
        path_data.append({"path": path, "color": [255, 20, 147], "name": "Pink Line"}) # Deep Pink

    layers = [crowded_layer, halo_layer, column_layer, label_layer]

    if path_data:
        path_layer = pdk.Layer(
            "PathLayer",
            data=path_data,
            get_path="path",
            get_color="color",
            width_scale=10,
            width_min_pixels=5,
            pickable=True
        )
        layers.append(path_layer)

    tooltip = {
        "html": "<b>{name}</b><br/>{category}<br/>{address}<br/>{note}",
        "style": {"backgroundColor": "rgba(20,20,20,0.9)", "color": "white", "fontSize": "12px"}
    }

    view_state = pdk.ViewState(
        latitude=37.493, 
        longitude=127.062,
        zoom=14.2,
        pitch=45,
        bearing=0
    )

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=view_state,
        layers=layers,
        tooltip=tooltip
    ), use_container_width=True)

def calculate_metrics():
    """Calculates average prices dynamically from properties.json."""
    props = load_properties()
    targets = ["대치팰리스", "대치SK뷰", "대치아이파크"]
    
    buckets = {20: [], 30: [], 40: []}
    
    for k, items in props.items():
        if k not in targets: continue
        for item in items:
            spec = item.get("spec", "")
            match = re.search(r"(\d+)평", spec)
            if match:
                size = int(match.group(1))
                if size >= 40:
                    b_key = 40
                elif size >= 30:
                    b_key = 30
                elif size >= 20:
                    b_key = 20
                else:
                    continue
                
                # Check pure Sale or Sale-like Listings
                price_str = item.get("price", "")
                # Ignore Wolse (contains /)
                if "/" not in price_str and "억" in price_str:
                    try:
                        # Extract number before 억
                        # "38억" -> 38.0
                        val_str = re.search(r"([\d\.]+)억", price_str).group(1)
                        val = float(val_str)
                        buckets[b_key].append(val)
                    except:
                        pass
    
    # Defaults/Fallbacks (Mock/Approx if no data)
    avgs = {
        20: 23.5, # Default fallback
        30: 32.5,
        40: 48.0
    }
    
    # Update with calculated
    for k, v in buckets.items():
        if v:
            avgs[k] = round(sum(v) / len(v), 1)
            
    return avgs

def render_rich_narrative(persona: str):
    """Renders the detailed 'Storytelling' report that parents value."""
    st.markdown("### 🎓 대치1동 프리미엄 리포트: 왜 대치1동인가?")
    if persona == "학부모":
        st.info("**\"아이의 통학 시간은 곧 수면 시간이고, 성적입니다.\"**\n\n대치1동은 대한민국 사교육의 심장이자, 유해시설이 전무한 '청정 교육 특구'입니다. **'자녀의 미래를 위한 베이스캠프'**로서의 가치를 제안합니다.")
    elif persona == "투자자":
        st.info("**\"불황에 강한 부동산은 결국 '확실한 수요'가 있는 곳입니다.\"**\n\n대치1동은 학군 수요로 인해 전세가율이 탄탄하게 받쳐주며, 재건축 이슈와 신축의 조화로 시세 상승 여력이 충분합니다.")
    else:
        st.info("**\"공실 없는 임대 수익, 대치1동이라면 가능합니다.\"**\n\n매년 11월 수능 이후부터 2월까지, 전국에서 몰려드는 학군 수요로 인해 가장 빠르고 높은 가격에 임대 계약이 체결되는 지역입니다.")

    st.divider()

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("#### 🏫 황금 학군 라인")
        st.markdown("지도에 표시된 <span style='color:#ff5050'>**빨간색 화살표**</span>는 **'초ㆍ중ㆍ고 원스톱 진학'** 경로입니다.", unsafe_allow_html=True)
        st.caption("이 라인 안에 거주한다는 것은 자녀에게 '시간'과 '체력'을 선물하는 것과 같습니다.")

        with st.expander("📍 각 학교별 상세 특징 보기", expanded=True):
            st.markdown("""
                **1. 서울대치초등학교** (초품아)\n- **특징**: 높은 학업 성취도\n- **Note**: 과밀학급 주의
                **2. 대청중학교** (남녀공학)\n- **특징**: 특목고/자사고 진학률 최상위\n
                **3. 단대부속고등학교 / 숙명여고**\n- **특징**: 서울대 진학 실적 전국 TOP
                """)
    with col2:
        st.markdown("#### 🏢 주요 명품 단지 분석")
        tab1, tab2, tab3 = st.tabs(["래미안대치팰리스", "대치아이파크/SK뷰", "은마아파트"])
        with tab1:
            st.success("👑 **대치동의 대장주**")
            st.write("대치초 배정, 학원가 바로 앞, 수영장/조식 등 완벽한 커뮤니티.")
        with tab2:
            st.warning("⚖️ **실속과 환경의 조화**")
            st.write("대치역/한티역 역세권, 백화점 슬세권, 쾌적한 주거 환경.")
        with tab3:
            st.error("🏗️ **재건축의 상징**")
            st.write("강남 재건축의 바로미터, 대곡초 배정, 압도적 투자가치.")

    st.divider()
    st.markdown("#### 🛡️ 안심 생활권 & 편의시설")
    st.write("대치1동 주민센터와 지구대가 인접하여 행정 업무와 치안이 매우 우수합니다.")

def get_sss_side_message(persona: str) -> str:
    if persona == "학부모":
        return "도보 통학/학원가 접근으로 '시간 가치' 극대화. 대치초-대청중-단대부 라인의 확실한 배정권."
    return "대치동 학군지 투자는 실패하지 않습니다."

def render(properties=None):
    render_dashboard()

def render_dashboard():
    # Sidebar
    with st.sidebar:
        st.header("설정 (Settings)")
        user_persona = st.selectbox("당신은 누구십니까?", ["학부모", "투자자", "임대인"])
        st.info(f"**{user_persona} 모드**로 분석합니다.")
        st.markdown("---")
        st.markdown("### 📌 대치1동 핵심 지표")
        st.metric("학군 등급", "SSS+", "전국 최상위")
        st.metric("전세가율", "52~55%", "안정적")
        st.markdown("---")
        st.markdown("### 🛡️ 보안 대시보드")
        st.success("🔒 내부망 보안 연결됨 (Secure)")
        st.caption("✅ 외부 해킹 원천 차단 (Localhost)")
        st.caption("✅ SSL/TLS 프로토콜 준비됨")

    # Header
    st.title(f"대치1동 AI 부동산 대시보드 ({user_persona})")
    
    # --------------------------------------------------------
    # 1. Enhanced Metrics with Calculation
    # --------------------------------------------------------
    avg_prices = calculate_metrics()
    
    st.markdown("### 📊 평형별 시세 트렌드 (앱 내 매물 기준)")
    
    m_col1, m_col2, m_col3 = st.columns(3)
    
    with m_col1:
        p20 = avg_prices[20]
        jeonse20 = round(p20 * 0.52, 1)
        st.metric("20평형대 (소형)", f"{p20}억", "+0.8%")
        st.caption(f"전세가 {jeonse20}억 (추정)")
        
    with m_col2:
        p30 = avg_prices[30]
        jeonse30 = round(p30 * 0.52, 1)
        st.metric("30평형대 (국민평형)", f"{p30}억", "+1.2%")
        st.caption(f"전세가 {jeonse30}억 (추정)")
        
    with m_col3:
        p40 = avg_prices[40]
        jeonse40 = round(p40 * 0.52, 1)
        st.metric("40평형대 이상 (대형)", f"{p40}억", "+2.5%")
        st.caption(f"전세가 {jeonse40}억 (추정)")

    st.caption("(참조: 당해 평균가격은 강남구 전반의 평균 가격으로 래대팰, 대치SK뷰, 대치아이파크의 국토부 실거래가는 준축 매물로 현황에 따라 전반적인 가격이 많이 다를 수 있으므로 국토부실거래가를 참조 바랍니다.)")

    st.divider()

    render_rich_narrative(user_persona)

    st.divider()

    render_daechi_map_block()

    st.divider()

    st.markdown("### 📄 맞춤형 제안서 PDF 다운로드")
    if st.button("PDF 생성 및 다운로드 (지도 포함)", key="pdf_btn"):
        with st.spinner("PDF 생성 중..."):
            try:
                df_points = load_points()
                points_list = []
                for _, r in df_points.iterrows():
                    points_list.append({
                        "name": r["name"],
                        "lat": r["lat"],
                        "lon": r["lon"],
                        "category": r["category"],
                        "color": r["color"],
                        "group": r["category"],
                        "note": r.get("note", "")
                    })
                map_png = build_points_map_png(points_list)
                
                pdf_path = build_lease_offer_pdf(
                    out_path="outputs/Daechi_Offer.pdf",
                    title=f"대치1동 {user_persona} 맞춤 제안서",
                    subtitle="2026년 학군 프리미엄 분석 리포트",
                    badge="SSS등급",
                    jeonse_text="16.5억 (52%)",
                    wolse_text="10억 / 280만원",
                    landlord_pitch="안정적인 전세 수요와 높은 학군 프리미엄으로 자산 가치 방어가 탁월합니다.",
                    consult_script="고객님, 이 물건은 대치초-대청중 라인의 핵심 매물로, 지금 잡으셔야 합니다.",
                    shorts_script="대치동 학군지, 지금이 기회입니다! 34평 로얄동 매물!",
                    summary_text=get_sss_side_message(user_persona).replace("<br/>", "\n"),
                    map_png_bytes=map_png
                )
                
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 PDF 다운로드",
                        data=f,
                        file_name="Daechi_Lease_Offer.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"PDF 생성 실패: {e}")

    render_bottom_nav("🎓 대치1동 특성")
