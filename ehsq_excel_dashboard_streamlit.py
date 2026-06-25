import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")
# Load the Excel file once
FILE_PATH = "EHSQ Metrics.xlsx"

# 1. Load Data
@st.cache_data
def load_all_data():
    # Load Master Files
    incidents = pd.read_excel("IncidentReports_All_MTH_2026-06-25.xlsx")
    metrics = "EHSQ Metrics.xlsx"
    
    # Load all sheets with correct skiprows to align with your file structure
    return {
        "Incidents": incidents,
        "TCIR": pd.read_excel(metrics, sheet_name="TCIR and DART", header=1),
        "Housekeeping": pd.read_excel(metrics, sheet_name="Housekeeping", skiprows=2),
        "CAPAs": pd.read_excel(metrics, sheet_name="CAPAs", skiprows=2),
        "Observations": pd.read_excel(metrics, sheet_name="Safe Observations", header=0)
    # Use specific header/skiprows settings based on your file structure
    data = {
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
    c4.metric("Completed Risks", counts.get("Completed", 0))

with tabs[1]: # Risk Mitigation Tracker
    st.subheader("Risk Mitigation Tracker")
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Completed", counts.get("Completed", 0))
    b2.metric("In Progress", counts.get("In Progress", 0))
    b3.metric("Resolved in Place", counts.get("Resolved in Place", 0))
    b4.metric("Need More Info", counts.get("Need More Information", 0))
    st.dataframe(df[['Incident', 'Status', 'Department', 'Description']], use_container_width=True)

with tabs[2]: # Core Metrics (Charts with Data Labels)
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("TCIR & DART Trends")
        fig1 = px.line(data["TCIR"], x='Month', y=['TCIR Actual', 'DART Actual'], markers=True)
        fig1.update_traces(texttemplate='%{y:.2f}', textposition='top center')
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_b:
        st.subheader("Safe Observations")
        fig2 = px.bar(data["Observations"], x='Unnamed: 0', y='% Completed', text_auto='.0%')
        st.plotly_chart(fig2, use_container_width=True)

with tabs[3]: # Data Explorer
    selected = st.selectbox("Select Excel Sheet", list(data.keys()))
    st.dataframe(data[selected], use_container_width=True)    st.subheader("Risk Mitigation Tracker")
    
    def map_risk(status):
        if status in ['Completed On Time', 'Completed Late']: return 'Completed'
        if status in ['In Draft', 'In Review']: return 'In Progress'
        if status == 'Resolved in Place': return 'Resolved in Place'
        return 'Need More Information'

    df['Cat'] = df['Status'].apply(map_risk)
    counts = df['Cat'].value_counts()

    # The 4 Required Boxes
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Completed", counts.get("Completed", 0))
    b2.metric("In Progress", counts.get("In Progress", 0))
    b3.metric("Resolved in Place", counts.get("Resolved in Place", 0))
    b4.metric("Need More Info", counts.get("Need More Information", 0))
    
    st.divider()
    st.dataframe(df[['Incident', 'Status', 'Department', 'Description']], use_container_width=True)

with tab3:
    st.subheader("System Performance Metrics")
    col_a, col_b = st.columns(2)
    
    with col_a:
        fig1 = px.line(tcir_df, x='Month', y=['TCIR Actual', 'DART Actual'], title="TCIR & DART Trends")
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_b:
        fig2 = px.bar(capa_df, x='Unnamed: 0', y='% On Time', title="CAPA On-Time Performance")
        st.plotly_chart(fig2, use_container_width=True)
    return data
