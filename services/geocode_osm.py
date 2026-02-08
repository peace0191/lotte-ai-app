# services/geocode_osm.py
from __future__ import annotations
import json
from pathlib import Path
import requests

CACHE_PATH = Path("outputs/geocode_cache.json")
CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

def _load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _save_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

def geocode(address: str) -> tuple[float, float] | None:
    """
    OpenStreetMap Nominatim 지오코딩 (무료).
    - 반드시 User-Agent 포함
    - 캐시 저장(다음 실행부터 빠름)
    """
    address = (address or "").strip()
    if not address:
        return None

    cache = _load_cache()
    if address in cache:
        lat, lon = cache[address]
        return float(lat), float(lon)

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    headers = {"User-Agent": "LotteTower-AI-DaechiMap/1.0 (contact: 02-578-8285)"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None

        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        cache[address] = [lat, lon]
        _save_cache(cache)
        return lat, lon
    except Exception:
        return None
