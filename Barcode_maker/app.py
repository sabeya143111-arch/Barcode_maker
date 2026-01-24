import streamlit as st
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.colors import black, HexColor
from reportlab.lib.utils import ImageReader
import io
import barcode
from barcode.writer import ImageWriter
from urllib.request import urlopen

# ================= LOGO =================
BASE_DIR = Path(__file__).resolve().parent
LOCAL_LOGO_PATH = BASE_DIR / "assets" / "logo.png"

GITHUB_LOGO_URL = "https://raw.githubusercontent.com/sabeya143111-arch/Barcode_maker/main/Barcode_maker/assets/logo.png"

_logo = None

def load_logo():
    global _logo
    if _logo:
        return _logo

    if LOCAL_LOGO_PATH.exists():
        img = Image.open(LOCAL_LOGO_PATH).convert("RGBA")
    else:
        data = urlopen(GITHUB_LOGO_URL).read()
        img = Image.open(io.BytesIO(data)).convert("RGBA")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    _logo = ImageReader(buf)
    return _logo


# ================= STREAMLIT =================
st.set_page_config("Warehouse Label", "🏷️", layout="wide")
st.title("🏷️ Warehouse Location Label")

code = st.text_input("Location Code", "W13-07-07-01-02")
btn = st.button("⬇️ Generate PDF")


# ================= PDF =================
def make_pdf():
    logo = load_logo()

    # Barcode
    bbuf = io.BytesIO()
    barcode.get("code128", code, writer=ImageWriter()).render({
        "write_text": False,
        "dpi": 600,
        "module_height": 22,
        "module_width": 0.45,
    }).save(bbuf, format="PNG")
    bbuf.seek(0)
    bar = ImageReader(bbuf)

    # Canvas size (exact label style)
    W, H = 210 * mm, 60 * mm
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(W, H))
    m = 4 * mm

    # ================= LEFT ARROW BOX =================
    left_w = W * 0.26
    box_h = H - 2 * m

    c.setLineWidth(1.5)
    c.roundRect(m, m, left_w, box_h, 4 * mm)

    c.setFillColor(HexColor("#E6E6E6"))
    c.roundRect(m + 1, m + 1, left_w - 2, box_h - 2, 4 * mm, stroke=0, fill=1)

    # Arrow
    cx = m + left_w / 2
    stem_w = 20 * mm
    stem_h = 28 * mm

    stem_y = m + 10 * mm
    head_top = m + box_h - 8 * mm

    c.setFillColor(black)

    c.rect(cx - stem_w / 2, stem_y, stem_w, stem_h, stroke=0, fill=1)

    p = c.beginPath()
    p.moveTo(cx - 35 * mm, stem_y + stem_h)
    p.lineTo(cx + 35 * mm, stem_y + stem_h)
    p.lineTo(cx, head_top)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # ================= RIGHT BOX =================
    rx = m + left_w + 2 * mm
    rw = W - rx - m

    c.roundRect(rx, m, rw, box_h, 4 * mm)

    # Barcode
    c.drawImage(
        bar,
        rx + 6 * mm,
        m + box_h * 0.55,
        width=rw - 12 * mm,
        height=box_h * 0.35,
        mask="auto",
    )

    # Separator line
    sep_y = m + box_h * 0.48
    c.setLineWidth(2.2)
    c.line(rx + 6 * mm, sep_y, rx + rw - 6 * mm, sep_y)

    # ================= BOTTOM =================
    band_y = m + 6 * mm
    band_h = sep_y - band_y - 3 * mm

    # Logo
    logo_size = 20 * mm
    c.drawImage(
        logo,
        rx + 10 * mm,
        band_y + (band_h - logo_size) / 2,
        logo_size,
        logo_size,
        mask="auto",
    )

    # Text
    c.setFont("Helvetica-Bold", 38)
    c.drawString(
        rx + 10 * mm + logo_size + 6 * mm,
        band_y + band_h / 2 - 12,
        code,
    )

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()


# ================= OUTPUT =================
if btn:
    pdf = make_pdf()
    st.download_button(
        "⬇️ Download PDF",
        pdf,
        f"{code}.pdf",
        "application/pdf",
    )
