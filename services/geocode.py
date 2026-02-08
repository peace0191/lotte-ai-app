# services/geocode.py
import json, os, time, re
import requests

CACHE_PATH = os.path.join("data", "geocode_cache.json")

def _load_cache():
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def _save_cache(cache: dict):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def geocode_nominatim(address: str):
    """
    무료 OSM Nominatim 사용 (키 불필요)
    - 캐시 우선 조회
    - Miss 시, 괄호(...) 제거 후 API 호출 (성공률 향상)
    """
    cache = _load_cache()
    
    # 1. Exact Match Check
    if address in cache:
        return cache[address]["lat"], cache[address]["lon"]

    # 2. API Call (Strip brackets for better hit rate)
    # e.g. "서울특별시 강남구 양재천로 363 (대치동 505)" -> "서울특별시 강남구 양재천로 363"
    clean_addr = re.sub(r'\([^)]*\)', '', address).strip()
    
    # If clean_addr is empty or too short, fallback to original
    query_addr = clean_addr if len(clean_addr) > 5 else address

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query_addr, "format": "json", "limit": 1}
    headers = {"User-Agent": "LotteTowerAI/1.0 (contact: 5788285@naver.com)"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        
        if not data:
            # Fallback: Try with original just in case
            if query_addr != address:
                 params["q"] = address
                 r = requests.get(url, params=params, headers=headers, timeout=10)
                 data = r.json()

        if not data:
            print(f"Geocode Failed (No Data): {address}")
            return None

        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        
        # Cache the ORIGINAL input address so next time it hits instantly
        cache[address] = {"lat": lat, "lon": lon, "ts": time.time()}
        _save_cache(cache)
        time.sleep(1.0)  # Nominatim 예의상 딜레이
        return lat, lon
    except Exception as e:
        print(f"Geocode Error: {e}")
        return None
