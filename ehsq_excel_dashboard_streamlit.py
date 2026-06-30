import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="EHSQ Performance Dashboard", layout="wide")
st.title("EHSQ Performance Dashboard - Mt. Holly")

# 2. Data Loading
@st.cache_data
def load_data():
    # Loading the Excel file
    df = pd.read_excel('IncidentReports_All_MTH_2026-06-25.xlsx', sheet_name='Sheet1')
    # Clean headers to prevent KeyError
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()

    # 3. Sidebar for Navigation
    menu = ["Overview", "Compliance", "Housekeeping", "Safe Observations", "Risk Mitigation", "Compliance & Reporting Trends"]
    choice = st.sidebar.selectbox("Navigate", menu)

    # 4. Content Logic
    if choice == "Housekeeping":
        st.header("Housekeeping Status")
        hk_df = df[df['Type'] == 'Housekeeping']
        
        if not hk_df.empty:
            # Using the corrected 'Status' column here
            hk_data = hk_df.groupby(['Department', 'Status']).size().reset_index(name='Count')
            fig = px.bar(hk_data, x='Status', y='Count', color='Department', barmode='group', title="Housekeeping by Department")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No housekeeping data found.")

    elif choice == "Risk Mitigation":
        st.header("Status on Risk Mitigation")
        # Correctly using 'Status' here as well
        risk_data = df['Status'].value_counts().reset_index()
        risk_data.columns = ['Status', 'Count']
        fig = px.pie(risk_data, values='Count', names='Status', title="Risk Mitigation Distribution")
        st.plotly_chart(fig, use_container_width=True)

    # ... (Other sections follow the same logic)
    else:
        st.write(f"Section '{choice}' is under construction.")

except Exception as e:
    st.error(f"An error occurred: {e}")
