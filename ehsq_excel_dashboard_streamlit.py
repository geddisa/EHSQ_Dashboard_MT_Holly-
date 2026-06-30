import streamlit as st
import pandas as pd
import plotly.express as px

# Dashboard Setup
st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

# Load and clean data
@st.cache_data
def load_all_data():
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
        "TCIR": clean_columns(pd.read_excel(metrics_path, sheet_name="TCIR and DART", skiprows=1)),
        "Severity": clean_columns(pd.read_excel(metrics_path, sheet_name="Overall Severity Ratings", skiprows=0))
    }

data = load_all_data()

# Categorization logic for Risk Mitigation
def map_risk(status):
    status = str(status).strip()
    if status in ['Completed On Time', 'Completed Late']: return 'Completed'
    if status in ['In Draft', 'In Review']: return 'In Progress'
    if status == 'Resolved in Place': return 'Resolved in Place'
    return 'Need More Information'

# Define Tabs
tabs = st.tabs(["Overview", "Compliance & Reporting", "Performance Trends", "Risk Mitigation", "Data Explorer"])

with tabs[0]:
    st.subheader("Executive Summary")
    st.metric("Total Incidents Logged", len(data["Incidents"]))
    
    st.write("### Environmental Compliance Issues")
    df_env = data["Environmental"]
    fig_env = px.bar(df_env.dropna(subset=[df_env.columns[1]]), 
                     x=df_env.columns[0], y=df_env.columns[1], title="Issues by Month")
    fig_env.update_traces(texttemplate='%{y:.0f}', textposition='outside')
    st.plotly_chart(fig_env, use_container_width=True)

with tabs[1]:
    st.subheader("Compliance & Reporting Trends")
    col1, col2 = st.columns(2)
    
    df_fsi = data["FSI"]
    fig_fsi = px.line(df_fsi, x=df_fsi.columns[0], y=df_fsi.columns[4], title="FSI % On Time", markers=True)
    fig_fsi.update_traces(texttemplate='%{y:.2f}', textposition='top center')
    col1.plotly_chart(fig_fsi, use_container_width=True)
    
    df_capa = data["CAPAs"]
    fig_capa = px.line(df_capa, x=df_capa.columns[0], y=df_capa.columns[4], title="CAPA % On Time", markers=True)
    fig_capa.update_traces(texttemplate='%{y:.2f}', textposition='top center')
    col2.plotly_chart(fig_capa, use_container_width=True)

with tabs[2]:
    st.subheader("Performance Trends (TCIR & DART)")
    df_tcir = data["TCIR"]
    fig_perf = px.line(df_tcir, x="Month", y=["TCIR Actual", "DART Actual"], markers=True, title="Safety Performance Trend")
    fig_perf.update_traces(texttemplate='%{y:.2f}', textposition='top center')
    st.plotly_chart(fig_perf, use_container_width=True)

with tabs[3]:
    st.subheader("Risk Mitigation Tracker")
    df_incidents = data["Incidents"].copy()
    df_incidents['Cat'] = df_incidents['Status'].apply(map_risk)
    counts = df_incidents['Cat'].value_counts()
    
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Completed", int(counts.get("Completed", 0)))
    b2.metric("In Progress", int(counts.get("In Progress", 0)))
    b3.metric("Resolved in Place", int(counts.get("Resolved in Place", 0)))
    b4.metric("Need More Info", int(counts.get("Need More Information", 0)))
    
    st.divider()
    
    st.write("### Update Incident Status")
    edited_df = st.data_editor(
        df_incidents[['Incident', 'Status', 'Department', 'Description']], 
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=['Completed On Time', 'Completed Late', 'In Draft', 'In Review', 'Resolved in Place'],
                required=True,
            )
        },
        use_container_width=True
    )
    
    if st.button("Save Changes"):
        st.success("Changes captured in session. (Ensure write permissions for file persistence).")

with tabs[4]:
    st.subheader("Data Explorer")
    selection = st.selectbox("Select Data to View:", list(data.keys()))
    st.dataframe(data[selection], use_container_width=True)
