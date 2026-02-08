# services/region_compare.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

REGIONS = ["대치1동", "도곡동", "압구정동"]

# 기본 프로필(0~100): 데모/실무 모두 쓰기 쉬운 “설명 가능한” 기준값
REGION_BASE_PROFILE: Dict[str, Dict[str, float]] = {
    "대치1동": {"school": 98, "demand": 95, "defense": 93, "lease": 94, "brand": 85},
    "도곡동": {"school": 85, "demand": 80, "defense": 82, "lease": 78, "brand": 80},
    "압구정동": {"school": 75, "demand": 88, "defense": 90, "lease": 70, "brand": 98},
}

# 페르소나별 가중치(합 1.0)
WEIGHTS = {
    "학부모": {"school": 0.40, "demand": 0.20, "defense": 0.15, "lease": 0.15, "brand": 0.10},
    "투자자": {"school": 0.15, "demand": 0.20, "defense": 0.30, "lease": 0.15, "brand": 0.20},
    "임대인": {"school": 0.15, "demand": 0.25, "defense": 0.20, "lease": 0.30, "brand": 0.10},
}

def seasonal_factor(region: str) -> float:
    """
    학군 시즌 프리미엄(대치1동만)
    2~3월: +4, 12~1월: +2 (점수에 더해지는 형태; 0~100 스케일)
    """
    m = datetime.now().month
    if region == "대치1동":
        if m in (2, 3):
            return 4.0
        if m in (12, 1):
            return 2.0
    return 0.0

def grade_from(score: float) -> str:
    if score >= 95: return "SSS"
    if score >= 90: return "S"
    return "A"

def clamp(x: float, lo=0.0, hi=100.0) -> float:
    return max(lo, min(hi, x))

def apply_slider_tweaks(profile: Dict[str, float], tweaks: Dict[str, float]) -> Dict[str, float]:
    """
    tweaks는 -10~+10 정도 권장(슬라이더)
    """
    out = dict(profile)
    for k, delta in (tweaks or {}).items():
        if k in out:
            out[k] = clamp(out[k] + float(delta))
    return out

def score_region(region: str, persona: str, tweaks: Dict[str, float] | None = None) -> Dict[str, Any]:
    base = REGION_BASE_PROFILE[region]
    w = WEIGHTS.get(persona, WEIGHTS["학부모"])
    prof = apply_slider_tweaks(base, tweaks or {})
    # 시즌 프리미엄은 school/lease에만 살짝 반영(설명 쉬움)
    sf = seasonal_factor(region)
    prof2 = dict(prof)
    prof2["school"] = clamp(prof2["school"] + sf * 0.6)
    prof2["lease"] = clamp(prof2["lease"] + sf * 0.4)

    score = (
        prof2["school"] * w["school"] +
        prof2["demand"] * w["demand"] +
        prof2["defense"] * w["defense"] +
        prof2["lease"]  * w["lease"]  +
        prof2["brand"]  * w["brand"]
    )
    score = round(score, 1)
    return {
        "region": region,
        "persona": persona,
        "score": score,
        "grade": grade_from(score),
        "profile": prof2,
        "weights": w,
        "season_bonus": sf,
    }

def summary_comment(top: str, persona: str) -> str:
    if persona == "학부모":
        return f"AI 결론: **{top}**은(는) 학군·도보 통학·학원 인프라 기준에서 가장 효율적인 선택입니다."
    if persona == "투자자":
        return f"AI 결론: **{top}**은(는) 시세 방어·브랜드·하락장 탄력 기준에서 우위입니다."
    if persona == "임대인":
        return f"AI 결론: **{top}**은(는) 공실 위험이 낮고 임대 회전/안정성이 유리한 선택입니다."
    return f"AI 결론: **{top}** 우위"

def lease_recommendation(score: float) -> dict:
    """
    score(0~100)에 따른 전세/월세 추천 범위(데모용 가이드)
    - 반환값은 화면/제안서에 그대로 사용 가능하도록 텍스트로 구성
    """
    if score >= 95:
        return {
            "title": "전세 우선(안정형) / 월세는 '낮은 월세+높은 보증금' 권장",
            "jeonse": "전세: 상단가 협상(입학 시즌/학군 수요 반영), 2~4% 내 조정 여지",
            "wolse": "월세: 보증금 ↑ / 월세 ↓ 구조(월세 상단 억제) 추천",
            "note": "학군 수요가 강해 공실 리스크 낮음. 임대인은 '전세+빠른 계약'이 유리."
        }
    if score >= 90:
        return {
            "title": "전세/월세 균형(표준형) — 수요/회전 고려",
            "jeonse": "전세: 중단가 기준, 조건(이사일/수리)으로 3~5% 조정",
            "wolse": "월세: 보증금/월세 균형(시장 평균대) 추천",
            "note": "임대인은 계약 안정성/유지관리 조건을 특약으로 확보."
        }
    return {
        "title": "월세 탄력(수익형) — 보증금 낮추고 회전 전략",
        "jeonse": "전세: 하단가 접근(유입 촉진), 조건부(기간/원상복구) 제안",
        "wolse": "월세: 보증금 ↓ / 월세 ↑ 구조로 수익성 확보",
        "note": "수요가 상대적으로 약하면 '빠른 계약' 조건이 핵심."
    }
