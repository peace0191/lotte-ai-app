# services/daechi_map_deck.py
from __future__ import annotations
import pandas as pd
import pydeck as pdk

# 카테고리별 색상 (RGBA)
COLOR = {
    "초등": [255, 0, 0, 190],     # 🔴
    "중등": [0, 200, 0, 190],     # 🟢
    "고등": [0, 120, 255, 190],   # 🔵
    "단지": [255, 200, 0, 190],   # 🟡
    "부동산": [160, 80, 255, 190] # 🟣
}

def build_daechi_deck(poi: list[dict], *, zoom: int = 14):
    df = pd.DataFrame(poi)
    df["color"] = df["category"].map(lambda c: COLOR.get(c, [200, 200, 200, 180]))
    df["radius"] = df.apply(lambda r: 140 if r.get("is_overcrowded") else 95, axis=1)

    # 1) 메인 포인트 레이어 + tooltip
    layer_points = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[lon, lat]",
        get_radius="radius",
        get_fill_color="color",
        pickable=True,
        stroked=True,
        get_line_color=[255, 255, 255, 120],
        line_width_min_pixels=1,
    )

    # 2) 과밀 경고(⚠️) 텍스트 레이어
    overcrowded = df[df["is_overcrowded"] == True].copy()
    layer_warning = pdk.Layer(
        "TextLayer",
        data=overcrowded,
        get_position="[lon, lat]",
        get_text='"⚠️"',
        get_size=16,
        get_color=[255, 255, 255, 230],
        get_angle=0,
        get_text_anchor='"middle"',
        get_alignment_baseline='"center"',
        pickable=False,
    )

    # 지도 중심(첫 항목 기준, 없으면 대치역 근처)
    if len(df) > 0:
        center_lat = float(df["lat"].mean())
        center_lon = float(df["lon"].mean())
    else:
        center_lat, center_lon = 37.4935, 127.0575

    view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=zoom, pitch=0)

    tooltip = {
        "html": """
        <div style="font-size:13px; line-height:1.4;">
          <div style="font-weight:800;">{name}</div>
          <div>구분: <b>{category}</b></div>
          <div>{desc}</div>
          <div style="margin-top:6px;">
            {overcrowd}
          </div>
        </div>
        """,
        "style": {"backgroundColor": "rgba(0,0,0,0.85)", "color": "white"},
    }
    # tooltip 텍스트용 필드 추가
    df["overcrowd"] = df.apply(lambda r: "⚠️ 과밀학급 주의" if r.get("is_overcrowded") else "", axis=1)

    deck = pdk.Deck(
        layers=[layer_points, layer_warning],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style=None,  # 기본 스타일
    )
    return deck
