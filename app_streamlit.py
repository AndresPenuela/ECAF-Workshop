import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. App Configuration ---
st.set_page_config(page_title="Agro-Hydrological Dashboard", layout="wide")
st.title("Unified Agro-Hydrological Model (Andalusia)")
st.markdown("Interactive tool for modeling the impact of vegetation cover on soil erosion, runoff, and olive productivity under future climate scenarios.")

# --- 2. Mathematical Models ---
def get_equilibrium_veg():
    return - (1.0 / 0.06) * np.log(1.4 / 11.47)

def project_parameters(veg_cover, years):
    rain_increase_pct = years * 0.5
    baseline_oc = 1.5
    veg_eq = get_equilibrium_veg()
    annual_oc_change = (veg_cover - veg_eq) * 0.0005 
    future_oc = max(0.5, min(5.0, baseline_oc + (annual_oc_change * years))) 
    return rain_increase_pct, future_oc

def predict_soil_loss(veg_cover, rain_increase_pct, oc_pct):
    base_soil_loss = 11.47 * np.exp(-0.06 * veg_cover)
    m_r = 1.0 + (rain_increase_pct / 100.0)
    m_k = max(0.1, (12.0 - (oc_pct * 1.724)) / (12.0 - (1.5 * 1.724)))
    return base_soil_loss * m_r * m_k

def predict_runoff(veg_cover, rain_increase_pct, oc_pct):
    base_runoff = np.maximum(0, -0.11 * veg_cover + 11.59)
    m_rain = 1.0 + (rain_increase_pct / 100.0) * 0.5 
    m_oc = np.exp(-0.2 * (oc_pct - 1.5))
    return np.minimum(100.0, base_runoff * m_rain * m_oc)

def estimate_productivity(rainfall):
    return np.maximum(0, np.minimum(3350, 10 * (rainfall - 120)))

# Constants
RO_BASELINE = predict_runoff(15.0, 0.0, 1.5) # Baseline Runoff at 15% veg cover, Year 0
EQ_VEG = get_equilibrium_veg()
X_VALS = np.linspace(0, 100, 500)
RAIN_RANGE = np.linspace(0, 1000, 500)

# --- 3. Sidebar Inputs ---
st.sidebar.header("Model Parameters")
veg_cover = st.sidebar.slider("Vegetation Cover (%)", min_value=0.0, max_value=100.0, value=35.0, step=1.0)
gross_rain = st.sidebar.slider("Gross Annual Rain (mm)", min_value=150.0, max_value=1000.0, value=450.0, step=10.0)
years_future = st.sidebar.selectbox("Prediction Timeframe (Years Future)", options=[0, 10, 25, 50])

# --- 4. Core Calculations ---
r_inc, oc = project_parameters(veg_cover, years_future)
sl = predict_soil_loss(veg_cover, r_inc, oc)
ro = predict_runoff(veg_cover, r_inc, oc)

infiltration_ratio = (100.0 - ro) / (100.0 - RO_BASELINE)
effective_rain = gross_rain * infiltration_ratio

prod_base = estimate_productivity(gross_rain)
prod_eff = estimate_productivity(effective_rain)

# --- 5. Metrics Dashboard ---
st.subheader("Environmental & Agronomic Context")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Projected Soil OC", f"{oc:.2f} %", f"{(oc - 1.5):.2f} % vs baseline")
with col2:
    st.metric("Soil Loss", f"{sl:.2f} t/ha/y", "Tolerable" if sl <= 1.4 else "High Risk", delta_color="inverse" if sl > 1.4 else "normal")
with col3:
    st.metric("Runoff Coefficient", f"{ro:.1f} %", f"{(ro - RO_BASELINE):.1f} % vs baseline", delta_color="inverse")
with col4:
    yield_diff = prod_eff - prod_base
    st.metric("Estimated Yield", f"{prod_eff:.0f} kg/ha", f"{yield_diff:.0f} kg/ha via soil mgmt")

st.divider()

# --- 6. Plotting Setup ---
try:
    plt.style.use('seaborn-v0_8-whitegrid')
except OSError:
    try:
        plt.style.use('seaborn-whitegrid')
    except OSError:
        pass

marker_style = dict(marker='o', markersize=12, markerfacecolor='#f1c40f', markeredgecolor='#2c3e50', markeredgewidth=2)

# --- Panel 1 & 2: Soil Loss and Runoff ---
col_charts1, col_charts2 = st.columns(2)

with col_charts1:
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10), facecolor='#f8f9fa')
    plt.subplots_adjust(hspace=0.4)
    
    # Soil Loss Chart
    y_soil = predict_soil_loss(X_VALS, r_inc, oc)
    ax1.plot(X_VALS, y_soil, '#e74c3c', lw=3.5)
    ax1.fill_between(X_VALS, y_soil, color='#e74c3c', alpha=0.15)
    ax1.axhline(1.4, color='#27ae60', linestyle='--', lw=2.5, label='Tolerable Limit')
    ax1.axhspan(0, 1.4, color='#2ecc71', alpha=0.9, zorder=1)
    ax1.axvline(EQ_VEG, color='gray', linestyle=':', lw=2)
    ax1.plot([veg_cover], [sl], **marker_style, zorder=10)
    
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, max(15, max(y_soil) * 1.1)) 
    ax1.set_ylabel('Soil loss (t/ha/y)', fontweight='bold')
    ax1.set_title('Future Soil Loss Projection', fontweight='bold', color='#34495e')
    
    # Runoff Chart
    y_runoff = predict_runoff(X_VALS, r_inc, oc)
    ax2.plot(X_VALS, y_runoff, '#3498db', lw=3.5)
    ax2.fill_between(X_VALS, y_runoff, color='#3498db', alpha=0.15)
    ax2.axvline(EQ_VEG, color='gray', linestyle=':', lw=2, label='OC Tipping Point')
    ax2.plot([veg_cover], [ro], **marker_style, zorder=10)
    
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, max(15, max(y_runoff) * 1.1))
    ax2.set_ylabel('Runoff coefficient (%)', fontweight='bold')
    ax2.set_xlabel('Vegetation cover (%)', fontweight='bold')
    ax2.set_title('Future Runoff Projection', fontweight='bold', color='#34495e')
    ax2.legend(loc='upper right')
    
    st.pyplot(fig1)

# --- Panel 3: Agronomic Impact ---
with col_charts2:
    fig2, ax3 = plt.subplots(figsize=(8, 10.3), facecolor='#f8f9fa')
    
    prod_curve = estimate_productivity(RAIN_RANGE)
    ax3.plot(RAIN_RANGE, prod_curve, '#27ae60', lw=2.5, linestyle='--')
    
    # Plot Baseline vs Effective
    ax3.plot([gross_rain], [prod_base], marker='o', markersize=10, markerfacecolor='gray', markeredgecolor='black', label='Gross Rain (Baseline)')
    ax3.plot([effective_rain], [prod_eff], **marker_style, label='Effective Rain (New Yield)')
    
    # Arrow showing the shift
    ax3.annotate('', xy=(effective_rain, prod_eff), xytext=(gross_rain, prod_base), 
                 arrowprops=dict(facecolor='#e67e22', shrink=0, width=2, headwidth=8), zorder=9)
    
    ax3.set_xlim(0, 1000)
    ax3.set_ylim(0, 4500)
    ax3.set_ylabel('Productivity (kg/ha)', fontweight='bold', fontsize=12)
    ax3.set_xlabel('Annual Rainfall (mm)', fontweight='bold', fontsize=12)
    ax3.set_title('Agronomic Impact (Yield vs Rainfall)', fontweight='bold', color='#34495e', fontsize=14)
    ax3.legend(loc='lower right')
    
    st.pyplot(fig2)