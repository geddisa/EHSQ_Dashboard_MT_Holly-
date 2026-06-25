import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EHSQ Dashboard", layout="wide")
st.title("EHSQ Performance Dashboard")

# --- Load Data from Excel ---
@st.cache_data
def load_data():
    # Load the incident report
    incidents = pd.read_excel("IncidentReports_All_MTH_2026-06-25.xlsx", sheet_name="Sheet1")
    
    # Load all metrics from the master metrics file
    # Ensure all tabs (CAPAs, Housekeeping, etc.) are in this file
    xls = pd.ExcelFile("EHSQ Metrics.xlsx")
    metrics = {sheet: pd.read_excel(xls, sheet_name=sheet) for sheet in xls.sheet_names}
    
    return incidents, metrics

df_incidents, data_metrics = load_data()

# --- Risk Mitigation Tracker (4-Box) ---
st.subheader("Risk Mitigation Tracker")
def map_status(status):
    if status in ['Completed On Time', 'Completed Late']: return 'Completed'
    if status in ['In Draft', 'In Review']: return 'In Progress'
    if status == 'Resolved in Place': return 'Resolved in Place'
    return 'Need More Information'

df_incidents['Cat'] = df_incidents['Status'].apply(map_status)
counts = df_incidents['Cat'].value_counts()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Completed", counts.get("Completed", 0))
c2.metric("In Progress", counts.get("In Progress", 0))
c3.metric("Resolved in Place", counts.get("Resolved in Place", 0))
c4.metric("Need Info", counts.get("Need More Information", 0))

# --- Charts (Using Excel Data) ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("TCIR & DART Trends")
    tcir_data = data_metrics.get("TCIR and DART")
    if tcir_data is not None:
        fig = px.line(tcir_data, x='Month', y=['TCIR Actual', 'DART Actual'], 
                      markers=True, text_auto='.2f')
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Housekeeping Scores")
    house = data_metrics.get("Housekeeping")
    if house is not None:
        fig2 = px.line(house, x='Unnamed: 0', y='Average Plant Score', 
                       markers=True, text_auto='.2f')
        st.plotly_chart(fig2, use_container_width=True)
