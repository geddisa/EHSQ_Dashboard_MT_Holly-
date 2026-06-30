import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

# --- DATA LOADING ---
@st.cache_data
def load_all_data():
    # Paths
    metrics_path = "EHSQ Metrics.xlsx"
    incident_path = "IncidentReports_All_MTH_2026-06-25.xlsx"
    
    # Load all sheets
    return {
        "Incidents": pd.read_excel(incident_path, sheet_name="Sheet1"),
        "FSI": pd.read_excel(metrics_path, sheet_name="FSI Reports"),
        "Other": pd.read_excel(metrics_path, sheet_name="Other Reports"),
        "CAPAs": pd.read_excel(metrics_path, sheet_name="CAPAs"),
        "Housekeeping": pd.read_excel(metrics_path, sheet_name="Housekeeping"),
        "Environmental": pd.read_excel(metrics_path, sheet_name="Environmental Compliance Issues"),
        "Observations": pd.read_excel(metrics_path, sheet_name="Safe Observations"),
        "TCIR": pd.read_excel(metrics_path, sheet_name="TCIR and DART"),
        "Severity": pd.read_excel(metrics_path, sheet_name="Overall Severity Ratings"),
        "YoY": pd.read_excel(metrics_path, sheet_name="Year over Year")
    }

data = load_all_data()

# --- DASHBOARD UI ---
tabs = st.tabs(["Overview", "Compliance & Reporting", "Performance Trends", "Data Explorer"])

with tabs[0]:
    st.subheader("Executive Summary")
    st.metric("Total Incidents Logged", len(data["Incidents"]))
    st.write("Year over Year Comparison:")
    st.table(data["YoY"])

with tabs[1]:
    st.subheader("Compliance Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.write("FSI Reports Status")
        st.dataframe(data["FSI"])
    with col2:
        st.write("Environmental Compliance")
        st.dataframe(data["Environmental"])

with tabs[2]:
    st.subheader("Performance Trends")
    st.write("TCIR and DART Trends")
    st.line_chart(data["TCIR"].set_index("Month")[["TCIR Actual", "DART Actual"]])
    
    st.write("Severity Rating Reference")
    st.table(data["Severity"])

with tabs[3]:
    st.subheader("Data Explorer")
    selected_sheet = st.selectbox("Select sheet to view:", list(data.keys()))
    st.dataframe(data[selected_sheet], use_container_width=True)
