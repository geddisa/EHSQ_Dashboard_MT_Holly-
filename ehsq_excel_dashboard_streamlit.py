import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

@st.cache_data
def load_all_data():
    # Ensure these paths are correct for your environment
    metrics_path = "EHSQ Metrics.xlsx"
    incident_path = "IncidentReports_All_MTH_2026-06-25.xlsx"
    audit_path = "Audit Schedule - Internal - LPA.xlsx"
    
    def clean_columns(df):
        df.columns = df.columns.astype(str).str.strip()
        return df

    try:
        return {
            "Incidents": clean_columns(pd.read_excel(incident_path, sheet_name="Sheet1")),
            "FSI": clean_columns(pd.read_excel(metrics_path, sheet_name="FSI Reports", skiprows=1)),
            "CAPAs": clean_columns(pd.read_excel(metrics_path, sheet_name="CAPAs", skiprows=1)),
            "HSEQ_Obs": clean_columns(pd.read_excel(audit_path, sheet_name="Safe Obs GS EHS")),
            "Lead_Obs": clean_columns(pd.read_excel(audit_path, sheet_name="Safe Obs - Leadership")),
            "GS_Obs": clean_columns(pd.read_excel(audit_path, sheet_name="Safe Obs - GS and EHS"))
        }
    except Exception as e:
        st.error(f"Error loading files: {e}")
        return None

data = load_all_data()

if data is not None:
    # --- GLOBAL DATA PROCESSING ---
    df_raw = data["Incidents"].copy()
    date_col = 'Date of Incident (UTC)'
    df_raw['Date'] = pd.to_datetime(df_raw[date_col], errors='coerce')
    
    # Filtered version for 2026 charts
    df = df_raw[df_raw['Date'].dt.year == 2026].dropna(subset=['Date']).copy()
    df['Week'] = df['Date'].dt.isocalendar().week

    tabs = st.tabs(["Overview", "Compliance", "Housekeeping", "Safe Observations", "Risk Mitigation"])

    with tabs[0]: 
        st.subheader("2026 Incident Severity Tracking")
        severity_mapping = {'Property Damage': 25, 'First Aid': 75, 'Other Recordable Case': 250, 'Days Away From Work': 350, 'Recordable - Fatality': 600}
        df['Points'] = df['Injury Classification'].map(severity_mapping).fillna(0)
        weekly_scores = df.groupby('Week')['Points'].sum().sort_index()
        fig = go.Figure(go.Scatter(x=weekly_scores.index, y=weekly_scores.values, mode='lines+markers'))
        st.plotly_chart(fig, use_container_width=True)

    with tabs[3]:
        st.subheader("Safe Observations")
        hseq_df = data["HSEQ_Obs"]
        # Use simple column indexing or check for presence
        st.metric("HSEQ Obs", len(hseq_df))

    with tabs[4]: 
        st.subheader("Risk Mitigation Progress (All Time)")
        # Using df_raw which is guaranteed to be defined in this scope
        total_risk = len(df_raw)
        completed = len(df_raw[df_raw['Status'].isin(['Completed On Time', 'Completed Late'])])
        in_progress = len(df_raw[df_raw['Status'].isin(['In Draft', 'In Review'])])
        need_info = max(0, total_risk - (completed + in_progress))
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Risk (All)", total_risk)
        c2.metric("Completed", completed)
        c3.metric("In Progress", in_progress)
        c4.metric("Need Info", need_info)
        
        st.divider()
        st.write("### Edit Incident Status (All Data)")
        st.data_editor(df_raw, column_config={
            "Status": st.column_config.SelectboxColumn(options=['Completed On Time', 'Completed Late', 'In Draft', 'In Review', 'Need Info'])
        }, use_container_width=True)
