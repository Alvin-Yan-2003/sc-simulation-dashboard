import streamlit as st
import matplotlib.pyplot as plt

from engines.simulator import run_simulation
from config import SimulationConfig, CostConfig


st.set_page_config(layout="wide")
st.title("📦 Portfolio-Level Demand–Forecast–Inventory Simulator")

# =============================
# SIDEBAR CONFIGURATION
# =============================

st.sidebar.header("Simulation Configuration")

weeks = st.sidebar.slider("Simulation Horizon (Weeks)", 26, 104, 52)

base_level = st.sidebar.number_input("Base Demand Level", 1000, 20000, 5000)

use_forecast = st.sidebar.checkbox("Use Forecast for Planning")

alpha = st.sidebar.slider("Forecast Alpha (Exp. Smoothing)", 0.1, 0.9, 0.3)

policy = st.sidebar.selectbox("Inventory Policy", ["EOQ", "(s,S)"])

lead_time = st.sidebar.slider("Lead Time (weeks)", 1, 8, 2)

eoq_qty = st.sidebar.number_input("EOQ Quantity", 1000, 20000, 5000)

s_level = st.sidebar.number_input("Reorder Point (s)", 1000, 20000, 3000)

S_level = st.sidebar.number_input("Order-up-to Level (S)", 2000, 30000, 8000)

capacity = st.sidebar.number_input("Warehouse Capacity", 5000, 50000, 20000)

holding_cost = st.sidebar.number_input("Holding Cost per Unit", 0.1, 10.0, 1.0)
order_cost = st.sidebar.number_input("Order Cost", 10.0, 500.0, 100.0)
penalty_cost = st.sidebar.number_input("Penalty Cost (Lost Sales)", 1.0, 50.0, 5.0)

# =============================
# BUILD CONFIG OBJECTS
# =============================

sim_config = SimulationConfig(
    weeks=weeks,
    base_level=base_level,
    use_forecast=use_forecast,
    alpha=alpha,
    policy=policy,
    lead_time=lead_time,
    eoq_qty=eoq_qty,
    s=s_level,
    S=S_level,
    capacity=capacity
)

cost_config = CostConfig(
    holding_cost=holding_cost,
    order_cost=order_cost,
    penalty_cost=penalty_cost
)

# =============================
# RUN SIMULATION
# =============================

df_demand, df_inventory, kpis = run_simulation(sim_config, cost_config)

# =============================
# KPI DASHBOARD
# =============================

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Fill Rate", kpis["Fill Rate"])
col2.metric("Service Level", kpis["Service Level"])
col3.metric("DIO (days)", kpis["DIO"])
col4.metric("Avg Inventory", kpis["Avg Inventory"])

st.markdown("---")

# =============================
# DEMAND vs FORECAST
# =============================

st.subheader("Demand vs Forecast")

fig1, ax1 = plt.subplots()
ax1.plot(df_demand["Week"], df_demand["Actual_Demand"], label="Actual Demand")

if use_forecast and "Forecast" in df_demand.columns:
    ax1.plot(df_demand["Week"], df_demand["Forecast"], label="Forecast")

ax1.set_xlabel("Week")
ax1.set_ylabel("Volume")
ax1.legend()

st.pyplot(fig1)

# =============================
# INVENTORY PROFILE
# =============================

st.subheader("Inventory Level")

fig2, ax2 = plt.subplots()
ax2.plot(df_inventory["Week"], df_inventory["Stock"], label="Stock Level")
ax2.set_xlabel("Week")
ax2.set_ylabel("Stock")
ax2.legend()

st.pyplot(fig2)

st.subheader("Order Quantity")

fig3, ax3 = plt.subplots()
ax3.bar(df_inventory["Week"], df_inventory["Order"])
ax3.set_xlabel("Week")
ax3.set_ylabel("Order Quantity")

st.pyplot(fig3)

# =============================
# LOST SALES
# =============================

st.subheader("Lost Sales")

fig4, ax4 = plt.subplots()
ax4.bar(df_inventory["Week"], df_inventory["Lost_Sales"])
ax4.set_xlabel("Week")
ax4.set_ylabel("Lost Sales")

st.pyplot(fig4)

# =============================
# CAPACITY UTILIZATION
# =============================

st.subheader("Warehouse Capacity Utilization")

df_inventory["Capacity_Utilization_%"] = (
    df_inventory["Stock"] / sim_config.capacity * 100
)

fig5, ax5 = plt.subplots()
ax5.plot(df_inventory["Week"], df_inventory["Capacity_Utilization_%"])
ax5.set_xlabel("Week")
ax5.set_ylabel("Utilization (%)")

st.pyplot(fig5)

# =============================
# RAW DATA VIEW
# =============================

st.subheader("Simulation Data")

tab1, tab2 = st.tabs(["Demand Data", "Inventory Data"])

with tab1:
    st.dataframe(df_demand)

with tab2:
    st.dataframe(df_inventory)