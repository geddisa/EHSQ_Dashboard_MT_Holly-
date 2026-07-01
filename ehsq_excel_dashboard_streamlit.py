import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# Dashboard Setup
st.set_page_config(layout="wide", page_title="Century Aluminum | Mt. Holly | EHSQ KPI Dashboard")
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
    # --- DATA PROCESSING ---
    df_raw = data["Incidents"].copy()
    df_raw['Date'] = pd.to_datetime(df_raw['Date of Incident (UTC)'], errors='coerce')
    df_raw = df_raw.dropna(subset=['Date'])
    
    df_2026 = df_raw[df_raw['Date'].dt.year == 2026].copy()

    # Tabs definition
    tabs = st.tabs(["Overview", "Compliance", "Housekeeping", "Safe Observations", "Risk Mitigation"])

    with tabs[0]: 
        st.subheader("Incident Breakdown")
        col1, col2 = st.columns(2)
        
        type_counts = df_2026.groupby('Type').size().reset_index(name='Count')
        
        # Create the bar chart with text enabled
        fig = px.bar(type_counts, x='Type', y='Count', title="Incidents by Type", text='Count')
        
        # Setting textangle to 0 makes all labels stand up (horizontal)
        fig.update_traces(texttemplate='%{text}', textposition='outside', textangle=0) 
        
        col1.plotly_chart(fig, width='stretch')
        dept_counts = df_2026.groupby(['Department', 'Type']).size().reset_index(name='Count')
        fig_dept = px.bar(dept_counts, x='Department', y='Count', color='Type', title="Incidents by Department", text='Count')
        fig_dept.update_traces(textangle=0, textposition='outside')
        st.plotly_chart(fig_dept, width='stretch')

    with tabs[1]: 
        st.subheader("Compliance & Reporting Trends")
        c1, c2 = st.columns(2)
        
        fsi_df = data["FSI"]
        fig_fsi = px.line(fsi_df, x=fsi_df.columns[0], y=fsi_df.columns[4], title="FSI % On Time", markers=True)
        fig_fsi.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Target 100%")
        c1.plotly_chart(fig_fsi, width='stretch')
        
        capa_df = data["CAPAs"]
        fig_capa = px.line(capa_df, x=capa_df.columns[0], y=capa_df.columns[4], title="CAPA % On Time", markers=True)
        fig_capa.add_hline(y=0.8, line_dash="dash", line_color="red", annotation_text="Target 80%")
        c2.plotly_chart(fig_capa, width='stretch')
        

    with tabs[2]: 
        st.subheader("Housekeeping Status")
        hk_data = df_2026.groupby(['Department', 'Status']).size().reset_index(name='Count')
        st.plotly_chart(px.bar(hk_data, x='Department', y='Count', color='Status', barmode='group', text_auto='.0f'), width='stretch')

    with tabs[3]: 
        st.subheader("Safe Observations Tracking")
        c1, c2, c3 = st.columns(3)
        c1.metric("Leadership Obs", len(data["Lead_Obs"]))
        c2.metric("GS Obs", len(data["GS_Obs"]))
        c3.metric("HSEQ_Obs", len(data["HSEQ_Obs"]))
        
        st.divider()
        st.subheader("Incident Severity Analysis")
        
        # Pulling directly from df_raw (which is loaded from IncidentReports_All_MTH_2026-06-25.xlsx)
        df_severity = df_raw.copy()
        
        # Ensure we are working with the Date column correctly
        df_severity['Week'] = df_severity['Date'].dt.isocalendar().week
        
        severity_mapping = {
            'Property Damage': 25, 
            'Record Only - No Treatment': 50, 
            'First Aid': 75,
            'Molten Metal Spill > 25 lbs': 150, 
            'Molten Metal Explosion (Force 2 or 3)': 150,
            'Other Recordable Case': 250, 
            'Restricted or Transferred Work': 250,
            'Days Away From Work': 350, 
            'Recordable - Fatality': 600 
        }

        # Mapping classification to points
        df_severity['Points'] = df_severity['Injury Classification'].map(severity_mapping).fillna(
            df_severity['Type'].map(severity_mapping)).fillna(0)

        # Grouping by Week
        weekly_scores = df_severity.groupby('Week')['Points'].sum()
        
        # Dynamic week calculation based on the current date
        current_week = pd.to_datetime('2026-06-09').isocalendar().week
        weekly_scores = weekly_scores.reindex(range(1, current_week + 1), fill_value=0)

        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Define Zones
        ax.axhspan(0, 400, color='lightgreen', alpha=0.4, label='Low Risk (Green: 0-400)')
        ax.axhspan(400, 800, color='khaki', alpha=0.4, label='Medium Risk (Yellow: 401-800)')
        ax.axhspan(800, 1250, color='lightcoral', alpha=0.4, label='High Risk (Red: 800+)')
        
        # Plot data
        ax.plot(weekly_scores.index, weekly_scores.values, color='black', linewidth=2.5, marker='o', label='Weekly Total')
        
        ax.set_title('Incident Severity Graph')
        ax.set_xlabel('Calendar Week Number')
        ax.set_ylabel('Points')
        ax.set_xticks(range(1, current_week + 1))
        
        # Add Legend to confirm color meanings
        ax.legend(loc='upper left', frameon=True)
        
        st.pyplot(fig)
        
    with tabs[4]: 
        st.subheader("Risk Mitigation Progress")
        total_risk = len(df_raw)
        completed = len(df_raw[df_raw['Status'].isin(['Completed On Time', 'Completed Late'])])
        in_progress = len(df_raw[df_raw['Status'].isin(['In Draft', 'In Review'])])
        need_info = max(0, total_risk - (completed + in_progress))
        
        def colored_metric(label, value, color):
            st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 10px; border-radius: 10px; border-left: 5px solid {color}; text-align: center;">
                    <h4 style="margin: 0; color: #555;">{label}</h4>
                    <h2 style="margin: 0; color: {color};">{value}</h2>
                </div>
            """, unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        with m1: colored_metric("Total Risk", total_risk, "blue")
        with m2: colored_metric("Completed", completed, "green")
        with m3: colored_metric("In Progress", in_progress, "orange")
        with m4: colored_metric("Need More Info", need_info, "red")
        
        st.divider()
        st.data_editor(df_raw, column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status", options=['Completed On Time', 'Completed Late', 'In Draft', 'In Review', 'Need Info'], required=True
            )
        }, hide_index=True, width='stretch')
