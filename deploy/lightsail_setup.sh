#!/bin/bash

# ============================================
# 🚀 AWS Lightsail 자동 배포 스크립트
# ============================================
#
# 사용법:
# 1. Lightsail 인스턴스 생성 (Ubuntu 22.04)
# 2. SSH 접속
# 3. 이 스크립트 실행: bash lightsail_setup.sh
#
# ============================================

set -e  # 에러 발생 시 중단

echo "============================================"
echo "🚀 Lotte RealEstate API 배포 시작"
echo "============================================"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1️⃣ 시스템 업데이트
echo -e "${YELLOW}📦 시스템 업데이트 중...${NC}"
sudo apt update && sudo apt upgrade -y

# 2️⃣ 필수 패키지 설치
echo -e "${YELLOW}📦 필수 패키지 설치 중...${NC}"
sudo apt install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    net-tools

# 3️⃣ Docker 설치
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}🐳 Docker 설치 중...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker 설치 완료${NC}"
else
    echo -e "${GREEN}✅ Docker 이미 설치됨${NC}"
fi

# 4️⃣ Docker Compose 설치
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}🐳 Docker Compose 설치 중...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose 설치 완료${NC}"
else
    echo -e "${GREEN}✅ Docker Compose 이미 설치됨${NC}"
fi

# 5️⃣ 프로젝트 클론 또는 업데이트
PROJECT_DIR="/home/ubuntu/lotte-ai-app"

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}🔄 프로젝트 업데이트 중...${NC}"
    cd $PROJECT_DIR
    git pull
else
    echo -e "${YELLOW}📥 프로젝트 클론 중...${NC}"
    git clone https://github.com/peace0191/lotte-ai-app.git $PROJECT_DIR
    cd $PROJECT_DIR
fi

# 6️⃣ 환경변수 설정
echo -e "${YELLOW}🔑 환경변수 설정 중...${NC}"

if [ ! -f ".env" ]; then
    cat > .env <<EOF
# 환경 설정
ENVIRONMENT=production
DEBUG=false

# API 보안 키 (자동 생성)
API_SECRET_KEY=$(openssl rand -hex 32)

# 데이터베이스
DATABASE_URL=sqlite:///./lotte_realestate.db

# 허용된 도메인
ALLOWED_ORIGINS=https://lotte-ai-app.streamlit.app,http://localhost:8501

# 서버 정보
SERVER_NAME=Lightsail-Production
TIMEZONE=Asia/Seoul
EOF
    echo -e "${GREEN}✅ .env 파일 생성 완료${NC}"
else
    echo -e "${GREEN}✅ .env 파일 이미 존재${NC}"
fi

# 7️⃣ Docker 이미지 빌드 및 실행
echo -e "${YELLOW}🏗️ Docker 컨테이너 빌드 및 실행 중...${NC}"

# 기존 컨테이너 중지 및 삭제
docker-compose down 2>/dev/null || true

# 새로운 컨테이너 시작
docker-compose up -d --build

# 8️⃣ 상태 확인
echo -e "${YELLOW}⏳ 서버 시작 대기 중...${NC}"
sleep 10

if curl -f http://localhost:8000/health &> /dev/null; then
    echo -e "${GREEN}✅ API 서버 정상 작동 중!${NC}"
else
    echo -e "${RED}❌ API 서버 시작 실패${NC}"
    docker-compose logs api
    exit 1
fi

# 9️⃣ 방화벽 설정 안내
echo ""
echo "============================================"
echo -e "${GREEN}🎉 배포 완료!${NC}"
echo "============================================"
echo ""
echo "📋 다음 단계:"
echo ""
echo "1️⃣ Lightsail 콘솔에서 방화벽 규칙 추가:"
echo "   - 포트 8000 TCP 허용"
echo ""
echo "2️⃣ API 테스트:"
INSTANCE_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "   http://${INSTANCE_IP}:8000/health"
echo "   http://${INSTANCE_IP}:8000/docs"
echo ""
echo "3️⃣ Streamlit Cloud Secrets 업데이트:"
echo "   [api]"
echo "   url = \"http://${INSTANCE_IP}:8000\""
echo "   key = \"$(grep API_SECRET_KEY .env | cut -d '=' -f2)\""
echo ""
echo "4️⃣ 로그 확인:"
echo "   docker-compose logs -f api"
echo ""
echo "5️⃣ 재시작:"
echo "   docker-compose restart api"
echo ""
echo "============================================"
