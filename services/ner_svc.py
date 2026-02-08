import re
from typing import Dict, List, Any
from services.money_parser import normalize_prices_from_text

# MVP 사전
DONG_LIST = ["대치동", "잠실동", "삼성동", "역삼동"]
COMPLEX_LIST = ["대치 SK뷰", "은마아파트", "대치아이파크", "대치팰리스"]
TYPE_LIST = ["아파트", "오피스텔", "빌딩", "상가", "레지던스"]
FEATURE_KEYS = ["학군", "역세권", "급매", "로얄층", "리모델링", "풀옵션", "한강뷰", "대단지"]
ORIENTATION = ["남향", "북향", "동향", "서향", "남동향", "남서향", "북동향", "북서향"]

class NERService:
    def __init__(self):
        self.labels = [
            "LOC_CITY", "LOC_DISTRICT", "LOC_DONG", "COMPLEX", "TYPE",
            "AREA_PYEONG", "AREA_SQM", "PRICE_SALE", "PRICE_RENT_JEONSE",
            "FLOOR", "ORIENTATION", "ROOMS", "BATHS", "TRANSIT", "SCHOOL",
            "FEATURE", "CONDITION", "MOVE_IN"
        ]

    def _find_first_match(self, words: List[str], text: str):
        for w in words:
            if w in text:
                return w
        return None

    def extract_entities(self, text: str) -> Dict[str, Any]:
        t = text.strip()

        loc_dong = self._find_first_match(DONG_LIST, t)
        complex_name = self._find_first_match(COMPLEX_LIST, t)
        prop_type = self._find_first_match(TYPE_LIST, t)
        orient = self._find_first_match(ORIENTATION, t)

        # 평형
        pyeong = None
        m = re.search(r"(\d+)\s*(평|평대)", t)
        if m:
            pyeong = int(m.group(1))

        # ㎡
        sqm = None
        m = re.search(r"(\d+)\s*(㎡|m2)", t, re.IGNORECASE)
        if m:
            sqm = int(m.group(1))

        # 방/화
        rooms = None
        m = re.search(r"(방|룸)\s*(\d+)|(\d+)\s*(방|룸)", t)
        if m:
            rooms = int(m.group(2) or m.group(3))

        baths = None
        m = re.search(r"(화|욕실)\s*(\d+)|(\d+)\s*(화|욕실)", t)
        if m:
            baths = int(m.group(2) or m.group(3))

        # 특징(키워드)
        feats = [k for k in FEATURE_KEYS if k in t]

        # 가격 정규화
        price_info = normalize_prices_from_text(t)

        return {
            "raw_text": t,
            "LOC_DONG": loc_dong,
            "COMPLEX": complex_name,
            "TYPE": prop_type,
            "AREA_PYEONG": pyeong,
            "AREA_SQM": sqm,
            "ROOMS": rooms,
            "BATHS": baths,
            "ORIENTATION": orient,
            "FEATURE": feats,
            **price_info,
        }

ner_svc = NERService()
