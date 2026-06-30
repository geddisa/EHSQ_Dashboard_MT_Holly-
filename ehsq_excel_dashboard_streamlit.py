import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

# 2. Data Loading with cleaning
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

# 3. Layout
tabs = st.tabs(["Overview", "Compliance & Reporting", "Performance Trends", "Data Explorer"])

with tabs[0]:
    st.subheader("Executive Summary")
    st.metric("Total Incidents Logged", len(data["Incidents"]))
    
    st.write("### Environmental Compliance Issues")
    df_env = data["Environmental"]
    # Using positional indexing to prevent ValueError
    fig_env = px.bar(df_env.dropna(subset=[df_env.columns[1]]), 
                     x=df_env.columns[0], y=df_env.columns[1], title="Issues by Month")
    st.plotly_chart(fig_env, use_container_width=True)

with tabs[1]:
    st.subheader("Compliance & Reporting Trends")
    col1, col2 = st.columns(2)
    
    # FSI Chart
    df_fsi = data["FSI"]
    col1.plotly_chart(px.line(df_fsi, x=df_fsi.columns[0], y=df_fsi.columns[4], title="FSI % On Time"), use_container_width=True)
    
    # CAPA Chart
    df_capa = data["CAPAs"]
    col2.plotly_chart(px.line(df_capa, x=df_capa.columns[0], y=df_capa.columns[4], title="CAPA % On Time"), use_container_width=True)

with tabs[2]:
    st.subheader("Performance Trends (TCIR & DART)")
    df_tcir = data["TCIR"]
    # Ensure column names match your Excel headers exactly
    fig_perf = px.line(df_tcir, x="Month", y=["TCIR Actual", "DART Actual"], markers=True, title="Safety Performance Trend")
    st.plotly_chart(fig_perf, use_container_width=True)

with tabs[3]:
    st.subheader("Data Explorer")
    selection = st.selectbox("Select Data to View:", list(data.keys()))
    st.dataframe(data[selection], use_container_width=True)
