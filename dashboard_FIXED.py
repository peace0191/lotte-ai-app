from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
from services.map_image import build_points_map_png
from pathlib import Path
import datetime
from services.ui import render_bottom_nav
from services.region_compare import REGIONS, score_region, summary_comment, lease_recommendation
from services.compare_pdf import build_compare_pdf
from services.lease_recommender import recommend_jeonse_wolse
from services.pdf_lease_offer import build_lease_offer_pdf
from services.geocode import geocode_nominatim
import json
import os

# ------------------------------------------------------------------------------
# NEW: Confirmed Coordinates Map Rendering (Source of Truth)
# ------------------------------------------------------------------------------
POINTS_PATH = Path("data/daechi_points.json")

COLOR_RGB = {
    "초등": [255, 99, 71],     # red-ish
    "중등": [50, 205, 50],     # green
    "고등": [65, 105, 225],    # blue
    "단지": [255, 215, 0],     # yellow
    "부동산": [186, 85, 211],  # purple
    "관공서": [150, 150, 150], # grey
}

def load_points():
    if not POINTS_PATH.exists():
        return pd.DataFrame()
    items = json.loads(POINTS_PATH.read_text(encoding="utf-8"))
    df = pd.DataFrame(items)
    # Filter for valid lat/lon
    df = df.dropna(subset=["lat", "lon"]).copy()
    # Normalize category names - use apply instead of fillna
    df["color"] = df["category"].apply(lambda x: COLOR_RGB.get(x, [200, 200, 200]))
    # Check for "Overcrowded" note
    df["is_overcrowded"] = df.get("note", "").fillna("").astype(str).str.contains("과밀")
    return df

def prefix_icon(cat):
    return {"초등":"🏫","중등":"🏫","고등":"🏫","단지":"🏠","부동산":"🏢","관공서":"🏛️"}.get(cat,"📍")

def render_daechi_map_block():
    st.markdown("### 🏫 학군 및 인프라 (정확 좌표 확정본 기준)")

    df = load_points()
    if df.empty:
        st.warning("daechi_points.json에 좌표 데이터가 없습니다.")
        return

    # Add icon to name for label
    df["display_name"] = df.apply(lambda r: f"{prefix_icon(r['category'])} {r['name']}", axis=1)

    # (1) Point Layer
    point_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_fill_color="color",
        get_radius=120,  # 60 → 120으로 증가 (더 잘 보임)
        radius_units="meters",
        pickable=True,
        auto_highlight=True,
        opacity=0.9,  # 약간 투명도 추가
        stroked=True,  # 테두리 추가
        get_line_color=[255, 255, 255],  # 흰색 테두리
        line_width_min_pixels=2,  # 테두리 두께
    )

    # (2) Label Layer
    label_layer = pdk.Layer(
        "TextLayer",
        data=df,
        get_position=["lon", "lat"],
        get_text="display_name",
        get_size=16,  # 13 → 16으로 증가 (더 잘 보임)
        get_color=[255, 255, 255],  # 순백색으로 변경
        get_text_anchor="'start'",
        get_alignment_baseline="'center'",
        get_pixel_offset=[12, 0],  # 10 → 12로 약간 더 띄움
        billboard=True,
        pickable=False,
        get_background_color=[0, 0, 0, 120],  # 반투명 검은색 배경 추가
        background_padding=[4, 2, 4, 2],  # 배경 패딩
    )

    # (3) Overcrowded Element Warning Circle
    crowded_df = df[df["is_overcrowded"]].copy()
    crowded_layer = pdk.Layer(
        "ScatterplotLayer",
        data=crowded_df,
        get_position=["lon", "lat"],
        get_fill_color=[255, 80, 80, 40],  # Semi-transparent red
        get_radius=350,                    # 350m radius warning
        radius_units="meters",
        pickable=False,
        stroked=True,
        get_line_color=[255, 80, 80, 180],
        line_width_min_pixels=2,
    )

    # (4) 새로운 라인 2개 추가
    def find_one(name_part):
        hit = df[df["name"].astype(str).str.contains(name_part)]
        return None if hit.empty else hit.iloc[0]

    layers = [crowded_layer, point_layer, label_layer]

    # 라인 1: 🟠 주황색 - 대치초 → 래미안대치팰리스 → 대치SK뷰
    daechi_elem = find_one("대치초")
    raemian = find_one("래미안대치팰리스")
    sk_view = find_one("대치SK뷰")
    
    if daechi_elem is not None and raemian is not None and sk_view is not None:
        orange_path = [
            [float(daechi_elem["lon"]), float(daechi_elem["lat"])],
            [float(raemian["lon"]), float(raemian["lat"])],
            [float(sk_view["lon"]), float(sk_view["lat"])],
        ]
        
        orange_layer = pdk.Layer(
            "PathLayer",
            data=[{"path": orange_path}],
            get_path="path",
            get_color=[255, 140, 0, 255],  # 주황색 (Orange)
            width_scale=25,
            width_min_pixels=5,
            pickable=False,
        )
        layers.append(orange_layer)
        
        # 주황색 라인 화살표
        orange_arrows = pd.DataFrame([
            {"lon": (orange_path[0][0] + orange_path[1][0]) / 2, 
             "lat": (orange_path[0][1] + orange_path[1][1]) / 2, 
             "txt": "▶"},
            {"lon": (orange_path[1][0] + orange_path[2][0]) / 2, 
             "lat": (orange_path[1][1] + orange_path[2][1]) / 2, 
             "txt": "▶"},
        ])
        
        orange_arrow_layer = pdk.Layer(
            "TextLayer",
            data=orange_arrows,
            get_position=["lon", "lat"],
            get_text="txt",
            get_size=16,
            get_color=[255, 140, 0],  # 주황색
            get_background_color=[0, 0, 0, 120],
            billboard=True,
            pickable=False,
        )
        layers.append(orange_arrow_layer)
    
    # 라인 2: 🩷 분홍색 - 단대부중고 → 대치아이파크 → 래미안 → SK뷰 → 삼환아르누보2
    dandae = find_one("단대부중")
    ipark = find_one("대치아이파크")
    arnuvo = find_one("삼환아르누보")
    
    if dandae is not None and ipark is not None and raemian is not None and sk_view is not None and arnuvo is not None:
        pink_path = [
            [float(dandae["lon"]), float(dandae["lat"])],
            [float(ipark["lon"]), float(ipark["lat"])],
            [float(raemian["lon"]), float(raemian["lat"])],
            [float(sk_view["lon"]), float(sk_view["lat"])],
            [float(arnuvo["lon"]), float(arnuvo["lat"])],
        ]
        
        pink_layer = pdk.Layer(
            "PathLayer",
            data=[{"path": pink_path}],
            get_path="path",
            get_color=[255, 105, 180, 255],  # 분홍색 (Hot Pink)
            width_scale=25,
            width_min_pixels=5,
            pickable=False,
        )
        layers.append(pink_layer)
        
        # 분홍색 라인 화살표
        pink_arrows = pd.DataFrame([
            {"lon": (pink_path[0][0] + pink_path[1][0]) / 2, 
             "lat": (pink_path[0][1] + pink_path[1][1]) / 2, 
             "txt": "▶"},
            {"lon": (pink_path[1][0] + pink_path[2][0]) / 2, 
             "lat": (pink_path[1][1] + pink_path[2][1]) / 2, 
             "txt": "▶"},
            {"lon": (pink_path[2][0] + pink_path[3][0]) / 2, 
             "lat": (pink_path[2][1] + pink_path[3][1]) / 2, 
             "txt": "▶"},
            {"lon": (pink_path[3][0] + pink_path[4][0]) / 2, 
             "lat": (pink_path[3][1] + pink_path[4][1]) / 2, 
             "txt": "▶"},
        ])
        
        pink_arrow_layer = pdk.Layer(
            "TextLayer",
            data=pink_arrows,
            get_position=["lon", "lat"],
            get_text="txt",
            get_size=16,
            get_color=[255, 105, 180],  # 분홍색
            get_background_color=[0, 0, 0, 120],
            billboard=True,
            pickable=False,
        )
        layers.append(pink_arrow_layer)
    
    # Tooltip
    tooltip = {
        "html": "<b>{name}</b><br/>{category}<br/>{address}<br/>{note}",
        "style": {"backgroundColor": "rgba(20,20,20,0.9)", "color": "white", "fontSize": "12px"}
    }

    # Center View
    view_state = pdk.ViewState(
        latitude=df["lat"].mean(),
        longitude=df["lon"].mean(),
        zoom=14.2,  # 13.8 → 14.2로 증가 (더 확대)
        pitch=0
    )

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=view_state,
        layers=layers,
        tooltip=tooltip
    ), use_container_width=True)

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
        else:
            return float(p_str) / 100000000 
    except:
        return 0

def get_sss_side_message(persona: str) -> str:
    if persona == "학부모":
        return (
            "• 도보 통학/학원가 접근으로 '시간 가치' 극대화<br/>"
            "• 입학 시즌 수요 집중 → 공실 리스크 최소화<br/>"
            "• 대치초—대청중—단대부 라인의 확실한 배정권"
        )
    elif persona == "투자자":
        return (
            "• 비탄력 수요 기반의 가격 방어력<br/>"
            "• 하락장에서도 거래 지속되는 코어 학군지<br/>"
            "• 전·월세 전환 모두 유연한 수익 구조"
        )
    else:  # 임대인
        return (
            "• 학기 시즌 대기 수요 풍부<br/>"
            "• 전세: 빠른 계약 / 월세: 수익 최적화<br/>"
            "• 조건만 맞으면 즉시 선점 가능"
        )

# ------------------------------------------------------------------------------
# ✅ NEW: render() 함수 추가 (app.py 호환성)
# ------------------------------------------------------------------------------
def render(properties=None):
    """
    app.py에서 pg_dash.render(properties) 호출 시 사용되는 함수
    실제로는 render_dashboard()를 호출합니다.
    """
    render_dashboard()

# ------------------------------------------------------------------------------
# Dashboard Main Logic
# ------------------------------------------------------------------------------
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

    # Header
    st.title(f"대치1동 AI 부동산 대시보드 ({user_persona})")
    st.markdown(f"**{user_persona}**님을 위한 맞춤형 분석 리포트입니다.")

    # Top Stats
    col1, col2, col3 = st.columns(3)
    # Mock data for demonstration
    col1.metric("평균 매매가 (34평)", "32.5억", "+1.2%")
    col2.metric("평균 전세가 (34평)", "16.8억", "-0.5%")
    col3.metric("학군 프리미엄 지수", "98/100", "최고")

    st.divider()

    # Layout: Map + List
    col_map, col_list = st.columns([2, 1])

    with col_map:
        # Call the new map block
        render_daechi_map_block()

    with col_list:
        st.markdown("### 📋 주요 단지 시세")
        # Load points to show list
        df_points = load_points()
        if not df_points.empty:
            # Simple dataframe view
            st.dataframe(
                df_points[["category", "name", "note"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("데이터 로딩 중...")

        st.info(get_sss_side_message(user_persona))

    st.divider()

    # PDF Generation Section
    st.markdown("### 📄 맞춤형 제안서 PDF (지도 포함)")
    
    col_pdf, col_dummy = st.columns([1, 2])
    with col_pdf:
        if st.button("PDF 생성 및 다운로드", key="pdf_btn"):
            with st.spinner("PDF 생성 중... (지도 캡처 포함)"):
                try:
                    # 1. Generate Map PNG
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
                    
                    # 2. Build PDF
                    # Mocking params for demonstration stability
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
                            label="📥 PDF 다운로드 완료",
                            data=f,
                            file_name="Daechi_Lease_Offer.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"PDF 생성 실패: {e}")

    render_bottom_nav("대시보드")
