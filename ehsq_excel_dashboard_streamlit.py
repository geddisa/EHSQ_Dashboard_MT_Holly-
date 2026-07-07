import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 

# --- DASHBOARD SETUP ---
st.set_page_config(layout="wide", page_title="MT. Holly | EHSQ KPI Dashboard")

col_logo, col_title = st.columns([1, 6], vertical_alignment="center")
with col_logo:
    try:
        st.image("Company_Logo.png", width=200)
    except:
        st.write("Logo missing")
with col_title:
    st.markdown("<h1 style='margin-bottom: 0; padding-top: 0;'>EHSQ KPI Dashboard</h1>", unsafe_allow_html=True)

# --- DATA LOADING ---
def load_all_data():
    # Adjusted skiprows based on your file structure
    path_lpa = "Audit Schedule - Internal - LPA.xlsx"
    data = {
        "Incidents": pd.read_excel("IncidentReports_All_MTH_2026-07-01.xlsx", sheet_name="Sheet1"),
        "FSI": pd.read_excel("EHSQ Metrics.xlsx", sheet_name="FSI Reports", skiprows=1),
        "CAPAs": pd.read_excel("EHSQ Metrics.xlsx", sheet_name="CAPAs", skiprows=1),
        "Lead_Obs": pd.read_excel(path_lpa, sheet_name="Safe Obs - Leadership", skiprows=2),
        "GS_Obs": pd.read_excel(path_lpa, sheet_name="Safe Obs - GS and EHS", skiprows=2),
        "HSEQ_Obs": pd.read_excel(path_lpa, sheet_name="Safe Obs GS EHS", skiprows=2)
    }
    return data

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
    type_counts = df_2026.groupby('Type').size().reset_index(name='Count')
    fig = px.bar(type_counts, x='Type', y='Count', title="Incidents by Type", text='Count')
    col1.plotly_chart(fig, use_container_width=True)
    
    dept_counts = df_2026.groupby(['Department', 'Type']).size().reset_index(name='Count')
    fig_dept = px.bar(dept_counts, x='Department', y='Count', color='Type', title="Incidents by Department", text='Count')
    col2.plotly_chart(fig_dept, use_container_width=True)

with tabs[1]: 
    st.subheader("Compliance & Reporting Trends")
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.line(data["FSI"], x=data["FSI"].columns[0], y=data["FSI"].columns[4], title="FSI % On Time"), use_container_width=True)
    c2.plotly_chart(px.line(data["CAPAs"], x=data["CAPAs"].columns[0], y=data["CAPAs"].columns[4], title="CAPA % On Time"), use_container_width=True)

with tabs[2]: 
    st.subheader("Housekeeping Status")
    hk_data = df_2026.groupby(['Department', 'Status']).size().reset_index(name='Count')
    st.plotly_chart(px.bar(hk_data, x='Department', y='Count', color='Status', barmode='group'), use_container_width=True)

with tabs[3]: 
    st.subheader("Safe Observations Tracking")
    
    def get_weekly_trend(df, category):
        # Dynamically find columns that contain the word 'Week'
        week_cols = [c for c in df.columns if 'Week' in str(c)]
        # Sum numeric values in these columns
        trend = df[week_cols].apply(pd.to_numeric, errors='coerce').sum().reset_index()
        trend.columns = ['Week', 'Count']
        trend['Category'] = category
        return trend

    df_trends = pd.concat([
        get_weekly_trend(data["Lead_Obs"], "Leadership"),
        get_weekly_trend(data["GS_Obs"], "GS"),
        get_weekly_trend(data["HSEQ_Obs"], "HSEQ")
    ])

    c1, c2, c3 = st.columns(3)
    c1.metric("Leadership Obs", 91)
    c2.metric("GS Obs", 177)
    c3.metric("HSEQ_Obs", 146)
    
    fig_obs = px.line(df_trends, x="Week", y="Count", color="Category", markers=True, title="Weekly Trends (All Weeks)")
    st.plotly_chart(fig_obs, use_container_width=True)

with tabs[4]: 
    st.subheader("Risk Mitigation Progress")
    cols_to_display = ["Incident", "Assigned To", "Status", "Type", "Department", "Due Date", "Description"]
    st.data_editor(df_raw[cols_to_display].dropna(subset=["Status"]), hide_index=True, use_container_width=True)
