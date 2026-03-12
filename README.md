# 환승 예금(Hwanseung-Yegeum)

## 📝 프로젝트 소개
"지금 예금을 깨고 저 예금으로 갈아타는 게 이득일까?"
**환승 예금**는 사용자가 기존 예금을 중도 해지하고 새로운 예금 상품으로 갈아탈 때의 유불리를 비교 분석해 주는 **금융 시뮬레이션 웹 서비스**입니다. 이를 통해 직관적이고 합리적인 금융 의사결정을 돕습니다.

---

## 🚀 주요 기능 (Key Features)

### 🖥️ Frontend (User Interface)


### ⚙️ Backend (Calculation Engine)
* **신규 가입 시뮬레이션:** 기존 원금 + 중도해지 이자를 재투자했을 때의 예상 만기 수령액 계산.
* **금리 스트레스 테스트:** 기준 금리 변동 시나리오(유지, +0.25%p, -0.25%p)에 따른 수익 비교 분석.
* **금융권 표준 오차 방지 로직:** 부동소수점 오차 제어 및 은행 실무 기준의 세금/이자 절사(Truncation) 적용.

---

## 🛠️ 기술 스택 (Tech Stack)

### Frontend

### Backend
* Language: Python 3
* Framework: Django, Django REST Framework (DRF)

---

## 💡 기술적 주안점 (Technical Highlights)

이 프로젝트는 금융 서비스의 생명인 **'계산의 무결성(Integrity)'**을 보장하기 위해 백엔드에 다음과 같은 핵심 로직을 설계했습니다.

1. **부동소수점(Float) 오차 원천 차단**
   * Python의 기본 `float` 연산 시 발생하는 이진법 근사치 오류를 막기 위해, 금액 및 이율 등 모든 실수 연산에 `Decimal` 객체를 도입했습니다.
   * 외부 데이터 파싱 시 `Decimal(str(value))` 형태로 변환하여 미세한 소수점 유입을 방지했습니다.

2. **은행 실무 수준의 단수 처리 (Quantize & Rounding)**
   * 단순 `round()` 함수 대신 `Decimal.quantize()`를 활용했습니다.
   * 세전 이자와 세금(15.4%) 계산 시 실무 은행과 동일하게 **원 단위 미만 절사(`ROUND_FLOOR`)** 규칙을 일관되게 적용하여 1원의 오차까지 제어합니다.

3. **안전한 날짜(Date) 연산 및 윤년 처리**
   * `datetime` 객체의 `timedelta`를 직접 연산하지 않고, `.days`를 통해 순수 정수(Integer)로 추출한 뒤 `Decimal`로 형변환하여 안전하게 일할(Days) 계산을 수행합니다.
   * 가입 연도의 윤년(`calendar.isleap`) 여부를 판별하여 1년의 기준 일수(365일/366일)를 동적으로 할당합니다.

---

## 🔗 API 명세 및 연동 가이드 (For Frontend)

### `POST` `/api/calculator/`
예금 환승 시나리오 결과를 반환합니다.

**Request Body (JSON):**
```json
{
  "today": "2026-03-12",
  "committed_amount": 1000000,
  "original_start_date": "2025-01-01",
  "original_end_date": "2026-01-01",
  "original_interest_rate": 3.6,
  "original_stop_rate": 1.5,
  "new_end_date": "2027-03-12",
  "new_interest_rate": 4.0,
  "user_early_interest": null 
}
```