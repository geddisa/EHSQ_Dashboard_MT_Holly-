import streamlit as st
import pandas as pd
import os
import glob

# Page Configuration
st.set_page_config(page_title="EHSQ Dashboard", layout="wide")

st.title("EHSQ Management Dashboard")

# 1. Automatic Data Loader
def get_latest_file(folder, pattern):
    list_of_files = glob.glob(f"{folder}/{pattern}")
    return max(list_of_files, key=os.path.getctime)

@st.cache_data
def load_data():
    incident_file = get_latest_file("data", "IncidentReports_*.xlsx")
    metrics_file = "data/EHSQ Metrics.xlsx"
    
    df_incidents = pd.read_excel(incident_file)
    df_metrics = pd.read_excel(metrics_file, sheet_name=0)
    return df_incidents, df_metrics

df, metrics = load_data()

# 2. Risk Mitigation Tracker Logic
def get_tracker_counts(df):
    def categorize(status):
        if status in ['Completed On Time', 'Completed Late']: return 'Completed'
        if status in ['In Draft', 'In Review']: return 'In Progress'
        if status == 'Resolved in Place': return 'Resolved in Place'
        if status == 'Need More Information': return 'Need More Information'
        return 'Other'

    df['Cat'] = df['Status'].apply(categorize)
    counts = df['Cat'].value_counts()
    
    return {
        "Completed": counts.get("Completed", 0),
        "In Progress": counts.get("In Progress", 0),
        "Resolved in Place": counts.get("Resolved in Place", 0),
        "Need More Information": counts.get("Need More Information", 0)
    }

# Display Risk Mitigation Tracker
st.subheader("Risk Mitigation Tracker")
counts = get_tracker_counts(df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Completed", counts["Completed"])
col2.metric("In Progress", counts["In Progress"])
col3.metric("Resolved in Place", counts["Resolved in Place"])
col4.metric("Need More Info", counts["Need More Information"])

# 3. Data Tables & Visualization
st.divider()
tab1, tab2 = st.tabs(["Incident Overview", "EHSQ Metrics"])

with tab1:
    st.subheader("Recent Incident Data")
    st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("Metric Performance")
    st.dataframe(metrics, use_container_width=True)
