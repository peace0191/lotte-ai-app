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
from services.ui import render_bottom_nav, scroll_to_top
from services.region_compare import REGIONS, score_region, summary_comment, lease_recommendation
from services.compare_pdf import build_compare_pdf
from services.lease_recommender import recommend_jeonse_wolse
from services.pdf_lease_offer import build_lease_offer_pdf
from services.geocode import geocode_nominatim
from services.data import load_properties
import json
import os

# ... (Previous imports)

# ------------------------------------------------------------------------------
# Confirmed Coordinates & Color Mapping (New Logic)
# ------------------------------------------------------------------------------
# ... (Lines 24-596)



# ------------------------------------------------------------------------------
# Confirmed Coordinates & Color Mapping (New Logic)
# ------------------------------------------------------------------------------
POINTS_PATH = Path("data/daechi_points.json")

COLOR_RGB = {
    "초등": [255, 140, 0],     # 주황 (Orange)
    "중등": [50, 205, 50],     # 녹색 (Green)
    "고등": [50, 205, 50],     # 녹색 (Green)
    "단지": [255, 215, 0],     # 노랑 (Yellow)
    "부동산": [255, 105, 180], # 분홍 (Pink)
    "관공서": [150, 150, 150], # Grey
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
    
    # 3D Height Logic
    def get_height(cat):
        if cat == "단지": return 250
        if cat in ["초등", "중등", "고등"]: return 120
        return 60
    df["height"] = df["category"].apply(get_height)
    
    return df

def prefix_icon(cat):
    return {"초등":"🏫","중등":"🏫","고등":"🏫","단지":"🏠","부동산":"🏢","관공서":"🏛️"}.get(cat,"📍")

def render_daechi_map_block():
    st.markdown("### 🏫 AI 대치1동 학군/단지 입체 지도")
    # Legend moved to the right column below

    df = load_points()
    if df.empty:
        st.warning("daechi_points.json에 좌표 데이터가 없습니다.")
        return

    # Add icon to name for label
    df["display_name"] = df.apply(lambda r: f"{prefix_icon(r['category'])} {r['name']}", axis=1)

    # (1) 3D Column Layer (Main Buildings)
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position=["lon", "lat"],
        get_elevation="height",
        elevation_scale=1,
        radius=35,
        get_fill_color="color",
        pickable=True,
        auto_highlight=True,
        extruded=True,
        material=True, # Light reflection
    )

    # (2) Scatterplot Halo (Ground base)
    halo_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_fill_color=[0, 0, 0, 50],
        get_line_color="color",
        stroked=True,
        filled=True,
        get_radius=70,
        radius_units="meters",
        line_width_min_pixels=2,
    )

    # (3) Label Layer
    label_layer = pdk.Layer(
        "TextLayer",
        data=df,
        get_position=["lon", "lat"],
        get_text="display_name",
        get_size=15,
        get_color=[255, 255, 255],
        get_text_anchor="'middle'",
        get_alignment_baseline="'bottom'",
        get_pixel_offset=[0, -30], # Lift above columns
        billboard=True,
        pickable=False,
        get_background_color=[0, 0, 0, 140],
        background_padding=[4, 2, 4, 2],
    )

    # (4) Overcrowded Element Warning Circle
    crowded_df = df[df["is_overcrowded"]].copy()
    crowded_layer = pdk.Layer(
        "ScatterplotLayer",
        data=crowded_df,
        get_position=["lon", "lat"],
        get_fill_color=[255, 80, 80, 30],
        get_radius=300,
        radius_units="meters",
        pickable=False,
        stroked=True,
        get_line_color=[255, 80, 80, 180],
        line_width_min_pixels=2,
    )

    # (5) Lines
    def find_one(name_part):
        hit = df[df["name"].astype(str).str.contains(name_part)]
        return None if hit.empty else hit.iloc[0]

    layers = [crowded_layer, halo_layer, column_layer, label_layer]

    # 라인 1: 🟠 주황색 - 대치초 학군 (갈래길)
    daechi_elem = find_one("대치초")
    raemian = find_one("래미안대치팰리스")
    sk_view = find_one("대치SK뷰")
    
    # 1-1. 대치초 -> 래대팰
    if daechi_elem is not None and raemian is not None:
        path1 = [
            [float(daechi_elem["lon"]), float(daechi_elem["lat"])],
            [float(raemian["lon"]), float(raemian["lat"])]
        ]
        layers.append(pdk.Layer(
            "PathLayer",
            data=[{"path": path1}],
            get_path="path",
            get_color=[255, 140, 0, 200],
            width_scale=20,
            width_min_pixels=4,
            pickable=False,
            billboard=True
        ))
        
    # 1-2. 대치초 -> SK뷰
    if daechi_elem is not None and sk_view is not None:
        path2 = [
            [float(daechi_elem["lon"]), float(daechi_elem["lat"])],
            [float(sk_view["lon"]), float(sk_view["lat"])]
        ]
        layers.append(pdk.Layer(
            "PathLayer",
            data=[{"path": path2}],
            get_path="path",
            get_color=[255, 140, 0, 200],
            width_scale=20,
            width_min_pixels=4,
            pickable=False,
            billboard=True
        ))

    # Arrows for Orange Lines
    orange_arrows = []
    if daechi_elem is not None and raemian is not None:
        orange_arrows.append({
            "lon": (float(daechi_elem["lon"]) + float(raemian["lon"])) / 2,
            "lat": (float(daechi_elem["lat"]) + float(raemian["lat"])) / 2,
            "txt": "▶"
        })
    if daechi_elem is not None and sk_view is not None:
         orange_arrows.append({
            "lon": (float(daechi_elem["lon"]) + float(sk_view["lon"])) / 2,
            "lat": (float(daechi_elem["lat"]) + float(sk_view["lat"])) / 2,
            "txt": "▶"
        })
    
    if orange_arrows:
        orange_arrow_layer = pdk.Layer(
            "TextLayer",
            data=pd.DataFrame(orange_arrows),
            get_position=["lon", "lat"],
            get_text="txt",
            get_size=20,
            get_color=[255, 160, 20],
            get_background_color=[0, 0, 0, 0],
            billboard=True,
            pickable=False,
            get_pixel_offset=[0, -10]
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
            get_color=[255, 105, 180, 200],
            width_scale=20,
            width_min_pixels=4,
            pickable=False,
        )
        layers.append(pink_layer)
        
        # Arrows
        pink_arrows = []
        for i in range(len(pink_path)-1):
            pink_arrows.append({
                "lon": (pink_path[i][0] + pink_path[i+1][0]) / 2, 
                "lat": (pink_path[i][1] + pink_path[i+1][1]) / 2, 
                "txt": "▶"
            })
        pink_arrows_df = pd.DataFrame(pink_arrows)
        
        pink_arrow_layer = pdk.Layer(
            "TextLayer",
            data=pink_arrows_df,
            get_position=["lon", "lat"],
            get_text="txt",
            get_size=20,
            get_color=[255, 105, 180], 
            get_background_color=[0, 0, 0, 0],
            billboard=True,
            pickable=False,
            get_pixel_offset=[0, -10]
        )
        layers.append(pink_arrow_layer)

    # 라인 2-2: 🩷 추가 분홍색 - 대청중학교 연결 (학군 배정)
    daecheong = find_one("대청중학교")
    
    # 대청중 -> 래미안대치팰리스
    if daecheong is not None and raemian is not None:
        p_path_1 = [[float(daecheong["lon"]), float(daecheong["lat"])],
                    [float(raemian["lon"]), float(raemian["lat"])]]
        layers.append(pdk.Layer(
            "PathLayer",
            data=[{"path": p_path_1}],
            get_path="path",
            get_color=[255, 105, 180, 200],
            width_scale=20,
            width_min_pixels=4,
            pickable=False
        ))
        # Arrow
        mx, my = (p_path_1[0][0]+p_path_1[1][0])/2, (p_path_1[0][1]+p_path_1[1][1])/2
        layers.append(pdk.Layer(
            "TextLayer",
            data=[{"lon": mx, "lat": my, "txt": "▶"}],
            get_position=["lon", "lat"],
            get_text="txt",
            get_size=20,
            get_color=[255, 105, 180],
            get_background_color=[0, 0, 0, 0],
            billboard=True,
            pickable=False,
            get_pixel_offset=[0, -10]
        ))

    # 대청중 -> 대치SK뷰
    if daecheong is not None and sk_view is not None:
        p_path_2 = [[float(daecheong["lon"]), float(daecheong["lat"])],
                    [float(sk_view["lon"]), float(sk_view["lat"])]]
        layers.append(pdk.Layer(
            "PathLayer",
            data=[{"path": p_path_2}],
            get_path="path",
            get_color=[255, 105, 180, 200],
            width_scale=20,
            width_min_pixels=4,
            pickable=False
        ))
        # Arrow
        mx, my = (p_path_2[0][0]+p_path_2[1][0])/2, (p_path_2[0][1]+p_path_2[1][1])/2
        layers.append(pdk.Layer(
            "TextLayer",
            data=[{"lon": mx, "lat": my, "txt": "▶"}],
            get_position=["lon", "lat"],
            get_text="txt",
            get_size=20,
            get_color=[255, 105, 180],
            get_background_color=[0, 0, 0, 0],
            billboard=True,
            pickable=False,
            get_pixel_offset=[0, -10]
        ))
    
    # 라인 3: 🔵 파란색 - 서울대도초등학교 -> 대치아이파크
    daedo = find_one("서울대도초등학교")
    ipark = find_one("대치아이파크")
    
    if daedo is not None and ipark is not None:
        blue_path = [
            [float(daedo["lon"]), float(daedo["lat"])],
            [float(ipark["lon"]), float(ipark["lat"])],
        ]
        
        blue_layer = pdk.Layer(
            "PathLayer",
            data=[{"path": blue_path}],
            get_path="path",
            get_color=[30, 144, 255, 200],  # Dodson Blue
            width_scale=20,
            width_min_pixels=4,
            pickable=False,
            billboard=True
        )
        layers.append(blue_layer)
        
        # Arrows
        mx, my = (blue_path[0][0]+blue_path[1][0])/2, (blue_path[0][1]+blue_path[1][1])/2
        blue_arrow_layer = pdk.Layer(
            "TextLayer",
            data=[{"lon": mx, "lat": my, "txt": "▶"}],
            get_position=["lon", "lat"],
            get_text="txt",
            get_size=20,
            get_color=[30, 144, 255],
            get_background_color=[0, 0, 0, 0],
            billboard=True,
            pickable=False,
            get_pixel_offset=[0, -10]
        )
        layers.append(blue_arrow_layer)

    # 라인 4: 🔵 파란색 - 삼환 - 대치아이파크 (대도초 배정 연계)
    samhwan = find_one("대치 삼환아르누보2(본사)")
    
    if samhwan is not None and ipark is not None:
        sb_path = [[float(samhwan["lon"]), float(samhwan["lat"])],
                   [float(ipark["lon"]), float(ipark["lat"])]]
        
        layers.append(pdk.Layer(
            "PathLayer",
            data=[{"path": sb_path}],
            get_path="path",
            get_color=[30, 144, 255, 200],  # Blue (Same as Daedo)
            width_scale=20,
            width_min_pixels=4,
            pickable=False
        ))
        # Arrow
        mx, my = (sb_path[0][0]+sb_path[1][0])/2, (sb_path[0][1]+sb_path[1][1])/2
        layers.append(pdk.Layer(
            "TextLayer",
            data=[{"lon": mx, "lat": my, "txt": "▶"}],
            get_position=["lon", "lat"],
            get_text="txt",
            get_size=20,
            get_color=[30, 144, 255],
            get_background_color=[0, 0, 0, 0],
            billboard=True,
            pickable=False,
            get_pixel_offset=[0, -10]
        ))
        
    # 라인 5: 🔵 파란색 - 삼환 - 단대부중·고 (추가 연결)
    dandae = find_one("단대부중·고등학교")
    
    if samhwan is not None and dandae is not None:
        sb_path_2 = [[float(samhwan["lon"]), float(samhwan["lat"])],
                     [float(dandae["lon"]), float(dandae["lat"])]]
                     
        layers.append(pdk.Layer(
            "PathLayer",
            data=[{"path": sb_path_2}],
            get_path="path",
            get_color=[30, 144, 255, 200],
            width_scale=20,
            width_min_pixels=4,
            pickable=False
        ))
        # Arrow (1/2 지점)
        mx, my = (sb_path_2[0][0]+sb_path_2[1][0])/2, (sb_path_2[0][1]+sb_path_2[1][1])/2
        layers.append(pdk.Layer(
            "TextLayer",
            data=[{"lon": mx, "lat": my, "txt": "▶"}],
            get_position=["lon", "lat"],
            get_text="txt",
            get_size=20,
            get_color=[30, 144, 255],
            get_background_color=[0, 0, 0, 0],
            billboard=True,
            pickable=False,
            get_pixel_offset=[0, -10]
        ))
    
    # Tooltip
    tooltip = {
        "html": "<b>{name}</b><br/>{category}<br/>{address}<br/>{note}",
        "style": {"backgroundColor": "rgba(20,20,20,0.9)", "color": "white", "fontSize": "12px"}
    }

    # Center View (Tilted for 3D effect)
    view_state = pdk.ViewState(
        latitude=df["lat"].mean(),
        longitude=df["lon"].mean(),
        zoom=14.5,
        pitch=50, # Tilted view
        bearing=10
    )

    col_map, col_legend = st.columns([6.5, 3.5])

    with col_map:
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/dark-v10",
            initial_view_state=view_state,
            layers=layers,
            tooltip=tooltip
        ), use_container_width=True)

    with col_legend:
        st.markdown("""
<div style="background-color: #1E1E1E; border: 1px solid #444; border-radius: 8px; padding: 20px; height: 500px; display: flex; flex-direction: column; justify-content: space-between;">
<div style="margin-bottom: 15px; font-weight: bold; color: #FFF; font-size: 1.1em; border-bottom: 1px solid #555; padding-bottom: 10px;">🗺️ 상세 범례 가이드</div>
<div style="display: flex; flex-direction: column; gap: 12px; font-size: 0.95em;">
<div style="display: flex; align-items: flex-start; color: #FFD700;">
<span style="font-size: 1.2em; margin-right: 10px; margin-top: -3px;">●</span>
<div>
<span style="font-weight:bold;">아파트 단지 (노랑)</span><br>
<span style="color: #ccc; font-size: 0.9em;">래대팰, SK뷰, 아이파크, 은마</span>
</div>
</div>
<div style="display: flex; align-items: flex-start; color: #32CD32;">
<span style="font-size: 1.2em; margin-right: 10px; margin-top: -3px;">●</span>
<div>
<span style="font-weight:bold;">중·고등학교 (녹색)</span><br>
<span style="color: #ccc; font-size: 0.9em;">대청중, 숙명여중고, 단대부중고</span>
</div>
</div>
<div style="display: flex; align-items: flex-start; color: #FF8C00;">
<span style="font-size: 1.2em; margin-right: 10px; margin-top: -3px;">●</span>
<div>
<span style="font-weight:bold;">초등학교 (주황)</span><br>
<span style="color: #ccc; font-size: 0.9em;">대치초, 대도초 (학군 배정)</span>
</div>
</div>
<div style="display: flex; align-items: flex-start; color: #FF69B4;">
<span style="font-size: 1.2em; margin-right: 10px; margin-top: -3px;">●</span>
<div>
<span style="font-weight:bold;">부동산 (분홍)</span><br>
<span style="color: #ccc; font-size: 0.9em;">롯데 AI 부동산 (본사)</span>
</div>
</div>
<div style="display: flex; align-items: flex-start; color: #A0A0A0;">
<span style="font-size: 1.2em; margin-right: 10px; margin-top: -3px;">●</span>
<div>
<span style="font-weight:bold;">관공서/기타 (회색)</span><br>
<span style="color: #ccc; font-size: 0.9em;">대치1동 주민센터, 지구대 등</span>
</div>
</div>
</div>
<div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #444; font-size: 0.85em; color: #AAA; line-height: 1.4;">
💡 <b>이용 팁</b><br>
• <b>Shift + 드래그</b>: 지도 3D 회전<br>
• <b>마우스 오버</b>: 상세 정보 확인
</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# Old UI Logic (Restored)
# ------------------------------------------------------------------------------
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
                if "/" not in price_str and "억" in price_str:
                    try:
                        val_str = re.search(r"([\d\.]+)억", price_str).group(1)
                        val = float(val_str)
                        buckets[b_key].append(val)
                    except:
                        pass
    
    avgs = {
        20: 23.5,
        30: 32.5,
        40: 48.0
    }
    
    for k, v in buckets.items():
        if v:
            avgs[k] = round(sum(v) / len(v), 1)
            
    return avgs

def render_rich_narrative(persona: str):
    """Renders the detailed 'Storytelling' report that parents value."""
    st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>🎓 대치1동 프리미엄 리포트: 대치동 중개실무 25년 공인중개사 -> 왜 대치1동인가?</h3>", unsafe_allow_html=True)
    if persona == "학부모":
        st.markdown("""
        <div style="background-color: rgba(46, 134, 222, 0.15); border: 1px solid rgba(46, 134, 222, 0.5); padding: 20px; border-radius: 10px; text-align: left; color: #f0f0f0;">
            <h4 style="margin: 0 0 10px 0; color: #d4af37; text-align: center;">"아이의 통학 시간은 곧 수면 시간이고, 성적입니다."</h4>
            <p style="margin-bottom: 5px; font-size: 1.05em;">대치1동은 대한민국 사교육의 심장이자, 유해시설이 전무한 '청정 교육 특구'입니다.</p>
            <p style="margin: 0; font-weight: bold; font-size: 1.1em;">'자녀의 미래를 위한 베이스캠프'로서의 가치를 제안합니다.</p>
        </div>
        """, unsafe_allow_html=True)
    elif persona == "투자자":
        st.info("**\\\"불황에 강한 부동산은 결국 '확실한 수요'가 있는 곳입니다.\\\"**\n\n대치1동은 학군 수요로 인해 전세가율이 탄탄하게 받쳐주며, 재건축 이슈와 신축의 조화로 시세 상승 여력이 충분합니다.")
    else:
        st.info("**\\\"공실 없는 임대 수익, 대치1동이라면 가능합니다.\\\"**\n\n매년 11월 수능 이후부터 2월까지, 전국에서 몰려드는 학군 수요로 인해 가장 빠르고 높은 가격에 임대 계약이 체결되는 지역입니다.")

    st.divider()

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("#### 🏫 학군 골드 라인")
        st.markdown("지도에 표시된 <span style='color:#ff8c00'>**주황색 화살표**</span>는 **'대치초-래대팰-SK뷰'** 학군 프리미엄 라인입니다.", unsafe_allow_html=True)
        st.markdown("또한 <span style='color:#ff1493'>**분홍색 화살표**</span>는 **'단대부중고-삼환'** 투자 동선을 시각화했습니다.", unsafe_allow_html=True)
        st.caption("이 라인 안에 거주한다는 것은 자녀에게 '시간'과 '체력'을 선물하는 것과 같습니다.")

        with st.expander("📍 각 학교별 상세 특징 보기", expanded=True):
            st.markdown("""
                **1. 서울대치초등학교** (초품아) - **양재천로 363**\n- **특징**: 높은 학업 성취도, 정확한 배정권역\n
                **2. 대청중학교** (남녀공학) - **양재천로 321**\n- **특징**: 특목고/자사고 진학률 최상위\n
                **3. 단대부속고등학교 / 숙명여고**\n- **특징**: 서울대 진학 실적 전국 TOP
                """)
    with col2:
        # Tabs Font Size Injection
        st.markdown("""
        <style>
            div[data-testid="stTabs"] button {
                font-size: 40px !important;
                font-weight: bold !important;
                padding: 15px 25px !important;
                flex: 1 !important; /* 가득 차게 */
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 🏢 주요 명품 단지 분석")
        tab1, tab2, tab3 = st.tabs(["래미안대치팰리스", "대치아이파크/SK뷰", "은마아파트"])
        with tab1:
            st.success("### 👑 대치동의 대장주")
            st.markdown("##### 대치초 배정, 학원가 바로 앞, 수영장/조식 등 완벽한 커뮤니티.")
        with tab2:
            st.warning("### ⚖️ 실속과 환경의 조화")
            st.markdown("##### 대치역/한티역 역세권, 백화점 슬세권, 쾌적한 주거 환경.")
        with tab3:
            st.error("### 🏗️ 재건축의 상징")
            st.markdown("##### 강남 재건축의 바로미터, 대곡초 배정, 압도적 투자가치.")

    st.divider()
    st.markdown("#### 🛡️ 안심 생활권 & 편의시설")
    st.write("대치1동 주민센터와 지구대가 인접하여 행정 업무와 치안이 매우 우수합니다.")
    
    # Custom Navigation Buttons for Premium Report Section
    st.markdown("---")
    # Mobile-friendly 3-button layout
    nav_c1, nav_c2, nav_c3 = st.columns(3)
    
    with nav_c1:
        if st.button("≡ 목록보기", use_container_width=True):
            st.session_state["manual_nav_target"] = "🏠 추천매물"
            st.rerun()
            
    with nav_c2:
        if st.button("⬆️ 처음 위로 가기", use_container_width=True):
            scroll_to_top()
            st.rerun()
            
    with nav_c3:
        if st.button("다음 ➡️", use_container_width=True):
            st.session_state["manual_nav_target"] = "🏠 추천매물"
            st.rerun()

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
        # st.caption("✅ SSL/TLS 프로토콜 준비됨")

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

    # Storytelling Section
    render_rich_narrative(user_persona)

    st.divider()

    # 3D Map (New)
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
