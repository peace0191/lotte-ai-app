# services/map_image.py
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def build_points_map_png(points, title="대치1동 학군/단지 지도", width=1200, height=700):
    """
    points: [{"name":..., "lat":..., "lon":..., "color":(R,G,B), "group":...}, ...]
    실제 타일 지도 스크린샷이 아니라,
    '좌표 기반 포인트 + 범례'가 있는 깔끔한 PNG를 만들어 PDF에 안정적으로 삽입합니다.
    """
    img = Image.new("RGB", (width, height), (28, 28, 35))
    draw = ImageDraw.Draw(img)

    # 폰트(윈도우: 맑은고딕 우선)
    font_path_candidates = [
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/gulim.ttc",
        "C:/Windows/Fonts/batang.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    ]
    font = None
    font_small = None
    
    for p in font_path_candidates:
        try:
            font = ImageFont.truetype(p, 24)
            font_small = ImageFont.truetype(p, 16)
            break
        except Exception:
            continue
            
    if font is None:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 타이틀
    draw.text((30, 22), title, font=font, fill=(240, 240, 240))

    # 좌표 범위
    lats = [p["lat"] for p in points if p.get("lat") is not None]
    lons = [p["lon"] for p in points if p.get("lon") is not None]
    
    if not lats or not lons:
        draw.text((30, 80), "표시할 좌표가 없습니다.", font=font_small, fill=(255, 120, 120))
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    # 패딩
    pad = 0.15
    lat_span = (max_lat - min_lat) or 0.001
    lon_span = (max_lon - min_lon) or 0.001
    min_lat -= lat_span * pad
    max_lat += lat_span * pad
    min_lon -= lon_span * pad
    max_lon += lon_span * pad

    # “지도 영역”
    left, top = 30, 80
    right, bottom = width - 300, height - 30
    
    # Background for map area
    draw.rounded_rectangle((left, top, right, bottom), radius=15, outline=(80, 80, 90), width=2, fill=(40, 40, 48))
    draw.text((left+20, top+15), "대치1동 학군 라인 (초→중→고)", font=font_small, fill=(180, 180, 190))

    def to_xy(lat, lon):
        # lat maps to y (inverted), lon maps to x
        # Normalized 0..1
        y_norm = (lat - min_lat) / (max_lat - min_lat)
        x_norm = (lon - min_lon) / (max_lon - min_lon)
        
        # Screen coords
        # x: left -> right
        # y: bottom -> top (lat increases upwards, screen y increases downwards)
        # So high lat = low y
        
        # Screen area width/height
        w_area = right - left
        h_area = bottom - top
        
        # Padding inside the box
        inner_pad = 40
        w_eff = w_area - 2*inner_pad
        h_eff = h_area - 2*inner_pad
        
        x = left + inner_pad + x_norm * w_eff
        y = bottom - inner_pad - y_norm * h_eff
        return x, y

    # --- Helper: Find Point ---
    def find_p(keyword):
        for p in points:
            if keyword in p.get("name", ""):
                return p
        return None

    # --- 1. Orange Line: 대치초 학군 (갈래길) ---
    daechi = find_p("대치초")
    raemian = find_p("래미안")
    skview = find_p("SK뷰")
    
    # 1-1. 대치초 -> 래미안
    if daechi and raemian:
        coords = [to_xy(daechi["lat"], daechi["lon"]), to_xy(raemian["lat"], raemian["lon"])]
        draw.line(coords, fill=(255, 140, 0), width=5)
        mx, my = (coords[0][0]+coords[1][0])/2, (coords[0][1]+coords[1][1])/2
        draw.text((mx, my), "▶", font=font_small, fill=(255, 165, 0), stroke_width=2, stroke_fill=(0,0,0))
        
    # 1-2. 대치초 -> SK뷰
    if daechi and skview:
        coords = [to_xy(daechi["lat"], daechi["lon"]), to_xy(skview["lat"], skview["lon"])]
        draw.line(coords, fill=(255, 140, 0), width=5)
        mx, my = (coords[0][0]+coords[1][0])/2, (coords[0][1]+coords[1][1])/2
        draw.text((mx, my), "▶", font=font_small, fill=(255, 165, 0), stroke_width=2, stroke_fill=(0,0,0))

    # --- 2. Pink Line: 단대부 -> 아이파크 -> 래미안 -> SK뷰 -> 삼환 ---
    p_names = ["단대부", "아이파크", "래미안", "SK뷰", "삼환"]
    p_points = [find_p(n) for n in p_names]
    
    if all(p_points):
        coords = [to_xy(p["lat"], p["lon"]) for p in p_points]
        
        # Draw Line (Hot Pink)
        draw.line(coords, fill=(255, 20, 147), width=5) 
        
        # Arrows
        for i in range(len(coords)-1):
            mx, my = (coords[i][0]+coords[i+1][0])/2, (coords[i][1]+coords[i+1][1])/2
            draw.text((mx, my), "▶", font=font_small, fill=(255, 105, 180), stroke_width=2, stroke_fill=(0,0,0))
            
    # --- 3. Blue Line: 대도초 -> 아이파크 ---
    daedo = find_p("대도초")
    ipark = find_p("아이파크")
    
    if daedo and ipark:
        coords = [to_xy(daedo["lat"], daedo["lon"]), to_xy(ipark["lat"], ipark["lon"])]
        
        # Draw Line (Dodger Blue)
        draw.line(coords, fill=(30, 144, 255), width=5)
        
        # Arrow (Midpoint)
        mx, my = (coords[0][0]+coords[1][0])/2, (coords[0][1]+coords[1][1])/2
        draw.text((mx, my), "▶", font=font_small, fill=(30, 144, 255), stroke_width=2, stroke_fill=(0,0,0))
        
    # --- 4. Pink Line 2: 대청중 -> 래미안, SK뷰 ---
    daecheong = find_p("대청중")
    raemian = find_p("래미안")
    skview = find_p("SK뷰")
    
    if daecheong:
        if raemian:
            c = [to_xy(daecheong["lat"], daecheong["lon"]), to_xy(raemian["lat"], raemian["lon"])]
            draw.line(c, fill=(255, 105, 180), width=5)
            mx, my = (c[0][0]+c[1][0])/2, (c[0][1]+c[1][1])/2
            draw.text((mx, my), "▶", font=font_small, fill=(255, 105, 180), stroke_width=2, stroke_fill=(0,0,0))
            
        if skview:
            c = [to_xy(daecheong["lat"], daecheong["lon"]), to_xy(skview["lat"], skview["lon"])]
            draw.line(c, fill=(255, 105, 180), width=5)
            mx, my = (c[0][0]+c[1][0])/2, (c[0][1]+c[1][1])/2
            draw.text((mx, my), "▶", font=font_small, fill=(255, 105, 180), stroke_width=2, stroke_fill=(0,0,0))

    # --- 5. Blue Line 2: 삼환 -> 대치아이파크 ---
    samhwan = find_p("삼환")
    ipark = find_p("아이파크")
    if samhwan and ipark:
        c = [to_xy(samhwan["lat"], samhwan["lon"]), to_xy(ipark["lat"], ipark["lon"])]
        draw.line(c, fill=(30, 144, 255), width=5)
        mx, my = (c[0][0]+c[1][0])/2, (c[0][1]+c[1][1])/2
        draw.text((mx, my), "▶", font=font_small, fill=(30, 144, 255), stroke_width=2, stroke_fill=(0,0,0))
    
    # --- 6. Blue Line 3: 삼환 -> 단대부중·고 ---
    dandae = find_p("단대부")
    
    if samhwan and dandae:
         c = [to_xy(samhwan["lat"], samhwan["lon"]), to_xy(dandae["lat"], dandae["lon"])]
         draw.line(c, fill=(30, 144, 255), width=5)
         mx, my = (c[0][0]+c[1][0])/2, (c[0][1]+c[1][1])/2
         draw.text((mx, my), "▶", font=font_small, fill=(30, 144, 255), stroke_width=2, stroke_fill=(0,0,0))

    # --- Draw Overcrowded Checks ---
    for p in points:
        if "과밀" in p.get("note", ""):
            cx, cy = to_xy(p["lat"], p["lon"])
            r_warn = 40 
            draw.ellipse((cx-r_warn, cy-r_warn, cx+r_warn, cy+r_warn), outline=(255, 50, 50), width=2)
            
    # --- Draw Points ---
    for p in points:
        x, y = to_xy(p["lat"], p["lon"])
        
        raw_color = p.get("color", (200, 200, 200))
        # Handle list vs tuple for PIL
        if isinstance(raw_color, list):
            c = tuple(raw_color)
        elif isinstance(raw_color, str):
             if raw_color == 'red': c = (255, 80, 80)
             else: c = (200, 200, 200)
        else:
            c = raw_color
            
        r = 8
        draw.ellipse((x-r, y-r, x+r, y+r), fill=c, outline=(255,255,255), width=2)
        
        # Label
        name = p.get("name", "")
        tx, ty = x + 12, y - 10
        draw.text((tx+1, ty+1), name, font=font_small, fill=(0,0,0))
        draw.text((tx, ty), name, font=font_small, fill=(240, 240, 240))

    # --- Legend ---
    lx = right + 20
    ly = top
    draw.text((lx, ly), "📌 범례", font=font, fill=(255, 255, 255))
    ly += 40
    
    # Legend Colors
    # Explicitly list categories to keep consistent order or use data
    # Let's derive from input points to match map
    legend_items = {}
    for p in points:
        cat = p.get("group") or p.get("category")
        col = p.get("color")
        if isinstance(col, list): col = tuple(col)
        if cat and col:
            legend_items[cat] = col
            
    for cat, col in legend_items.items():
        draw.rectangle((lx, ly, lx+20, ly+20), fill=col, outline=(200,200,200))
        draw.text((lx+30, ly), cat, font=font_small, fill=(220, 220, 220))
        ly += 35

    # Legend Lines
    draw.text((lx, ly+20), "── 대치초 학군", font=font_small, fill=(255, 140, 0))
    draw.text((lx, ly+50), "── 중학 배정 (대청/단대부)", font=font_small, fill=(255, 20, 147))
    draw.text((lx, ly+80), "── 대도/단대부 통학 (아이파크/삼환)", font=font_small, fill=(30, 144, 255))
    draw.text((lx, ly+110), "⭕ 과밀 학급", font=font_small, fill=(255, 50, 50))

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
