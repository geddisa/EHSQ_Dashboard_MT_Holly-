import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

# --- DATA LOADING ---
@st.cache_data
def load_all_data():
    metrics_path = "EHSQ Metrics.xlsx"
    incident_path = "IncidentReports_All_MTH_2026-06-25.xlsx"
    
    def clean_columns(df):
        df.columns = df.columns.astype(str).str.strip()
        return df

    # Load and clean sheets individually to ensure schema stability
    return {
        "Incidents": clean_columns(pd.read_excel(incident_path, sheet_name="Sheet1")),
        "FSI": clean_columns(pd.read_excel(metrics_path, sheet_name="FSI Reports", skiprows=1)),
        "CAPAs": clean_columns(pd.read_excel(metrics_path, sheet_name="CAPAs", skiprows=1)),
        "Environmental": clean_columns(pd.read_excel(metrics_path, sheet_name="Environmental Compliance Issues", skiprows=1)),
        "TCIR": clean_columns(pd.read_excel(metrics_path, sheet_name="TCIR and DART", skiprows=1)),
        "Severity": clean_columns(pd.read_excel(metrics_path, sheet_name="Overall Severity Ratings", skiprows=0))
    }

data = load_all_data()

# --- UI LAYOUT ---
tabs = st.tabs(["Overview", "Compliance & Reporting", "Performance Trends", "Data Explorer"])

with tabs[0]:
    st.subheader("Executive Summary")
    st.metric("Total Incidents Logged", len(data["Incidents"]))
    st.write("Environmental Compliance Status")
    st.plotly_chart(px.bar(data["Environmental"].dropna(subset=["# of Reported Compliance Issues"]), 
                           x="2026 Environmental Compliance Issues", y="# of Reported Compliance Issues"), use_container_width=True)

with tabs[1]:
    st.subheader("Compliance Metrics")
    col1, col2 = st.columns(2)
    # Use positional indexing (iloc) to guarantee column selection regardless of header name
    col1.plotly_chart(px.line(data["FSI"], x=data["FSI"].iloc[:,0], y=data["FSI"].iloc[:,4], title="FSI % On Time"), use_container_width=True)
    col2.plotly_chart(px.line(data["CAPAs"], x=data["CAPAs"].iloc[:,0], y=data["CAPAs"].iloc[:,4], title="CAPA % On Time"), use_container_width=True)

with tabs[2]:
    st.subheader("Performance Trends (TCIR & DART)")
    # Explicit mapping for TCIR based on known columns
    df_tcir = data["TCIR"].copy()
    fig = px.line(df_tcir, x="Month", y=["TCIR Actual", "DART Actual"], markers=True, title="Safety Performance Trend")
    st.plotly_chart(fig, use_container_width=True)

with tabs[3]:
    st.subheader("Data Explorer")
    selection = st.selectbox("Select Data:", list(data.keys()))
    st.dataframe(data[selection], use_container_width=True)
