import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Dashboard Setup
st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

@st.cache_data
def load_all_data():
    # Load your actual data files
    incident_path = "IncidentReports_All_MTH_2026-06-25.xlsx - Sheet1.csv"
    # Ensure other files (Metrics, Audit) are in the same directory
    try:
        return {
            "Incidents": pd.read_csv(incident_path),
            "FSI": pd.read_excel("EHSQ Metrics.xlsx", sheet_name="FSI Reports", skiprows=1),
            "CAPAs": pd.read_excel("EHSQ Metrics.xlsx", sheet_name="CAPAs", skiprows=1),
            "Lead_Obs": pd.read_excel("Audit Schedule - Internal - LPA.xlsx", sheet_name="Safe Obs - Leadership"),
            "GS_Obs": pd.read_excel("Audit Schedule - Internal - LPA.xlsx", sheet_name="Safe Obs - GS and EHS"),
            "HSEQ_Obs": pd.read_excel("Audit Schedule - Internal - LPA.xlsx", sheet_name="Safe Obs GS EHS")
        }
    except Exception as e:
        st.error(f"Error loading files: {e}")
        return None

data = load_all_data()

if data:
    # --- DATA PROCESSING ---
    df_raw = data["Incidents"].copy()
    # Correct column name based on your file
    df_raw['Date'] = pd.to_datetime(df_raw['Date of Incident (UTC)'], errors='coerce')
    df_raw = df_raw.dropna(subset=['Date'])
    
    # Filter for 2026 for charts
    df_2026 = df_raw[df_raw['Date'].dt.year == 2026].copy()

    tabs = st.tabs(["Overview", "Compliance", "Housekeeping", "Safe Observations", "Risk Mitigation"])

    with tabs[0]: 
        st.subheader("2026 Incident Breakdown")
        col1, col2 = st.columns(2)
        type_counts = df_2026.groupby('Type').size().reset_index(name='Count')
        col1.plotly_chart(px.bar(type_counts, x='Type', y='Count', title="2026 Incidents by Type"), use_container_width=True)
        
        dept_counts = df_2026.groupby(['Department', 'Type']).size().reset_index(name='Count')
        fig_dept = px.bar(dept_counts, x='Department', y='Count', color='Type', title="2026 Incidents by Department")
        st.plotly_chart(fig_dept, use_container_width=True)

    with tabs[1]: 
        st.subheader("Compliance & Reporting Trends")
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.line(data["FSI"], title="FSI % On Time"), use_container_width=True)
        c2.plotly_chart(px.line(data["CAPAs"], title="CAPA % On Time"), use_container_width=True)

    with tabs[2]: 
        st.subheader("2026 Housekeeping Status")
        hk_data = df_2026.groupby(['Department', 'Status']).size().reset_index(name='Count')
        st.plotly_chart(px.bar(hk_data, x='Department', y='Count', color='Status', barmode='group'), use_container_width=True)

    with tabs[3]: 
        st.subheader("Safe Observations Tracking")
        c1, c2, c3 = st.columns(3)
        c1.metric("Leadership Obs", len(data["Lead_Obs"]))
        c2.metric("GS Obs", len(data["GS_Obs"]))
        c3.metric("HSEQ Obs", len(data["HSEQ_Obs"]))

    with tabs[4]: 
        st.subheader("Risk Mitigation Progress (All Data)")
        # Calculations use df_raw (All Time)
        total_risk = len(df_raw)
        completed = len(df_raw[df_raw['Status'].isin(['Completed On Time', 'Completed Late'])])
        in_progress = len(df_raw[df_raw['Status'].isin(['In Draft', 'In Review'])])
        need_info = max(0, total_risk - (completed + in_progress))
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Risk (All)", total_risk)
        m2.metric("Completed", completed)
        m3.metric("In Progress", in_progress)
        m4.metric("Need More Info", need_info)
        
        st.divider()
        st.data_editor(
            df_raw, 
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status", 
                    options=['Completed On Time', 'Completed Late', 'In Draft', 'In Review', 'Need Info'], 
                    required=True
                )
            }, 
            hide_index=True, 
            use_container_width=True
        )
