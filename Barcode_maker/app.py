import streamlit as st
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.colors import black, Color, HexColor
from reportlab.lib.utils import ImageReader
import io
import barcode
from barcode.writer import ImageWriter

st.set_page_config(page_title="Premium Warehouse Label", page_icon="🏷️")

st.title("🏷️ Premium Warehouse Label Maker")

logo_file = st.file_uploader(
    "📁 Company Logo (PNG / JPG)",
    type=["png", "jpg", "jpeg"]
)

barcode_text = st.text_input(
    "🔢 Location Code",
    value="W13-07-07-01-02"
)

col1, col2 = st.columns(2)
with col1:
    label_width_mm = st.number_input("Label width (mm)", value=210.0)
with col2:
    label_height_mm = st.number_input("Label height (mm)", value=60.0)

if st.button("✨ Generate Premium Label", use_container_width=True, type="primary"):

    if logo_file is None:
        st.error("Pehle logo upload karo.")
    elif not barcode_text.strip():
        st.error("Code likho.")
    else:
        try:
            # ---------- LOGO ----------
            logo_img = Image.open(logo_file).convert("RGBA")
            lbuf = io.BytesIO()
            logo_img.save(lbuf, format="PNG")
            lbuf.seek(0)
            logo_ir = ImageReader(lbuf)

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

            # ===== LEFT: PREMIUM ARROW BOX =====
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
            c.roundRect(left_x + 0.8*mm, left_y + 0.8*mm,
                        left_w - 1.6*mm, left_h - 1.6*mm, radius,
                        stroke=0, fill=1)

            mid_x = left_x + left_w / 2.0
            top_y = left_y + left_h - 1.5*mm
            bottom_y = left_y + 1.5*mm

            head_h = left_h * 0.46
            shaft_w = left_w * 0.32

            path = c.beginPath()
            path.moveTo(mid_x - shaft_w/2, bottom_y)
            path.lineTo(mid_x + shaft_w/2, bottom_y)
            path.lineTo(mid_x + shaft_w/2, bottom_y + (left_h - head_h) * 0.97)
            path.lineTo(left_x + left_w * 0.95, bottom_y + left_h - head_h)
            path.lineTo(mid_x, top_y)
            path.lineTo(left_x + left_w * 0.05, bottom_y + left_h - head_h)
            path.lineTo(mid_x - shaft_w/2, bottom_y + (left_h - head_h) * 0.97)
            path.close()

            c.setFillColor(main_col)
            c.drawPath(path, stroke=0, fill=1)

            # ===== RIGHT: LOGO + BARCODE + TEXT =====
            right_x = left_x + left_w + 1 * mm
            right_w = lw - right_x - margin
            right_y = margin
            right_h = lh - 2 * margin

            c.setLineWidth(1.5)
            c.roundRect(right_x, right_y, right_w, right_h, 3*mm)

            center_x = right_x + right_w / 2.0

            # ---- TOP: LOGO ----
            logo_area_h = right_h * 0.25
            ratio = logo_img.height / logo_img.width
            logo_h = logo_area_h
            logo_w = logo_h / ratio
            max_logo_w = right_w * 0.28
            if logo_w > max_logo_w:
                logo_w = max_logo_w
                logo_h = logo_w * ratio

            logo_y = right_y + right_h - logo_h - 4*mm
            logo_x = center_x - logo_w / 2.0

            c.drawImage(
                logo_ir,
                logo_x,
                logo_y,
                width=logo_w,
                height=logo_h,
                mask="auto"
            )

            # ---- TOP UNDERLINE ----
            top_line_y = logo_y - 3*mm
            c.setLineWidth(2)
            c.setStrokeColor(HexColor("#333333"))
            c.line(right_x + 4*mm, top_line_y, right_x + right_w - 4*mm, top_line_y)

            # ---- BARCODE ----
            barcode_area_bottom = right_y + right_h * 0.40
            barcode_area_top = top_line_y - 2*mm
            barcode_area_h = barcode_area_top - barcode_area_bottom

            bar_w = right_w * 0.86
            bar_h = barcode_area_h * 0.70

            bar_x = center_x - bar_w / 2.0
            bar_y = barcode_area_bottom + (barcode_area_h - bar_h)

            c.drawImage(
                bar_ir,
                bar_x,
                bar_y,
                width=bar_w,
                height=bar_h,
                mask="auto"
            )

            # ---- BOTTOM UNDERLINE ----
            bottom_line_y = bar_y - 3*mm
            c.setLineWidth(2)
            c.line(right_x + 4*mm, bottom_line_y, right_x + right_w - 4*mm, bottom_line_y)

            # ---- TEXT (CLEAR, SEPARATE BOX) ----
            text_area_bottom = right_y + 5*mm
            text_area_top = bottom_line_y - 2*mm
            text_center_y = (text_area_bottom + text_area_top) / 2.0

            c.setFillColor(HexColor("#111111"))
            c.setFont("Helvetica-Bold", 26)
            c.drawCentredString(center_x, text_center_y, barcode_text)

            # ===== SAVE =====
            c.showPage()
            c.save()
            pdf_buffer.seek(0)
            pdf_bytes = pdf_buffer.getvalue()

            st.success("✅ Text ab clear visible hoga!")
            st.download_button(
                "⬇️ Download PDF",
                data=pdf_bytes,
                file_name=f"premium_label_{barcode_text}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Error: {e}")
