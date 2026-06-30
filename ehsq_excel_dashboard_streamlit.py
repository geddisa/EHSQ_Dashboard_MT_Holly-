import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="EHSQ Performance Dashboard", layout="wide")

# Custom CSS to make containers look like "cards"
st.markdown("""
    <style>
    [data-testid="stMetric"] { background-color: #f0f2f6; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("EHSQ KPI Dashboard")

# 2. Load Data
@st.cache_data
def load_data():
    df = pd.read_excel('IncidentReports_All_MTH_2026-06-25.xlsx', sheet_name='Sheet1')
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# 3. KPI Summary Row (The "Card" Layout)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Incidents", len(df))
col2.metric("Open Risks", len(df[df['Status'] != 'Completed']))
col3.metric("Safe Observations", len(df[df['Type'] == 'Safe Observation']))
col4.metric("Housekeeping Items", len(df[df['Type'] == 'Housekeeping']))

st.divider()

# 4. Detailed Chart Grid
row1 = st.columns(2)

# Chart 1: Housekeeping
with row1[0]:
    st.subheader("Housekeeping by Location")
    hk_df = df[df['Type'] == 'Housekeeping']
    if not hk_df.empty:
        hk_data = hk_df.groupby(['Location', 'Status']).size().reset_index(name='Count')
        fig = px.bar(hk_data, x='Location', y='Count', color='Status', barmode='group')
        st.plotly_chart(fig, use_container_width=True)

# Chart 2: Risk Mitigation Status
with row1[1]:
    st.subheader("Risk Mitigation Distribution")
    fig = px.pie(df, names='Status', title="Current Risk Statuses")
    st.plotly_chart(fig, use_container_width=True)

# Chart 3: Incident Breakdown
st.subheader("Incident Breakdown by Type & Location")
fig_sun = px.sunburst(df, path=['Type', 'Location'], values=None) # Default count
st.plotly_chart(fig_sun, use_container_width=True)
