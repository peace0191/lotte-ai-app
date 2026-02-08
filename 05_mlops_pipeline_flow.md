# 🔄 MLOps 파이프라인 전체 흐름도
## 데이터부터 배포까지 한눈에 보기

> **목적**: MLOps 전체 흐름을 시각적으로 이해  
> **핵심**: 데이터 → 학습 → 배포 → 피드백 루프  
> **작성일**: 2026.02.06

---

## 📋 목차

1. [전체 개요도](#1-전체-개요도)
2. [상세 단계별 흐름](#2-상세-단계별-흐름)
3. [의사결정 트리](#3-의사결정-트리)
4. [실패 시나리오 및 복구](#4-실패-시나리오-및-복구)
5. [타임라인 및 SLA](#5-타임라인-및-sla)

---

## 1. 전체 개요도

### 1.1 MLOps 생명주기 (High-Level)

```mermaid
graph TB
    subgraph "1. 데이터 수집 & 준비"
        A1[공공 API] --> B[데이터 수집]
        A2[크롤링] --> B
        A3[자체 DB] --> B
        B --> C[데이터 검증]
        C --> D[Feature Store]
    end
    
    subgraph "2. 모델 개발 & 실험"
        D --> E[Feature Engineering]
        E --> F[모델 학습]
        F --> G[MLflow 실험 기록]
        G --> H{성능 기준<br/>충족?}
        H -->|No| F
        H -->|Yes| I[Model Registry]
    end
    
    subgraph "3. 모델 검증 & 배포"
        I --> J[Staging 배포]
        J --> K[A/B 테스트]
        K --> L{비즈니스<br/>지표 개선?}
        L -->|No| M[실험 종료]
        L -->|Yes| N[Production 승격]
    end
    
    subgraph "4. 서빙 & 모니터링"
        N --> O[API 서빙]
        O --> P[실시간 모니터링]
        P --> Q{성능 저하<br/>감지?}
        Q -->|Yes| R[알림 + 롤백]
        Q -->|No| O
    end
    
    subgraph "5. 피드백 루프"
        O --> S[사용자 행동 추적]
        S --> T[계약 데이터 수집]
        T --> U{재학습<br/>트리거?}
        U -->|Yes| D
        U -->|No| S
    end
    
    R --> N
    M --> F
    
    style H fill:#ffe1e1
    style L fill:#ffe1e1
    style Q fill:#fff4e1
    style U fill:#e1f5ff
```

### 1.2 핵심 포인트

**🔁 자동 피드백 루프**
- 계약 데이터가 다시 학습 데이터로 → 모델이 자동으로 진화
- 사람의 개입 최소화 → 확장 가능

**⚡ 빠른 실패, 빠른 복구**
- 각 단계에 검증 게이트
- 문제 발생 시 즉시 롤백

**📊 데이터 중심**
- 모델보다 데이터 품질이 우선
- Feature Store로 일관성 보장

---

## 2. 상세 단계별 흐름

### 2.1 Phase 1: 데이터 수집 (Daily)

```mermaid
graph LR
    A[Airflow DAG 실행<br/>매일 02:00] --> B{API 응답<br/>정상?}
    B -->|No| C[Slack 알림<br/>+ 3회 재시도]
    B -->|Yes| D[원본 데이터 저장<br/>S3]
    C --> B
    D --> E[스키마 검증]
    E --> F{검증<br/>통과?}
    F -->|No| G[에러 로그<br/>+ 알림]
    F -->|Yes| H[데이터 정제<br/>중복/이상치 제거]
    H --> I[PostgreSQL 적재]
    I --> J[성공 로그]
    
    style B fill:#ffe1e1
    style F fill:#ffe1e1
    style J fill:#e1ffe1
```

**입력**:
- 국토부 실거래가 API
- 네이버/다음 부동산 크롤링 데이터
- 자체 DB 매물 정보

**출력**:
- 원본 데이터: `s3://raw-data/YYYY-MM-DD/`
- 정제 데이터: PostgreSQL `properties` 테이블

**검증 조건**:
```python
# 스키마 검증
assert 'address' in df.columns
assert 'price' in df.columns

# 범위 검증
assert df['price'].between(1000, 500000).all()  # 1천만~50억

# 분포 검증
assert abs(df['price'].mean() - historical_mean) < 0.2 * historical_mean
```

**소요 시간**: 30분

---

### 2.2 Phase 2: Feature Engineering (Daily)

```mermaid
graph TB
    A[정제된 데이터] --> B[시계열 피처 생성]
    B --> C[최근 3개월 평균 가격]
    B --> D[가격 변동률]
    
    A --> E[지리 피처 생성]
    E --> F[지하철역 거리 계산]
    E --> G[학군 점수 계산]
    
    A --> H[파생 피처 생성]
    H --> I[전세가율 = 전세가/매매가]
    H --> J[평당 가격]
    H --> K[층 보정 점수]
    
    C --> L[Feature Store 저장]
    D --> L
    F --> L
    G --> L
    I --> L
    J --> L
    K --> L
    
    L --> M{피처 통계<br/>정상 범위?}
    M -->|No| N[알림 + 재생성]
    M -->|Yes| O[학습 준비 완료]
    
    style M fill:#ffe1e1
    style O fill:#e1ffe1
```

**입력**:
- `properties` 테이블
- 외부 데이터 (지하철역 좌표, 학군 정보)

**출력**:
- `features` 테이블
- 피처 명세서 (자동 생성)

**핵심 피처**:
```python
features = [
    'area_sqm',           # 면적
    'floor',              # 층
    'avg_price_3m',       # 최근 3개월 평균가
    'price_change_pct',   # 가격 변동률
    'subway_distance_m',  # 지하철 거리
    'school_score',       # 학군 점수
    'jeonse_ratio',       # 전세가율
    'price_per_pyeong',   # 평당 가격
    'floor_penalty',      # 층 보정
]
```

**소요 시간**: 20분

---

### 2.3 Phase 3: 모델 학습 (Weekly)

```mermaid
graph TB
    A[학습 트리거<br/>주 1회 or 수동] --> B[Feature Store 조회]
    B --> C[Train/Val/Test 분할<br/>70/15/15]
    
    C --> D[하이퍼파라미터 그리드]
    D --> E1[실험 1: XGBoost<br/>n=100, lr=0.1]
    D --> E2[실험 2: XGBoost<br/>n=200, lr=0.05]
    D --> E3[실험 3: LightGBM<br/>n=200, lr=0.05]
    
    E1 --> F1[MLflow Run 1]
    E2 --> F2[MLflow Run 2]
    E3 --> F3[MLflow Run 3]
    
    F1 --> G[평가: Test Set]
    F2 --> G
    F3 --> G
    
    G --> H{MAE < 350만원<br/>AND<br/>R² > 0.80?}
    H -->|No| I[실험 실패<br/>로그 기록]
    H -->|Yes| J[Best Model 선택]
    
    J --> K[SHAP 값 계산]
    K --> L[Model Registry 등록]
    L --> M[Staging 스테이지]
    
    style H fill:#ffe1e1
    style M fill:#e1ffe1
```

**MLflow 로깅 내용**:
```python
with mlflow.start_run():
    # 1. 파라미터
    mlflow.log_params({
        'n_estimators': 200,
        'learning_rate': 0.05,
        'max_depth': 5,
    })
    
    # 2. 메트릭
    mlflow.log_metrics({
        'mae': 320,
        'rmse': 480,
        'r2': 0.83,
    })
    
    # 3. 아티팩트
    mlflow.log_artifact('feature_importance.png')
    mlflow.log_artifact('shap_summary.png')
    
    # 4. 모델
    mlflow.sklearn.log_model(model, 'model')
```

**소요 시간**: 30분 (3개 실험 병렬 실행)

---

### 2.4 Phase 4: A/B 테스트 (1-2주)

```mermaid
graph TB
    A[Staging 모델 준비] --> B[트래픽 분할 설정<br/>90% Prod / 10% Staging]
    
    B --> C[1주차 데이터 수집]
    C --> D[지표 계산]
    
    D --> E1[Production 모델<br/>계약 성사율: 12%]
    D --> E2[Staging 모델<br/>계약 성사율: 13.5%]
    
    E1 --> F{통계적<br/>유의성?<br/>p < 0.05}
    E2 --> F
    
    F -->|No| G[데이터 더 수집<br/>2주차 진행]
    F -->|Yes| H{Staging<br/>성과 > Prod?}
    
    H -->|No| I[Staging 기각<br/>원인 분석]
    H -->|Yes| J[Production 승격 승인]
    
    J --> K[Blue-Green 배포]
    K --> L[100% 트래픽 전환]
    L --> M[이전 모델 Archived]
    
    G --> C
    
    style F fill:#ffe1e1
    style H fill:#ffe1e1
    style M fill:#e1ffe1
```

**측정 지표**:
```python
metrics = {
    'primary': {
        'contract_rate': '계약 성사율',  # 주요 지표
    },
    'secondary': {
        'ctr': '클릭율',
        'inquiry_rate': '문의율',
        'avg_contract_amount': '평균 계약 금액',
    }
}
```

**통계 검정**:
```python
from scipy.stats import ttest_ind

control_conversions = [0, 1, 0, 1, 1, ...]  # Production
treatment_conversions = [0, 1, 1, 1, 1, ...]  # Staging

t_stat, p_value = ttest_ind(control_conversions, treatment_conversions)

if p_value < 0.05:
    print("통계적으로 유의미한 차이 있음")
```

**소요 시간**: 1-2주 (트래픽에 따라)

---

### 2.5 Phase 5: 배포 (10분)

```mermaid
graph LR
    A[Production 승격 승인] --> B[Blue 환경<br/>현재 Production v1.2]
    A --> C[Green 환경<br/>새 모델 v1.3 배포]
    
    C --> D[Health Check<br/>Green 환경]
    D --> E{정상<br/>응답?}
    E -->|No| F[배포 실패<br/>알림]
    E -->|Yes| G[트래픽 전환<br/>Blue → Green]
    
    G --> H[5분간 모니터링]
    H --> I{에러율<br/>< 1%?}
    I -->|No| J[즉시 롤백<br/>Green → Blue]
    I -->|Yes| K[Blue 환경 대기]
    
    K --> L[24시간 모니터링]
    L --> M{안정적?}
    M -->|No| J
    M -->|Yes| N[Blue 환경 종료<br/>v1.2 Archived]
    
    style E fill:#ffe1e1
    style I fill:#ffe1e1
    style M fill:#ffe1e1
    style N fill:#e1ffe1
```

**배포 체크리스트**:
```yaml
pre_deployment:
  - [ ] MLflow에 모델 등록 확인
  - [ ] A/B 테스트 통계적 유의성 확인
  - [ ] 배포 승인 문서 작성
  - [ ] 롤백 계획 수립

deployment:
  - [ ] Green 환경에 새 모델 배포
  - [ ] Health check 통과
  - [ ] 트래픽 1% 라우팅 (smoke test)
  - [ ] 트래픽 100% 전환

post_deployment:
  - [ ] 에러율 모니터링 (< 1%)
  - [ ] 응답 시간 모니터링 (< 500ms)
  - [ ] 비즈니스 지표 추적
  - [ ] 24시간 안정화 확인
```

**소요 시간**: 10분 (자동화)

---

### 2.6 Phase 6: 모니터링 & 피드백 (실시간)

```mermaid
graph TB
    A[API 요청] --> B[Prediction]
    B --> C[로깅<br/>요청/응답/지연시간]
    
    C --> D[Prometheus 수집]
    D --> E[Grafana 시각화]
    
    E --> F{에러율<br/>> 5%?}
    E --> G{응답시간<br/>> 1초?}
    E --> H{MAE 증가<br/>> 20%?}
    
    F -->|Yes| I[즉시 롤백 알림]
    G -->|Yes| J[인프라 스케일업]
    H -->|Yes| K[재학습 스케줄링]
    
    B --> L[사용자 행동 추적]
    L --> M[클릭/문의/계약]
    M --> N[DB 저장]
    
    N --> O{계약 성사?}
    O -->|Yes| P[학습 데이터 추가]
    P --> Q{데이터 변화<br/>> 10%?}
    Q -->|Yes| K
    
    K --> R[자동 재학습 트리거]
    
    style F fill:#ffe1e1
    style G fill:#ffe1e1
    style H fill:#ffe1e1
```

**모니터링 대시보드**:
```
📊 실시간 메트릭
━━━━━━━━━━━━━━━━━━━━━━━━
API 응답 시간 (P95):    245ms ✅
에러율:                0.3% ✅
예측 지연 시간:         12ms ✅

📈 모델 성능
━━━━━━━━━━━━━━━━━━━━━━━━
MAE (최근 7일):         320만원 ✅
예측 정확도:            83% ✅
데이터 드리프트 점수:    0.12 ✅

💼 비즈니스 지표
━━━━━━━━━━━━━━━━━━━━━━━━
일일 예측 수:           2,450건
계약 성사율:            13.2% ✅
평균 계약 금액:         4.2억원
```

---

## 3. 의사결정 트리

### 3.1 모델 승격 결정 플로우

```mermaid
graph TB
    A[새 모델 학습 완료] --> B{기술 지표<br/>충족?}
    B -->|No| C[실험 종료<br/>원인 분석]
    B -->|Yes| D[Staging 등록]
    
    D --> E[A/B 테스트 시작]
    E --> F{1주일<br/>데이터 충분?}
    F -->|No| G[데이터 더 수집]
    G --> F
    
    F -->|Yes| H{통계적<br/>유의성?<br/>p < 0.05}
    H -->|No| C
    
    H -->|Yes| I{비즈니스<br/>지표 개선?}
    I -->|No| C
    
    I -->|Yes| J{개선율<br/>> 5%?}
    J -->|No| K[보류<br/>추가 검토]
    
    J -->|Yes| L[자동 승격]
    L --> M[Production 배포]
    
    M --> N[24시간 모니터링]
    N --> O{안정적?}
    O -->|No| P[롤백]
    O -->|Yes| Q[승격 확정]
    
    style B fill:#ffe1e1
    style H fill:#ffe1e1
    style I fill:#ffe1e1
    style J fill:#ffe1e1
    style O fill:#ffe1e1
    style Q fill:#e1ffe1
```

---

## 4. 실패 시나리오 및 복구

### 4.1 데이터 수집 실패

```mermaid
graph LR
    A[API 호출 실패] --> B[재시도 1/3]
    B --> C{성공?}
    C -->|No| D[재시도 2/3]
    D --> E{성공?}
    E -->|No| F[재시도 3/3]
    F --> G{성공?}
    G -->|No| H[Slack 알림<br/>온콜 엔지니어]
    G -->|Yes| I[데이터 수집 계속]
    C -->|Yes| I
    E -->|Yes| I
    
    H --> J[수동 개입<br/>API 키 확인]
    J --> K[백업 소스 사용<br/>크롤링 데이터]
    
    style H fill:#ffe1e1
```

**복구 시간**: 2시간 (수동 개입)

---

### 4.2 모델 성능 저하

```mermaid
graph TB
    A[모니터링 알림<br/>MAE 20% 증가] --> B[즉시 조사]
    
    B --> C{데이터<br/>드리프트?}
    C -->|Yes| D[재학습 스케줄링<br/>최신 데이터 사용]
    
    C -->|No| E{코드<br/>버그?}
    E -->|Yes| F[핫픽스 배포]
    
    E -->|No| G{인프라<br/>문제?}
    G -->|Yes| H[리소스 증설]
    
    G -->|No| I[이전 모델로 롤백]
    I --> J[근본 원인 분석]
    
    style A fill:#ffe1e1
```

**복구 시간**: 30분 (자동 롤백)

---

### 4.3 배포 실패

```mermaid
graph LR
    A[배포 시작] --> B[Green 환경<br/>Health Check]
    B --> C{정상?}
    C -->|No| D[배포 중단]
    D --> E[로그 분석]
    E --> F[수정 후 재시도]
    
    C -->|Yes| G[트래픽 전환]
    G --> H[5분간 모니터링]
    H --> I{에러율<br/>< 1%?}
    I -->|No| J[자동 롤백<br/>Blue 환경으로]
    I -->|Yes| K[배포 성공]
    
    J --> L[원인 분석<br/>다음 배포 준비]
    
    style C fill:#ffe1e1
    style I fill:#ffe1e1
    style K fill:#e1ffe1
```

**복구 시간**: 즉시 (자동 롤백)

---

## 5. 타임라인 및 SLA

### 5.1 전체 파이프라인 타임라인

```
Day 1 (월요일)
02:00 ├─ 데이터 수집 시작
02:30 ├─ Feature Engineering
03:00 ├─ 데이터 준비 완료
      │
09:00 ├─ 주간 모델 학습 트리거
09:30 ├─ 3개 실험 병렬 실행
10:00 ├─ Best Model 선택
10:15 ├─ Staging 등록
      │
Day 2-8 (화~월)
      ├─ A/B 테스트 진행 (10% 트래픽)
      ├─ 데이터 수집 중
      │
Day 9 (화요일)
10:00 ├─ A/B 테스트 분석
10:30 ├─ 통계적 유의성 확인
11:00 ├─ Production 승격 결정
11:10 ├─ Blue-Green 배포
11:20 ├─ 배포 완료 ✅
      │
Day 9-10
      ├─ 24시간 안정화 모니터링
      │
Day 10
11:20 ├─ 이전 모델 Archived
      └─ 사이클 완료
```

### 5.2 SLA (Service Level Agreement)

| 지표 | 목표 | 알림 임계값 | 조치 |
|------|------|-------------|------|
| **API 응답 시간 (P95)** | < 500ms | > 800ms | 인프라 스케일업 |
| **API 에러율** | < 1% | > 3% | 즉시 롤백 |
| **예측 정확도 (MAE)** | < 350만원 | > 420만원 | 재학습 스케줄 |
| **데이터 수집 성공률** | > 95% | < 90% | 백업 소스 사용 |
| **모델 학습 시간** | < 1시간 | > 2시간 | 리소스 증설 검토 |
| **배포 다운타임** | 0초 | > 0초 | 롤백 + 프로세스 검토 |
| **A/B 테스트 기간** | 1-2주 | > 3주 | 트래픽 증가 필요 |

### 5.3 온콜 대응 프로토콜

```
📱 알림 우선순위
━━━━━━━━━━━━━━━━━━━━━━━━
P0 (Critical): 즉시 대응 (15분 내)
- API 완전 다운
- 에러율 > 10%
- 데이터 유실

P1 (High): 30분 내 대응
- 에러율 3-10%
- 응답 시간 > 1초
- 배포 실패

P2 (Medium): 2시간 내 대응
- MAE 20% 증가
- 데이터 수집 실패
- 디스크 사용률 > 80%

P3 (Low): 영업일 내 대응
- 성능 최적화 권장
- 리팩토링 필요
```

---

## 6. 핵심 원칙 요약

### 6.1 설계 철학

> **"자동화할 수 있는 것은 모두 자동화하되, 중요한 의사결정은 투명하게"**

1. **자동화 우선**
   - 데이터 수집 → 자동
   - Feature Engineering → 자동
   - 모델 학습 → 자동
   - A/B 테스트 → 자동
   - 배포 → 반자동 (승인 필요)

2. **빠른 실패, 빠른 복구**
   - 각 단계에 검증 게이트
   - 문제 감지 시 즉시 알림
   - 자동 롤백 메커니즘

3. **데이터 중심**
   - 모델보다 데이터 품질 우선
   - Feature Store로 일관성 보장
   - 피드백 루프로 지속 개선

4. **투명성**
   - 모든 실험 MLflow에 기록
   - 의사결정 기준 명확화
   - 성능 지표 실시간 공개

### 6.2 성공 지표

```
✅ 배포 빈도: 주 1회 → 월 4회
✅ 배포 성공률: > 95%
✅ 롤백 시간: < 5분
✅ 모델 성능: MAE < 350만원
✅ API 가용성: > 99.9%
✅ 자동화율: > 80%
```

---

## 7. 다음 단계

이 흐름도를 바탕으로:

1. ✅ **코드 구현**: 각 단계의 실제 코드 작성
2. **자동화 강화**: CI/CD 파이프라인 구축
3. **모니터링 고도화**: 더 세밀한 메트릭 수집
4. **확장**: 멀티 모델, 멀티 지역 지원

---

**문서 버전**: v1.0  
**최종 수정**: 2026.02.06  
**다음 업데이트**: 실제 운영 데이터 기반 타임라인 조정
