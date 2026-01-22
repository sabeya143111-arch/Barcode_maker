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


st.set_page_config(page_title="Warehouse Label", page_icon="🏷️")
st.title("🏷️ Warehouse Label Maker (Odoo Ready)")

# ===== INPUTS =====
barcode_text = st.text_input(
    "Location Code (jaise: W13-07-07-01-02)",
    value="W13-07-07-01-02",
)

col1, col2 = st.columns(2)
with col1:
    label_width_mm = st.number_input("Label width (mm)", value=210.0)
with col2:
    label_height_mm = st.number_input("Label height (mm)", value=60.0)

st.markdown("### 🎨 Customization")

c1, c2, c3 = st.columns(3)

with c1:
    text_font_size = st.slider(
        "Text font size", min_value=16, max_value=90, value=60, step=1
    )

with c2:
    logo_scale = st.slider(
        "Logo size (%)", min_value=20, max_value=80, value=45, step=5
    )

with c3:
    underline_gap_mm = st.slider(
        "Text–underline gap (mm)", min_value=1.0, max_value=10.0, value=3.0, step=0.5
    )

uploaded_logo = st.file_uploader(
    "Custom logo (PNG/JPG)", type=["png", "jpg", "jpeg"]
)

preview_btn = st.button("👀 Preview", use_container_width=True)
download_btn = st.button("⬇️ Generate & Download PDF", use_container_width=True)

def build_pdf(return_png_preview=False):
    if not barcode_text.strip():
        raise ValueError("Code likho.")

    # ---------- LOGO ----------
    logo_img, logo_ir = load_logo(uploaded_logo)

    # ---------- BARCODE ----------
    bbuf = io.BytesIO()
    code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
    writer_opts = {
        "write_text": False,
        "dpi": 600,
        "module_height": 18,
        "module_width": 0.45,
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

    # Outer border
    c.setStrokeColor(black)
    c.roundRect(left_x, left_y, left_w, left_h, radius)

    # Light grey background
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

    # Solid black arrow
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

    # ===== RIGHT: LOGO + BARCODE + TEXT =====
    right_x = left_x + left_w + 1 * mm
    right_w = lw - right_x - margin
    right_y = margin
    right_h = lh - 2 * margin

    c.setLineWidth(1.2)
    c.setStrokeColor(black)
    c.roundRect(right_x, right_y, right_w, right_h, 3 * mm)
    center_x = right_x + right_w / 2.0

    # ---- LOGO (center top) ----
    if logo_img and logo_ir:
        logo_area_h = right_h * 0.40
        ratio = logo_img.height / logo_img.width

        logo_h = logo_area_h * (logo_scale / 100.0)
        logo_w = logo_h / ratio

        max_logo_w = right_w * 0.45
        if logo_w > max_logo_w:
            logo_w = max_logo_w
            logo_h = logo_w * ratio

        logo_y = right_y + right_h - logo_h - 1.5 * mm
        logo_x = center_x - logo_w / 2.0

        c.drawImage(
            logo_ir,
            logo_x,
            logo_y,
            width=logo_w,
            height=logo_h,
            mask="auto",
        )

        top_line_y = logo_y - 2 * mm
        c.setLineWidth(2)
        c.line(
            right_x + 3 * mm,
            top_line_y,
            right_x + right_w - 3 * mm,
            top_line_y,
        )

        barcode_area_bottom = right_y + right_h * 0.40
        barcode_area_top = top_line_y - 2 * mm
    else:
        barcode_area_bottom = right_y + right_h * 0.25
        barcode_area_top = right_y + right_h - 4 * mm

    # ---- BARCODE ----
    barcode_area_h = barcode_area_top - barcode_area_bottom
    bar_w = right_w * 0.92
    bar_h = barcode_area_h * 0.70

    bar_x = center_x - bar_w / 2.0
    bar_y = barcode_area_bottom + (barcode_area_h - bar_h)

    c.drawImage(
        bar_ir,
        bar_x,
        bar_y,
        width=bar_w,
        height=bar_h,
        mask="auto",
    )

    # ---- UPPER TEXT LINE ----
    bottom_line_y = bar_y - 3.5 * mm
    c.setLineWidth(2)
    c.line(
        right_x + 3 * mm,
        bottom_line_y,
        right_x + right_w - 3 * mm,
        bottom_line_y,
    )

    # ==== TEXT BAND (do line ke beech) ====
    band_bottom_y = right_y + 3 * mm
    band_top_y = bottom_line_y - underline_gap_mm * mm
    text_center_y = (band_top_y + band_bottom_y) / 2.0

    # Lower underline line
    c.setLineWidth(2)
    c.line(
        right_x + 3 * mm,
        band_bottom_y,
        right_x + right_w - 3 * mm,
        band_bottom_y,
    )

    # ---- ORANGE BAND jisme text fit hoga ----
    band_margin_x = 4 * mm
    band_height = band_top_y - band_bottom_y

    c.setFillColor(HexColor("#FF7A1A"))
    c.roundRect(
        right_x + band_margin_x,
        band_bottom_y,
        right_w - 2 * band_margin_x,
        band_height,
        2 * mm,
        stroke=0,
        fill=1,
    )

    # ---- TEXT: band ke 90% height tak ----
    c.setFillColor(black)
    base_font = "Helvetica-Bold"

    max_width = right_w - 2 * band_margin_x - 2 * mm
    max_font_from_height = abs(band_height) * 0.90

    size = min(text_font_size, int(max_font_from_height))
    while size > 8:
        w = c.stringWidth(barcode_text, base_font, size)
        if w <= max_width:
            break
        size -= 1

    text_center_x = right_x + right_w / 2.0
    c.setFont(base_font, size)
    c.drawCentredString(text_center_x, text_center_y, barcode_text)

    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    if not return_png_preview:
        return pdf_buffer.getvalue()

    return pdf_buffer.getvalue()


# ===== HANDLERS =====
if preview_btn:
    try:
        pdf_bytes = build_pdf(return_png_preview=False)
        st.success("Preview (PDF) niche dikh raha hai. Zoom karke check kar.")
        st.download_button(
            "⬇️ Download this preview PDF",
            data=pdf_bytes,
            file_name=f"preview_{barcode_text}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Error: {e}")

if download_btn:
    try:
        pdf_bytes = build_pdf(return_png_preview=False)
        st.success("✅ Final PDF ready!")
        st.download_button(
            "⬇️ Download Final PDF",
            data=pdf_bytes,
            file_name=f"label_{barcode_text}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Error: {e}")
