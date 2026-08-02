import streamlit as st
import cmath
import math
import pandas as pd
import numpy as np

# 1. Page Configuration (Must be first)
st.set_page_config(page_title="Power System Analyzer Suite", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# 2. Custom CSS
st.markdown("""
<style>
    [data-testid="stToolbar"] {visibility: hidden;}
    .main-header { font-size: 2.5rem; color: #1E88E5; text-align: center; font-weight: 800; margin-bottom: 0px; }
    .sub-text { text-align: center; color: #6c757d; font-size: 1.1rem; margin-bottom: 30px; }
    .result-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #1E88E5; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); text-align: center; }
</style>
""", unsafe_allow_html=True)

# 3. Sidebar Dropdown for Navigation
st.sidebar.header("🔀 Select Calculator")
app_mode = st.sidebar.selectbox(
    "Choose your network topology:",
    [
        "1. Radial System (Voltage Regulation)", 
        "2. Fault Analysis Calculator",
        "3. Multi-Bus Meshed (Example 5.9 Auto-Matrix)",
        "4. Ultimate Auto-Matrix (Raw Data Input)"
    ]
)
st.sidebar.markdown("---")

# =====================================================================
# APP 1: RADIAL SYSTEM (VOLTAGE REGULATION ONLY)
# =====================================================================
if app_mode == "1. Radial System (Voltage Regulation)":
    st.markdown('<p class="main-header">⚡ Radial System Analyzer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">Complete Assignment Solution Dashboard</p>', unsafe_allow_html=True)

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
        T1_kV_Z1 = st.number_input("T1 kV (Zone 1 - Gen)", value=6.6, key="r_t1kv1")
        T1_kV_Z2 = st.number_input("T1 kV (Zone 2 - Line)", value=132.0, key="r_t1kv2")
        T1_X_pu = st.number_input("T1 Reactance X (%)", value=8.0, key="r_t1x") / 100.0
        st.divider()
        T2_MVA = st.number_input("T2 MVA", value=25.0, key="r_t2mva")
        T2_kV_Z2 = st.number_input("T2 kV (Zone 2 - Line)", value=132.0, key="r_t2kv2")
        T2_kV_Z3 = st.number_input("T2 kV (Zone 3 - Load)", value=11.0, key="r_t2kv3")
        T2_X_pu = st.number_input("T2 Reactance X (%)", value=7.0, key="r_t2x") / 100.0

    with st.sidebar.expander("3. Line & Load", expanded=False):
        line_R = st.number_input("Line Resistance (Ω)", value=15.0, key="r_liner")
        line_X = st.number_input("Line Reactance (Ω)", value=45.0, key="r_linex")
        st.divider()
        load_MW = st.number_input("Load MW", value=18.0, key="r_loadmw")
        load_pf = st.number_input("Load PF (lagging)", value=0.9, key="r_loadpf")
        load_kV = st.number_input("Load operating kV", value=11.0, key="r_loadkv")

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

    tab1, tab2 = st.tabs(["📊 Key Results", "🔬 Detailed Impedance Network"])
    
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
            cz1.markdown(f"**Zone 1**\n* V_base = {V_base1:.2f} kV\n* I_base = {I_base1:.2f} A\n* Z_base = {Z_base1:.4f} Ω")
            cz2.markdown(f"**Zone 2**\n* V_base = {V_base2:.2f} kV\n* I_base = {I_base2:.2f} A\n* Z_base = {Z_base2:.4f} Ω")
            cz3.markdown(f"**Zone 3**\n* V_base = {V_base3:.2f} kV\n* I_base = {I_base3:.2f} A\n* Z_base = {Z_base3:.4f} Ω")
            
        with st.expander("Problem 2: Per-Unit Reactance"):
            st.markdown(f"* **Generator:** j{G_X_new:.4f} pu\n* **T1:** j{T1_X_new:.4f} pu\n* **T2:** j{T2_X_new:.4f} pu")
            
        with st.expander("Problem 3: Line Impedance"):
            st.markdown(f"* **Line Z_pu:** {Z_line_pu.real:.4f} + j{Z_line_pu.imag:.4f} pu")
            
        with st.expander("Problem 4: Load Representation"):
            st.markdown(f"* **S_pu:** {S_load_pu.real:.4f} + j{S_load_pu.imag:.4f} pu\n* **I_pu:** {I_load_pu.real:.4f} + j{I_load_pu.imag:.4f} pu\n* **Z_pu:** {Z_load_pu.real:.4f} + j{Z_load_pu.imag:.4f} pu")
            
        with st.expander("Problem 5: Voltage Regulation"):
            st.markdown(f"* **V_gen (per-unit):** {V_term_pu.real:.4f} + j{V_term_pu.imag:.4f} pu\n* **Magnitude V_gen_pu:** {abs(V_term_pu):.4f} pu\n* **Actual Required Voltage:** {V_term_kV:.2f} kV")

    with tab2:
        st.markdown("### 🧩 Per-Unit Impedance Breakdown")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="result-card"><b>T1</b><br>j{T1_X_new:.4f} pu</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="result-card"><b>Line</b><br>{Z_line_pu.real:.4f} + j{Z_line_pu.imag:.4f} pu</div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="result-card"><b>T2</b><br>j{T2_X_new:.4f} pu</div>', unsafe_allow_html=True)
        st.success(f"**Total Series Impedance:** {Z_series_terminals.real:.4f} + j{Z_series_terminals.imag:.4f} pu")
        # =====================================================================
# APP 2: UNIVERSAL FAULT CALCULATOR (NEW)
# =====================================================================
elif app_mode == "2. Fault Analysis Calculator":
    st.markdown('<p class="main-header">💥 Universal Fault Calculator</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">Input Thevenin Sequence Impedances to solve any fault condition</p>', unsafe_allow_html=True)

    st.sidebar.header("⚙️ Fault Parameters")
    V_pre = st.sidebar.number_input("Pre-fault Voltage (pu)", value=1.00)
    Base_MVA = st.sidebar.number_input("System Base MVA", value=30.0)
    Base_kV = st.sidebar.number_input("Fault Location Base kV", value=11.0)
    
    with st.sidebar.expander("Thevenin Sequence Impedances (PU)", expanded=True):
        st.write("Positive Sequence ($Z_1$)")
        z1_r = st.number_input("Z1 R", value=0.0258)
        z1_x = st.number_input("Z1 X", value=0.3615)
        st.write("Negative Sequence ($Z_2$)")
        z2_r = st.number_input("Z2 R", value=0.0258)
        z2_x = st.number_input("Z2 X", value=0.3615)
        st.write("Zero Sequence ($Z_0$)")
        z0_r = st.number_input("Z0 R", value=0.0774)
        z0_x = st.number_input("Z0 X", value=1.0845)
    
    with st.sidebar.expander("Fault Impedance ($Z_f$)", expanded=False):
        zf_r = st.number_input("Zf R", value=0.0)
        zf_x = st.number_input("Zf X", value=0.0)

    # Complex Assignments
    Z1 = complex(z1_r, z1_x)
    Z2 = complex(z2_r, z2_x)
    Z0 = complex(z0_r, z0_x)
    Zf = complex(zf_r, zf_x)
    
    I_base = (Base_MVA * 1000) / (math.sqrt(3) * Base_kV)

    # Fault Math Engine
    I_LLL_pu = abs(V_pre / Z1)
    I_LL_pu = abs((math.sqrt(3) * V_pre) / (Z1 + Z2))
    I_LG_pu = abs((3.0 * V_pre) / (Z1 + Z2 + Z0 + complex(3*zf_r, 3*zf_x)))
    
    Z_p = (Z2 * (Z0 + complex(3*zf_r, 3*zf_x))) / (Z2 + Z0 + complex(3*zf_r, 3*zf_x))
    I1_LLG = V_pre / (Z1 + Z_p)
    I0_LLG = -I1_LLG * (Z2 / (Z2 + Z0 + complex(3*zf_r, 3*zf_x)))
    I_LLG_pu = abs(3.0 * I0_LLG)

    st.markdown("### ⚡ Short Circuit Results")
    f1, f2 = st.columns(2)
    f1.metric("Three-Phase (LLL)", f"{I_LLL_pu * I_base:,.0f} A", f"{I_LLL_pu:.4f} pu", delta_color="off")
    f2.metric("Line-to-Line (LL)", f"{I_LL_pu * I_base:,.0f} A", f"{I_LL_pu:.4f} pu", delta_color="off")
    
    f3, f4 = st.columns(2)
    f3.metric("Line-to-Ground (LG)", f"{I_LG_pu * I_base:,.0f} A", f"{I_LG_pu:.4f} pu", delta_color="off")
    f4.metric("Double Line-to-Ground (LLG)", f"{I_LLG_pu * I_base:,.0f} A", f"{I_LLG_pu:.4f} pu", delta_color="off")
    
    st.info(f"**Base Current at Fault Location:** {I_base:.2f} A")

# =====================================================================
# APP 3: MULTI-BUS MESHED SYSTEM (EXAMPLE 5.9)
# =====================================================================
elif app_mode == "3. Multi-Bus Meshed (Example 5.9 Auto-Matrix)":
    st.markdown('<p class="main-header">🌐 Multi-Bus Network Analyzer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">Converts raw parameters to PU and builds Y-Bus automatically</p>', unsafe_allow_html=True)

    st.sidebar.header("⚙️ Raw Network Parameters")
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

    st.markdown("### 📊 Step 1: Per-Unit Conversion")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="result-card" style="border-left-color: #FFC107;">
            <h4>Generators & Transformers</h4>
            <b>T1 Reactance:</b> j{T1_X_new_m:.4f} pu <br>
            <b>T2 Reactance:</b> j{T2_X_new_m:.4f} pu <br>
            <b>G1 Reactance:</b> j{G1_X_new_m:.4f} pu <br>
            <b>G2 Reactance:</b> j{G2_X_new_m:.4f} pu</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="result-card" style="border-left-color: #FFC107;">
            <h4>Transmission Lines & Load</h4>
            <b>Line 3-4:</b> {Z34_pu.real:.4f} + j{Z34_pu.imag:.4f} pu <br>
            <b>Line 3-5:</b> {Z35_pu.real:.4f} + j{Z35_pu.imag:.4f} pu <br>
            <b>Line 4-5:</b> {Z45_pu.real:.4f} + j{Z45_pu.imag:.4f} pu <br>
            <b>Load Apparent Power:</b> {Load_pu:.4f} pu</div>""", unsafe_allow_html=True)

    y13 = 1.0 / complex(0, T1_X_new_m)
    y24 = 1.0 / complex(0, T2_X_new_m)
    y34 = 1.0 / Z34_pu
    y35 = 1.0 / Z35_pu
    y45 = 1.0 / Z45_pu

    Y_bus = np.zeros((5, 5), dtype=complex)
    Y_bus[0, 2] = Y_bus[2, 0] = -y13
    Y_bus[1, 3] = Y_bus[3, 1] = -y24
    Y_bus[2, 3] = Y_bus[3, 2] = -y34
    Y_bus[2, 4] = Y_bus[4, 2] = -y35
    Y_bus[3, 4] = Y_bus[4, 3] = -y45
    Y_bus[0, 0] = y13
    Y_bus[1, 1] = y24
    Y_bus[2, 2] = y13 + y34 + y35
    Y_bus[3, 3] = y24 + y34 + y45
    Y_bus[4, 4] = y35 + y45

    formatted_Y = pd.DataFrame(Y_bus).map(lambda x: f"{x.real:.4f} {'+' if x.imag >= 0 else '-'} j{abs(x.imag):.4f}")
    formatted_Y.index = [f"Bus {i+1}" for i in range(5)]
    formatted_Y.columns = [f"Bus {i+1}" for i in range(5)]
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 🧮 Step 2: Automatic System Admittance Matrix ($Y_{bus}$)")
    st.dataframe(formatted_Y, use_container_width=True)
    # =====================================================================
# APP 4: ULTIMATE RAW-TO-MATRIX BUILDER (INFINITE COMPONENTS)
# =====================================================================
elif app_mode == "4. Ultimate Auto-Matrix (Raw Data Input)":
    st.markdown('<p class="main-header">🚀 Ultimate Auto-Matrix Builder</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">Input RAW system data -> Auto PU Conversion -> Dynamic Y-Bus matrix</p>', unsafe_allow_html=True)

    S_base_sys = st.number_input("Overall System Base MVA", value=150.0, step=10.0)

    st.markdown("### 1️⃣ Define Bus Base Voltages")
    if 'bus_data' not in st.session_state:
        st.session_state.bus_data = pd.DataFrame({
            "Bus Number": [1, 2, 3, 4, 5],
            "Base kV": [11.0, 6.35, 220.0, 220.0, 220.0]
        })
    bus_df = st.data_editor(st.session_state.bus_data, num_rows="dynamic", use_container_width=True, key="bus_table")
    
    st.markdown("### 2️⃣ Equipment (Generators & Transformers)")
    st.caption("Enter the manufacturer ratings here. Set 'To Bus' to 0 for Generators.")
    if 'equip_data' not in st.session_state:
        st.session_state.equip_data = pd.DataFrame({
            "Component": ["G1", "G2", "T1", "T2"],
            "From Bus": [1, 2, 1, 2],
            "To Bus": [0, 0, 3, 4],
            "Rated MVA": [50.0, 40.0, 100.0, 150.0],
            "Rated kV (Primary)": [11.0, 6.6, 11.0, 6.6],
            "Raw Reactance (pu)": [0.10, 0.12, 0.15, 0.10]
        })
    equip_df = st.data_editor(st.session_state.equip_data, num_rows="dynamic", use_container_width=True, key="equip_table")

    st.markdown("### 3️⃣ Transmission Lines (Raw Ohms)")
    if 'line_data' not in st.session_state:
        st.session_state.line_data = pd.DataFrame({
            "From Bus": [3, 3, 4],
            "To Bus": [4, 5, 5],
            "R (Ohms)": [30.0, 20.0, 25.0],
            "X (Ohms)": [150.0, 40.0, 60.0]
        })
    line_df = st.data_editor(st.session_state.line_data, num_rows="dynamic", use_container_width=True, key="line_table")

    if st.button("Convert to PU & Build Y-Bus", type="primary"):
        try:
            bus_kv_map = dict(zip(bus_df["Bus Number"], bus_df["Base kV"]))
            bus_kv_map[0] = 1.0
            max_bus = int(bus_df["Bus Number"].max())
            Y_bus = np.zeros((max_bus, max_bus), dtype=complex)

            st.markdown("### 📊 Calculated Per-Unit Values")
            st.write("**Generators & Transformers:**")
            for _, row in equip_df.iterrows():
                from_bus = int(row["From Bus"])
                to_bus = int(row["To Bus"])
                bus_base_kv = bus_kv_map.get(from_bus, 1.0)
                pu_adj = row["Raw Reactance (pu)"] * (S_base_sys / row["Rated MVA"]) * ((row["Rated kV (Primary)"] / bus_base_kv)**2)
                st.write(f"- {row['Component']}: j{pu_adj:.4f} pu")
                
                Y = 1.0 / complex(0, pu_adj)
                if from_bus != 0: Y_bus[from_bus - 1, from_bus - 1] += Y
                if to_bus != 0: Y_bus[to_bus - 1, to_bus - 1] += Y
                if from_bus != 0 and to_bus != 0:
                    Y_bus[from_bus - 1, to_bus - 1] -= Y
                    Y_bus[to_bus - 1, from_bus - 1] -= Y

            st.write("**Transmission Lines:**")
            for _, row in line_df.iterrows():
                from_bus = int(row["From Bus"])
                to_bus = int(row["To Bus"])
                bus_base_kv = bus_kv_map.get(from_bus, 1.0)
                Z_base = (bus_base_kv ** 2) / S_base_sys
                
                R_pu = row["R (Ohms)"] / Z_base
                X_pu = row["X (Ohms)"] / Z_base
                st.write(f"- Line {from_bus}-{to_bus}: {R_pu:.4f} + j{X_pu:.4f} pu")
                
                Y = 1.0 / complex(R_pu, X_pu)
                if from_bus != 0: Y_bus[from_bus - 1, from_bus - 1] += Y
                if to_bus != 0: Y_bus[to_bus - 1, to_bus - 1] += Y
                if from_bus != 0 and to_bus != 0:
                    Y_bus[from_bus - 1, to_bus - 1] -= Y
                    Y_bus[to_bus - 1, from_bus - 1] -= Y

            formatted_Y = pd.DataFrame(Y_bus).map(lambda x: f"{x.real:.4f} {'+' if x.imag >= 0 else '-'} j{abs(x.imag):.4f}")
            formatted_Y.index = [f"Bus {i+1}" for i in range(max_bus)]
            formatted_Y.columns = [f"Bus {i+1}" for i in range(max_bus)]
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("### 🧮 Final System Admittance Matrix ($Y_{bus}$)")
            st.dataframe(formatted_Y, use_container_width=True)

        except Exception as e:
            st.error(f"Calculation Error: Please ensure all Bus Numbers in your components exist in the Bus Voltages table. Detail: {e}")
