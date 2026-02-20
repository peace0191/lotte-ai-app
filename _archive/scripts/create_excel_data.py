import json
import pandas as pd
from pathlib import Path

# Load existing JSON
BASE_DIR = Path(__file__).resolve().parent
json_path = BASE_DIR / "data" / "properties.json"
try:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print(f"Error reading JSON: {e}")
    data = {}

# Map old complex names to new requested section names
complex_map = {
    "시그니엘 레지던스": "롯데월드타워몰 시그니엘 레지던스",
    "대치SK뷰": "대치 SK뷰아파트",
    "대치팰리스": "래미안대치팰리스",
    "대치아이파크": "대치아이파크",
    "대치은마아파트": "대치은마아파트",
    "삼환아르누보2": "대치삼환아르누보2 오피스텔"
}

rows = []

# 1. Migrate existing data
for group_name, items in data.items():
    section_name = complex_map.get(group_name, group_name) # Default to existing if not mapped
    for item in items:
        # Extract area from spec if possible, or leave blank?
        # item['spec'] ex: "89평 · 1억 / 1,700만 · 프리미엄"
        # Let's try to extract area number
        area_py = ""
        if "평" in item.get("spec", ""):
            area_py = item["spec"].split("평")[0].strip()
        
        # Tags from features + badge
        tags = []
        if item.get("badge"): tags.append(item["badge"])
        if item.get("features"):
            # features is a string "A / B / C"
            feats = item["features"].split("/")
            tags.extend([f.strip() for f in feats])
        
        rows.append({
            "id": item.get("id"),
            "section": section_name,
            "title": item.get("name"),
            "price": item.get("price"),
            "area_py": area_py,
            "tags": ";".join(tags),
            "video_url": f"https://www.youtube.com/watch?v={item.get('youtube_id')}" if item.get("youtube_id") else "",
            "description": item.get("features", "")
        })

# 2. Add new 6 properties requested by user
new_items = [
    {
        "id": "3001",
        "section": "롯데월드타워몰 시그니엘 레지던스",
        "title": "롯데월드타워몰 시그니엘 레지던스 30평대 추천",
        "price": "59억",
        "area_py": "30",
        "tags": "학군;역세권;희소",
        "video_url": "",
        "description": "프리미엄 수요 높은 타입(조망/입지/희소성 중심)"
    },
    {
        "id": "3002",
        "section": "대치 SK뷰아파트",
        "title": "대치 SK뷰아파트 33평 추천",
        "price": "40억",
        "area_py": "33",
        "tags": "학군;실거주;메인",
        "video_url": "",
        "description": "문의 많은 대표 평형(학군/동선/실거주 만족도)"
    },
    {
        "id": "3003",
        "section": "래미안대치팰리스",
        "title": "래미안대치팰리스 32평 추천",
        "price": "38억",
        "area_py": "32",
        "tags": "학군;투자;프리미엄",
        "video_url": "",
        "description": "호가/수요 대비 경쟁력(브랜드+학군 프리미엄)"
    },
    {
        "id": "3004",
        "section": "대치아이파크",
        "title": "대치아이파크 40평대 추천",
        "price": "55억",
        "area_py": "40",
        "tags": "신축;브랜드;학군",
        "video_url": "",
        "description": "컨디션 우수/선호도 높음(대형 평형 수요)"
    },
    {
        "id": "3005",
        "section": "대치은마아파트",
        "title": "대치은마아파트 34평 추천",
        "price": "44억",
        "area_py": "34",
        "tags": "학군;실거주;역세권",
        "video_url": "",
        "description": "전환 수요 많은 타입(학군+생활 인프라)"
    },
    {
        "id": "3006",
        "section": "대치삼환아르누보2 오피스텔",
        "title": "대치삼환아르누보2 오피스텔 33평 추천",
        "price": "42억",
        "area_py": "33",
        "tags": "학군;희소;추천",
        "video_url": "",
        "description": "빠른 응대 권장(희소 타입/입지 강점)"
    }
]

rows.extend(new_items)

# Convert to DataFrame and save
df = pd.DataFrame(rows)
excel_path = BASE_DIR / "data" / "properties.xlsx"
df.to_excel(excel_path, index=False)
print(f"Created {excel_path} with {len(df)} rows.")
