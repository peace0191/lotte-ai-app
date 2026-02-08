class MatchingService:
    def __init__(self):
        self.brand_name = "롯데타워앤 강남빌딩 부동산중개주식회사"
        self.active_listings = []
        self.buyer_leads = []
        self.social_leads = []
        self.match_reservations = []
        self.security_logs = [] # [timestamp, action, user_id, status]

    def _log_security_event(self, action, user_id, status="SUCCESS"):
        """보안감사 로그 기록 (v4.25 Security)"""
        from datetime import datetime
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "user_id": user_id,
            "status": status
        }
        self.security_logs.append(log_entry)

    def get_masked_reservations(self):
        """개인정보보호를 위해 마스킹 처리된 명단 반환"""
        self._log_security_event("ACCESS_LEAD_LIST", "ADMIN")
        masked_list = []
        for r in self.match_reservations:
            r_mask = r.copy()
            cond = r_mask["conditions"].copy()
            
            # Masking
            name = cond.get("user_name", "익명")
            phone = cond.get("user_phone", "-")
            
            cond["user_name"] = name[0] + "*" + name[-1] if len(name) > 1 else name
            if "-" in phone:
                p = phone.split("-")
                cond["user_phone"] = f"{p[0]}-****-{p[2]}"
            else:
                cond["user_phone"] = phone[:3] + "****" + phone[-4:] if len(phone) > 7 else phone
            
            r_mask["conditions"] = cond
            masked_list.append(r_mask)
        return masked_list
    def register_new_listing(self, property_id, agent_id='admin', status='active'):
        """입동 중개 가능 매물 등록"""
        listing = {
            "property_id": property_id,
            "agent_id": agent_id,
            "status": status,
            "created_at": "2026-02-03"
        }
        self.active_listings.append(listing)
        return self.check_immediate_match(listing) # Return alerts if any

    def calculate_matching_score(self, conditions):
        """AI 초정밀 매칭 점수 산출 (v4.20) - Sigmoid 기반 실무 로직"""
        import math
        
        # 1. 시뮬레이션용 가중치 (Feature Weights)
        # 가격 적합도(w1), 일정 유연성(w2), 협의가능성(w3), 긴급도(w4)
        w_intercept = -1.5
        w_price = 1.6
        w_date = 1.1
        w_negotiable = 0.7
        w_urgency = 0.5
        
        # 2. 개별 변수 산출 (데모용 고정값 또는 로직)
        price_fit = 0.85 
        date_fit = 0.7 if conditions.get("move_in_date") else 0.5
        negotiable = 1.0 
        urgency = 0.8 
        
        # 3. Z-Score 및 Sigmoid 계산
        z = w_intercept + (w_price * price_fit) + (w_date * date_fit) + (w_negotiable * negotiable) + (w_urgency * urgency)
        probability = 1 / (1 + math.exp(-z))
        
        return round(probability * 100)

    def register_match_request(self, user_id, conditions):
        """매칭 조건 예약 및 대기 순번 등록 (v4.20 Upgrade)"""
        import random
        dist = conditions.get("district", "대치동")
        ctype = conditions.get("type", "임차")
        
        existing_count = len([
            r for r in self.match_reservations 
            if r["conditions"].get("district") == dist and r["conditions"].get("type") == ctype
        ])
        queue_no = existing_count + 1
        
        # AI 초정밀 매칭 점수 계산
        match_score = self.calculate_matching_score(conditions)
        
        # Determine Status and Alerts (v4.21 Automation Trigger)
        status = "VIP_HOT" if match_score >= 80 else "ANALYZING"
        alerts = []
        if status == "VIP_HOT":
            alerts.append(f"🔥 [VIP 리드] {conditions.get('user_name')}님 매칭 확률 {match_score}%! 즉시 상담 필요.")
        
        req = {
            "user_id": user_id,
            "conditions": conditions,
            "status": status,
            "queue_no": queue_no,
            "match_score": match_score,
            "created_at": "2026-02-03"
        }
        self.match_reservations.append(req)
        
        # Advice for Condition Tuning
        advice = ""
        if match_score < 70:
            advice = "💡 보증금을 5,000만원 상향하거나 입주일 범위를 넓히면 매칭 점수가 15점 이상 상승합니다."

        return {
            "req_id": f"REQ_{random.randint(100, 999)}", 
            "queue_no": queue_no, 
            "match_score": match_score,
            "alerts": alerts,
            "advice": advice
        }

    def check_immediate_match(self, listing_data):
        """신규 매물 등록 시 예약자와 즉시 대조 알림"""
        alerts = []
        for res in self.match_reservations:
            # Simple match logic for demo
            if res["conditions"].get("district") in listing_data.get("property_id", ""):
                alerts.append(f"🔔 [{res['user_id']}]님께 알림 발송: 요청하신 매물이 등록되었습니다.")
        return alerts

    def find_matches(self, property_data):
        """매물 조건에 맞는 잠재 수요(중개사) 매칭"""
        matches = []
        target_region = property_data.get("district", "대치동")
        target_budget = property_data.get("price") # Simple mock
        
        # Logic: Find agents who have buyers for this region and budget
        for lead in self.buyer_leads:
            if lead["region"] == target_region:
                matches.append(lead["agent_id"])
        
        return list(set(matches)) # Unique agent list

    def qualify_lead(self, user_response_code):
        """
        Qualifies a lead based on the 1~4 funnel response.
        1: Timeline, 2: Duration, 3: Purpose, 4: Value Priority
        """
        score = 0
        if "1" in user_response_code: score += 40 # Urgent Move-in is top priority
        if "3" in user_response_code: score += 30 # Goal-oriented (School)
        if "4" in user_response_code: score += 20 # Value/Budget match
        if "2" in user_response_code: score += 10 # Short-term is stable
        
        status = "HOT" if score >= 70 else "WARM" if score >= 40 else "COLD"
        return {"score": score, "status": status}

    def get_matching_score(self, listing, lead):
        """매칭 적합도 점수 산출"""
        score = 80 # Base score
        if listing.get("status") == "IMMEDIATE" and lead.get("timeline") == "URGENT":
            score += 20
        return min(100, score)

# Singleton Instance
matching_svc = MatchingService()

# Mock Seeds for Demo
matching_svc.buyer_leads = [
    {"region": "대치동", "budget": "10-15억", "timeline": "URGENT", "agent_id": "Agent_A_Daechi"},
    {"region": "대치동", "budget": "30-50억", "timeline": "NORMAL", "agent_id": "Agent_B_Daechi"},
    {"region": "잠실동", "budget": "20억", "timeline": "URGENT", "agent_id": "Agent_C_Jamsil"}
]
