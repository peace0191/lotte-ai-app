#!/usr/bin/env bash
# Fail-fast 및 Bash 엄격 모드 적용
set -euo pipefail

echo "[4/6] Configuring Docker DNS (Infrastructure Level)..."
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json >/dev/null <<EOF
{
  "dns": ["8.8.8.8", "1.1.1.1"]
}
EOF

# [C] systemctl 의존성 제거 및 환경별 최적화된 재시작 로직
if command -v systemctl >/dev/null 2>&1; then
    sudo systemctl daemon-reload
    sudo systemctl restart docker || sudo systemctl start docker
elif command -v service >/dev/null 2>&1; then
    sudo service docker restart
else
    sudo /etc/init.d/docker restart
fi

sleep 3
echo "[OK] Docker DNS configured."

# [A] alpine 이미지 내 bind-tools 설치 및 정밀 검증 (nslookup, curl 통합)
echo "[5/6] Verifying DNS/HTTPS Connectivity (Gatekeeping)..."
sudo docker run --rm alpine:3.20 sh -lc \
"apk add --no-cache bind-tools ca-certificates curl >/dev/null && \
 nslookup pypi.org >/dev/null && \
 curl -fsS https://pypi.org/simple/ >/dev/null"

echo "DNS Verification Success: OK"
