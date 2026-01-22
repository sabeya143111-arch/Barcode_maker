import streamlit as st
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.colors import black, Color
from reportlab.lib.utils import ImageReader
import io
import barcode
from barcode.writer import ImageWriter

st.set_page_config(page_title="Arrow + Barcode Label", page_icon="🎫")

st.title("Arrow + Barcode Label Maker")

logo_file = None   # yahan abhi logo nahi, sirf arrow + barcode bana rahe hain

barcode_text = st.text_input(
    "Barcode text daalo (jaise: W102-07-01-01-03)",
    value="W102-07-01-01-03"
)

label_width_mm = st.number_input("Label width (mm)", value=180.0)
label_height_mm = st.number_input("Label height (mm)", value=60.0)

if st.button("Generate Label"):

    if not barcode_text.strip():
        st.error("Barcode text khali hai.")
    else:
        try:
            # --------- Barcode image (no text) ----------
            bar_buf = io.BytesIO()
            code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
            render_opts = {"write_text": False}  # text hatane ke liye [web:19][web:20]
            code128.render(render_opts).save(bar_buf, format="PNG")
            bar_buf.seek(0)
            bar_img = Image.open(bar_buf).convert("RGBA")

            # --------- PDF canvas ----------
            lw = float(label_width_mm) * mm
            lh = float(label_height_mm) * mm

            pdf_buffer = io.BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=(lw, lh))

            # ---- Layout: left arrow block, right barcode block ----
            left_margin = 5 * mm
            right_margin = 5 * mm
            gap = 5 * mm

            arrow_block_w = lw * 0.30       # 30% width arrow ke liye
            arrow_block_h = lh - 10 * mm

            bar_area_x = left_margin + arrow_block_w + gap
            bar_area_w = lw - bar_area_x - right_margin

            # ---- Arrow shape (filled) ----
            arrow_x0 = left_margin
            arrow_y0 = (lh - arrow_block_h) / 2.0
            arrow_x1 = arrow_x0 + arrow_block_w
            arrow_y1 = arrow_y0 + arrow_block_h

            # Arrow ke relative points (simple house shape ↑)
            mid_x = (arrow_x0 + arrow_x1) / 2.0
            head_height = arrow_block_h * 0.4
            shaft_width = arrow_block_w * 0.35

            p = c.beginPath()
            # bottom center of shaft
            p.moveTo(mid_x - shaft_width / 2, arrow_y0)
            p.lineTo(mid_x + shaft_width / 2, arrow_y0)
            p.lineTo(mid_x + shaft_width / 2, arrow_y0 + arrow_block_h - head_height)
            p.lineTo(arrow_x1, arrow_y0 + arrow_block_h - head_height)
            p.lineTo(mid_x, arrow_y1)  # arrow tip
            p.lineTo(arrow_x0, arrow_y0 + arrow_block_h - head_height)
            p.lineTo(mid_x - shaft_width / 2, arrow_y0 + arrow_block_h - head_height)
            p.close()

            orange = Color(1, 0.5, 0.2)   # thoda light orange
            c.setFillColor(orange)
            c.setStrokeColor(orange)
            c.drawPath(p, stroke=1, fill=1)

            # ---- Barcode size ----
            bar_w = bar_area_w
            bar_ratio = bar_img.height / bar_img.width
            bar_h = bar_w * bar_ratio

            text_height = 10 * mm
            max_bar_height = lh - 20 * mm - text_height
            if bar_h > max_bar_height:
                scale = max_bar_height / bar_h
                bar_w *= scale
                bar_h *= scale

            bar_x = bar_area_x
            bar_y = (lh - bar_h) / 2.0 + text_height / 2.0

            # ---- Draw barcode ----
            bar_img_buf = io.BytesIO()
            bar_img.save(bar_img_buf, format="PNG")
            bar_img_buf.seek(0)

            c.drawImage(
                ImageReader(bar_img_buf),
                bar_x,
                bar_y,
                width=bar_w,
                height=bar_h,
                mask="auto",
            )

            # ---- Big text below barcode ----
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 20)
            text_y = bar_y - 6 * mm
            text_x_center = bar_x + bar_w / 2.0
            c.drawCentredString(text_x_center, text_y, barcode_text)  # [web:24][web:26]

            c.showPage()
            c.save()
            pdf_buffer.seek(0)
            pdf_bytes = pdf_buffer.getvalue()

            st.success("Label ready ho gaya ✅")
            st.download_button(
                label="Download Label PDF",
                data=pdf_bytes,
                file_name=f"arrow_label_{barcode_text}.pdf",
                mime="application/pdf",
            )

        except Exception as e:
            st.error(f"Error aaya: {e}")
