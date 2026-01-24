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

# ================= PATHS =================
BASE_DIR = Path(__file__).resolve().parent
LOCAL_LOGO_PATH = BASE_DIR / "assets" / "logo.png"

GITHUB_LOGO_URL = (
    "https://raw.githubusercontent.com/"
    "sabeya143111-arch/Barcode_maker/main/Barcode_maker/assets/logo.png"
)

_logo_cache = {}

def load_logo():
    if "ir" in _logo_cache:
        return _logo_cache["img"], _logo_cache["ir"]

    try:
        if LOCAL_LOGO_PATH.exists():
            img = Image.open(LOCAL_LOGO_PATH).convert("RGBA")
        else:
            data = urlopen(GITHUB_LOGO_URL).read()
            img = Image.open(io.BytesIO(data)).convert("RGBA")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        ir = ImageReader(buf)
        _logo_cache["img"], _logo_cache["ir"] = img, ir
        return img, ir
    except:
        return None, None


# ================= STREAMLIT =================
st.set_page_config("Swag Label Maker", "🏷️", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background:#020617; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏷️ Swag Warehouse Label Maker")

barcode_text = st.text_input("Location Code", "W13-07-07-01-02")
download = st.button("⬇️ Generate PDF")


# ================= PDF BUILDER =================
def build_pdf():
    logo_img, logo_ir = load_logo()
    if not logo_ir:
        raise Exception("Logo missing")

    # Barcode
    bbuf = io.BytesIO()
    code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
    code128.render({
        "write_text": False,
        "dpi": 600,
        "module_height": 22,
        "module_width": 0.45,
    }).save(bbuf, format="PNG")
    bbuf.seek(0)
    bar_ir = ImageReader(bbuf)

    # Canvas
    W, H = 210 * mm, 60 * mm
    c = canvas.Canvas(io.BytesIO(), pagesize=(W, H))
    m = 4 * mm

    # ===== LEFT ARROW BOX =====
    left_w = W * 0.26
    box_h = H - 2 * m

    c.setLineWidth(1.4)
    c.roundRect(m, m, left_w, box_h, 3 * mm)

    c.setFillColor(HexColor("#E5E5E5"))
    c.roundRect(m + 1, m + 1, left_w - 2, box_h - 2, 3 * mm, stroke=0, fill=1)

    cx = m + left_w / 2
    top = m + box_h - 3 * mm
    bot = m + 3 * mm

    p = c.beginPath()
    p.moveTo(cx - 18 * mm, bot)
    p.lineTo(cx + 18 * mm, bot)
    p.lineTo(cx + 18 * mm, m + box_h * 0.52)
    p.lineTo(m + left_w - 4 * mm, m + box_h * 0.52)
    p.lineTo(cx, top)
    p.lineTo(m + 4 * mm, m + box_h * 0.52)
    p.lineTo(cx - 18 * mm, m + box_h * 0.52)
    p.close()

    c.setFillColor(black)
    c.drawPath(p, fill=1, stroke=0)

    # ===== RIGHT BOX =====
    rx = m + left_w + 2 * mm
    rw = W - rx - m

    c.roundRect(rx, m, rw, box_h, 3 * mm)

    # Barcode
    c.drawImage(
        bar_ir,
        rx + 5 * mm,
        m + box_h * 0.48,
        width=rw - 10 * mm,
        height=box_h * 0.42,
        mask="auto",
    )

    # Separator
    sep_y = m + box_h * 0.44
    c.setLineWidth(2)
    c.line(rx + 4 * mm, sep_y, rx + rw - 4 * mm, sep_y)

    # ===== BOTTOM BAND =====
    band_y = m + 4 * mm
    band_h = sep_y - band_y - 3 * mm

    # Logo
    logo_size = band_h * 0.95
    c.drawImage(
        logo_ir,
        rx + 6 * mm,
        band_y + (band_h - logo_size) / 2,
        logo_size,
        logo_size,
        mask="auto",
    )

    # Text
    c.setFont("Helvetica-Bold", 38)
    c.drawString(
        rx + 6 * mm + logo_size + 6 * mm,
        band_y + band_h / 2 - 12,
        barcode_text,
    )

    c.showPage()
    c.save()
    return c.getpdfdata()


# ================= OUTPUT =================
if download:
    pdf = build_pdf()
    st.download_button(
        "⬇️ Download Label PDF",
        pdf,
        f"{barcode_text}.pdf",
        "application/pdf",
    )
