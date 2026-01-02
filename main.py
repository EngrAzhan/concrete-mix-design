import streamlit as st
import pandas as pd
import base64
import plotly.graph_objects as go
from fpdf import FPDF

# --- PAGE SETUP ---
st.set_page_config(page_title="Concrete Calc - Pro 3D Edition", layout="wide")

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
            background-color: rgba(255, 255, 255, 0.94);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        </style>
        """,
        unsafe_allow_html=True
        )
    except FileNotFoundError:
        st.warning("Background image 'background.jpg' not found.")

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
    dry_factor = st.number_input("Dry Volume Factor", value=1.5400, format="%.4f")
    wastage_percent = st.number_input("Wastage (%)", value=5.0000, format="%.4f")
    wastage_factor = 1 + (wastage_percent / 100)

    st.header("⚖️ 3. Material Densities")
    u_dens_c = st.number_input("Cement Density", value=def_c, format="%.4f")
    u_dens_s = st.number_input("Sand Density", value=def_s, format="%.4f")
    u_dens_a = st.number_input("Stone Density", value=def_a, format="%.4f")

# --- 3D VISUALIZATION LOGIC ---
def draw_3d_specimen(l, w, h):
    fig = go.Figure(data=[
        go.Mesh3d(
            # 8 vertices of the prism
            x=[0, l, l, 0, 0, l, l, 0],
            y=[0, 0, w, w, 0, 0, w, w],
            z=[0, 0, 0, 0, h, h, h, h],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            opacity=0.7,
            color='lightgrey',
            flatshading=True
        )
    ])
    fig.update_layout(
        scene=dict(
            xaxis=dict(nticks=4, range=[-1, max(l,w,h)+1]),
            yaxis=dict(nticks=4, range=[-1, max(l,w,h)+1]),
            zaxis=dict(nticks=4, range=[-1, max(l,w,h)+1]),
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=400
    )
    return fig

# --- CALCULATIONS ---
wet_volume = l * w * h
dry_volume = wet_volume * dry_factor * wastage_factor

# Identify Shape
if l == w == h: shape_name = "Cube"
elif l > h*2 and w > h*2: shape_name = "Slab"
elif l > w and l > h: shape_name = "Beam"
elif h > l and h > w: shape_name = "Column"
else: shape_name = "Specimen"

# --- MAIN PAGE DISPLAY ---
st.title(f"🏗️ 3D {shape_name} Mix Design Calculator")
st.markdown("---")

col_vis, col_inp = st.columns([1, 1])

with col_vis:
    st.subheader(f"3D {shape_name} Visualization")
    st.plotly_chart(draw_3d_specimen(l, w, h), use_container_width=True)

with col_inp:
    st.subheader("Mix Proportion Inputs")
    c_ratio = st.number_input("Cement Ratio", value=1.0000, format="%.4f")
    s_ratio = st.number_input("Sand Ratio", value=2.0000, format="%.4f")
    a_ratio = st.number_input("Stone Ratio", value=4.0000, format="%.4f")
    
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
    "Material": ["Cement", "Sand", "Stone"],
    f"Volume ({v_unit})": [f"{vol_c:.4f}", f"{vol_s:.4f}", f"{vol_a:.4f}"],
    f"Weight ({w_unit})": [f"{weight_c:.4f}", f"{weight_s:.4f}", f"{weight_a:.4f}"]
})
st.table(res_df)

# --- METHODOLOGY ---
st.markdown("---")
st.header("🧮 Step-by-Step Methodology")

st.markdown(f"### 1. {shape_name} Volume Calculation")

st.latex(r"V_{wet} = L \times W \times H")
st.code(f"{l:.4f} × {w:.4f} × {h:.4f} = {wet_volume:.4f} {v_unit}")

st.markdown("### 2. Shrinkage and Wastage Adjustment")

st.latex(r"V_{dry} = V_{wet} \times \text{Dry Factor} \times \text{Wastage Factor}")
st.code(f"{wet_volume:.4f} × {dry_factor:.4f} × {wastage_factor:.4f} = {dry_volume:.4f} {v_unit}")

st.markdown("### 3. Volumetric Proportioning")
st.latex(r"V_{material} = \frac{\text{Ratio Part}}{\sum \text{Ratios}} \times V_{dry}")
st.code(f"Cement Vol = ({c_ratio:.4f} / {total_ratio:.4f}) × {dry_volume:.4f} = {vol_c:.4f} {v_unit}")

st.markdown("### 4. Weight Conversion")
st.write("We convert the calculated volume of each material into its required weight using the bulk densities provided in the sidebar.")
st.latex(r"\text{Weight} = \text{Volume} \times \text{Density}")

# Displaying all three material weight calculations
st.code(f"""
Cement Weight: {vol_c:.4f} {v_unit} × {u_dens_c:.4f} = {weight_c:.4f} {w_unit}
Sand Weight:   {vol_s:.4f} {v_unit} × {u_dens_s:.4f} = {weight_s:.4f} {w_unit}
Stone Weight:  {vol_a:.4f} {v_unit} × {u_dens_a:.4f} = {weight_a:.4f} {w_unit}
""")

st.success(f"**Total Material Weight:** {weight_c + weight_s + weight_a:.4f} {w_unit}")
# --- PDF GENERATION ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"{shape_name} Concrete Mix Design Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Shape Detected: {shape_name}", ln=True)
    pdf.cell(200, 10, f"Dimensions: {l}x{w}x{h} {v_unit[0]}", ln=True)
    pdf.cell(200, 10, f"Total Weight: {weight_c + weight_s + weight_a:.4f} {w_unit}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

if st.button("Generate PDF Report"):
    pdf_out = create_pdf()
    st.download_button(label="📥 Download Result PDF", data=pdf_out, file_name=f"{shape_name}_Report.pdf", mime="application/pdf")





