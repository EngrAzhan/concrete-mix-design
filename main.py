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
        /* 1. Background setup */
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string.decode()}");
            background-attachment: fixed;
            background-size: cover;
        }}

        /* 2. FIX: SETTINGS ICON & HEADER (Image cff156) */
        [data-testid="stHeader"] {{
            background-color: white !important;
            border-bottom: 1px solid #ddd;
        }}
        [data-testid="stHeader"] svg {{
            fill: #111 !important;
        }}

        /* 3. MAIN CONTENT CONTAINER */
        [data-testid="stVerticalBlock"] {{
            background-color: rgba(20, 20, 20, 0.9) !important;
            padding: 30px;
            border-radius: 15px;
            margin-top: 20px;
        }}

        /* 4. FIX: INVISIBLE PDF BUTTON (The white-on-white issue) */
        /* This forces the button to have a visible orange border and dark background */
        div.stButton > button {{
            background-color: #FFB300 !important;
            color: #000000 !important;
            border: 2px solid #FFB300 !important;
            font-weight: bold !important;
            width: 100%;
        }}
        div.stButton > button:hover {{
            background-color: #e6a100 !important;
            color: #ffffff !important;
        }}

        /* 5. FIX: METHODOLOGY BOXES (Image d04446 / d05b4b) */
        code {{
            color: #FFB300 !important;
            background-color: #1a1a1a !important;
            padding: 2px 5px !important;
            border-radius: 4px;
        }}
        pre {{
            background-color: #1a1a1a !important;
            border: 1px solid #444 !important;
        }}

        /* 6. GLOBAL TEXT & TABLE FIXES */
        p, span, label, li, [data-testid="stMetricLabel"] {{
            color: #FFFFFF !important;
        }}
        h1, h2, h3, b, strong {{
            color: #FFB300 !important;
        }}
        [data-testid="stMetricValue"] {{
            color: #FFFFFF !important;
        }}
        table, th, td {{
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            color: white !important;
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

    st.header("💧 4. Water Content")
    wc_ratio = st.number_input("Water-Cement (W/C) Ratio", value=0.5000, format="%.4f")

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

# Apply background
add_bg_from_local('background.jpg')

# --- NEW: HORIZONTAL HERO IMAGE ---
# This will appear at the very top of your app content
st.image("bg.jpg", 
         use_container_width=True)

# --- MAIN PAGE DISPLAY ---
st.title(f"🏙 Concrete Mix Design Calculator")
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
    weight_water = wc_ratio * weight_c

# --- RESULTS SECTION WITH IMAGES ---
st.markdown("---")
st.header("🧱 Material Breakdown & Requirements")

# 1. Top Metrics for Volumes
m1, m2 = st.columns(2)
m1.metric("Total Wet Volume", f"{wet_volume:.4f} {v_unit}")
m2.metric("Total Dry Volume (+Wastage)", f"{dry_volume:.4f} {v_unit}")

st.markdown("### Mix Details")

# 2. Visual Cards for Materials
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.image("cement.png")
    st.subheader("Cement")
    st.write(f"**Ratio:** {c_ratio:.1f}")
    st.write(f"**Weight:** {weight_c:.4f} {w_unit}")

with col2:
    st.image("sand.png")
    st.subheader("Sand")
    st.write(f"**Ratio:** {s_ratio:.1f}")
    st.write(f"**Weight:** {weight_s:.4f} {w_unit}")

with col3:
    st.image("coarse.png")
    st.subheader("Stone")
    st.write(f"**Ratio:** {a_ratio:.1f}")
    st.write(f"**Weight:** {weight_a:.4f} {w_unit}")

with col4:
    st.image("water.png")
    st.subheader("Water")
    st.write(f"**W/C Ratio:** {wc_ratio:.2f}")
    st.write(f"**Weight:** {weight_water:.4f} {w_unit}")

# Keep the table below for official reference if needed
st.markdown("#### Official Data Table")
res_df = pd.DataFrame({
    "Material": ["Cement", "Sand", "Stone", "Water"],
    "Ratio": [c_ratio, s_ratio, a_ratio, wc_ratio],
    f"Weight ({w_unit})": [f"{weight_c:.4f}", f"{weight_s:.4f}", f"{weight_a:.4f}", f"{weight_water:.4f}"]
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

st.markdown("### 5. Water Content Calculation")
st.write("Water requirement is calculated based on the weight of the cement using the Water-Cement ratio.")
st.latex(r"W_{water} = W_{cement} \times \text{W/C Ratio}")
st.code(f"Water Weight: {weight_c:.4f} × {wc_ratio:.4f} = {weight_water:.4f} {w_unit}")

# Optional: Convert to Liters for Metric
if unit_system == "Metric (SI)":
    st.info(f"💡 Since 1kg of water ≈ 1 Liter, you need approximately **{weight_water:.2f} Liters** of water.")

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

















