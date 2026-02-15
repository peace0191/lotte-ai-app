from io import BytesIO
import qrcode

def make_qr_png_bytes(url: str) -> bytes:
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
