import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="EHSQ Performance Dashboard", layout="wide")
st.title("EHSQ Performance Dashboard - Mt. Holly")

# 2. Data Loading
@st.cache_data
def load_data():
    df = pd.read_csv('IncidentReports_All_MTH_2026-06-25.xlsx - Sheet1.csv')
    df.columns = df.columns.str.strip() # Clean headers
    return df

df = load_data()

# 3. Sidebar Navigation
menu = ["Overview", "Compliance", "Housekeeping", "Safe Observations", "Risk Mitigation", "Incident Breakdown"]
choice = st.sidebar.selectbox("Navigate", menu)

# 4. Content Logic
if choice == "Housekeeping":
    st.header("Housekeeping Status")
    # Filter for Housekeeping (Update 'Type' value if your data uses a different term)
    hk_df = df[df['Type'] == 'Housekeeping']
    
    if not hk_df.empty:
        hk_data = hk_df.groupby(['Location', 'Status']).size().reset_index(name='Count')
        fig = px.bar(hk_data, x='Status', y='Count', color='Location', barmode='group', title="Housekeeping by Location")
        st.plotly_chart(fig)
    else:
        st.warning("No housekeeping data found in the current report.")

elif choice == "Incident Breakdown":
    st.header("Incident Breakdown")
    # Count by type (as requested on whiteboard)
    incident_counts = df.groupby(['Type', 'Location']).size().reset_index(name='Count')
    fig = px.sunburst(incident_counts, path=['Type', 'Location'], values='Count')
    st.plotly_chart(fig)

elif choice == "Safe Observations":
    st.header("Safe Observations")
    # Generating 3 charts for Leadership, GS, and HSEQ
    groups = ['Leadership', 'GS', 'HSEQ']
    for group in groups:
        # Example filter logic - adjust column/value based on your data structure
        group_df = df[df['Reported By'].str.contains(group, na=False)] 
        st.subheader(f"Observations: {group}")
        st.bar_chart(group_df['Status'].value_counts())

elif choice == "Risk Mitigation":
    st.header("Status on Risk Mitigation")
    # Visualize the status counts
    risk_data = df['Status'].value_counts().reset_index()
    risk_data.columns = ['Status', 'Count']
    fig = px.pie(risk_data, values='Count', names='Status', title="Risk Mitigation Distribution")
    st.plotly_chart(fig)

else:
    st.write("Welcome to the Dashboard. Please select a section from the sidebar.")
