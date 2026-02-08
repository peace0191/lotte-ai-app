import random
from typing import Dict, Any

TEMPLATES = {
    "undervalue_hook": [
        "{지역}에서 이 가격… 말이 돼요? {단지} {평형}이 {가격}입니다.",
        "실거래 {실거래}인데, 지금 {가격}. 할인율 {할인율}. 이건 급매죠.",
        "오늘 올라온 숨은 저평가 1건. {단지} {평형} 15초 요약 갑니다.",
        "{지역} 국평 라인에서 {가격}이면 흔치 않습니다.",
        "이 가격은 이유가 있어요. 체크 포인트 3개만 보면 결론 납니다.",
    ],
    "data_proof": [
        "최근 90일 실거래 중위 {실거래}. 현재 {가격} → {할인율}.",
        "같은 평형 최근 거래가 {실거래}. 이 매물은 그보다 낮아요.",
        "저평가 점수 {score}/100. 실거래 기반으로 계산했습니다.",
        "체크 3가지: 층/향/수리. 여기 통과하면 ‘진짜 급매’입니다.",
        "학군·교통 프리미엄인데 가격이 내려온 포인트는 {포인트}입니다.",
    ],
    "cta": [
        "원하시면 {지역} 저평가 TOP5 뽑아드릴게요. 댓글 ‘TOP5’.",
        "링크/문의 주시면 실거래 비교표+체크리스트 드립니다.",
        "DM 주시면 조건 맞춰 ‘진짜 급매’만 골라드려요.",
        "다음 영상에서 {지역} 2탄 갑니다. 팔로우 해두세요.",
        "결론: {단지} {평형} {가격}, 실거래 {실거래}, 할인 {할인율}. 저장!",
    ]
}

class ScriptTemplateService:
    def __init__(self):
        self.templates = TEMPLATES

    def _fmt_money(self, won: int) -> str:
        if won is None:
            return "-"
        eok = won / 100_000_000
        if eok >= 1:
            return f"{eok:.1f}억"
        man = won / 10_000
        return f"{man:.0f}만"

    def make_shorts_script(self, ent: Dict[str, Any], score_data: Dict[str, Any]) -> str:
        score = score_data.get("score", 50)
        evidence_data = score_data.get("evidence", {})
        
        region = ent.get("LOC_DONG") or "이 지역"
        complex_name = ent.get("COMPLEX") or "이 단지"
        pyeong = ent.get("AREA_PYEONG")
        pyeong_txt = f"{pyeong}평" if pyeong else "인기 평형"

        ask = ent.get("sale_won")
        rt = evidence_data.get("rt_median_180d")
        rt_count = evidence_data.get("rt_count_180d", 0)

        price_txt = self._fmt_money(ask)
        rt_txt = self._fmt_money(rt)
        disc_txt = f"{evidence_data.get('discount_rate', 0)*100:.0f}%"

        # 1. Hook Selection (Precise Branching)
        if score >= 75:
            hook = random.choice(self.templates["undervalue_hook"])
        elif score >= 65:
            hook = f"데이터로 검증된 {region} {complex_name}의 적정 가치를 공개합니다."
        else:
            hook = f"🛑 {complex_name} 허위 급매 주의! AI가 실제 가치를 비교 분석해 드립니다."

        # 2. Evidence (Statistical Proof)
        sample_caution = ""
        if rt_count < 5:
            sample_caution = " (※ 현재 거래 표본이 적어 주의가 필요합니다)"
        
        proof = f"최근 180일 실거래 중위 {rt_txt}. 현재 {price_txt}로 {disc_txt} 저평가 확인.{sample_caution}"
        
        # 3. Features & CTA
        feats = ent.get("FEATURE") or []
        point = "급매" if "급매" in feats else ("학군" if "학군" in feats else "입지")
        
        cta = random.choice(self.templates["cta"])

        def render(s: str) -> str:
            # Simple format but robust for precise data
            try:
                return s.format(
                    지역=region, 단지=complex_name, 평형=pyeong_txt,
                    가격=price_txt, 실거래=rt_txt, 할인율=disc_txt,
                    score=score, 포인트=point, cta_msg="지금 상담 예약"
                )
            except:
                return s # Fallback if format fails

        return f"[0-2초: 훅]\n{render(hook)}\n\n[3-10초: 근거]\n{proof}\n\n[11-15초: CTA]\n{render(cta)}"

script_template_svc = ScriptTemplateService()
