import streamlit as st
import pandas as pd
import base64
import plotly.graph_objects as go
from fpdf import FPDF
import io

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
        /* 1. Background and Containers */
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string.decode()}");
            background-attachment: fixed;
            background-size: cover;
        }}
        [data-testid="stVerticalBlock"] {{
            background-color: rgba(20, 20, 20, 0.9) !important;
            padding: 30px;
            border-radius: 15px;
        }}
        /* 1. FIXING THE GREY METRIC NUMBERS (image_f9c37c) */
        [data-testid="stMetricValue"] {{
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            font-weight: bold !important;
        }}

        /* 2. OPTIONAL: BRIGHTEN THE LABELS ABOVE THE NUMBERS */
        [data-testid="stMetricLabel"] p {{
            color: #FFB300 !important;
            font-size: 1.1rem !important;
        }}
        /* 2. Header Fixes */
        [data-testid="stHeader"] {{
            background-color: white !important;
        }}

        /* 3. MAIN CONTENT CONTAINER */
        [data-testid="stVerticalBlock"] {{
            background-color: rgba(20, 20, 20, 0.9) !important;
            padding: 30px;
            border-radius: 15px;
        }}

        /* 4. BUTTON STYLING */
        div.stButton > button {{
            background-color: #FFB300 !important;
            color: #000000 !important;
            font-weight: bold !important;
        }}

        /* 5. CODE BOXES */
        code {{
            color: #FFB300 !important;
            background-color: #1a1a1a !important;
        }}

       /* 3. Global Text & Headers */
        p, span, label, li {{
            color: #FFFFFF !important;
        }}
        h1, h2, h3, h4, b, strong {{
            color: #FFB300 !important;
        }}
        
        /* 7. OFFICIAL DATA TABLE - THE "INVISIBLE" FIX */
        div[data-testid="stTable"] {{
            background-color: rgba(0, 0, 0, 0.85) !important;
            border: 2px solid #FFB300 !important;
            border-radius: 10px !important;
            padding: 10px !important;
        }}

        div[data-testid="stTable"] table {{
            color: #FFFFFF !important;
        }}

        div[data-testid="stTable"] thead tr th {{
            background-color: #FFB300 !important;
            color: #000000 !important;
            font-weight: bold !important;
        }}

        div[data-testid="stTable"] tbody tr td {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }}

        /* MOBILE RESPONSIVE TABLE FIX */
        @media only screen and (max-width: 600px) {{
            div[data-testid="stTable"] {{
                overflow-x: auto !important;
                display: block !important;
                width: 100% !important;
            }}
            div[data-testid="stTable"] table {{
                min-width: 600px !important; /* Forces enough width to stay readable */
            }}
        }}

        /* ENSURE DATA TABLE HEADERS DON'T WRAP */
        div[data-testid="stTable"] thead tr th {{
            white-space: nowrap !important;
            padding: 10px 20px !important;
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
    dry_factor = st.number_input("Dry Volume Factor", value=1.54)
    wastage_percent = st.number_input("Wastage (%)", value=5)
    wastage_factor = 1 + (wastage_percent / 100)

    st.header("⚖️ 3. Material Densities")
    u_dens_c = st.number_input("Cement Density", value=def_c)
    u_dens_s = st.number_input("Sand Density", value=def_s)
    u_dens_a = st.number_input("Stone Density", value=def_a)

    st.header("💧 4. Water Content")
    wc_ratio = st.number_input("Water-Cement (W/C) Ratio", value=0.50)

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
            opacity=0.6,
            color='lightcoral',
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

# --- NEW: HORIZONTAL HERO IMAGE WITH ERROR HANDLING ---
try:
    st.image("bg.png", use_container_width=True)
except Exception:
    # If bg.jpeg is missing, use a professional online placeholder to keep the app running
    st.image("https://images.unsplash.com/photo-1541888946425-d81bb19480c5?q=80&w=2000&auto=format&fit=crop", 
             use_container_width=True)

# --- MAIN PAGE DISPLAY ---
# This removes the double title and cleans up the header
st.title("🏙 Concrete Mix Design Calculator")
st.markdown("---")

col_vis, col_inp = st.columns([1, 1])

with col_vis:
    st.subheader(f"3D Specimen ({shape_name}) Visualization")
    st.plotly_chart(draw_3d_specimen(l, w, h), use_container_width=True)

with col_inp:
    st.subheader("Mix Proportion Inputs")
    c_ratio = st.number_input("Cement Ratio", value=1)
    s_ratio = st.number_input("Sand Ratio", value=2)
    a_ratio = st.number_input("Stone Ratio", value=4)

    # --- THIS FILLS THE GAP (image_ee44ea) ---
    st.markdown("---")
    try:
        # Check if the file name matches your uploaded file exactly
        st.image("image_ede32d.png", caption="Concrete Mixture", use_container_width=True)
    except Exception:
        st.warning("⚠️ image_ede32d.png not found. Please check the filename in your folder.")

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
# --- ADD THIS: STANDARDS & WORKABILITY SECTION ---
st.markdown("---")
st.header("📋 Standards & Recommended Workability")

# 1. Interactive Slump Selection
col_slump1, col_slump2 = st.columns([1, 2])
with col_slump1:
    st.subheader("🍙 Target Slump")
    slump_val = st.number_input("Enter Target Slump (mm)", value=100, step=5)
    
    # Selection logic based on ACI 211.1
    if slump_val < 25:
        workability = "Very Low / Stiff"
        color = "red"
    elif 25 <= slump_val < 75:
        workability = "Low / Plastic"
        color = "orange"
    elif 75 <= slump_val < 125:
        workability = "Medium"
        color = "green"
    else:
        workability = "High / Flowing"
        color = "blue"
    
    st.markdown(f"**Workability Class:** :{color}[{workability}]")


    # --- ADDED COMBINED SLUMP IMAGE HERE ---
    st.markdown("---")
    try:
        # Make sure the file name matches exactly what you uploaded to GitHub
        st.image("slump_combined.png", caption="Concrete Slump Test:    Types & Procedure ", use_container_width=True)
    except:
        st.info("💡 Upload 'slump_combined.png' to your folder to display the technical diagram.")

with col_slump2:
    st.subheader("ACI 211.1 Reference Guide")
    st.write("Recommended slumps for various types of construction (Table 6.3.1):")
    
    standards_data = {
        "Type of Construction": [
            "Reinforced foundation walls and footings",
            "Beams and reinforced walls",
            "Building columns",
            "Pavements and slabs",
            "Mass concrete"
        ],
        "Slump (Inches)": ["1\" – 3\"", "1\" – 4\"", "1\" – 4\"", "1\" – 3\"", "1\" – 2\""],
        "Slump (mm)": ["25 – 75 mm", "25 – 100 mm", "25 – 100 mm", "25 – 75 mm", "25 – 50 mm"]
    }
    st.table(pd.DataFrame(standards_data))

# 2. Official Sources & Notes
st.info("""
**Engineering Reference:**
* **ASTM C143:** Standard Test Method for Slump of Hydraulic-Cement Concrete.
* **ACI 211.1:** Standard Practice for Selecting Proportions for Normal, Heavyweight, and Mass Concrete.
""")

# --- CONTINUING TO YOUR METHODOLOGY SECTION ---




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
import tempfile
import os

# --- PDF GENERATION ---
import tempfile
import os

def create_pdf(shape_name, l, w, h, v_unit, w_unit, c_ratio, s_ratio, a_ratio, wc_ratio, 
               wet_vol, dry_vol, dry_f, waste_p, weight_c, weight_s, weight_a, weight_water, 
               fig, slump_val, workability):
    
    pdf = FPDF()
    pdf.add_page()
    
    # --- 1. HEADER ---
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(255, 179, 0) # Gold theme color
    pdf.cell(200, 15, "Concrete Mix Quantity & Workability Report", ln=True, align='C')
    pdf.set_draw_color(255, 179, 0)
    pdf.line(10, 25, 200, 25)
    pdf.ln(5)

    # --- 2. DESIGN SPECS & SLUMP DATA ---
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "1. Design Specifications", ln=True)
    pdf.set_font("Arial", '', 11)
    
    col_width = 90
    pdf.cell(col_width, 7, f"Specimen Type: {shape_name}", ln=0)
    pdf.cell(col_width, 7, f"W/C Ratio: {wc_ratio}", ln=1)
    pdf.cell(col_width, 7, f"Target Slump: {slump_val} mm", ln=0)
    pdf.cell(col_width, 7, f"Workability: {workability}", ln=1)
    pdf.cell(col_width, 7, f"Dry Factor: {dry_f}", ln=0)
    pdf.cell(col_width, 7, f"Wastage: {waste_p}%", ln=1)
    pdf.ln(5)

    # --- 3. 3D VISUALIZATION ---
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "2. Specimen Visualization", ln=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        try:
            fig.write_image(tmpfile.name, engine="kaleido", width=600, height=400)
            pdf.image(tmpfile.name, x=40, w=130)
        except Exception:
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(200, 10, "(Image capture failed: Ensure kaleido is installed)", ln=True)
        finally:
            tmp_path = tmpfile.name
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    pdf.ln(5)

    # --- 4. MATERIAL TABLE ---
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "3. Required Material Weights", ln=True)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_fill_color(255, 179, 0) 
    pdf.cell(60, 10, "Material", 1, 0, 'C', True)
    pdf.cell(60, 10, "Ratio", 1, 0, 'C', True)
    pdf.cell(60, 10, f"Weight ({w_unit})", 1, 1, 'C', True)
    
    pdf.set_font("Arial", '', 11)
    mats = [["Cement", c_ratio, weight_c], ["Sand", s_ratio, weight_s], 
            ["Stone", a_ratio, weight_a], ["Water", wc_ratio, weight_water]]
    for m in mats:
        pdf.cell(60, 10, f" {m[0]}", 1)
        pdf.cell(60, 10, f" {m[1]}", 1, 0, 'C')
        pdf.cell(60, 10, f" {m[2]:.4f}", 1, 1, 'C')

    # --- 5. METHODOLOGY ---
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "4. Step-by-Step Methodology", ln=True)
    pdf.set_font("Arial", '', 10)
    method = [
        f"Step 1: Wet Volume (LxWxH) = {wet_vol:.4f} {v_unit}",
        f"Step 2: Dry Volume (incl. {waste_p}% wastage) = {dry_vol:.4f} {v_unit}",
        f"Step 3: Total Weight (C+S+A+W) = {weight_c + weight_s + weight_a + weight_water:.4f} {w_unit}",
        f"Step 4: Slump Verification = {slump_val}mm (Class: {workability})"
    ]
    for step in method:
        pdf.multi_cell(0, 7, step)

    return pdf.output(dest='S').encode('latin-1')

# --- FINAL BUTTON TRIGGER ---
st.markdown("---")
if st.button("🚀 Generate Detailed PDF Report"):
    # Generate fresh visual for PDF
    current_fig = draw_3d_specimen(l, w, h)
    
    # Build PDF with all data including Slump
    pdf_out = create_pdf(
        shape_name, l, w, h, v_unit, w_unit, c_ratio, s_ratio, a_ratio, wc_ratio,
        wet_volume, dry_volume, dry_factor, wastage_percent,
        weight_c, weight_s, weight_a, weight_water, 
        current_fig, slump_val, workability
    )
    
    st.download_button(
        label="📥 Download Result PDF", 
        data=pdf_out, 
        file_name=f"{shape_name}_Full_Report.pdf", 
        mime="application/pdf"
    )












































