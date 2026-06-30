import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="EHSQ Performance Dashboard", layout="wide")
st.title("EHSQ Performance Dashboard - Mt. Holly")

# 2. Data Loading
@st.cache_data
def load_data():
    file_path = 'IncidentReports_All_MTH_2026-06-25.xlsx'
    df = pd.read_excel(file_path, sheet_name='Sheet1')
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# 3. Layout: Three-column dashboard
row1 = st.columns(2)
row2 = st.columns(2)

# --- SECTION: Housekeeping ---
with row1[0]:
    st.subheader("Housekeeping Status")
    hk_df = df[df['Type'] == 'Housekeeping']
    if not hk_df.empty:
        hk_data = hk_df.groupby(['Location', 'Status']).size().reset_index(name='Count')
        fig = px.bar(hk_data, x='Status', y='Count', color='Location', title="Housekeeping by Location")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No housekeeping data available.")

# --- SECTION: Risk Mitigation ---
with row1[1]:
    st.subheader("Risk Mitigation Status")
    risk_data = df['Status'].value_counts().reset_index()
    risk_data.columns = ['Status', 'Count']
    fig = px.pie(risk_data, values='Count', names='Status', title="Risk Distribution")
    st.plotly_chart(fig, use_container_width=True)

# --- SECTION: Incident Breakdown ---
with row2[0]:
    st.subheader("Incident Breakdown")
    incident_counts = df.groupby(['Type', 'Location']).size().reset_index(name='Count')
    fig = px.sunburst(incident_counts, path=['Type', 'Location'], values='Count')
    st.plotly_chart(fig, use_container_width=True)

# --- SECTION: Safe Observations ---
with row2[1]:
    st.subheader("Safe Observations")
    # Dynamically show charts for the requested groups
    groups = ['Leadership', 'GS', 'HSEQ']
    for group in groups:
        group_df = df[df['Reported By'].str.contains(group, na=False)]
        if not group_df.empty:
            st.write(f"**{group}**")
            st.bar_chart(group_df['Status'].value_counts())
