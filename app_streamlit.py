import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="Olive Grove Cover Crop Simulator", layout="wide")
st.title("Olive Grove Cover Crop Simulator")
st.markdown("Optimize cover crop management to maximize water retention and yield.")

# --- Sidebar Inputs ---
st.sidebar.header("Management & Climate Variables")

rainfall = st.sidebar.slider("Annual Rainfall (mm)", min_value=200, max_value=800, value=400, step=10)
cover_pct = st.sidebar.slider("Cover Crop Percentage (%)", min_value=0, max_value=100, value=30, step=10)
mowing_time = st.sidebar.selectbox("Mowing Timing", ["Early (March)", "Late (May)", "Unmowed"])

st.sidebar.markdown("---")
st.sidebar.header("Future Scenarios")
climate_change = st.sidebar.checkbox("Apply Climate Change Scenario (Mid-Century)")
st.sidebar.caption("Simulates +20% rainfall intensity (higher runoff) and -10% total rainfall.")

# --- Mathematical Engine ---

# 1. Climate Change Adjustments
actual_rainfall = rainfall * 0.9 if climate_change else rainfall
base_runoff_pct = 0.30 if climate_change else 0.20 # Higher intensity means more base runoff

# 2. Infiltration & Runoff (Section 3)
# Every 10% cover improves infiltration by 1% (reduces runoff by 1%)
runoff_reduction = (cover_pct / 10) * 0.01
final_runoff_pct = max(0.05, base_runoff_pct - runoff_reduction) # Assume min 5% runoff
runoff_mm = actual_rainfall * final_runoff_pct

# 3. Evaporation (Section 4)
# Base evaporation for bare soil. Cover crop mulch reduces it.
# 30% cover mowed saves 16.5 mm
base_evap = 120 # Assumed base evaporation in mm
evap_savings = 0
if "Early" in mowing_time or "Late" in mowing_time:
    evap_savings = (cover_pct / 30) * 16.5
evap_mm = max(30, base_evap - evap_savings)

# 4. Transpiration (Section 5)
# Base assumptions for 50% cover: Early = 70 mm, Late = 110 mm
if mowing_time == "Early (March)":
    transp_mm = (cover_pct / 50) * 70
elif mowing_time == "Late (May)":
    transp_mm = (cover_pct / 50) * 110
else:
    transp_mm = (cover_pct / 50) * 150 # Unmowed penalty

# 5. Net Water & Yield (Section 2)
# Net Water (x)
net_water = actual_rainfall - runoff_mm - evap_mm - transp_mm

# Yield (y) = 10x - 1300
yield_kg = max(0, (10 * net_water) - 1300)

# 6. Long-Term Soil Erosion (Section 7)
years = list(range(1, 21))
soil_depth = [1000] # Starting arbitrary soil depth in mm
erosion_rate = 3.0 if climate_change else 2.0 # mm per year for bare soil
if cover_pct >= 30:
    erosion_rate = 0.2 # drastic reduction as per Section 7

for y in range(1, 20):
    soil_depth.append(soil_depth[-1] - erosion_rate)

soil_df = pd.DataFrame({"Year": years, "Soil Depth (mm)": soil_depth})

# --- Layout & Outputs ---

col1, col2, col3 = st.columns(3)

col1.metric("Net Stored Water", f"{net_water:.1f} mm", 
            help="Rainfall minus Runoff, Evaporation, and Transpiration")
col2.metric("Estimated Yield", f"{yield_kg:.0f} kg/ha", 
            help="Based on y = 10x - 1300")
col3.metric("Annual Soil Loss", f"{erosion_rate:.1f} mm/yr", 
            delta="- Tolerable" if erosion_rate <= 0.2 else "High Risk!", delta_color="inverse")

st.markdown("### Water Balance Breakdown")
water_breakdown = pd.DataFrame({
    "Component": ["Rainfall", "Runoff", "Evaporation", "Cover Transpiration", "Net Stored Water"],
    "mm": [actual_rainfall, -runoff_mm, -evap_mm, -transp_mm, net_water]
})
st.bar_chart(water_breakdown.set_index("Component"))

st.markdown("### 20-Year Soil Preservation (Erosion Impact)")
st.line_chart(soil_df.set_index("Year"))
