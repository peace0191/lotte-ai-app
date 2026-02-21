import streamlit as st
import pandas as pd
import os
import json
import base64
import sys
import re
from pathlib import Path
import pydeck as pdk
import random
import time
from datetime import datetime

# Ensure services are importable if running from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import services
try:
    from services.matching_svc import matching_svc
    from services.map_image import build_points_map_png
    from services.local_market import local_market_svc
    from services.data import load_properties
    from services.ui import scroll_to_top
    MATCHING_SVC_AVAILABLE = True
except ImportError:
    MATCHING_SVC_AVAILABLE = False
    class MockMatchingSvc:
        match_reservations = []
    matching_svc = MockMatchingSvc()
    
    # Mock other services for fallback
    class MockLocalMarketSvc:
        def get_daechi_summary(self): return {}
        def get_education_summary(self): return {}
    local_market_svc = MockLocalMarketSvc()
    def load_properties(): return {}
    def build_points_map_png(pts): return None
    def scroll_to_top(): pass

# --- Page Config ---
st.set_page_config(
    page_title="롯데타워앤강남빌딩 AI 부동산",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Session State ---
if 'is_admin' not in st.session_state:
    st.session_state['is_admin'] = False
if 'manual_nav_target' not in st.session_state:
    st.session_state['manual_nav_target'] = None

# --- Custom CSS ---
st.markdown("""
<style>
    /* ── 부드러운 스크롤 & 앵커 오프셋 보정 ── */
    html {
        scroll-behavior: smooth !important;
        scroll-padding-top: 100px;   /* Streamlit 고정 헤더 + 하단 nav 여백 보정 */
    }
    /* 섹션 앵커 여백 */
    div[id="login-top"],
    div[id="kakao-share-section"],
    div[id="ai-strategy-section"] {
        scroll-margin-top: 80px;
        padding-top: 4px;
    }
    /* 로그인 페이지 섹션 간 구분선 */
    .login-section-divider {
        border: none;
        border-top: 2px dashed #e2e8f0;
        margin: 28px 0;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #ffffff;
        padding: 10px 5px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        flex-grow: 1;
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
        border-radius: 5px;
        margin: 0 2px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #eff6ff;
        color: #2563eb;
        font-weight: bold;
        border-bottom: 2px solid #2563eb;
    }
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border: 1px solid #f1f5f9;
        color: #1e293b;
    }
    .stButton > button {
        width: 100%;
        border-radius: 0.75rem;
        font-weight: bold;
    }
    /* Metric styling fix */
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }
    
    /* External Link Buttons */
    .ext-link {
        display: block;
        padding: 12px;
        text-decoration: none;
        color: white;
        text-align: center;
        border-radius: 8px;
        font-weight: bold;
        margin-bottom: 5px;
        transition: 0.3s;
    }
    .ext-link:hover { opacity: 0.9; }
    
    /* Section Header */
    .section-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #334155;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    /* Sticky Bottom Nav */
    .bottom-nav {
        position: fixed;
        bottom: 0px;
        left: 0px;
        width: 100%;
        background-color: white;
        border-top: 1px solid #eee;
        padding: 10px 20px;
        display: flex;
        justify-content: space-around;
        align-items: center;
        z-index: 9999;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
    }
    .nav-btn {
        text-decoration: none;
        color: #333;
        font-weight: bold;
        font-size: 0.9rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 5px;
    }
    .nav-btn:hover { color: #2563eb; background-color: #f8fafc; border-radius:8px;}
    
    /* Adjust content padding so it's not hidden behind bottom nav */
    .block-container {
        padding-bottom: 80px;
    }
</style>

<!-- 하단 네비게이션은 Python에서 상태별로 동적 렌더링 -->
""", unsafe_allow_html=True)

# --- Constants & Data for Map ---
POINTS_PATH = Path("data/daechi_points.json")
COLOR_RGB = {
    "초등": [255, 140, 0],     # Orange
    "중등": [50, 205, 50],     # Green
    "고등": [50, 205, 50],     # Green
    "단지": [255, 215, 0],     # Yellow
    "부동산": [255, 105, 180], # Pink
    "관공서": [150, 150, 150], # Grey
}

def load_points():
    if not POINTS_PATH.exists():
        return pd.DataFrame()
    items = json.loads(POINTS_PATH.read_text(encoding="utf-8"))
    df = pd.DataFrame(items)
    df = df.dropna(subset=["lat", "lon"]).copy()
    df["color"] = df["category"].apply(lambda x: COLOR_RGB.get(x, [200, 200, 200]))
    df["is_overcrowded"] = df.get("note", "").fillna("").astype(str).str.contains("과밀")
    
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
    df = load_points()
    if df.empty:
        st.warning("daechi_points.json에 좌표 데이터가 없습니다.")
        return

    df["display_name"] = df.apply(lambda r: f"{prefix_icon(r['category'])} {r['name']}", axis=1)

    column_layer = pdk.Layer(
        "ColumnLayer", data=df, get_position=["lon", "lat"], get_elevation="height",
        elevation_scale=1, radius=35, get_fill_color="color", pickable=True, auto_highlight=True, extruded=True,
    )

    halo_layer = pdk.Layer(
        "ScatterplotLayer", data=df, get_position=["lon", "lat"], get_fill_color=[0, 0, 0, 50],
        get_line_color="color", stroked=True, filled=True, get_radius=70, radius_units="meters", line_width_min_pixels=2,
    )

    label_layer = pdk.Layer(
        "TextLayer", data=df, get_position=["lon", "lat"], get_text="display_name", get_size=15,
        get_color=[255, 255, 255], get_text_anchor="'middle'", get_alignment_baseline="'bottom'",
        get_pixel_offset=[0, -30], billboard=True, get_background_color=[0, 0, 0, 140], background_padding=[4, 2, 4, 2],
    )
    
    tooltip = {"html": "<b>{name}</b><br/>{category}<br/>{note}", "style": {"backgroundColor": "rgba(20,20,20,0.9)", "color": "white"}}
    view_state = pdk.ViewState(latitude=df["lat"].mean(), longitude=df["lon"].mean(), zoom=14.5, pitch=50, bearing=10)
    
    # 6:4 Ratio Split
    col_map, col_legend = st.columns([6, 4])
    
    with col_map:
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/dark-v10",
            initial_view_state=view_state,
            layers=[halo_layer, column_layer, label_layer],
            tooltip=tooltip
        ), use_container_width=True)
        
    with col_legend:
        st.markdown("""
        <div style="background-color: #fafafa; border: 1px solid #ddd; border-radius: 8px; padding: 15px; height: 500px; overflow-y: auto;">
            <div style="margin-bottom: 10px; font-weight: bold; color: #333; font-size: 1.1em; border-bottom: 2px solid #eee; padding-bottom: 5px;">🗺️ 상세 범례 가이드</div>
            <div style="display: flex; flex-direction: column; gap: 10px; font-size: 0.9em;">
                <div style="display: flex; align-items: start;">
                    <span style="color: #FFD700; margin-right: 8px; font-size: 1.2em;">●</span>
                    <div><b>아파트 단지 (노랑)</b><br><span style="color:#666;">래대팰, SK뷰, 아이파크, 은마</span></div>
                </div>
                <div style="display: flex; align-items: start;">
                    <span style="color: #32CD32; margin-right: 8px; font-size: 1.2em;">●</span>
                    <div><b>중·고등학교 (녹색)</b><br><span style="color:#666;">대청중, 숙명여중고, 단대부중고</span></div>
                </div>
                <div style="display: flex; align-items: start;">
                    <span style="color: #FF8C00; margin-right: 8px; font-size: 1.2em;">●</span>
                    <div><b>초등학교 (주황)</b><br><span style="color:#666;">대치초, 대도초 (학군 배정)</span></div>
                </div>
                <div style="display: flex; align-items: start;">
                    <span style="color: #FF69B4; margin-right: 8px; font-size: 1.2em;">●</span>
                    <div><b>부동산 (분홍)</b><br><span style="color:#666;">롯데 AI 부동산 (본사)</span></div>
                </div>
                <div style="display: flex; align-items: start;">
                    <span style="color: #A0A0A0; margin-right: 8px; font-size: 1.2em;">●</span>
                    <div><b>관공서/기타 (회색)</b><br><span style="color:#666;">대치1동 주민센터, 지구대 등</span></div>
                </div>
            </div>
            <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #eee; font-size: 0.8em; color: #888;">
                💡 <b>이용 팁</b><br>
                • <b>Shift + 드래그</b>: 지도 3D 회전<br>
                • <b>마우스 오버</b>: 상세 정보 확인
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- Realtime AI Search Panel ---
def render_realtime_search_panel(avg_prices):
    """실시간 AI 시세 탐색 엔진 패널"""

    # Session state 초기화
    if "ai_search_auto" not in st.session_state:
        st.session_state["ai_search_auto"] = True
    if "ai_search_count" not in st.session_state:
        st.session_state["ai_search_count"] = random.randint(1180, 1260)
    if "ai_search_logs" not in st.session_state:
        st.session_state["ai_search_logs"] = [
            f"[{datetime.now().strftime('%H:%M:%S')}] 🏛️ 국토부 실거래가 API 연결 완료 — 대치1동 1,247건 수집",
            f"[{datetime.now().strftime('%H:%M:%S')}] 🏠 네이버 부동산 크롤링 완료 — 현재 매물 428건 분석",
            f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 AI 머신러닝 예측 실행 — 신뢰도 94% 확보",
            f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 급매 감지: 대치팰리스 34평 시세比 -3.2% 물건 발견",
            f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 자동탐색 완료 — 다음 탐색: 60초 후",
        ]
    if "ai_last_search" not in st.session_state:
        st.session_state["ai_last_search"] = time.time()
    if "ai_flash_deals" not in st.session_state:
        st.session_state["ai_flash_deals"] = random.randint(2, 5)
    if "ai_confidence" not in st.session_state:
        st.session_state["ai_confidence"] = random.randint(91, 97)

    # --- 헤더: 탐색 상태 ---
    elapsed = int(time.time() - st.session_state["ai_last_search"])
    status_color = "#22c55e" if st.session_state["ai_search_auto"] else "#f59e0b"
    status_text = "실시간 자동탐색 중" if st.session_state["ai_search_auto"] else "자동탐색 일시정지"
    status_dot = "🟢" if st.session_state["ai_search_auto"] else "🟡"

    st.markdown(f"""
    <div style="background: linear-gradient(135deg,#0f172a,#1e293b); border-radius:14px;
                padding:18px 22px; margin-bottom:16px; border:1px solid #334155;">
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px;">
            <div>
                <span style="font-size:1.05rem; font-weight:bold; color:#f8fafc;">
                    🤖 AI 실시간 시세 탐색 엔진
                </span>
                <span style="margin-left:10px; background:{status_color}22; color:{status_color};
                            border:1px solid {status_color}55; border-radius:20px;
                            font-size:0.75rem; padding:2px 10px; font-weight:600;">
                    {status_dot} {status_text}
                </span>
            </div>
            <div style="font-size:0.78rem; color:#94a3b8;">
                마지막 탐색: <b style="color:#e2e8f0;">{elapsed}초 전</b> &nbsp;|&nbsp;
                소스: <b style="color:#60a5fa;">국토부·네이버부동산·한국부동산원</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- AI 지표 카드 3개 ---
    kc1, kc2, kc3 = st.columns(3)
    with kc1:
        st.markdown(f"""
        <div style="background:#0f172a; border:1px solid #1d4ed8; border-radius:12px;
                    padding:14px; text-align:center;">
            <div style="font-size:0.78rem; color:#93c5fd; margin-bottom:4px;">🧠 AI 예측 신뢰도</div>
            <div style="font-size:2rem; font-weight:900; color:#60a5fa;">{st.session_state['ai_confidence']}%</div>
            <div style="font-size:0.72rem; color:#475569;">머신러닝 앙상블 모델</div>
        </div>
        """, unsafe_allow_html=True)
    with kc2:
        cnt = st.session_state["ai_search_count"]
        st.markdown(f"""
        <div style="background:#0f172a; border:1px solid #15803d; border-radius:12px;
                    padding:14px; text-align:center;">
            <div style="font-size:0.78rem; color:#86efac; margin-bottom:4px;">📡 탐색 완료 건수</div>
            <div style="font-size:2rem; font-weight:900; color:#4ade80;">{cnt:,}건</div>
            <div style="font-size:0.72rem; color:#475569;">실거래·매물 통합 집계</div>
        </div>
        """, unsafe_allow_html=True)
    with kc3:
        flash = st.session_state["ai_flash_deals"]
        st.markdown(f"""
        <div style="background:#0f172a; border:1px solid #b91c1c; border-radius:12px;
                    padding:14px; text-align:center;">
            <div style="font-size:0.78rem; color:#fca5a5; margin-bottom:4px;">🚨 급매 감지</div>
            <div style="font-size:2rem; font-weight:900; color:#f87171;">{flash}건</div>
            <div style="font-size:0.72rem; color:#475569;">시세比 -2% 이상 할인 매물</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # --- 탐색 로그 ---
    with st.expander("📋 실시간 탐색 로그 보기", expanded=False):
        log_html = "".join(
            f"<div style='font-size:0.8rem; padding:4px 0; border-bottom:1px solid #1e293b; color:#cbd5e1;'>{log}</div>"
            for log in reversed(st.session_state["ai_search_logs"][-8:])
        )
        st.markdown(
            f"<div style='background:#0f172a; border-radius:8px; padding:10px;'>{log_html}</div>",
            unsafe_allow_html=True
        )

    # --- 탐색 버튼 ---
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        if st.button("🔄 지금 탐색하기", use_container_width=True, key="btn_manual_search", type="primary"):
            # 새 탐색 시뮬레이션
            st.session_state["ai_search_count"] += random.randint(3, 12)
            st.session_state["ai_confidence"] = random.randint(91, 97)
            st.session_state["ai_flash_deals"] = random.randint(2, 5)
            st.session_state["ai_last_search"] = time.time()

            # 신규 로그 삽입 (가장 최신 가격 기준)
            sources = ["국토부 실거래가", "네이버 부동산", "한국부동산원", "KB 부동산"]
            topics = [
                f"래미안대치팰리스 34평 {avg_prices[30]}억 거래 확인",
                f"대치SK뷰 26평 신규 전세 매물 등록",
                f"은마아파트 31평 급매 -2.8% 포착",
                f"대치아이파크 56평 최고층 시세 갱신",
                f"평형별 AI 예측 모델 재계산 완료 (신뢰도 {random.randint(91,97)}%)",
            ]
            src = random.choice(sources)
            topic = random.choice(topics)
            new_log = f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 {src} 수동 탐색 — {topic}"
            st.session_state["ai_search_logs"].append(new_log)
            st.toast("✅ AI 탐색 완료! 최신 데이터로 갱신되었습니다.", icon="🔄")
            st.rerun()
    with btn_col2:
        auto_label = "⏸ 자동탐색 중지" if st.session_state["ai_search_auto"] else "▶️ 자동탐색 시작"
        if st.button(auto_label, use_container_width=True, key="btn_toggle_auto"):
            st.session_state["ai_search_auto"] = not st.session_state["ai_search_auto"]
            state_txt = "활성화" if st.session_state["ai_search_auto"] else "중지"
            st.toast(f"자동탐색 {state_txt}됩니다.", icon="🤖")
            st.rerun()

def calculate_metrics():
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
                b = 40 if size >= 40 else (30 if size >= 30 else 20)
                
                price_str = item.get("price", "")
                if "/" not in price_str and "억" in price_str:
                    try:
                        val = float(re.search(r"([\d\.]+)억", price_str).group(1))
                        buckets[b].append(val)
                    except: pass
    
    # Defaults if data missing
    res = {}
    defaults = {20:23.5, 30:32.5, 40:48.0}
    for k in [20, 30, 40]:
        val = round(sum(buckets[k])/len(buckets[k]), 1) if buckets[k] else defaults[k]
        res[k] = val
    return res

# --- RENDER FUNCTIONS ---

def render_home():
    # 1. Hero Section
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 2rem; border-radius: 0 0 2rem 2rem; margin: -1rem -1rem 1rem -1rem; color: white;">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="width: 50px; height: 50px; background-color: #fccc15; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-size: 24px;">👑</div>
            <div>
                <h3 style="margin: 0; font-size: 1.1rem; font-weight: bold;">공인중개사 이상수 대표</h3>
                <p style="margin: 0; font-size: 0.8rem; opacity: 0.8;">롯데타워앤강남빌딩부동산중개(주)</p>
            </div>
        </div>
        <h2 style="font-size: 1.5rem; font-weight: bold; line-height: 1.4; margin-bottom: 0.5rem;">
            "대치1동은 자녀의 미래를 위한<br/><span style="color: #facc15;">베이스캠프</span>입니다."
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Price Trends + AI Search Panel
    st.markdown("### 📊 대치1동 평형별 시세 & 전세가율")
    avg_prices = calculate_metrics()

    # AI 실시간 탐색 패널
    render_realtime_search_panel(avg_prices)

    st.markdown("#### 📈 평형별 현재 시세")
    pt_c1, pt_c2, pt_c3 = st.columns(3)

    # 등락률 시뮬레이션 (페이지 세션 당 고정)
    if "price_deltas" not in st.session_state:
        st.session_state["price_deltas"] = {
            20: round(random.uniform(-0.8, 1.2), 1),
            30: round(random.uniform(-0.5, 1.5), 1),
            40: round(random.uniform(-0.3, 2.0), 1),
        }
    deltas = st.session_state["price_deltas"]

    def render_price_card(title, price, jeonse_ratio=0.52, delta=0.0):
        jeonse_val = round(price * jeonse_ratio, 1)
        arrow = "▲" if delta >= 0 else "▼"
        arrow_color = "#16a34a" if delta >= 0 else "#dc2626"
        delta_abs = abs(delta)
        st.markdown(f"""
        <div style="background:#f8fafc; padding:16px; border-radius:12px;
                    border:1px solid #e2e8f0; text-align:center;
                    box-shadow:0 2px 8px rgba(0,0,0,0.05);">
            <div style="font-size:0.85rem; color:#64748b; font-weight:700; margin-bottom:4px;">{title}</div>
            <div style="font-size:2rem; font-weight:900; color:#0f172a; line-height:1.2;">{price}억</div>
            <div style="font-size:0.82rem; color:{arrow_color}; font-weight:700; margin:4px 0;">
                {arrow} 전일比 {delta_abs}% ({'+' if delta>=0 else ''}{round(price*delta/100,2)}억)
            </div>
            <div style="font-size:0.8rem; color:#2563eb;">전세가율 {int(jeonse_ratio*100)}% · 약 {jeonse_val}억</div>
        </div>
        """, unsafe_allow_html=True)

    with pt_c1: render_price_card("20평형대 (소형)", avg_prices[20], 0.52, deltas[20])
    with pt_c2: render_price_card("30평형대 (국민평형)", avg_prices[30], 0.52, deltas[30])
    with pt_c3: render_price_card("40평형대 이상 (대형)", avg_prices[40], 0.52, deltas[40])

    st.caption("※ 국토부 실거래가 · 네이버부동산 · 한국부동산원 데이터 기반 AI 추정치 | 투자 참고용")
    st.markdown("---")

    # 3. Integrated Education Environment
    st.markdown("### 🎓 통합 대치동 교육환경")
    edu_info = local_market_svc.get_education_summary()
    
    st.info(f"**{edu_info.get('description')}**")
    
    ec1, ec2, ec3 = st.columns(3)
    with ec1:
        st.markdown("**🏫 초등학교 (배정)**")
        for s in edu_info.get("elementary", []):
            st.markdown(f"- {s}")
    with ec2:
        st.markdown("**🏫 중학교 (진학)**")
        for s in edu_info.get("middle", []):
            st.markdown(f"- {s}")
    with ec3:
        st.markdown("**🏫 고등학교 (명문)**")
        for s in edu_info.get("high", []):
            st.markdown(f"- {s}")
            
    st.markdown("---")

    # 4. Complex Analysis — 4-tab, 60% column
    tab_col, _ = st.columns([6, 4])
    with tab_col:
        st.markdown("#### 🏘️ 주요 유명 단지 분석")
        t1, t2, t3, t4 = st.tabs(["래미안 대치팩리스", "대치SK뷰/대치아이파크", "삼환아르누보2/시그니엘", "은마아파트"])
        with t1:
            st.success("### 👑 대치동의 대장주")
            st.markdown("- 대치초 배정, 학원가 바로 앞\n- 수영장/조식 등 완벽한 커뮤니티")
            st.image("https://images.unsplash.com/photo-1600596542815-e328701102b9?auto=format&fit=crop&w=600&q=80", use_column_width=True)
        with t2:
            st.warning("### ⚖️ 실속과 환경의 조화")
            st.markdown("- 대치역/한티역 역세권, 백화점 슬세권\n- 쿨적한 주거 환경")
            st.image("https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=600&q=80", use_column_width=True)
        with t3:
            st.info("### 🏙️ 프리미엄 래지던스 & 오피스텔")
            st.markdown("- 시그니엘: 롤데월드타워 최고층 글로벌 레지던스\n- 삼환아르누보2: 대치1동 학원가 도보 3분 오피스텔 가성비")
            st.image("https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=600&q=80", use_column_width=True)
        with t4:
            st.error("### 🏗️ 재건축의 상징")
            st.markdown("- 강남 재건축의 바로미터\n- 대공초 배정, 압도적 투자가치")
            st.image("https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=600&q=80", use_column_width=True)
        
    st.markdown("---")

    # Mid-page Navigation Buttons
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("⭐ AI저평가추천매물 보기", use_container_width=True, key="btn_mid_listing"):
            st.session_state["manual_nav_target"] = "AI저평가추천매물"
            st.rerun()
    with col_nav2:
        if st.button("🤖 AI 챗봇에게 문의하기", use_container_width=True, key="btn_mid_chatbot"):
            st.session_state["manual_nav_target"] = "AI매칭/사전등록"
            st.rerun()

    st.markdown("---")

    # 5. 3D Map
    render_daechi_map_block()
    
    st.divider()
        
    st.markdown("---")
    
    # 6. Buttons
    st.markdown("##### 🔗 주요 사이트 바로가기 (새창 열림)")
    el_c1, el_c2, el_c3, el_c4 = st.columns(4)
    with el_c1:
        st.markdown('<a href="https://rt.molit.go.kr/" target="_blank" class="ext-link" style="background:#1e3a5f;">🏛️ 국토부 실거래가</a>', unsafe_allow_html=True)
    with el_c2:
        st.markdown('<a href="https://land.naver.com/" target="_blank" class="ext-link" style="background:#03C75A;">🏠 네이버 부동산</a>', unsafe_allow_html=True)
    with el_c3:
        st.markdown('<a href="https://map.kakao.com/" target="_blank" class="ext-link" style="background:#FAE100; color:#333;">🗺️ 카카오맵</a>', unsafe_allow_html=True)
    with el_c4:
        st.markdown('<a href="https://www.reb.or.kr/" target="_blank" class="ext-link" style="background:#4f46e5;">📊 한국부동산원</a>', unsafe_allow_html=True)

    st.caption("※ 외부 사이트는 새 탭에서 열립니다.")


def render_listing():
    st.markdown("### ⭐ AI저평가추천매물")

    # helper for one item
    def property_card(title, price, desc, img_url, badge=None, key_suffix=None):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(img_url, use_column_width=True)
        with c2:
            if badge:
                st.markdown(f"<span style='background:#facc15; font-size:0.8em; padding:2px 4px; border-radius:4px;'>{badge}</span>", unsafe_allow_html=True)
            st.markdown(f"#### {title}")
            st.markdown(f"### {price}")
            st.caption(desc)
            _key = key_suffix if key_suffix else f"{title}_{random.randint(1,99999)}"
            if st.button("AI 리포트 보기", key=f"btn_{_key}"):
                st.info("AI 분석 리포트가 생성되었습니다. (데모)")
        st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # 【상단 고정】 AI 저평가 매물 (국토부 실거래가 대비 약 8% 전후 저평가)
    # ══════════════════════════════════════════════════════════════
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
                border-radius: 16px; padding: 20px 24px; margin-bottom: 20px;
                border-left: 5px solid #facc15; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
            <span style="font-size:2rem;">🤖</span>
            <div>
                <div style="font-size:1.3rem; font-weight:900; color:#facc15;">AI 저평가 추천매물</div>
                <div style="font-size:0.85rem; color:#93c5fd; margin-top:2px;">
                    국토부 실거래가 API 기반 · <b style="color:#fbbf24;">시세 대비 약 8% 전후 저평가</b> 매물만 선별
                </div>
            </div>
        </div>
        <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:10px;">
            <span style="background:#1e40af33; color:#93c5fd; border:1px solid #3b82f6;
                         border-radius:20px; padding:3px 12px; font-size:0.78rem; font-weight:700;">🏛️ 국토부 실거래가 연동</span>
            <span style="background:#14532d33; color:#86efac; border:1px solid #22c55e;
                         border-radius:20px; padding:3px 12px; font-size:0.78rem; font-weight:700;">✅ AI 검증 완료</span>
            <span style="background:#7f1d1d33; color:#fca5a5; border:1px solid #ef4444;
                         border-radius:20px; padding:3px 12px; font-size:0.78rem; font-weight:700;">🚨 매물 수 한정</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 매매 저평가 매물 (2개)
    st.markdown("""
    <div style="background:#162032; border-radius:12px; padding:14px 18px; margin-bottom:14px;
                border-left:4px solid #f59e0b;">
        <span style="font-size:1.05rem; font-weight:900; color:#fcd34d;">🏠 매매 저평가 매물</span>
        <span style="margin-left:10px; font-size:0.8rem; color:#94a3b8;">
            국토부 실거래가 대비 <b style="color:#f87171;">-7~9% 저평가</b> 확인 매물
        </span>
    </div>
    """, unsafe_allow_html=True)

    ai_col1, ai_col2 = st.columns(2)
    with ai_col1:
        st.markdown("""
        <div style="background:#0f172a; border:2px solid #f59e0b; border-radius:14px; padding:18px; position:relative; margin-bottom:4px;">
            <div style="position:absolute; top:-12px; left:16px; background:#f59e0b; color:#1e293b;
                        font-weight:900; font-size:0.78rem; padding:2px 12px; border-radius:20px;">🤖 AI 저평가 -8.2%</div>
            <div style="display:flex; gap:10px; align-items:flex-start; margin-top:6px;">
                <div style="font-size:2rem;">🏢</div>
                <div>
                    <div style="font-size:0.95rem; font-weight:800; color:#f8fafc;">래미안대치팰리스 34평 남향</div>
                    <div style="font-size:1.4rem; font-weight:900; color:#fcd34d; margin:4px 0;">40.5억</div>
                    <div style="font-size:0.78rem; color:#94a3b8;">국토부 실거래 기준가: 44.1억</div>
                    <div style="font-size:0.78rem; color:#f87171; font-weight:700; margin-top:2px;">▼ 3.6억 저평가 (8.2%↓)</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:6px;">34평 · 중층 · 남향 · 대치초 배정권</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 AI 저평가 리포트 보기", key="ai_under_sale_1", use_container_width=True, type="primary"):
            st.info("래미안대치팰리스 34평 저평가 분석 리포트가 생성되었습니다. (데모)")

    with ai_col2:
        st.markdown("""
        <div style="background:#0f172a; border:2px solid #f59e0b; border-radius:14px; padding:18px; position:relative; margin-bottom:4px;">
            <div style="position:absolute; top:-12px; left:16px; background:#f59e0b; color:#1e293b;
                        font-weight:900; font-size:0.78rem; padding:2px 12px; border-radius:20px;">🤖 AI 저평가 -7.5%</div>
            <div style="display:flex; gap:10px; align-items:flex-start; margin-top:6px;">
                <div style="font-size:2rem;">🏙️</div>
                <div>
                    <div style="font-size:0.95rem; font-weight:800; color:#f8fafc;">시그니엘 레지던스 88평 매매</div>
                    <div style="font-size:1.4rem; font-weight:900; color:#fcd34d; margin:4px 0;">63.8억</div>
                    <div style="font-size:0.78rem; color:#94a3b8;">국토부 실거래 기준가: 69억</div>
                    <div style="font-size:0.78rem; color:#f87171; font-weight:700; margin-top:2px;">▼ 5.2억 저평가 (7.5%↓)</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:6px;">88평 · 고층 · 한강뷰 · 풀옵션 급매</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 AI 저평가 리포트 보기", key="ai_under_sale_2", use_container_width=True, type="primary"):
            st.info("시그니엘 레지던스 88평 저평가 분석 리포트가 생성되었습니다. (데모)")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── 임대차/렌트 저평가 매물 (2개)
    st.markdown("""
    <div style="background:#162032; border-radius:12px; padding:14px 18px; margin-bottom:14px;
                border-left:4px solid #22d3ee;">
        <span style="font-size:1.05rem; font-weight:900; color:#67e8f9;">🔑 임대차·렌트 저평가 매물</span>
        <span style="margin-left:10px; font-size:0.8rem; color:#94a3b8;">
            시세 대비 <b style="color:#34d399;">-7~9% 저렴한</b> 전세·월세 확인 매물
        </span>
    </div>
    """, unsafe_allow_html=True)

    rent_col1, rent_col2 = st.columns(2)
    with rent_col1:
        st.markdown("""
        <div style="background:#0f172a; border:2px solid #22d3ee; border-radius:14px; padding:18px; position:relative; margin-bottom:4px;">
            <div style="position:absolute; top:-12px; left:16px; background:#22d3ee; color:#0f172a;
                        font-weight:900; font-size:0.78rem; padding:2px 12px; border-radius:20px;">🤖 전세 저평가 -8.8%</div>
            <div style="display:flex; gap:10px; align-items:flex-start; margin-top:6px;">
                <div style="font-size:2rem;">🔑</div>
                <div>
                    <div style="font-size:0.95rem; font-weight:800; color:#f8fafc;">대치SK뷰 33평 전세</div>
                    <div style="font-size:1.4rem; font-weight:900; color:#67e8f9; margin:4px 0;">14.5억</div>
                    <div style="font-size:0.78rem; color:#94a3b8;">국토부 실거래 기준 전세가: 15.9억</div>
                    <div style="font-size:0.78rem; color:#34d399; font-weight:700; margin-top:2px;">▼ 1.4억 저렴 (8.8%↓)</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:6px;">33평 · 중층 · 동향 · 대치역 도보 5분</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 AI 저평가 리포트 보기", key="ai_under_rent_1", use_container_width=True):
            st.info("대치SK뷰 33평 전세 저평가 분석 리포트가 생성되었습니다. (데모)")

    with rent_col2:
        st.markdown("""
        <div style="background:#0f172a; border:2px solid #22d3ee; border-radius:14px; padding:18px; position:relative; margin-bottom:4px;">
            <div style="position:absolute; top:-12px; left:16px; background:#22d3ee; color:#0f172a;
                        font-weight:900; font-size:0.78rem; padding:2px 12px; border-radius:20px;">🤖 월세 저평가 -7.9%</div>
            <div style="display:flex; gap:10px; align-items:flex-start; margin-top:6px;">
                <div style="font-size:2rem;">🏘️</div>
                <div>
                    <div style="font-size:0.95rem; font-weight:800; color:#f8fafc;">은마아파트 31평 월세</div>
                    <div style="font-size:1.4rem; font-weight:900; color:#67e8f9; margin:4px 0;">5천/185만</div>
                    <div style="font-size:0.78rem; color:#94a3b8;">국토부 실거래 기준 월세: 5천/201만</div>
                    <div style="font-size:0.78rem; color:#34d399; font-weight:700; margin-top:2px;">▼ 월 16만원 저렴 (7.9%↓)</div>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:6px;">31평 · 중층 · 남향 · 재건축 호재</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 AI 저평가 리포트 보기", key="ai_under_rent_2", use_container_width=True):
            st.info("은마아파트 31평 월세 저평가 분석 리포트가 생성되었습니다. (데모)")

    # 구분선 + 스크롤 안내
    st.markdown("""
    <div style="text-align:center; padding:18px 0; margin:10px 0;">
        <div style="display:inline-flex; align-items:center; gap:10px; background:#1e293b;
                    border-radius:30px; padding:8px 24px; border:1px solid #334155;">
            <span style="font-size:1.2rem;">⬇️</span>
            <span style="color:#94a3b8; font-size:0.9rem; font-weight:700;">
                아래로 스크롤하여 단지별 전체 추천매물 보기 (6개 단지 × 3개 매물)
            </span>
        </div>
    </div>
    <hr style="border:none; border-top:2px dashed #334155; margin:10px 0 24px 0;">
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # 【하단 스크롤】 단지별 추천매물 (6개 단지 × 3개)
    # ══════════════════════════════════════════════════════════════
    st.markdown("#### 🏘️ 단지별 전체 추천매물 (부동산 등록 매물)")

    # 1. Signiel (Modified Name & Restored Prices)
    st.markdown('<div class="section-header">💎 시그니엘 레지던스 (롯데월드타워몰)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: property_card("시그니엘 89평 프리미엄 매물", "1억 / 1,700만", "89평 · 고층 · 남향 · 한강뷰 풀옵션", "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=400&q=80", "월세")
    with c2: property_card("시그니엘 88평 프리미엄 매물", "69억", "88평 · 고층 · 급매", "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=400&q=80")
    with c3: property_card("시그니엘 95평 월세", "3억 / 1,800만", "95평 · 중층 · 입주협의", "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=400&q=80")

    # 2. Raemian Daechi Palace (Restored Prices)
    st.markdown('<div class="section-header">🏫 래미안 대치팰리스 (대장주)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: property_card("대치팰리스 45평형 남향 고층", "55억", "45평형 · 고층 · 남향 · 대치중심", "https://images.unsplash.com/photo-1600596542815-e328701102b9?auto=format&fit=crop&w=400&q=80", "강력추천")
    with c2: property_card("대치팰리스 34평 고층뷰", "44억", "34평 · 고층 · 남향 · 한강조망", "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=400&q=80")
    with c3: property_card("대치팰리스 33평 실용형", "42억", "33평 · 저층 · 남향 · 초급매", "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=400&q=80")

    # 3. Daechi SK View (Restored Prices)
    st.markdown('<div class="section-header">🚆 대치 SK뷰 (초역세권)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: property_card("대치SK뷰 33평 급매", "38억", "33평 · 중층 · 남향 · 대치역 도보 5분", "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=400&q=80", "급매")
    with c2: property_card("대치SK뷰 26평형 인기타입", "10억 / 150만", "26평형 · 동남향 · 저층 · 방3화2", "https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=400&q=80", "월세")
    with c3: property_card("대치SK뷰 37평형 방4", "8억 / 530만", "37평형 · 저층 · 가성비", "https://images.unsplash.com/photo-1502005229766-5283522a6f1f?auto=format&fit=crop&w=400&q=80", "반전세")

    # 4. Daechi I-Park (NEW)
    st.markdown('<div class="section-header">🏘️ 대치 아이파크 (추가됨)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: property_card("대치아이파크 56평 펜트하우스", "59억", "56평 · 고층 · 남향 · 명문학군", "https://images.unsplash.com/photo-1512915922610-06c2b585408e?auto=format&fit=crop&w=400&q=80", "희소")
    with c2: property_card("대치아이파크 33평 인기형", "40억", "33평 · 고층 · 남향 · 조망 우수", "https://images.unsplash.com/photo-1560185127-6ed189bf02f4?auto=format&fit=crop&w=400&q=80")
    with c3: property_card("대치아이파크 32평 실속형", "38억", "32평 · 저층 · 남향 · 가성비", "https://images.unsplash.com/photo-1484154218962-a1c002085d2f?auto=format&fit=crop&w=400&q=80")

    # 5. Eunma Apartment (Restored Prices)
    st.markdown('<div class="section-header">📉 대치 은마아파트 (재건축)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: property_card("대치은마 31평 급매", "36.5억", "31평 · 중층 · 남향 · 대치동 중심", "https://images.unsplash.com/photo-1560185893-a55cbc8c57e8?auto=format&fit=crop&w=400&q=80", "투자추천")
    with c2: property_card("대치은마 31평 고층뷰", "38억", "31평 · 고층 · 남향 · 조망 우수", "https://images.unsplash.com/photo-1484154218962-a1c002085d2f?auto=format&fit=crop&w=400&q=80")
    with c3: property_card("대치은마 34평 넓은평형", "41억", "34평 · 남향 · 중층", "https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=400&q=80")

    # 6. Samhwan Art Nouveau 2
    st.markdown('<div class="section-header">🎓 삼환 아르누보 2 (오피스텔)</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: property_card("삼환아르누보 17평형 매매", "4.6억", "17평형 · 서향 · 고층", "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=400&q=80", "인기")
    with c2: property_card("삼환아르누보 17평형 복층", "1,000만 / 122만", "17평형 · 북동향 · 고층", "https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=400&q=80", "월세")
    with c3: property_card("삼환아르누보 18평형 복층", "2,000만 / 200만", "18평형 · 북동향 · 2룸 확장형", "https://images.unsplash.com/photo-1486304873000-235643847519?auto=format&fit=crop&w=400&q=80")


def render_matching_and_reservation():
    # 1. AI Chatbot Section (Revamped Dashboard Style)
    with st.expander("💬 AI 챗봇 상담 (열기/닫기)", expanded=True):
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3 style="color: #fccc15; margin:0;">☁️ AI Real Estate Assistant</h3>
            <span style="font-size: 0.8em; color: gray;">24시간 365일, 대치동 부동산/세금/법률 데이터를 실시간 분석하여 답변합니다.</span>
        </div>
        """, unsafe_allow_html=True)

        # FAQ Dashboard
        st.markdown("##### 💡 자주 묻는 질문 (Top 50+)")
        faq_tab1, faq_tab2, faq_tab3, faq_tab4 = st.tabs(["🔥 인기질문", "💰 매매/투자", "🏠 전세/월세", "⚖️ 세금/정책"])
        
        selected_question = None
        
        with faq_tab1:
            fq1, fq2 = st.columns(2)
            if fq1.button("📌 대치동 학군 배정 원칙이 어떻게 되나요?", use_container_width=True): selected_question = "대치동 학군 배정 원칙 알려줘"
            if fq2.button("📈 대치동 국평(34평) 최근 시세 추이는?", use_container_width=True): selected_question = "대치동 34평 시세 추이 보여줘"
            if fq1.button("🚨 급매물 알림을 가장 먼저 받으려면?", use_container_width=True): selected_question = "급매물 알림 신청 방법 알려줘"
            if fq2.button("🏗️ 은마아파트 재건축 현재 단계는?", use_container_width=True): selected_question = "은마아파트 재건축 진행 현황 알려줘"
            
        with faq_tab2:
            fq1, fq2 = st.columns(2)
            if fq1.button("토지거래허가구역 실거주 요건은?", use_container_width=True): selected_question = "토지거래허가구역 요건 설명해줘"
            if fq2.button("갭투자 가능한 단지가 있나요?", use_container_width=True): selected_question = "대치동 갭투자 매물 추천해줘"

        with faq_tab3:
            fq1, fq2 = st.columns(2)
            if fq1.button("전세자금대출 최대 한도는?", use_container_width=True): selected_question = "전세자금대출 한도 알려줘"
            if fq2.button("전세 만기 시 보증금 반환 절차", use_container_width=True): selected_question = "전세 보증금 반환 내용 설명해줘"

        with faq_tab4:
            fq1, fq2 = st.columns(2)
            if fq1.button("1가구 2주택 양도세 비과세 요건", use_container_width=True): selected_question = "양도세 비과세 요건 알려줘"
            if fq2.button("취득세 중과 배제 기준", use_container_width=True): selected_question = "취득세 중과 기준 설명해줘"

        st.markdown("---")
        
        # Chat Interface
        msg_container = st.container(height=300)
        with msg_container:
            st.chat_message("assistant").write("안녕하세요! 롯데타워 AI 부동산 비서입니다. 궁금하신 점을 선택하거나 직접 물어보세요.")
            # Simple simulation of response to clicked button
            if selected_question:
                st.chat_message("user").write(selected_question)
                st.chat_message("assistant").write(f"네, **'{selected_question}'**에 대해 분석 중입니다...\n\n(AI가 관련 법규와 실거래 데이터를 조회하고 있습니다.)")

        prompt = st.chat_input("여기에 질문을 입력하세요...")
        if prompt:
            with msg_container:
                st.chat_message("user").write(prompt)
                st.chat_message("assistant").write("문의하신 내용을 확인했습니다. 상세 분석 리포트를 생성하고 있습니다.")

    st.markdown("---")
    
    # 2. Reservation Section (Styled Update)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #fccc15; margin-bottom: 5px;">🚀 롯데타워 AI 사전 매칭 센터</h2>
        <p style="color: #64748b; font-size: 0.9rem;">에어비앤비 방식의 스마트 예약 시스템으로 매칭 확률을 300% 높이세요.</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab_supply, tab_demand = st.tabs(["🏠 1. 공급자(임대/매도) 등록", "🔑 2. 수요자(임차/매수) 등록"])
    
    with tab_supply:
        st.info("### 🛡️ 내 집의 골든타임 예약 (공급)\nAI가 주변 실거래와 학원가 입지 데이터를 분석하여 가장 비싸게 거래될 시점에 마케팅을 시작합니다.")
        with st.form("form_supply"):
            c1, c2 = st.columns(2)
            with c1: st.selectbox("대상 단지", ["래미안대치팰리스", "시그니엘", "대치SK뷰", "은마아파트", "삼환아르누보2", "기타"])
            with c2: st.text_input("동/호수 (비공개 보안 유지)", placeholder="예: 101동 1502호")
            
            c3, c4 = st.columns(2)
            with c3: st.number_input("희망 가격 (억 단위)", min_value=0, value=30, step=1)
            with c4: st.date_input("매물 인도 가능일")

            st.markdown("#### 🎁 AI 공급자 패키지 (체크 시 자동 수행)")
            st.checkbox("🎥 나노 바나나 CEO AI 숏츠 제작 및 배포", value=True)
            st.checkbox("📊 주변 단지 대비 저평가 분석 리포트 생성", value=True)
            st.checkbox("👑 VIP 대기 수요자(4,200명) 우선 매칭 알림", value=True)

            st.markdown("---")
            if st.form_submit_button("🚀 AI 마케팅 및 매칭 예약 완료", use_container_width=True):
                st.success("✅ 등록 완료! 현재 대기 수요자 데이터와 대조한 결과입니다.")
                st.markdown("""
                <div style="background-color:#1e3a8a; padding:20px; border-radius:10px; text-align:center; color:white; border:1px solid #3b82f6;">
                    <div style="font-size:0.9em; opacity:0.8;">AI 기반 매칭 예상 점수</div>
                    <div style="font-size:2.5em; font-weight:bold; color:#facc15;">94 / 100</div>
                    <div style="font-size:0.8em; margin-top:10px;">
                    🚨 <b>코멘트:</b> 현재 대치동 학군지 인근 수요가 급증하고 있어,<br>
                    등록하신 가격대는 '1주일 내 계약' 확률이 매우 높습니다.<br>
                    <b>나노 바나나 CEO 숏츠 제작을 즉시 시작합니다!</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.caption("본 시스템은 Fast Campus MLOps 파이프라인(MLflow, Airflow)을 통해 실시간으로 데이터를 검증하고 있습니다.")
            
    with tab_demand:
        st.success("### 🎯 VIP 입주 희망 대기 (수요)\n비공개 급매물이나 퇴거 예정 매물을 일반 포털보다 48시간 먼저 선점하세요.")
        with st.form("form_demand"):
            st.multiselect("선호 단지 (복수 선택)", ["시그니엘", "래미안대치팰리스", "대치SK뷰", "대치아이파크", "은마아파트", "삼환아르누보2", "기타"])
            c1, c2 = st.columns(2)
            with c1: st.selectbox("희망 거래", ["매수 (사기)", "전세 찾기", "월세 찾기"])
            with c2: st.slider("예산 범위 (억)", 10, 100, (30, 50))
            st.text_input("연락처")
            st.checkbox("🔔 개인화 매칭 알림 수신 동의")
            st.form_submit_button("매칭 대기 등록하기", use_container_width=True)

def render_shorts_and_youlab():
    st.markdown("### 🎬 AI 숏츠 플레이어")
    st.video("https://www.w3schools.com/html/mov_bbb.mp4")
    
    st.markdown("---")
    
    # YOU-LAB Section
    st.markdown("""
    <div style="background-color: #7f1d1d; color: white; padding: 15px; border-radius: 5px; text-align: center; margin-bottom: 20px;">
        <h2 style="margin:0; color:white;">🔴 YOU-LAB: 초고속 숏츠 연구소</h2>
        <p style="margin:5px 0 0 0; font-size:0.8em; opacity:0.8;">Token Inference Server 가동 중 | GPU 가속 엔진 활성화</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        st.markdown("#### ⚙️ 촬영 및 인코딩 설정")
        with st.container(border=True):
            st.radio("시네마틱 스타일 선택", ["💥 마이클 베이 (폭발적/화려함)", "✨ 미니멀 (세련됨/깔끔함)", "🎵 트렌디 (힙합/빠른템포)"])
            st.slider("영상 길이 설정 (초)", 15, 60, 30)
            st.text_area("프롬프트 (장면 묘사)", "대치동 학원가 전경에서 래미안대치팰리스로 줌인, 웅장한 배경음악", height=100)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🎥 10mm 숏츠 제작 렌더링 시작", use_container_width=True, type="primary", key="btn_render_shorts"):
                st.toast("렌더링 서버에 작업을 요청했습니다!")
            
            st.markdown("""
            <div style="font-size:0.8em; color:gray; margin-top:10px;">
            1. 시나리오 생성 및 Python 코드 번역<br>
            2. 베가스(Vegas) 자동 편집 스크립트 실행<br>
            3. H.264 Server 사이드 렌더링 후 S3 업로드
            </div>
            """, unsafe_allow_html=True)

    with c2:
        st.markdown("#### 🖥️ 모니터링 데스크")
        with st.container(border=True):
            # Placeholder for monitoring screen
            st.markdown("""
            <div style="background-color:black; width:100%; height:300px; display:flex; align-items:center; justify-content:center; border-radius:5px; margin-bottom:10px;">
                <div style="text-align:center; color:gray;">
                    <span style="font-size:2em;">⚠️</span><br>
                    실시간 렌더링 미리보기 대기 중...<br>
                    (GPU: RTX 4090 - Idle)
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Terminal logs
            st.code("""
[SYSTEM] Token Inference Server Connected... OK
[INFO] Loaded Model: Lotte-RealEstate-v4.7
[GPU] CUDA Core Active: 0%
[QUEUE] Waiting for render job...
            """, language="bash")

def render_joint_matching():
    st.markdown("### 🤝 AI 부동산 공동중개 플랫폼")
    st.caption("강남구 등록된 1,500개 부동산과 실시간으로 매칭됩니다. (공동중개망 연동)")

    # 1. Register Requests (Send Management -> Find Client/Property)
    st.markdown("#### 📢 요청 등록 (고객 / 물건 찾기)")
    
    req_tab1, req_tab2 = st.tabs(["🙋‍♂️ 고객 찾아요 (매수/임차 의뢰)", "🏠 물건 찾아요 (전속 매물 공유)"])
    
    with req_tab1:
        st.info("💡 **'고객 찾아요'**는 내가 보유한 **매물**을 소화해줄 매수(임차) 손님을 찾는 기능입니다.")
        with st.form("find_client_form"):
            c1, c2, c3 = st.columns(3)
            with c1: st.selectbox("보유 매물", ["대치SK뷰 34평 전세", "은마 31평 매매", "직접입력"])
            with c2: st.number_input("거래 금액 (억)", value=15)
            with c3: st.text_input("특이사항", placeholder="입기협 전세자금대출 가능")
            
            if st.form_submit_button("🔔 전체 부동산에 '손님 찾기' 알림 발송", use_container_width=True):
                 st.toast("📢 강남구 1,500개 부동산에 알림이 발송되었습니다!")

    with req_tab2:
        st.info("💡 **'물건 찾아요'**는 내 **손님**에게 딱 맞는 공동 중개 매물을 찾는 기능입니다.")
        with st.form("find_property_form"):
            c1, c2, c3 = st.columns(3)
            with c1: st.text_input("찾는 물건", placeholder="래대팰 45평 판상형")
            with c2: st.number_input("손님 예산 (억)", value=45)
            with c3: st.text_input("손님 조건", placeholder="3개월 내 입주, 현금보유")
            
            if st.form_submit_button("🔔 전체 부동산에 '매물 요청' 알림 발송", use_container_width=True):
                 st.toast("📢 공동 중개망에 매물 요청이 등록되었습니다.")
    
    st.markdown("---")

    # 2. Matching Results (Receive Management -> AI Joint Matching)
    st.markdown("#### ⚡ AI 공동매칭 결과 (자동 챗봇 연결)")
    st.info("✅ **AI 매칭 성공!** 귀하의 요청과 딱 맞는 상대방 부동산이 발견되었습니다. 버튼을 누르면 **자동 채팅**이 연결됩니다.")

    # Mock Data
    data = {
        "시간": ["방금 전", "10분 전", "30분 전", "1시간 전", "어제"],
        "구분": ["🚨 매칭성공", "🚨 매칭성공", "수신", "수신", "발신"],
        "제목 (AI 요약)": [
            "래대팰 45평 판상형 매물 보유 (진공인)", 
            "SK뷰 34평 전세 손님 대기 (대박부동산)",
            "은마 31평 급매 찾으시는 분",
            "학원가 50평 임대 맞춤 가능",
            "대치아이파크 매수 손님 의뢰"
        ],
        "상대 부동산": ["진공인중개사", "대박부동산", "개포굿", "한티역공인", "전체발송"],
        "매칭률": ["99%", "97%", "85%", "82%", "-"],
        "상태": ["💬 채팅 연결 대기", "💬 채팅 연결 대기", "확인중", "확인중", "발송완료"]
    }
    df = pd.DataFrame(data)
    
    # Simulating a grid view
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("""
    <style>
    div[data-testid="stDataFrame"] {
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def render_admin_system():
    if "admin_unlocked" not in st.session_state:
        st.session_state["admin_unlocked"] = False

    st.markdown("### 🔒 관리자 보안 시스템")
    
    if not st.session_state["admin_unlocked"]:
        # 1. Security Check UI
        with st.container(border=True):
            st.markdown("##### 🔐 관리자 접속 권한 인증")
            password = st.text_input("관리자 비밀번호를 입력하세요", type="password", placeholder="비밀번호 입력")
            st.caption("ℹ️ 초기 비밀번호는 **1234** 입니다.")
            
            if st.button("🔓 관리자 권한 확인", use_container_width=True):
                if password == "1234":
                    st.session_state["admin_unlocked"] = True
                    st.toast("🟢 관리자 인증 성공!")
                    st.rerun()
                else:
                    st.error("⛔ 비밀번호가 일치하지 않습니다.")

            st.markdown("---")
            st.markdown("##### ❓ 비밀번호를 잊으셨나요?")
            if st.button("📲 핸드폰으로 비번 찾기", use_container_width=True):
                st.toast("📩 등록된 관리자 휴대폰(010-****-8285)으로 임시 비밀번호가 발송되었습니다.")
        return

    # If unlocked, show the dashboard
    if st.button("🔒 로그아웃 (시스템 잠금)", type="secondary"):
        st.session_state["admin_unlocked"] = False
        st.rerun()

    st.markdown("---")

    # 2. Admin Dashboard - Sales Pack Generator
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h3 style="color: #cbd5e1;">📑 부동산 AI 영업팩 생성기 (자동화)</h3>
        <p style="color: #64748b; font-size: 0.9rem;">버튼 하나로 블로그 / 카톡 / 상담 스크립트 / 영상 멘트를 한 번에 생성합니다.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("admin_sales_pack_form"):
        st.markdown("##### ⚡ 매물 기본 정보 입력 (자동 생성)")
        
        c1, c2, c3 = st.columns(3)
        with c1: st.text_input("매물 이름 (단지명)", "대치 SK VIEW")
        with c2: st.text_input("평형 / 타입", "34평 / A타입")
        with c3: st.selectbox("거래 유형", ["매매", "전세", "월세"])
        
        st.markdown("---")
        
        c4, c5, c6 = st.columns(3)
        with c4: st.text_input("학군 키워드", "대치초, 대청중 배정")
        with c5: st.text_input("교통 키워드", "대치역 초역세권, 3호선")
        with c6: st.text_input("입지 키워드", "대치동 학원가 도보 3분")
        
        st.markdown("---")
        
        # Full width red button
        submit = st.form_submit_button("🚀 영업 문구 및 자료 생성하기",type="primary", use_container_width=True)
        
        if submit:
            st.success("✅ AI 영업팩 생성이 완료되었습니다!")
            st.markdown("""
            <div style="background-color:#0f172a; padding:15px; border-radius:5px; border:1px solid #334155;">
                <h4 style="color:#38bdf8;">[블로그 제목]</h4>
                <p>대치동 학원가 바로 앞! SK VIEW 34평 귀한 전세, 놓치면 후회합니다.</p>
                <h4 style="color:#38bdf8; margin-top:15px;">[카톡 브리핑]</h4>
                <p>안녕하세요 대표님, 롯데AI부동산입니다.<br>
                대치초 배정 가능한 34평 로얄층 물건이 방금 접수되었습니다.<br>
                주말 내 계약 예상되오니 바로 연락 부탁드립니다.</p>
            </div>
            """, unsafe_allow_html=True)


def render_login_page():
    # ── 스크롤 플래그 처리 (하단 nav 버튼 클릭 후 이동)
    scroll_target = st.session_state.pop("scroll_to", None)
    if scroll_target:
        st.markdown(
            f'<script>setTimeout(function(){{var el=document.getElementById("{scroll_target}");if(el)el.scrollIntoView({{behavior:"smooth"}});}},300);</script>',
            unsafe_allow_html=True
        )

    # 최상단 앵커 (베이스캠프 헤더로 이동용)
    st.markdown('<div id="login-top"></div>', unsafe_allow_html=True)

    # Styled Header Section (Dark Blue)
    st.markdown("""
    <div style="background-color: #0f172a; color: white; padding: 30px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        <div style="display: flex; align-items: start; margin-bottom: 20px;">
            <div style="background-color: #fbbf24; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px; font-size: 30px; flex-shrink: 0; margin-top: 5px;">
                👨‍💼
            </div>
            <div>
                <h2 style="margin: 0 0 5px 0; font-size: 1.2rem; color: #f8fafc; line-height: 1.3;">롯데타워앤강남빌딩부동산중개주식회사</h2>
                <div style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 5px;">
                    등록번호: 11680-2023-00078 | 사업자: 461-86-02740
                </div>
                <div style="font-size: 1.1rem; color: #fbbf24; font-weight: bold; margin-bottom: 5px;">
                    대표: 공인중개사 이상수
                </div>
                <div style="color: #cbd5e1; font-size: 0.9rem;">
                    Tel: 02-578-8289 / 010-8985-8945
                </div>
            </div>
        </div>
        <h3 style="color: #fcd34d; margin-top: 10px; font-size: 1.3rem;">"대치1동은 자녀의 미래 베이스캠프입니다."</h3>
        <p style="color: #cbd5e1; line-height: 1.6; font-size: 0.95rem;">
            AI 저평가 분석과 예약 AI자동 매칭 시스템으로 숨겨진 부동산 가치를 발굴하고,<br>
            대한민국 최고의 교육 환경으로 가는 최적의 출발점을 찾아드립니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 3 Core Strategies Section — 았커 id 추가
    st.markdown('<div id="ai-strategy-section"></div>', unsafe_allow_html=True)
    st.markdown("#### 🔷 AI 부동산 핵심 3대 전략")
    
    st.markdown("""
    <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #3b82f6;">
        <h4 style="margin: 0 0 10px 0; color: #1e293b;">🎓 교육특구 1번지 분석</h4>
        <p style="margin: 0; color: #64748b; font-size: 0.9rem;">래대팰·SK뷰(대치초/단대부고) vs 아이파크(대도초/숙명여중고)<br>학군 정밀 분석 및 배정 원칙 데이터화</p>
    </div>
    
    <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #8b5cf6;">
        <h4 style="margin: 0 0 10px 0; color: #1e293b;">🧬 AI저평가 매물 매수·매도·임대차 예약 AI자동매칭</h4>
        <p style="margin: 0; color: #64748b; font-size: 0.9rem;">빅데이터로 저평가 매물을 발굴하고, 매수·매도·임대차 예약 고객에게 <b>1초 만에 AI자동 매칭</b>하여 거래 성사율 극대화</p>
    </div>

    <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; margin-bottom: 30px; border-left: 5px solid #ef4444;">
        <h4 style="margin: 0 0 10px 0; color: #1e293b;">📢 AI 자동 홍보 시스템</h4>
        <p style="margin: 0; color: #64748b; font-size: 0.9rem;">매물 접수 즉시 영업 문구 자동 생성 및 타겟 고객 발송</p>
    </div>
    """, unsafe_allow_html=True)

    # ── 앱 소개글 ──
    st.markdown("""
<div style="background:linear-gradient(135deg,#0f172a,#1e3a5f); color:white; border-radius:14px;
            padding:24px 22px; margin-bottom:20px;">
  <h4 style="color:#fcd34d; margin:0 0 14px 0; font-size:1.05rem;">
    🏠 부동산 저평가 매물 &amp; 사전예약 AI 자동매칭 플랫폼
  </h4>

  <div style="display:flex; gap:10px; margin-bottom:12px;">
    <div style="background:rgba(239,68,68,0.18); border-radius:10px; padding:14px 16px; flex:1;">
      <div style="font-size:0.78rem; color:#fca5a5; font-weight:700; margin-bottom:6px;">❓ 핵심 문제</div>
      <div style="font-size:0.82rem; color:#e2e8f0; line-height:1.6;">
        학군 이사 가족은 <b>10년간</b> 같은 지역에 머뭅니다.<br>
        원하는 시기·가격의 매물은 <b>구조적으로 희소</b>합니다.
      </div>
    </div>
    <div style="background:rgba(59,130,246,0.18); border-radius:10px; padding:14px 16px; flex:1;">
      <div style="font-size:0.78rem; color:#93c5fd; font-weight:700; margin-bottom:6px;">✅ 해결책</div>
      <div style="font-size:0.82rem; color:#e2e8f0; line-height:1.6;">
        AI가 저평가 매물을 <b>1초 분석</b>.<br>
        매도·임대인 ↔ 매수·임차인 이사 시기를 <b>사전 자동매칭</b>.
      </div>
    </div>
  </div>

  <div style="background:rgba(16,185,129,0.15); border-radius:10px; padding:12px 16px;">
    <div style="font-size:0.78rem; color:#6ee7b7; font-weight:700; margin-bottom:6px;">🎯 기대 효과</div>
    <div style="font-size:0.8rem; color:#e2e8f0; line-height:1.8;">
      👨‍👩‍👧 <b>소비자</b> — 입주·입학 시기 혼란 해소 &nbsp;|&nbsp;
      📊 <b>시장</b> — 수급 투명화, 가격 왜곡 감소 &nbsp;|&nbsp;
      🏙️ <b>사회</b> — 기존 주거지역 흐름 안정화
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Login Form

    with st.container(border=True):
        st.markdown("### 📱 핸드폰 인증 로그인")
        name = st.text_input("이름을 입력하세요", placeholder="예: 홍길동")
        phone = st.text_input("휴대폰 번호를 입력하세요 (- 없이 입력)", placeholder="01012345678")
        
        if st.button("인증번호 발송 및 로그인", use_container_width=True, type="primary"):
            if not name or len(name.strip()) < 2:
                st.error("이름을 입력해주세요. (2자 이상)")
            elif len(phone) < 10:
                st.error("올바른 휴대폰 번호를 입력해주세요.")
            else:
                st.session_state["logged_in"] = True
                st.session_state["user_name"] = name.strip()
                st.toast(f"✅ {name.strip()}님, 인증되었습니다! 환영합니다.")
                st.rerun()

    st.markdown("---")
    
    # Kakao Share Preview — 앵커 id 삽입 (공유하기 버튼 이동 대상)
    st.markdown('<div id="kakao-share-section"></div>', unsafe_allow_html=True)
    st.markdown("### 🟡 카카오톡으로 AI 전략 공유하기")
    
    # Layout for the 'Mock' Kakao Card
    APP_URL = "https://lotte-ai-app.streamlit.app/"
    with st.container(border=True):
        c_l, c_r = st.columns([1, 2])
        with c_l:
            st.markdown(f"""
            <a href="{APP_URL}" target="_blank">
                <img src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=300&q=80" style="border-radius: 10px; width: 100%; height: 100px; object-fit: cover;" title="클릭하여 앱으로 이동">
            </a>
            """, unsafe_allow_html=True)
        with c_r:
            st.markdown(f"[**[공인중개사 이상수] 대치1동 베이스캠프**]({APP_URL})")
            st.caption("""
            1. 🎓 교육특구 1번지 학군 분석
            2. 🧬 AI 저평가 매물 1초 매칭
            3. 📢 자동화 마케팅 시스템
            """)
        
        if st.button("카카오톡 링크 보내기 (데모)", use_container_width=True):
             st.toast("🚀 카카오톡 공유 창이 활성화되었습니다! (실제 동작을 위해선 도메인 등록이 필요합니다)")
             st.markdown(f"""
             <div style="padding:10px; background-color:#fef01b; color:#3c1e1e; border-radius:5px; text-align:center; margin-top:10px; font-weight:bold;">
                <a href="{APP_URL}" target="_blank" style="text-decoration:none; color:#3c1e1e;">앱으로 이동하기 👉 lotte-ai-app.streamlit.app</a>
             </div>
             """, unsafe_allow_html=True)

    # ── 핸드폰 번호로 앱 링크 전송 ──
    st.markdown("#### 📲 핸드폰 번호로 앱 링크 전송")
    with st.container(border=True):
        col_s, col_r2 = st.columns(2)
        with col_s:
            sender_phone = st.text_input(
                "📤 발신 번호 (내 번호)",
                placeholder="01012345678",
                key="sender_phone_input",
                help="링크를 보내는 사람의 핸드폰 번호 (- 없이 입력)"
            )
        with col_r2:
            receiver_phone = st.text_input(
                "📥 수신 번호 (받는 사람)",
                placeholder="01098765432",
                key="receiver_phone_input",
                help="링크를 받을 상대방 핸드폰 번호 (- 없이 입력)"
            )

        send_msg = st.text_area(
            "✉️ 전송 메시지",
            value=f"안녕하세요! 롯데타워&강남빌딩 부동산 이상수 대표입니다.\n대치1동 AI 부동산 정보 앱을 소개드립니다.\n👉 {APP_URL}",
            height=100,
            key="kakao_send_msg"
        )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📨 링크 문자 전송 (데모)", use_container_width=True, type="primary",
                         key="btn_send_sms"):
                if not sender_phone or len(sender_phone) < 10:
                    st.error("발신 번호를 올바르게 입력해주세요.")
                elif not receiver_phone or len(receiver_phone) < 10:
                    st.error("수신 번호를 올바르게 입력해주세요.")
                else:
                    st.success(f"✅ {receiver_phone} 번호로 앱 링크 전송 완료! (데모)")
                    st.info("💡 실제 문자 전송은 문자 API(알리고·Cool SMS 등) 연동 시 동작합니다.")
                    st.code(f"수신: {receiver_phone}\n발신: {sender_phone}\n내용: {send_msg}", language="text")

        with col_btn2:
            kakao_url = f"https://open.kakao.com/o/share?url={APP_URL}"
            st.markdown(
                f'<a href="{kakao_url}" target="_blank" style="display:block; text-align:center; '
                f'background:#fef01b; color:#3c1e1e; font-weight:bold; padding:10px; '
                f'border-radius:8px; text-decoration:none; border:1px solid #ddd;">💛 카카오톡으로 직접 공유</a>',
                unsafe_allow_html=True
            )
# --- Bottom Navigation Renderers ---

BOTTOM_NAV_CSS = """
<style>
.bottom-nav {
    position: fixed; bottom: 0px; left: 0px; width: 100%;
    background-color: white; border-top: 1px solid #eee;
    padding: 10px 20px; display: flex;
    justify-content: space-around; align-items: center;
    z-index: 9999; box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
}
.nav-btn {
    text-decoration: none; color: #333; font-weight: bold;
    font-size: 0.9rem; display: flex; flex-direction: column;
    align-items: center; padding: 5px;
}
.nav-btn:hover { color: #2563eb; background-color: #f8fafc; border-radius:8px; }
</style>
"""

@st.dialog("💼 롯데타워&강남빌딩 부동산 중개(주) 명함", width="large")
def show_business_card_dialog():
    """부동산 명함 팝업 (st.dialog)"""
    CARD_HTML = """
    <style>
    .biz-card {
        background: linear-gradient(135deg, #003087, #1565c0);
        border-radius: 14px; padding: 22px 24px;
        color: white; margin-bottom: 16px; position: relative;
    }
    .biz-card .logo-tag {
        font-size: 0.68rem; color: #90caf9; line-height: 1.6;
        margin-bottom: 6px;
    }
    .biz-card .company {
        font-size: 1.05rem; font-weight: 900; color: #ffd54f; margin-bottom: 2px;
    }
    .biz-card .sub { font-size: 0.78rem; color: #bbdefb; margin-bottom: 12px; }
    .biz-card .title-label { font-size: 0.82rem; color: #90caf9; }
    .biz-card .name { font-size: 1.5rem; font-weight: 900; letter-spacing: 4px; color: #fff; margin: 4px 0; }
    .biz-card .mobile { color: #ffd54f; font-size: 0.95rem; font-weight: bold; margin: 4px 0; }
    .biz-card .contact { color: #fff; font-size: 0.82rem; margin: 2px 0; }
    .biz-card .addr { color: #bbdefb; font-size: 0.75rem; margin-top: 4px; }
    .biz-card .desc-list {
        margin-top: 14px; padding-top: 12px;
        border-top: 1px solid #1976d2;
        font-size: 0.76rem; color: #bbdefb; line-height: 1.9;
    }
    </style>

    <!-- 이상수 대표 명함 -->
    <div class="biz-card">
      <div class="logo-tag">KNR 롯데월드타워 몰 시그니엘 레지던스 전문 | 학원가 한티 삼환·오피스텔 렌트</div>
      <div class="company">롯데타워 &amp; 강남빌딩 부동산 중개(주)</div>
      <div class="sub">LOTTE WORLD TOWER</div>
      <div class="title-label">대 표 / 공인중개사</div>
      <div class="name">이 상 수</div>
      <div class="mobile">Mobile : 010-8985-8945</div>
      <div class="contact">E-mail : 5788285@naver.com &nbsp;|&nbsp; tel : 578-8285</div>
      <div class="addr">서울시 강남구 도곡로 405, 5층 507호 [대치동, 삼환 아르누보2]</div>
      <div class="desc-list">
        ■ 랜드마크명품 주거 : 에테르노 청담 입주<br>
        ■ 주거 : 단대·숙명 인근아파트상담(래미안대치팰리스, SK뷰 외 다수)<br>
        ■ 입주 : 개포(THE HFIRSTIER IPARK)<br>
        ■ 투자 : 은마·미도·재건축 / 용산·한남 3구역 재개발<br>
        ■ 사업 : 상가·학원·건물·요양병원개설·토지
      </div>
    </div>

    <!-- 김은경 이사 명함 -->
    <div class="biz-card">
      <div class="logo-tag">KNR 롯데월드타워 몰 시그니엘 레지던스 전문 | 학원가 삼환 클레시아 랜드</div>
      <div class="company">롯데타워 &amp; 강남빌딩 부동산 중개(주)</div>
      <div class="sub">LOTTE WORLD TOWER</div>
      <div class="title-label">이 사</div>
      <div class="name">김 은 경</div>
      <div class="mobile">Mobile : 010-2482-2460</div>
      <div class="contact">E-mail : koung713@naver.com &nbsp;|&nbsp; tel : 578-8285</div>
      <div class="addr">서울시 강남구 도곡로 405, 5층 507호 [대치동, 삼환 아르누보2]</div>
      <div class="desc-list">
        ■ 랜드마크명품 주거 : 에테르노 청담 입주<br>
        ■ 주거 : 단대·숙명 인근아파트상담(래미안대치팰리스, SK뷰 외 다수)<br>
        ■ 입주 : 개포(THE HFIRSTIER IPARK)<br>
        ■ 투자 : 은마·미도·재건축 / 용산·한남 3구역 재개발<br>
        ■ 사업 : 상가·학원·건물·요양병원개설·토지
      </div>
    </div>

    <p style="text-align:center; color:#64748b; font-size:0.75rem; margin-top:8px;">
      📞 대표번호 02-578-8285 &nbsp;|&nbsp; 등록번호: 11680-2023-00078 &nbsp;|&nbsp; 사업자: 461-86-02740
    </p>
    """
    st.markdown(CARD_HTML, unsafe_allow_html=True)


def render_login_bottom_nav():
    """로그인 화면 전용 하단 Nav: 공유하기 | AI핵심3대전략 | 부동산명함보기(st.dialog 팝업)
    - position:fixed HTML 바 방식: 스크롤 시 항상 화면 하단에 고정
    - 코드 개선: data-key 직접 타겟팅 + off-screen 숨김으로 신뢰성 있는 클릭 보장
    """
    st.markdown("""
<style>
/* 본문 하단 여백 (fixed bar 뒤로 내용 안 가리게) */
.block-container { padding-bottom: 90px !important; }

/* 명함보기 숨김 Streamlit 버튼: 화면 차지 0, JS click()은 작동 */
div[data-key="btn_biz_card_login"] {
    visibility: hidden !important;
    height: 0px !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* 고정 HTML 버튼 바 */
#lotte-login-fixed-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 99999;
    background: #ffffff;
    border-top: 2px solid #e2e8f0;
    box-shadow: 0 -4px 16px rgba(0,0,0,0.10);
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 6px;
    padding: 8px 10px;
}
.llnb-btn {
    background: transparent;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    cursor: pointer;
    font-size: 0.80rem;
    font-weight: 800;
    padding: 7px 4px;
    text-align: center;
    line-height: 1.5;
    transition: background 0.15s, transform 0.1s;
    font-family: sans-serif;
}
.llnb-btn:hover  { background: #f1f5f9; transform: translateY(-1px); }
.llnb-btn:active { transform: translateY(0); }
.llnb-share    { color: #2563eb; }
.llnb-strategy { color: #7c3aed; }
.llnb-card     { color: #dc2626; }
</style>

<div id="lotte-login-fixed-bar">
  <!-- ① 공유하기: JS scrollIntoView 직접 -->
  <button class="llnb-btn llnb-share"
    onclick="(function(){
      var el=document.getElementById('kakao-share-section');
      if(el){el.scrollIntoView({behavior:'smooth',block:'start'});}
      else{window.scrollTo({top:document.body.scrollHeight,behavior:'smooth'});}
    })()">📤<br>공유하기</button>

  <!-- ② AI3대전략: JS scrollIntoView 직접 -->
  <button class="llnb-btn llnb-strategy"
    onclick="(function(){
      var el=document.getElementById('ai-strategy-section');
      if(el){el.scrollIntoView({behavior:'smooth',block:'start'});}
      else{window.scrollTo({top:0,behavior:'smooth'});}
    })()">🔷<br>AI핵심 3대전략</button>

  <!-- ③ 명함보기: data-key로 Streamlit 버튼 컨테이너 직접 타겟 후 내부 버튼 클릭 -->
  <button class="llnb-btn llnb-card"
    onclick="(function(){
      var c=document.querySelector('div[data-key="btn_biz_card_login"]');
      if(c){var b=c.querySelector('button');if(b){b.click();}}
    })()">💼<br>부동산명함보기</button>
</div>
""", unsafe_allow_html=True)

    # ── 명함보기 전용 숨겨진 Streamlit 버튼 (off-screen, data-key로 JS가 클릭 트리거) ──
    if st.button("💼\n부동산명함보기", use_container_width=True, key="btn_biz_card_login"):
        show_business_card_dialog()

def render_main_bottom_nav():
    """항상 화면 하단에 고정된 네비게이션 바
    - data-key 직접 타겟팅 + off-screen 숨김 방식으로 신뢰성 있는 클릭 보장
    """

    # ── 1. 고정 HTML 버튼 바 (position:fixed) + 숨김 Streamlit 버튼 스타일 ──
    st.markdown("""
<style>
/* 본문 하단 여백 */
.block-container { padding-bottom: 90px !important; }

/* Streamlit 버튼 숨김: 화면 차지 0, JS click()은 정상 작동 */
div[data-key="nav_main_matching"],
div[data-key="nav_main_shorts"],
div[data-key="nav_main_top"] {
    visibility: hidden !important;
    height: 0px !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* 고정 HTML 버튼 바 */
#lotte-fixed-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 99999;
    background: #ffffff;
    border-top: 2px solid #e2e8f0;
    box-shadow: 0 -4px 16px rgba(0,0,0,0.10);
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 6px;
    padding: 8px 10px;
}
.lnb-btn {
    background: transparent;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    cursor: pointer;
    font-size: 0.80rem;
    font-weight: 800;
    padding: 7px 4px;
    text-align: center;
    line-height: 1.5;
    transition: background 0.15s, transform 0.1s;
    font-family: sans-serif;
}
.lnb-btn:hover  { background: #f1f5f9; transform: translateY(-1px); }
.lnb-btn:active { transform: translateY(0); }
.lnb-matching { color: #2563eb; }
.lnb-shorts   { color: #7c3aed; }
.lnb-top      { color: #dc2626; }
</style>

<div id="lotte-fixed-bar">
  <!-- data-key 직접 타겟: Streamlit 버튼 컨테이너 안 버튼 클릭 (HTML 버튼과 100% 구분) -->
  <button class="lnb-btn lnb-matching"
    onclick="(function(){
      var c=document.querySelector('div[data-key=\"nav_main_matching\"]');
      if(c){var b=c.querySelector('button');if(b){b.click();}}
    })()">🤖<br>AI매칭사전예약가기</button>

  <button class="lnb-btn lnb-shorts"
    onclick="(function(){
      var c=document.querySelector('div[data-key=\"nav_main_shorts\"]');
      if(c){var b=c.querySelector('button');if(b){b.click();}}
    })()">🎦<br>AI숏츠 바로가기</button>

  <button class="lnb-btn lnb-top"
    onclick="(function(){
      var c=document.querySelector('div[data-key=\"nav_main_top\"]');
      if(c){var b=c.querySelector('button');if(b){b.click();}}
    })()">⬆️<br>AI저평가매물보기</button>
</div>
""", unsafe_allow_html=True)

    # ── 2. 실제 Streamlit 버튼: columns 미사용 (흡색박스 방지), 개별 렌더링으로 숨김 ──
    if st.button("🤖\nAI매칭사전예약가기", use_container_width=True, key="nav_main_matching"):
        st.session_state["nav_tab_idx"] = 2
        st.rerun()
    if st.button("🎬\nAI숏츠 바로가기", use_container_width=True, key="nav_main_shorts"):
        st.session_state["nav_tab_idx"] = 3
        st.rerun()
    if st.button("⬆️\nAI저평가매물보기", use_container_width=True, key="nav_main_top"):
        st.session_state["nav_tab_idx"] = 1
        st.rerun()

# --- Main ---
def main():
    # Sidebar: Share & Info
    st.sidebar.header("🔗 접속 주소 안내")
    st.sidebar.success("https://lotte-ai-estate.streamlit.app")
    st.sidebar.caption("👆 위 주소가 공식 앱 주소입니다. 복사해서 사용하세요!")
    
    with st.sidebar.expander("📤 앱 공유 및 카톡 바로가기", expanded=True):
        st.markdown("👇 **친구에게 공유할 링크**")
        st.code("https://lotte-ai-estate.streamlit.app", language="text")
        st.warning("⚠️ **주의**: 카카오톡 등 인앱 브라우저에서는 주소창이 숨겨질 수 있습니다. 이 주소를 확인하세요!")
        
        st.markdown("---")
        st.markdown("📱 **(개발용) 로컬 접속 시**")
        st.code("http://localhost:8502", language="text")

    # Session State Initialization
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    
    if not st.session_state["logged_in"]:
        render_login_page()
        render_login_bottom_nav()
        return

    # Define Tabs and Functions
    tab_config = [
        ("🏠 대치1동 특성 (초중고)", render_home),           # idx 0
        ("⭐ AI저평가추천매물", render_listing),              # idx 1
        ("🤖 AI매칭/사전등록(예약)매칭", render_matching_and_reservation),  # idx 2
        ("🎬 AI 숏츠 / YOU-LAB", render_shorts_and_youlab),      # idx 3
        ("🤝 AI공동매물매칭", render_joint_matching),           # idx 4
        ("🔒 시스템/영업팩생성", render_admin_system)             # idx 5
    ]

    # ── 직접 탭 인덱스 설정 (버튼 클릭 시 nav_tab_idx 사용)
    target_idx = st.session_state.pop("nav_tab_idx", None)
    if target_idx is not None:
        idx = int(target_idx)
        if 0 < idx < len(tab_config):
            item = tab_config.pop(idx)
            tab_config.insert(0, item)

    # ── 탁임 누늘스 호환: 문자열매칭이 스트링으로 온 경우 인덱스 전환
    legacy_target = st.session_state.pop("manual_nav_target", None)
    if legacy_target and target_idx is None:
        mapping = {
            "AI저평가추천매물": 1,
            "AI매칭": 2,
            "AI매칭/사전등록": 2,
            "AI 숏츠": 3,
            "대치1동": 0,
        }
        for key, val in mapping.items():
            if key in legacy_target:
                if val > 0:
                    item = tab_config.pop(val)
                    tab_config.insert(0, item)
                break

    # Render Tabs
    tabs = st.tabs([t[0] for t in tab_config])
    
    for i, tab in enumerate(tabs):
        with tab:
            tab_config[i][1]()

    render_main_bottom_nav()

if __name__ == "__main__":
    main()
