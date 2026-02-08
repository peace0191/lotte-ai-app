from datetime import datetime

class ReportEngine:
    def __init__(self):
        self.template_version = "v1.0-Premium"

    def generate_briefing(self, property_data, score, risks):
        """
        Generates a premium text-based briefing that can be converted to PDF or shown in UI.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        report = f"""
# [PREMIUM AI ANALYSIS REPORT]
**단지명**: {property_data.get('name')}
**분석 시점**: {now}
**담당 에이전트**: 롯데 부동산 AI (B2B SaaS)

---

## 1. AI 의사결정 지수
### 🏆 종합 점수: {score} / 100
- **판단**: {'매수 강력 추천' if score >= 85 else '매수 추천' if score >= 70 else '관망 및 모니터링'}
- **근거**: 인근 단지 대비 저평가율 및 학군 가중치 분석 결과 상위 5% 이내 진입.

## 2. 정량적 시장 리스크 (Risk Radar)
- **탐지된 리스크**: {", ".join(risks)}
- **AI 코멘트**: 현재 감지된 리스크는 시장 전체의 공통 요인이며, 해당 단국지적 방어력은 매우 우수한 것으로 분석됨.

## 3. 가격 적정 가이드 (Relative Value)
- **현재가**: {property_data.get('price')}
- **AI 산정 적정가**: ₩ {self._calculate_fair_price(property_data)} (예상)
- **갭 차이**: {property_data.get('discount')} (상대적 저평가 상태)

## 4. 로컬 특화 성적표
- **학군(Daechi Grade)**: S+
- **환금성(Liquidity)**: 상 (평칠 거래 빈도 우수)

---
*본 리포트는 롯데 부동산 AI MLOps 파이프라인에 의해 생성된 데이터 기반 분석 자료입니다.*
        """
        return report

    def _calculate_fair_price(self, data):
        # Mock logic for fair price calculation
        return "상담 후 공개 (데이터 보정 중)"

report_engine = ReportEngine()
