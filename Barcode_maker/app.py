import streamlit as st
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.colors import black
from reportlab.lib.utils import ImageReader
import io
import barcode
from barcode.writer import ImageWriter

# ---------- Streamlit page config ----------
st.set_page_config(page_title="Logo + Barcode Label Maker", page_icon="🎫")

st.title("Logo + Barcode Label Maker")
st.write("Logo + Barcode + arrow + bold text → ekdum clean label.")

# ---------- Inputs ----------
logo_file = st.file_uploader(
    "Logo image upload karo (PNG / JPG)",
    type=["png", "jpg", "jpeg"]
)

barcode_text = st.text_input(
    "Barcode text daalo (jaise: W102-07-01-01-03)",
    value="W102-07-01-01-03"
)

label_width_mm = st.number_input("Label width (mm)", value=80.0)
label_height_mm = st.number_input("Label height (mm)", value=40.0)

# ---------- Button ----------
if st.button("Generate Label"):

    if logo_file is None:
        st.error("Pehle logo image upload karo.")
    elif not barcode_text.strip():
        st.error("Barcode text khali hai.")
    else:
        try:
            # ----- 1) Logo load -----
            logo_img = Image.open(logo_file).convert("RGBA")

            # ----- 2) Barcode image generate (Code128, WITHOUT text) -----
            bar_buf = io.BytesIO()
            code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
            # python-barcode me text off karne ke liye render options use karte hain [web:19][web:20]
            render_opts = {"write_text": False}
            code128.render(render_opts).save(bar_buf, format="PNG")
            bar_buf.seek(0)
            bar_img = Image.open(bar_buf).convert("RGBA")

            # ----- 3) Label PDF canvas -----
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

            # ---------- Layout ----------
            left_margin = 5 * mm
            right_margin = 5 * mm
            mid_gap = 3 * mm

            # Logo block (fixed area)
            logo_block_w = lw * 0.30
            logo_block_h = lh - 10 * mm
            logo_max_side = min(logo_block_w, logo_block_h)
            logo_w = logo_max_side
            logo_h = logo_max_side

            logo_x = left_margin
            logo_y = (lh - logo_h) / 2.0

            # Barcode area (right side)
            bar_area_x = logo_x + logo_block_w + mid_gap
            bar_area_w = lw - bar_area_x - right_margin

            bar_w = bar_area_w
            bar_ratio = bar_img.height / bar_img.width
            bar_h = bar_w * bar_ratio

            text_height = 8 * mm
            arrow_height = 6 * mm
            # top + bottom padding + arrow + text ke hisaab se max height [web:26]
            max_bar_height = lh - (12 * mm + text_height + arrow_height)

            if bar_h > max_bar_height:
                scale = max_bar_height / bar_h
                bar_w *= scale
                bar_h *= scale

            # Barcode ko vertical center rakhte hue, upar arrow aur niche text ke liye jagah
            bar_x = bar_area_x
            bar_y = (lh - bar_h) / 2.0

            # ----- 4) Draw logo -----
            c.drawImage(
                ImageReader(logo_buf),
                logo_x,
                logo_y,
                width=logo_w,
                height=logo_h,
                mask="auto",
            )

            # ----- 5) Draw barcode -----
            c.drawImage(
                ImageReader(bar_img_buf),
                bar_x,
                bar_y,
                width=bar_w,
                height=bar_h,
                mask="auto",
            )

            # ----- 6) Arrow UP (orientation mark) -----
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 14)
            arrow_y = bar_y + bar_h + 2 * mm
            arrow_x_center = bar_x + bar_w / 2.0
            c.drawCentredString(arrow_x_center, arrow_y, "↑")  # [web:24]

            # ----- 7) BIG single text below barcode -----
            c.setFillColor(black)
            c.setFont("Helvetica-Bold", 16)
            text_y = bar_y - 6 * mm
            text_x_center = bar_x + bar_w / 2.0
            c.drawCentredString(text_x_center, text_y, barcode_text)

            # ----- Finish -----
            c.showPage()
            c.save()
            pdf_buffer.seek(0)
            pdf_bytes = pdf_buffer.getvalue()

            st.success("Label ready ho gaya ✅")
            st.download_button(
                label="Download Label PDF",
                data=pdf_bytes,
                file_name=f"label_{barcode_text}.pdf",
                mime="application/pdf",
            )

        except Exception as e:
            st.error(f"Error aaya: {e}")
