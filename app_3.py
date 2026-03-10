import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. App Configuration ---
st.set_page_config(page_title="Olive Productivity Model", layout="centered")
st.title("Olive Productivity Estimation Model")
st.markdown("Interactive tool to estimate olive yield based on annual rainfall in Andalusia.")

# --- 2. Mathematical Model & Constants ---
def estimate_productivity(rainfall):
    """Calculates olive productivity trend based on a segmented linear-plateau model."""
    return np.maximum(0, np.minimum(3350, 10 * (rainfall - 120)))

BASE_RAIN = 450.0
BASE_PROD = estimate_productivity(BASE_RAIN)

# --- 3. Sidebar Input ---
st.sidebar.header("Model Parameters")
r = st.sidebar.slider(
    'Gross Rain (mm)', 
    min_value=0.0, 
    max_value=1000.0, 
    value=450.0, 
    step=10.0
)

# --- 4. Core Calculations ---
prod_estimate = estimate_productivity(r)

# Calculate differences against the 450mm baseline
rain_diff = r - BASE_RAIN
prod_diff = prod_estimate - BASE_PROD

# Determine Status
if r < 120:
    status_text = 'Status: Minimal Production (Drought)'
elif r < 455:
    status_text = 'Status: Water-Limited Growth'
else:
    status_text = 'Status: Productivity Plateau'

# --- 5. Metrics Dashboard (Streamlit Native UI) ---
col1, col2, col3 = st.columns(3)
col1.metric("Selected Rainfall", f"{int(r)} mm", f"{int(rain_diff)} mm vs baseline" if r != BASE_RAIN else None)
col2.metric("Estimated Yield", f"{int(prod_estimate)} kg/ha", f"{int(prod_diff)} kg/ha vs baseline" if r != BASE_RAIN else None)
col3.info(status_text)

st.divider()

# --- 6. Plotting Setup ---
try:
    plt.style.use('seaborn-v0_8-whitegrid')
except OSError:
    try:
        plt.style.use('seaborn-whitegrid')
    except OSError:
        pass 

fig, ax1 = plt.subplots(figsize=(10, 6), facecolor='#f4f6f9')

rain_range = np.linspace(0, 1000, 500)
estimated_productivity = estimate_productivity(rain_range)

box_style = dict(boxstyle='round,pad=0.8', facecolor='#ffffff', alpha=0.95, edgecolor='#bdc3c7', linewidth=1.5)
marker_style = dict(marker='o', markersize=13, markerfacecolor='#f1c40f', markeredgecolor='black', markeredgewidth=1.5, zorder=10)

# Main Plot: Estimated Productivity vs Annual Rainfall
ax1.plot(rain_range, estimated_productivity, '#27ae60', lw=2.5, linestyle='--', label='Estimated Trendline')

# Baseline Reference Point (450 mm)
ax1.plot([BASE_RAIN], [BASE_PROD], marker='o', markersize=10, markerfacecolor='gray', markeredgecolor='black', zorder=9, label='Baseline (450 mm)')

# Dynamic elements: current dot and deficit arrow
ax1.plot([r], [prod_estimate], **marker_style, label='Current Selection')

if r < BASE_RAIN:
    ax1.annotate('', xy=(r, prod_estimate), xytext=(BASE_RAIN, BASE_PROD), 
                 arrowprops=dict(facecolor='#e74c3c', shrink=0, width=2, headwidth=8), zorder=8)

# Build text dynamically
display_text = f'For {int(r)} mm Annual Rainfall:\nEstimated Yield: {int(prod_estimate)} kg/ha\n'

if r < BASE_RAIN:
    display_text += f'\n--- Deficit vs Baseline (450mm) ---\n'
    display_text += f'Rain Decrease: {int(rain_diff)} mm\n'
    display_text += f'Yield Loss: {int(prod_diff)} kg/ha\n'
    
display_text += f'\n{status_text}'
    
ax1.text(0.05, 0.85, display_text, transform=ax1.transAxes, fontsize=12, bbox=box_style, va='top', color='#2c3e50')

# Plot settings
ax1.set_xlim(0, 1000)
ax1.set_ylim(0, 4500)
ax1.set_ylabel('Productivity (kg/ha)', fontsize=12, fontweight='bold', color='#34495e')
ax1.set_xlabel('Annual Rainfall (mm)', fontsize=12, fontweight='bold', color='#34495e')
ax1.set_title('Agronomic Impact (Yield vs Rainfall)', fontsize=14, fontweight='bold', color='#34495e', pad=10)
ax1.grid(True, color='#e0e6ed', linestyle='--', alpha=0.6, linewidth=1)
ax1.legend(loc='lower right', framealpha=1, fontsize=10)

# Render the plot in Streamlit
st.pyplot(fig)