import streamlit as st
from fpdf import FPDF
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="Concrete Mix & Quantity Calculator", layout="wide")


# --- PDF GENERATION FUNCTION ---
def create_pdf(data_vol, data_weight, wet_v, dry_v):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Concrete Mix Design Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Wet Volume: {wet_v:.3f} ft3", ln=True)
    pdf.cell(200, 10, f"Dry Volume: {dry_v:.3f} ft3", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, "Material Quantities:", ln=True)
    for index, row in data_vol.iterrows():
        pdf.cell(200, 10, f"{row['Material']}: {row['Volume (ft³)']} ft3", ln=True)
    return pdf.output(dest='S').encode('latin-1')


# --- HEADER ---
st.title("🏗️ Concrete Mix Design & Quantity Calculator")
st.caption("Professional ACI-based material estimator")

# --- SIDEBAR: Dimensions & Factors ---
with st.sidebar:
    st.header("Specimen Dimensions (ft)")
    l = st.number_input("Length (L)", value=1.0)
    h = st.number_input("Height (H)", value=1.0)
    w = st.number_input("Width (W)", value=1.0)

    st.write("---")
    st.header("Factors")
    dry_factor = st.number_input("Dry Factor", value=1.54)
    wastage = st.number_input("Wastage (e.g. 0.05 for 5%)", value=0.05)

# --- MAIN SECTION: Mix Ratio ---
st.subheader("Materials Mix Ratio (C:FA:CA)")
c1, c2, c3 = st.columns(3)
with c1: c_ratio = st.number_input("Cement", value=1.0)
with c2: fa_ratio = st.number_input("Fine Aggregate", value=2.0)
with c3: ca_ratio = st.number_input("Coarse Aggregate", value=4.0)

# --- CALCULATIONS ---
wet_volume = l * w * h
total_ratio = c_ratio + fa_ratio + ca_ratio
final_dry_vol = (wet_volume * dry_factor) * (1 + wastage)

v_c = (c_ratio / total_ratio) * final_dry_vol
v_fa = (fa_ratio / total_ratio) * final_dry_vol
v_ca = (ca_ratio / total_ratio) * final_dry_vol

# Weight conversions (Approximate KG per cubic foot)
w_c, w_fa, w_ca = v_c * 40.77, v_fa * 45.30, v_ca * 43.80

# --- DISPLAY RESULTS ---
st.markdown(f"### Selected Ratio: {c_ratio}:{fa_ratio}:{ca_ratio}")
col_v1, col_v2 = st.columns(2)
col_v1.metric("Wet Volume (ft³)", f"{wet_volume:.3f}")
col_v2.metric("Dry Volume (+Wastage)", f"{final_dry_vol:.3f}")

# Table 1: Volumes
df_vol = pd.DataFrame({
    "Material": ["Cement", "Fine Aggregate", "Coarse Aggregate"],
    "Volume (ft³)": [round(v_c, 3), round(v_fa, 3), round(v_ca, 3)],
    "Notes": [f"{round(v_c / 1.25, 2)} Bags (1.25ft3/bag)", "", ""]
})
st.subheader("Required Material Volumes")
st.table(df_vol)

# Table 2: Weights
df_weight = pd.DataFrame({
    "Material": ["Cement", "Fine Aggregate", "Coarse Aggregate"],
    "Weight (Kg)": [round(w_c, 2), round(w_fa, 2), round(w_ca, 2)]
})
st.subheader("Required Material Weights")
st.table(df_weight)

# --- DOWNLOAD PDF ---
pdf_data = create_pdf(df_vol, df_weight, wet_volume, final_dry_vol)
st.download_button(label="📥 Download Result PDF", data=pdf_data, file_name="Concrete_Report.pdf",
                   mime="application/pdf")