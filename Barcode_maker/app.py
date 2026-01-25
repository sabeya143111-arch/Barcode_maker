import streamlit as st
from pathlib import Path
from PIL import Image, ImageChops
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.colors import black, HexColor
from reportlab.lib.utils import ImageReader
import io
import barcode
from barcode.writer import ImageWriter
from urllib.request import urlopen

# ================= LOGO =================
BASE_DIR = Path(__file__).resolve().parent
LOCAL_LOGO_PATH = BASE_DIR / "assets" / "logo.png"
GITHUB_LOGO_URL = "https://raw.githubusercontent.com/sabeya143111-arch/Barcode_maker/main/Barcode_maker/assets/logo.png"

_logo_cache = {}

def _crop_alpha(img):
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    bg = Image.new("RGBA", img.size, (0, 0, 0, 0))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    return img.crop(bbox) if bbox else img

def _make_square_rgba(img):
    img = _crop_alpha(img)
    side = max(img.width, img.height)
    canvas_img = Image.new("RGBA", (side, side), (255, 255, 255, 0))
    canvas_img.paste(img, ((side-img.width)//2, (side-img.height)//2), img)
    return canvas_img

def load_logo():
    if "img" in _logo_cache:
        return _logo_cache["img"], _logo_cache["ir"]

    try:
        if LOCAL_LOGO_PATH.exists():
            raw = Image.open(LOCAL_LOGO_PATH).convert("RGBA")
        else:
            raw = Image.open(io.BytesIO(urlopen(GITHUB_LOGO_URL).read())).convert("RGBA")

        img = _make_square_rgba(raw)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        ir = ImageReader(buf)

        _logo_cache["img"] = img
        _logo_cache["ir"] = ir
        return img, ir
    except:
        return None, None

# ================= PAGE CONFIG =================
st.set_page_config("Swag Barcode Maker", "🏷️", layout="wide")

# ================= GLOBAL CSS =================
st.markdown("""
<style>
.stApp {background:#020617;color:#E5E7EB;font-family:system-ui;}
[data-testid="stSidebar"] {background:#020617;}
.glass-card{background:rgba(15,23,42,.92);border-radius:16px;padding:16px;border:1px solid rgba(148,163,184,.4)}
.hero-title{font-size:48px;font-weight:900;letter-spacing:.08em;text-transform:uppercase;
background:linear-gradient(90deg,#F97316,#FACC15,#22C55E);-webkit-background-clip:text;color:transparent}
.hero-wrapper{text-align:center;margin-bottom:1.5rem}
.hero-pill{display:inline-flex;gap:6px;padding:4px 12px;border-radius:999px;border:1px solid #334155}
.hero-dot{width:7px;height:7px;border-radius:50%;background:#22C55E}
</style>
""", unsafe_allow_html=True)

# ================= HERO =================
st.markdown("""
<div class="hero-wrapper">
  <div class="hero-pill"><div class="hero-dot"></div> Instant warehouse labels • Made for Odoo</div>
  <div class="hero-title">SWAG BARCODE MAKER</div>
  <div>Design <b>premium location labels</b> with logo + Code128 barcode, export high-res PDFs.</div>
  <div style="font-size:11px;letter-spacing:.2em;margin-top:6px">TYPE LOCATION • TUNE SIZE • DOWNLOAD PDF</div>
</div>
""", unsafe_allow_html=True)

# ================= FEATURE GRID =================
st.markdown("""
<div class="glass-card">
<b>BUILT FOR BUSY WAREHOUSES</b><br>
Generate perfect location labels in under 60 seconds.<br><br>

✔ Smart spacing (logo + text + barcode)<br>
✔ High DPI print quality<br>
✔ Odoo compatible Code128 barcodes<br>
✔ Fully adjustable size & thickness
</div>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    barcode_text = st.text_input("Location Code", "W13-07-07-01-02")
    c1,c2 = st.columns(2)
    label_width_mm = c1.number_input("Width (mm)",210.0)
    label_height_mm = c2.number_input("Height (mm)",60.0)
    underline_gap_mm = st.slider("Gap (mm)",1.0,10.0,2.0)
    module_height = st.slider("Bar Height",5,40,18)
    module_width = st.slider("Thickness",0.2,1.0,0.45)
    dpi_value = st.slider("DPI",300,1200,600,100)
    preview_btn = st.button("👀 Live Preview")
    download_btn = st.button("⬇️ Download PDF")
    st.markdown('</div>', unsafe_allow_html=True)

# ================= PDF BUILDER =================
def build_pdf():
    logo_img, logo_ir = load_logo()
    if not logo_ir:
        raise Exception("Logo missing")

    bbuf = io.BytesIO()
    barcode.get("code128", barcode_text, writer=ImageWriter()).render({
        "write_text":False,
        "dpi":dpi_value,
        "module_height":module_height,
        "module_width":module_width
    }).save(bbuf,"PNG")
    bbuf.seek(0)

    lw, lh = label_width_mm*mm, label_height_mm*mm
    buf = io.BytesIO()
    c = canvas.Canvas(buf,(lw,lh))
    c.drawImage(ImageReader(bbuf),10,lh/2,width=lw-20,height=lh/2-10,mask='auto')
    c.drawImage(logo_ir,10,10,width=lh/2,height=lh/2,mask='auto')
    c.setFont("Helvetica-Bold",28)
    c.drawString(lh/2+20,lh/4,barcode_text)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

# ================= MAIN =================
if preview_btn or download_btn:
    try:
        pdf = build_pdf()
        st.download_button("Download PDF",pdf,file_name=f"{barcode_text}.pdf",mime="application/pdf")
    except Exception as e:
        st.error(e)
