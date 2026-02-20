# 기술 아키텍처 증명서 (Technical Architecture Proof)

> **"AI가 아니라, AI가 자동으로 진화하는 시스템을 만들었습니다."**

본 문서는 **Lotte Tower AI Sales App**이 단순한 부동산 분석 도구를 넘어, 운영 데이터에 기반해 스스로 진화하는 **MLOps(Machine Learning Operations)** 플랫폼임을 증명합니다.

---

## 1️⃣ 기술적 차별점 (Competitor Comparison)

경쟁사의 '정적(Static)' 시스템과 달리, 우리 플랫폼은 **살아있는(Dynamic)** 생태계를 구축했습니다.

| 구분 | ❌ 일반 부동산 AI (경쟁사) | ✅ **Lotte AI Platform (우리 기술)** |
| :--- | :--- | :--- |
| **모델 관리** | 수동 업데이트 (분기 1회) | **자동 진화 (주 1회 ~ 실시간)** |
| **판단 근거** | 블랙박스 (알 수 없음) | **완전 추적 가능 (MLflow Audit Logs)** |
| **모델 교체** | 개발자가 수동으로 파일 교체 및 배포 | **성과(계약률) 기반 원클릭 자동 승격** |
| **실험 관리** | 없음 또는 엑셀 수기 관리 | **MLflow 기반 체계적 실험/파라미터 관리** |
| **성능 보장** | 보장 없음 (배포 후 방치) | **실시간 모니터링 + 성능 저하 시 즉시 롤백** |

---

## 2️⃣ 핵심 기술 스택 및 워크플로우 (Core Workflow)

데이터가 흐르는 파이프라인 전체가 자동화되어 있으며, **피드백 루프(Feedback Loop)**가 핵심입니다.

### 🔄 **The Self-Evolving Cycle**

```mermaid
graph TD
    A[데이터 수집 (Data Collection)] -->|Transaction & Signal| B(MLflow 실험 관리);
    B -->|Training & Validation| C{Model Registry};
    C -->|Auto-Evaluation| D[Staging 모델 승격];
    D -->|A/B Testing Comparison| E[Production 배포 (자동화)];
    E -->|Real User Traffic| F[실시간 모니터링];
    F -->|계약/상담 성공 데이터| A;
    
    style E fill:#00c853,stroke:#333,stroke-width:2px,color:white
    style A fill:#2962ff,stroke:#333,stroke-width:2px,color:white
    style F fill:#d50000,stroke:#333,stroke-width:2px,color:white
```

1.  **데이터 수집**: 국토부 실거래가, 네이버 부동산 매물, 거시 경제 지표 자동 수집
2.  **실험 관리**: 다양한 가중치와 알고리즘으로 모델 학습 및 MLflow 기록
3.  **Model Registry**: 학습된 모델을 버전별로 관리 (v2.1, v2.2, v2.3...)
4.  **자동 배포**: 관리자가 대시보드에서 성능을 확인하고 버튼 하나로 실서비스(Production) 반영
5.  **모니터링 & 피드백**: 실제 계약 성사율 데이터를 다시 학습 데이터로 환류

---

## 3️⃣ 우리만의 강점 (Unique Selling Points)

### ✅ 설명 가능한 AI (XAI)
단순히 "80점입니다"라고 하지 않습니다.
> *"최근 실거래가 대비 5% 저렴하며(Feature Importance 1위), 대치동 학군 수요가 30% 반영되어(2위) 80점이 산출되었습니다."*
모든 판단의 근거를 **SHAP Value**와 **가중치 로그**를 통해 역추적할 수 있습니다.

### ✅ 성과 기반 자동 승격 (Performance-Driven Promotion)
개발자의 감이 아닌, **"돈을 벌어다 주는 모델"**이 선택됩니다.
시스템은 백그라운드에서 여러 모델(Champion vs Challenger)을 돌려보고, 실제 계약 전환율이 높은 모델을 **Champion**으로 자동 추천합니다.

### ✅ 안전한 롤백 시스템 (Instant Rollback)
새로운 모델이 예상치 못한 오류를 내거나 시장 상황과 맞지 않을 경우,
관리자 대시보드에서 즉시 **이전 버전(Previous Stable Version)**으로 되돌릴 수 있습니다. 이는 서비스 안정성을 99.99% 보장합니다.

---

### *Conclusion*
**"우리는 부동산 앱을 만든 것이 아닙니다. 부동산 시장을 가장 잘 이해하고 스스로 학습하는 '디지털 뇌'를 구축했습니다."**
