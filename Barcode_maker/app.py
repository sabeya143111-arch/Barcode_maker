import streamlit as st
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.colors import black, Color
from reportlab.lib.utils import ImageReader
import io
import barcode
from barcode.writer import ImageWriter

st.set_page_config(page_title="Perfect Warehouse Label", page_icon="🏷️")

st.title("🏷️ Perfect Warehouse Label Maker - HD Print")
st.caption("Exact aapke warehouse label jaisa - Print ready!")

# ===== SIDEBAR - Fine Tuning =====
with st.sidebar:
    st.header("⚙️ Label Settings")
    
    label_width_mm = st.number_input("Label width (mm)", value=210.0, min_value=100.0)
    label_height_mm = st.number_input("Label height (mm)", value=80.0, min_value=50.0)
    
    st.divider()
    
    # DPI for print quality
    dpi = st.select_slider("Print Quality (DPI)", options=[300, 600, 1200], value=1200)
    
    # Logo size
    logo_height_percent = st.slider("Logo size (%)", min_value=15, max_value=35, value=22)
    
    # Barcode size
    barcode_scale = st.slider("Barcode size scale", min_value=0.7, max_value=1.2, value=1.0, step=0.1)
    
    # Arrow color
    arrow_color_opt = st.selectbox("Arrow color", ["Orange", "Teal", "Blue", "Red"])
    color_map = {
        "Orange": Color(1, 0.55, 0.20),
        "Teal": Color(0.2, 0.6, 0.6),
        "Blue": Color(0.2, 0.5, 1),
        "Red": Color(1, 0.3, 0.3)
    }
    arrow_color = color_map[arrow_color_opt]
    
    st.divider()
    st.info("💡 Print resolution: 1200 DPI = Crystal clear barcode")

# ===== MAIN INPUT =====
col1, col2 = st.columns(2)

with col1:
    logo_file = st.file_uploader(
        "📁 Company Logo (PNG/JPG)",
        type=["png", "jpg", "jpeg"],
        help="High resolution logo best hai"
    )

with col2:
    barcode_text = st.text_input(
        "🔢 Product Code",
        value="W13-07-07-01-02",
        placeholder="Jaise: W102-07-01-01-03"
    )

# ===== GENERATE BUTTON =====
if st.button("✨ Generate HD Label", use_container_width=True, type="primary"):

    if logo_file is None:
        st.error("❌ Logo upload karo!")
    elif not barcode_text.strip():
        st.error("❌ Product code likho!")
    else:
        try:
            with st.spinner("🔄 HD Label ban raha hai..."):
                # --------- Logo load ----------
                logo_img = Image.open(logo_file).convert("RGBA")

                # --------- ULTRA HIGH DPI Barcode ----------
                bar_buf = io.BytesIO()
                code128 = barcode.get("code128", barcode_text, writer=ImageWriter())
                
                # HIGH QUALITY SETTINGS
                writer_opts = {
                    "write_text": False,
                    "dpi": dpi,  # 1200 DPI for crystal clear print
                    "module_height": 20,  # Thicker bars
                    "module_width": 0.5,  # Precise width
                }
                
                code128.render(writer_opts).save(bar_buf, format="PNG")
                bar_buf.seek(0)
                bar_img = Image.open(bar_buf).convert("RGBA")

                # --------- PDF Canvas setup (300 DPI) ----------
                lw = float(label_width_mm) * mm
                lh = float(label_height_mm) * mm

                pdf_buffer = io.BytesIO()
                # High resolution canvas
                c = canvas.Canvas(pdf_buffer, pagesize=(lw, lh))

                def pil_to_buf(img):
                    b = io.BytesIO()
                    img.save(b, format="PNG")
                    b.seek(0)
                    return b

                logo_buf = pil_to_buf(logo_img)
                bar_img_buf = pil_to_buf(bar_img)

                margin = 8 * mm

                # ===== LEFT: ARROW =====
                arrow_block_w = lw * 0.28
                arrow_block_h = lh - 2 * margin

                arrow_x = margin
                arrow_y = (lh - arrow_block_h) / 2.0

                mid_x = arrow_x + arrow_block_w / 2.0
                head_height = arrow_block_h * 0.5
                shaft_width_top = arrow_block_w * 0.26
                shaft_width_bottom = arrow_block_w * 0.38
                base_h = arrow_block_h * 0.18

                p = c.beginPath()
                p.moveTo(mid_x - shaft_width_bottom / 2, arrow_y)
                p.lineTo(mid_x + shaft_width_bottom / 2, arrow_y)
                p.lineTo(mid_x + shaft_width_top / 2, arrow_y + base_h)
                p.lineTo(mid_x + shaft_width_top / 2, arrow_y + arrow_block_h - head_height)
                p.lineTo(arrow_x + arrow_block_w, arrow_y + arrow_block_h - head_height)
                p.lineTo(mid_x, arrow_y + arrow_block_h)
                p.lineTo(arrow_x, arrow_y + arrow_block_h - head_height)
                p.lineTo(mid_x - shaft_width_top / 2, arrow_y + arrow_block_h - head_height)
                p.lineTo(mid_x - shaft_width_top / 2, arrow_y + base_h)
                p.close()

                c.setFillColor(arrow_color)
                c.setStrokeColor(arrow_color)
                c.drawPath(p, stroke=0, fill=1)

                # ===== RIGHT SIDE: CONTENT =====
                tiny_gap = 1.5 * mm
                right_x = arrow_x + arrow_block_w + tiny_gap
                right_w = lw - right_x - margin

                col_top = lh - margin
                col_bottom = margin

                # ===== TOP: LOGO =====
                logo_area_h = (col_top - col_bottom) * (logo_height_percent / 100)
                
                logo_ratio = logo_img.height / logo_img.width
                logo_h = logo_area_h
                logo_w = logo_h / logo_ratio
                max_logo_w = right_w * 0.85
                
                if logo_w > max_logo_w:
                    logo_w = max_logo_w
                    logo_h = logo_w * logo_ratio

                logo_y = col_top - logo_h
                logo_x = right_x + (right_w - logo_w) / 2.0

                c.drawImage(
                    ImageReader(logo_buf),
                    logo_x,
                    logo_y,
                    width=logo_w,
                    height=logo_h,
                    mask="auto",
                    preserveAspectRatio=True,
                )

                # ===== BOTTOM: BARCODE + UNDERLINE + TEXT =====
                barcode_area_top = logo_y - 4 * mm
                barcode_area_bottom = col_bottom + 4 * mm
                barcode_area_h = barcode_area_top - barcode_area_bottom

                center_x = right_x + right_w / 2.0

                # ---- Calculate Barcode Size (BADA) ----
                bar_ratio = bar_img.height / bar_img.width
                
                # Barcode ko jitna possible ho utna bada banao
                bar_w = right_w * 0.90 * barcode_scale  # 90% of available width
                bar_h = bar_w * bar_ratio

                # Agar bahat zyada height ho to reduce karo
                if bar_h > barcode_area_h * 0.55:
                    scale = (barcode_area_h * 0.55) / bar_h
                    bar_w *= scale
                    bar_h *= scale

                # ---- UNDERLINE (Barcode ke same width, colored) ----
                line_y = barcode_area_top - 3 * mm
                c.setStrokeColor(arrow_color)
                c.setLineWidth(2.5)  # Slightly thicker line
                
                underline_x1 = center_x - bar_w / 2.0
                underline_x2 = center_x + bar_w / 2.0
                
                c.line(underline_x1, line_y, underline_x2, line_y)

                # ---- BARCODE (Barcode ke niche, HD Quality) ----
                bar_x = center_x - bar_w / 2.0
                bar_y = line_y - bar_h - 2 * mm

                c.drawImage(
                    ImageReader(bar_img_buf),
                    bar_x,
                    bar_y,
                    width=bar_w,
                    height=bar_h,
                    mask="auto",
                    preserveAspectRatio=True,
                )

                # ---- TEXT (Bold, Clear) ----
                c.setFillColor(black)
                c.setFont("Helvetica-Bold", 26)  # Slightly larger
                text_y = bar_y - 7 * mm
                
                c.drawCentredString(center_x, text_y, barcode_text)

                # ===== SAVE PDF =====
                c.showPage()
                c.save()
                pdf_buffer.seek(0)
                pdf_bytes = pdf_buffer.getvalue()

            # ===== SUCCESS MESSAGE + DOWNLOAD =====
            st.success("✅ HD Label ready! Print quality guaranteed!")
            
            st.markdown("---")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.info("📌 **Print Settings:**\n- Quality: " + str(dpi) + " DPI\n- Paper: 210x80mm (MEDIUM)\n- Color: Recommended")
            
            with col2:
                st.download_button(
                    label="⬇️ Download HD PDF",
                    data=pdf_bytes,
                    file_name=f"label_{barcode_text}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.warning("💡 Tip: Logo clear hona chahiye aur valid JPG/PNG format mein ho")
