FROM python:3.11-slim

# 보안: root 사용자 대신 일반 사용자 생성
RUN useradd -m -u 1000 appuser

WORKDIR /app

# 시스템 패키지 업데이트 및 curl 설치 (헬스체크용)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 종속성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY --chown=appuser:appuser . .

# 일반 사용자로 전환
USER appuser

# 포트 노출
EXPOSE 8000

# 실행
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
