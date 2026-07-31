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
    .result-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #1E88E5; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); text-align: center; }
</style>
""", unsafe_allow_html=True)

# 3. Sidebar Dropdown for Navigation
st.sidebar.header("🔀 Select Calculator")
app_mode = st.sidebar.selectbox(
    "Choose your network topology:",
    [
        "1. Radial System (Voltage Regulation)", 
        "2. Multi-Bus Meshed (Example 5.9 Auto-Matrix)",
        "3. Ultimate Auto-Matrix (Raw Data Input)"
    ]
)
st.sidebar.markdown("---")

# =====================================================================
# APP 1: RADIAL SYSTEM
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

    V_base2 = V_base1 * (T1_kV_Z2 / T1_kV_Z1)
    V_base3 = V_base2 * (T2_kV_Z3 / T2_kV_Z2)
    Z_base1 = (V_base1 ** 2) / S_base
    Z_base2 = (V_base2 ** 2) / S_base
    Z_base3 = (V_base3 ** 2) / S_base
    
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
    with tab2:
        st.markdown("### 🧩 Per-Unit Impedance Breakdown")
        st.success(f"**Total Series Impedance:** {Z_series_terminals.real:.4f} + j{Z_series_terminals.imag:.4f} pu")

# =====================================================================
# APP 2: MULTI-BUS MESHED SYSTEM
# =====================================================================
elif app_mode == "2. Multi-Bus Meshed (Example 5.9 Auto-Matrix)":
    st.markdown('<p class="main-header">🌐 Multi-Bus Network Analyzer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">Converts raw parameters to PU and builds Y-Bus automatically</p>', unsafe_allow_html=True)
    st.info("Please use the new 'Ultimate Auto-Matrix' mode for unlimited raw component inputs.")

# =====================================================================
# APP 3: ULTIMATE RAW-TO-MATRIX BUILDER (INFINITE COMPONENTS)
# =====================================================================
elif app_mode == "3. Ultimate Auto-Matrix (Raw Data Input)":
    st.markdown('<p class="main-header">🚀 Ultimate Auto-Matrix Builder</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">Input RAW system data -> Auto PU Conversion -> Dynamic Y-Bus matrix</p>', unsafe_allow_html=True)

    S_base_sys = st.number_input("Overall System Base MVA", value=150.0, step=10.0)

    # 1. Bus Voltages Table
    st.markdown("### 1️⃣ Define Bus Base Voltages")
    if 'bus_data' not in st.session_state:
        st.session_state.bus_data = pd.DataFrame({
            "Bus Number": [1, 2, 3, 4, 5],
            "Base kV": [11.0, 6.35, 220.0, 220.0, 220.0]
        })
    bus_df = st.data_editor(st.session_state.bus_data, num_rows="dynamic", use_container_width=True, key="bus_table")
    
    # 2. Equipment (Generators / Transformers) Table
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

    # 3. Transmission Lines Table (Raw Ohms)
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
            # Create a dictionary to easily lookup Base kV for any bus
            bus_kv_map = dict(zip(bus_df["Bus Number"], bus_df["Base kV"]))
            bus_kv_map[0] = 1.0 # Dummy value for ground to avoid division errors

            # Find max bus to size the matrix
            max_bus = int(bus_df["Bus Number"].max())
            Y_bus = np.zeros((max_bus, max_bus), dtype=complex)

            st.markdown("### 📊 Calculated Per-Unit Values")
            
            # Process Equipment
            st.write("**Generators & Transformers (PU Adjusted to System Base):**")
            for _, row in equip_df.iterrows():
                from_bus = int(row["From Bus"])
                to_bus = int(row["To Bus"])
                
                # Base change formula: X_new = X_old * (S_base_new / S_base_old) * (V_old / V_base_new)^2
                bus_base_kv = bus_kv_map.get(from_bus, 1.0)
                pu_adj = row["Raw Reactance (pu)"] * (S_base_sys / row["Rated MVA"]) * ((row["Rated kV (Primary)"] / bus_base_kv)**2)
                
                st.write(f"- {row['Component']}: j{pu_adj:.4f} pu")
                
                # Add to Admittance Matrix
                Y = 1.0 / complex(0, pu_adj)
                if from_bus != 0: Y_bus[from_bus - 1, from_bus - 1] += Y
                if to_bus != 0: Y_bus[to_bus - 1, to_bus - 1] += Y
                if from_bus != 0 and to_bus != 0:
                    Y_bus[from_bus - 1, to_bus - 1] -= Y
                    Y_bus[to_bus - 1, from_bus - 1] -= Y

            # Process Lines
            st.write("**Transmission Lines (Ohms to PU):**")
            for _, row in line_df.iterrows():
                from_bus = int(row["From Bus"])
                to_bus = int(row["To Bus"])
                
                bus_base_kv = bus_kv_map.get(from_bus, 1.0)
                Z_base = (bus_base_kv ** 2) / S_base_sys
                
                R_pu = row["R (Ohms)"] / Z_base
                X_pu = row["X (Ohms)"] / Z_base
                st.write(f"- Line {from_bus}-{to_bus}: {R_pu:.4f} + j{X_pu:.4f} pu")
                
                # Add to Admittance Matrix
                Y = 1.0 / complex(R_pu, X_pu)
                if from_bus != 0: Y_bus[from_bus - 1, from_bus - 1] += Y
                if to_bus != 0: Y_bus[to_bus - 1, to_bus - 1] += Y
                if from_bus != 0 and to_bus != 0:
                    Y_bus[from_bus - 1, to_bus - 1] -= Y
                    Y_bus[to_bus - 1, from_bus - 1] -= Y

            # Display Final Matrix
            formatted_Y = pd.DataFrame(Y_bus).map(lambda x: f"{x.real:.4f} {'+' if x.imag >= 0 else '-'} j{abs(x.imag):.4f}")
            formatted_Y.index = [f"Bus {i+1}" for i in range(max_bus)]
            formatted_Y.columns = [f"Bus {i+1}" for i in range(max_bus)]
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("### 🧮 Final System Admittance Matrix ($Y_{bus}$)")
            st.dataframe(formatted_Y, use_container_width=True)

        except Exception as e:
            st.error(f"Calculation Error: Please ensure all Bus Numbers in your components exist in the Bus Voltages table. Detail: {e}")
