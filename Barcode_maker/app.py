import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.colors import black
from reportlab.lib.utils import ImageReader
import io
import barcode
from barcode.writer import ImageWriter

st.set_page_config(page_title="Warehouse Rack Label", page_icon="🏷️")

st.title("🏷️ Warehouse Rack Label Maker")
st.caption("Perfect Print Ready - Exact Layout")

# ===== INPUT =====
barcode_text = st.text_input(
    "🔢 Location Code",
    value="W13-07-07-01-02",
    placeholder="Jaise: W102-07-01-01-03"
)

col1, col2 = st.columns(2)
with col1:
    label_width_mm = st.number_input("Label width (mm)", value=210.0)
with col2:
    label_height_mm = st.number_input("Label height (mm)", value=60.0)

# ===== GENERATE =====
if st.button("✨ Generate Label", use_container_width=True, type="primary"):

    if not barcode_text.strip():
        st.error("❌ Code likho!")
    else:
        try:
            with st.spinner("🔄 Label ban raha hai..."):
                
                # --------- HIGH DPI BARCODE ----------
                bar_buf = io.BytesIO()
                code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
                writer_opts = {
                    "write_text": False,
                    "dpi": 1200,  # Ultra HD
                    "module_height": 20,
                    "module_width": 0.5,
                }
                code128.render(writer_opts).save(bar_buf, format="PNG")
                bar_buf.seek(0)
                bar_img = ImageReader(bar_buf)

                # --------- PDF CANVAS ----------
                lw = float(label_width_mm) * mm
                lh = float(label_height_mm) * mm

                pdf_buffer = io.BytesIO()
                c = canvas.Canvas(pdf_buffer, pagesize=(lw, lh))

                margin = 2 * mm

                # ===== LEFT: ARROW SECTION =====
                left_w = lw * 0.28
                left_h = lh - 2 * margin
                left_x = margin
                left_y = margin

                # Border rectangle
                c.setLineWidth(1.5)
                c.rect(left_x, left_y, left_w, left_h)

                # Arrow shape (black fill)
                mid_x = left_x + left_w / 2.0
                head_height = left_h * 0.48
                shaft_width = left_w * 0.35
                base_h = left_h * 0.22

                path = c.beginPath()
                path.moveTo(mid_x - shaft_width/2, left_y)
                path.lineTo(mid_x + shaft_width/2, left_y)
                path.lineTo(mid_x + shaft_width/2, left_y + left_h - head_height)
                path.lineTo(left_x + left_w, left_y + left_h - head_height)
                path.lineTo(mid_x, left_y + left_h)
                path.lineTo(left_x, left_y + left_h - head_height)
                path.lineTo(mid_x - shaft_width/2, left_y + left_h - head_height)
                path.lineTo(mid_x - shaft_width/2, left_y + base_h)
                path.close()

                c.setFillColor(black)
                c.drawPath(path, stroke=0, fill=1)

                # ===== RIGHT: BARCODE + TEXT SECTION =====
                right_x = left_x + left_w + 1*mm
                right_w = lw - right_x - margin
                right_h = lh - 2*margin
                right_y = margin

                # Border rectangle
                c.setLineWidth(1.5)
                c.rect(right_x, right_y, right_w, right_h)

                center_x = right_x + right_w / 2.0

                # ===== TOP UNDERLINE =====
                top_line_y = right_y + right_h - 6*mm
                c.setLineWidth(2)
                c.line(right_x + 3*mm, top_line_y, right_x + right_w - 3*mm, top_line_y)

                # ===== BARCODE (CENTER, LARGE) =====
                bar_w = right_w * 0.88  # 88% width
                bar_h = bar_w * 0.32   # Aspect ratio
                
                bar_x = center_x - bar_w / 2.0
                bar_y = top_line_y - bar_h - 3*mm

                c.drawImage(
                    bar_img,
                    bar_x,
                    bar_y,
                    width=bar_w,
                    height=bar_h,
                    mask='auto'
                )

                # ===== BOTTOM UNDERLINE =====
                bottom_line_y = bar_y - 3*mm
                c.setLineWidth(2)
                c.line(right_x + 3*mm, bottom_line_y, right_x + right_w - 3*mm, bottom_line_y)

                # ===== TEXT (INSIDE BOTTOM BOX, CENTERED) =====
                # Text area between bottom line aur bottom edge
                text_area_h = bottom_line_y - right_y - 2*mm
                text_y = right_y + text_area_h / 2.0 + 2*mm
                
                c.setFont("Helvetica-Bold", 28)  # Large
                c.setFillColor(black)
                c.drawCentredString(center_x, text_y, barcode_text)

                # ===== SAVE =====
                c.showPage()
                c.save()
                pdf_buffer.seek(0)
                pdf_bytes = pdf_buffer.getvalue()

            st.success("✅ Label ready! Perfect print quality")
            
            st.info("📌 Print Settings:\n- Quality: 1200 DPI (Crystal Clear)\n- Paper: 210x60mm\n- Scale: 100% (NO scaling)")
            
            st.download_button(
                label="⬇️ Download HD PDF",
                data=pdf_bytes,
                file_name=f"rack_label_{barcode_text}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


