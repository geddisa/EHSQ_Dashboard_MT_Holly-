import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Dashboard Setup
st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

@st.cache_data
def load_all_data():
    metrics_path = "EHSQ Metrics.xlsx"
    incident_path = "IncidentReports_All_MTH_2026-06-25.xlsx"
    
    # Load data
    incidents_df = pd.read_excel(incident_path, sheet_name="Sheet1")
    fsi_df = pd.read_excel(metrics_path, sheet_name="FSI Reports", skiprows=1)
    capa_df = pd.read_excel(metrics_path, sheet_name="CAPAs", skiprows=1)
    
    return incidents_df, fsi_df, capa_df

df_incidents, df_fsi, df_capa = load_all_data()

# Standardize column names
df_fsi.columns = df_fsi.columns.str.strip()
df_capa.columns = df_capa.columns.str.strip()

tabs = st.tabs(["Overview", "Compliance"])

with tabs[0]:
    st.subheader("Incident Severity Graph")
    
    # Logic based on 'Severity Graph - Incident Reporting by Aliyah Geddis.py'
    df_incidents['Date of Incident (EDT)'] = pd.to_datetime(df_incidents['Date of Incident (EDT)'])
    df_incidents['Week'] = df_incidents['Date of Incident (EDT)'].dt.isocalendar().week
    
    severity_mapping = {
        'Property Damage': 25, 'Record Only-No Treatment': 50, 'First Aid': 75,
        'Molten Metal Spill > 25 lbs': 150, 'Molten Metal Explosion (Force 2 or 3)': 150,
        'Other Recordable Case': 250, 'Restricted or Transferred Work': 250,
        'Days Away From Work': 350, 'Recordable - Fatality': 600 
    }
    
    df_incidents['Points'] = df_incidents['Injury Classification'].map(severity_mapping).fillna(
        df_incidents['Type'].map(severity_mapping)
    ).fillna(0)
    
    weekly_scores = df_incidents.groupby('Week')['Points'].sum().reindex(range(1, 25), fill_value=0)
    
    # Generate Plot
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axhspan(0, 400, color='lightgreen', alpha=0.4, label='Low Risk Zone (0-400)')
    ax.axhspan(400, 800, color='khaki', alpha=0.4, label='Medium Risk Zone (401-800)')
    ax.axhspan(800, 1250, color='lightcoral', alpha=0.4, label='High Risk Zone (800+)')
    
    ax.plot(weekly_scores.index, weekly_scores.values, color='black', linewidth=2.5, marker='o', markersize=6, label='Weekly Severity Total')
    ax.set_title('Incident Severity Graph', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(range(1, 25))
    ax.legend(loc='upper left')
    
    st.pyplot(fig)

with tabs[1]:
    st.subheader("Compliance & Reporting Trends")
    col1, col2 = st.columns(2)
    
    # FSI Graph
    fig_fsi = px.line(df_fsi, x=df_fsi.columns[0], y=df_fsi.columns[4], title="FSI % On Time", markers=True)
    fig_fsi.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Target (100%)")
    col1.plotly_chart(fig_fsi, use_container_width=True)
    
    # CAPA Graph
    fig_capa = px.line(df_capa, x=df_capa.columns[0], y=df_capa.columns[4], title="CAPA % On Time", markers=True)
    fig_capa.add_hline(y=0.8, line_dash="dash", line_color="red", annotation_text="Target (80%)")
    col2.plotly_chart(fig_capa, use_container_width=True)
