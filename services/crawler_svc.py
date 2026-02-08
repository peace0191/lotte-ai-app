import random

class CrawlerService:
    def __init__(self):
        self.platforms = ["YouTube Shorts", "Naver Blog", "Instagram", "맘카페"]
        self.mock_leads = [
            {"platform": "YouTube", "content": "대치 SK뷰 26평 반전세 자리 있나요? 3월 초 입주 희망해요.", "category": "BUYER"},
            {"platform": "Naver Blog", "content": "시그니엘 월세 매물 찾고 있습니다. 법인 계약 가능할까요?", "category": "BUYER"},
            {"platform": "Instagram", "content": "#시그니엘 #강남빌딩 매각 관심 있는 법인입니다.", "category": "SELLER"},
            {"platform": "맘카페", "content": "래대팰 전세 만기라 급하게 대치동 20평대 반전세 구해요.", "category": "BUYER"}
        ]

    def crawl_social_leads(self, keyword):
        """SNS 채널에서 키워드 기반 잠재 고객 크롤링 (Simulation)"""
        results = []
        for lead in self.mock_leads:
            if keyword in lead["content"] or keyword in ["대치동", "잠실동", "강남"]:
                results.append({
                    "id": f"social_{random.randint(1000, 9999)}",
                    "platform": lead["platform"],
                    "summary": lead["content"][:30] + "...",
                    "category": lead["category"],
                    "intent_score": random.randint(80, 100)
                })
        return results

# Singleton
crawler_svc = CrawlerService()
