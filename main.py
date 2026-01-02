import streamlit as st
import pandas as pd
import base64
from fpdf import FPDF

# --- PAGE SETUP ---
st.set_page_config(page_title="Concrete Calc - Pro Edition", layout="wide")

# --- FUNCTION TO SET LOCAL BACKGROUND ---
def add_bg_from_local(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read())
        st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string.decode()}");
            background-attachment: fixed;
            background-size: cover;
        }}
        [data-testid="stVerticalBlock"] {{
            background-color: rgba(255, 255, 255, 0.92);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        </style>
        """,
        unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning("Background image 'background.jpg' not found. Please upload it to your GitHub folder.")

add_bg_from_local('background.jpg')

# --- SIDEBAR: INPUTS ---
with st.sidebar:
    st.header("📐 1. Dimensions")
    unit_system = st.selectbox("Unit System", ["Metric (SI)", "Imperial (BG)"])
    
    if unit_system == "Metric (SI)":
        l = st.number_input("Length (m)", value=1.0000, format="%.4f")
        w = st.number_input("Width (m)", value=1.0000, format="%.4f")
        h = st.number_input("Height (m)", value=1.0000, format="%.4f")
        v_unit, w_unit = "m³", "kg"
        def_c, def_s, def_a = 1440.0000, 1600.0000, 1550.0000
    else:
        l = st.number_input("Length (ft)", value=1.0000, format="%.4f")
        w = st.number_input("Width (ft)", value=1.0000, format="%.4f")
        h = st.number_input("Height (ft)", value=1.0000, format="%.4f")
        v_unit, w_unit = "ft³", "lb"
        def_c, def_s, def_a = 94.0000, 100.0000, 105.0000

    st.header("⚙️ 2. Design Factors")
    dry_factor = st.number_input("Dry Volume Factor", value=1.54)
    wastage_percent = st.number_input("Wastage (%)", value=5)
    wastage_factor = 1 + (wastage_percent / 100)

    st.header("⚖️ 3. Material Densities")
    u_dens_c = st.number_input("Cement Density", value=def_c)
    u_dens_s = st.number_input("Sand Density", value=def_s)
    u_dens_a = st.number_input("Stone Density", value=def_a)

# --- CALCULATIONS ---
wet_volume = l * w * h
dry_volume = wet_volume * dry_factor * wastage_factor

# --- MAIN PAGE DISPLAY ---
st.title("🏗️ Precise Concrete Mix & Quantity Calculator")
st.markdown("---")

st.subheader("Mix Proportion Inputs")
c_col, s_col, a_col = st.columns(3)
c_ratio = c_col.number_input("Cement Ratio", value=1.0000, format="%.4f")
s_ratio = s_col.number_input("Sand Ratio", value=2.0000, format="%.4f")
a_ratio = a_col.number_input("Stone Ratio", value=4.0000, format="%.4f")

total_ratio = c_ratio + s_ratio + a_ratio
vol_c = (c_ratio / total_ratio) * dry_volume
vol_s = (s_ratio / total_ratio) * dry_volume
vol_a = (a_ratio / total_ratio) * dry_volume

weight_c = vol_c * u_dens_c
weight_s = vol_s * u_dens_s
weight_a = vol_a * u_dens_a

# Results Section
m1, m2 = st.columns(2)
m1.metric("Total Wet Volume", f"{wet_volume:.4f} {v_unit}")
m2.metric("Total Dry Volume (+Wastage)", f"{dry_volume:.4f} {v_unit}")

res_df = pd.DataFrame({
    "Material": ["Cement", "Fine Aggregate (Sand)", "Coarse Aggregate (Stone)"],
    f"Volume ({v_unit})": [f"{vol_c:.4f}", f"{vol_s:.4f}", f"{vol_a:.4f}"],
    f"Weight ({w_unit})": [f"{weight_c:.4f}", f"{weight_s:.4f}", f"{weight_a:.4f}"]
})
st.table(res_df)

# --- HOW IT WORKS SECTION (Directly below) ---
st.markdown("---")
st.header("🧮 Step-by-Step Methodology")

st.markdown("### 1. Structure Volume")
st.latex(r"V_{wet} = L \times W \times H")
st.code(f"{l:.4f} × {w:.4f} × {h:.4f} = {wet_volume:.4f} {v_unit}")

st.markdown("### 2. Shrinkage and Wastage Adjustment")
st.write(f"We convert wet volume to dry volume using a factor of **{dry_factor:.4f}** and adding **{wastage_percent:.4f}%** wastage.")
st.latex(r"V_{dry} = V_{wet} \times \text{Dry Factor} \times \text{Wastage Factor}")
st.code(f"{wet_volume:.4f} × {dry_factor:.4f} × {wastage_factor:.4f} = {dry_volume:.4f} {v_unit}")



st.markdown("### 3. Volumetric Proportioning")
st.latex(r"V_{material} = \frac{\text{Ratio Part}}{\text{Total Ratio}} \times V_{dry}")
st.write(f"Total parts: {c_ratio:.4f} + {s_ratio:.4f} + {a_ratio:.4f} = **{total_ratio:.4f}**")
st.code(f"Cement Vol = ({c_ratio:.4f} / {total_ratio:.4f}) × {dry_volume:.4f} = {vol_c:.4f} {v_unit}")

st.markdown("### 4. Weight Conversion")
st.latex(r"\text{Weight} = \text{Volume} \times \text{Density}")
st.code(f"Cement: {vol_c:.4f} × {u_dens_c:.4f} = {weight_c:.4f} {w_unit}")
st.code(f"Sand: {vol_s:.4f} × {u_dens_s:.4f} = {weight_s:.4f} {w_unit}")
st.code(f"Stone: {vol_a:.4f} × {u_dens_a:.4f} = {weight_a:.4f} {w_unit}")

# --- PDF GENERATION ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Concrete Mix Design Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Wet Volume: {wet_volume:.4f} {v_unit}", ln=True)
    pdf.cell(200, 10, f"Dry Volume: {dry_volume:.4f} {v_unit}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, "Material Quantities:", ln=True)
    pdf.cell(200, 10, f"Cement: {weight_c:.4f} {w_unit}", ln=True)
    pdf.cell(200, 10, f"Sand: {weight_s:.4f} {w_unit}", ln=True)
    pdf.cell(200, 10, f"Stone: {weight_a:.4f} {w_unit}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

st.markdown("---")
if st.button("Generate PDF Report"):
    pdf_out = create_pdf()
    st.download_button(label="📥 Download Result PDF", data=pdf_out, file_name="Concrete_Report.pdf", mime="application/pdf")



