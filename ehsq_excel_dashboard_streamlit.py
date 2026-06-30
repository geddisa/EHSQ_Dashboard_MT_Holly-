import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="EHSQ Performance Dashboard", layout="wide")
st.title("EHSQ Performance Dashboard - Mt. Holly")

# 2. Data Loading
@st.cache_data
def load_data():
    # Loading the Excel file directly
    file_path = 'IncidentReports_All_MTH_2026-06-25.xlsx'
    # 'sheet_name=0' loads the first sheet by default
    df = pd.read_excel(file_path, sheet_name=0)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()

    # 3. Sidebar Navigation
    menu = ["Overview", "Compliance", "Housekeeping", "Safe Observations", "Risk Mitigation", "Incident Breakdown"]
    choice = st.sidebar.selectbox("Navigate", menu)

    # 4. Content Logic
    if choice == "Housekeeping":
        st.header("Housekeeping Status")
        # Filter for rows where Type is 'Housekeeping'
        hk_df = df[df['Type'] == 'Housekeeping']
        
        if not hk_df.empty:
            hk_data = hk_df.groupby(['Location', 'Status']).size().reset_index(name='Count')
            fig = px.bar(hk_data, x='Status', y='Count', color='Location', barmode='group', title="Housekeeping by Location")
            st.plotly_chart(fig)
        else:
            st.warning("No housekeeping data found.")

    elif choice == "Incident Breakdown":
        st.header("Incident Breakdown")
        incident_counts = df.groupby(['Type', 'Location']).size().reset_index(name='Count')
        fig = px.sunburst(incident_counts, path=['Type', 'Location'], values='Count')
        st.plotly_chart(fig)

    elif choice == "Safe Observations":
        st.header("Safe Observations")
        # Filtering for the 3 groups
        groups = ['Leadership', 'GS', 'HSEQ']
        for group in groups:
            group_df = df[df['Reported By'].str.contains(group, na=False)]
            st.subheader(f"Observations: {group}")
            if not group_df.empty:
                st.bar_chart(group_df['Status'].value_counts())
            else:
                st.write(f"No records found for {group}")

    elif choice == "Risk Mitigation":
        st.header("Status on Risk Mitigation")
        risk_data = df['Status'].value_counts().reset_index()
        risk_data.columns = ['Status', 'Count']
        fig = px.pie(risk_data, values='Count', names='Status', title="Risk Mitigation Distribution")
        st.plotly_chart(fig)

    else:
        st.write("Select a section from the sidebar to view metrics.")

except FileNotFoundError:
    st.error("Error: The file 'IncidentReports_All_MTH_2026-06-25.xlsx' was not found. Please ensure it is in the same folder as this script.")
except Exception as e:
    st.error(f"An error occurred: {e}")
