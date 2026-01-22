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
st.write("Logo + Barcode + neat text → ekdum clean label.")

# ---------- Inputs ----------
logo_file = st.file_uploader(
    "Logo image upload karo (PNG / JPG)",
    type=["png", "jpg", "jpeg"]
)

barcode_text = st.text_input(
    "Barcode text daalo (jaise: W102-07-01-01-03)",
    value="W102-07-01-01-03"
)

# Label ka size FIX kar diya
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

            # ----- 2) Barcode image generate (Code128) -----
            bar_buf = io.BytesIO()
            code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
            code128.write(bar_buf)
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

            # ---------- DESIGN LAYOUT ----------
            # Left 1/3 = logo area, right 2/3 = barcode + text
            left_margin = 5 * mm
            right_margin = 5 * mm
            mid_gap = 3 * mm  # logo aur barcode ke beech thoda sa breathing space

            # ---- Logo size (fixed & centered block) ----
            logo_block_w = (lw * 0.30)        # total width ka 30% logo ke liye
            logo_block_h = lh - 10 * mm       # thoda top/bottom margin

            # Logo ko square block me center karna
            logo_max_side = min(logo_block_w, logo_block_h)
            logo_w = logo_max_side
            logo_h = logo_max_side

            logo_x = left_margin
            logo_y = (lh - logo_h) / 2.0

            # ---- Barcode area ----
            bar_area_x = logo_x + logo_block_w + mid_gap
            bar_area_w = lw - bar_area_x - right_margin

            # Barcode width/height
            bar_w = bar_area_w
            bar_ratio = bar_img.height / bar_img.width
            bar_h = bar_w * bar_ratio

            # Barcode ko thoda upar, niche text ke liye jagah
            text_height = 8 * mm   # text ke liye reserved height
            max_bar_height = lh - 12 * mm - text_height

            if bar_h > max_bar_height:
                scale = max_bar_height / bar_h
                bar_w *= scale
                bar_h *= scale

            bar_x = bar_area_x
            bar_y = (lh - bar_h - text_height) / 2.0 + text_height / 2.0

            # ---------- 6) Draw logo ----------
            c.drawImage(
                ImageReader(logo_buf),
                logo_x,
                logo_y,
                width=logo_w,
                height=logo_h,
                mask="auto",
            )

            # ---------- 7) Draw barcode ----------
            c.drawImage(
                ImageReader(bar_img_buf),
                bar_x,
                bar_y,
                width=bar_w,
                height=bar_h,
                mask="auto",
            )

            # ---------- 8) Draw BIG, CLEAN text ----------
            c.setFillColor(black)
            # Font size bada rakha, center under barcode
            font_name = "Helvetica-Bold"
            font_size = 14  # try 16 bhi kar sakta hai
            c.setFont(font_name, font_size)

            text_y = bar_y - 4 * mm  # barcode ke just niche
            # Center text in barcode area
            text_x_center = bar_x + bar_w / 2.0

            c.drawCentredString(text_x_center, text_y, barcode_text)

            # ---------- 9) Finish ----------
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
