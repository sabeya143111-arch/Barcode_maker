import streamlit as st
from pathlib import Path
from PIL import Image, ImageChops
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


def _crop_alpha(img: Image.Image) -> Image.Image:
    """Transparent borders hata ke tight crop karta hai."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    bg = Image.new("RGBA", img.size, (0, 0, 0, 0))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        return img.crop(bbox)
    return img


def _make_square_rgba(img: Image.Image) -> Image.Image:
    """Transparent PNG ko pehle crop, fir square canvas pe centre karta hai."""
    img = _crop_alpha(img)
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
st.set_page_config(page_title="Swag Barcode Maker", page_icon="🏷️", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top, #020617 0, #020617 40%, #020617 100%);
        color: #E5E7EB;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
    }
    .block-container {
        padding-top: 2.5rem;
        max-width: 1000px;
    }
    [data-testid="stSidebar"] {
        background: radial-gradient(circle at top, #111827 0, #020617 55%);
        border-right: 1px solid rgba(148,163,184,0.5);
        color: #E5E7EB;
    }
    label, .stMarkdown, .stTextInput, .stNumberInput, .stSlider, .stButton {
        color: #E5E7EB !important;
    }
    .stSlider > div > div > div[data-baseweb="slider"] div {
        color: #E5E7EB !important;
    }
    .stTextInput input, .stNumberInput input {
        color: #F9FAFB !important;
        background-color: rgba(15,23,42,0.9) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(148,163,184,0.6) !important;
    }
    .stButton button {
        color: #0F172A !important;
        font-weight: 600 !important;
    }

    .glass-card {
        background: rgba(15,23,42,0.92);
        border-radius: 16px;
        padding: 16px;
        border: 1px solid rgba(148,163,184,0.55);
        box-shadow: 0 18px 40px rgba(0,0,0,0.7);
        backdrop-filter: blur(18px);
        color: #E5E7EB;
    }

    .hero-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        gap: 0.8rem;
        margin-bottom: 1.8rem;
        color: #E5E7EB;
    }
    .hero-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 999px;
        background: rgba(15,23,42,0.98);
        border: 1px solid rgba(248,250,252,0.25);
        box-shadow: 0 0 0 1px rgba(15,23,42,0.8);
        font-size: 12px;
        color: #E5E7EB;
    }
    .hero-dot {
        width: 7px;
        height: 7px;
        border-radius: 999px;
        background: #22C55E;
        box-shadow: 0 0 14px rgba(34,197,94,1);
        animation: pulse 1.8s ease-out infinite;
    }
    .hero-title {
        font-size: 52px;
        font-weight: 900;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        background: conic-gradient(from 180deg, #F97316, #FACC15, #22C55E, #F97316);
        -webkit-background-clip: text;
        color: transparent;
        text-shadow: 0 14px 40px rgba(0,0,0,0.85);
        animation: glowText 3.5s ease-in-out infinite;
    }
    .hero-sub {
        font-size: 14px;
        color: #E5E7EB;
        max-width: 520px;
    }
    .hero-sub span {
        color: #FACC15;
        font-weight: 600;
    }
    .hero-bottom-note {
        font-size: 11px;
        color: #D1D5DB;
        text-transform: uppercase;
        letter-spacing: 0.18em;
    }

    .glass-card h1, .glass-card h2, .glass-card h3,
    .glass-card div, .glass-card ul, .glass-card li, .glass-card ol {
        color: #E5E7EB;
    }
    .glass-card small, .glass-card span.subtle {
        color: #9CA3AF;
    }

    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        60% { transform: scale(1.6); opacity: 0; }
        100% { transform: scale(1.6); opacity: 0; }
    }
    @keyframes glowText {
        0% { text-shadow: 0 10px 25px rgba(0,0,0,0.8); }
        50% { text-shadow: 0 14px 45px rgba(249,115,22,0.5); }
        100% { text-shadow: 0 10px 25px rgba(0,0,0,0.8); }
    }
    @keyframes borderGlow {
        0% { opacity: 0.65; box-shadow: 0 0 12px rgba(250,204,21,0.2); }
        50% { opacity: 1; box-shadow: 0 0 30px rgba(56,189,248,0.35); }
        100% { opacity: 0.65; box-shadow: 0 0 12px rgba(250,204,21,0.2); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===== HERO HEADER =====
st.markdown(
    """
    <div class="hero-wrapper">
        <div class="hero-pill">
            <div class="hero-dot"></div>
            <span>Instant warehouse labels • Made for Odoo</span>
        </div>
        <div class="hero-title">
            SWAG BARCODE MAKER
        </div>
        <div class="hero-sub">
            Design <span>premium location labels</span> with logo + Code128 barcode,
            export as crisp high‑res PDFs ready for warehouse printing.
        </div>
        <div class="hero-bottom-note">
            TYPE LOCATION • TUNE SIZE • DOWNLOAD PDF
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ===== FEATURE GRID (yahi block tumne bheja tha, ab sahi wrap kiya) =====
st.markdown(
    """
    <div style="
        margin-top: 0.8rem;
        margin-bottom: 1.4rem;
        padding: 1px;
        border-radius: 18px;
        background: linear-gradient(120deg, rgba(250,204,21,0.25), rgba(56,189,248,0.1), rgba(249,115,22,0.25));
        animation: borderGlow 4s ease-in-out infinite;
    ">
      <div class="glass-card" style="border-radius: 16px; background: radial-gradient(circle at top left, rgba(15,23,42,0.98), rgba(15,23,42,0.92));">
        <div style="display:flex; flex-wrap:wrap; gap:18px; align-items:stretch;">
          
          <!-- Left big value prop -->
          <div style="flex:1.3; min-width:230px; display:flex; flex-direction:column; gap:10px;">
            <div style="font-size:11px; text-transform:uppercase; letter-spacing:0.18em; color:#9CA3AF;">
              BUILT FOR BUSY WAREHOUSES
            </div>
            <div style="font-size:20px; font-weight:650; color:#F9FAFB;">
              One clean tool to generate every location label your pickers will ever scan.
            </div>
            <div style="display:flex; gap:16px; margin-top:6px;">
              <div style="font-size:24px; font-weight:700; color:#FACC15;">60s</div>
              <div style="font-size:12px; color:#E5E7EB;">
                From typing a new rack code<br>to downloading a print‑ready PDF.
              </div>
            </div>
            <div style="margin-top:6px; font-size:11px; color:#9CA3AF;">
              Optimised for barcode scanners, forklifts & real‑world warehouse chaos.
            </div>
          </div>

          <!-- Middle feature pills -->
          <div style="flex:1; min-width:220px; display:flex; flex-direction:column; gap:10px;">
            <div style="font-size:11px; text-transform:uppercase; letter-spacing:0.16em; color:#9CA3AF;">
              SIGNATURE FEATURES
            </div>
            <div style="display:flex; flex-direction:column; gap:8px; font-size:12px;">
              <div style="
                  padding:8px 10px;
                  border-radius:999px;
                  background:rgba(15,23,42,0.95);
                  border:1px solid rgba(148,163,184,0.6);
                  display:flex; align-items:center; gap:8px;
              ">
                <span style="width:7px; height:7px; border-radius:999px; background:#FACC15; box-shadow:0 0 10px rgba(250,204,21,1);"></span>
                <span>Smart spacing: text + logo + barcode always perfectly balanced.</span>
              </div>
              <div style="
                  padding:8px 10px;
                  border-radius:999px;
                  background:rgba(15,23,42,0.95);
                  border:1px solid rgba(148,163,184,0.45);
                  display:flex; align-items:center; gap:8px;
              ">
                <span style="width:7px; height:7px; border-radius:999px; background:#38BDF8; box-shadow:0 0 10px rgba(56,189,248,1);"></span>
                <span>High‑DPI export tuned for thermal & laser label printers.</span>
              </div>
              <div style="
                  padding:8px 10px;
                  border-radius:999px;
                  background:rgba(15,23,42,0.95);
                  border:1px solid rgba(148,163,184,0.45);
                  display:flex; align-items:center; gap:8px;
              ">
                <span style="width:7px; height:7px; border-radius:999px; background:#22C55E; box-shadow:0 0 10px rgba(34,197,94,1);"></span>
                <span>Odoo‑ready Code128 barcodes that scan perfectly first time.</span>
              </div>
            </div>
          </div>

          <!-- Right mini cards -->
          <div style="flex:0.9; min-width:210px; display:flex; flex-direction:column; gap:10px;">
            <div style="font-size:11px; text-transform:uppercase; letter-spacing:0.16em; color:#9CA3AF;">
              TUNED CONTROLS
            </div>
            <div style="display:flex; flex-direction:column; gap:8px; font-size:12px;">
              <div style="padding:10px; border-radius:12px; background:rgba(15,23,42,0.96); border:1px solid rgba(148,163,184,0.6);">
                <div style="font-size:11px; color:#9CA3AF;">LABEL CANVAS</div>
                <div style="font-size:13px; color:#E5E7EB;">
                  Width / height in millimetres for A4 sheets, rack strips, bin labels & pallet tags.
                </div>
              </div>
              <div style="padding:10px; border-radius:12px; background:rgba(15,23,42,0.96); border:1px solid rgba(148,163,184,0.45);">
                <div style="font-size:11px; color:#9CA3AF;">BARCODE LOOK</div>
                <div style="font-size:13px; color:#E5E7EB;">
                  Control bar height + thickness so every scanner in the building reads it clean.
                </div>
              </div>
              <div style="padding:10px; border-radius:12px; background:rgba(15,23,42,0.96); border:1px solid rgba(148,163,184,0.45);">
                <div style="font-size:11px; color:#9CA3AF;">PRINT QUALITY</div>
                <div style="font-size:13px; color:#E5E7EB;">
                  DPI slider for crisp lines on both economy and high‑end printers.
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
    """,
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

    # LOGO
    usable_w = rw - 8 * mm
    logo_section_w = usable_w * 0.50
    logo_x = rx + 4 * mm
    lh_logo = band_h * 0.99
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

    # TEXT
    text_start_x = logo_x + logo_section_w + 1 * mm
    max_tw = rx + rw - text_start_x - 3 * mm
    text_size = int(band_h * 1.0)
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
