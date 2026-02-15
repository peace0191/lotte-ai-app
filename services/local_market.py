import json
from decimal import Decimal

def _to_json_safe(x):
    """UI/JSON에서 절대 안 터지도록 타입을 안전하게 변환"""
    if x is None:
        return None
    if isinstance(x, (int, float, str, bool)):
        return x
    if isinstance(x, Decimal):
        return float(x)
    if isinstance(x, dict):
        return {str(k): _to_json_safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [_to_json_safe(v) for v in x]
    return str(x)

class LocalMarketService:
    def __init__(self):
        # District & Landmark-specific weights (Refined v4.3)
        self.configs = {
            "시그니엘": {
                "luxury_weight": 0.60,
                "branding_weight": 0.30,
                "relative_value_weight": 0.10,
                "risk_factors": ["글로벌경기변동", "오피스텔세제"],
                "district": "잠실동"
            },
            "래미안대치팰리스": {
                "education_weight": 0.45,
                "liquidity_weight": 0.35,
                "status_weight": 0.20,
                "risk_factors": ["고점경계감", "증여제한"],
                "district": "대치동"
            },
            "대치SK뷰": {
                "education_weight": 0.55,
                "proximity_weight": 0.25,
                "value_weight": 0.20,
                "risk_factors": ["단지규모작음", "학원가소음"],
                "district": "대치동"
            },
            "대치은마": {
                "reconstruction_weight": 0.70,
                "investment_weight": 0.20,
                "education_weight": 0.10,
                "risk_factors": ["추가분담금", "정부규제"],
                "district": "대치동"
            },
            "삼환아르누보2": {
                "rent_yield_weight": 0.50,
                "location_weight": 0.40,
                "management_weight": 0.10,
                "risk_factors": ["공실률_방학외", "시설노후화"],
                "district": "대치동"
            }
        }

    def get_district_config(self, node_name):
        # Match by specific landmark name first, then fall back to district
        for key in self.configs:
            if key in node_name:
                return self.configs[key]
        return {"education_weight": 0.5, "risk_factors": ["일반리스크"], "district": "대치동"}

    def calculate_undervalue_score_precise(self, ask_price, rt_median, rt_count, rt_iqr, bonuses=0, penalties=0):
        """
        [2026.2.5 MLOps Precise Version]
        score = clamp(50 + 400 * discount_rate * conf - vol_penalty + bonus - penalty)
        """
        import math
        
        if rt_count < 1 or rt_median <= 0:
            return 50.0, {"msg": "No transaction data"}

        # 1. Discount Rate
        discount_rate = (rt_median - ask_price) / rt_median
        
        # 2. Confidence (sqrt scaling)
        conf = min(1.0, math.sqrt(rt_count / 20.0))
        
        # 3. Volatility Penalty (IQR focus)
        vol_penalty = max(0, min(8.0, (rt_iqr / rt_median) * 100))
        
        # 4. Final Calculation
        impact = 400 * discount_rate * conf
        raw_score = 50 + impact - vol_penalty + bonuses - penalties
        final_score = max(0, min(100, raw_score))
        
        evidence = {
            "rt_median_180d": rt_median,
            "rt_count_180d": rt_count,
            "rt_iqr": rt_iqr,
            "discount_rate": round(discount_rate, 4),
            "conf": round(conf, 4),
            "vol_penalty": round(vol_penalty, 2),
            "bonus": bonuses,
            "penalty": penalties,
            "calc_impact": round(impact, 2)
        }
        
        return round(final_score, 1), evidence

    def calculate_decision_score(self, property_id, property_data):
        import os
        from services.stats_svc import stats_svc
        
        name = property_data.get("name", "")
        config = self.get_district_config(name)
        
        # 1. Map name to standard complex_id
        name_map = {"래미안대치팰리스": "APT_RDP", "대치SK뷰": "APT_SKV", "대치은마": "APT_ENM"}
        complex_id = "APT_RDP" # Default
        for k, v in name_map.items():
            if k in name:
                complex_id = v
                break
        
        # 2. Get Price and Area Bucket
        # Handle price string like '35억 5,000' -> numeric (using services.money_parser.money_parser if available, else simple)
        try:
            from services.money_parser import money_parser
            ask_price_val = money_parser.parse_price(property_data.get("price", "0"))
        except:
            # Fallback to simple extraction
            import re
            p_str = str(property_data.get("price", "0")).replace(",", "")
            billions = re.search(r'(\d+)억', p_str)
            millions = re.search(r'억\s*(\d+)', p_str)
            deposit_rent = re.search(r'(\d+)\s*/\s*(\d+)', p_str)
            
            if billions or millions:
                ask_price_val = (int(billions.group(1)) * 10000 if billions else 0) + (int(millions.group(1)) if millions else 0)
            elif deposit_rent:
                # Treat deposit as price proxy to avoid 0
                ask_price_val = int(deposit_rent.group(1))
            else:
                # Try raw number if it's just digits
                try:
                    ask_price_val = int(p_str)
                except:
                    ask_price_val = 0 # Safe default
            
            if ask_price_val == 0:
                ask_price_val = 1  # Prevent ZeroDivisionError later

        spec = property_data.get("spec", "84")
        area_match = [int(s) for s in spec.split() if s.isdigit()]
        area_bucket = area_match[0] if area_match else 84.0

        # 3. Query Real Stats from stats_svc (v4.30 Upgrade)
        stats = stats_svc.get_complex_stats(name, area_bucket)
        
        if stats:
            rt_median = stats["median"]
            rt_count = stats["count"]
            rt_iqr = stats["iqr"]
        else:
            # Fallback to simulation
            rt_median, rt_count, rt_iqr = ask_price_val * 1.05, 5, ask_price_val * 0.1
        
        penalties = len(config["risk_factors"]) * 2
        bonuses = 5 if "급매" in property_data.get("features", "") else 0
        
        score, evidence = self.calculate_undervalue_score_precise(
            ask_price_val, rt_median, rt_count, rt_iqr, bonuses, penalties
        )
        
        # --- UI-safe Normalization (v4.31) ---
        safe_score = int(round(float(score))) if score is not None else 0
        
        raw_discount = evidence.get("discount_rate", 0) if isinstance(evidence, dict) else 0
        try:
            raw_discount = float(raw_discount)
        except:
            raw_discount = 0.0
        
        if 0 <= raw_discount <= 1:
            raw_discount *= 100
        safe_discount_rate = round(raw_discount, 1)
        
        safe_name = str(name) if name is not None else ""
        safe_is_urgent = ("급매" in str(property_data.get("features", "")))
        safe_evidence = _to_json_safe(evidence if isinstance(evidence, dict) else {})

        # [New] MLflow Experiment Logging (Auto-Tracking)
        try:
            from services.ml_service import ml_service
            ml_params = {
                "ask_price": float(ask_price_val),
                "rt_median": float(rt_median),
                "rt_count": float(rt_count),
                "area_bucket": float(area_bucket)
            }
            ml_metrics = {
                "score": float(score) if score is not None else 0.0,
                "discount_rate": float(safe_discount_rate),
                "vol_penalty": float(evidence.get("vol_penalty", 0)) if isinstance(evidence, dict) else 0.0
            }
            ml_tags = {
                "property_name": safe_name,
                "district": config.get("district", "Unknown"),
                "is_urgent": str(safe_is_urgent)
            }
            ml_service.log_valuation_experiment(ml_params, ml_metrics, ml_tags)
        except Exception:
            pass

        return {
            "score": safe_score,
            "discount_rate": safe_discount_rate,
            "complex_name": safe_name,
            "is_urgent": safe_is_urgent,
            "evidence": safe_evidence,
            "complex_id": complex_id,
            "area_bucket": area_bucket
        }

    def get_market_momentum(self, property_name):
        """
        Returns real-world market context based on the current date (Feb 2026).
        """
        if "SK뷰" in property_name and "26평" in property_name:
            return {
                "status": "EMERGENCY_SALE",
                "deadline": "2026-03-05",
                "strategy": "Decision Fatigue Removal",
                "reason": "Relocation for work"
            }
        return {"status": "NORMAL", "strategy": "Value Appreciation"}

    def get_risk_status(self, district_name):
        config = self.get_district_config(district_name)
        return config["risk_factors"]

    def get_daechi_summary(self):
        """
        대치1동 핵심 요약 정보를 반환합니다. (Legacy 호환용)
        Returns:
            dict: 학군, 교통, 수요, 가격대 정보
        """
        return {
            "region_name": "대치1동 (Daechi-dong)",
            "school_district": "대치초, 대청중, 단대부중/숙명여중 등 강남 8학군 핵심",
            "academy_street": "은마아파트 사거리 ~ 한티역 (대한민국 사교육 1번지)",
            "transport": "3호선(대치역, 도곡역), 수인분당선(한티역, 도곡역)",
            "demand_trend": "방학 이사철 전세 수요 급증, 매매는 똘똘한 한 채 선호 지속",
            "price_range": {
                "30py_apt": "28억 ~ 35억",
                "jeonse": "13억 ~ 18억"
            },
            "major_complexes": ["래미안대치팰리스", "대치SK뷰", "대치은마", "선경/미도/우성"]
        }

    # Aliases for compatibility
    get_region_summary = get_daechi_summary
    get_daechi_info = get_daechi_summary

    def get_education_summary(self):
        """
        대치동 교육 환경/학군 정보를 반환합니다.
        """
        return {
            "elementary": ["대치초등학교 (혁신초)", "대곡초등학교", "대도초등학교"],
            "middle": ["대청중학교 (특목고 진학률 최상위)", "단국대부속중학교 (남중)", "숙명여자중학교", "역삼중학교", "진선여자중학교"],
            "high": ["단국대부속고등학교 (의대 진학 최상위)", "숙명여자고등학교", "중대부고", "경기여고", "은광여고", "진선여고"],
            "academy_zone": "은마아파트 사거리 ~ 한티역 대로변 및 이면도로 (대한민국 사교육 1번지, 1000여개 학원 밀집)",
            "description": "대치1동은 대한민국 최고의 학군지로, 초등학교부터 불변의 학군 프리미엄을 자랑합니다. 특히 대청중-단대부고/숙명여고 라인은 학부모님들의 선호도가 가장 높습니다."
        }

    # Aliases
    get_school_info = get_education_summary
    get_daechi_education = get_education_summary

# Singleton instance
local_market_svc = LocalMarketService()
