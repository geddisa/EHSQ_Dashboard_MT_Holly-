import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="MT. Holly | EHSQ KPI Dashboard")

# --- DATA LOADING ---
@st.cache_data
def load_all_data():
    # Update these paths if your files are in a folder like 'data/'
    # E.g., "data/IncidentReports_All_MTH_2026-07-01.xlsx"
    path_incidents = "IncidentReports_All_MTH_2026-07-01.xlsx"
    path_lpa = "Audit Schedule - Internal - LPA.xlsx"
    
    data = {
        "Incidents": pd.read_excel(path_incidents, sheet_name="Sheet1"),
        "Lead_Obs": pd.read_excel(path_lpa, sheet_name="Safe Obs - Leadership"),
        "GS_Obs": pd.read_excel(path_lpa, sheet_name="Safe Obs - GS and EHS"),
        "HSEQ_Obs": pd.read_excel(path_lpa, sheet_name="Safe Obs GS EHS")
    }
    return data

# Load data with error handling
try:
    data = load_all_data()
except Exception as e:
    st.error(f"Error loading files: {e}. Ensure all .xlsx files are in the repository.")
    st.stop()

# --- DATA TRANSFORMATION FOR TRENDS ---
def process_obs_data(df, category_name):
    # Sum numeric data across all columns after the first 3 identifier columns
    # Adjust .iloc[:, 3:] if your Week data starts at a different column index
    df_weekly = df.iloc[:, 3:].apply(pd.to_numeric, errors='coerce').sum().reset_index()
    df_weekly.columns = ['Week', 'Count']
    df_weekly['Category'] = category_name
    return df_weekly

# Consolidate trends
df_trend = pd.concat([
    process_obs_data(data["Lead_Obs"], "Leadership"),
    process_obs_data(data["GS_Obs"], "GS"),
    process_obs_data(data["HSEQ_Obs"], "HSEQ")
])

# --- UI ---
st.title("EHSQ Dashboard")
tabs = st.tabs(["Overview", "Safe Observations"])

with tabs[0]:
    st.subheader("Incident Analysis")
    st.write("Your existing incident logic goes here.")

with tabs[1]:
    st.subheader("Safe Observations Tracking")
    
    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Leadership Total", int(df_trend[df_trend['Category']=="Leadership"]['Count'].sum()))
    c2.metric("GS Total", int(df_trend[df_trend['Category']=="GS"]['Count'].sum()))
    c3.metric("HSEQ Total", int(df_trend[df_trend['Category']=="HSEQ"]['Count'].sum()))
    
    # Trend Chart
    fig = px.line(
        df_trend, 
        x="Week", 
        y="Count", 
        color="Category", 
        markers=True,
        title="Weekly Observation Trends"
    )
    st.plotly_chart(fig, use_container_width=True)
