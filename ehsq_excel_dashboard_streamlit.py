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

# Ensure date formatting for 2026 analysis
df['Date of Incident (UTC)'] = pd.to_datetime(df['Date of Incident (UTC)'])
df['Year'] = df['Date of Incident (UTC)'].dt.year
df['Week'] = df['Date of Incident (UTC)'].dt.isocalendar().week

# Filter specifically for 2026 data
df_2026 = df[df['Year'] == 2026].copy()

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
    c1.metric("Total Incidents (2026)", len(df_2026))
    c2.metric("Avg Housekeeping", f"{data['Housekeeping']['Average Plant Score'].mean():.2%}")
    c3.metric("CAPA On-Time", f"{data['CAPAs']['% On Time'].mean():.2%}")
    c4.metric("Completed Risks", int(counts.get("Completed", 0)))
    
    st.divider()
    
    # Recent Incidents 
    st.subheader("Recent Incidents")
    june_incidents = df_2026[df_2026['Date of Incident (UTC)'].dt.month == 6]
    if not june_incidents.empty:
        st.dataframe(june_incidents.sort_values(by='Date of Incident (UTC)', ascending=False), use_container_width=True)
    else:
        st.info("No incidents recorded for June 2026.")
    
    st.divider()
    
    # Severity Graph (2026 Focused)
    st.subheader("Incident Severity Trend (2026)")
    severity_mapping = {
        'Property Damage': 25, 'Record Only - No Treatment': 50, 'First Aid': 75,
        'Molten Metal Spill > 25 lbs': 150, 'Molten Metal Explosion (Force 2 or 3)': 150,
        'Other Recordable Case': 250, 'Restricted or Transferred Work': 250,
        'Days Away From Work': 350, 'Recordable - Fatality': 600 
    }
    df_2026['Points'] = df_2026['Injury Classification'].map(severity_mapping).fillna(df_2026['Type'].map(severity_mapping)).fillna(0)
    weekly_scores = df_2026.groupby('Week')['Points'].sum().reindex(range(1, df_2026['Week'].max() + 1), fill_value=0)

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axhspan(0, 400, color='lightgreen', alpha=0.4, label='Low Risk (0-400)')
    ax.axhspan(400, 800, color='khaki', alpha=0.4, label='Medium Risk (401-800)')
    ax.axhspan(800, 1250, color='lightcoral', alpha=0.4, label='High Risk (800+)')
    ax.plot(weekly_scores.index, weekly_scores.values, color='black', linewidth=2.5, marker='o', label='Weekly Severity Total')
    ax.set_title('Incident Severity Graph (2026)')
    ax.set_xlabel('Calendar Week Number')
    ax.set_ylabel('Total Accumulated Severity Points')
    ax.set_xticks(range(1, df_2026['Week'].max() + 1))
    ax.legend(loc='upper left')
    st.pyplot(fig)

with tabs[1]: # Risk Mitigation Tracker
    st.subheader("Risk Mitigation Tracker")
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Completed", int(counts.get("Completed", 0)))
    b2.metric("In Progress", int(counts.get("In Progress", 0)))
    b3.metric("Resolved in Place", int(counts.get("Resolved in Place", 0)))
    b4.metric("Need More Info", int(counts.get("Need More Information", 0)))
    st.divider()
    st.dataframe(df[['Incident', 'Status', 'Department', 'Description']], use_container_width=True)

with tabs[2]: # Core Metrics
    st.subheader("System Performance Metrics")
    col_a, col_b = st.columns(2)
    with col_a:
        fig1 = px.line(data["TCIR"], x='Month', y=['TCIR Actual', 'DART Actual'], title="TCIR & DART Trends", markers=True)
        st.plotly_chart(fig1, use_container_width=True)
    with col_b:
        fig2 = px.bar(data["CAPAs"], x=data["CAPAs"].columns[0], y='% On Time', title="CAPA On-Time Performance")
        st.plotly_chart(fig2, use_container_width=True)

with tabs[3]: # Data Explorer
    selected = st.selectbox("Select Excel Sheet", list(data.keys()))
    st.dataframe(data[selected], use_container_width=True)
