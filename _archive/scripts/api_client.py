import streamlit as st
import requests
import json
from typing import Dict, Any

class APIClient:
    """
    Streamlit 앱과 FastAPI 서버 간의 안전한 통신을 담당하는 클라이언트
    """
    def __init__(self):
        # secrets.toml에서 설정 읽기 (없으면 기본값 사용)
        try:
            self.base_url = st.secrets["api"]["url"]
            self.api_key = st.secrets["api"]["key"]
        except (FileNotFoundError, KeyError):
            # 로컬 개발 환경용 기본값 (경고 표시)
            self.base_url = "http://localhost:8000"
            self.api_key = "TEST_KEY_CHANGE_ME_IN_PROD"
            # st.warning("⚠️ API 설정이 감지되지 않았습니다. 로컬 기본값(localhost:8000)을 사용합니다.")
        
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }

    def _post(self, endpoint, data):
        """내부용 POST 요청 처리 함수"""
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}", 
                json=data, 
                headers=self.headers,
                timeout=10 # 10초 타임아웃 (설문 데이터 등)
            )
            response.raise_for_status() # 4xx, 5xx 에러 발생 시 예외 처리
            return response.json()
        except requests.exceptions.HTTPError as e:
            st.error(f"🛑 API 오류 ({e.response.status_code}): {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"🔌 서버 통신 오류: {e}")
            return None
        except Exception as e:
            st.error(f"⚠️ 알 수 없는 오류: {e}")
            return None

    def _get(self, endpoint, params=None):
        """내부용 GET 요청 처리 함수"""
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}", 
                params=params, 
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"🔌 서버 통신 오류: {e}")
            return None

    # --- 실제 서비스 기능 ---

    def check_health(self):
        """API 서버 상태 확인"""
        return self._get("/")

    def submit_vip_survey(self, user_name: str, user_phone: str, survey_data: Dict[str, Any]):
        """
        VIP 50문항 설문 데이터 제출 (보안 적용)
        """
        payload = {
            "user_name": user_name,
            "user_phone": user_phone,
            "survey_data": survey_data
        }
        return self._post("/api/v1/vip-survey", payload)

    def register_demand(self, demand_data):
        """수요자(매수/임차) 등록 (기본형)"""
        return self._post("/api/v1/demand", demand_data)

    def register_supply(self, supply_data):
        """공급자(매도/임대) 등록"""
        return self._post("/api/v1/supply", supply_data)

    def run_matching(self, demand_id):
        """AI 매칭 실행"""
        # POST 요청이지만 body 대신 query parameter로 id 전달하는 경우 등 API spec에 맞춤
        # 현재 API main.py 설계상: POST /api/v1/match?demand_id=...
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/match",
                params={"demand_id": demand_id},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(str(e))
            return None

    def create_reservation(self, reservation_data):
        """예약 신청"""
        return self._post("/api/v1/reservation", reservation_data)

    def get_listings(self, region=None):
        """매물 리스트 조회"""
        params = {"region": region} if region else {}
        return self._get("/api/v1/listings", params)

# 전역에서 사용할 수 있는 인스턴스
client = APIClient()
