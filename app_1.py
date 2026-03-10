import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. App Configuration ---
st.set_page_config(page_title="Soil Loss & Runoff Explorer", layout="wide")
st.title("Soil Loss & Runoff - Scenario Exploration")
st.markdown("Use the sidebar to adjust environmental and management parameters.")

# --- 2. Define the Mathematical Models ---
def predict_soil_loss(veg_cover, rain_increase_pct, oc_pct):
    """Calculates soil loss with RUSLE R and K factor adjustments."""
    base_soil_loss = 11.47 * np.exp(-0.06 * veg_cover)
    m_r = 1.0 + (rain_increase_pct / 100.0)
    
    # Updated baseline OM calculation for 1.5% OC
    om_baseline = 1.5 * 1.724
    om_new = oc_pct * 1.724
    m_k = (12.0 - om_new) / (12.0 - om_baseline)
    m_k = max(0.1, m_k) 
    
    return base_soil_loss * m_r * m_k

def predict_runoff(veg_cover, rain_increase_pct, oc_pct):
    """Calculates runoff coefficient with hydrological modifiers."""
    base_runoff = np.maximum(0, -0.11 * veg_cover + 11.59)
    
    m_rain = 1.0 + (rain_increase_pct / 100.0) * 0.5 
    # Updated exponential modifier so 1.5% OC acts as the true baseline
    m_oc = np.exp(-0.2 * (oc_pct - 1.5))
    
    final_runoff = base_runoff * m_rain * m_oc
    return np.minimum(100.0, final_runoff)

# Calculate the equilibrium vegetation cover (where soil loss = 1.4)
eq_veg = - (1.0 / 0.06) * np.log(1.4 / 11.47)
x_vals = np.linspace(0, 100, 500)

# --- 3. Sidebar Inputs (Streamlit Native UI) ---
st.sidebar.header("Model Parameters")
v = st.sidebar.slider("Veg Cover (%) (Management)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
r_inc = st.sidebar.slider("Rainfall Erosivity Increase (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
oc = st.sidebar.slider("Soil Organic Carbon (%)", min_value=0.5, max_value=6.0, value=1.5, step=0.1)

# --- 4. Core Calculations ---
sl = predict_soil_loss(v, r_inc, oc)
ro = predict_runoff(v, r_inc, oc)

new_y_soil = predict_soil_loss(x_vals, r_inc, oc)
new_y_runoff = predict_runoff(x_vals, r_inc, oc)

# Status determinations
if sl <= 1.4:
    status = 'Tolerable'
    text_color = '#27ae60' 
else:
    status = 'High Risk'
    text_color = '#c0392b' 

# --- 5. Plotting Setup ---
# Set modern style if available
try:
    plt.style.use('seaborn-v0_8-whitegrid')
except OSError:
    try:
        plt.style.use('seaborn-whitegrid')
    except OSError:
        pass

fig = plt.figure(figsize=(10, 9), facecolor='#f8f9fa')
ax1 = fig.add_subplot(211, facecolor='#ffffff')
ax2 = fig.add_subplot(212, facecolor='#ffffff')
plt.subplots_adjust(bottom=0.1, hspace=0.35) 

box_style = dict(boxstyle='round,pad=1', facecolor='#ffffff', alpha=0.95, edgecolor='#bdc3c7', linewidth=1.5)
marker_style = dict(marker='o', markersize=14, markerfacecolor='#f1c40f', markeredgecolor='#2c3e50', markeredgewidth=2.5, zorder=10)

color_soil = '#e74c3c'
color_runoff = '#3498db'

# === Plot a) Soil Loss ===
ax1.plot(x_vals, new_y_soil, color=color_soil, lw=3.5, label='Soil loss model', zorder=4)
ax1.fill_between(x_vals, new_y_soil, color=color_soil, alpha=0.15, zorder=2)
ax1.axhline(1.4, color='#27ae60', linestyle='--', lw=2.5, label='Tolerable Limit (1.4 t/ha/y)', zorder=5)
ax1.axvline(eq_veg, color='gray', linestyle=':', lw=2, label='OC Equilibrium Tipping Point', zorder=3)
ax1.axhspan(0, 1.4, color='#2ecc71', alpha=0.9, zorder=1) 

# Dynamic Point and Text
ax1.plot([v], [sl], **marker_style)
text_sl = f'Parameters:\n• Erosivity Inc: +{r_inc:.1f}%\n• Soil OC: {oc:.2f}%\n\nSoil Loss: {sl:.2f} t/ha/y\nStatus: {status}'
ax1.text(0.75, 0.40, text_sl, transform=ax1.transAxes, fontsize=11, fontweight='bold', bbox=box_style, zorder=11, color=text_color)

ax1.set_xlim(0, 100)
# Dynamic Y-Axis scale based on spikes
max_soil = max(new_y_soil)
ax1.set_ylim(0, max(15, max_soil * 1.1) if max_soil > 15 else 15) 

ax1.set_ylabel('Soil loss (t/ha/y)', fontsize=12, fontweight='bold', color='#34495e')
ax1.set_title('Soil loss model - Scenario exploration', fontsize=15, color='#34495e', pad=15)
ax1.grid(True, color='#e2e8f0', linestyle='-', linewidth=1.5, zorder=0)

# === Plot b) Runoff Coefficient ===
ax2.plot(x_vals, new_y_runoff, color=color_runoff, lw=3.5, label='Runoff model', zorder=4)
ax2.fill_between(x_vals, new_y_runoff, color=color_runoff, alpha=0.15, zorder=2)
ax2.axvline(eq_veg, color='gray', linestyle=':', lw=2, label='OC Equilibrium Tipping Point', zorder=3)

# Dynamic Point and Text
ax2.plot([v], [ro], **marker_style)
text_ro = f'Parameters:\n• Erosivity Inc: +{r_inc:.1f}%\n• Soil OC: {oc:.2f}%\n\nRunoff: {ro:.2f} %'
ax2.text(0.75, 0.40, text_ro, transform=ax2.transAxes, fontsize=11, fontweight='bold', bbox=box_style, zorder=11, color='#2980b9')

ax2.set_xlim(0, 100)
ax2.set_ylim(0, 15)
ax2.set_ylabel('Runoff coefficient (%)', fontsize=12, fontweight='bold', color='#34495e')
ax2.set_xlabel('Vegetation cover (%)', fontsize=12, fontweight='bold', color='#34495e')
ax2.set_title('Runoff model - Scenario exploration', fontsize=15, color='#34495e', pad=15)
ax2.grid(True, color='#e2e8f0', linestyle='-', linewidth=1.5, zorder=0)

# --- 6. Render the Plot ---
# st.pyplot() draws the Matplotlib figure right into the browser
st.pyplot(fig)