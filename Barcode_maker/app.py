import streamlit as st
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.utils import ImageReader
import io

st.set_page_config(page_title="Logo + Barcode Label Maker", page_icon="🎫")

st.title("Logo + Barcode Label Maker")
st.write("Logo image + Barcode image se label PDF banayega.")

# ---- Inputs ----
logo_file = st.file_uploader(
    "Logo image upload karo (PNG/JPG)",
    type=["png", "jpg", "jpeg"]
)

bar_file = st.file_uploader(
    "Barcode image upload karo (PNG/JPG)",
    type=["png", "jpg", "jpeg"]
)

label_width_mm = st.number_input("Label width (mm)", value=50.0)
label_height_mm = st.number_input("Label height (mm)", value=30.0)

if st.button("Generate Label"):

    if logo_file is None or bar_file is None:
        st.error("Dono files upload karo: logo + barcode image.")
    else:
        logo_img = Image.open(logo_file).convert("RGBA")
        bar_img = Image.open(bar_file).convert("RGBA")

        # ----- canvas size (as float) -----
        lw = float(label_width_mm) * mm
        lh = float(label_height_mm) * mm

        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=(lw, lh))

        def pil_to_buf(img):
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            return buf

        logo_buf = pil_to_buf(logo_img)
        bar_buf = pil_to_buf(bar_img)

        # ---- Sizes ----
        logo_w = 20.0 * mm
        logo_ratio = logo_img.height / logo_img.width
        logo_h = logo_w * logo_ratio

        bar_w = 40.0 * mm
        bar_ratio = bar_img.height / bar_img.width
        bar_h = bar_w * bar_ratio

        # ---- Positions ----
        logo_x = (lw - logo_w) / 2.0
        logo_y = lh - logo_h - 5.0 * mm

        bar_x = (lw - bar_w) / 2.0
        bar_y = 5.0 * mm

        # Draw
        c.drawImage(ImageReader(logo_buf), logo_x, logo_y,
                    width=logo_w, height=logo_h, mask='auto')

        c.drawImage(ImageReader(bar_buf), bar_x, bar_y,
                    width=bar_w, height=bar_h, mask='auto')

        c.showPage()
        c.save()
        pdf_buffer.seek(0)
        out_bytes = pdf_buffer.getvalue()

        st.success("Label ready ho gaya.")
        st.download_button(
            label="Download Label PDF",
            data=out_bytes,
            file_name="label_logo_barcode.pdf",
            mime="application/pdf"
        )
