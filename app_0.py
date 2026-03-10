import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. App Configuration ---
st.set_page_config(page_title="Soil & Runoff Model", layout="wide")
st.title("Mediterranean Olive Orchards - Erosion & Runoff")
st.markdown("Use the slider in the sidebar to adjust the vegetation cover and see its impact.")

# --- 2. Mathematical Models ---
def predict_soil_loss(veg_cover):
    """Calculates soil loss (baseline Year 0 context)."""
    return 11.47 * np.exp(-0.06 * veg_cover)

def predict_runoff(veg_cover):
    """Calculates runoff coefficient (%) based on linear fit."""
    return -0.11 * veg_cover + 11.59

# --- 3. Sidebar Input (Streamlit Native UI) ---
st.sidebar.header("Management Parameters")
v = st.sidebar.slider("Vegetation cover (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0)

# --- 4. Core Calculations ---
x_vals = np.linspace(0, 100, 500)

sl = predict_soil_loss(v)
ro = predict_runoff(v)

y_soil = predict_soil_loss(x_vals)
y_runoff = predict_runoff(x_vals)

# Determine Status & Colors
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

box_style = dict(boxstyle='round,pad=1', facecolor='#ffffff', alpha=0.95, edgecolor='#bdc3c7', linewidth=1.5)
marker_style = dict(marker='o', markersize=14, markerfacecolor='#f1c40f', markeredgecolor='#2c3e50', markeredgewidth=2.5, zorder=10)

color_soil = '#e74c3c'
color_runoff = '#3498db'

# Create two columns to display charts side-by-side
col1, col2 = st.columns(2)

# === Plot a) Soil Loss (Left Column) ===
with col1:
    fig1, ax1 = plt.subplots(figsize=(6, 5), facecolor='#f8f9fa')
    plt.subplots_adjust(bottom=0.15)
    
    # Plot curves and fills
    ax1.plot(x_vals, y_soil, color=color_soil, lw=3.5, label='Soil loss model', zorder=4)
    ax1.fill_between(x_vals, y_soil, color=color_soil, alpha=0.15, zorder=2)
    ax1.axhline(1.4, color='#27ae60', linestyle='--', lw=2.5, label='Tolerable Limit (1.4 t/ha/y)', zorder=5)
    ax1.axhspan(0, 1.4, color='#2ecc71', alpha=0.9, zorder=1) 

    # Dynamic Point and Text
    ax1.plot([v], [sl], **marker_style)
    text_sl = f'Soil Loss: {sl:.2f} t/ha/y\nStatus: {status}'
    ax1.text(0.40, 0.45, text_sl, transform=ax1.transAxes, fontsize=11, fontweight='bold', bbox=box_style, zorder=11, color=text_color)

    # Formatting
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, 15) 
    ax1.set_ylabel('Soil loss (t/ha/y)', fontsize=12, fontweight='bold', color='#34495e')
    ax1.set_xlabel('Vegetation cover (%)', fontsize=12, fontweight='bold', color='#34495e')
    ax1.set_title('Soil loss model - Mediterranean Olive Orchards', fontsize=13, color='#34495e', pad=15)
    ax1.grid(True, color='#e2e8f0', linestyle='-', linewidth=1.5, zorder=0)
    ax1.legend(loc='upper right', framealpha=1, edgecolor='#bdc3c7')
    
    # Render in Streamlit
    st.pyplot(fig1)

# === Plot b) Runoff Coefficient (Right Column) ===
with col2:
    fig2, ax2 = plt.subplots(figsize=(6, 5), facecolor='#f8f9fa')
    plt.subplots_adjust(bottom=0.15)

    # Plot curves and fills
    ax2.plot(x_vals, y_runoff, color=color_runoff, lw=3.5, label='Runoff model', zorder=4)
    ax2.fill_between(x_vals, y_runoff, color=color_runoff, alpha=0.15, zorder=2)

    # Dynamic Point and Text
    ax2.plot([v], [ro], **marker_style)
    text_ro = f'Runoff: {ro:.2f} %'
    ax2.text(0.40, 0.55, text_ro, transform=ax2.transAxes, fontsize=11, fontweight='bold', bbox=box_style, zorder=11, color='#2980b9')

    # Formatting
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 15)
    ax2.set_ylabel('Runoff coefficient (%)', fontsize=12, fontweight='bold', color='#34495e')
    ax2.set_xlabel('Vegetation cover (%)', fontsize=12, fontweight='bold', color='#34495e')
    ax2.set_title('Surface runoff model - Mediterranean Olive Orchards', fontsize=13, color='#34495e', pad=15)
    ax2.grid(True, color='#e2e8f0', linestyle='-', linewidth=1.5, zorder=0)
    ax2.legend(loc='upper right', framealpha=1, edgecolor='#bdc3c7')
    
    # Render in Streamlit
    st.pyplot(fig2)