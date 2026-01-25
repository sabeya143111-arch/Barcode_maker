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

# ===== PATH / LOGO SETTINGS =====
BASE_DIR = Path(__file__).resolve().parent
LOCAL_LOGO_PATH = BASE_DIR / "assets" / "logo.png"

GITHUB_LOGO_URL = (
    "https://raw.githubusercontent.com/"
    "sabeya143111-arch/Barcode_maker/main/Barcode_maker/assets/logo.png"
)

# ---- logo cache to prevent garbage collection ----
_logo_cache = {}


def _make_square_rgba(img: Image.Image) -> Image.Image:
    """Transparent PNG ko square canvas pe centre karta hai."""
    side = max(img.width, img.height)
    canvas_img = Image.new("RGBA", (side, side), (255, 255, 255, 0))
    off_x = (side - img.width) // 2
    off_y = (side - img.height) // 2
    canvas_img.paste(img, (off_x, off_y), img)
    return canvas_img


def load_logo():
    """Pehle local logo, phir GitHub fallback; buffers ko cache mein rakhta hai."""
    if "img" in _logo_cache:
        return _logo_cache["img"], _logo_cache["ir"]

    # 1) Local logo check
    try:
        if LOCAL_LOGO_PATH.exists():
            raw = Image.open(LOCAL_LOGO_PATH).convert("RGBA")
            img = _make_square_rgba(raw)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            ir = ImageReader(buf)
            _logo_cache["img"], _logo_cache["ir"], _logo_cache["buf"] = img, ir, buf
            return img, ir
    except Exception:
        pass

    # 2) GitHub logo fallback
    try:
        response = urlopen(GITHUB_LOGO_URL, timeout=10)
        data = response.read()
        buf = io.BytesIO(data)
        buf.seek(0)
        raw = Image.open(buf).convert("RGBA")
        img = _make_square_rgba(raw)
        buf2 = io.BytesIO()
        img.save(buf2, format="PNG")
        buf2.seek(0)
        ir = ImageReader(buf2)
        _logo_cache["img"], _logo_cache["ir"], _logo_cache["buf"] = img, ir, buf2
        return img, ir
    except Exception:
        return None, None


# ===== PAGE CONFIG + GLOBAL CSS =====
st.set_page_config(page_title="Swag Logo Maker", page_icon="🏷️", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: radial-gradient(circle at top, #020617 0, #020617 40%, #020617 100%); }
    .block-container { padding-top: 1.5rem; max-width: 1200px; }
    [data-testid="stSidebar"] {
        background: radial-gradient(circle at top, #111827 0, #020617 55%);
        border-right: 1px solid rgba(148,163,184,0.35);
    }
    .glass-card {
        background: rgba(15,23,42,0.85);
        border-radius: 14px;
        padding: 14px;
        border: 1px solid rgba(148,163,184,0.35);
        box-shadow: 0 18px 40px rgba(0,0,0,0.45);
        backdrop-filter: blur(18px);
    }
    .hero-title {
        font-size: 40px;
        font-weight: 800;
        background: linear-gradient(90deg,#FF6B35,#FACC15);
        -webkit-background-clip: text;
        color: transparent;
    }
    .hero-sub { font-size: 14px; color: #9CA3AF; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===== HERO HEADER =====
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="hero-title">Swag Logo Maker</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-sub">Premium warehouse labels • Odoo‑ready • High‑res PDFs</div>',
        unsafe_allow_html=True,
    )

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    barcode_text = st.text_input("Location Code", value="W13-07-07-01-02")

    c1, c2 = st.columns(2)
    label_width_mm = c1.number_input("Width (mm)", value=210.0)
    label_height_mm = c2.number_input("Height (mm)", value=60.0)

    underline_gap_mm = st.slider("Gap (mm)", 1.0, 10.0, 2.0)
    module_height = st.slider("Bar Height", 5, 40, 18)
    module_width = st.slider("Thickness", 0.2, 1.0, 0.45)
    dpi_value = st.slider("DPI", 300, 1200, 600, 100)

    st.markdown("---")
    preview_btn = st.button("👀 Live Preview")
    download_btn = st.button("⬇️ Download PDF", type="primary")
    st.markdown("</div>", unsafe_allow_html=True)


# ===== PDF BUILDER =====
def build_pdf():
    logo_img, logo_ir = load_logo()
    if not logo_ir:
        raise ValueError("Logo not found.")

    # BARCODE
    bbuf = io.BytesIO()
    code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
    code128.render(
        {
            "write_text": False,
            "dpi": dpi_value,
            "module_height": module_height,
            "module_width": module_width,
        }
    ).save(bbuf, format="PNG")
    bbuf.seek(0)
    bar_ir = ImageReader(bbuf)

    # CANVAS
    lw, lh = label_width_mm * mm, label_height_mm * mm
    pdf_buf = io.BytesIO()
    c = canvas.Canvas(pdf_buf, pagesize=(lw, lh))
    m = 3 * mm

    # LEFT ARROW BOX
    lw_left = lw * 0.25
    lh_left = lh - 2 * m
    c.setLineWidth(1.2)
    c.setStrokeColor(black)
    c.roundRect(m, m, lw_left, lh_left, 3 * mm)

    c.setFillColor(HexColor("#DDDDDD"))
    c.roundRect(
        m + 1 * mm,
        m + 1 * mm,
        lw_left - 2 * mm,
        lh_left - 2 * mm,
        2.5 * mm,
        stroke=0,
        fill=1,
    )

    mx = m + lw_left / 2
    top_y = m + lh_left - 3 * mm
    bottom_y = m + 3 * mm
    mid_y = bottom_y + lh_left * 0.45

    path = c.beginPath()
    path.moveTo(mx - lw_left * 0.20, bottom_y)
    path.lineTo(mx + lw_left * 0.20, bottom_y)
    path.lineTo(mx + lw_left * 0.20, mid_y)
    path.lineTo(m + lw_left * 0.93, mid_y)
    path.lineTo(mx, top_y)
    path.lineTo(m + lw_left * 0.07, mid_y)
    path.lineTo(mx - lw_left * 0.20, mid_y)
    path.close()
    c.setFillColor(black)
    c.drawPath(path, stroke=0, fill=1)

    # RIGHT MAIN BOX
    rx = m + lw_left + 1 * mm
    rw = lw - rx - m
    rh = lh - 2 * m
    c.setStrokeColor(black)
    c.roundRect(rx, m, rw, rh, 3 * mm)

    # BARCODE TOP
    bh = rh * 0.42
    bw = rw * 0.92
    c.drawImage(
        bar_ir,
        rx + (rw - bw) / 2,
        m + rh - bh - 3 * mm,
        width=bw,
        height=bh,
        mask="auto",
    )

    line_y = m + rh - bh - 6 * mm
    c.setLineWidth(2)
    c.line(rx + 3 * mm, line_y, rx + rw - 3 * mm, line_y)

    # ===== BOTTOM BAND (LOGO + TEXT) =====
    band_y = m + 4 * mm
    band_h = line_y - band_y - 2 * mm

    # ---------- LOGO (slightly bigger) ----------
    usable_w = rw - 8 * mm
    logo_section_w = usable_w * 0.50      # 50% width logo

    logo_x = rx + 4 * mm

    lh_logo = band_h * 0.99               # almost full band height
    lw_logo = lh_logo
    ratio = logo_img.width / logo_img.height
    if lw_logo / lh_logo > ratio:
        lw_logo = lh_logo * ratio
    else:
        lh_logo = lw_logo / ratio

    logo_y = band_y + (band_h - lh_logo) / 2
    c.drawImage(
        logo_ir,
        logo_x,
        logo_y,
        width=lw_logo,
        height=lh_logo,
        mask="auto",
    )

    # ---------- TEXT (centre + bigger) ----------
    text_start_x = logo_x + logo_section_w + 1 * mm
    max_tw = rx + rw - text_start_x - 3 * mm

    text_size = int(band_h * 1.0)     # 100% of band height
    text_size = min(text_size, 60)
    text_size = max(text_size, 22)

    c.setFont("Helvetica-Bold", text_size)
    tw = c.stringWidth(barcode_text, "Helvetica-Bold", text_size)
    while tw > max_tw and text_size > 18:
        text_size -= 2
        c.setFont("Helvetica-Bold", text_size)
        tw = c.stringWidth(barcode_text, "Helvetica-Bold", text_size)

    text_y = band_y + band_h / 2 - text_size / 3
    text_cx = text_start_x + max_tw / 2
    c.drawCentredString(text_cx, text_y, barcode_text)

    c.showPage()
    c.save()
    pdf_buf.seek(0)
    return pdf_buf.getvalue()


# ===== MAIN APP =====
if preview_btn or download_btn:
    try:
        with st.spinner("Generating PDF..."):
            pdf_data = build_pdf()
        st.success("Success!")
        st.download_button(
            "Download PDF",
            data=pdf_data,
            file_name=f"{barcode_text}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Error: {e}")
