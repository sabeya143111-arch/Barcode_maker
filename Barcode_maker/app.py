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
# Path ko current file ke folder ke mutabiq set kiya gaya hai
BASE_DIR = Path(__file__).resolve().parent
LOCAL_LOGO_PATH = BASE_DIR / "assets" / "logo.png"

# GitHub URL ko bhi updated structure ke mutabiq set kiya gaya hai
GITHUB_LOGO_URL = (
    "https://raw.githubusercontent.com/"
    "sabeya143111-arch/Barcode_maker/main/Barcode_maker/assets/logo.png"
)

# ---- logo cache to prevent garbage collection ----
_logo_cache = {}

def load_logo():
    """Pehle local logo, phir GitHub fallback; buffers ko cache mein rakhta hai."""
    if "img" in _logo_cache:
        return _logo_cache["img"], _logo_cache["ir"]

    # 1) Local logo check
    try:
        if LOCAL_LOGO_PATH.exists():
            img = Image.open(LOCAL_LOGO_PATH).convert("RGBA")
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
        img = Image.open(buf).convert("RGBA")
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
    [data-testid="stSidebar"] { background: radial-gradient(circle at top, #111827 0, #020617 55%); border-right: 1px solid rgba(148,163,184,0.35); }
    .glass-card { background: rgba(15,23,42,0.85); border-radius: 14px; padding: 14px; border: 1px solid rgba(148,163,184,0.35); box-shadow: 0 18px 40px rgba(0,0,0,0.45); backdrop-filter: blur(18px); }
    .section-title { font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: #9CA3AF; margin: 10px 0 5px 0; }
    .hero-title { font-size: 40px; font-weight: 800; background: linear-gradient(90deg,#FF6B35,#FACC15); -webkit-background-clip: text; color: transparent; }
    .hero-sub { font-size: 14px; color: #9CA3AF; }
    .preview-card { background: radial-gradient(circle at top left,#0F172A 0,#020617 55%); border-radius: 18px; padding: 20px; border: 1px solid rgba(148,163,184,0.35); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===== HERO HEADER =====
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="hero-title">Swag Logo Maker</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Premium warehouse labels • Odoo‑ready • High‑res PDFs</div>', unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div style="color:white; font-weight:600;">Control Panel</div>', unsafe_allow_html=True)
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
    if not logo_ir: raise ValueError("Logo not found in assets or GitHub.")

    # Barcode setup
    bbuf = io.BytesIO()
    code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
    code128.render({"write_text": False, "dpi": dpi_value, "module_height": module_height, "module_width": module_width}).save(bbuf, format="PNG")
    bbuf.seek(0)
    bar_ir = ImageReader(bbuf)

    # Canvas setup
    lw, lh = label_width_mm * mm, label_height_mm * mm
    pdf_buf = io.BytesIO()
    c = canvas.Canvas(pdf_buf, pagesize=(lw, lh))
    m = 3 * mm

    # Left Box (Arrow)
    lw_box, lh_box = lw * 0.26, lh - 2 * m
    c.setLineWidth(1.2)
    c.roundRect(m, m, lw_box, lh_box, 2.5 * mm)
    c.setFillColor(HexColor("#DDDDDD"))
    c.roundRect(m + 0.8 * mm, m + 0.8 * mm, lw_box - 1.6 * mm, lh_box - 1.6 * mm, 2.5 * mm, stroke=0, fill=1)
    
    # Arrow shape
    mx, ty, by = m + lw_box / 2, m + lh_box - 2 * mm, m + 2 * mm
    path = c.beginPath()
    path.moveTo(mx - (lw_box * 0.19), by)
    path.lineTo(mx + (lw_box * 0.19), by)
    path.lineTo(mx + (lw_box * 0.19), by + lh_box * 0.5)
    path.lineTo(m + lw_box * 0.95, by + lh_box * 0.5)
    path.lineTo(mx, ty)
    path.lineTo(m + lw_box * 0.05, by + lh_box * 0.5)
    path.lineTo(mx - (lw_box * 0.19), by + lh_box * 0.5)
    path.close()
    c.setFillColor(black); c.drawPath(path, stroke=0, fill=1)

    # Right Box
    rx, rw, rh = m + lw_box + 1 * mm, lw - (m + lw_box + 1 * mm) - m, lh - 2 * m
    c.roundRect(rx, m, rw, rh, 3 * mm)

    # Barcode
    bh = rh * 0.45; bw = rw * 0.9
    c.drawImage(bar_ir, rx + (rw - bw) / 2, m + rh - bh - 4 * mm, width=bw, height=bh, mask="auto")

    # Bottom Band (Logo + Text)
    band_y = m + 3 * mm
    band_h = (m + rh - bh - 4 * mm) - band_y - (underline_gap_mm * mm)
    c.setLineWidth(2)
    c.line(rx + 3 * mm, band_y + band_h + underline_gap_mm * mm, rx + rw - 3 * mm, band_y + band_h + underline_gap_mm * mm)
    
    # Logo placement
    lh_logo = band_h * 0.8; lw_logo = lh_logo
    ratio = logo_img.width / logo_img.height
    if lw_logo / lh_logo > ratio: lw_logo = lh_logo * ratio
    else: lh_logo = lw_logo / ratio
    c.drawImage(logo_ir, rx + 4 * mm, band_y + (band_h - lh_logo) / 2, width=lw_logo, height=lh_logo, mask="auto")

    # Text placement
    c.setFont("Helvetica-Bold", 40)
    tw = c.stringWidth(barcode_text, "Helvetica-Bold", 40)
    max_tw = rw - lw_logo - 12 * mm
    size = 40
    while tw > max_tw and size > 10:
        size -= 2
        c.setFont("Helvetica-Bold", size)
        tw = c.stringWidth(barcode_text, "Helvetica-Bold", size)
    c.drawCentredString(rx + lw_logo + 8 * mm + max_tw / 2, band_y + band_h / 2 - size / 4, barcode_text)

    c.showPage(); c.save()
    pdf_buf.seek(0)
    return pdf_buf.getvalue()

# ===== MAIN APP =====
if preview_btn or download_btn:
    try:
        with st.spinner("Generating PDF..."):
            pdf_data = build_pdf()
        st.success("Success!")
        st.download_button("Download PDF", data=pdf_data, file_name=f"{barcode_text}.pdf", mime="application/pdf", use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")
