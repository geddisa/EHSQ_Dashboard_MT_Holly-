import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

# Paths
INCIDENT_PATH = "IncidentReports_All_MTH_2026-06-25.xlsx"
FILE_PATH = "EHSQ Metrics.xlsx"

@st.cache_data
def load_all_data():
    # Load Incidents
    incidents = pd.read_excel(INCIDENT_PATH)
    # Remove any accidental leading/trailing spaces in headers
    incidents.columns = incidents.columns.str.strip()
    
    return {
        "Incidents": incidents,
        "TCIR": pd.read_excel(FILE_PATH, sheet_name="TCIR and DART", skiprows=1),
        "Housekeeping": pd.read_excel(FILE_PATH, sheet_name="Housekeeping", skiprows=2),
        "CAPAs": pd.read_excel(FILE_PATH, sheet_name="CAPAs", skiprows=2),
        "Observations": pd.read_excel(FILE_PATH, sheet_name="Safe Observations", skiprows=1),
        "Severity": pd.read_excel(FILE_PATH, sheet_name="Overall Severity Ratings")
    }

data = load_all_data()
df = data["Incidents"]

# Now the column lookup will be much more resilient
df['Date'] = pd.to_datetime(df['Date of Incident (EDT)'])
df['Week'] = df['Date'].dt.isocalendar().week

# Mapping
def map_risk(status):
    if status in ['Completed On Time', 'Completed Late']: return 'Completed'
    if status in ['In Draft', 'In Review']: return 'In Progress'
    return 'Need More Information'

df['Cat'] = df['Status'].apply(map_risk)
counts = df['Cat'].value_counts()

# --- Tabs ---
tabs = st.tabs(["Overview", "Severity Graph", "KPI Visuals", "Data Explorer"])

with tabs[0]: # Dashboard Overview
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Incidents", len(df))
    # Ensure column names match exactly what is in your Excel
    c2.metric("Avg Housekeeping", f"{data['Housekeeping']['Average Plant Score'].mean():.2%}")
    c3.metric("CAPA On-Time", f"{data['CAPAs']['% On Time'].mean():.2%}")
    c4.metric("Completed Risks", int(counts.get("Completed", 0)))

with tabs[1]: # Severity Graph
    st.subheader("Incident Severity Trend (2026)")
    # Using 'Classification ' as identified in your CSV metadata
    sev_map = dict(zip(data['Severity']['Classification '], data['Severity']['Points Assigned']))
    df['Points'] = df['Injury Classification'].map(sev_map).fillna(0)
    w_scores = df.groupby('Week')['Points'].sum().reindex(range(1, 25), fill_value=0)
    
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axhspan(0, 400, color='lightgreen', alpha=0.3)
    ax.axhspan(400, 800, color='khaki', alpha=0.3)
    ax.axhspan(800, 1250, color='lightcoral', alpha=0.3)
    ax.plot(w_scores.index, w_scores.values, color='black', linewidth=2.5, marker='o')
    ax.axhline(y=400, color='red', linestyle='--', label='Target Line')
    
    for x, y in zip(w_scores.index, w_scores.values):
        if y > 0: ax.annotate(str(int(y)), (x, y), xytext=(0,10), textcoords="offset points", ha='center')
    st.pyplot(fig)

with tabs[2]: # KPI Visuals
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.line(data["TCIR"], x='Month', y=['TCIR Actual', 'DART Actual'], title="TCIR & DART Trends", markers=True))
    with col2:
        st.plotly_chart(px.bar(df['Type'].value_counts().reset_index(), x='Type', y='count', title="Incidents by Type"))

with tabs[3]: # Data Explorer
    sheet = st.selectbox("Select Data", list(data.keys()))
    st.dataframe(data[sheet], use_container_width=True)
