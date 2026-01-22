import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.colors import black
from reportlab.lib.utils import ImageReader
import io
import barcode
from barcode.writer import ImageWriter

st.set_page_config(page_title="Rack Label Maker", page_icon="🏷️")

st.title("Warehouse Rack Label - SAME as photo")

barcode_text = st.text_input(
    "Location Code", 
    value="W13-07-07-01-02"
)

label_width_mm = st.number_input("Label width (mm)", value=210.0)
label_height_mm = st.number_input("Label height (mm)", value=60.0)

if st.button("Generate Label"):

    if not barcode_text.strip():
        st.error("Code likho.")
    else:
        try:
            # --------- Barcode image (high DPI) ----------
            bar_buf = io.BytesIO()
            code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
            writer_opts = {
                "write_text": False,
                "dpi": 600,
                "module_height": 18,
            }
            code128.render(writer_opts).save(bar_buf, format="PNG")
            bar_buf.seek(0)
            bar_img = ImageReader(bar_buf)

            # --------- Canvas ----------
            lw = float(label_width_mm) * mm
            lh = float(label_height_mm) * mm

            pdf_buffer = io.BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=(lw, lh))

            margin = 4 * mm

            # ===== LEFT BLOCK: ARROW + BORDER =====
            left_w = lw * 0.27
            left_x = margin
            left_y = margin
            left_h = lh - 2 * margin

            # outer rectangle
            c.setLineWidth(1)
            c.rect(left_x, left_y, left_w, left_h)

            # arrow inside
            ax = left_x
            ay = left_y
            aw = left_w
            ah = left_h

            mid_x = ax + aw / 2.0
            head_h = ah * 0.45
            base_h = ah * 0.2
            shaft_w = aw * 0.32

            p = c.beginPath()
            p.moveTo(mid_x - shaft_w/2, ay)
            p.lineTo(mid_x + shaft_w/2, ay)
            p.lineTo(mid_x + shaft_w/2, ay + ah - head_h)
            p.lineTo(ax + aw, ay + ah - head_h)
            p.lineTo(mid_x, ay + ah)
            p.lineTo(ax, ay + ah - head_h)
            p.lineTo(mid_x - shaft_w/2, ay + ah - head_h)
            p.lineTo(mid_x - shaft_w/2, ay + base_h)
            p.close()
            c.setFillColor(black)
            c.drawPath(p, stroke=0, fill=1)

            # ===== RIGHT BLOCK: BARCODE + TEXT with FULL UNDERLINES =====
            right_x = left_x + left_w
            right_w = lw - right_x - margin

            top_y = lh - margin
            bottom_y = margin

            # outer rectangle
            c.rect(right_x, bottom_y, right_w, lh - 2*margin)

            center_x = right_x + right_w / 2.0

            # area for barcode + text
            inner_top = top_y - 6*mm
            inner_bottom = bottom_y + 8*mm

            # ---- barcode size ----
            # try to fit most of width
            bar_w = right_w * 0.85
            # assume aspect ratio approx 0.3
            bar_h = bar_w * 0.3

            # top underline (full width)
            top_line_y = inner_top
            c.line(right_x + 2*mm, top_line_y, right_x + right_w - 2*mm, top_line_y)

            # barcode position
            bar_y = top_line_y - bar_h - 2*mm
            bar_x = center_x - bar_w/2

            c.drawImage(
                bar_img,
                bar_x,
                bar_y,
                width=bar_w,
                height=bar_h,
                mask='auto'
            )

            # bottom underline (full width, same jaisa photo)
            bottom_line_y = bar_y - 2*mm
            c.line(right_x + 2*mm, bottom_line_y, right_x + right_w - 2*mm, bottom_line_y)

            # text niche center
            c.setFont("Helvetica-Bold", 26)
            text_y = bottom_line_y - 6*mm
            c.drawCentredString(center_x, text_y, barcode_text)

            c.showPage()
            c.save()
            pdf_buffer.seek(0)
            pdf_bytes = pdf_buffer.getvalue()

            st.success("Label ready ✅")
            st.download_button(
                "Download PDF",
                data=pdf_bytes,
                file_name=f"rack_label_{barcode_text}.pdf",
                mime="application/pdf",
            )

        except Exception as e:
            st.error(f"Error: {e}")
