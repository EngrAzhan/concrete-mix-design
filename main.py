import streamlit as st
import pandas as pd
import base64

# --- PAGE SETUP ---
st.set_page_config(page_title="Concrete Calc - Pro Edition", layout="wide")

# --- FUNCTION TO SET LOCAL BACKGROUND ---
def add_bg_from_local(image_file):
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
    /* This part makes the content area slightly transparent so you can see the image */
    [data-testid="stVerticalBlock"] {{
        background-color: rgba(255, 255, 255, 0.85);
        padding: 20px;
        border-radius: 15px;
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

# --- APPLY BACKGROUND ---
# Make sure 'my_background.jpg' is in the same folder as main.py
try:
    add_bg_from_local('background.jpg') 
except FileNotFoundError:
    st.warning("Background image not found. Please upload 'background.jpg' to your GitHub folder.")

# --- TITLE & HEADER ---
st.title("🏗️ Precise Concrete Mix & Quantity Calculator")
st.markdown("---")

# --- SIDEBAR (Remains the same as previous version) ---
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
    dry_factor = st.number_input("Dry Volume Factor", value=1.5400, format="%.4f")
    wastage_percent = st.number_input("Wastage (%)", value=5.0000, format="%.4f")
    wastage_factor = 1 + (wastage_percent / 100)

    st.header("⚖️ 3. Material Densities")
    u_dens_c = st.number_input("Cement Density", value=def_c, format="%.4f")
    u_dens_s = st.number_input("Sand (FA) Density", value=def_s, format="%.4f")
    u_dens_a = st.number_input("Stone (CA) Density", value=def_a, format="%.4f")

# --- CALCULATIONS ---
wet_volume = l * w * h
dry_volume = wet_volume * dry_factor * wastage_factor

# --- TABS ---
tab1, tab2 = st.tabs(["📊 Precise Results", "📝 How it Works"])

with tab1:
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

    m1, m2 = st.columns(2)
    m1.metric("Total Wet Volume", f"{wet_volume:.4f} {v_unit}")
    m2.metric("Total Dry Volume (+Wastage)", f"{dry_volume:.4f} {v_unit}")

    res_df = pd.DataFrame({
        "Material": ["Cement", "Fine Aggregate (Sand)", "Coarse Aggregate (Stone)"],
        f"Volume ({v_unit})": [f"{vol_c:.4f}", f"{vol_s:.4f}", f"{vol_a:.4f}"],
        f"Weight ({w_unit})": [f"{weight_c:.4f}", f"{weight_s:.4f}", f"{weight_a:.4f}"]
    })
    st.table(res_df)

with tab2:
    st.header("Step-by-Step Mix Design Logic")
    st.markdown(f"**Wet Volume:** {wet_volume:.4f}")
    st.markdown(f"**Dry Volume (Factor {dry_factor}):** {dry_volume:.4f}")
    st.code(f"Cement Weight = ({c_ratio} / {total_ratio}) * {dry_volume:.4f} * {u_dens_c}")



