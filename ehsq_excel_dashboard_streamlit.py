import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Dashboard Setup
st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

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
    # Corrected: Targeting the specific column name from your Excel file
    df_raw['Date'] = pd.to_datetime(df_raw['Date of Incident (UTC)'], errors='coerce')
    df_raw = df_raw.dropna(subset=['Date'])
    
    # Filter for 2026 for charts
    df_2026 = df_raw[df_raw['Date'].dt.year == 2026].copy()

    tabs = st.tabs(["Overview", "Compliance", "Housekeeping", "Safe Observations", "Risk Mitigation"])

    with tabs[0]: 
        st.subheader("Incident Breakdown")
        col1, col2 = st.columns(2)
        type_counts = df_2026.groupby('Type').size().reset_index(name='Count')
        # Added text_auto='.0f' for data labels
        col1.plotly_chart(px.bar(type_counts, x='Type', y='Count', title="2026 Incidents by Type", text_auto='.0f'), width='stretch')
        
        dept_counts = df_2026.groupby(['Department', 'Type']).size().reset_index(name='Count')
        # Added text_auto='.0f' for data labels
        fig_dept = px.bar(dept_counts, x='Department', y='Count', color='Type', title="2026 Incidents by Department", text_auto='.0f')
        st.plotly_chart(fig_dept, width='stretch')

    with tabs[1]: 
        st.subheader("Compliance & Reporting Trends")
        c1, c2 = st.columns(2)
        
        fsi_df = data["FSI"]
        # Added .add_hline for target line (1.0 = 100%)
        fig_fsi = px.line(fsi_df, x=fsi_df.columns[0], y=fsi_df.columns[4], title="FSI % On Time", markers=True)
        fig_fsi.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Target 100%")
        c1.plotly_chart(fig_fsi, width='stretch')
        
        capa_df = data["CAPAs"]
        # Added .add_hline for target line (0.8 = 80%)
        fig_capa = px.line(capa_df, x=capa_df.columns[0], y=capa_df.columns[4], title="CAPA % On Time", markers=True)
        fig_capa.add_hline(y=0.8, line_dash="dash", line_color="red", annotation_text="Target 80%")
        c2.plotly_chart(fig_capa, width='stretch')

    with tabs[2]: 
        st.subheader("2026 Housekeeping Status")
        hk_data = df_2026.groupby(['Department', 'Status']).size().reset_index(name='Count')
        st.plotly_chart(px.bar(hk_data, x='Department', y='Count', color='Status', barmode='group'), width='stretch')

    with tabs[3]: 
        st.subheader("Safe Observations Tracking")
        c1, c2, c3 = st.columns(3)
        c1.metric("Leadership Obs", len(data["Lead_Obs"]))
        c2.metric("GS Obs", len(data["GS_Obs"]))
        c3.metric("HSEQ Obs", len(data["HSEQ_Obs"]))

    with tabs[4]: 
        st.subheader("Risk Mitigation Progress")
        
        # Calculated from df_raw (All Time)
        total_risk = len(df_raw)
        completed = len(df_raw[df_raw['Status'].isin(['Completed On Time', 'Completed Late'])])
        in_progress = len(df_raw[df_raw['Status'].isin(['In Draft', 'In Review'])])
        need_info = max(0, total_risk - (completed + in_progress))
        
        # Custom function to apply colors
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
        with m3: colored_metric("In Progress", in_progress, "orange") # Using orange for visibility as yellow can be hard to read
        with m4: colored_metric("Need More Info", need_info, "red")
        
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
            width='stretch'
        )
