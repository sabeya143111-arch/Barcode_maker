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

# ================= LOGO PATH =================
BASE_DIR = Path(__file__).resolve().parent
LOCAL_LOGO_PATH = BASE_DIR / "assets" / "logo.png"

GITHUB_LOGO_URL = (
    "https://raw.githubusercontent.com/"
    "sabeya143111-arch/Barcode_maker/main/Barcode_maker/assets/logo.png"
)

_logo_cache = {}

def load_logo():
    if "ir" in _logo_cache:
        return _logo_cache["ir"]

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
        _logo_cache["ir"] = ir
        return ir
    except:
        return None


# ================= STREAMLIT =================
st.set_page_config("Warehouse Label", "🏷️", layout="wide")
st.title("🏷️ Warehouse Location Label")

barcode_text = st.text_input("Location Code", "W13-07-07-01-02")
generate = st.button("⬇️ Generate PDF")


# ================= PDF =================
def build_pdf():
    logo_ir = load_logo()
    if not logo_ir:
        raise Exception("Logo not found")

    # Barcode image
    bbuf = io.BytesIO()
    code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
    code128.render({
        "write_text": False,
        "dpi": 600,
        "module_height": 20,
        "module_width": 0.45,
    }).save(bbuf, format="PNG")
    bbuf.seek(0)
    bar_ir = ImageReader(bbuf)

    # Canvas
    W, H = 210 * mm, 60 * mm
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(W, H))
    m = 4 * mm

    # ================= LEFT ARROW BOX =================
    left_w = W * 0.26
    box_h = H - 2 * m

    c.setLineWidth(1.4)
    c.roundRect(m, m, left_w, box_h, 3 * mm)

    c.setFillColor(HexColor("#E6E6E6"))
    c.roundRect(m + 1, m + 1, left_w - 2, box_h - 2, 3 * mm, stroke=0, fill=1)

    # ---- SIMPLE ARROW (PHOTO MATCH) ----
    cx = m + left_w / 2
    arrow_bottom = m + 7 * mm
    arrow_top = m + box_h - 7 * mm

    stem_w = 14 * mm
    stem_h = 22 * mm

    c.setFillColor(black)

    # Stem
    c.rect(
        cx - stem_w / 2,
        arrow_bottom,
        stem_w,
        stem_h,
        stroke=0,
        fill=1,
    )

    # Head
    p = c.beginPath()
    p.moveTo(cx - 26 * mm, arrow_bottom + stem_h)
    p.lineTo(cx + 26 * mm, arrow_bottom + stem_h)
    p.lineTo(cx, arrow_top)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # ================= RIGHT BOX =================
    rx = m + left_w + 2 * mm
    rw = W - rx - m

    c.setLineWidth(1.4)
    c.roundRect(rx, m, rw, box_h, 3 * mm)

    # Barcode (top)
    c.drawImage(
        bar_ir,
        rx + 6 * mm,
        m + box_h * 0.50,
        width=rw - 12 * mm,
        height=box_h * 0.40,
        mask="auto",
    )

    # Separator line
    sep_y = m + box_h * 0.45
    c.setLineWidth(2)
    c.line(rx + 5 * mm, sep_y, rx + rw - 5 * mm, sep_y)

    # ================= BOTTOM BAND =================
    band_y = m + 5 * mm
    band_h = sep_y - band_y - 3 * mm

    # Logo (SMALL & FIXED)
    logo_size = 13 * mm
    c.drawImage(
        logo_ir,
        rx + 8 * mm,
        band_y + (band_h - logo_size) / 2,
        logo_size,
        logo_size,
        mask="auto",
    )

    # Text
    c.setFont("Helvetica-Bold", 38)
    c.drawString(
        rx + 8 * mm + logo_size + 6 * mm,
        band_y + band_h / 2 - 12,
        barcode_text,
    )

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()


# ================= OUTPUT =================
if generate:
    try:
        pdf = build_pdf()
        st.download_button(
            "⬇️ Download PDF",
            pdf,
            f"{barcode_text}.pdf",
            "application/pdf",
        )
    except Exception as e:
        st.error(str(e))
