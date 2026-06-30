import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

# File paths
FILE_PATH = "EHSQ Metrics.xlsx"
INCIDENT_PATH = "IncidentReports_All_MTH_2026-06-25.xlsx"

# 1. Load Data
@st.cache_data
def load_all_data():
    return {
        "Incidents": pd.read_excel(INCIDENT_PATH),
        "TCIR": pd.read_excel(FILE_PATH, sheet_name="TCIR and DART", header=1),
        "Housekeeping": pd.read_excel(FILE_PATH, sheet_name="Housekeeping", skiprows=2),
        "CAPAs": pd.read_excel(FILE_PATH, sheet_name="CAPAs", skiprows=2),
        "Observations": pd.read_excel(FILE_PATH, sheet_name="Safe Observations", header=0),
        "Environmental": pd.read_excel(FILE_PATH, sheet_name="Environmental Compliance Issues", header=0),
        "Other": pd.read_excel(FILE_PATH, sheet_name="Other Reports", skiprows=2),
        "FSI": pd.read_excel(FILE_PATH, sheet_name="FSI Reports", skiprows=2),
        "Severity": pd.read_excel(FILE_PATH, sheet_name="Overall Severity Ratings", skiprows=8)
    }

data = load_all_data()
df = data["Incidents"]

# 2. Risk Mitigation Tracker Logic
def map_risk(status):
    if status in ['Completed On Time', 'Completed Late']: return 'Completed'
    if status in ['In Draft', 'In Review']: return 'In Progress'
    if status == 'Resolved in Place': return 'Resolved in Place'
    return 'Need More Information'

df['Cat'] = df['Status'].apply(map_risk)
counts = df['Cat'].value_counts()

# 3. Tabbed Layout
tabs = st.tabs(["Dashboard Overview", "Risk Mitigation", "Core Metrics", "Data Explorer"])

with tabs[0]: # Dashboard Overview
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Incidents", len(df))
    c2.metric("Avg Housekeeping", f"{data['Housekeeping']['Average Plant Score'].mean():.2%}")
    c3.metric("CAPA On-Time", f"{data['CAPAs']['% On Time'].mean():.2%}")
    c4.metric("Completed Risks", int(counts.get("Completed", 0)))
    
    st.divider()
    
    # Severity Graph Integration
    st.subheader("Incident Severity Trend")
    df['Date of Incident (UTC)'] = pd.to_datetime(df['Date of Incident (UTC)'])
    df['Week'] = df['Date of Incident (UTC)'].dt.isocalendar().week
    
    severity_mapping = {
        'Property Damage': 25, 'Record Only - No Treatment': 50, 'First Aid': 75,
        'Molten Metal Spill > 25 lbs': 150, 'Molten Metal Explosion (Force 2 or 3)': 150,
        'Other Recordable Case': 250, 'Restricted or Transferred Work': 250,
        'Days Away From Work': 350, 'Recordable - Fatality': 600 
    }
    
    df['Points'] = df['Injury Classification'].map(severity_mapping).fillna(df['Type'].map(severity_mapping)).fillna(0)
    weekly_scores = df.groupby('Week')['Points'].sum()
    current_week = df['Week'].max()
    weekly_scores = weekly_scores.reindex(range(1, current_week + 1), fill_value=0)

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axhspan(0, 400, color='lightgreen', alpha=0.4, label='Low Risk (0-400)')
    ax.axhspan(400, 800, color='khaki', alpha=0.4, label='Medium Risk (401-800)')
    ax.axhspan(800, 1250, color='lightcoral', alpha=0.4, label='High Risk (800+)')
    
    ax.plot(weekly_scores.index, weekly_scores.values, color='black', linewidth=2.5, marker='o', label='Severity Total')
    ax.set_title('Incident Severity Graph')
    ax.set_xlabel('Calendar Week Number')
    ax.set_ylabel('Total Accumulated Severity Points')
    ax.legend(loc='upper left')
    
    st.pyplot(fig)

# Other tabs (1, 2, 3) remain as you defined them in your script...
