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

GITHUB_LOGO_URL = (
    "https://raw.githubusercontent.com/"
    "sabeya143111-arch/Barcode_maker/main/Barcode_maker/assets/logo.png"
)

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
        "module_height": 18,
        "module_width": 0.42,
    }).save(bbuf, format="PNG")
    bbuf.seek(0)
    bar = ImageReader(bbuf)

    # Canvas
    W, H = 210 * mm, 60 * mm
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(W, H))
    m = 4 * mm

    # ================= LEFT ARROW BOX =================
    left_w = W * 0.27
    box_h = H - 2 * m

    c.setLineWidth(1.3)
    c.roundRect(m, m, left_w, box_h, 3 * mm)

    c.setFillColor(HexColor("#E3E3E3"))
    c.roundRect(m + 1, m + 1, left_w - 2, box_h - 2, 3 * mm, stroke=0, fill=1)

    # ---- ARROW (EXACT LOOK) ----
    cx = m + left_w / 2
    stem_w = 18 * mm
    stem_h = 30 * mm

    stem_y = m + 8 * mm
    head_top = m + box_h - 8 * mm

    c.setFillColor(black)

    # stem
    c.rect(cx - stem_w / 2, stem_y, stem_w, stem_h, stroke=0, fill=1)

    # head
    p = c.beginPath()
    p.moveTo(cx - 36 * mm, stem_y + stem_h)
    p.lineTo(cx + 36 * mm, stem_y + stem_h)
    p.lineTo(cx, head_top)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # ================= RIGHT BOX =================
    rx = m + left_w + 2 * mm
    rw = W - rx - m

    c.roundRect(rx, m, rw, box_h, 3 * mm)

    # Barcode (top)
    c.drawImage(
        bar,
        rx + 6 * mm,
        m + box_h * 0.53,
        width=rw - 12 * mm,
        height=box_h * 0.37,
        mask="auto",
    )

    # underline
    sep_y = m + box_h * 0.47
    c.setLineWidth(2)
    c.line(rx + 6 * mm, sep_y, rx + rw - 6 * mm, sep_y)

    # ================= BOTTOM =================
    band_y = m + 6 * mm
    band_h = sep_y - band_y - 3 * mm

    # Logo (BIG ROUND LIKE PHOTO)
    logo_size = 18 * mm
    c.drawImage(
        logo,
        rx + 10 * mm,
        band_y + (band_h - logo_size) / 2,
        logo_size,
        logo_size,
        mask="auto",
    )

    # Text
    c.setFont("Helvetica-Bold", 40)
    c.drawString(
        rx + 10 * mm + logo_size + 6 * mm,
        band_y + band_h / 2 - 13,
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
