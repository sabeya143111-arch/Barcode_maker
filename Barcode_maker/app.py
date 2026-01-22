import streamlit as st
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.utils import ImageReader
import io
import barcode
from barcode.writer import ImageWriter

# ---------- Streamlit page config ----------
st.set_page_config(page_title="Logo + Barcode Label Maker", page_icon="🎫")

st.title("Logo + Barcode Label Maker")
st.write("Logo image + Barcode text → label PDF bana dega.")

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

    # Basic validation
    if logo_file is None:
        st.error("Pehle logo image upload karo.")
    elif not barcode_text.strip():
        st.error("Barcode text khali hai.")
    else:
        try:
            # ----- 1) Logo load -----
            logo_img = Image.open(logo_file).convert("RGBA")

            # ----- 2) Barcode image generate (Code128) -----
            bar_buf = io.BytesIO()
            code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
            code128.write(bar_buf)          # PNG bytes
            bar_buf.seek(0)
            bar_img = Image.open(bar_buf).convert("RGBA")

            # ----- 3) Label PDF canvas -----
            lw = float(label_width_mm) * mm   # label width in points
            lh = float(label_height_mm) * mm  # label height in points

            pdf_buffer = io.BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=(lw, lh))

            def pil_to_buf(img):
                b = io.BytesIO()
                img.save(b, format="PNG")
                b.seek(0)
                return b

            logo_buf = pil_to_buf(logo_img)
            bar_img_buf = pil_to_buf(bar_img)

            # ----- 4) Sizes (mm) -----
            # Logo circle thoda chhota
            logo_w = 18.0 * mm
            logo_ratio = logo_img.height / logo_img.width
            logo_h = logo_w * logo_ratio

            # Barcode bada rakha (pure right area ke liye)
            bar_w = 50.0 * mm
            bar_ratio = bar_img.height / bar_img.width
            bar_h = bar_w * bar_ratio

            # Agar height zyada ho rahi ho to adjust
            if logo_h > lh - 6 * mm:
                scale = (lh - 6 * mm) / logo_h
                logo_w *= scale
                logo_h *= scale

            if bar_h > lh - 6 * mm:
                scale = (lh - 6 * mm) / bar_h
                bar_w *= scale
                bar_h *= scale

            # ----- 5) Positions : EKDAM BAGAL ME -----
            # Left me logo, usi ke turant baad barcode
            left_margin = 5.0 * mm
            gap = 0.5 * mm  # almost no space

            logo_x = left_margin
            logo_y = (lh - logo_h) / 2.0

            bar_x = logo_x + logo_w + gap
            bar_y = (lh - bar_h) / 2.0

            # Safety: agar barcode right edge cross kare to thoda compress
            total_needed_width = (logo_w + gap + bar_w + left_margin)
            if total_needed_width > lw:
                compress = (lw - left_margin) / (logo_w + gap + bar_w)
                logo_w *= compress
                logo_h *= compress
                bar_w *= compress
                bar_h *= compress

                logo_y = (lh - logo_h) / 2.0
                bar_x = logo_x + logo_w + gap
                bar_y = (lh - bar_h) / 2.0

            # ----- 6) Draw on PDF -----
            c.drawImage(
                ImageReader(logo_buf),
                logo_x,
                logo_y,
                width=logo_w,
                height=logo_h,
                mask="auto",
            )

            c.drawImage(
                ImageReader(bar_img_buf),
                bar_x,
                bar_y,
                width=bar_w,
                height=bar_h,
                mask="auto",
            )

            c.showPage()
            c.save()
            pdf_buffer.seek(0)
            pdf_bytes = pdf_buffer.getvalue()

            # ----- 7) Download -----
            st.success("Label ready ho gaya ✅")
            st.download_button(
                label="Download Label PDF",
                data=pdf_bytes,
                file_name=f"label_{barcode_text}.pdf",
                mime="application/pdf",
            )

        except Exception as e:
            st.error(f"Error aaya: {e}")
