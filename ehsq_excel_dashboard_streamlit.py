import streamlit as st
import pandas as pd
import plotly.express as px

# Dashboard Setup
st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

@st.cache_data
def load_all_data():
    # Update these paths as needed
    metrics_path = "EHSQ Metrics.xlsx"
    incident_path = "IncidentReports_All_MTH_2026-06-25.xlsx"
    
    def clean_columns(df):
        df.columns = df.columns.astype(str).str.strip()
        return df

    return {
        "Incidents": clean_columns(pd.read_excel(incident_path, sheet_name="Sheet1")),
        "FSI": clean_columns(pd.read_excel(metrics_path, sheet_name="FSI Reports", skiprows=1)),
        "CAPAs": clean_columns(pd.read_excel(metrics_path, sheet_name="CAPAs", skiprows=1)),
        "Environmental": clean_columns(pd.read_excel(metrics_path, sheet_name="Environmental Compliance Issues", skiprows=1)),
        "TCIR": clean_columns(pd.read_excel(metrics_path, sheet_name="TCIR and DART", skiprows=1))
    }

data = load_all_data()
df = data["Incidents"]

# Define Tabs
tabs = st.tabs(["Overview", "Compliance", "Housekeeping", "Safe Observations", "Risk Mitigation"])

with tabs[0]: # Overview: Incidents by Type and Location
    st.subheader("Incident Breakdown")
    col1, col2 = st.columns(2)
    
    # Count by Type
    type_counts = df.groupby('Type').size().reset_index(name='Count')
    fig_type = px.bar(type_counts, x='Type', y='Count', title="Incidents by Type", text_auto=True)
    col1.plotly_chart(fig_type, use_container_width=True)
    
    # Categorization by Location
    loc_counts = df.groupby(['Location', 'Type']).size().reset_index(name='Count')
    fig_loc = px.bar(loc_counts, x='Location', y='Count', color='Type', title="Incidents by Location & Type", barmode='group')
    col2.plotly_chart(fig_loc, use_container_width=True)

with tabs[1]: # Compliance
    st.subheader("Compliance & Reporting Trends")
    col1, col2 = st.columns(2)
    df_fsi = data["FSI"]
    fig_fsi = px.line(df_fsi, x=df_fsi.columns[0], y=df_fsi.columns[4], title="FSI % On Time", markers=True)
    col1.plotly_chart(fig_fsi, use_container_width=True)
    
    df_capa = data["CAPAs"]
    fig_capa = px.line(df_capa, x=df_capa.columns[0], y=df_capa.columns[4], title="CAPA % On Time", markers=True)
    col2.plotly_chart(fig_capa, use_container_width=True)

with tabs[2]: # Housekeeping
    st.subheader("Housekeeping Status by Location")
    hk_data = df.groupby(['Location', 'Housekeeping_Status']).size().reset_index(name='Count')
    fig_hk = px.bar(hk_data, x='Location', y='Count', color='Housekeeping_Status', barmode='group', title="Housekeeping Status Tracking")
    st.plotly_chart(fig_hk, use_container_width=True)

with tabs[3]: # Safe Observations
    st.subheader("Safe Observations (Filtered)")
    df_obs = df[df["Category"] == "Observation"]
    
    c1, c2, c3 = st.columns(3)
    # Leadership
    c1.metric("Leadership Obs", len(df_obs[df_obs["Auditor_Group"] == "Leadership"]))
    # GS
    c2.metric("GS Obs", len(df_obs[df_obs["Auditor_Group"] == "GS"]))
    # HSEQ (excluding Maddi)
    hseq_obs = df_obs[(df_obs["Auditor_Group"] == "HSEQ") & (df_obs["Auditor_Name"] != "Maddi")]
    c3.metric("HSEQ Obs (Excl. Maddi)", len(hseq_obs))

with tabs[4]: # Risk Mitigation
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
    st.write("### Data Explorer")
    st.dataframe(df, use_container_width=True)
