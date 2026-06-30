import streamlit as st
import pandas as pd
import plotly.express as px

# Dashboard Setup
st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

@st.cache_data
def load_all_data():
    metrics_path = "EHSQ Metrics.xlsx"
    incident_path = "IncidentReports_All_MTH_2026-06-25.xlsx"
    audit_path = "Audit Schedule - Internal - LPA.xlsx"
    
    def clean_columns(df):
        df.columns = df.columns.astype(str).str.strip()
        return df

    try:
        return {
            "Incidents": clean_columns(pd.read_excel(incident_path, sheet_name="Sheet1")),
            "FSI": clean_columns(pd.read_excel(metrics_path, sheet_name="FSI Reports", skiprows=1)),
            "CAPAs": clean_columns(pd.read_excel(metrics_path, sheet_name="CAPAs", skiprows=1)),
            "TCIR": clean_columns(pd.read_excel(metrics_path, sheet_name="TCIR and DART", skiprows=1)),
            "Lead_Obs": clean_columns(pd.read_excel(audit_path, sheet_name="Safe Obs - Leadership")),
            "GS_Obs": clean_columns(pd.read_excel(audit_path, sheet_name="Safe Obs - GS and EHS")),
            "HSEQ_Obs": clean_columns(pd.read_excel(audit_path, sheet_name="Safe Obs GS EHS"))
        }
    except Exception as e:
        st.error(f"Error loading files: {e}")
        return None

data = load_all_data()

if data:
    df = data["Incidents"]
    tabs = st.tabs(["Overview", "Compliance", "Housekeeping", "Safe Observations", "Risk Mitigation"])

    with tabs[0]: 
        st.subheader("Incident Breakdown")
        col1, col2 = st.columns(2)
        type_counts = df.groupby('Type').size().reset_index(name='Count')
        fig_type = px.bar(type_counts, x='Type', y='Count', title="Incidents by Type", text_auto='.0f')
        col1.plotly_chart(fig_type, use_container_width=True)
        
        dept_counts = df.groupby(['Department', 'Type']).size().reset_index(name='Count')
        fig_dept = px.bar(dept_counts, x='Department', y='Count', color='Type', 
                         title="Incidents by Department & Type", barmode='group', text_auto='.0f', height=600)
        fig_dept.update_layout(xaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig_dept, use_container_width=True)

    with tabs[1]: 
        st.subheader("Compliance & Reporting Trends")
        col1, col2 = st.columns(2)
        
        # FSI Plot with 100% Target Line
        df_fsi = data["FSI"].dropna(subset=[data["FSI"].columns[4]])
        fig_fsi = px.line(df_fsi, x=df_fsi.columns[0], y=df_fsi.columns[4], title="FSI % On Time", markers=True)
        fig_fsi.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Target (100%)")
        col1.plotly_chart(fig_fsi, use_container_width=True)
        
        # CAPA Plot with 80% Target Line
        df_capa = data["CAPAs"].dropna(subset=[data["CAPAs"].columns[4]])
        fig_capa = px.line(df_capa, x=df_capa.columns[0], y=df_capa.columns[4], title="CAPA % On Time", markers=True)
        fig_capa.add_hline(y=0.8, line_dash="dash", line_color="red", annotation_text="Target (80%)")
        col2.plotly_chart(fig_capa, use_container_width=True)

    with tabs[2]: 
        st.subheader("Housekeeping Status by Department")
        hk_data = df.groupby(['Department', 'Status']).size().reset_index(name='Count')
        fig_hk = px.bar(hk_data, x='Department', y='Count', color='Status', barmode='group', title="Status Tracking", text_auto='.0f')
        st.plotly_chart(fig_hk, use_container_width=True)

    with tabs[3]: 
        st.subheader("Safe Observations Tracking")
        c1, c2, c3 = st.columns(3)
        c1.metric("Leadership Obs", len(data["Lead_Obs"]))
        c2.metric("GS Obs", len(data["GS_Obs"]))
        
        hseq_df = data["HSEQ_Obs"]
        hseq_filtered = hseq_df[hseq_df['Auditor_Name'] != 'Maddi'] if 'Auditor_Name' in hseq_df.columns else hseq_df
        c3.metric("HSEQ Obs (Excl. Maddi)", len(hseq_filtered))

    with tabs[4]: 
        st.subheader("Risk Mitigation Progress")
        total_risk = len(df)
        completed = len(df[df['Status'].isin(['Completed On Time', 'Completed Late'])])
        in_progress = len(df[df['Status'].isin(['In Draft', 'In Review'])])
        need_info = total_risk - (completed + in_progress)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Risk Identified", total_risk)
        m2.metric("Completed", completed)
        m3.metric("In Progress", in_progress)
        m4.metric("Need More Info", max(0, need_info))
        st.divider()
        st.dataframe(df, use_container_width=True)
