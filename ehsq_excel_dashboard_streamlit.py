import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

@st.cache_data
def load_all_data():
    metrics_path = "EHSQ Metrics.xlsx"
    incident_path = "IncidentReports_All_MTH_2026-06-25.xlsx"
    
    # Load TCIR with forced headers
    tcir_df = pd.read_excel(metrics_path, sheet_name="TCIR and DART", header=1)
    tcir_df.columns = ["Month", "TCIR Actual", "TCIR Target", "DART Actual", 
                       "DART Target", "TCIR Industry Average", "DART Industry Average"]
    
    return {
        "Incidents": pd.read_excel(incident_path, sheet_name="Sheet1"),
        "FSI": pd.read_excel(metrics_path, sheet_name="FSI Reports"),
        "CAPAs": pd.read_excel(metrics_path, sheet_name="CAPAs"),
        "Housekeeping": pd.read_excel(metrics_path, sheet_name="Housekeeping"),
        "Environmental": pd.read_excel(metrics_path, sheet_name="Environmental Compliance Issues"),
        "TCIR": tcir_df,
        "Severity": pd.read_excel(metrics_path, sheet_name="Overall Severity Ratings")
    }

data = load_all_data()

# --- DASHBOARD UI ---
tabs = st.tabs(["Overview", "Compliance Trends", "Performance Charts", "Data Explorer"])

with tabs[0]:
    st.subheader("Executive Summary")
    st.metric("Total Incidents Logged", len(data["Incidents"]))
    
    # Severity Bar Chart
    fig_sev = px.bar(data["Severity"].dropna(subset=["Classification "]), 
                     x="Classification ", y="Points Assigned", title="Severity Point Distribution")
    st.plotly_chart(fig_sev, use_container_width=True)

with tabs[1]:
    st.subheader("Compliance & Reporting Trends")
    col1, col2 = st.columns(2)
    
    # FSI Completion Chart
    fig_fsi = px.line(data["FSI"], x=data["FSI"].iloc[:,0], y="% On Time", title="FSI % On Time")
    col1.plotly_chart(fig_fsi, use_container_width=True)
    
    # Environmental Issues Chart
    fig_env = px.bar(data["Environmental"], x=data["Environmental"].iloc[:,0], y="# of Reported Compliance Issues", title="Env. Compliance Issues")
    col2.plotly_chart(fig_env, use_container_width=True)

with tabs[2]:
    st.subheader("Performance Trends (TCIR & DART)")
    # Multi-line chart for TCIR/DART
    fig_perf = px.line(data["TCIR"], x="Month", y=["TCIR Actual", "DART Actual"], 
                       markers=True, title="TCIR vs DART Performance")
    st.plotly_chart(fig_perf, use_container_width=True)

with tabs[3]:
    st.subheader("Data Explorer")
    selected_sheet = st.selectbox("Select raw data to view:", list(data.keys()))
    st.dataframe(data[selected_sheet], use_container_width=True)
