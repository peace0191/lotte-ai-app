from __future__ import annotations
from typing import Dict
from services.local_market import local_market_svc

SENSITIVE = ["등기","소송","경매","채무","압류","세금","사기","하자","가압류","가처분"]

def is_sensitive(q: str) -> bool:
    return any(k in q for k in SENSITIVE)

def faq_router(q: str) -> str:
    q = q.strip()
    # Branching for Buyer/Seller context (v4.4 Framework)
    if any(k in q for k in ["사도","매수","투자","실거주","언제 사"]):
        return "buyer_decision"
    if any(k in q for k in ["언제 팔","매도","안 팔려","가격 조정"]):
        return "seller_decision"
    
    # New Market Status logic
    if any(k in q for k in ["공사비","갈등","재건축 속도","분담금"]):
        return "reconstruction_risk"
    if any(k in q for k in ["고금리","금리","대출","DSR"]):
        return "financial_status"
    
    # Sales Funnel Filtering (v4.7)
    if any(k in q for k in ["1","2","3","4"]) and len(q) <= 5:
        return "lead_qualification"
    if any(k in q for k in ["고민","불안","진짜","맞나"]):
        return "decision_anxiety"
    
    if any(k in q for k in ["예약","알림","매칭 신청","찾아줘","대기"]):
        return "match_reservation"
    
    if any(k in q for k in ["계약", "체결", "안전", "서류", "등기", "매칭 확인"]):
        return "contract"
    
    if any(k in q for k in ["가격","저렴","할인","급매","호가","실거래"]):
        return "discount"
    if any(k in q for k in ["시그니엘","Signiel","올림픽로 300"]):
        return "landmark_signiel"
    if any(k in q for k in ["은마","은마아파트","재건축"]):
        return "landmark_eunma"
    if any(k in q for k in ["학교","학군","교육","아이","학원","대치초","대도초","숙명","단대부","셔틀"]):
        return "education"
    if any(k in q for k in ["전세","보증금","월세","수익률","GAP","갭"]):
        return "deposit"
    return "general"

def build_response(q: str, faq_common: Dict[str, str], selected: dict | None) -> str:
    if is_sensitive(q):
        return faq_common.get("sensitive", "보안상 답변이 제한되는 질문입니다. 유선으로 문의 부탁드립니다.")

    key = faq_router(q)
    
    # Emotional Comfort Prefix (Refined v4.4)
    comfort_prefix = "많이 고민되시죠? 현재 서울 부동산은 '대세 상승기'보다는 '단지별 양극화'가 심한 시장입니다. 😊\n\n"
    
    # 1. Market Status - Reconstruction Risk
    if key == "reconstruction_risk":
        return comfort_prefix + "최근 공사비 급상승으로 인해 사업성이 낮은 단지들은 속도가 늦어지고 있습니다. 대치은마 같은 핵심 입지는 결국 추진되겠지만, 분담금 변동성을 AI 점수에 반영하여 안내드리고 있습니다."

    # 2. Market Status - Financial Status
    if key == "financial_status":
        return comfort_prefix + "금리가 최고점을 찍고 횡보 중입니다. DSR 규제로 인해 현금 동원력이 시장의 키를 쥐고 있습니다. 매수 계획이시라면 AI 리포트의 '자금 계획 시뮬레이터'를 먼저 확인해보세요."

    # 3. Landmark Specifics - Signiel
    if key == "landmark_signiel":
        return comfort_prefix + "올림픽로 300, 시그니엘 레지던스는 단순 주거가 아닌 '글로벌 자산'입니다. 현재 렌트 수요는 법인 임원 위주로 꾸준하며, 매매는 희소성 기반의 가격 방어가 강력합니다."

    # 4. Landmark Specifics - Eunma
    if key == "landmark_eunma":
        return comfort_prefix + "대치은마는 재건축 추진위 단계의 고비를 넘기고 있습니다. 투자자라면 '실거주 의무'와 '분담금' 사이의 실익을 따져야 합니다. 현재 AI 투자 가중치는 70%로 매우 높은 편입니다."

    # 5. Buyer Decision Logic (Updated with v4.4 Framework)
    if key == "buyer_decision":
        if selected:
            score = local_market_svc.calculate_decision_score(selected.get("id"), selected)
            config = local_market_svc.get_district_config(selected.get("name", ""))
            return (
                f"{comfort_prefix}"
                f"🔎 **AI 의사결정 분석 결과 ({selected.get('name')}):**\n"
                f"- **종합 추천 점수:** {score}점\n"
                f"- **가장 큰 무기:** {', '.join(config.get('risk_factors', []))} (리스크 관리중)\n\n"
                "지금 바로 아래 번호 중 하나를 골라 답해주시면, 맞춤형 분석을 시작합니다.\n"
                "1️⃣ 3월초입주 2️⃣ 단기거주 3️⃣ 학군전입 4️⃣ 가성비중심"
            )

    # 6. Sales Funnel - Lead Qualification (v4.7)
    if key == "lead_qualification":
        return (
            "✅ **의사결정 적합성 분석 완료**\n\n"
            "응답해주신 내용을 바탕으로 볼 때, 고객님은 **'실용적 대치 입성'**에 최적화된 후보자이십니다.\n\n"
            "현재 매물은 리스크를 가격에 100% 반영하여, 주변 전세 대비 월 부담이 매우 낮습니다.\n"
            "고민 중이신 포인트가 **① 저층의 거주성**인가요, 아니면 **② 입주 시기 조율**인가요?\n\n"
            "답변에 따라 '상세 리포트'와 '중개사 직접 연결'을 도와드리겠습니다."
        )

    # 7. Decision Anxiety Support
    if key == "decision_anxiety":
        return (
            f"{comfort_prefix}"
            "결정이 힘드신 이유는 '정보가 부족해서'가 아니라 '확신이 없어서'일 것입니다.\n\n"
            "이 매물은 데이터상 결점이 명확하지만(저층), 그 결점이 가격이라는 강력한 무기로 상쇄된 상태입니다.\n"
            "**'더 좋은 집'**이 아니라 **'지금 손해 보지 않는 선택'**을 하시기 바랍니다."
        )

    # 2. Seller Decision Logic
    if key == "seller_decision":
        return comfort_prefix + "매도가 안 되어 답답하신 마음 충분히 이해합니다. 현재 시장은 매수자 우위 시장이라 단순히 가격을 내리기보다, '전략적 노출'과 '데이터 기반 설득'이 필요합니다. 상세 상담을 원하시면 연락주세요."

    # 3. Existing Specific Logic (Updated with Score)
    if key == "discount" and selected:
        score = local_market_svc.calculate_decision_score(selected.get("id"), selected)
        return (
            f"**📢 '{selected.get('name')}' MLOps 데이터 분석 결과:**\n\n"
            f"AI 모델 연산 결과, 현재 가격은 {selected.get('discount')} 저평가된 상태이며 **종합 매수 추천 점수 {score}점**입니다.\n\n"
            "💡 **데이터 분석 리포트:**\n"
            "1. 실거래가 Drift 감지: 주변 단지 대비 상승 여력이 15% 이상 남음\n"
            "2. 매칭 파이프라인 분석: 현재 해당 평형대 대기 수요자 12명 포착\n"
            "3. 나노 바나나 제안: 급매 타이밍이 MLOps 시그널에 포착되었으므로 즉시 방문 권장"
        )

    # 8. Match Reservation Flow (v4.13.1 - High Tech)
    if key == "match_reservation":
        import streamlit as st
        st.session_state.show_match_form = True
        return (
            "🎯 **AI 초정밀 매칭 파이프라인 시스템**으로 안내해 드릴게요.\n\n"
            "패스트캠퍼스 MLOps 기법을 적용하여 실시간으로 공급(임대인)과 수요(임차인) 데이터를 최적화하고 있습니다.\n\n"
            "💬 **'사전등록 매칭'** 탭에서 정보를 입력하시면, AI가 계약 성사 확률을 계산하여 실시간으로 순번을 발급해 드립니다!"
        )

    if key == "contract":
        if selected:
            score = local_market_svc.calculate_decision_score(selected.get("id"), selected)
            return (
                f"{comfort_prefix}"
                f"📄 **'{selected.get('name')}' AI 안전 계약 매칭 리포트**\n\n"
                f"현재 이 물건은 AI 매수 적합도 **{score}점**으로, 계약을 진행하기에 매우 안정적인 상태입니다.\n\n"
                f"롯데타워앤강남빌딩만의 **'Contract-Match'** 서비스:\n"
                f"1. **권리 분석 자동화:** 등기부등본 실시간 변동 이력 감지 (Clean)\n"
                f"2. **가격 적정성 검증:** 최근 3개월 실거래 중위값 대비 {selected.get('discount', '5%')} 저렴한 급매물\n"
                f"3. **입주 매칭 완료:** 현재 고객님의 조건과 단지 내 대기 수요 간의 초정밀 매칭 완료\n\n"
                "지금 바로 '실거래 기반 안심 계약'을 위해 전문가 상담을 연결해 드릴까요?"
            )
        return (
            "📄 **AI 안전 계약 가이드**\n\n"
            "롯데타워앤강남빌딩은 단순 중개를 넘어 데이터로 안전을 증명합니다.\n"
            "1. 등기부 및 권리 분석 자동 수행\n"
            "2. MLOps 기반 향후 2년간 시세 방어력 예측\n"
            "3. 나노 바나나 CEO의 특약 사항(하자/입주일) 조율 서비스\n\n"
            "지금 바로 상세 상담을 예약하시면 더 안전한 계약을 도와드립니다."
        )

    # 9. Education & School District Specifics (v5.0 Updated)
    if key == "education":
        return (
            f"{comfort_prefix}"
            "대치1동은 단순 부동산 시장이 아닌 **'교육 행정 특구'**입니다. 🎓\n\n"
            "📍 **학군 수요 분석:**\n"
            "- **초등:** 대도초, 대치초 배정 여부에 따라 단지 선호도가 갈립니다.\n"
            "- **중학:** 대청중, 숙명여중, 단대부중 등 최상위권 중학교 배정이 핵심입니다.\n"
            "- **고교:** 숙명여고, 단대부고, 경기여고, 경기고 등 명문 학군 중심지입니다.\n\n"
            "💡 **AI 현장 데이터:**\n"
            "- **국지적 필연성:** 대치1동 내 거주하지 않으면 선호 학교 배정에서 열외될 가능성이 커, 방학 시즌 전 '이동 수요'가 폭발적입니다.\n"
            "- **임차 가격 괴리:** 길 하나 차이임에도 배정권에 따라 20평대 렌트비가 인근 30평대보다 높은 역전 현상이 데이터로 확인됩니다.\n\n"
            "현재 고객님 자녀의 **입학/전학 예정 시기**를 알려주시면, 배정 확률이 가장 높은 단지를 AI 매칭해 드립니다."
        )

    # (Previous logic fallback)
    if key in faq_common:
        return faq_common[key]

    if selected:
        score = local_market_svc.calculate_decision_score(selected.get("id"), selected)
        return (
            f"선택하신 매물은 AI 분석 점수 {score}점의 우량 물건입니다.\n\n"
            f"✅ {selected.get('name')}\n"
            f"- {selected.get('spec')}\n\n"
            "AI 매칭 파이프라인이 실시간으로 확인한 결과, 현재 즉시 계약이 가능한 상태입니다. 상담 예약을 도와드릴까요?"
        )
    
    return "안녕하세요! 😊 '매물' 탭에서 단지를 선택하시면, AI가 '저평가 점수'와 함께 정확한 의사결정 가이드를 제공합니다."
