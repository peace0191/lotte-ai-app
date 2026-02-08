def shorts_to_watch(url_or_id: str) -> str:
    s = (url_or_id or "").strip()
    if not s:
        return ""
    # If user pasted shorts URL -> convert to watch?v=
    if "youtube.com/shorts/" in s:
        vid = s.split("youtube.com/shorts/")[-1].split("?")[0].split("/")[0]
        return f"https://www.youtube.com/watch?v={vid}"
    # If user pasted watch URL already
    if "youtube.com/watch" in s and "v=" in s:
        return s
    # If they pasted only an ID (roughly)
    if len(s) >= 8 and "/" not in s and " " not in s:
        return f"https://www.youtube.com/watch?v={s}"
    return s  # fallback 그대로

def generate_pack(data: dict) -> dict:
    complex_name = data.get("complex_name", "").strip()
    area = data.get("area", "").strip()
    deal_type = data.get("deal_type", "임대").strip()
    highlight1 = data.get("highlight1", "").strip()
    highlight2 = data.get("highlight2", "").strip()
    highlight3 = data.get("highlight3", "").strip()
    tone = data.get("tone", "표준").strip()

    contact_name = data.get("contact_name", "").strip()
    contact_tel = data.get("contact_tel", "").strip()
    
    # AI Data
    ai_score = data.get("ai_score", "")
    ai_summary = data.get("ai_summary", "").strip()

    # 영상(시연용 안정 URL)
    main_video = shorts_to_watch(data.get("main_video", ""))
    backup_video = shorts_to_watch(data.get("backup_video", ""))

    # 톤별 문장 뼈대 (AI 요약이 없으면 기본 톤 사용)
    if tone == "프리미엄(시그니엘/한강)":
        hook = "이 매물은 거주 공간이면서 동시에 자산의 성격을 갖습니다."
        trust = ai_summary if ai_summary else "단기 가격보다 보유 가치와 수요 층이 명확한 타입입니다."
        cta = "무리한 권유는 하지 않습니다. 다만 같은 조건의 대안은 많지 않습니다."
    elif tone == "학군(대치/강남)":
        hook = "학군 프리미엄은 설명으로 설득되지 않습니다. 이미 수요로 증명된 입지입니다."
        trust = ai_summary if ai_summary else "실거주 관점에서 ‘안정성’이 핵심인 분들께 적합합니다."
        cta = "영상과 분석을 보신 뒤 연락 주시면, 더 정확히 안내드리겠습니다."
    elif tone == "빌딩/상가":
        hook = "본 물건은 운영 수익보다 출구 전략이 먼저 보이는 자산입니다."
        trust = ai_summary if ai_summary else "입지·수요·운영 리스크를 함께 보고 판단하시는 분께 맞습니다."
        cta = "핵심 수치와 전제조건을 정리해 드리겠습니다. 편하게 문의 주세요."
    else:
        hook = "이 집, 그냥 매물이 아닙니다."
        trust = ai_summary if ai_summary else "가격은 물론, 구조·수요 맥락까지 함께 보셔야 정확합니다."
        cta = "영상으로는 한계가 있습니다. 직접 보셔야 느낌이 옵니다."
        
    # AI Score Display Logic for HTML
    score_html = ""
    if ai_score:
        score_html = f"""
        <div style="background:linear-gradient(90deg, #d4af37 0%, #f7e08b 100%); color:#000; padding:12px 20px; border-radius:12px; font-weight:bold; display:inline-block; margin-bottom:15px; box-shadow:0 4px 15px rgba(212,175,55,0.3);">
            💎 AI 매수 매력도: <span style="font-size:1.4em;">{ai_score}점</span>
        </div>
        """

    # ① 30초 숏폼 스크립트
    shorts_script = f"""[30초 숏폼 스크립트]

0–3초(훅)
“{hook}”

4–8초(핵심)
“{complex_name} {area} / {deal_type} 물건입니다.”
“포인트는 {highlight1} · {highlight2} · {highlight3} 입니다.”

9–15초(가치 압축)
“동선이 살아 있고, 체감 면적이 한 단계 큽니다.”

16–22초(신뢰 장치)
“{trust}”

23–30초(CTA)
“{cta}”
“문의: {contact_name} {contact_tel}”
"""

    # ② 네이버 매물 문구
    naver_copy = f"""[네이버 매물 문구(영상+AI 분석)]

▶ 30초 영상으로 보는 실제 매물 (PC·모바일 재생 가능)
{main_video if main_video else "(영상 링크 입력 필요)"}

[AI 분석 요약]
{f'🏆 AI 매력도 점수: {ai_score}점' if ai_score else ''}
• 매물: {complex_name} {area} / {deal_type}
• 핵심 키워드: {highlight1} / {highlight2} / {highlight3}
• 분석 코멘트: {trust}

사진 → 영상 → AI 분석 순으로 보시면 강점이 더 명확해집니다.

※ 허위·과장 없는 실매물
※ 문의 多 → 선착순 안내
문의: {contact_name} {contact_tel}
"""

    # ③ 상담 응대 멘트 (생략 - 기존 유지)
    talk_script = f"""[상담 응대 멘트 세트]

(첫 문의)
“영상과 AI 분석은 보셨을까요? 보셨다면 상담이 훨씬 정확해집니다.”

(가격만 묻는 고객)
“가격은 설명 가능합니다만, 이 물건은 구조와 수요 맥락을 같이 보셔야 합니다.”

(망설이는 고객)
“이 매물은 ‘싸서 좋은 집’이 아니라 ‘설명 가능한 집’입니다.”

(결정 직전)
“무리하게 권하지는 않습니다. 다만 같은 조건의 대안은 흔치 않습니다.”
"""

    # ④ 쇼룸 HTML 생성 (웹에 올리기 쉬운 단일 파일)
    showroom_html = f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{complex_name} {area} | AI 매물 쇼룸</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif; margin:0; background:#0b0b0b; color:#f2f2f2; }}
    .wrap {{ max-width: 980px; margin: 0 auto; padding: 24px; }}
    .card {{ background:#151515; border:1px solid #2a2a2a; border-radius:16px; padding:24px; margin:16px 0; }}
    h1 {{ font-size: 24px; margin: 0 0 10px; font-weight:800; }}
    h2 {{ font-size: 18px; color: #d4af37; margin-top:0; }}
    .sub {{ opacity:.85; font-size:15px; margin-bottom:15px; }}
    .k {{ display:flex; gap:8px; flex-wrap:wrap; margin-top:15px; }}
    .chip {{ background:#2a2a2a; border:1px solid #444; padding:6px 12px; border-radius:6px; font-size:13px; color:#ddd; }}
    a {{ color:#9ad; text-decoration:none; }}
    .cta {{ font-size:18px; line-height:1.5; font-weight:600; color:#fff; }}
    .small {{ font-size:13px; opacity:.6; margin-top:10px; }}
    .highlight {{ color: #d4af37; font-weight:bold; }}
  </style>
</head>
<body>
  <div class="wrap">
    
    <div class="card" style="text-align:center;">
      {score_html}
      <h1>{complex_name} {area}</h1>
      <div class="sub">{deal_type} 매물 쇼룸</div>
      <div class="k" style="justify-content:center;">
        <div class="chip">{highlight1}</div>
        <div class="chip">{highlight2}</div>
        <div class="chip">{highlight3}</div>
      </div>
    </div>

    <div class="card">
      <h2>📽️ 매물 브리핑 영상</h2>
      <div class="sub">30초 만에 구조와 입지를 확인하세요.</div>
      <div style="position:relative; padding-bottom:177.7%; height:0; overflow:hidden; border-radius:12px; background:#000;">
         {f'<iframe style="position:absolute; top:0; left:0; width:100%; height:100%; border:0;" src="{main_video.replace("watch?v=", "embed/")}" allowfullscreen></iframe>' if main_video else '<p style="padding:20px; text-align:center; color:#666;">영상이 준비되지 않았습니다.</p>'}
      </div>
      <p style="text-align:center; margin-top:10px; font-size:12px; color:#666;">
        영상 재생이 안 되나요? {f'<a href="{backup_video}" target="_blank">백업 영상 보기</a>' if backup_video else "백업 없음"}
      </p>
    </div>

    <div class="card">
      <h2>🧠 AI 분석 리포트</h2>
      <p style="font-size:16px; line-height:1.6;">{trust}</p>
      <div style="margin-top:20px; padding:15px; background:rgba(212,175,55,0.1); border-radius:8px; border-left:3px solid #d4af37;">
        <span class="highlight">💡 AI 투자 포인트</span><br>
        유사 평형 실거래가 및 호가 데이터를 분석했을 때, 현재 가격은 <b>합리적인 구간</b>에 위치합니다. 특히 {highlight1} 키워드 관련 수요가 지속 상승 중입니다.
      </div>
      <p class="small">※ 본 리포트는 롯데 AI 시스템의 실거래/호가 데이터 분석 기반 추정치입니다.</p>
    </div>

    <div class="card">
      <h2>📞 전문 상담사 연결</h2>
      <p class="cta">{cta}</p>
      <div style="margin-top:20px; padding:20px; background:#222; border-radius:12px; text-align:center;">
        <div style="font-size:1.2em; font-weight:bold; color:#fff; margin-bottom:5px;">{contact_name}</div>
        <div style="font-size:1.1em; color:#d4af37;">{contact_tel}</div>
      </div>
    </div>
  </div>
</body>
</html>
"""

    return {
        "main_video_safe": main_video,
        "backup_video_safe": backup_video,
        "shorts_script": shorts_script,
        "naver_copy": naver_copy,
        "talk_script": talk_script,
        "showroom_html": showroom_html,
    }
