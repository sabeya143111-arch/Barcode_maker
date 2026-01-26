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
import re
import zipfile
import pandas as pd
from datetime import datetime


# ===== PATH / LOGO SETTINGS =====
BASE_DIR = Path(__file__).resolve().parent
LOCAL_LOGO_PATH = BASE_DIR / "assets" / "logo.png"
GITHUB_LOGO_URL = (
    "https://raw.githubusercontent.com/"
    "sabeya143111-arch/Barcode_maker/main/Barcode_maker/assets/logo.png"
)

_logo_cache = {}


# ===== GLOBAL LUXURY THEME (CSS) =====
def load_css():
    luxury_css = """
    <style>
    /* Page background */
    .stApp {
        background: radial-gradient(circle at top left, #1c1f2b, #050609);
        color: #ffffff;
        font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .block-container {
        max-width: 1200px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    section.main > div {
        padding-top: 1rem;
    }

    .lux-header {
        padding: 0.7rem 1.5rem 1.5rem 1.5rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #151824 0%, #202636 50%, #3c2b18 100%);
        box-shadow:
            0 20px 45px rgba(0, 0, 0, 0.75),
            0 0 0 1px rgba(255, 215, 0, 0.1);
        border: 1px solid rgba(255, 215, 0, 0.25);
        position: relative;
        overflow: hidden;
    }

    .lux-header::before {
        content: "";
        position: absolute;
        top: -40%;
        left: -10%;
        width: 50%;
        height: 200%;
        background: linear-gradient(
            120deg,
            rgba(255, 215, 0, 0.0) 0%,
            rgba(255, 215, 0, 0.4) 40%,
            rgba(255, 215, 0, 0.0) 80%
        );
        transform: translateX(-120%) rotate(8deg);
        animation: lux-sweep 9s infinite;
        pointer-events: none;
    }

    @keyframes lux-sweep {
        0%   { transform: translateX(-120%) rotate(8deg); opacity: 0; }
        18%  { opacity: 1; }
        40%  { transform: translateX(130%) rotate(8deg); opacity: 0; }
        100% { transform: translateX(130%) rotate(8deg); opacity: 0; }
    }

    .lux-title {
        font-size: 2.15rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #ffffff;
        text-shadow: 0 0 16px rgba(0, 0, 0, 0.85);
    }

    .lux-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        border: 1px solid rgba(255, 215, 0, 0.5);
        background: radial-gradient(circle at top left, rgba(255, 215, 0, 0.18), transparent 65%);
        font-size: 0.7rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #ffffff;
    }

    .lux-subtitle {
        margin-top: 0.5rem;
        font-size: 0.9rem;
        color: #ffffff;
        max-width: 560px;
    }

    .lux-chip-row {
        margin-top: 0.75rem;
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .lux-chip {
        font-size: 0.7rem;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        background: rgba(7, 11, 25, 0.96);
        border: 1px solid rgba(134, 142, 160, 0.5);
        color: #ffffff;
    }

    button[data-baseweb="tab"] {
        border-radius: 999px !important;
        padding: 0.35rem 1.2rem !important;
        margin-right: 0.2rem;
        background: rgba(13, 17, 31, 0.92);
        color: #ffffff !important;
        border: 1px solid rgba(255, 215, 0, 0.15);
        transition: all 0.25s ease-out;
        font-size: 0.82rem;
    }

    button[data-baseweb="tab"]:hover {
        border-color: rgba(255, 215, 0, 0.5);
        box-shadow: 0 0 0 1px rgba(255, 215, 0, 0.35), 0 12px 28px rgba(0, 0, 0, 0.9);
        transform: translateY(-1px);
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background: radial-gradient(circle at top, #f1e2a0, #c9973f 55%, #362612 100%);
        color: #0b0c11 !important;
        font-weight: 600;
        box-shadow:
            0 0 0 1px rgba(255, 215, 0, 0.8),
            0 14px 30px rgba(0, 0, 0, 0.9);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #080914 0%, #090b12 35%, #050509 100%);
        border-right: 1px solid rgba(255, 215, 0, 0.14);
        box-shadow: 6px 0 25px rgba(0, 0, 0, 0.75);
        color: #ffffff;
    }

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: #ffffff;
    }

    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    textarea {
        background: rgba(10, 12, 22, 0.95) !important;
        color: #ffffff !important;
        border-radius: 999px !important;
        border: 1px solid rgba(255, 215, 0, 0.35) !important;
        box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.9);
    }

    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus {
        border-color: rgba(255, 215, 0, 0.9) !important;
        box-shadow:
            0 0 0 1px rgba(255, 215, 0, 0.9),
            0 0 0 3px rgba(255, 215, 0, 0.15);
    }

    textarea {
        border-radius: 14px !important;
        background: rgba(10, 12, 22, 0.94) !important;
        border: 1px solid rgba(255, 215, 0, 0.35) !important;
        color: #ffffff !important;
        width: 100% !important;
        white-space: pre-wrap !important;
        overflow-wrap: break-word !important;
    }

    .stSlider > div > div > div[data-baseweb="slider"] > div {
        background: rgba(47, 52, 72, 0.95) !important;
    }
    .stSlider [data-baseweb="slider"] div[role="slider"] {
        background: radial-gradient(circle at top, #ffe29b, #ffc000 55%, #a56a00 100%) !important;
        box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.9);
    }

    .stButton > button {
        border-radius: 999px;
        padding: 0.45rem 1.1rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        border: 1px solid rgba(255, 215, 0, 0.8);
        background: radial-gradient(circle at top, #ffe29b, #ffc000 40%, #8f6400 100%);
        color: #16130a;
        box-shadow:
            0 14px 32px rgba(0, 0, 0, 0.95),
            0 0 0 1px rgba(255, 215, 0, 0.8);
        transition: all 0.18s ease-out;
    }

    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow:
            0 18px 40px rgba(0, 0, 0, 1),
            0 0 0 1px rgba(255, 235, 170, 1);
        filter: brightness(1.03);
    }

    .stButton > button:active {
        transform: translateY(0px) scale(0.99);
        box-shadow:
            0 10px 24px rgba(0, 0, 0, 0.7),
            0 0 0 1px rgba(255, 215, 0, 0.8);
    }

    .stAlert {
        border-radius: 14px !important;
        border: 1px solid rgba(255, 215, 0, 0.35) !important;
        background: radial-gradient(circle at top left, rgba(255, 215, 0, 0.19), rgba(14, 18, 36, 0.96)) !important;
        color: #ffffff !important;
    }

    .stDataFrame, .stTable {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(255, 215, 0, 0.16);
        background: rgba(12, 14, 26, 0.98);
        color: #ffffff;
    }

    [data-testid="stWidgetLabel"] > label,
    [data-testid="stWidgetLabel"] p,
    label {
        color: #ffffff !important;
    }
    </style>
    """
    st.markdown(luxury_css, unsafe_allow_html=True)


def _crop_alpha(img: Image.Image) -> Image.Image:
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    bg = Image.new("RGBA", img.size, (0, 0, 0, 0))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        return img.crop(bbox)
    return img


def _make_square_rgba(img: Image.Image) -> Image.Image:
    img = _crop_alpha(img)
    side = max(img.width, img.height)
    canvas_img = Image.new("RGBA", (side, side), (255, 255, 255, 0))
    off_x = (side - img.width) // 2
    off_y = (side - img.height) // 2
    canvas_img.paste(img, (off_x, off_y), img)
    return canvas_img


def load_logo():
    if "img" in _logo_cache:
        return _logo_cache["img"], _logo_cache["ir"]

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


# ===== BARCODE IMAGE BUILDER (for preview) =====
def build_barcode_image(
    barcode_text,
    module_height,
    module_width,
    dpi_value,
):
    code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
    options = {
        "write_text": False,
        "dpi": dpi_value,
        "module_height": module_height,
        "module_width": module_width,
    }
    img = code128.render(options)
    return img


# ===== PDF BUILDER (Single Label) =====
def build_pdf(
    barcode_text,
    label_width_mm,
    label_height_mm,
    module_height,
    module_width,
    dpi_value,
    include_logo: bool = True,
    product_name: str = "",
    sku: str = "",
    footer_text: str = "",
    print_date: bool = False,
):
    logo_img, logo_ir = (None, None)
    if include_logo:
        logo_img, logo_ir = load_logo()
        if not logo_ir:
            include_logo = False

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

    # BOTTOM BAND (LOGO + TEXT)
    band_y = m + 8 * mm
    band_h = line_y - band_y - 4 * mm

    usable_w = rw - 8 * mm
    if include_logo and logo_img is not None:
        logo_section_w = usable_w * 0.40
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
    else:
        logo_section_w = 0
        logo_x = rx + 4 * mm

    # MAIN RED TEXT
    text_start_x = logo_x + logo_section_w + (1 * mm if include_logo else 0)
    max_tw = rx + rw - text_start_x - 3 * mm
    text_size = int(band_h * 1.05)
    text_size = min(text_size, 60)
    text_size = max(text_size, 22)
    c.setFont("Helvetica-Bold", text_size)
    tw = c.stringWidth(barcode_text, "Helvetica-Bold", text_size)
    while tw > max_tw and text_size > 18:
        text_size -= 2
        c.setFont("Helvetica-Bold", text_size)
        tw = c.stringWidth(barcode_text, "Helvetica-Bold", text_size)

    text_y = band_y + band_h / 2 - text_size / 3
    text_cx = rx + rw / 2
    c.setFillColor(HexColor("#FF0000"))
    c.drawCentredString(text_cx, text_y, barcode_text)
    c.setFillColor(black)

    # EXTRA SMALL TEXT (PRODUCT NAME + SKU)
    extra = " • ".join(x for x in [product_name.strip(), sku.strip()] if x)
    extra_y = text_y - text_size * 0.8
    if extra:
        small_font = 10
        c.setFont("Helvetica", small_font)
        c.setFillColor(black)
        c.drawCentredString(text_cx, extra_y, extra)

    # FOOTER TEXT + DATE SECTION
    footer_lines = []
    if footer_text.strip():
        footer_lines.append(footer_text.strip())
    if print_date:
        today_str = datetime.now().strftime("%Y-%m-%d")
        footer_lines.append(f"Printed: {today_str}")

    if footer_lines:
        footer_full = "   |   ".join(footer_lines)
        c.setFont("Helvetica", 7)
        c.setFillColor(black)
        c.drawRightString(rx + rw - 3 * mm, m + 2 * mm, footer_full)

    c.showPage()
    c.save()
    pdf_buf.seek(0)
    return pdf_buf.getvalue()


# ===== PAGE CONFIG =====
st.set_page_config(page_title="Swag Barcode Maker", page_icon="🏷️", layout="wide")

# Load global CSS theme
load_css()

# ===== SESSION STATE FOR PRESETS =====
if "presets" not in st.session_state:
    st.session_state["presets"] = {}
if "selected_preset" not in st.session_state:
    st.session_state["selected_preset"] = "None"


# ===== HEADER =====
st.markdown(
    """
    <div class="lux-header">
      <div class="lux-badge">
        <span>SWAG WAREHOUSE</span>
        <span>PREMIUM LABEL DESIGNER</span>
      </div>
      <div style="display:flex;justify-content:space-between;align-items:flex-end;gap:1rem;margin-top:0.4rem;">
        <div>
          <div class="lux-title">SWAG BARCODE MAKER</div>
          <div class="lux-subtitle">
            Design ultra‑clean warehouse labels with logo + Code128 barcode.
            Single or batch — export ready‑to‑print PDFs in one click.
          </div>
          <div class="lux-chip-row">
            <span class="lux-chip">Code128 · High‑DPI</span>
            <span class="lux-chip">Logo Branding Ready</span>
            <span class="lux-chip">Batch ZIP Export</span>
            <span class="lux-chip">Warehouse Locations</span>
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# ===== TABS =====
tab1, tab2 = st.tabs(["📋 Single Label", "📦 Batch Labels"])

# ===== SIDEBAR SETTINGS =====
with st.sidebar:
    st.header("Label Settings")

    preset = st.selectbox(
        "Preset size",
        ["Custom", "Small Shelf (80x40)", "Box (100x60)", "Pallet (210x60)"],
    )

    # defaults
    width_default = 210.0
    height_default = 60.0

    if preset == "Small Shelf (80x40)":
        width_default, height_default = 80.0, 40.0
    elif preset == "Box (100x60)":
        width_default, height_default = 100.0, 60.0
    elif preset == "Pallet (210x60)":
        width_default, height_default = 210.0, 60.0

    # APPLY SAVED PRESET IF ANY
    saved_presets_names = ["None"] + list(st.session_state["presets"].keys())
    selected_saved = st.selectbox(
        "My saved presets",
        saved_presets_names,
        index=saved_presets_names.index(st.session_state["selected_preset"])
        if st.session_state["selected_preset"] in saved_presets_names
        else 0,
    )

    if selected_saved != "None":
        st.session_state["selected_preset"] = selected_saved
        p = st.session_state["presets"][selected_saved]
        width_default = p["label_width_mm"]
        height_default = p["label_height_mm"]
        default_module_height = p["module_height"]
        default_module_width = p["module_width"]
        default_dpi = p["dpi_value"]
        default_logo = p["include_logo"]
    else:
        default_module_height = 18
        default_module_width = 0.45
        default_dpi = 600
        default_logo = True

    label_width_mm = st.number_input(
        "Width (mm)", value=width_default, min_value=50.0, max_value=500.0
    )
    label_height_mm = st.number_input(
        "Height (mm)", value=height_default, min_value=20.0, max_value=300.0
    )

    module_height = st.slider("Bar Height", 5, 40, default_module_height)
    module_width = st.slider("Thickness", 0.2, 1.0, float(default_module_width))
    dpi_value = st.slider("DPI", 300, 1200, default_dpi, 100)
    include_logo_global = st.checkbox("Include Logo on labels", value=default_logo)

    st.markdown("---")
    st.subheader("Branding / Footer")
    footer_text = st.text_input(
        "Footer text (e.g. SWAG WAREHOUSE – JEDDAH)",
        value="SWAG WAREHOUSE – JEDDAH",
    )
    print_date = st.checkbox("Print date on label", value=True)

    st.markdown("---")
    st.subheader("Save current settings as preset")
    new_preset_name = st.text_input("Preset name", value="")
    if st.button("💾 Save preset"):
        if new_preset_name.strip():
            st.session_state["presets"][new_preset_name.strip()] = {
                "label_width_mm": label_width_mm,
                "label_height_mm": label_height_mm,
                "module_height": module_height,
                "module_width": module_width,
                "dpi_value": dpi_value,
                "include_logo": include_logo_global,
            }
            st.session_state["selected_preset"] = new_preset_name.strip()
            st.success(f"Preset '{new_preset_name.strip()}' saved!")
        else:
            st.warning("Please enter a preset name before saving.")


# ===== HELPER: TEXT LENGTH SUGGESTION =====
def text_length_hint(barcode_text, module_width):
    length = len(barcode_text.strip())
    if not barcode_text.strip():
        return ""
    if length > 25 and module_width > 0.4:
        return "Text is long: consider using thinner bars (0.25–0.35) or bigger label width."
    if length > 35:
        return "Very long code detected: recommended to increase label width or split code visually."
    return ""


# ===== TAB 1: SINGLE =====
with tab1:
    st.subheader("Generate Single Barcode Label")

    barcode_text = st.text_input("Location Code", value="W102-07-03-01-01", key="single_code")
    product_name = st.text_input("Product Name (optional)", value="", key="single_product")
    sku = st.text_input("SKU (optional)", value="", key="single_sku")

    hint = text_length_hint(barcode_text, module_width)
    if hint:
        st.info(hint)

    # LIVE PREVIEW
    col_preview, col_actions = st.columns([1.2, 1])
    with col_preview:
        if barcode_text.strip():
            try:
                preview_img = build_barcode_image(
                    barcode_text,
                    module_height=module_height,
                    module_width=module_width,
                    dpi_value=dpi_value,
                )
                st.image(preview_img, caption="Live Barcode Preview", use_column_width=True)
            except Exception as e:
                st.warning(f"Preview not available: {e}")

    with col_actions:
        if st.button("👀 Generate PDF", key="preview_btn", use_container_width=True):
            try:
                with st.spinner("Creating premium label PDF…"):
                    pdf_data = build_pdf(
                        barcode_text,
                        label_width_mm,
                        label_height_mm,
                        module_height,
                        module_width,
                        dpi_value,
                        include_logo=include_logo_global,
                        product_name=product_name,
                        sku=sku,
                        footer_text=footer_text,
                        print_date=print_date,
                    )
                st.success("✅ PDF Generated!")

                safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", barcode_text).strip("_")
                if not safe_name:
                    safe_name = "label"

                st.download_button(
                    "📥 Download PDF",
                    data=pdf_data,
                    file_name=f"{safe_name}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ===== TAB 2: BATCH =====
with tab2:
    st.subheader("Generate Multiple Barcode Labels (Batch)")
    st.write("Paste location codes (one per line) or upload CSV/Excel file.")

    batch_product_name = st.text_input(
        "Batch Product Name (optional, same for all)", value="", key="batch_product"
    )
    batch_sku = st.text_input(
        "Batch SKU (optional, same for all)", value="", key="batch_sku"
    )
    prefix = st.text_input(
        "Optional prefix to add if missing (e.g. W102/)", value="", key="batch_prefix"
    )

    input_method = st.radio("Input Method:", ["📝 Text Area", "📄 CSV/Excel File"], horizontal=True)

    barcode_list = []
    df = None
    code_column = None
    product_column = None
    sku_column = None

    if input_method == "📝 Text Area":
        codes_text = st.text_area(
            "Enter location codes (one per line):",
            value="W102/W102-07-03-01-01\nW102/W102-07-03-01-02\nW102/W102-07-03-01-03",
            height=150,
            key="batch_codes",
        )
        if codes_text:
            for line in codes_text.split("\n"):
                code = line.strip()
                if not code:
                    continue
                if prefix and not code.startswith(prefix):
                    code = prefix + code
                barcode_list.append(code)
    else:
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel file", type=["csv", "xlsx", "xls"], key="file_upload"
        )
        if uploaded_file:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                st.write("Detected columns:", list(df.columns))

                code_column = st.selectbox(
                    "Select column for location codes",
                    df.columns,
                    index=0,
                )
                use_product_col = st.checkbox(
                    "Use column for Product Name (optional, overrides batch Product Name)",
                    value=False,
                )
                if use_product_col:
                    product_column = st.selectbox(
                        "Select Product Name column",
                        df.columns,
                        index=min(1, len(df.columns) - 1),
                    )

                use_sku_col = st.checkbox(
                    "Use column for SKU (optional, overrides batch SKU)",
                    value=False,
                )
                if use_sku_col:
                    sku_column = st.selectbox(
                        "Select SKU column",
                        df.columns,
                        index=min(1, len(df.columns) - 1),
                    )

                # BUILD BARCODE LIST + optional row-wise product / sku
                per_row_products = []
                per_row_skus = []
                for _, row in df.iterrows():
                    code = str(row[code_column]).strip()
                    if not code:
                        continue
                    if prefix and not code.startswith(prefix):
                        code = prefix + code
                    barcode_list.append(code)

                    if product_column:
                        per_row_products.append(str(row[product_column]).strip())
                    else:
                        per_row_products.append("")

                    if sku_column:
                        per_row_skus.append(str(row[sku_column]).strip())
                    else:
                        per_row_skus.append("")

            except Exception as e:
                st.error(f"❌ Error reading file: {e}")
                df = None

    if barcode_list:
        st.info(f"📊 Total codes to generate: **{len(barcode_list)}**")

        if st.button("🚀 Generate ZIP (All PDFs)", use_container_width=True, key="generate_zip_btn"):
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for idx, code in enumerate(barcode_list, 1):
                        status_text.text(f"⏳ Generating {idx}/{len(barcode_list)}: {code}")
                        try:
                            # row-wise product / sku if provided
                            row_product = batch_product_name
                            row_sku = batch_sku

                            if df is not None:
                                if product_column:
                                    row_product = per_row_products[idx - 1] or batch_product_name
                                if sku_column:
                                    row_sku = per_row_skus[idx - 1] or batch_sku

                            pdf_data = build_pdf(
                                code,
                                label_width_mm,
                                label_height_mm,
                                module_height,
                                module_width,
                                dpi_value,
                                include_logo=include_logo_global,
                                product_name=row_product,
                                sku=row_sku,
                                footer_text=footer_text,
                                print_date=print_date,
                            )
                            safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", code).strip("_")
                            if not safe_name:
                                safe_name = f"label_{idx}"
                            zip_file.writestr(f"{safe_name}.pdf", pdf_data)
                        except Exception as e:
                            st.warning(f"⚠️ Skipped {code}: {e}")

                        progress_bar.progress(idx / len(barcode_list))

                zip_buffer.seek(0)
                status_text.empty()
                progress_bar.empty()
                st.success(f"✅ Successfully generated {len(barcode_list)} PDFs!")
                st.download_button(
                    "📦 Download ZIP",
                    data=zip_buffer.getvalue(),
                    file_name="barcode_labels.zip",
                    mime="application/zip",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"❌ Error generating ZIP: {e}")
    else:
        st.info("👆 Enter barcode codes above to get started")
