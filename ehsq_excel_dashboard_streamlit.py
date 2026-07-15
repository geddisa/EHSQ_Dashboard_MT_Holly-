import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# =====================================================
# DASHBOARD SETUP
# =====================================================
st.set_page_config(
    layout="wide",
    page_title="EHSQ KPI Dashboard"
)

# -----------------------------------------------------
# HEADER SECTION WITH LOGO
# -----------------------------------------------------
header_left, header_right = st.columns([1, 4])

with header_left:
    st.image("century_logo.png", use_container_width=True)

with header_right:
    st.markdown(
        "<h1 style='margin-top: 10px;'>EHSQ KPI Dashboard</h1>",
        unsafe_allow_html=True
    )

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data
def load_all_data():
    path_lpa = "Audit Schedule - Internal - LPA.xlsx"
    return {
        "Risk_Mitigation": pd.read_excel("RiskNotifications_All_MTH_2026-07-14.xlsx", sheet_name="Sheet1"),
        "Incidents": pd.read_excel("IncidentReports_All_MTH_2026-07-14.xlsx", sheet_name="Sheet1"),
        "FSI": pd.read_excel("EHSQ Metrics.xlsx", sheet_name="FSI Reports", skiprows=1),
        "CAPAs": pd.read_excel("EHSQ Metrics.xlsx", sheet_name="CAPAs", skiprows=1),
        "Lead_Obs": pd.read_excel(path_lpa, sheet_name="Safe Obs - Leadership", skiprows=2),
        "GS_Obs": pd.read_excel(path_lpa, sheet_name="Safe Obs - GS and EHS", skiprows=2),
        "HSEQ_Obs": pd.read_excel(path_lpa, sheet_name="Safe Obs GS EHS", skiprows=2)
    }

try:
    data = load_all_data()
except Exception as e:
    st.error(f"Error loading files: {e}")
    st.stop()

# =====================================================
# PROCESS INCIDENT DATA
# =====================================================
df_raw = data["Incidents"].copy()
df_raw["Date"] = pd.to_datetime(df_raw["Date of Incident (UTC)"], errors="coerce")
df_2026 = df_raw[df_raw["Date"].dt.year == 2026].copy()

# =====================================================
# TABS SETUP
# =====================================================
tabs = st.tabs(["Overview", "Compliance", "Housekeeping", "Safe Observations", "Risk Mitigation"])
tab1, tab2, tab3, tab4, tab5 = tabs

# =====================================================
# TAB 1 - OVERVIEW
# =====================================================
with tab1:
    st.subheader("Incident Breakdown")
    col1, col2 = st.columns(2)

    if not df_2026.empty:
        # Incidents by Type
        type_counts = df_2026.groupby("Type").size().reset_index(name="Count")
        fig_type = px.bar(type_counts, x="Type", y="Count", text="Count", title="Incidents by Type")
        fig_type.update_traces(textposition="outside")
        col1.plotly_chart(fig_type, use_container_width=True)

        # Incidents by Department
        dept_counts = df_2026.groupby(["Department", "Type"]).size().reset_index(name="Count")
        fig_dept = px.bar(dept_counts, x="Department", y="Count", color="Type", text="Count", 
                          title="Incidents by Department", barmode="group")
        fig_dept.update_traces(textposition="outside", texttemplate="%{text}")
        col2.plotly_chart(fig_dept, use_container_width=True)

    # Incident Severity Trend
    st.subheader("Incident Severity Trend")
    df_incidents = data["Incidents"].copy()
    df_incidents['Date of Incident (UTC)'] = pd.to_datetime(df_incidents['Date of Incident (UTC)'])
    df_incidents['Week'] = df_incidents['Date of Incident (UTC)'].dt.isocalendar().week
    
    severity_mapping = {'Property Damage': 25, 'Record Only - No Treatment': 50, 'First Aid': 75, 
                        'Molten Metal Spill > 25 lbs': 150, 'Molten Metal Explosion (Force 2 or 3)': 150, 
                        'Other Recordable Case': 250, 'Restricted or Transferred Work': 250, 
                        'Days Away From Work': 350, 'Recordable - Fatality': 600}
    
    df_incidents['Points'] = df_incidents['Injury Classification'].map(severity_mapping).fillna(df_incidents['Type'].map(severity_mapping)).fillna(0)
    weekly_scores = df_incidents.groupby('Week')['Points'].sum()
    current_week = pd.Timestamp.now().isocalendar().week
    weekly_scores = weekly_scores.reindex(range(1, current_week + 1), fill_value=0)

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axhspan(0, 400, color='lightgreen', alpha=0.4, label='Low Risk (0-400)')
    ax.axhspan(400, 800, color='khaki', alpha=0.4, label='Medium Risk (401-800)')
    ax.axhspan(800, 1250, color='lightcoral', alpha=0.4, label='High Risk (800+)')
    ax.plot(weekly_scores.index, weekly_scores.values, color='black', marker='o', label='Severity Total')
    ax.set_title('Incident Severity Graph')
    ax.set_xlabel('Week')
    ax.set_ylabel('Points')
    ax.set_ylim(0, 1250)
    ax.legend()
    st.pyplot(fig)

# =====================================================
# TAB 2 - COMPLIANCE
# =====================================================
with tab2:
    st.subheader("Compliance & Reporting Trends")
    c1, c2 = st.columns(2)

    for col_obj, data_key, title in [(c1, "FSI", "FSI % On Time"), (c2, "CAPAs", "CAPA % On Time")]:
        df = data[data_key].copy()
        col_name = df.columns[4]
        df[col_name] = pd.to_numeric(df[col_name], errors='coerce') * 100
        fig = px.line(df, x=df.columns[0], y=col_name, markers=True, text=col_name, title=title)
        fig.update_traces(texttemplate="%{text:.0f}%", textposition="top center")
        fig.update_yaxes(range=[0, 100], tickformat=".0f")
        col_obj.plotly_chart(fig, use_container_width=True)

# =====================================================
# TABS 3, 4, 5 (REMAINING)
# =====================================================
# (Place your existing Housekeeping, Safe Obs, and Risk Mitigation code here, 
# ensuring 4-space indentation under the 'with tabX:' statements)
