import os
import secrets
from fastapi import Security, HTTPException, status, Request
from fastapi.security import APIKeyHeader
from datetime import datetime, timedelta

# 1. API KEY 보안 설정
# 헤더에서 'X-API-Key'를 찾습니다.
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# 환경변수에서 키를 가져오거나, 없으면 랜덤 생성 (로그에 출력됨)
# 실운영시는 반드시 .env 파일나 Docker env로 주입해야 합니다.
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
if not API_SECRET_KEY:
    generated_key = secrets.token_hex(32)
    print(f"\n[SECURITY WARNING] API_SECRET_KEY not found. Generated temporary key: {generated_key}\n")
    VALID_API_KEYS = {generated_key}
else:
    VALID_API_KEYS = set(API_SECRET_KEY.split(","))

# 2. Rate Limiting (DDoS 방지 - 간단한 인메모리 버전)
request_history = {}

def rate_limit(request: Request):
    """
    IP당 1분에 60회 요청 제한
    """
    client_ip = request.client.host
    now = datetime.now()
    window = timedelta(minutes=1)
    
    # 기록 초기화 (오래된 것 삭제)
    if client_ip not in request_history:
        request_history[client_ip] = []
    
    request_history[client_ip] = [t for t in request_history[client_ip] if now - t < window]
    
    # 체크
    if len(request_history[client_ip]) > 60:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    request_history[client_ip].append(now)

# 3. 인증 의존성 함수
async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    """
    모든 중요 API 요청마다 이 함수가 실행되어 키를 검사합니다.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials (Missing API Key)"
        )
    
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    
    return api_key
