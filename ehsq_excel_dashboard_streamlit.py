import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Setup
st.set_page_config(page_title="EHSQ Performance Dashboard", layout="wide")
st.title("EHSQ Performance Dashboard")

# 2. Data Loading
@st.cache_data
def load_data():
    df = pd.read_excel("IncidentReports_All_MTH_2026-06-25.xlsx")
    metrics = pd.read_excel("EHSQ Metrics.xlsx", sheet_name="TCIR and DART")
    return df, metrics

df, metrics = load_data()

# 3. Top Level KPIs
c1, c2, c3 = st.columns(3)
c1.metric("Total Incidents", len(df))
c2.metric("Severe Incidents", len(df[df['Risk Level'] == 'High']))
c3.metric("Total Recordables", len(df[df['Injury Classification'] != 'No Data']))

st.divider()

# 4. Risk Mitigation Tracker
st.subheader("Risk Mitigation Tracker")
def map_risk(status):
    if status in ['Completed On Time', 'Completed Late']: return 'Completed'
    if status in ['In Draft', 'In Review']: return 'In Progress'
    if status == 'Resolved in Place': return 'Resolved in Place'
    return 'Need More Information'

df['Cat'] = df['Status'].apply(map_risk)
counts = df['Cat'].value_counts()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Completed", counts.get("Completed", 0))
col2.metric("In Progress", counts.get("In Progress", 0))
col3.metric("Resolved in Place", counts.get("Resolved in Place", 0))
col4.metric("Need Info", counts.get("Need More Information", 0))

st.divider()

# 5. Charts with Data Labels
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Incidents by Department")
    fig1 = px.bar(df['Department'].value_counts().reset_index(), 
                  x='Department', y='count', text_auto=True)
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader("Incidents by Hazard Type")
    fig2 = px.bar(df['Hazard Type'].value_counts().reset_index(), 
                  x='Hazard Type', y='count', text_auto=True)
    st.plotly_chart(fig2, use_container_width=True)

# 6. TCIR & DART Trend
st.subheader("TCIR & DART Performance")
fig3 = px.line(metrics, x='Month', y=['TCIR Actual', 'DART Actual'], 
               markers=True, text='TCIR Actual')
st.plotly_chart(fig3, use_container_width=True)

# 7. Raw Data
st.subheader("Incident Details")
st.dataframe(df, use_container_width=True)
