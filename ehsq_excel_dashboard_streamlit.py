import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="EHSQ Performance Dashboard", layout="wide")
st.title("EHSQ Performance Dashboard")

# 2. Data Loading (Excel-Only)
@st.cache_data
def load_data():
    # Load Incident Data
    df = pd.read_excel("IncidentReports_All_MTH_2026-06-25.xlsx", sheet_name="Sheet1")
    
    # Load Metrics (Skipping header rows to align with your specific Excel format)
    metrics_file = "EHSQ Metrics.xlsx"
    tcir = pd.read_excel(metrics_file, sheet_name="TCIR and DART", header=1)
    house = pd.read_excel(metrics_file, sheet_name="Housekeeping", skiprows=2)
    capa = pd.read_excel(metrics_file, sheet_name="CAPAs", skiprows=2)
    
    return df, tcir, house, capa

df, tcir_df, house_df, capa_df = load_data()

# 3. Tab Structure (Power BI Style)
tab1, tab2, tab3 = st.tabs(["Dashboard Overview", "Risk Mitigation", "System Metrics"])

with tab1:
    st.subheader("Executive KPI Overview")
    # Top Level Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Incidents", len(df))
    c2.metric("Total Recordables", len(df[df['Injury Classification'] != 'No Data']))
    c3.metric("Avg Housekeeping", f"{house_df['Average Plant Score'].mean():.2%}")

with tab2:
    st.subheader("Risk Mitigation Tracker")
    
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
