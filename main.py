import streamlit as st
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="High-Precision Concrete Calc", layout="wide")

st.title("🏗️ Precise Concrete Mix & Quantity Calculator")
st.markdown("---")

# --- SIDEBAR: DIMENSIONS, FACTORS & DENSITIES ---
with st.sidebar:
    st.header("📐 1. Dimensions")
    unit_system = st.selectbox("Unit System", ["Metric (SI)", "Imperial (BG)"])
    
    # Using format="%.4f" to force 4 decimal places in inputs
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
    # Added Dry Factor and Wastage as sidebar requirements
    dry_factor = st.number_input("Dry Volume Factor", value=1.54, help="Usually 1.54 - 1.57")
    wastage_percent = st.number_input("Wastage (%)", value=5)
    wastage_factor = 1 + (wastage_percent / 100)

    st.header("⚖️ 3. Material Densities")
    st.caption(f"Input bulk density in {w_unit}/{v_unit}")
    u_dens_c = st.number_input("Cement Density", value=def_c)
    u_dens_s = st.number_input("Sand (FA) Density", value=def_s
    u_dens_a = st.number_input("Stone (CA) Density", value=def_a

# --- CALCULATIONS ---
wet_volume = l * w * h
dry_volume = wet_volume * dry_factor * wastage_factor

# --- TABS ---
tab1, tab2 = st.tabs(["📊 Precise Results", "📝 How it Works (Formulas)"])

with tab1:
    st.subheader("Mix Proportion Inputs")
    c_col, s_col, a_col = st.columns(3)
    c_ratio = c_col.number_input("Cement Ratio", value=1)
    s_ratio = s_col.number_input("Sand Ratio", value=2)
    a_ratio = a_col.number_input("Stone Ratio", value=4)
    
    total_ratio = c_ratio + s_ratio + a_ratio
    
    # Volume Calculations
    vol_c = (c_ratio / total_ratio) * dry_volume
    vol_s = (s_ratio / total_ratio) * dry_volume
    vol_a = (a_ratio / total_ratio) * dry_volume
    
    # Weight Calculations
    weight_c = vol_c * u_dens_c
    weight_s = vol_s * u_dens_s
    weight_a = vol_a * u_dens_a

    # Metrics
    m1, m2 = st.columns(2)
    m1.metric("Total Wet Volume", f"{wet_volume:.4f} {v_unit}")
    m2.metric("Total Dry Volume (+Wastage)", f"{dry_volume:.4f} {v_unit}")

    # Results Table with 4 decimal formatting
    res_df = pd.DataFrame({
        "Material": ["Cement", "Fine Aggregate (Sand)", "Coarse Aggregate (Stone)"],
        f"Volume ({v_unit})": [f"{vol_c:.4f}", f"{vol_s:.4f}", f"{vol_a:.4f}"],
        f"Weight ({w_unit})": [f"{weight_c:.4f}", f"{weight_s:.4f}", f"{weight_a:.4f}"]
    })
    st.table(res_df)

with tab2:
    st.header("Step-by-Step Mix Design Logic")
    
    st.markdown("### 1. Volume Calculation")
    st.code(f"Wet Volume = {l:.4f} × {w:.4f} × {h:.4f} = {wet_volume:.4f} {v_unit}")
    
    st.markdown("### 2. Conversion to Dry Volume")
    st.write(f"Multiplied by Dry Factor (**{dry_factor:.4f}**) and Wastage (**{wastage_factor:.4f}**).")
    st.code(f"Dry Volume = {wet_volume:.4f} × {dry_factor:.4f} × {wastage_factor:.4f} = {dry_volume:.4f} {v_unit}")
    
    st.markdown("### 3. Ratio Proportioning")
    st.write(f"Total Ratio = {c_ratio:.4f} + {s_ratio:.4f} + {a_ratio:.4f} = **{total_ratio:.4f}**")
    st.code(f"Cement Vol = ({c_ratio:.4f} / {total_ratio:.4f}) × {dry_volume:.4f} = {vol_c:.4f} {v_unit}")
    
    st.markdown("### 4. Weight Calculation")
    st.code(f"Cement Weight = {vol_c:.4f} × {u_dens_c:.4f} = {weight_c:.4f} {w_unit}")
    st.code(f"Sand Weight = {vol_s:.4f} × {u_dens_s:.4f} = {weight_s:.4f} {w_unit}")
    st.code(f"Stone Weight = {vol_a:.4f} × {u_dens_a:.4f} = {weight_a:.4f} {w_unit}")




