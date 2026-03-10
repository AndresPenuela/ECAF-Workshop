import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. App Configuration ---
st.set_page_config(page_title="Future Soil Loss & Runoff", layout="wide")
st.title("Predictive Erosion & Runoff Model")
st.markdown("Adjust the parameters in the sidebar to see the projected impact on soil loss and runoff.")

# --- 2. Predictive Mathematical Models ---
def get_equilibrium_veg():
    """Calculates the exact veg cover needed to reach tolerable soil loss (1.4)."""
    return - (1.0 / 0.06) * np.log(1.4 / 11.47)

def project_parameters(veg_cover, years):
    """Predicts future rainfall erosivity and OC based on time and management."""
    rain_increase_pct = years * 0.5
    baseline_oc = 1.5
    veg_eq = get_equilibrium_veg() 
    annual_oc_change = (veg_cover - veg_eq) * 0.001
    future_oc = baseline_oc + (annual_oc_change * years)
    future_oc = max(0.5, min(5.0, future_oc)) 
    return rain_increase_pct, future_oc

def predict_soil_loss(veg_cover, rain_increase_pct, oc_pct):
    """Calculates soil loss with RUSLE R and K factor adjustments."""
    base_soil_loss = 11.47 * np.exp(-0.06 * veg_cover)
    m_r = 1.0 + (rain_increase_pct / 100.0)
    om_baseline = 1.5 * 1.724 
    om_new = oc_pct * 1.724
    m_k = (12.0 - om_new) / (12.0 - om_baseline)
    m_k = max(0.1, m_k) 
    return base_soil_loss * m_r * m_k

def predict_runoff(veg_cover, rain_increase_pct, oc_pct):
    """Calculates runoff coefficient with hydrological modifiers."""
    base_runoff = np.maximum(0, -0.11 * veg_cover + 11.59)
    m_rain = 1.0 + (rain_increase_pct / 100.0) * 0.5 
    m_oc = np.exp(-0.2 * (oc_pct - 1.5)) 
    final_runoff = base_runoff * m_rain * m_oc
    return np.minimum(100.0, final_runoff)

# --- 3. Sidebar Inputs ---
st.sidebar.header("Model Parameters")
v = st.sidebar.slider('Veg Cover (%)', min_value=0.0, max_value=100.0, value=0.0, step=1.0)
years = st.sidebar.radio('Years Future', options=[0, 10, 25, 50])

# --- 4. Core Calculations ---
x_vals = np.linspace(0, 100, 500)
r_inc, oc = project_parameters(v, years)
veg_eq = get_equilibrium_veg()

sl = predict_soil_loss(v, r_inc, oc)
ro = predict_runoff(v, r_inc, oc)

if years == 0:
    oc_trend = "(Baseline)"
elif v > veg_eq + 0.5:
    oc_trend = "(Regenerating)"
elif v < veg_eq - 0.5:
    oc_trend = "(Degrading)"
else:
    oc_trend = "(Equilibrium)"

env_context = f"Context in Year {years}:\n• Erosivity Inc: +{r_inc:.1f}%\n• Projected OC: {oc:.2f}% {oc_trend}"

status_text = 'Status: Tolerable' if sl <= 1.4 else 'Status: High Risk'
text_color = '#27ae60' if sl <= 1.4 else '#c0392b'

# --- 5. Plotting Setup ---
box_style = dict(boxstyle='round,pad=0.8', facecolor='#ffffff', alpha=0.95, edgecolor='#bdc3c7', linewidth=1.5)
marker_style = dict(marker='o', markersize=12, markerfacecolor='#f1c40f', markeredgecolor='#2c3e50', markeredgewidth=2, zorder=10)

# Create two columns for a side-by-side layout
col1, col2 = st.columns(2)

# --- Panel 1: Soil Loss (Left Column) ---
with col1:
    fig1, ax1 = plt.subplots(figsize=(7, 6), facecolor='#f4f6f9')
    plt.subplots_adjust(bottom=0.15) 
    
    color_soil = '#e74c3c'
    new_y_soil = predict_soil_loss(x_vals, r_inc, oc)

    ax1.plot(x_vals, new_y_soil, color=color_soil, lw=3)
    ax1.fill_between(x_vals, new_y_soil, color=color_soil, alpha=0.15)
    ax1.axhline(1.4, color='#27ae60', linestyle='--', lw=2, label='Tolerable Limit (1.4 t/ha/y)')
    ax1.axvline(veg_eq, color='gray', linestyle=':', lw=1.5, label='OC Equilibrium')
    ax1.axhspan(0, 1.4, color='#2ecc71', alpha=0.15)

    ax1.plot([v], [sl], **marker_style)
    text1_content = f'{env_context}\n\nSoil Loss: {sl:.2f} t/ha/y\n{status_text}'
    ax1.text(0.40, 0.55, text1_content, transform=ax1.transAxes, fontsize=10, fontweight='bold', bbox=box_style, color=text_color)

    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, 15)
    ax1.set_ylabel('Soil loss (t/ha/y)', fontsize=12, fontweight='bold', color='#34495e')
    ax1.set_xlabel('Vegetation cover (%)', fontsize=12, fontweight='bold', color='#34495e')
    ax1.set_title('Future Soil Loss', fontsize=14, color='#34495e', pad=10)
    ax1.grid(True, color='#e0e6ed', linestyle='-', linewidth=1)
    
    st.pyplot(fig1)

# --- Panel 2: Runoff Coefficient (Right Column) ---
with col2:
    fig2, ax2 = plt.subplots(figsize=(7, 6), facecolor='#f4f6f9')
    plt.subplots_adjust(bottom=0.15) 
    
    color_runoff = '#3498db'
    new_y_runoff = predict_runoff(x_vals, r_inc, oc)

    ax2.plot(x_vals, new_y_runoff, color=color_runoff, lw=3)
    ax2.fill_between(x_vals, new_y_runoff, color=color_runoff, alpha=0.15)
    ax2.axvline(veg_eq, color='gray', linestyle=':', lw=1.5, label='OC Equilibrium')

    ax2.plot([v], [ro], **marker_style)
    text2_content = f'{env_context}\n\nRunoff: {ro:.2f} %'
    ax2.text(0.40, 0.65, text2_content, transform=ax2.transAxes, fontsize=10, fontweight='bold', bbox=box_style, color='#2980b9')

    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 15)
    ax2.set_ylabel('Runoff coefficient (%)', fontsize=12, fontweight='bold', color='#34495e')
    ax2.set_xlabel('Vegetation cover (%)', fontsize=12, fontweight='bold', color='#34495e')
    ax2.set_title('Future Runoff', fontsize=14, color='#34495e', pad=10)
    ax2.grid(True, color='#e0e6ed', linestyle='-', linewidth=1)
    
    st.pyplot(fig2)