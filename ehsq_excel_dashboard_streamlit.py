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
    
    try:
        data = {
            "Incidents": pd.read_excel(incident_path, sheet_name="Sheet1"),
            "FSI": pd.read_excel(metrics_path, sheet_name="FSI Reports", skiprows=1),
            "CAPAs": pd.read_excel(metrics_path, sheet_name="CAPAs", skiprows=1),
        }
        
        # Prepare Incident Points
        df = data["Incidents"]
        df.columns = df.columns.str.strip()
        
        # Define severity map based on your project requirements
        severity_mapping = {
            'Property Damage': 25,
            'Record Only-No Treatment': 50,
            'First Aid': 75,
            'Other Recordable Case': 250
        }
        df['Points'] = df['Injury Classification'].map(severity_mapping).fillna(0)
        
        # Aggregate severity by index for the chart
        data["Weekly_Scores"] = df.groupby(df.index)['Points'].sum()
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
        # Add risk zones (Low, Medium, High)
        fig.add_hrect(y0=0, y1=400, fillcolor="lightgreen", opacity=0.3, layer="below")
        fig.add_hrect(y0=400, y1=800, fillcolor="khaki", opacity=0.3, layer="below")
        fig.add_hrect(y0=800, y1=1250, fillcolor="lightcoral", opacity=0.3, layer="below")
        
        fig.add_trace(go.Scatter(y=data["Weekly_Scores"].values, mode='lines+markers', name='Severity Points'))
        fig.update_layout(title="Severity Trends", yaxis_title="Points")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]: 
        st.subheader("Compliance & Reporting Trends")
        col1, col2 = st.columns(2)
        
        # FSI with 100% Target
        fsi_df = data["FSI"].dropna(subset=[data["FSI"].columns[4]])
        fig_fsi = px.line(fsi_df, x=fsi_df.columns[0], y=fsi_df.columns[4], title="FSI % On Time", markers=True)
        fig_fsi.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Target (100%)")
        col1.plotly_chart(fig_fsi, use_container_width=True)
        
        # CAPA with 80% Target
        capa_df = data["CAPAs"].dropna(subset=[data["CAPAs"].columns[4]])
        fig_capa = px.line(capa_df, x=capa_df.columns[0], y=capa_df.columns[4], title="CAPA % On Time", markers=True)
        fig_capa.add_hline(y=0.8, line_dash="dash", line_color="red", annotation_text="Target (80%)")
        col2.plotly_chart(fig_capa, use_container_width=True)
