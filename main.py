import streamlit as st
from fpdf import FPDF
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="Global Concrete Calculator", layout="wide")

# --- PHYSICAL CONSTANTS & CONVERSIONS ---
# Base densities in SI (kg/m3)
DENSITY_SI = {"Cement": 1440, "Sand": 1600, "Stone": 1550}
# Base densities in BG (lb/ft3)
DENSITY_BG = {"Cement": 94, "Sand": 100, "Stone": 105}

# --- PDF GENERATION ---
def create_pdf(df_vol, df_weight, wet_v, dry_v, v_unit, w_unit):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Concrete Mix & Quantity Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Wet Volume: {wet_v:.3f} {v_unit}", ln=True)
    pdf.cell(200, 10, f"Dry Volume: {dry_v:.3f} {v_unit}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, "Material Breakdown:", ln=True)
    for i in range(len(df_vol)):
        m = df_vol.iloc[i]['Material']
        v = df_vol.iloc[i]['Volume']
        w = df_weight.iloc[i][f'Weight ({w_unit})']
        pdf.cell(200, 10, f"- {m}: {v} {v_unit} | {w} {w_unit}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- SIDEBAR: SYSTEM & DIMENSIONS ---
with st.sidebar:
    st.header("🌍 System Selection")
    system = st.radio("Choose Unit System", ["Metric (SI) - m, kg", "Imperial (BG) - ft, lb"])
    
    st.write("---")
    st.header("📏 Dimensions")
    
    if "Metric" in system:
        v_unit, w_unit = "m³", "kg"
        l = st.number_input("Length (meters)", value=1.0)
        w = st.number_input("Width (meters)", value=1.0)
        h = st.number_input("Height (meters)", value=1.0)
    else:
        v_unit, w_unit = "ft³", "lb"
        l = st.number_input("Length (feet)", value=1.0)
        w = st.number_input("Width (feet)", value=1.0)
        h = st.number_input("Height (feet)", value=1.0)

    st.write("---")
    st.header("⚙️ Design Factors")
    dry_factor = st.number_input("Dry Factor (Shrinkage)", value=1.54)
    wastage = st.number_input("Wastage (Decimal)", value=0.05)

# --- MAIN SECTION ---
st.title("🏗️ Concrete Quantity Estimator (SI & BG)")

# --- CALCULATIONS ---
wet_vol = l * w * h
dry_vol = (wet_vol * dry_factor) * (1 + wastage)

st.subheader("Mix Proportions (C : FA : CA)")
c1, c2, c3 = st.columns(3)
with c1: c_ratio = st.number_input("Cement", value=1.0)
with c2: fa_ratio = st.number_input("Fine Aggregate", value=2.0)
with c3: ca_ratio = st.number_input("Coarse Aggregate", value=4.0)

total_ratio = c_ratio + fa_ratio + ca_ratio

# Calculate Individual Volumes
vol_c = (c_ratio / total_ratio) * dry_vol
vol_fa = (fa_ratio / total_ratio) * dry_vol
vol_ca = (ca_ratio / total_ratio) * dry_vol

# Calculate Individual Weights
if "Metric" in system:
    weight_c = vol_c * DENSITY_SI["Cement"]
    weight_fa = vol_fa * DENSITY_SI["Sand"]
    weight_ca = vol_ca * DENSITY_SI["Stone"]
    bag_text = f"{round(weight_c/50, 1)} Bags (50kg each)"
else:
    weight_c = vol_c * DENSITY_BG["Cement"]
    weight_fa = vol_fa * DENSITY_BG["Sand"]
    weight_ca = vol_ca * DENSITY_BG["Stone"]
    bag_text = f"{round(weight_c/94, 1)} Bags (94lb each)"

# --- DISPLAY ---
col_v1, col_v2 = st.columns(2)
col_v1.metric("Wet Volume", f"{wet_vol:.3f} {v_unit}")
col_v2.metric("Dry Volume", f"{dry_vol:.3f} {v_unit}")

st.write("---")
tab_res, tab_info = st.tabs(["📊 Quantities", "📖 Unit Specs"])

with tab_res:
    df_vol = pd.DataFrame({
        "Material": ["Cement", "Fine Aggregate", "Coarse Aggregate"],
        "Volume": [round(vol_c, 3), round(vol_fa, 3), round(vol_ca, 3)],
        "Unit": [v_unit, v_unit, v_unit]
    })
    st.subheader(f"Volumes ({v_unit})")
    st.table(df_vol)
    
    df_weight = pd.DataFrame({
        "Material": ["Cement", "Fine Aggregate", "Coarse Aggregate"],
        f"Weight ({w_unit})": [round(weight_c, 2), round(weight_fa, 2), round(weight_ca, 2)]
    })
    st.subheader(f"Weights ({w_unit})")
    st.table(df_weight)
    st.success(f"**Packing Hint:** {bag_text}")

with tab_info:
    st.markdown("### Conversion & Density Log")
    if "Metric" in system:
        st.write("Using SI System: 1m³ concrete requires ~1.54m³ dry materials.")
        st.write(f"Cement Density: {DENSITY_SI['Cement']} kg/m³")
    else:
        st.write("Using BG System: 1ft³ concrete requires ~1.54ft³ dry materials.")
        st.write(f"Cement Density: {DENSITY_BG['Cement']} lb/ft³")

# --- EXPORT ---
pdf_data = create_pdf(df_vol, df_weight, wet_vol, dry_vol, v_unit, w_unit)
st.download_button("📥 Download Report", data=pdf_data, file_name="Concrete_Design_Report.pdf")
