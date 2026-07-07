import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="MT. Holly | EHSQ KPI Dashboard")

# --- DATA LOADING ---
def load_all_data():
    # Adjusted to point to your specific CSV files
    files = {
        "Incidents": "IncidentReports_All_MTH_2026-07-01.csv",
        "Lead_Obs": "Audit Schedule - Internal - LPA.xlsx - Safe Obs - Leadership.csv",
        "GS_Obs": "Audit Schedule - Internal - LPA.xlsx - Safe Obs - GS and EHS.csv",
        "HSEQ_Obs": "Audit Schedule - Internal - LPA.xlsx - Safe Obs GS EHS.csv"
    }
    data = {k: pd.read_csv(v) for k, v in files.items()}
    return data

# --- DATA TRANSFORMATION ---
def process_obs_data(df, category_name):
    """
    Cleans the observation CSVs: assumes weekly data is in columns 
    after the initial descriptive columns.
    """
    # Keep only numeric columns (weeks) and sum them up
    # Note: Adjust column index [3:] to match where your 'Week' columns start
    df_weekly = df.iloc[:, 3:].apply(pd.to_numeric, errors='coerce').sum().reset_index()
    df_weekly.columns = ['Week', 'Count']
    df_weekly['Category'] = category_name
    return df_weekly

data = load_all_data()

# Process Observation Trends
df_trend = pd.concat([
    process_obs_data(data["Lead_Obs"], "Leadership"),
    process_obs_data(data["GS_Obs"], "GS"),
    process_obs_data(data["HSEQ_Obs"], "HSEQ")
])

# --- DASHBOARD UI ---
st.title("EHSQ Dashboard")
tabs = st.tabs(["Overview", "Safe Observations"])

with tabs[0]:
    st.subheader("Incident Severity Analysis")
    # ... (Your existing incident logic here)

with tabs[1]:
    st.subheader("Safe Observations Tracking & Trends")
    
    # Current Snapshot Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Leadership Obs", int(df_trend[df_trend['Category']=="Leadership"]['Count'].sum()))
    c2.metric("GS Obs", int(df_trend[df_trend['Category']=="GS"]['Count'].sum()))
    c3.metric("HSEQ Obs", int(df_trend[df_trend['Category']=="HSEQ"]['Count'].sum()))
    
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
    
    # Raw Data Table
    st.dataframe(df_trend)
