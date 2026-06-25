import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("EHSQ Performance Dashboard")

# Load your data
@st.cache_data
def load_data():
    df = pd.read_excel("IncidentReports_All_MTH_2026-06-25.xlsx")
    return df

df = load_data()

# --- 1. Top Level Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Incidents", len(df))
col2.metric("Severe Incidents", len(df[df['Risk Level'] == 'High'])) # Adjust column/filter as needed
col3.metric("Total Recordables", len(df[df['Injury Classification'] != 'No Data']))

# --- 2. Risk Mitigation Tracker (The 4-Box requirement) ---
st.subheader("Risk Mitigation Tracker")
def map_risk_status(status):
    if status in ['Completed On Time', 'Completed Late']: return 'Completed'
    if status in ['In Draft', 'In Review']: return 'In Progress'
    if status == 'Resolved in Place': return 'Resolved in Place'
    return 'Need More Information'

df['Mitigation_Cat'] = df['Status'].apply(map_risk_status)
risk_counts = df['Mitigation_Cat'].value_counts()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Completed", risk_counts.get("Completed", 0))
c2.metric("In Progress", risk_counts.get("In Progress", 0))
c3.metric("Resolved in Place", risk_counts.get("Resolved in Place", 0))
c4.metric("Need More Information", risk_counts.get("Need More Information", 0))

# --- 3. Charts Based on PDF Requirements ---
st.divider()
c_left, c_right = st.columns(2)

with c_left:
    st.subheader("Incidents by Department")
    dept_chart = px.bar(df['Department'].value_counts(), orientation='h')
    st.plotly_chart(dept_chart, use_container_width=True)

with c_right:
    st.subheader("Incidents by Hazard Type")
    hazard_chart = px.bar(df['Hazard Type'].value_counts())
    st.plotly_chart(hazard_chart, use_container_width=True)

# --- 4. Raw Data View ---
st.subheader("Incident Details")
st.dataframe(df[['Incident', 'Status', 'Department', 'Hazard Type', 'Description']], use_container_width=True)
