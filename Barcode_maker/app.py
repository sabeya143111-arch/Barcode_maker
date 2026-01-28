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
import json
from collections import Counter
import random

try:
    import qrcode
except ImportError:
    qrcode = None


# ===== PATH / LOGO SETTINGS =====
BASE_DIR = Path(__file__).resolve().parent
LOCAL_LOGO_PATH = BASE_DIR / "assets" / "logo.png"
GITHUB_LOGO_URL = (
    "https://raw.githubusercontent.com/"
    "sabeya143111-arch/Barcode_maker/main/Barcode_maker/assets/logo.png"
)

_logo_cache = {}

# ===== WAREHOUSE PROFILES (ADVANCED FEATURE) =====
WAREHOUSE_PROFILES = {
    "JEDDAH_MAIN": {
        "footer": "SWAG WAREHOUSE - JEDDAH",
        "warehouse": "JEDDAH_MAIN",
        "zone": "",
        "dpi": 600,
        "preset": "Pallet (210x60)",
    },
    "RIYADH_DC": {
        "footer": "SWAG WAREHOUSE - RIYADH DC",
        "warehouse": "RIYADH_DC",
        "zone": "",
        "dpi": 600,
        "preset": "Box (100x60)",
    },
    "DAMMAM_HUB": {
        "footer": "SWAG WAREHOUSE - DAMMAM HUB",
        "warehouse": "DAMMAM_HUB",
        "zone": "",
        "dpi": 600,
        "preset": "Small Shelf (80x40)",
    },
    "Custom": {
        "footer": "SWAG WAREHOUSE",
        "warehouse": "WAREHOUSE",
        "zone": "",
        "dpi": 600,
        "preset": "Custom",
    },
}


# ===== GLOBAL THEMES (CSS) =====
def luxury_dark_css():
    return """
    <style>
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


def clean_light_css():
    return """
    <style>
    .stApp {
        background: #f5f7fb;
        color: #111827;
        font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
        box-shadow: 4px 0 18px rgba(0,0,0,0.04);
    }
    .block-container {
        max-width: 1200px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    .lux-header {
        padding: 0.7rem 1.5rem 1.5rem 1.5rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #ffffff 0%, #e5e7eb 50%, #d1d5db 100%);
        box-shadow: 0 16px 40px rgba(15,23,42,0.16);
        border: 1px solid rgba(148,163,184,0.6);
        position: relative;
        overflow: hidden;
    }
    .lux-title {
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #111827;
    }
    .lux-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        border: 1px solid rgba(59,130,246,0.4);
        background: rgba(59,130,246,0.06);
        font-size: 0.7rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #1f2937;
    }
    .lux-subtitle {
        margin-top: 0.5rem;
        font-size: 0.9rem;
        color: #374151;
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
        background: #ffffff;
        border: 1px solid #d1d5db;
        color: #111827;
    }
    .stButton > button {
        border-radius: 999px;
        padding: 0.45rem 1.1rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        border: 1px solid #2563eb;
        background: linear-gradient(135deg,#3b82f6,#2563eb);
        color: #ffffff;
        box-shadow: 0 12px 28px rgba(37,99,235,0.45);
    }
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    textarea {
        background: #ffffff !important;
        color: #111827 !important;
        border-radius: 10px !important;
        border: 1px solid #d1d5db !important;
    }
    </style>
    """


def load_css(theme: str):
    if theme == "Luxury Dark":
        css = luxury_dark_css()
    else:
        css = clean_light_css()
    st.markdown(css, unsafe_allow_html=True)


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


# ===== BARCODE HELPERS =====
BARCODE_TYPES = ["Code128", "EAN13", "EAN8", "UPCA", "QR"]


def validate_code(barcode_type: str, text: str) -> str:
    t = text.strip()
    if not t:
        return "Code is empty."
    if barcode_type == "Code128":
        return ""
    if barcode_type in ["EAN13", "EAN8", "UPCA"]:
        if not t.isdigit():
            return f"{barcode_type} requires numeric digits only."
        required = {"EAN13": 13, "EAN8": 8, "UPCA": 12}[barcode_type]
        if len(t) != required:
            return f"{barcode_type} must be exactly {required} digits."
        return ""
    if barcode_type == "QR":
        return ""
    return ""


def human_friendly_location(code: str) -> str:
    """Advanced feature: convert location code into human-friendly string."""
    parts = re.split(r"[-/]", code)
    # Example pattern: W102-07-03-01-01
    if len(parts) >= 5:
        return f"Rack {parts[0]} · Aisle {parts[1]} · Bay {parts[2]} · Shelf {parts[3]} · Bin {parts[4]}"
    return code


def build_barcode_image(
    barcode_type,
    barcode_text,
    module_height,
    module_width,
    dpi_value,
):
    if barcode_type == "QR":
        if qrcode is None:
            raise RuntimeError("qrcode library not installed, cannot generate QR.")
        qr = qrcode.QRCode(
            version=1,
            box_size=8,
            border=2,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
        )
        qr.add_data(barcode_text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        return img.convert("RGB")

    code_cls_map = {
        "Code128": "code128",
        "EAN13": "ean13",
        "EAN8": "ean8",
        "UPCA": "upca",
    }
    code_name = code_cls_map.get(barcode_type, "code128")
    code128 = barcode.get(code_name, barcode_text, writer=ImageWriter())
    options = {
        "write_text": False,
        "dpi": dpi_value,
        "module_height": module_height,
        "module_width": module_width,
    }
    img = code128.render(options)
    return img


def build_pdf(
    barcode_type,
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
    warehouse: str = "",
    zone: str = "",
    rotation: int = 0,
    show_human_location: bool = True,
):
    """rotation in degrees: 0, 90, 270."""
    logo_img, logo_ir = (None, None)
    if include_logo:
        logo_img, logo_ir = load_logo()
        if not logo_ir:
            include_logo = False

    # barcode image
    bbuf = io.BytesIO()
    img = build_barcode_image(
        barcode_type,
        barcode_text,
        module_height,
        module_width,
        dpi_value,
    )
    img.save(bbuf, format="PNG")
    bbuf.seek(0)
    bar_ir = ImageReader(bbuf)

    lw, lh = label_width_mm * mm, label_height_mm * mm
    if rotation in (90, 270):
        # swap width/height for rotated labels
        lw, lh = lh, lw

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

    # BARCODE / QR TOP
    bh = rh * 0.42 if barcode_type != "QR" else rh * 0.7
    bw = rw * (0.92 if barcode_type != "QR" else 0.65)
    c.drawImage(
        bar_ir,
        rx + (rw - bw) / 2,
        m + rh - bh - 3 * mm,
        width=bw,
        height=bh,
        mask="auto",
    )
    line_y = m + rh - bh - 6 * mm
    if barcode_type != "QR":
        c.setLineWidth(2)
        c.line(rx + 3 * mm, line_y, rx + rw - 3 * mm, line_y)
    else:
        line_y = m + rh - bh - 4 * mm

    # BOTTOM BAND (LOGO + TEXT)
    band_y = m + 8 * mm
    band_h = line_y - band_y - 4 * mm

    usable_w = rw - 8 * mm
    if include_logo and logo_img is not None:
        # allocate about ~32% of usable band width to the logo
        logo_section_w = usable_w * 0.32
        logo_x = rx + 4 * mm

        # propose a larger intended logo height (almost 2x), but enforce a strict cap
        lh_logo = band_h * 1.9
        # ensure logo stays inside the band visually (cap at 95% of band height)
        if lh_logo > band_h * 0.95:
            lh_logo = band_h * 0.95
        lw_logo = lh_logo
        ratio = logo_img.width / logo_img.height
        if lw_logo / lh_logo > ratio:
            lw_logo = lh_logo * ratio
        else:
            lh_logo = lw_logo / ratio
        # center logo inside its allocated section
        logo_y = band_y + (band_h - lh_logo) / 2
        logo_x = rx + 4 * mm + max(0, (logo_section_w - lw_logo) / 2)
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
    # slightly larger but balanced text sizing relative to band height
    text_size = int(band_h * 1.6)
    text_size = min(text_size, 80)
    text_size = max(text_size, 28)
    c.setFont("Helvetica-Bold", text_size)
    display_text = barcode_text if len(barcode_text) <= 40 else barcode_text[:37] + "..."
    tw = c.stringWidth(display_text, "Helvetica-Bold", text_size)
    while tw > max_tw and text_size > 18:
        text_size -= 2
        c.setFont("Helvetica-Bold", text_size)
        tw = c.stringWidth(display_text, "Helvetica-Bold", text_size)

    # position vertically centered in band (slightly adjusted offset)
    text_y = band_y + band_h / 2 - text_size / 2.8
    # center text in the remaining space AFTER the logo section
    text_cx = rx + logo_section_w + (rw - logo_section_w) / 2
    c.setFillColor(HexColor("#FF0000"))
    c.drawCentredString(text_cx, text_y, display_text)
    c.setFillColor(black)

    # EXTRA SMALL TEXT (PRODUCT NAME + SKU + WAREHOUSE + ZONE + HUMAN LOCATION)
    meta_bits = []
    if product_name.strip():
        meta_bits.append(product_name.strip())
    if sku.strip():
        meta_bits.append(sku.strip())
    if warehouse.strip():
        meta_bits.append(warehouse.strip())
    if zone.strip():
        meta_bits.append(zone.strip())
    if show_human_location:
        meta_bits.append(human_friendly_location(barcode_text))
    extra = "  •  ".join(meta_bits)
    extra_y = text_y - text_size * 0.85
    if extra:
        small_font = 9
        c.setFont("Helvetica", small_font)
        c.setFillColor(black)
        # Ensure minimum gap from red text
        min_gap = text_size * 0.15
        if (text_y - extra_y) < (text_size + min_gap):
            extra_y = text_y - text_size - min_gap
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

    # Rotation (advanced)
    if rotation in (90, 270):
        # rotate around center of page
        c.saveState()
        if rotation == 90:
            c.rotate(90)
            # translate to adjust
        elif rotation == 270:
            c.rotate(270)
        c.restoreState()

    c.showPage()
    c.save()
    pdf_buf.seek(0)
    return pdf_buf.getvalue()


# ===== PAGE CONFIG =====
st.set_page_config(page_title="Swag Barcode Maker", page_icon="🏷", layout="wide")

# ===== SESSION STATE =====
if "templates" not in st.session_state:
    st.session_state["templates"] = {}
if "selected_template" not in st.session_state:
    st.session_state["selected_template"] = "None"
if "theme" not in st.session_state:
    st.session_state["theme"] = "Luxury Dark"
if "csv_mappings" not in st.session_state:
    st.session_state["csv_mappings"] = {}
if "debug_mode" not in st.session_state:
    st.session_state["debug_mode"] = False

# ===== SIDEBAR TOP (GLOBAL) =====
with st.sidebar:
    st.header("App Mode & Theme")
    mode = st.selectbox("Mode", ["Picker View", "Supervisor View"])
    theme = st.selectbox("Theme", ["Luxury Dark", "Clean Light"], index=0)
    st.session_state["theme"] = theme

    st.markdown("---")
    st.header("Warehouse Profile")
    profile_name = st.selectbox("Profile", list(WAREHOUSE_PROFILES.keys()), index=0)

# Load theme CSS
load_css(st.session_state["theme"])

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
            Design ultra clean warehouse labels with logo + multitype barcodes (Code128, EAN, QR).
            Single or batch a export ready to print PDFs & logs in one click.
          </div>
          <div class="lux-chip-row">
            <span class="lux-chip">Code128 · EAN · QR</span>
            <span class="lux-chip">Logo Branding & Footer</span>
            <span class="lux-chip">Batch ZIP & Logs</span>
            <span class="lux-chip">Warehouse Zones</span>
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

# ===== SIDEBAR SETTINGS (DETAIL) =====
with st.sidebar:
    st.markdown("---")
    st.header("Label Settings")

    barcode_type = st.selectbox("Barcode type", BARCODE_TYPES)

    # profile defaults
    prof = WAREHOUSE_PROFILES.get(profile_name, WAREHOUSE_PROFILES["Custom"])

    preset = st.selectbox(
        "Preset size",
        ["Custom", "Small Shelf (80x40)", "Box (100x60)", "Pallet (210x60)"],
        index=["Custom", "Small Shelf (80x40)", "Box (100x60)", "Pallet (210x60)"].index(
            prof.get("preset", "Custom")
        ),
    )

    width_default = 210.0
    height_default = 60.0
    if preset == "Small Shelf (80x40)":
        width_default, height_default = 80.0, 40.0
    elif preset == "Box (100x60)":
        width_default, height_default = 100.0, 60.0
    elif preset == "Pallet (210x60)":
        width_default, height_default = 210.0, 60.0

    # APPLY TEMPLATE IF ANY
    template_names = ["None"] + list(st.session_state["templates"].keys())
    selected_template = st.selectbox(
        "Template",
        template_names,
        index=template_names.index(st.session_state["selected_template"])
        if st.session_state["selected_template"] in template_names
        else 0,
    )

    if selected_template != "None":
        st.session_state["selected_template"] = selected_template
        tpl = st.session_state["templates"][selected_template]
        width_default = tpl["label_width_mm"]
        height_default = tpl["label_height_mm"]
        default_module_height = tpl["module_height"]
        default_module_width = tpl["module_width"]
        default_dpi = tpl["dpi_value"]
        default_logo = tpl["include_logo"]
        barcode_type = tpl["barcode_type"]
        footer_default = tpl.get("footer_text", prof["footer"])
        date_default = tpl.get("print_date", True)
        warehouse_default = tpl.get("warehouse", prof["warehouse"])
        zone_default = tpl.get("zone", prof["zone"])
    else:
        default_module_height = 18
        default_module_width = 0.45
        default_dpi = prof.get("dpi", 600)
        default_logo = True
        footer_default = prof["footer"]
        date_default = True
        warehouse_default = prof["warehouse"]
        zone_default = prof["zone"]

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

    rotation = st.selectbox("Label rotation", [0, 90, 270], index=0)
    show_human_location = st.checkbox("Show human-friendly location text", value=True)

    st.markdown("---")
    st.header("Warehouse context")
    warehouse = st.text_input("Warehouse", value=warehouse_default)
    zone = st.text_input("Zone / Aisle", value=zone_default)

    st.markdown("---")
    st.header("Branding / Footer")
    footer_text = st.text_input(
        "Footer text", value=footer_default
    )
    print_date = st.checkbox("Print date on label", value=date_default)

    st.markdown("---")
    st.header("Templates")
    new_tpl_name = st.text_input("Template name", value="")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("💾 Save / Update template"):
            if new_tpl_name.strip():
                st.session_state["templates"][new_tpl_name.strip()] = {
                    "label_width_mm": label_width_mm,
                    "label_height_mm": label_height_mm,
                    "module_height": module_height,
                    "module_width": module_width,
                    "dpi_value": dpi_value,
                    "include_logo": include_logo_global,
                    "barcode_type": barcode_type,
                    "footer_text": footer_text,
                    "print_date": print_date,
                    "warehouse": warehouse,
                    "zone": zone,
                }
                st.session_state["selected_template"] = new_tpl_name.strip()
                st.success(f"Template '{new_tpl_name.strip()}' saved/updated!")
            else:
                st.warning("Enter a template name first.")
    with col_t2:
        if st.button("🗑️ Delete selected template"):
            if selected_template != "None":
                st.session_state["templates"].pop(selected_template, None)
                st.session_state["selected_template"] = "None"
                st.success(f"Template '{selected_template}' deleted.")
            else:
                st.warning("No template selected.")

    st.markdown("---")
    st.header("Batch ZIP Settings")
    max_labels_per_zip = st.number_input(
        "Max labels per ZIP chunk", min_value=100, max_value=5000, value=1000, step=100
    )
    skip_duplicates = st.checkbox("Skip duplicate codes in batch", value=True)
    split_zip_by_warehouse = st.checkbox("Split ZIP by warehouse (if available)", value=False)

    st.markdown("---")
    st.header("Config Import / Export")
    if st.button("⬇️ Export config"):
        cfg = {
            "templates": st.session_state["templates"],
            "selected_template": st.session_state["selected_template"],
            "theme": st.session_state["theme"],
            "csv_mappings": st.session_state["csv_mappings"],
        }
        cfg_bytes = json.dumps(cfg, indent=2).encode("utf-8")
        st.download_button(
            "Download config.json",
            data=cfg_bytes,
            file_name="swag_barcode_config.json",
            mime="application/json",
        )

    cfg_file = st.file_uploader("Import config.json", type=["json"], key="cfg_upload")
    if cfg_file is not None:
        try:
            cfg_data = json.load(cfg_file)
            st.session_state["templates"] = cfg_data.get("templates", {})
            st.session_state["selected_template"] = cfg_data.get(
                "selected_template", "None"
            )
            st.session_state["theme"] = cfg_data.get("theme", "Luxury Dark")
            st.session_state["csv_mappings"] = cfg_data.get("csv_mappings", {})
            st.success("Config imported. Refresh page to fully apply theme.")
        except Exception as e:
            st.error(f"Config import error: {e}")

    st.markdown("---")
    st.header("Advanced / Debug")
    st.session_state["debug_mode"] = st.checkbox("Enable debug mode", value=False)


def text_length_hint(barcode_text, module_width):
    length = len(barcode_text.strip())
    if not barcode_text.strip():
        return ""
    if length > 25 and module_width > 0.4:
        return "Text is long: consider thinner bars (0.25-0.35) or larger label width."
    if length > 35:
        return "Very long code: increase label width or visually split code."
    return ""


# ===== TAB 1: SINGLE =====
with tab1:
    st.subheader("Generate Single Barcode Label")

    if mode == "Picker View":
        barcode_text = st.text_input("Location Code", value="W102-07-03-01-01", key="single_code")
        product_name = ""
        sku = ""
    else:
        barcode_text = st.text_input("Location Code", value="W102-07-03-01-01", key="single_code")
        product_name = st.text_input("Product Name (optional)", value="", key="single_product")
        sku = st.text_input("SKU (optional)", value="", key="single_sku")

    # Auto QR fallback toggle
    auto_qr_fallback = st.checkbox("Auto switch to QR if Code128 invalid", value=True)

    error_msg = validate_code(barcode_type, barcode_text)
    if error_msg and auto_qr_fallback and barcode_type == "Code128":
        # Switch to QR automatically
        barcode_type = "QR"
        error_msg = ""

    if error_msg:
        st.error(error_msg)
    hint = text_length_hint(barcode_text, module_width)
    if hint and not error_msg:
        st.info(hint)

    col_preview, col_actions = st.columns([1.2, 1])
    with col_preview:
        if barcode_text.strip() and not error_msg:
            try:
                preview_img = build_barcode_image(
                    barcode_type,
                    barcode_text,
                    module_height=module_height,
                    module_width=module_width,
                    dpi_value=dpi_value,
                )
                st.image(preview_img, caption=f"Live {barcode_type} Preview", use_column_width=True)
            except Exception as e:
                st.warning(f"Preview not available: {e}")

    with col_actions:
        if st.button("👀 Generate PDF", key="preview_btn", use_container_width=True, disabled=bool(error_msg)):
            try:
                with st.spinner("Creating premium label PDF..."):
                    pdf_data = build_pdf(
                        barcode_type,
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
                        warehouse=warehouse,
                        zone=zone,
                        rotation=rotation,
                        show_human_location=show_human_location,
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

    if mode == "Picker View":
        batch_product_name = ""
        batch_sku = ""
    else:
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
    per_row_products = []
    per_row_skus = []
    per_row_wh = []
    per_row_zone = []
    code_column = None
    product_column = None
    sku_column = None
    wh_column = None
    zone_column = None

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
                per_row_products.append("")
                per_row_skus.append("")
                per_row_wh.append("")
                per_row_zone.append("")
    else:
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel file", type=["csv", "xlsx", "xls"], key="file_upload"
        )
        mapping_name = st.text_input("Mapping preset name (optional)", value="default")
        if uploaded_file:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                st.write("Detected columns:", list(df.columns))

                saved_map = st.session_state["csv_mappings"].get(mapping_name, {})

                code_column = st.selectbox(
                    "Select column for location codes",
                    df.columns,
                    index=saved_map.get("code_idx", 0),
                )

                use_product_col = st.checkbox(
                    "Use column for Product Name", value=saved_map.get("use_product_col", False)
                )
                if use_product_col:
                    product_column = st.selectbox(
                        "Select Product Name column",
                        df.columns,
                        index=saved_map.get("product_idx", min(1, len(df.columns) - 1)),
                    )

                use_sku_col = st.checkbox(
                    "Use column for SKU", value=saved_map.get("use_sku_col", False)
                )
                if use_sku_col:
                    sku_column = st.selectbox(
                        "Select SKU column",
                        df.columns,
                        index=saved_map.get("sku_idx", min(1, len(df.columns) - 1)),
                    )

                use_wh_col = st.checkbox(
                    "Use column for Warehouse", value=saved_map.get("use_wh_col", False)
                )
                if use_wh_col:
                    wh_column = st.selectbox(
                        "Select Warehouse column",
                        df.columns,
                        index=saved_map.get("wh_idx", min(1, len(df.columns) - 1)),
                    )

                use_zone_col = st.checkbox(
                    "Use column for Zone / Aisle", value=saved_map.get("use_zone_col", False)
                )
                if use_zone_col:
                    zone_column = st.selectbox(
                        "Select Zone column",
                        df.columns,
                        index=saved_map.get("zone_idx", min(1, len(df.columns) - 1)),
                    )

                if st.button("💾 Save mapping preset"):
                    st.session_state["csv_mappings"][mapping_name] = {
                        "code_idx": list(df.columns).index(code_column),
                        "use_product_col": use_product_col,
                        "product_idx": list(df.columns).index(product_column) if product_column else 0,
                        "use_sku_col": use_sku_col,
                        "sku_idx": list(df.columns).index(sku_column) if sku_column else 0,
                        "use_wh_col": use_wh_col,
                        "wh_idx": list(df.columns).index(wh_column) if wh_column else 0,
                        "use_zone_col": use_zone_col,
                        "zone_idx": list(df.columns).index(zone_column) if zone_column else 0,
                    }
                    st.success(f"Mapping preset '{mapping_name}' saved.")

                for _, row in df.iterrows():
                    code = str(row[code_column]).strip()
                    if not code:
                        continue
                    if prefix and not code.startswith(prefix):
                        code = prefix + code
                    barcode_list.append(code)

                    per_row_products.append(str(row[product_column]).strip() if product_column else "")
                    per_row_skus.append(str(row[sku_column]).strip() if sku_column else "")
                    per_row_wh.append(str(row[wh_column]).strip() if wh_column else "")
                    per_row_zone.append(str(row[zone_column]).strip() if zone_column else "")

                st.markdown("**CSV preview (first 10 rows):**")
                st.dataframe(df.head(10))

            except Exception as e:
                st.error(f"❌ Error reading file: {e}")
                df = None

    st.markdown("---")
    st.subheader("CSV Template Helper")
    if st.button("⬇️ Download CSV Template"):
        sample = pd.DataFrame(
            {
                "code": ["W102-07-03-01-01", "W102-07-03-01-02"],
                "product_name": ["T-SHIRT BLACK", "T-SHIRT WHITE"],
                "sku": ["TSH-BLK-S", "TSH-WHT-M"],
                "warehouse": ["JEDDAH_MAIN", "JEDDAH_MAIN"],
                "zone": ["A1", "A1"],
            }
        )
        csv_bytes = sample.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download sample_template.csv",
            data=csv_bytes,
            file_name="barcode_template_sample.csv",
            mime="text/csv",
        )

    # Duplicate detection (advanced)
    duplicates = []
    if barcode_list:
        counts = Counter(barcode_list)
        duplicates = [c for c, n in counts.items() if n > 1]

    invalid_codes = []
    valid_codes = []
    if barcode_list:
        for code in barcode_list:
            err = validate_code(barcode_type, code)
            if err:
                invalid_codes.append((code, err))
            else:
                valid_codes.append(code)

    if barcode_list:
        st.info(f"📊 Total codes input: **{len(barcode_list)}**")
        st.write(f"✅ Valid for {barcode_type}: {len(valid_codes)}")
        st.write(f"⚠️ Invalid: {len(invalid_codes)}")
        st.write(f"📋 Duplicates detected: {len(duplicates)}")
        if invalid_codes:
            with st.expander("View invalid codes"):
                for code, msg in invalid_codes:
                    st.write(f"- `{code}` → {msg}")
        if duplicates:
            with st.expander("View duplicate codes"):
                for code in duplicates:
                    st.write(f"- `{code}` (count: {counts[code]})")

    log_records = []

    # helper to flush ZIP buffers
    def flush_zip_state(current_zip, current_zip_file, zip_buffers, zip_index, current_count, zip_label_suffix=""):
        current_zip_file.close()
        current_zip.seek(0)
        zip_buffers.append((zip_index, current_zip.getvalue(), zip_label_suffix))
        zip_index += 1
        current_zip = io.BytesIO()
        current_zip_file = zipfile.ZipFile(current_zip, "w", zipfile.ZIP_DEFLATED)
        current_count = 0
        return current_zip, current_zip_file, zip_buffers, zip_index, current_count

    # Random sample test print (advanced)
    if barcode_list and st.button("🧪 Generate random sample of 5 labels for test"):
        sample_codes = random.sample(barcode_list, min(5, len(barcode_list)))
        st.write("Random sample codes:", sample_codes)
        for code in sample_codes:
            try:
                pdf_data = build_pdf(
                    barcode_type,
                    code,
                    label_width_mm,
                    label_height_mm,
                    module_height,
                    module_width,
                    dpi_value,
                    include_logo=include_logo_global,
                    product_name=batch_product_name,
                    sku=batch_sku,
                    footer_text=footer_text,
                    print_date=print_date,
                    warehouse=warehouse,
                    zone=zone,
                    rotation=rotation,
                    show_human_location=show_human_location,
                )
                safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", code).strip("_") or "sample"
                st.download_button(
                    f"Download sample {safe_name}.pdf",
                    data=pdf_data,
                    file_name=f"sample_{safe_name}.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.warning(f"Sample failed for {code}: {e}")

    if barcode_list and valid_codes:
        if st.button("🚀 Generate ZIP (All PDFs)", use_container_width=True, key="generate_zip_btn"):
            try:
                # Apply duplicate skipping if selected
                if skip_duplicates:
                    seen = set()
                    filtered_barcodes = []
                    for c in barcode_list:
                        if c not in seen:
                            seen.add(c)
                            filtered_barcodes.append(c)
                    barcode_list_to_use = filtered_barcodes
                else:
                    barcode_list_to_use = barcode_list

                total = len(barcode_list_to_use)
                progress_bar = st.progress(0)
                status_text = st.empty()

                zip_buffers = []
                current_zip = io.BytesIO()
                current_zip_file = zipfile.ZipFile(current_zip, "w", zipfile.ZIP_DEFLATED)
                current_count = 0
                zip_index = 1

                # optional split by warehouse (multi ZIPs logically grouped)
                current_zip_label = warehouse if split_zip_by_warehouse else ""

                for idx, code in enumerate(barcode_list_to_use, 1):
                    err = validate_code(barcode_type, code)
                    if err:
                        log_records.append(
                            {
                                "code": code,
                                "status": "invalid",
                                "error": err,
                                "warehouse": warehouse,
                                "zone": zone,
                            }
                        )
                        status_text.text(f"⚠️ Skipped invalid {idx}/{total}: {code}")
                        progress_bar.progress(idx / total)
                        continue

                    status_text.text(f"⏳ Generating {idx}/{total}: {code}")
                    try:
                        # use index on original arrays safely
                        row_idx = min(idx - 1, len(per_row_products) - 1)
                        row_product = batch_product_name
                        row_sku = batch_sku
                        row_wh = warehouse
                        row_zone = zone

                        if df is not None and len(per_row_products) == len(barcode_list):
                            # If from CSV, align via same index as original barcode_list (best-effort)
                            row_idx = barcode_list.index(code)
                        if df is not None:
                            if product_column:
                                val = per_row_products[row_idx]
                                row_product = val or batch_product_name
                            if sku_column:
                                val = per_row_skus[row_idx]
                                row_sku = val or batch_sku
                            if wh_column:
                                val = per_row_wh[row_idx]
                                row_wh = val or warehouse
                            if zone_column:
                                val = per_row_zone[row_idx]
                                row_zone = val or zone

                        pdf_data = build_pdf(
                            barcode_type,
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
                            warehouse=row_wh,
                            zone=row_zone,
                            rotation=rotation,
                            show_human_location=show_human_location,
                        )
                        safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", code).strip("_")
                        if not safe_name:
                            safe_name = f"label_{idx}"
                        current_zip_file.writestr(f"{safe_name}.pdf", pdf_data)
                        current_count += 1

                        log_records.append(
                            {
                                "code": code,
                                "status": "ok",
                                "error": "",
                                "warehouse": row_wh,
                                "zone": row_zone,
                            }
                        )

                        if current_count >= max_labels_per_zip:
                            suffix = current_zip_label
                            current_zip, current_zip_file, zip_buffers, zip_index, current_count = flush_zip_state(
                                current_zip, current_zip_file, zip_buffers, zip_index, current_count, suffix
                            )

                    except Exception as e:
                        log_records.append(
                            {
                                "code": code,
                                "status": "error",
                                "error": str(e),
                                "warehouse": warehouse,
                                "zone": zone,
                            }
                        )
                        st.warning(f"⚠️ Skipped {code}: {e}")

                    progress_bar.progress(idx / total)

                if current_count > 0:
                    suffix = current_zip_label
                    current_zip, current_zip_file, zip_buffers, zip_index, current_count = flush_zip_state(
                        current_zip, current_zip_file, zip_buffers, zip_index, current_count, suffix
                    )

                status_text.empty()
                progress_bar.empty()

                ok_count = sum(1 for r in log_records if r["status"] == "ok")
                invalid_count = sum(1 for r in log_records if r["status"] == "invalid")
                error_count = sum(1 for r in log_records if r["status"] == "error")

                st.success(
                    f"✅ Successfully processed {total} codes. "
                    f"Valid PDFs generated for {ok_count} codes. "
                    f"Invalid: {invalid_count}, Errors: {error_count}."
                )

                # Batch summary (advanced)
                st.markdown("### Batch summary")
                summary_df = pd.DataFrame(
                    [
                        ["Total input codes", len(barcode_list)],
                        ["After duplicate filter", total],
                        ["Valid PDFs", ok_count],
                        ["Invalid codes", invalid_count],
                        ["Errors during generation", error_count],
                        ["Duplicates detected", len(duplicates)],
                    ],
                    columns=["Metric", "Value"],
                )
                st.table(summary_df)

                if log_records:
                    log_df = pd.DataFrame(log_records)
                    if "warehouse" in log_df.columns:
                        st.markdown("#### Output per warehouse")
                        wh_summary = log_df.groupby("warehouse")["code"].count().reset_index()
                        wh_summary.columns = ["Warehouse", "Labels"]
                        st.table(wh_summary)

                # Download buttons (with grouping info)
                only_ok = st.checkbox("Only download ZIPs (log separate)", value=True)
                for idx_zip, data, suffix in zip_buffers:
                    label_suffix = f"_{suffix}" if suffix else ""
                    file_name = f"barcode_labels_part{idx_zip}{label_suffix}.zip"
                    st.download_button(
                        f"📦 Download ZIP part {idx_zip}{label_suffix}",
                        data=data,
                        file_name=file_name,
                        mime="application/zip",
                        use_container_width=True,
                    )

                if log_records:
                    st.markdown("---")
                    st.subheader("Batch log")
                    log_df = pd.DataFrame(log_records)
                    st.dataframe(log_df, use_container_width=True)
                    log_csv = log_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇️ Download log CSV (all statuses)",
                        data=log_csv,
                        file_name="barcode_batch_log.csv",
                        mime="text/csv",
                    )

            except Exception as e:
                st.error(f"❌ Error generating ZIPs: {e}")
    elif not barcode_list:
        st.info("👆 Enter or upload barcode codes above to get started")

# Debug info
if st.session_state["debug_mode"]:
    with st.expander("Debug info"):
        st.write("Session state:", st.session_state)
