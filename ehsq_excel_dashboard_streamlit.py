import streamlit as st
import pandas as pd
import plotly.express as px

# --- DASHBOARD SETUP ---
st.set_page_config(layout="wide", page_title="EHSQ KPI Dashboard")

st.markdown("<h1 style='text-align: center;'>EHSQ KPI Dashboard</h1>", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_all_data():
    path_lpa = "Audit Schedule - Internal - LPA.xlsx"
    return {
        "Incidents": pd.read_excel("IncidentReports_All_MTH_2026-07-01.xlsx", sheet_name="Sheet1"),
        "FSI": pd.read_excel("EHSQ Metrics.xlsx", sheet_name="FSI Reports", skiprows=1),
        "CAPAs": pd.read_excel("EHSQ Metrics.xlsx", sheet_name="CAPAs", skiprows=1),
        "Lead_Obs": pd.read_excel(path_lpa, sheet_name="Safe Obs - Leadership", skiprows=2),
        "GS_Obs": pd.read_excel(path_lpa, sheet_name="Safe Obs - GS and EHS", skiprows=2),
        "HSEQ_Obs": pd.read_excel(path_lpa, sheet_name="Safe Obs GS EHS", skiprows=2)
    }

try:
    data = load_all_data()
except Exception as e:
    st.error(f"Error loading files: {e}")
    st.stop()

# --- PROCESSING ---
df_raw = data["Incidents"].copy()
df_raw['Date'] = pd.to_datetime(df_raw['Date of Incident (UTC)'], errors='coerce')
df_2026 = df_raw[df_raw['Date'].dt.year == 2026].copy()

# --- TABS ---
tabs = st.tabs(["Overview", "Compliance", "Housekeeping", "Safe Observations", "Risk Mitigation"])

with tabs[0]: 
    st.subheader("Incident Breakdown")
    col1, col2 = st.columns(2)
    # Ensure data exists before plotting
    if not df_2026.empty:
        type_counts = df_2026.groupby('Type').size().reset_index(name='Count')
        col1.plotly_chart(px.bar(type_counts, x='Type', y='Count', title="Incidents by Type", text='Count'), use_container_width=True)
        
        dept_counts = df_2026.groupby(['Department', 'Type']).size().reset_index(name='Count')
        col2.plotly_chart(px.bar(dept_counts, x='Department', y='Count', color='Type', title="Incidents by Department", text='Count'), use_container_width=True)

with tabs[1]: 
    st.subheader("Compliance & Reporting Trends")
    c1, c2 = st.columns(2)
    # Using iloc to dynamically grab columns based on your provided structure
    c1.plotly_chart(px.line(data["FSI"], x=data["FSI"].columns[0], y=data["FSI"].columns[4], title="FSI % On Time"), use_container_width=True)
    c2.plotly_chart(px.line(data["CAPAs"], x=data["CAPAs"].columns[0], y=data["CAPAs"].columns[4], title="CAPA % On Time"), use_container_width=True)

with tabs[2]: 
    st.subheader("Housekeeping Status")
    hk_data = df_2026.groupby(['Department', 'Status']).size().reset_index(name='Count')
    st.plotly_chart(px.bar(hk_data, x='Department', y='Count', color='Status', barmode='group'), use_container_width=True)

with tabs[3]: 
    st.subheader("Safe Observations Tracking")
    c1, c2, c3 = st.columns(3)
    c1.metric("Leadership Obs", 91)
    c2.metric("GS Obs", 177)
    c3.metric("HSEQ_Obs", 146)

    def prepare_trend_data(df, category):
        week_cols = [c for c in df.columns if 'Week' in str(c)]
        trend = df[week_cols].apply(pd.to_numeric, errors='coerce').sum().reset_index()
        trend.columns = ['Week', 'Count']
        trend['Category'] = category
        return trend

    df_trends = pd.concat([prepare_trend_data(data[key], name) for key, name in 
                           zip(["Lead_Obs", "GS_Obs", "HSEQ_Obs"], ["Leadership", "GS", "HSEQ"])])
    
    fig_obs = px.line(df_trends, x="Week", y="Count", color="Category", markers=True, title="Weekly Observation Trends")
    fig_obs.update_layout(hovermode="x unified")
    st.plotly_chart(fig_obs, use_container_width=True)

with tabs[4]: 
    st.subheader("Risk Mitigation Progress")
    cols_to_display = ["Incident", "Assigned To", "Status", "Type", "Department", "Due Date", "Description"]
    # Filter for non-empty status and display
    display_df = df_raw[cols_to_display].dropna(subset=["Status"])
    st.data_editor(display_df, hide_index=True, use_container_width=True, disabled=["Incident", "Type", "Department"])
