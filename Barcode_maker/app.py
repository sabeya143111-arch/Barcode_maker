import streamlit as st
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.colors import black, Color
from reportlab.lib.utils import ImageReader
import io
import barcode
from barcode.writer import ImageWriter

st.set_page_config(page_title="Arrow + Logo + Barcode Label", page_icon="🎫")

st.title("Arrow + Logo + Barcode Label Maker")

logo_file = st.file_uploader(
    "Logo image upload karo (PNG / JPG)",
    type=["png", "jpg", "jpeg"]
)

barcode_text = st.text_input(
    "Barcode text daalo (jaise: W102-07-01-01-03)",
    value="W102-07-01-01-03"
)

label_width_mm = st.number_input("Label width (mm)", value=180.0)
label_height_mm = st.number_input("Label height (mm)", value=60.0)

if st.button("Generate Label"):

    if logo_file is None:
        st.error("Pehle logo image upload karo.")
    elif not barcode_text.strip():
        st.error("Barcode text khali hai.")
    else:
        try:
            # --------- Logo load ----------
            logo_img = Image.open(logo_file).convert("RGBA")

            # --------- Barcode image (no text) ----------
            bar_buf = io.BytesIO()
            code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
            render_opts = {"write_text": False}      # [web:19][web:20]
            code128.render(render_opts).save(bar_buf, format="PNG")
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

            # --------- Layout:  left arrow, right logo+barcode+text ---------
            left_margin = 5 * mm
            right_margin = 5 * mm
            gap = 6 * mm

            arrow_block_w = lw * 0.30
            arrow_block_h = lh - 10 * mm

            # ------ Arrow (left) ------
            arrow_x0 = left_margin
            arrow_y0 = (lh - arrow_block_h) / 2.0
            arrow_x1 = arrow_x0 + arrow_block_w
            arrow_y1 = arrow_y0 + arrow_block_h

            mid_x = (arrow_x0 + arrow_x1) / 2.0
            head_height = arrow_block_h * 0.45
            shaft_width = arrow_block_w * 0.35

            p = c.beginPath()
            p.moveTo(mid_x - shaft_width / 2, arrow_y0)
            p.lineTo(mid_x + shaft_width / 2, arrow_y0)
            p.lineTo(mid_x + shaft_width / 2, arrow_y0 + arrow_block_h - head_height)
            p.lineTo(arrow_x1, arrow_y0 + arrow_block_h - head_height)
            p.lineTo(mid_x, arrow_y1)
            p.lineTo(arrow_x0, arrow_y0 + arrow_block_h - head_height)
            p.lineTo(mid_x - shaft_width / 2, arrow_y0 + arrow_block_h - head_height)
            p.close()

            orange = Color(1, 0.55, 0.20)
            c.setFillColor(orange)
            c.setStrokeColor(orange)
            c.drawPath(p, stroke=1, fill=1)

            # ------ Right side area (logo + barcode + text) ------
            right_x0 = left_margin + arrow_block_w + gap
            right_w = lw - right_x0 - right_margin

            # --- Logo on top of barcode ---
            logo_max_width = right_w * 0.35
            logo_ratio = logo_img.height / logo_img.width
            logo_w = logo_max_width
            logo_h = logo_w * logo_ratio

            logo_x = right_x0
            logo_y = lh - logo_h - 8 * mm   # top se thoda niche

            c.drawImage(
                ImageReader(logo_buf),
                logo_x,
                logo_y,
                width=logo_w,
                height=logo_h,
                mask="auto",
            )

            # --- Barcode just to the right of logo, aligned bottom of logo ---
            bar_available_w = right_w - logo_w - 4 * mm
            bar_w = bar_available_w
            bar_ratio = bar_img.height / bar_img.width
            bar_h = bar_w * bar_ratio

            max_bar_height = logo_h  # barcode ki height ~ logo height
            if bar_h > max_bar_height:
                scale = max_bar_height / bar_h
                bar_w *= scale
                bar_h *= scale

            bar_x = logo_x + logo_w + 4 * mm
            bar_y = logo_y   # top align with logo

            c.drawImage(
                ImageReader(bar_img_buf),
                bar_x,
                bar_y,
                width=bar_w,
                height=bar_h,
                mask="auto",
            )

            # --- Big text under full right area ---
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 20)
            text_y = bar_y - 8 * mm
            text_center_x = right_x0 + right_w / 2.0
            c.drawCentredString(text_center_x, text_y, barcode_text)  # [web:24][web:26]

            # --------- Finish ----------
            c.showPage()
            c.save()
            pdf_buffer.seek(0)
            pdf_bytes = pdf_buffer.getvalue()

            st.success("Label ready ho gaya ✅")
            st.download_button(
                label="Download Label PDF",
                data=pdf_bytes,
                file_name=f"arrow_logo_barcode_{barcode_text}.pdf",
                mime="application/pdf",
            )

        except Exception as e:
            st.error(f"Error aaya: {e}")
