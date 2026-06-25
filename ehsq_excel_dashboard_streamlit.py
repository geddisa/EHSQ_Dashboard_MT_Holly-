import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="EHSQ Performance Dashboard", layout="wide")
st.title("EHSQ Performance Dashboard")

# 2. Data Loading
@st.cache_data
def load_all_data():
    # Load Incident Report
    df_incidents = pd.read_excel("IncidentReports_All_MTH_2026-06-25.xlsx", sheet_name="Sheet1")
    
    # Load Metrics Master File
    metrics_file = "EHSQ Metrics.xlsx"
    tcir_dart = pd.read_excel(metrics_file, sheet_name="TCIR and DART")
    housekeeping = pd.read_excel(metrics_file, sheet_name="Housekeeping", skiprows=1)
    capas = pd.read_excel(metrics_file, sheet_name="CAPAs", skiprows=1)
    
    return df_incidents, tcir_dart, housekeeping, capas

df, tcir_dart, housekeeping, capas = load_all_data()

# 3. Risk Mitigation Tracker (4-Box)
st.subheader("Risk Mitigation Tracker")
def map_risk(status):
    if status in ['Completed On Time', 'Completed Late']: return 'Completed'
    if status in ['In Draft', 'In Review']: return 'In Progress'
    if status == 'Resolved in Place': return 'Resolved in Place'
    return 'Need More Information'

df['Cat'] = df['Status'].apply(map_risk)
counts = df['Cat'].value_counts()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Completed", counts.get("Completed", 0))
c2.metric("In Progress", counts.get("In Progress", 0))
c3.metric("Resolved in Place", counts.get("Resolved in Place", 0))
c4.metric("Need Info", counts.get("Need More Information", 0))

st.divider()

# 4. Charts Section
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("TCIR & DART Trends")
    fig1 = px.line(tcir_dart, x='Month', y=['TCIR Actual', 'DART Actual'], markers=True)
    fig1.update_traces(texttemplate='%{y:.2f}', textposition='top center')
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("Housekeeping Performance")
    fig2 = px.line(housekeeping, x='Unnamed: 0', y='Average Plant Score', markers=True)
    fig2.update_traces(texttemplate='%{y:.2f}', textposition='top center')
    st.plotly_chart(fig2, use_container_width=True)

# 5. Raw Data Preview
st.divider()
st.subheader("Incident Details")
st.dataframe(df, use_container_width=True)
