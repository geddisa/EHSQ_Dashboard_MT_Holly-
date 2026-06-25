import streamlit as st
import pandas as pd
import os
import glob

# Set page layout
st.set_page_config(page_title="EHSQ Dashboard", layout="wide")

st.title("EHSQ Management Dashboard")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    # Look for files in the same directory as this script
    incident_files = glob.glob("IncidentReports_*.xlsx")
    metrics_file = "EHSQ Metrics.xlsx"
    
    if not incident_files:
        st.error("Error: No 'IncidentReports_*.xlsx' file found in the repository root.")
        st.stop()
    if not os.path.exists(metrics_file):
        st.error(f"Error: '{metrics_file}' not found.")
        st.stop()
        
    # Get the latest incident file
    latest_incident = max(incident_files, key=os.path.getctime)
    
    df_incidents = pd.read_excel(latest_incident)
    df_metrics = pd.read_excel(metrics_file, sheet_name=0)
    return df_incidents, df_metrics

# Execute load
df, metrics = load_data()

# --- RISK MITIGATION TRACKER ---
st.subheader("Risk Mitigation Tracker")

def get_tracker_counts(df):
    # Ensure column exists
    if 'Status' not in df.columns:
        return {"Completed": 0, "In Progress": 0, "Resolved in Place": 0, "Need More Information": 0}
        
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

counts = get_tracker_counts(df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Completed", counts["Completed"])
col2.metric("In Progress", counts["In Progress"])
col3.metric("Resolved in Place", counts["Resolved in Place"])
col4.metric("Need More Info", counts["Need More Information"])

# --- DATA DISPLAY ---
st.divider()
st.subheader("Raw Data View")
st.dataframe(df, use_container_width=True)
