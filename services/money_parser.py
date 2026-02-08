import re
from typing import Optional, Tuple, Dict

_EOK = 100_000_000
_CHEON = 10_000_000
_MAN = 10_000

def parse_korean_money(text: str) -> Optional[int]:
    """
    '18억', '12억5천', '3억 2천', '9000만', '1억2000만' 등을 원 단위 int로 변환.
    실패 시 None.
    """
    if text is None: return None
    s = text.replace(" ", "").replace(",", "")
    if not s:
        return None

    # 5000/200 같은 케이스는 여기서 제외 (별도 함수)
    if "/" in s:
        return None

    total = 0

    # 억
    m = re.search(r"(\d+)\s*억", s)
    if m:
        total += int(m.group(1)) * _EOK
        s = re.sub(r"\d+\s*억", "", s)

    # 천(=천만원 단위로 쓰는 경우가 많아 '5천'을 5*1천만원 처리)
    m = re.search(r"(\d+)\s*천", s)
    if m:
        total += int(m.group(1)) * _CHEON
        s = re.sub(r"\d+\s*천", "", s)

    # 만
    m = re.search(r"(\d+)\s*만", s)
    if m:
        total += int(m.group(1)) * _MAN
        s = re.sub(r"\d+\s*만", "", s)

    # 남은 숫자(예: '2,500'처럼 만/천 표기 없이 남는 경우) → 원으로 간주
    leftover = re.sub(r"[^\d]", "", s)
    if leftover:
        try:
            total += int(leftover)
        except ValueError:
            pass

    return total if total > 0 else None


def parse_deposit_monthly(text: str) -> Optional[Tuple[int, int]]:
    """
    '500/200', '보증금 5000 / 월 200' 같은 문자열에서 (보증금, 월세)를 만원 기준으로 파싱 후 원단위로 반환.
    """
    if text is None: return None
    s = text.replace(" ", "").replace(",", "")
    m = re.search(r"(\d+)\s*/\s*(\d+)", s)
    if not m:
        return None
    deposit_mw = int(m.group(1))
    monthly_mw = int(m.group(2))
    return deposit_mw * _MAN, monthly_mw * _MAN


def normalize_prices_from_text(text: str) -> Dict[str, Optional[int]]:
    """
    문장에서 매매/전세/월세 패턴을 대충 잡아 정규화 값 추출(원 단위).
    """
    s = text

    # 월세 500/200
    rent = parse_deposit_monthly(s)
    deposit_won = monthly_won = None
    if rent:
        deposit_won, monthly_won = rent

    # 매매/전세 금액 후보들
    sale_won = None
    jeonse_won = None

    sale_m = re.search(r"(매매|매매가|매도가)\s*([0-9억천만,\s]+)", s)
    if sale_m:
        sale_won = parse_korean_money(sale_m.group(2))

    jeonse_m = re.search(r"(전세|전세가)\s*([0-9억천만,\s]+)", s)
    if jeonse_m:
        jeonse_won = parse_korean_money(jeonse_m.group(2))

    # 금액 단독 등장(‘18억’만 있는 경우) → sale 후보로 fallback
    if sale_won is None:
        any_price = re.search(r"(\d+\s*억(\s*\d+\s*천)?(\s*\d+\s*만)?)", s)
        if any_price:
            sale_won = parse_korean_money(any_price.group(1))

    return {
        "sale_won": sale_won,
        "jeonse_won": jeonse_won,
        "deposit_won": deposit_won,
        "monthly_won": monthly_won,
    }
