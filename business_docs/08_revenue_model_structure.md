# 💰 수익 예측 모델 구조 (Revenue Model Structure)

### 📌 엑셀 계산 구조 (Revenue Forecast Logic)

이 구조는 **3가지 주요 수익원(Revenue Streams)**으로 구성됩니다.
1.  **중개 수수료 (Core Logic)**
2.  **구독 (SaaS Logic)**
3.  **데이터/광고 (Platform Logic)**

---

### [Stream 1] 중개 수수료 (Core Logic)

**변수 (Variables)**:
- `V`: 월 방문자 수 (MAU)
- `C1`: 상세 진입 전환율 (%)
- `C2`: 상담 요청 전환율 (%)
- `C3`: 계약 성사율 (Closing Rate, %)
- `P`: 평균 거래가 (Transaction Value)
- `R`: 평균 수수료율 (Commission Rate, %)

**공식 (Formula)**:
> **Core Revenue = V * C1 * C2 * C3 * (P * R)**

---

### [Stream 2] 리드 우선 배정 구독 (SaaS Logic)

**변수 (Variables)**:
- `A`: 활성 파트너 수 (Partner Agencies)
- `S`: 월 구독료 (Subscription Fee, 99,000원 ~ 499,000원)
- `L`: 리드 당 추가 과금 (Cost Per Lead, CPL)

**공식 (Formula)**:
> **SaaS Revenue = (A * S) + (High-Intent Leads * L)**

---

### [Stream 3] 광고 최적화 및 데이터 판매 (Platform Logic)

**변수 (Variables)**:
- `I`: 월 노출 수 (Impressions)
- `CPM`: 1000회 노출 당 단가 (Cost Per Mille)
- `D`: 데이터 API 호출 수 (API Calls)
- `DP`: 호출 당 단가 (Price Per Call)

**공식 (Formula)**:
> **Platform Revenue = (I / 1000 * CPM) + (D * DP)**

---

### 🧮 3개년 통합 수익 모델 (Excel Structure Example)

| 구분 (Category) | Year 1 (Seed) | Year 2 (Growth) | Year 3 (Scale) | 비고 |
|---|---|---|---|---|
| **MAU (방문자)** | 10,000 | 50,000 | 200,000 | |
| **중개 수수료** | **1.8억** (1.5%) | **15억** (8%) | **85억** (40%) | C3: 1.0% -> 2.0% |
| **구독 매출** | **0.2억** | **5억** (200개소) | **30억** (1000개소) | 파트너 확대 |
| **데이터/광고** | - | **2억** | **15억** | API 판매 개시 |
| **총 매출 (Total)** | **2.0억** | **22억** | **130억** | Series A/B 규모 |
| **영업이익 (OP)** | **0.5억** (25%) | **11억** (50%) | **85억** (65%) | 고수익 구조 |

**[Key Driver]**
- Year 1: **직접 중개** 중심 (Product Market Fit 검증)
- Year 2: **파트너 확장** (AI 리드 스코어링 도입)
- Year 3: **데이터 플랫폼화** (전국 확대 및 금융권 연동)

---

### 📝 (참고) 엑셀 함수 예시

**`Core_Revenue` 계산 셀 (D5)**:
`=PRODUCT(B5, C5, D5, E5, F5, G5)`
*(B5: 방문자, C5: 상세전환, D5: 상담전환, E5: 계약전환, F5: 평균거래가, G5: 수수료율)*

**`Sensitivity_Table` (민감도 분석)**:
데이터 표(Data Table) 기능을 활용하여, **계약 전환율(1.0~3.0%)** 변화에 따른 **총 매출** 자동 산출.
