# services/compare_pdf.py
from __future__ import annotations
import os
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

WATERMARK = "롯데타워앤강남빌딩부동산중개 (주) 02-578-8285"

# --- Font Registration Logic ---
FONT_NAME = "MyKoreanFont"
FONT_PATH_CANDIDATES = [
    r"C:\Windows\Fonts\malgun.ttf",      # Windows 10/11 Default
    r"C:\Windows\Fonts\gulim.ttc",       # Legacy Windows
    r"C:\Windows\Fonts\batang.ttc",
    r"/usr/share/fonts/truetype/nanum/NanumGothic.ttf", # Linux
]

font_registered = False
for fpath in FONT_PATH_CANDIDATES:
    if os.path.exists(fpath):
        try:
            pdfmetrics.registerFont(TTFont(FONT_NAME, fpath))
            font_registered = True
            break
        except Exception:
            continue

if not font_registered:
    # Fallback if no Korean font found
    FONT_NAME = "Helvetica"
    FONT_BOLD = "Helvetica-Bold" # Not really used in logic below but kept for consistency
    FONT_REGULAR = "Helvetica"
else:
    # Use same font for everything if custom font (Malgun)
    FONT_BOLD = FONT_NAME 
    FONT_REGULAR = FONT_NAME

def build_compare_pdf(
    *,
    title: str,
    persona: str,
    rows: list[dict],     # score_region 결과들
    highlight_region: str = "대치1동",
) -> bytes:
    """
    1페이지 비교 PDF (A4)
    rows: [{region, score, grade, profile, weights, season_bonus}, ...]
    """
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    # Header
    c.setFont(FONT_BOLD, 16)
    c.drawString(40, h-55, title)

    c.setFont(FONT_REGULAR, 10)
    c.drawRightString(w-40, h-55, datetime.now().strftime("%Y-%m-%d"))
    c.setFillColor(colors.black)
    c.setFont(FONT_REGULAR, 11)
    # persona, region might contain Korean
    c.drawString(40, h-78, f"관점: {persona}  |  비교: {', '.join([r['region'] for r in rows])}")

    # Badge
    top = sorted(rows, key=lambda x: x["score"], reverse=True)[0]
    badge = f"TOP: {top['region']}  {top['grade']}  ({top['score']})"
    c.setFillColorRGB(0.83, 0.69, 0.22)
    c.roundRect(40, h-108, 260, 22, 8, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont(FONT_BOLD, 10)
    c.drawString(50, h-102, badge)

    # Divider
    c.setFillColor(colors.black)
    c.line(40, h-122, w-40, h-122)

    y = h-150

    # Table header
    c.setFont(FONT_BOLD, 11)
    c.drawString(40, y, "지역")
    c.drawString(160, y, "AI 점수")
    c.drawString(240, y, "등급")
    c.drawString(310, y, "핵심 코멘트")
    y -= 18

    c.setFont(FONT_REGULAR, 10)
    for r in rows:
        region = r["region"]
        score = r["score"]
        grade = r["grade"]
        sb = r.get("season_bonus", 0.0)
        profile = r["profile"]

        if region == highlight_region:
            c.setFillColorRGB(0.95, 0.95, 0.95)
            c.roundRect(38, y-4, w-76, 18, 4, stroke=0, fill=1)
            c.setFillColor(colors.black)

        c.drawString(40, y, region)
        c.drawString(160, y, f"{score}")
        c.drawString(240, y, grade)

        # 코멘트(짧게)
        prof = r["profile"] 
        # Convert floats to int safely
        sc = int(prof.get('school', 0))
        le = int(prof.get('lease', 0))
        de = int(prof.get('defense', 0))
        
        comment = ""
        # Try to fit standard comment
        # Note: if comment is too long, drawString might clip.
        base_cmt = f"학군 {sc}/임대 {le}/방어 {de}"
        
        season_cmt = ""
        if sb and region == "대치1동":
            season_cmt = f" (+시즌 {int(sb)}p)"
            
        final_cmt = base_cmt + season_cmt
        c.drawString(310, y, final_cmt)

        y -= 22

    y -= 6
    c.line(40, y, w-40, y)
    y -= 18

    # Explanation block
    c.setFont(FONT_BOLD, 11)
    c.drawString(40, y, "AI 해설")
    y -= 16
    c.setFont(FONT_REGULAR, 10)
    explain = [
        f"- {persona} 관점 가중치로 종합 점수를 산출했습니다.",
        f"- 대치1동은 2~3월/12~1월에 학군 시즌 프리미엄이 자동 반영됩니다.",
        f"- 본 리포트는 상담용 1페이지 요약본이며, 상세 매물 제안서는 별도 생성 가능합니다.",
    ]
    for line in explain:
        c.drawString(40, y, line)
        y -= 14

    # Watermark
    c.setFont(FONT_REGULAR, 9)
    c.setFillGray(0.6)
    c.drawRightString(w-40, 30, WATERMARK)

    c.showPage()
    c.save()
    return buf.getvalue()
