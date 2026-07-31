import streamlit as st
import cmath
import math
import pandas as pd
import numpy as np

# 1. Page Configuration (Must be first)
st.set_page_config(page_title="Power System Analyzer Suite", page_icon="⚡", layout="wide")

# 2. Custom CSS
st.markdown("""
<style>
    [data-testid="stToolbar"] {visibility: hidden;}
    .main-header { font-size: 2.5rem; color: #1E88E5; text-align: center; font-weight: 800; margin-bottom: 0px; }
    .sub-text { text-align: center; color: #6c757d; font-size: 1.1rem; margin-bottom: 30px; }
    .result-card, .node-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #1E88E5; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); text-align: center; }
</style>
""", unsafe_allow_html=True)

# 3. Sidebar Dropdown for Navigation
st.sidebar.header("🔀 Select Calculator")
app_mode = st.sidebar.selectbox(
    "Choose your network topology:",
    [
        "1. Radial System (Voltage Regulation)", 
        "2. Multi-Bus Meshed (Example 5.9)",
        "3. Dynamic Y-Bus Builder (PRO Mode)"
    ]
)
st.sidebar.markdown("---")

# =====================================================================
# APP 1: RADIAL SYSTEM
# =====================================================================
if app_mode == "1. Radial System (Voltage Regulation)":
    st.markdown('<p class="main-header">⚡ Radial System Analyzer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">Complete Assignment Solution Dashboard</p>', unsafe_allow_html=True)

    # SIDEBAR: Inputs for App 1
    st.sidebar.header("⚙️ Radial Parameters")
    
    with st.sidebar.expander("1. Common Base & Gen", expanded=True):
        S_base = st.number_input("Common Base MVA", value=30.0, key="r_sbase")
        V_base1 = st.number_input("Zone 1 Base Voltage (kV)", value=6.6, key="r_vbase1")
        st.divider()
        G_MVA = st.number_input("Gen MVA", value=30.0, key="r_gmva")
        G_kV = st.number_input("Gen kV", value=6.6, key="r_gkv")
        G_X_pu = st.number_input("Gen Reactance X (%)", value=12.0, key="r_gx") / 100.0

    with st.sidebar.expander("2. Transformers", expanded=False):
        T1_MVA = st.number_input("T1 MVA", value=30.0, key="r_t1mva")
        T1_kV_Z1 = st.number_input("T1 kV (Gen Side)", value=6.6, key="r_t1kv1")
        T1_kV_Z2 = st.number_input("T1 kV (Line Side)", value=132.0, key="r_t1kv2")
        T1_X_pu = st.number_input("T1 Reactance X (%)", value=8.0, key="r_t1x") / 100.0
        st.divider()
        T2_MVA = st.number_input("T2 MVA", value=25.0, key="r_t2mva")
        T2_kV_Z2 = st.number_input("T2 kV (Line Side)", value=132.0, key="r_t2kv2")
        T2_kV_Z3 = st.number_input("T2 kV (Load Side)", value=11.0, key="r_t2kv3")
        T2_X_pu = st.number_input("T2 Reactance X (%)", value=7.0, key="r_t2x") / 100.0

    with st.sidebar.expander("3. Line & Load", expanded=False):
        line_R = st.number_input("Line Resistance (Ω)", value=15.0, key="r_liner")
        line_X = st.number_input("Line Reactance (Ω)", value=45.0, key="r_linex")
        st.divider()
        load_MW = st.number_input("Load MW", value=18.0, key="r_loadmw")
        load_pf = st.number_input("Load PF (lagging)", value=0.9, key="r_loadpf")
        load_kV = st.number_input("Load operating kV", value=11.0, key="r_loadkv")

    # BACKGROUND CALCULATIONS (App 1)
    V_base2 = V_base1 * (T1_kV_Z2 / T1_kV_Z1)
    V_base3 = V_base2 * (T2_kV_Z3 / T2_kV_Z2)

    Z_base1 = (V_base1 ** 2) / S_base
    Z_base2 = (V_base2 ** 2) / S_base
    Z_base3 = (V_base3 ** 2) / S_base

    I_base1 = (S_base * 1000) / (math.sqrt(3) * V_base1)
    I_base2 = (S_base * 1000) / (math.sqrt(3) * V_base2)
    I_base3 = (S_base * 1000) / (math.sqrt(3) * V_base3)

    G_X_new = G_X_pu * ((G_kV / V_base1) ** 2) * (S_base / G_MVA)
    T1_X_new = T1_X_pu * ((T1_kV_Z1 / V_base1) ** 2) * (S_base / T1_MVA)
    T2_X_new = T2_X_pu * ((T2_kV_Z3 / V_base3) ** 2) * (S_base / T2_MVA)
    Z_line_pu = complex(line_R, line_X) / Z_base2

    load_MVA = load_MW / load_pf
    S_load_pu = cmath.rect(load_MVA, math.acos(load_pf)) / S_base
    V_load_complex = complex(load_kV / V_base3, 0)
    I_load_pu = (S_load_pu / V_load_complex).conjugate()
    Z_load_pu = V_load_complex / I_load_pu

    Z_series_terminals = complex(0, T2_X_new) + Z_line_pu + complex(0, T1_X_new)
    V_term_pu = V_load_complex + (I_load_pu * Z_series_terminals)
    V_term_kV = abs(V_term_pu) * V_base1
    percent_VR = ((abs(V_term_pu) - abs(V_load_complex)) / abs(V_load_complex)) * 100

    # MAIN DASHBOARD (App 1)
    tab1, tab2 = st.tabs(["📊 Key Results & Assignment Answers", "🔬 Detailed Impedance Network"])

    with tab1:
        st.markdown("### 🎯 Final Voltage Regulation")
        col1, col2, col3 = st.columns(3)
        col1.metric("Terminal Voltage (PU)", f"{abs(V_term_pu):.4f} pu")
        col2.metric("Actual Voltage (kV)", f"{V_term_kV:.2f} kV")
        col3.metric("Voltage Regulation", f"{percent_VR:.2f} %")
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown("### 📝 Assignment Solutions")
        with st.expander("Problem 1: Base Values in Each Zone", expanded=True):
            cz1, cz2, cz3 = st.columns(3)
            cz1.markdown(f"**Zone 1**\n* $V_{{base}}$ = {V_base1:.2f} kV\n* $I_{{base}}$ = {I_base1:.2f} A\n* $Z_{{base}}$ = {Z_base1:.4f} Ω")
            cz2.markdown(f"**Zone 2**\n* $V_{{base}}$ = {V_base2:.2f} kV\n* $I_{{base}}$ = {I_base2:.2f} A\n* $Z_{{base}}$ = {Z_base2:.4f} Ω")
            cz3.markdown(f"**Zone 3**\n* $V_{{base}}$ = {V_base3:.2f} kV\n* $I_{{base}}$ = {I_base3:.2f} A\n* $Z_{{base}}$ = {Z_base3:.4f} Ω")
            
        with st.expander("Problem 2: Per-Unit Reactance"):
            st.markdown(f"* **Generator:** j{G_X_new:.4f} pu\n* **T1:** j{T1_X_new:.4f} pu\n* **T2:** j{T2_X_new:.4f} pu")

        with st.expander("Problem 3: Line Impedance"):
            st.markdown(f"* **Line:** {Z_line_pu.real:.4f} + j{Z_line_pu.imag:.4f} pu")

        with st.expander("Problem 4: Load Representation"):
            st.markdown(f"* **S:** {S_load_pu.real:.4f} + j{S_load_pu.imag:.4f} pu\n* **I:** {I_load_pu.real:.4f} + j{I_load_pu.imag:.4f} pu\n* **Z:** {Z_load_pu.real:.4f} + j{Z_load_pu.imag:.4f} pu")
            
        with st.expander("Problem 5: Voltage Regulation"):
            st.markdown(f"* **$V_{{gen\_pu}}$:** {V_term_pu.real:.4f} + j{V_term_pu.imag:.4f} pu\n* **Magnitude:** {abs(V_term_pu):.4f} pu\n* **Actual:** {V_term_kV:.2f} kV")

    with tab2:
        st.markdown("### 🧩 Per-Unit Impedance Breakdown")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="result-card"><b>T1</b><br>j{T1_X_new:.4f} pu</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="result-card"><b>Line</b><br>{Z_line_pu.real:.4f} + j{Z_line_pu.imag:.4f} pu</div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="result-card"><b>T2</b><br>j{T2_X_new:.4f} pu</div>', unsafe_allow_html=True)
        st.success(f"**Total Series Impedance ($Z_{{series}}$):** {Z_series_terminals.real:.4f} + j{Z_series_terminals.imag:.4f} pu")

# =====================================================================
# APP 2: MULTI-BUS MESHED SYSTEM
# =====================================================================
elif app_mode == "2. Multi-Bus Meshed (Example 5.9)":
    st.markdown('<p class="main-header">🌐 Multi-Bus Network Analyzer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">Solves per-unit values for Example 5.9</p>', unsafe_allow_html=True)

    # SIDEBAR: Inputs for App 2
    st.sidebar.header("⚙️ Meshed Parameters")
    
    S_base_m = st.sidebar.number_input("System Base MVA", value=150.0, key="m_sbase")

    with st.sidebar.expander("Generator 1 (Node 1)", expanded=False):
        G1_MVA = st.number_input("G1 MVA", value=50.0, key="m_g1mva")
        G1_kV = st.number_input("G1 kV", value=11.0, key="m_g1kv")
        G1_X_pu = st.number_input("G1 Reactance (pu)", value=0.10, step=0.01, key="m_g1x")

    with st.sidebar.expander("Transformer 1 (Node 1 to 3)", expanded=False):
        T1_MVA_m = st.number_input("T1 MVA", value=100.0, key="m_t1mva")
        T1_kV_Z1_m = st.number_input("T1 Primary kV", value=11.0, key="m_t1kv1")
        T1_kV_Z2_m = st.number_input("T1 Secondary kV (Line)", value=220.0, key="m_t1kv2")
        T1_X_pu_m = st.number_input("T1 Reactance (pu)", value=0.15, step=0.01, key="m_t1x")

    with st.sidebar.expander("Transformer 2 (Node 2 to 4)", expanded=False):
        st.caption("Note: Enter 3-phase equivalent values")
        T2_MVA_m = st.number_input("T2 3-Phase MVA", value=150.0, key="m_t2mva")
        T2_kV_Z3_m = st.number_input("T2 Gen-Side kV (Delta)", value=6.6, key="m_t2kv3")
        T2_kV_Z2_m = st.number_input("T2 Line-Side kV (Y)", value=228.63, key="m_t2kv2") 
        T2_X_pu_m = st.number_input("T2 Reactance (pu)", value=0.10, step=0.01, key="m_t2x")

    with st.sidebar.expander("Generator 2 (Node 2)", expanded=False):
        G2_MVA = st.number_input("G2 MVA", value=40.0, key="m_g2mva")
        G2_kV = st.number_input("G2 kV", value=6.6, key="m_g2kv")
        G2_X_pu = st.number_input("G2 Reactance (pu)", value=0.12, step=0.01, key="m_g2x")

    with st.sidebar.expander("Transmission Lines (Nodes 3, 4, 5)", expanded=True):
        st.markdown("**Line 3-4**")
        Z34_R = st.number_input("Z34 Resistance (Ω)", value=30.0, key="m_z34r")
        Z34_X = st.number_input("Z34 Reactance (Ω)", value=150.0, key="m_z34x")
        st.markdown("**Line 3-5**")
        Z35_R = st.number_input("Z35 Resistance (Ω)", value=20.0, key="m_z35r")
        Z35_X = st.number_input("Z35 Reactance (Ω)", value=40.0, key="m_z35x")
        st.markdown("**Line 4-5**")
        Z45_R = st.number_input("Z45 Resistance (Ω)", value=25.0, key="m_z45r")
        Z45_X = st.number_input("Z45 Reactance (Ω)", value=60.0, key="m_z45x")

    with st.sidebar.expander("Load (Node 5)", expanded=False):
        Load_MVA = st.number_input("Load MVA", value=75.0, key="m_loadmva")
        Load_PF = st.number_input("Load PF", value=0.8, key="m_loadpf")

    # BACKGROUND CALCULATIONS (App 2)
    V_base1_m = G1_kV 
    V_base2_m = V_base1_m * (T1_kV_Z2_m / T1_kV_Z1_m)
    V_base3_m = V_base2_m * (T2_kV_Z3_m / T2_kV_Z2_m)

    Z_base2_m = (V_base2_m ** 2) / S_base_m

    G1_X_new_m = G1_X_pu * (S_base_m / G1_MVA) * ((G1_kV / V_base1_m) ** 2)
    G2_X_new_m = G2_X_pu * (S_base_m / G2_MVA) * ((G2_kV / V_base3_m) ** 2)

    T1_X_new_m = T1_X_pu_m * (S_base_m / T1_MVA_m) * ((T1_kV_Z1_m / V_base1_m) ** 2)
    T2_X_new_m = T2_X_pu_m * (S_base_m / T2_MVA_m) * ((T2_kV_Z2_m / V_base2_m) ** 2)

    Z34_pu = complex(Z34_R, Z34_X) / Z_base2_m
    Z35_pu = complex(Z35_R, Z35_X) / Z_base2_m
    Z45_pu = complex(Z45_R, Z45_X) / Z_base2_m

    Load_pu = Load_MVA / S_base_m

    # DASHBOARD DISPLAY (App 2)
    st.markdown("### 📊 System Base Values")
    col1, col2, col3 = st.columns(3)
    col1.metric("Zone 1 (G1) Base Voltage", f"{V_base1_m:.2f} kV")
    col2.metric("Zone 2 (Lines) Base Voltage", f"{V_base2_m:.2f} kV")
    col3.metric("Zone 3 (G2) Base Voltage", f"{V_base3_m:.2f} kV")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### ⚡ Per-Unit Impedance Network")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="result-card" style="border-left-color: #FFC107;">
            <h4>Generators & Transformers</h4>
            <b>G1 Reactance:</b> j{G1_X_new_m:.4f} pu <br>
            <b>T1 Reactance:</b> j{T1_X_new_m:.4f} pu <br><br>
            <b>G2 Reactance:</b> j{G2_X_new_m:.4f} pu <br>
            <b>T2 Reactance:</b> j{T2_X_new_m:.4f} pu
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="result-card" style="border-left-color: #FFC107;">
            <h4>Transmission Lines & Load</h4>
            <b>Line 3-4 ($Z_{{34}}$):</b> {Z34_pu.real:.4f} + j{Z34_pu.imag:.4f} pu <br>
            <b>Line 3-5 ($Z_{{35}}$):</b> {Z35_pu.real:.4f} + j{Z35_pu.imag:.4f} pu <br>
            <b>Line 4-5 ($Z_{{45}}$):</b> {Z45_pu.real:.4f} + j{Z45_pu.imag:.4f} pu <br><br>
            <b>Load Apparent Power:</b> {Load_pu:.4f} pu
        </div>
        """, unsafe_allow_html=True)


# =====================================================================
# APP 3: DYNAMIC Y-BUS MATRIX BUILDER (INFINITE BUSES)
# =====================================================================
elif app_mode == "3. Dynamic Y-Bus Builder (PRO Mode)":
    st.markdown('<p class="main-header">🚀 Dynamic Y-Bus Matrix Builder</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">Automatically calculates the Admittance Matrix for any size grid</p>', unsafe_allow_html=True)

    # Setup default interactive table data
    if 'branch_data' not in st.session_state:
        st.session_state.branch_data = pd.DataFrame({
            "From Bus": [1, 1, 2],
            "To Bus": [2, 3, 3],
            "R (pu)": [0.02, 0.01, 0.03],
            "X (pu)": [0.04, 0.03, 0.05]
        })

    st.markdown("### 📝 Transmission Line Data")
    st.caption("Click any cell to edit. Hover over the table and click the '➕ Add row' button at the bottom to expand the grid.")
    
    # st.data_editor creates the magical interactive spreadsheet
    edited_df = st.data_editor(st.session_state.branch_data, num_rows="dynamic", use_container_width=True)
    
    if st.button("Calculate Y-Bus Matrix", type="primary"):
        try:
            # 1. Find out how many buses exist in the network
            buses = pd.concat([edited_df["From Bus"], edited_df["To Bus"]]).unique()
            num_buses = int(max(buses))
            
            # 2. Create an empty complex matrix filled with zeros
            Y_bus = np.zeros((num_buses, num_buses), dtype=complex)
            
            # 3. Loop through the table to build the matrix
            for index, row in edited_df.iterrows():
                from_bus = int(row["From Bus"]) - 1  # Python arrays start at 0
                to_bus = int(row["To Bus"]) - 1
                R = row["R (pu)"]
                X = row["X (pu)"]
                
                # Calculate Admittance (Y = 1 / Z)
                Z = complex(R, X)
                Y = 1.0 / Z if Z != 0 else 0
                
                # Populate diagonal elements
                Y_bus[from_bus, from_bus] += Y
                Y_bus[to_bus, to_bus] += Y
                
                # Populate off-diagonal elements
                Y_bus[from_bus, to_bus] -= Y
                Y_bus[to_bus, from_bus] -= Y
                
            # 4. Format the matrix so it looks beautiful and readable
            formatted_Y = pd.DataFrame(Y_bus).map(lambda x: f"{x.real:.4f} {'+' if x.imag >= 0 else '-'} j{abs(x.imag):.4f}")
            formatted_Y.index = [f"Bus {i+1}" for i in range(num_buses)]
            formatted_Y.columns = [f"Bus {i+1}" for i in range(num_buses)]
            
            st.markdown("### 🧮 System Admittance Matrix ($Y_{bus}$)")
            st.dataframe(formatted_Y, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error in calculation. Please ensure all inputs are valid numbers. Error: {e}")
