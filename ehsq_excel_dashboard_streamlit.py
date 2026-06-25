import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

# 1. Load Data
@st.cache_data
def load_data():
    # Load your Incident Data
    df = pd.read_excel("IncidentReports_All_MTH_2026-06-25.xlsx", sheet_name="Sheet1")
    
    # Load Metrics with skiprows to ignore the title/extra rows in the Excel file
    metrics_file = "EHSQ Metrics.xlsx"
    tcir = pd.read_excel(metrics_file, sheet_name="TCIR and DART", header=1)
    house = pd.read_excel(metrics_file, sheet_name="Housekeeping", skiprows=2)
    capa = pd.read_excel(metrics_file, sheet_name="CAPAs", skiprows=2)
    
    return df, tcir, house, capa

df, tcir_df, house_df, capa_df = load_data()

# 2. Risk Mitigation Tracker (Using Incident Data)
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

# 3. Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("TCIR & DART Trends")
    fig1 = px.line(tcir_df, x='Month', y=['TCIR Actual', 'DART Actual'], markers=True)
    fig1.update_traces(texttemplate='%{y:.2f}', textposition='top center')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Housekeeping Scores")
    fig2 = px.line(house_df, x='Unnamed: 0', y='Average Plant Score', markers=True)
    fig2.update_traces(texttemplate='%{y:.2f}', textposition='top center')
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.subheader("Incident Details")
st.dataframe(df, use_container_width=True)
