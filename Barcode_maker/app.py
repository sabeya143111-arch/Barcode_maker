import streamlit as st
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.colors import black, Color
from reportlab.lib.utils import ImageReader
import io
import barcode
from barcode.writer import ImageWriter

st.set_page_config(page_title="Professional Barcode Label", page_icon="🎫")

st.title("Professional Barcode Label Maker")
st.write("Arrow + Brand Logo + Barcode → Professional label")

logo_file = st.file_uploader(
    "Company Logo upload karo (PNG / JPG)",
    type=["png", "jpg", "jpeg"]
)

barcode_text = st.text_input(
    "Product Code (jaise: W102-07-01-01-03)",
    value="W102-07-01-01-03"
)

label_width_mm = st.number_input("Label width (mm)", value=200.0)
label_height_mm = st.number_input("Label height (mm)", value=80.0)

if st.button("Generate Label"):

    if logo_file is None:
        st.error("Pehle company logo upload karo.")
    elif not barcode_text.strip():
        st.error("Product code khali hai.")
    else:
        try:
            # --------- Load images ----------
            logo_img = Image.open(logo_file).convert("RGBA")

            bar_buf = io.BytesIO()
            code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
            render_opts = {"write_text": False}
            code128.render(render_opts).save(bar_buf, format="PNG")
            bar_buf.seek(0)
            bar_img = Image.open(bar_buf).convert("RGBA")

            # --------- PDF Canvas ----------
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

            # --------- LAYOUT: LEFT ARROW | RIGHT (LOGO TOP, BARCODE MIDDLE, TEXT BOTTOM) ----------
            margin = 8 * mm
            gap = 8 * mm

            # LEFT: Arrow block
            arrow_w = lw * 0.32
            arrow_h = lh - 2 * margin

            arrow_x = margin
            arrow_y = (lh - arrow_h) / 2.0

            # RIGHT: Logo + Barcode + Text block
            right_x = arrow_x + arrow_w + gap
            right_w = lw - right_x - margin

            # ------ 1) ARROW (BIG, ORANGE, LEFT SIDE) ------
            mid_x = arrow_x + arrow_w / 2.0
            head_height = arrow_h * 0.5
            shaft_width = arrow_w * 0.4

            p = c.beginPath()
            p.moveTo(mid_x - shaft_width / 2, arrow_y)
            p.lineTo(mid_x + shaft_width / 2, arrow_y)
            p.lineTo(mid_x + shaft_width / 2, arrow_y + arrow_h - head_height)
            p.lineTo(arrow_x + arrow_w, arrow_y + arrow_h - head_height)
            p.lineTo(mid_x, arrow_y + arrow_h)
            p.lineTo(arrow_x, arrow_y + arrow_h - head_height)
            p.lineTo(mid_x - shaft_width / 2, arrow_y + arrow_h - head_height)
            p.close()

            orange = Color(1, 0.55, 0.20)
            c.setFillColor(orange)
            c.setStrokeColor(orange)
            c.drawPath(p, stroke=1, fill=1)

            # ------ 2) LOGO (TOP, PROMINENT) ------
            logo_max_h = lh * 0.45   # Logo 45% height
            logo_ratio = logo_img.height / logo_img.width
            logo_h = logo_max_h
            logo_w = logo_h / logo_ratio

            # Agar logo bada ho gaya right side se, width compress karo
            if logo_w > right_w:
                logo_w = right_w * 0.85
                logo_h = logo_w * logo_ratio

            logo_x = right_x + (right_w - logo_w) / 2.0    # center align
            logo_y = lh - logo_h - 6 * mm                   # top side

            c.drawImage(
                ImageReader(logo_buf),
                logo_x,
                logo_y,
                width=logo_w,
                height=logo_h,
                mask="auto",
            )

            # ------ 3) BARCODE (MIDDLE, LOGO KE NICHE) ------
            barcode_area_h = lh * 0.35
            bar_w = right_w * 0.95
            bar_ratio = bar_img.height / bar_img.width
            bar_h = bar_w * bar_ratio

            if bar_h > barcode_area_h:
                scale = barcode_area_h / bar_h
                bar_w *= scale
                bar_h *= scale

            bar_x = right_x + (right_w - bar_w) / 2.0
            bar_y = logo_y - bar_h - 6 * mm    # logo ke bilkul niche

            c.drawImage(
                ImageReader(bar_img_buf),
                bar_x,
                bar_y,
                width=bar_w,
                height=bar_h,
                mask="auto",
            )

            # ------ 4) TEXT (BOTTOM, BOLD) ------
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 24)
            text_y = bar_y - 8 * mm
            text_x = right_x + right_w / 2.0
            c.drawCentredString(text_x, text_y, barcode_text)

            # --------- Finish ----------
            c.showPage()
            c.save()
            pdf_buffer.seek(0)
            pdf_bytes = pdf_buffer.getvalue()

            st.success("Professional label ready ✅")
            st.download_button(
                label="Download Label PDF",
                data=pdf_bytes,
                file_name=f"label_{barcode_text}.pdf",
                mime="application/pdf",
            )

        except Exception as e:
            st.error(f"Error: {e}")
