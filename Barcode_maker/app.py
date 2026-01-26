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

# ===== PATH / LOGO SETTINGS =====
BASE_DIR = Path(__file__).resolve().parent
LOCAL_LOGO_PATH = BASE_DIR / "assets" / "logo.png"
GITHUB_LOGO_URL = (
    "https://raw.githubusercontent.com/"
    "sabeya143111-arch/Barcode_maker/main/Barcode_maker/assets/logo.png"
)

_logo_cache = {}


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

    # 1) Local logo
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

    # 2) GitHub fallback
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


# ===== SIMPLE PAGE CONFIG / HERO =====
st.set_page_config(page_title="Swag Barcode Maker", page_icon="🏷️", layout="wide")

st.title("SWAG BARCODE MAKER")
st.write(
    "Design premium warehouse location labels with logo + Code128 barcode and export as a high‑resolution PDF."
)

# Common controls in sidebar
with st.sidebar:
    st.header("Label settings (common)")
    c1, c2 = st.columns(2)
    label_width_mm = c1.number_input("Width (mm)", value=210.0)
    label_height_mm = c2.number_input("Height (mm)", value=60.0)
    underline_gap_mm = st.slider("Gap (mm)", 1.0, 10.0, 2.0)
    module_height = st.slider("Bar Height", 5, 40, 18)
    module_width = st.slider("Thickness", 0.2, 1.0, 0.45)
    dpi_value = st.slider("DPI", 300, 1200, 600, 100)


# ===== PDF BUILDER (SINGLE CODE) =====
def build_pdf(barcode_text: str) -> bytes:
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

    # BOTTOM BAND (LOGO + TEXT)
    band_y = m + 4 * mm
    band_h = line_y - band_y - 2 * mm

    usable_w = rw - 8 * mm
    logo_section_w = usable_w * 0.40   # thoda kam logo, zyada text space
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

    # ===== BIGGER, BOLD, CENTER TEXT =====
    text_start_x = logo_x + logo_section_w + 1 * mm
    max_tw = rx + rw - text_start_x - 3 * mm

    # bada starting size
    text_size = int(band_h * 1.2)
    text_size = min(text_size, 72)
    text_size = max(text_size, 26)

    c.setFont("Helvetica-Bold", text_size)
    tw = c.stringWidth(barcode_text, "Helvetica-Bold", text_size)

    # agar lamba code ho to hi chhota karo
    while tw > max_tw and text_size > 24:
        text_size -= 2
        c.setFont("Helvetica-Bold", text_size)
        tw = c.stringWidth(barcode_text, "Helvetica-Bold", text_size)

    text_y = band_y + band_h / 2 - text_size / 3
    text_cx = rx + rw / 2   # pure right box center

    c.setFillColor(HexColor("#FF0000"))   # red
    c.drawCentredString(text_cx, text_y, barcode_text)
    c.setFillColor(black)

    c.showPage()
    c.save()
    pdf_buf.seek(0)
    return pdf_buf.getvalue()


# ===== TABS =====
tab_single, tab_batch = st.tabs(["Single Label", "Batch Labels (Multi PDF ZIP)"])

# ---------- SINGLE LABEL TAB ----------
with tab_single:
    barcode_text_single = st.text_input("Location Code", value="W13-07-07-01-02")
    if st.button("👀 Generate Preview / PDF (Single)"):
        try:
            pdf_data = build_pdf(barcode_text_single)
            st.success("Success!")
            safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", barcode_text_single).strip("_")
            if not safe_name:
                safe_name = "label"
            st.download_button(
                "Download PDF",
                data=pdf_data,
                file_name=f"{safe_name}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Error: {e}")

# ---------- BATCH TAB ----------
with tab_batch:
    st.subheader("Paste / Upload multiple location codes")

    st.write("Example:")
    st.code(
        """W102/W102-07-03-01-01
W102/W102-07-03-01-02
W102/W102-07-03-01-03
...
W102/W102-07-03-10-04"""
    )

    col1, col2 = st.columns(2)

    with col1:
        text_input = st.text_area(
            "Paste location codes (one per line)",
            height=250,
            placeholder="W102/W102-07-03-01-01\nW102/W102-07-03-01-02\nW102/W102-07-03-01-03\n...",
        )

    with col2:
        uploaded_file = st.file_uploader(
            "OR upload CSV / Excel (codes in first column)",
            type=["csv", "xlsx", "xls"],
        )

    codes = []

    # From text area
    if text_input.strip():
        for line in text_input.splitlines():
            val = line.strip()
            if val:
                codes.append(val)

    # From uploaded file
    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded_file, header=None)
            else:
                df = pd.read_excel(uploaded_file, header=None)
            file_codes = df.iloc[:, 0].dropna().astype(str).str.strip().tolist()
            codes.extend(file_codes)
        except Exception as e:
            st.error(f"File read error: {e}")

    # Remove duplicates but keep order
    seen = set()
    unique_codes = []
    for ccode in codes:
        if ccode not in seen:
            seen.add(ccode)
            unique_codes.append(ccode)

    st.write(f"Total unique codes detected: **{len(unique_codes)}**")

    if unique_codes:
        st.write("First few codes:")
        st.write(unique_codes[:5])

    generate_zip_btn = st.button("🚀 Generate ZIP (All PDFs)")

    if generate_zip_btn:
        if not unique_codes:
            st.warning("Please paste or upload at least one location code.")
        else:
            try:
                progress = st.progress(0)
                status = st.empty()

                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    total = len(unique_codes)
                    for i, code in enumerate(unique_codes, start=1):
                        status.text(f"Generating {i}/{total}: {code}")
                        pdf_bytes = build_pdf(code)
                        safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", code).strip("_")
                        if not safe_name:
                            safe_name = f"label_{i}"
                        zf.writestr(f"{safe_name}.pdf", pdf_bytes)
                        progress.progress(i / total)

                zip_buf.seek(0)
                st.success("All labels generated!")

                st.download_button(
                    "Download ZIP",
                    data=zip_buf.getvalue(),
                    file_name="barcode_labels.zip",
                    mime="application/zip",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Batch error: {e}")
