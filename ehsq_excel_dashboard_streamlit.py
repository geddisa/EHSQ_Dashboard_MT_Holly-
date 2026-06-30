import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ... [Keep your existing Data Loading and setup code from the previous block] ...

with tabs[0]: # Dashboard Overview
    # ... [Keep your existing metrics and tables from the previous block] ...

    st.divider()
    
    # Severity Graph - Exact original logic
    st.subheader("Incident Severity Trend (2026)")
    
    # Prepare data
    df_incidents = df_2026.copy()
    severity_mapping = {
        'Property Damage': 25, 'Record Only - No Treatment': 50, 'First Aid': 75,
        'Molten Metal Spill > 25 lbs': 150, 'Molten Metal Explosion (Force 2 or 3)': 150,
        'Other Recordable Case': 250, 'Restricted or Transferred Work': 250,
        'Days Away From Work': 350, 'Recordable - Fatality': 600 
    }
    df_incidents['Points'] = df_incidents['Injury Classification'].map(severity_mapping).fillna(df_incidents['Type'].map(severity_mapping)).fillna(0)
    weekly_scores = df_incidents.groupby('Week')['Points'].sum()
    current_week = df_incidents['Week'].max()

    # Create Figure
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(weekly_scores.index, weekly_scores.values, marker='o', linestyle='-', color='#004c99', linewidth=2)
    
    # Add your original background color bands
    ax.axhspan(0, 400, color='lightgreen', alpha=0.2)
    ax.axhspan(400, 800, color='yellow', alpha=0.2)
    ax.axhspan(800, 1250, color='salmon', alpha=0.2)

    # Add Target Line
    ax.axhline(y=400, color='red', linestyle='--', label='Target Line')
    
    # Add Data Labels for points
    for x, y in zip(weekly_scores.index, weekly_scores.values):
        ax.annotate(str(int(y)), (x, y), textcoords="offset points", xytext=(0,10), ha='center')

    # Formatting labels and title (matches your script)
    ax.set_title('Incident Severity Graph', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Calendar Week Number', fontsize=11, labelpad=12)
    ax.set_ylabel('Total Accumulated Severity Points', fontsize=11, labelpad=12)
    
    # BBox properties for the legend annotations from your original script
    bbox_props = dict(boxstyle="round,pad=0.5", fc="white", ec="gray", lw=1)
    
    st.pyplot(fig)
