import streamlit as st
import pandas as pd

# --- PAGE SETUP ---
st.set_page_config(page_title="Transparent Concrete Calc", layout="wide")

st.title("🏗️ Concrete Mix Design & Quantity Calculator")
st.markdown("---")

# --- SIDEBAR: DIMENSIONS & USER-DEFINED DENSITIES ---
with st.sidebar:
    st.header("📐 1. Dimensions")
    unit_system = st.selectbox("Unit System", ["Metric (SI)", "Imperial (BG)"])
    
    if unit_system == "Metric (SI)":
        l = st.number_input("Length (m)", value=1.0)
        w = st.number_input("Width (m)", value=1.0)
        h = st.number_input("Height (m)", value=1.0)
        v_unit, w_unit = "m³", "kg"
        def_c, def_s, def_a = 1440.0, 1600.0, 1550.0
    else:
        l = st.number_input("Length (ft)", value=1.0)
        w = st.number_input("Width (ft)", value=1.0)
        h = st.number_input("Height (ft)", value=1.0)
        v_unit, w_unit = "ft³", "lb"
        def_c, def_s, def_a = 94.0, 100.0, 105.0

    # --- NEW INPUTS ADDED HERE ---
    st.header("⚙️ 2. Design Factors")
    dry_factor = st.number_input("Dry Volume Factor", value=1.54, help="Commonly 1.54 to 1.57")
    wastage_percent = st.number_input("Wastage (%)", value=5.0)
    wastage_factor = 1 + (wastage_percent / 100)

    st.header("⚖️ 3. Material Densities")
    u_dens_c = st.number_input("Cement Density", value=def_c)
    u_dens_s = st.number_input("Sand (FA) Density", value=def_s)
    u_dens_a = st.number_input("Stone (CA) Density", value=def_a)

# --- CALCULATIONS ---
wet_volume = l * w * h
# Now using the inputs from the sidebar instead of fixed numbers
dry_volume = wet_volume * dry_factor * wastage_factor

# --- TABS FOR USER EXPERIENCE ---
tab1, tab2 = st.tabs(["📊 Calculator Results", "📝 How it Works (Formulas)"])

with tab1:
    st.subheader("Mix Proportion Inputs")
    c_col, s_col, a_col = st.columns(3)
    c_ratio = c_col.number_input("Cement Ratio", value=1.0)
    s_ratio = s_col.number_input("Sand Ratio", value=2.0)
    a_ratio = a_col.number_input("Stone Ratio", value=4.0)
    
    total_ratio = c_ratio + s_ratio + a_ratio
    
    # Material Volumes
    vol_c = (c_ratio / total_ratio) * dry_volume
    vol_s = (s_ratio / total_ratio) * dry_volume
    vol_a = (a_ratio / total_ratio) * dry_volume
    
    # Material Weights (Using User Inputs)
    weight_c = vol_c * u_dens_c
    weight_s = vol_s * u_dens_s
    weight_a = vol_a * u_dens_a

    # Metrics
    m1, m2 = st.columns(2)
    m1.metric("Total Wet Volume", f"{wet_volume:.3f} {v_unit}")
    m2.metric("Total Dry Volume (+Wastage)", f"{dry_volume:.3f} {v_unit}")

    # Results Table
    res_df = pd.DataFrame({
        "Material": ["Cement", "Fine Aggregate (Sand)", "Coarse Aggregate (Stone)"],
        f"Volume ({v_unit})": [round(vol_c, 3), round(vol_s, 3), round(vol_a, 3)],
        f"Weight ({w_unit})": [round(weight_c, 2), round(weight_s, 2), round(weight_a, 2)]
    })
    st.table(res_df)

with tab2:
    st.header("Step-by-Step Mix Design Logic")
    
    st.markdown("""
    ### 1. Volume Calculation
    First, we find the volume of the structure.
    """)
    st.code(f"Wet Volume = Length ({l}) × Width ({w}) × Height ({h}) = {wet_volume:.3f} {v_unit}")
    
    st.markdown("### 2. Conversion to Dry Volume")
    st.write("Concrete shrinks when water is added. We multiply by a **Dry Factor (1.54)** and a **Wastage Factor (1.05)**.")
    st.code(f"Dry Volume = {wet_volume:.3f} × 1.54 × 1.05 = {dry_volume:.3f} {v_unit}")
    
    st.markdown("### 3. Ratio Proportioning")
    st.write(f"Sum of Ratios = {c_ratio} + {s_ratio} + {a_ratio} = **{total_ratio}**")
    st.code(f"Cement Vol = ({c_ratio} / {total_ratio}) × {dry_volume:.3f} = {vol_c:.3f} {v_unit}")
    
    st.markdown("### 4. Weight Calculation (Using your Density Inputs)")
    st.write(f"Weight = Volume × User-Input Density")
    st.code(f"Cement Weight = {vol_c:.3f} × {u_dens_c} = {weight_c:.2f} {w_unit}")
    st.code(f"Sand Weight = {vol_s:.3f} × {u_dens_s} = {weight_s:.2f} {w_unit}")
    st.code(f"Stone Weight = {vol_a:.3f} × {u_dens_a} = {weight_a:.2f} {w_unit}")

