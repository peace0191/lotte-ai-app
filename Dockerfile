# Dockerfile for Lotte Tower AI App
FROM python:3.11-slim-bookworm

WORKDIR /app

# apt-get은 시간을 단축하기 위해 생략합니다.
COPY requirements.txt .
RUN pip3 install --no-cache-dir --retries 10 --timeout 60 -r requirements.txt

COPY . .

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
