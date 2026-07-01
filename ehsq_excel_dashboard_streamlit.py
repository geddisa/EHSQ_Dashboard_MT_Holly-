import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Dashboard Setup
st.set_page_config(layout="wide", page_title="MT. Holly | EHSQ KPI Dashboard")

try:
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        st.image("Company_Logo.png", width=200)
    with col_title:
        st.title("EHSQ KPI Dashboard")
except:
    st.title("EHSQ KPI Dashboard")

@st.cache_data
def load_all_data():
    incident_path = "IncidentReports_All_MTH_2026-06-25.xlsx"
    metrics_path = "EHSQ Metrics.xlsx"
    audit_path = "Audit Schedule - Internal - LPA.xlsx"
    
    try:
        return {
            "Incidents": pd.read_excel(incident_path, sheet_name="Sheet1"),
            "FSI": pd.read_excel(metrics_path, sheet_name="FSI Reports", skiprows=1),
            "CAPAs": pd.read_excel(metrics_path, sheet_name="CAPAs", skiprows=1),
            "Lead_Obs": pd.read_excel(audit_path, sheet_name="Safe Obs - Leadership"),
            "GS_Obs": pd.read_excel(audit_path, sheet_name="Safe Obs - GS and EHS"),
            "HSEQ_Obs": pd.read_excel(audit_path, sheet_name="Safe Obs GS EHS")
        }
    except Exception as e:
        st.error(f"Error loading files: {e}")
        return None

data = load_all_data()

if data:
    df_raw = data["Incidents"].copy()
    df_raw['Date'] = pd.to_datetime(df_raw['Date of Incident (UTC)'], errors='coerce')
    df_raw = df_raw.dropna(subset=['Date'])
    df_2026 = df_raw[df_raw['Date'].dt.year == 2026].copy()

    tabs = st.tabs(["Overview", "Compliance", "Housekeeping", "Safe Observations", "Risk Mitigation"])

    # --- TAB 0: OVERVIEW ---
    with tabs[0]: 
        st.subheader("Incident Breakdown")
        col1, col2 = st.columns(2)
        
        type_counts = df_2026.groupby('Type').size().reset_index(name='Count')
        fig = px.bar(type_counts, x='Type', y='Count', title="Incidents by Type", text='Count')
        fig.update_traces(texttemplate='%{text}', textposition='outside', textangle=0) 
        col1.plotly_chart(fig, use_container_width=True)
        
        dept_counts = df_2026.groupby(['Department', 'Type']).size().reset_index(name='Count')
        fig_dept = px.bar(dept_counts, x='Department', y='Count', color='Type', title="Incidents by Department", text='Count')
        fig_dept.update_traces(textangle=0, textposition='outside')
        col2.plotly_chart(fig_dept, use_container_width=True)
        
        st.divider()
        
        st.subheader("Incident Severity Analysis")
        df_severity = df_raw.copy()
        df_severity['Week'] = df_severity['Date'].dt.isocalendar().week
        
        severity_mapping = {
            'Property Damage': 25, 'Record Only - No Treatment': 50, 'First Aid': 75,
            'Molten Metal Spill > 25 lbs': 150, 'Molten Metal Explosion (Force 2 or 3)': 150,
            'Other Recordable Case': 250, 'Restricted or Transferred Work': 250,
            'Days Away From Work': 350, 'Recordable - Fatality': 600 
        }
        df_severity['Points'] = df_severity['Injury Classification'].map(severity_mapping).fillna(
            df_severity['Type'].map(severity_mapping)).fillna(0)

        weekly_scores = df_severity.groupby('Week')['Points'].sum().reset_index()
        current_week = pd.to_datetime('2026-06-09').isocalendar().week
        all_weeks = pd.DataFrame({'Week': range(1, current_week + 1)})
        weekly_scores = pd.merge(all_weeks, weekly_scores, on='Week', how='left').fillna(0)
        
        fig_severity = px.line(weekly_scores, x='Week', y='Points', title="Weekly Incident Severity Score", markers=True)
        st.plotly_chart(fig_severity, use_container_width=True)

    # --- TAB 1: COMPLIANCE ---
    with tabs[1]: 
        st.subheader("Compliance & Reporting Trends")
        c1, c2 = st.columns(2)
        fsi_df = data["FSI"]
        fig_fsi = px.line(fsi_df, x=fsi_df.columns[0], y=fsi_df.columns[4], title="FSI % On Time", markers=True)
        fig_fsi.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Target 100%")
        c1.plotly_chart(fig_fsi, use_container_width=True)
        
        capa_df = data["CAPAs"]
        fig_capa = px.line(capa_df, x=capa_df.columns[0], y=capa_df.columns[4], title="CAPA % On Time", markers=True)
        fig_capa.add_hline(y=0.8, line_dash="dash", line_color="red", annotation_text="Target 80%")
        c2.plotly_chart(fig_capa, use_container_width=True)

    # --- TAB 2: HOUSEKEEPING ---
    with tabs[2]: 
        st.subheader("Housekeeping Status")
        hk_data = df_2026.groupby(['Department', 'Status']).size().reset_index(name='Count')
        fig_hk = px.bar(hk_data, x='Department', y='Count', color='Status', barmode='group', text='Count')
        fig_hk.update_traces(texttemplate='%{text}', textposition='outside', textangle=0)
        st.plotly_chart(fig_hk, use_container_width=True)

    # --- TAB 3: SAFE OBSERVATIONS ---
    with tabs[3]: 
        st.subheader("Safe Observations Tracking")
        c1, c2, c3 = st.columns(3)
        c1.metric("Leadership Obs", len(data["Lead_Obs"]))
        c2.metric("GS Obs", len(data["GS_Obs"]))
        c3.metric("HSEQ_Obs", len(data["HSEQ_Obs"]))
        
    # --- TAB 4: RISK MITIGATION ---
    with tabs[4]: 
        st.subheader("Risk Mitigation Progress")
        total_risk = len(df_raw)
        completed = len(df_raw[df_raw['Status'].isin(['Completed On Time', 'Completed Late'])])
        in_progress = len(df_raw[df_raw['Status'].isin(['In Draft', 'In Review'])])
        need_info = max(0, total_risk - (completed + in_progress))
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Risk", total_risk)
        m2.metric("Completed", completed)
        m3.metric("In Progress", in_progress)
        m4.metric("Need More Info", need_info)
        
        st.divider()
        st.data_editor(df_raw, column_config={
            "Status": st.column_config.SelectboxColumn("Status", options=['Completed On Time', 'Completed Late', 'In Draft', 'In Review', 'Need Info'], required=True)
        }, hide_index=True, use_container_width=True)
