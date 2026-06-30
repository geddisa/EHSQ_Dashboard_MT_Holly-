import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Dashboard Setup
st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

@st.cache_data
def load_all_data():
    metrics_path = "EHSQ Metrics.xlsx"
    incident_path = "IncidentReports_All_MTH_2026-06-25.xlsx"
    audit_path = "Audit Schedule - Internal - LPA.xlsx"
    
    def clean_columns(df):
        df.columns = df.columns.astype(str).str.strip()
        return df

    try:
        data = {
            "Incidents": clean_columns(pd.read_excel(incident_path, sheet_name="Sheet1")),
            "FSI": clean_columns(pd.read_excel(metrics_path, sheet_name="FSI Reports", skiprows=1)),
            "CAPAs": clean_columns(pd.read_excel(metrics_path, sheet_name="CAPAs", skiprows=1)),
            "Lead_Obs": clean_columns(pd.read_excel(audit_path, sheet_name="Safe Obs - Leadership")),
            "GS_Obs": clean_columns(pd.read_excel(audit_path, sheet_name="Safe Obs - GS and EHS")),
            "HSEQ_Obs": clean_columns(pd.read_excel(audit_path, sheet_name="Safe Obs GS EHS"))
        }
        # Prepare Incident Points for Severity Graph
        df = data["Incidents"]
        df['Date of Incident (EDT)'] = pd.to_datetime(df['Date of Incident (EDT)'])
        df['Week'] = df['Date of Incident (EDT)'].dt.isocalendar().week
        severity_mapping = {'Property Damage': 25, 'First Aid': 75, 'Other Recordable Case': 250} # Simplified
        df['Points'] = df['Injury Classification'].map(severity_mapping).fillna(0)
        data["Weekly_Scores"] = df.groupby('Week')['Points'].sum().reindex(range(1, 26), fill_value=0)
        return data
    except Exception as e:
        st.error(f"Error loading files: {e}")
        return None

data = load_all_data()

if data:
    tabs = st.tabs(["Overview", "Compliance", "Housekeeping", "Safe Observations", "Risk Mitigation"])

    with tabs[0]: 
        st.subheader("Incident Severity Tracking")
        fig = go.Figure()
        # Risk Zones
        fig.add_hrect(y0=0, y1=400, fillcolor="lightgreen", opacity=0.3, layer="below")
        fig.add_hrect(y0=400, y1=800, fillcolor="khaki", opacity=0.3, layer="below")
        fig.add_hrect(y0=800, y1=1250, fillcolor="lightcoral", opacity=0.3, layer="below")
        # Trend Line
        fig.add_trace(go.Scatter(x=data["Weekly_Scores"].index, y=data["Weekly_Scores"].values, mode='lines+markers', name='Weekly Severity'))
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]: 
        st.subheader("Compliance & Reporting Trends")
        col1, col2 = st.columns(2)
        # FSI with Target
        df_fsi = data["FSI"].dropna(subset=[data["FSI"].columns[4]])
        fig_fsi = px.line(df_fsi, x=df_fsi.columns[0], y=df_fsi.columns[4], title="FSI % On Time")
        fig_fsi.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Target (100%)")
        col1.plotly_chart(fig_fsi, use_container_width=True)
        # CAPA with Target
        df_capa = data["CAPAs"].dropna(subset=[data["CAPAs"].columns[4]])
        fig_capa = px.line(df_capa, x=df_capa.columns[0], y=df_capa.columns[4], title="CAPA % On Time")
        fig_capa.add_hline(y=0.8, line_dash="dash", line_color="red", annotation_text="Target (80%)")
        col2.plotly_chart(fig_capa, use_container_width=True)
