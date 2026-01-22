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
BASE_DIR = Path(__file__).resolve().parent.parent
LOCAL_LOGO_PATH = BASE_DIR / "assets" / "logo.png"

GITHUB_LOGO_URL = (
    "https://raw.githubusercontent.com/"
    "sabeya143111-arch/Barcode_maker/main/assets/logo.png"
)


def load_logo(uploaded_file=None):
    """Logo load karega - pehle uploaded, phir local, phir GitHub se."""
    # 1) User uploaded logo
    if uploaded_file is not None:
        try:
            img = Image.open(uploaded_file).convert("RGBA")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            return img, ImageReader(buf)
        except Exception:
            pass

    # 2) Local logo
    if LOCAL_LOGO_PATH.exists():
        try:
            img = Image.open(LOCAL_LOGO_PATH).convert("RGBA")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            return img, ImageReader(buf)
        except Exception:
            pass

    # 3) GitHub logo
    try:
        response = urlopen(GITHUB_LOGO_URL, timeout=10)
        data = response.read()
        buf = io.BytesIO(data)
        buf.seek(0)
        img = Image.open(buf).convert("RGBA")
        buf2 = io.BytesIO()
        img.save(buf2, format="PNG")
        buf2.seek(0)
        return img, ImageReader(buf2)
    except Exception:
        return None, None


# ===== PAGE CONFIG + GLOBAL CSS =====
st.set_page_config(page_title="Swag Logo Maker", page_icon="🏷️", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top, #020617 0, #020617 40%, #020617 100%);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        max-width: 1200px;
    }

    [data-testid="stSidebar"] {
        background: radial-gradient(circle at top, #111827 0, #020617 55%);
        border-right: 1px solid rgba(148,163,184,0.35);
    }

    .glass-card {
        background: rgba(15,23,42,0.85);
        border-radius: 14px;
        padding: 14px 14px 6px 14px;
        border: 1px solid rgba(148,163,184,0.35);
        box-shadow: 0 18px 40px rgba(0,0,0,0.45);
        backdrop-filter: blur(18px);
    }

    .section-title {
        font-size: 12px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #9CA3AF;
        margin: 4px 0 6px 0;
    }

    .hero-title {
        font-size: 40px;
        font-weight: 800;
        background: linear-gradient(90deg,#FF6B35,#FACC15);
        -webkit-background-clip: text;
        color: transparent;
        margin-bottom: 4px;
    }

    .hero-sub {
        font-size: 14px;
        color: #9CA3AF;
    }

    .preview-card {
        background: radial-gradient(circle at top left,#0F172A 0,#020617 55%);
        border-radius: 18px;
        padding: 18px;
        border: 1px solid rgba(148,163,184,0.35);
    }

    .preview-title {
        font-size: 18px;
        font-weight: 600;
        color: #E5E7EB;
        margin-bottom: 6px;
    }

    .preview-sub {
        font-size: 13px;
        color: #9CA3AF;
        margin-bottom: 10px;
    }

    .settings-title {
        font-size: 16px;
        font-weight: 600;
        color: #E5E7EB;
        margin-bottom: 6px;
    }

    .settings-sub {
        font-size: 12px;
        color: #9CA3AF;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===== HERO HEADER =====
with st.container():
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown('<div class="hero-title">Swag Logo Maker</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="hero-sub">'
            'Premium warehouse labels • Odoo‑ready • High‑resolution PDFs'
            "</div>",
            unsafe_allow_html=True,
        )
    with col_h2:
        st.markdown(
            """
            <div style="text-align:right; margin-top:4px;">
                <span style="font-size:12px; color:#9CA3AF;">
                    Powered by Streamlit • ReportLab • python-barcode
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("")

# ===== SIDEBAR INPUTS =====
with st.sidebar:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="settings-title">Control panel</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="settings-sub">Tune your label layout, logo and barcode exactly the way warehouse needs.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">Location code</div>', unsafe_allow_html=True)
    barcode_text = st.text_input(
        "Location Code (e.g. W13-07-07-01-02)",
        value="W13-07-07-01-02",
    )

    st.markdown('<div class="section-title">Label size</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        label_width_mm = st.number_input("Width (mm)", value=210.0, min_value=20.0)
    with c2:
        label_height_mm = st.number_input("Height (mm)", value=60.0, min_value=20.0)

    st.markdown('<div class="section-title">Text</div>', unsafe_allow_html=True)
    text_font_size = st.slider(
        "Font size", min_value=16, max_value=90, value=60, step=1
    )
    underline_gap_mm = st.slider(
        "Text–underline gap (mm)", min_value=1.0, max_value=10.0, value=3.0, step=0.5
    )

    st.markdown('<div class="section-title">Logo</div>', unsafe_allow_html=True)
    logo_scale = st.slider(
        "Logo size (%)", min_value=20, max_value=80, value=45, step=5
    )
    uploaded_logo = st.file_uploader(
        "Custom logo (PNG/JPG)", type=["png", "jpg", "jpeg"]
    )

    st.markdown('<div class="section-title">Barcode</div>', unsafe_allow_html=True)
    module_height = st.slider(
        "Height", min_value=5, max_value=40, value=18, step=1
    )
    module_width = st.slider(
        "Thickness",
        min_value=0.2,
        max_value=1.0,
        value=0.45,
        step=0.05,
    )
    dpi_value = st.slider(
        "DPI", min_value=300, max_value=1200, value=600, step=100
    )

    st.markdown("---")
    preview_btn = st.button("👀 Live preview")
    download_btn = st.button("⬇️ Download PDF", type="primary")
    st.markdown("</div>", unsafe_allow_html=True)


def build_pdf(
    module_h: int = 18,
    module_w: float = 0.45,
    dpi: int = 600,
):
    if not barcode_text.strip():
        raise ValueError("Code likho.")

    # ---------- LOGO ----------
    logo_img, logo_ir = load_logo(uploaded_logo)

    # ---------- BARCODE ----------
    bbuf = io.BytesIO()
    code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
    writer_opts = {
        "write_text": False,
        "dpi": dpi,
        "module_height": module_h,
        "module_width": module_w,
    }
    code128.render(writer_opts).save(bbuf, format="PNG")
    bbuf.seek(0)
    bar_ir = ImageReader(bbuf)

    # ---------- CANVAS / PAGE SIZE ----------
    lw = float(label_width_mm) * mm
    lh = float(label_height_mm) * mm

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=(lw, lh))

    margin = 3 * mm

    # ===== LEFT: ARROW BOX =====
    left_w = lw * 0.26
    left_h = lh - 2 * margin
    left_x = margin
    left_y = margin

    c.setLineWidth(1.2)
    radius = 2.5 * mm

    c.setStrokeColor(black)
    c.roundRect(left_x, left_y, left_w, left_h, radius)

    bg_grey = HexColor("#DDDDDD")
    c.setFillColor(bg_grey)
    c.roundRect(
        left_x + 0.8 * mm,
        left_y + 0.8 * mm,
        left_w - 1.6 * mm,
        left_h - 1.6 * mm,
        radius,
        stroke=0,
        fill=1,
    )

    mid_x = left_x + left_w / 2.0
    top_y = left_y + left_h - 2.0 * mm
    bottom_y = left_y + 2.0 * mm

    head_h = left_h * 0.50
    shaft_w = left_w * 0.38

    p = c.beginPath()
    p.moveTo(mid_x - shaft_w / 2, bottom_y)
    p.lineTo(mid_x + shaft_w / 2, bottom_y)
    p.lineTo(mid_x + shaft_w / 2, bottom_y + (left_h - head_h))
    p.lineTo(left_x + left_w * 0.95, bottom_y + left_h - head_h)
    p.lineTo(mid_x, top_y)
    p.lineTo(left_x + left_w * 0.05, bottom_y + left_h - head_h)
    p.lineTo(mid_x - shaft_w / 2, bottom_y + (left_h - head_h))
    p.close()

    c.setFillColor(black)
    c.drawPath(p, stroke=0, fill=1)

    # ===== RIGHT: BARCODE UPAR, NICHE LOGO + TEXT =====
    right_x = left_x + left_w + 1 * mm
    right_w = lw - right_x - margin
    right_y = margin
    right_h = lh - 2 * margin

    c.setLineWidth(1.2)
    c.setStrokeColor(black)
    c.roundRect(right_x, right_y, right_w, right_h, 3 * mm)
    center_x = right_x + right_w / 2.0

    # ---- BARCODE AREA (TOP) ----
    barcode_area_top = right_y + right_h - 4 * mm
    barcode_area_bottom = right_y + right_h * 0.55  # niche ka band bada rakhne ke liye

    barcode_area_h = barcode_area_top - barcode_area_bottom
    bar_w = right_w * 0.92
    bar_h = barcode_area_h * 0.90

    bar_x = center_x - bar_w / 2.0
    bar_y = barcode_area_bottom + (barcode_area_h - bar_h) / 2.0

    c.drawImage(
        bar_ir,
        bar_x,
        bar_y,
        width=bar_w,
        height=bar_h,
        mask="auto",
    )

    # ---- TEXT + LOGO BAND (BARCODE KE NICHE) ----
    band_top_y = barcode_area_bottom - underline_gap_mm * mm   # upper line
    band_bottom_y = right_y + 3 * mm                           # lower line
    text_center_y = (band_top_y + band_bottom_y) / 2.0

    c.setLineWidth(2)
    c.line(
        right_x + 3 * mm,
        band_top_y,
        right_x + right_w - 3 * mm,
        band_top_y,
    )
    c.line(
        right_x + 3 * mm,
        band_bottom_y,
        right_x + right_w - 3 * mm,
        band_bottom_y,
    )

    band_height = band_top_y - band_bottom_y

    # ---- LOGO BOX (LEFT, BAND KE ANDAR) ----
    green_h = band_height * 0.80
    green_w = green_h
    green_x = right_x + 4 * mm
    green_y = band_bottom_y + (band_height - green_h) / 2.0

    c.setLineWidth(1)
    c.roundRect(green_x, green_y, green_w, green_h, 3 * mm)

    if logo_img and logo_ir:
        logo_margin = 1.0 * mm
        logo_w = green_w - 2 * logo_margin
        logo_h = green_h - 2 * logo_margin

        ratio = logo_img.width / logo_img.height
        if logo_w / logo_h > ratio:
            logo_w = logo_h * ratio
        else:
            logo_h = logo_w / ratio

        lx = green_x + (green_w - logo_w) / 2.0
        ly = green_y + (green_h - logo_h) / 2.0

        c.drawImage(
            logo_ir,
            lx,
            ly,
            width=logo_w,
            height=logo_h,
            mask="auto",
        )

    # ---- TEXT (LOGO KE R
