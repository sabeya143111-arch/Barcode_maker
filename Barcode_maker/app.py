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
# Repo:
#  - Barcode_maker/
#      - Barcode_maker/app.py
#      - assets/logo.png
BASE_DIR = Path(__file__).resolve().parent.parent
LOCAL_LOGO_PATH = BASE_DIR / "assets" / "logo.png"

GITHUB_LOGO_URL = (
    "https://raw.githubusercontent.com/"
    "sabeya143111-arch/Barcode_maker/main/assets/logo.png"
)


def load_logo():
    """Logo load karega - local ya GitHub se."""
    # 1) Local assets/logo.png
    if LOCAL_LOGO_PATH.exists():
        try:
            img = Image.open(LOCAL_LOGO_PATH).convert("RGBA")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            return img, ImageReader(buf)
        except Exception as e:
            st.warning(f"Local logo error: {e}")

    # 2) GitHub raw se
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
    except Exception as e:
        st.warning(f"Logo load nahi hua: {e}")
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

if st.button("Generate Label", use_container_width=True):

    if not barcode_text.strip():
        st.error("Code likho.")
    else:
        try:
            # ---------- LOGO ----------
            logo_img, logo_ir = load_logo()
            if logo_img is None or logo_ir is None:
                st.info("Logo ke bina sirf barcode + text banega.")

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

            # ---------- CANVAS ----------
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

            c.setLineWidth(1.5)
            radius = 3 * mm
            c.roundRect(left_x, left_y, left_w, left_h, radius)

            main_col = HexColor("#111111")
            light_col = HexColor("#444444")

            c.setFillColor(light_col)
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
            top_y = left_y + left_h - 1.5 * mm
            bottom_y = left_y + 1.5 * mm

            head_h = left_h * 0.46
            shaft_w = left_w * 0.32

            p = c.beginPath()
            p.moveTo(mid_x - shaft_w / 2, bottom_y)
            p.lineTo(mid_x + shaft_w / 2, bottom_y)
            p.lineTo(mid_x + shaft_w / 2, bottom_y + (left_h - head_h) * 0.97)
            p.lineTo(left_x + left_w * 0.95, bottom_y + left_h - head_h)
            p.lineTo(mid_x, top_y)
            p.lineTo(left_x + left_w * 0.05, bottom_y + left_h - head_h)
            p.lineTo(mid_x - shaft_w / 2, bottom_y + (left_h - head_h) * 0.97)
            p.close()

            c.setFillColor(main_col)
            c.drawPath(p, stroke=0, fill=1)

            # ===== RIGHT: LOGO + BARCODE + TEXT =====
            right_x = left_x + left_w + 1 * mm
            right_w = lw - right_x - margin
            right_y = margin
            right_h = lh - 2 * margin

            c.setLineWidth(1.5)
            c.roundRect(right_x, right_y, right_w, right_h, 3 * mm)
            center_x = right_x + right_w / 2.0

            # ---- LOGO (extra bada) ----
            if logo_img and logo_ir:
                logo_area_h = right_h * 0.40   # bada area
                ratio = logo_img.height / logo_img.width
                logo_h = logo_area_h
                logo_w = logo_h / ratio
                max_logo_w = right_w * 0.45    # width bhi bada
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
                c.setStrokeColor(HexColor("#333333"))
                c.line(
                    right_x + 3 * mm,
                    top_line_y,
                    right_x + right_w - 3 * mm,
                    top_line_y,
                )

                barcode_area_bottom = right_y + right_h * 0.38
                barcode_area_top = top_line_y - 2 * mm
            else:
                barcode_area_bottom = right_y + right_h * 0.20
                barcode_area_top = right_y + right_h - 3 * mm

            # ---- BARCODE ----
            barcode_area_h = barcode_area_top - barcode_area_bottom
            bar_w = right_w * 0.90
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

            # ---- BOTTOM LINE ----
            bottom_line_y = bar_y - 2.5 * mm
            c.setLineWidth(2)
            c.line(
                right_x + 3 * mm,
                bottom_line_y,
                right_x + right_w - 3 * mm,
                bottom_line_y,
            )

            # ---- TEXT: FULL WIDTH ME FIT ----
            text_area_bottom = right_y + 4 * mm
            text_area_top = bottom_line_y - 2 * mm
            text_center_y = (text_area_bottom + text_area_top) / 2.0

            c.setFillColor(black)

            # font size choose karne ke liye ek chhota helper:
            # bada size try karo, jab tak width box se bahar na nikle
            max_width = right_w - 6 * mm  # thoda side margin
            base_font = "Helvetica-Bold"
            size = 36  # start big
            while size > 18:
                w = c.stringWidth(barcode_text, base_font, size)
                if w <= max_width:
                    break
                size -= 1

            c.setFont(base_font, size)
            c.drawCentredString(center_x, text_center_y, barcode_text)

            # ===== SAVE =====
            c.showPage()
            c.save()
            pdf_buffer.seek(0)
            pdf_bytes = pdf_buffer.getvalue()

            st.success("✅ Label ready! Text box me nicely fit + logo bada.")
            st.download_button(
                "⬇️ Download PDF",
                data=pdf_bytes,
                file_name=f"label_{barcode_text}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        except Exception as e:
            st.error(f"Error: {e}")
