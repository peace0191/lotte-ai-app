import urllib.parse
import streamlit as st

APP_URL = "https://lotte-ai-app.streamlit.app"

def _clean(s: str) -> str:
    return (s or "").strip()

def build_app_link(property_id: str | None = None):
    # If deep linking is needed later, modify here.
    if property_id:
        # Example deep link format
        return f"{APP_URL}/?property_id={urllib.parse.quote(property_id)}"
    return APP_URL

def build_deeplink(property_id: str | None = None, campaign: str = "shorts_auto"):
    base = APP_URL
    params = {}
    if property_id:
        params["property_id"] = property_id
    # Marketing params
    params.update({
        "utm_source": "share",
        "utm_medium": "organic",
        "utm_campaign": campaign
    })
    q = urllib.parse.urlencode(params)
    return f"{base}/?{q}" if q else base

def generate_long_text(title: str, price: str, highlight: str, property_id: str | None = None):
    link = build_app_link(property_id)
    return f"""📍 {_clean(title)}
💰 {_clean(price)}

✨ {_clean(highlight)}

🏫 대치1동 교육특구 AI 추천 매물
👉 자세히 보기: {link}

#대치1동 #대치동아파트 #학군특구 #AI저평가매물 #부동산AI
""".strip()

def generate_short_text(title: str, price: str, property_id: str | None = None):
    link = build_app_link(property_id)
    return f"""📍 {_clean(title)} | 💰 {_clean(price)}
👉 {link}""".strip()

def generate_momcafe_text(title: str, highlight: str, property_id: str | None = None):
    link = build_app_link(property_id)
    return f"""[대치1동 학군수요 맞춤 매물]
- {_clean(title)}
- 포인트: {_clean(highlight)}

AI가 저평가/학군/입주시기 기준으로 추천하고,
바로 상담·예약까지 연결됩니다.
👉 {link}""".strip()

def generate_naver_html(title: str, price: str, highlight: str, phone: str, company: str, regno: str, property_id: str | None = None):
    link = build_app_link(property_id)
    # Simple HTML for Naver Blog/Cafe
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>{_clean(title)}</title>
</head>
<body style="font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;line-height:1.5;">
  <div style="max-width:720px;margin:0 auto;padding:16px;">
    <h2 style="margin:0 0 6px 0;">📍 {_clean(title)}</h2>
    <p style="margin:0 0 10px 0;"><b>💰 {_clean(price)}</b></p>

    <div style="padding:12px;border:1px solid #e5e7eb;border-radius:12px;background:#fafafa;">
      <b>✨ 핵심 포인트</b>
      <p style="margin:8px 0 0 0;">{_clean(highlight)}</p>
    </div>

    <div style="margin-top:14px;padding:12px;border:1px solid #e5e7eb;border-radius:12px;">
      <b>🏫 대치1동 교육특구 AI 매물 시스템</b>
      <ul style="margin:8px 0 0 18px;padding:0;">
        <li>대치1동 학군/입지 특성 기반 매물 이해</li>
        <li>AI 저평가 매물 추천 → 상담/예약 → 계약 매칭</li>
        <li>숏츠·SNS 자동 홍보로 전환률 강화</li>
      </ul>
      <p style="margin:10px 0 0 0;">
        👉 <a href="{link}" target="_blank" rel="noreferrer">{link}</a>
      </p>
    </div>

    <div style="margin-top:14px;padding:12px;border:1px solid #e5e7eb;border-radius:12px;">
      <b>📞 상담/예약</b>
      <p style="margin:8px 0 0 0;">{phone}</p>
      <p style="margin:6px 0 0 0;color:#6b7280;font-size:13px;">
        {company} | 등록번호 {regno}
      </p>
    </div>
  </div>
</body>
</html>
""".strip()

def kakao_share_link(text: str):
    # Kakao share via copy/clip logic often preferred, but here is link builder
    encoded = urllib.parse.quote(text)
    return f"https://share.kakao.com/?text={encoded}"

def naver_copy_set_1(title: str, price: str, highlight: str, property_id: str | None = None):
    link = build_deeplink(property_id, "naver_set1")
    return f"""[대치1동 교육특구 추천]
📍 {title}
💰 {price}

✨ {highlight}

👉 매물 상세로 이동: {link}
""".strip()
