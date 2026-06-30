import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

# Paths
FILE_PATH = "EHSQ Metrics.xlsx"
INCIDENT_PATH = "IncidentReports_All_MTH_2026-06-25.xlsx"

@st.cache_data
def load_all_data():
    incidents = pd.read_excel(INCIDENT_PATH)
    incidents.columns = incidents.columns.str.strip()
    return {
        "Incidents": incidents,
        "TCIR": pd.read_excel(FILE_PATH, sheet_name="TCIR and DART", skiprows=1),
        "Housekeeping": pd.read_excel(FILE_PATH, sheet_name="Housekeeping", skiprows=2),
        "CAPAs": pd.read_excel(FILE_PATH, sheet_name="CAPAs", skiprows=2),
        "Severity": pd.read_excel(FILE_PATH, sheet_name="Overall Severity Ratings")
    }

data = load_all_data()
df = data["Incidents"]

# Prepare Date
df['Date'] = pd.to_datetime(df['Date of Incident (EDT)'])
df['Week'] = df['Date'].dt.isocalendar().week

# Severity Logic from your provided script
severity_mapping = {
    'Property Damage': 25, 'Record Only - No Treatment': 50, 'First Aid': 75,
    'Molten Metal Spill > 25 lbs': 150, 'Molten Metal Explosion (Force 2 or 3)': 150,
    'Other Recordable Case': 250, 'Restricted or Transferred Work': 250,
    'Days Away From Work': 350, 'Recordable - Fatality': 600 
}

df['Points'] = df['Injury Classification'].map(severity_mapping).fillna(
    df['Type'].map(severity_mapping)).fillna(0)

weekly_scores = df.groupby('Week')['Points'].sum().reindex(range(1, 25), fill_value=0)
current_week = weekly_scores.index[-1]

# Layout
tabs = st.tabs(["Overview", "Severity Graph", "KPI Visuals", "Data Explorer"])

with tabs[1]: # Severity Graph
    st.subheader("Incident Severity Trend (2026)")
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(weekly_scores.index, weekly_scores.values, color='#1f77b4', linewidth=2.5, marker='o')
    
    # Legend/Labeling logic from your script
    bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="gray", lw=1.0)
    static_y_positions = {25: 25, 50: 140, 75: 255, 150: 375, 250: 515, 350: 640, 600: 760}
    
    # Note: Replace 'grouped_mapping' with a simple dict iteration if your script didn't define it globally
    for pt, y_pos in static_y_positions.items():
        ax.text(current_week + 0.6, y_pos, f"{pt} pt", va='center', ha='left', fontsize=8.5, bbox=bbox_props)
    
    ax.set_title('Incident Severity Graph', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Calendar Week Number', fontsize=11, labelpad=12)
    ax.set_ylabel('Total Accumulated Severity Points', fontsize=11, labelpad=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig)

with tabs[0]: # Dashboard Overview
    st.metric("Total Incidents", len(df))
    st.dataframe(df.head())

with tabs[3]: # Data Explorer
    sheet = st.selectbox("Select Data", list(data.keys()))
    st.dataframe(data[sheet])
