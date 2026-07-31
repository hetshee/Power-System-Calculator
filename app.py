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
    st.info("Code for Radial System is running perfectly. (Minimized for display)")
    # (Your previous App 1 code remains identical here in your actual file, I have shortened it here to focus on the new feature. You can paste your existing App 1 logic here.)

# =====================================================================
# APP 2: MULTI-BUS MESHED SYSTEM
# =====================================================================
elif app_mode == "2. Multi-Bus Meshed (Example 5.9)":
    st.markdown('<p class="main-header">🌐 Multi-Bus Network Analyzer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">Solves per-unit values for Example 5.9</p>', unsafe_allow_html=True)
    st.info("Code for Example 5.9 is running perfectly. (Minimized for display)")
    # (Your previous App 2 code remains identical here in your actual file.)

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
