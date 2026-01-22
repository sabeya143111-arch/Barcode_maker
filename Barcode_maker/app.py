import streamlit as st
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.colors import black, Color
from reportlab.lib.utils import ImageReader
import io
import barcode
from barcode.writer import ImageWriter

st.set_page_config(page_title="Perfect Warehouse Label", page_icon="🎫")

st.title("Perfect Warehouse Label Maker")

logo_file = st.file_uploader(
    "Company Logo upload karo (PNG / JPG)",
    type=["png", "jpg", "jpeg"]
)

barcode_text = st.text_input(
    "Product Code (jaise: W102-07-01-01-03)",
    value="W102-07-01-01-03"
)

label_width_mm = st.number_input("Label width (mm)", value=210.0)
label_height_mm = st.number_input("Label height (mm)", value=80.0)

if st.button("Generate Label"):

    if logo_file is None:
        st.error("Pehle company logo upload karo.")
    elif not barcode_text.strip():
        st.error("Product code khali hai.")
    else:
        try:
            # --------- Logo load ----------
            logo_img = Image.open(logo_file).convert("RGBA")

            # --------- High‑DPI barcode ----------
            bar_buf = io.BytesIO()
            code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
            writer_opts = {
                "write_text": False,
                "dpi": 600,
                "module_height": 15,
            }
            code128.render(writer_opts).save(bar_buf, format="PNG")
            bar_buf.seek(0)
            bar_img = Image.open(bar_buf).convert("RGBA")

            # --------- PDF canvas ----------
            lw = float(label_width_mm) * mm
            lh = float(label_height_mm) * mm

            pdf_buffer = io.BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=(lw, lh))

            def pil_to_buf(img):
                b = io.BytesIO()
                img.save(b, format="PNG")
                b.seek(0)
                return b

            logo_buf = pil_to_buf(logo_img)
            bar_img_buf = pil_to_buf(bar_img)

            margin = 8 * mm

            # ===== LEFT: arrow =====
            arrow_block_w = lw * 0.32          # thoda wide
            arrow_block_h = lh - 2 * margin

            arrow_x = margin
            arrow_y = (lh - arrow_block_h) / 2.0

            mid_x = arrow_x + arrow_block_w / 2.0
            head_height = arrow_block_h * 0.5
            shaft_width_top = arrow_block_w * 0.26
            shaft_width_bottom = arrow_block_w * 0.38
            base_h = arrow_block_h * 0.18

            p = c.beginPath()
            p.moveTo(mid_x - shaft_width_bottom / 2, arrow_y)
            p.lineTo(mid_x + shaft_width_bottom / 2, arrow_y)
            p.lineTo(mid_x + shaft_width_top / 2, arrow_y + base_h)
            p.lineTo(mid_x + shaft_width_top / 2, arrow_y + arrow_block_h - head_height)
            p.lineTo(arrow_x + arrow_block_w, arrow_y + arrow_block_h - head_height)
            p.lineTo(mid_x, arrow_y + arrow_block_h)
            p.lineTo(arrow_x, arrow_y + arrow_block_h - head_height)
            p.lineTo(mid_x - shaft_width_top / 2, arrow_y + arrow_block_h - head_height)
            p.lineTo(mid_x - shaft_width_top / 2, arrow_y + base_h)
            p.close()

            orange = Color(1, 0.55, 0.20)
            c.setFillColor(orange)
            c.setStrokeColor(orange)
            c.drawPath(p, stroke=0, fill=1)

            # ===== RIGHT COLUMN (bilkul arrow ke paas) =====
            tiny_gap = 1 * mm               # almost no gap
            right_x = arrow_x + arrow_block_w + tiny_gap
            right_w = lw - right_x - margin

            col_top = lh - margin
            col_bottom = margin
            col_height = col_top - col_bottom

            logo_area_h = col_height * 0.30
            barcode_area_h = col_height * 0.40

            # ---- Logo ----
            logo_ratio = logo_img.height / logo_img.width
            logo_h = logo_area_h
            logo_w = logo_h / logo_ratio
            max_logo_w = right_w * 0.6        # center me compact
            if logo_w > max_logo_w:
                logo_w = max_logo_w
                logo_h = logo_w * logo_ratio

            logo_y = col_top - logo_h
            logo_x = right_x + (right_w - logo_w) / 2.0

            c.drawImage(
                ImageReader(logo_buf),
                logo_x,
                logo_y,
                width=logo_w,
                height=logo_h,
                mask="auto",
            )

            # ---- Common center line for underline + barcode + text ----
            center_x = right_x + right_w / 2.0

            # ---- Underline (logo se thoda wider, center) ----
            line_margin = 2 * mm
            line_y = logo_y - line_margin
            line_half = max(logo_w * 0.6, right_w * 0.35)

            c.setStrokeColor(orange)
            c.setLineWidth(2)
            c.line(center_x - line_half, line_y, center_x + line_half, line_y)

            # ---- Barcode (underline ke just niche, center) ----
            bar_w = line_half * 2 * 0.95      # underline ke just andar
            bar_ratio = bar_img.height / bar_img.width
            bar_h = bar_w * bar_ratio
            if bar_h > barcode_area_h:
                scale = barcode_area_h / bar_h
                bar_w *= scale
                bar_h *= scale

            bar_x = center_x - bar_w / 2.0
            bar_y = line_y - bar_h - 2 * mm

            c.drawImage(
                ImageReader(bar_img_buf),
                bar_x,
                bar_y,
                width=bar_w,
                height=bar_h,
                mask="auto",
            )

            # ---- Text (center, barcode ke thoda niche) ----
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 26)
            text_y = bar_y - 6 * mm
            c.drawCentredString(center_x, text_y, barcode_text)

            # ===== DONE =====
            c.showPage()
            c.save()
            pdf_buffer.seek(0)
            pdf_bytes = pdf_buffer.getvalue()

            st.success("Label ready ✅")
            st.download_button(
                label="Download Label PDF",
                data=pdf_bytes,
                file_name=f"label_{barcode_text}.pdf",
                mime="application/pdf",
            )

        except Exception as e:
            st.error(f"Error: {e}")
