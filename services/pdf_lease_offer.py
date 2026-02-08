# services/pdf_lease_offer.py
from __future__ import annotations
import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from io import BytesIO

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
    FONT_BOLD = "Helvetica-Bold"
else:
    FONT_BOLD = FONT_NAME # Use same font for bold if single TTF, or register bold separately if available. 
    # Malgun doesn't have separate Bold file usually, machine synthesis works or just use same.
    # Actually reportlab doesn't synthesize bold for TTFont automatically unless registered.
    # We will just use the regular font for everything to ensure characters show up.

def build_lease_offer_pdf(
    *,
    out_path: str,
    title: str,
    subtitle: str,
    badge: str,
    jeonse_text: str,
    wolse_text: str,
    landlord_pitch: str,
    consult_script: str,
    shorts_script: str,
    summary_text: str = "",
    map_png_bytes: bytes | None = None
) -> str:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(out), pagesize=A4)
    w, h = A4

    def block(label: str, body: str, y0: float) -> float:
        if font_registered: c.setFont(FONT_NAME, 11)
        else: c.setFont("Helvetica-Bold", 11)
        c.drawString(18*mm, y0, label)
        y0 -= 6*mm
        
        if font_registered: c.setFont(FONT_NAME, 10.5)
        else: c.setFont("Helvetica", 10.5)
        
        text = c.beginText(18*mm, y0)
        # Handle line breaks explicitly if needed, but reportlab text object handles newline char \n ? No, need textLine
        if font_registered: text.setFont(FONT_NAME, 10.5)
        
        for line in (body or "").split("\n"):
            # Replace literal \n chars if data has them
            line = line.replace("\\n", "\n") 
            # If line has internal newlines
            for subline in line.split("\n"):
                 text.textLine(subline)
                 
        c.drawText(text)
        
        # Calculate height roughly
        line_count = 0
        for line in (body or "").split("\n"):
            line = line.replace("\\n", "\n")
            line_count += len(line.split("\n"))
            
        y0 -= max(18*mm, (line_count+1) * 5*mm)
        return y0

    # Use registered font
    c.setFont(FONT_NAME, 18) if font_registered else c.setFont("Helvetica-Bold", 18)
    
    # Header
    # If font registered, use it. Else broken text is inevitable for Korean.
    if font_registered:
        c.setFont(FONT_NAME, 18)
    else:
        c.setFont("Helvetica-Bold", 18)
        
    c.drawString(18*mm, h-22*mm, title)

    if font_registered: c.setFont(FONT_NAME, 11)
    else: c.setFont("Helvetica", 11)
    c.drawString(18*mm, h-30*mm, subtitle)
    
    y = h-45*mm
    # Insert Summary Block
    if summary_text:
        y = block("SSS 학군 요약", summary_text, y)

    # Badge
    if font_registered: c.setFont(FONT_NAME, 12)
    else: c.setFont("Helvetica-Bold", 12)
    c.drawString(18*mm, h-40*mm, f"🏅 {badge}")

    # Force y gap
    y -= 5*mm
    
    if font_registered: c.setFont(FONT_NAME, 12)
    else: c.setFont("Helvetica-Bold", 12)
    c.drawString(18*mm, y, "전·월세 추천 조건(자동)")
    y -= 7*mm
    
    if font_registered: c.setFont(FONT_NAME, 11)
    else: c.setFont("Helvetica", 11)
    c.drawString(18*mm, y, f"전세: {jeonse_text}")
    y -= 6*mm
    c.drawString(18*mm, y, f"월세: {wolse_text}")
    y -= 10*mm

    y = block("① 임대인 설득용 멘트(전·월세 제안)", landlord_pitch, y)
    y = block("② 30초 상담 멘트(중개사 낭독용)", consult_script, y)
    y = block("③ 대치1동 전용 숏폼 30초 스크립트", shorts_script, y)

    # Footer watermark
    if font_registered: c.setFont(FONT_NAME, 11)
    else: c.setFont("Helvetica-Bold", 11)
    c.drawString(18*mm, 16*mm, WATERMARK)
    
    # --- Page 2: Map (if provided) ---
    if map_png_bytes:
        c.showPage()
        
        # Header
        if font_registered: c.setFont(FONT_NAME, 16)
        else: c.setFont("Helvetica-Bold", 16)
        c.drawString(18*mm, h-22*mm, "부록: 대치1동 학군/단지 정밀 지도")
        
        # Map Image
        try:
            # Use ImageReader for better PNG support
            img = ImageReader(BytesIO(map_png_bytes))
            # Draw per user spec
            c.drawImage(img, x=18*mm, y=120*mm, width=174*mm, height=70*mm, preserveAspectRatio=True, mask='auto')
            
            # Caption
            if font_registered: c.setFont(FONT_NAME, 9)
            else: c.setFont("Helvetica", 9)
            c.drawString(18*mm, 116*mm, "대치1동 학군 지도(정확 주소 기반 좌표 변환) + 컬러 범례")
            
        except Exception:
            pass
            
        # Footer
        if font_registered: c.setFont(FONT_NAME, 11)
        else: c.setFont("Helvetica-Bold", 11)
        c.drawString(18*mm, 16*mm, WATERMARK)
    
    c.showPage()
    c.save()
    return str(out)
