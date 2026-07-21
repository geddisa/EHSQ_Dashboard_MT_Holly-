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
        "Risk_Mitigation": pd.read_excel(
            "RiskNotifications_All_MTH_2026-07-14.xlsx",
            sheet_name="Sheet1"
        ),
        "Incidents": pd.read_excel(
            "IncidentReports_All_MTH_2026-07-21.xlsx",
            sheet_name="Sheet1"
        ),
        "FSI": pd.read_excel(
            "EHSQ Metrics.xlsx",
            sheet_name="FSI Reports",
            skiprows=1
        ),
        "CAPAs": pd.read_excel(
            "EHSQ Metrics.xlsx",
            sheet_name="CAPAs",
            skiprows=1
        ),
        "Lead_Obs": pd.read_excel(
            path_lpa,
            sheet_name="Safe Obs - Leadership",
            skiprows=2
        ),
        "GS_Obs": pd.read_excel(
            path_lpa,
            sheet_name="Safe Obs - GS and EHS",
            skiprows=2
        ),
        "HSEQ_Obs": pd.read_excel(
            path_lpa,
            sheet_name="Safe Obs GS EHS",
            skiprows=2
        )
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

df_raw["Date"] = pd.to_datetime(
    df_raw["Date of Incident (UTC)"],
    errors="coerce"
)

df_2026 = df_raw[
    df_raw["Date"].dt.year == 2026
].copy()

# =====================================================
# TABS SETUP & UNPACKING
# =====================================================
tabs = st.tabs([
    "Overview",
    "Compliance",
    "Housekeeping",
    "Safe Observations",
    "Risk Mitigation"
])

tab1, tab2, tab3, tab4, tab5 = tabs

# =====================================================
# TAB 1 - OVERVIEW
# =====================================================
with tab1:
    st.subheader("Incident Breakdown")

    col1, col2 = st.columns(2)

    if not df_2026.empty:

        # -----------------------------------------
        # Incidents by Type
        # -----------------------------------------
        type_counts = (
            df_2026.groupby("Type")
            .size()
            .reset_index(name="Count")
        )

        fig_type = px.bar(
            type_counts,
            x="Type",
            y="Count",
            text="Count",
            title="Incidents by Type"
        )

        fig_type.update_traces(textposition="outside")

        col1.plotly_chart(
            fig_type,
            use_container_width=True
        )

        # -----------------------------------------
        # Incidents by Department
        # -----------------------------------------
        dept_counts = (
            df_2026.groupby(["Department", "Type"])
            .size()
            .reset_index(name="Count")
        )

        fig_dept = px.bar(
            dept_counts,
            x="Department",
            y="Count",
            color="Type",
            text="Count",
            title="Incidents by Department",
            barmode="group"
        )

        fig_dept.update_traces(
            textposition="outside",
            texttemplate="%{text}"
        )

        col2.plotly_chart(
            fig_dept,
            use_container_width=True
        )
    # -----------------------------------------
    # Incident Severity Trend
    # -----------------------------------------
    st.subheader("Incident Severity Trend")

    # Prepare data for severity graph
    df_incidents = data["Incidents"].copy()
    df_incidents['Date of Incident (UTC)'] = pd.to_datetime(df_incidents['Date of Incident (UTC)'])
    df_incidents['Week'] = df_incidents['Date of Incident (UTC)'].dt.isocalendar().week

    severity_mapping = {
        'Property Damage': 25, 'Record Only - No Treatment': 50, 'First Aid': 75,
        'Molten Metal Spill > 25 lbs': 150, 'Molten Metal Explosion (Force 2 or 3)': 150,
        'Other Recordable Case': 250, 'Restricted or Transferred Work': 250,
        'Days Away From Work': 350, 'Recordable - Fatality': 600
    }

    df_incidents['Points'] = df_incidents['Injury Classification'].map(severity_mapping).fillna(
        df_incidents['Type'].map(severity_mapping)
    ).fillna(0)

    weekly_scores = df_incidents.groupby('Week')['Points'].sum()
    current_week = pd.Timestamp.now().isocalendar().week
    weekly_scores = weekly_scores.reindex(range(1, current_week + 1), fill_value=0)

    # Plotting
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axhspan(0, 400, color='lightgreen', alpha=0.4, label='Low Risk (0-400)')
    ax.axhspan(400, 800, color='khaki', alpha=0.4, label='Medium Risk (401-800)')
    ax.axhspan(800, 1250, color='lightcoral', alpha=0.4, label='High Risk (800+)')
    ax.plot(weekly_scores.index, weekly_scores.values, color='black', linewidth=2.5, marker='o', label='Weekly Severity Total')
    
    ax.set_title('Incident Severity Graph')
    ax.set_xlabel('Calendar Week Number')
    ax.set_ylabel('Total Accumulated Severity Points')
    ax.set_ylim(0, 1250)
    ax.set_xticks(range(1, current_week + 1))
    ax.legend(loc='upper left')

    # Display in Streamlit
    st.pyplot(fig)
    # -----------------------------------------
    # Severity Point System Legend
    # -----------------------------------------
    st.markdown("### Severity Point Legend")
    
    # Create a clean layout for the points
    col_l1, col_l2 = st.columns(2)
    
    with col_l1:
        st.write("**Property Damage:** 25 pts")
        st.write("**Record Only - No Treatment:** 50 pts")
        st.write("**First Aid:** 75 pts")
        st.write("**Molten Metal Spill > 25 lbs:** 150 pts")
        
    with col_l2:
        st.write("**Molten Metal Explosion (Force 2 or 3):** 150 pts")
        st.write("**Other Recordable Case / Restricted or Transferred Work:** 250 pts")
        st.write("**Days Away From Work:** 350 pts")
        st.write("**Recordable - Fatality:** 600 pts")
# =====================================================
# TAB 2 - COMPLIANCE
# =====================================================
with tab2:
    st.subheader("Compliance & Reporting Trends")

    c1, c2 = st.columns(2)

    # -----------------------------------------
    # FSI Trend
    # -----------------------------------------
    df_fsi = data["FSI"].copy()
    fsi_col = df_fsi.columns[4]
    df_fsi[fsi_col] = pd.to_numeric(df_fsi[fsi_col], errors='coerce')
    df_fsi['Plot_Value'] = df_fsi[fsi_col] * 100

    fig_fsi = px.line(
        df_fsi,
        x=df_fsi.columns[0],
        y='Plot_Value',
        markers=True,
        text='Plot_Value',
        title="FSI % On Time"
    )

    fig_fsi.update_traces(
        texttemplate="%{text:.0f}%",
        textposition="top center"
    )
    
    fig_fsi.update_yaxes(range=[0, 100], tickformat=".0f")

    c1.plotly_chart(fig_fsi, use_container_width=True)

    # -----------------------------------------
    # CAPA Trend
    # -----------------------------------------
    df_capa = data["CAPAs"].copy()
    capa_col = df_capa.columns[4]
    df_capa[capa_col] = pd.to_numeric(df_capa[capa_col], errors='coerce')
    df_capa['Plot_Value'] = df_capa[capa_col] * 100

    fig_capa = px.line(
        df_capa,
        x=df_capa.columns[0],
        y='Plot_Value',
        markers=True,
        text='Plot_Value',
        title="CAPA % On Time"
    )

    fig_capa.update_traces(
        texttemplate="%{text:.0f}%",
        textposition="top center"
    )
    
    fig_capa.update_yaxes(range=[0, 100], tickformat=".0f")

    c2.plotly_chart(fig_capa, use_container_width=True)

# =====================================================
# TAB 3 - HOUSEKEEPING
# =====================================================
with tab3:

    st.subheader("Housekeeping Status")



    hk_data = (

        df_2026.groupby(

            ["Department", "Status"]

        )

        .size()

        .reset_index(name="Count")

    )



    fig_hk = px.bar(

        hk_data,

        x="Department",

        y="Count",

        color="Status",

        text="Count",

        barmode="group",

        title="Housekeeping Status"

    )



    fig_hk.update_traces(

        textposition="outside"

    )



    st.plotly_chart(

        fig_hk,

        use_container_width=True

    )

# =====================================================
# TAB 4 - SAFE OBSERVATIONS
# =====================================================
with tab4:
    st.subheader("Safe Observations Tracking")

    # Display Metrics with Context
    c1, c2, c3 = st.columns(3)
    c1.metric("Leadership Obs", 91, delta="+4 vs last week")
    c2.metric("GS Obs", 177, delta="-2 vs last week")
    c3.metric("HSEQ Obs", 146, delta="+12 vs last week")

    st.markdown("---")
# =====================================================
# TAB 5 - RISK MITIGATION
# =====================================================
with tab5:
    st.subheader("Risk Mitigation")
    risk_df = data["Risk_Mitigation"]
    status_counts = risk_df['Status'].value_counts()

    def display_metric(label, value, color):
        st.markdown(
            f"""
            <div style="background-color: {color}; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;">
                {label}<br><span style="font-size: 24px;">{value}</span>
            </div>
            """, unsafe_allow_html=True
        )

    cols = st.columns(6)
    with cols[0]: display_metric("Completed On Time", status_counts.get("Completed On Time", 0),"#7aeb7a")
    with cols[1]: display_metric("In Draft", status_counts.get("In Draft", 0),"#28a745")
    with cols[2]: display_metric("In Review", status_counts.get("In Review", 0), "#F6BE00" )
    with cols[3]: display_metric("Completed Late", status_counts.get("Completed Late", 0), "#FF4500")
    with cols[4]: display_metric("Rejected", status_counts.get("Rejected", 0), "#dc3545")
    with cols[5]: display_metric("Draft Overdue", status_counts.get("Draft Overdue", 0), "#D3d3d3")

    st.markdown("---")

    edited_risk_df = st.data_editor(
        risk_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=["Completed On Time", "In Draft", "Rejected", "In Review", "Completed Late", "Draft Overdue"],
                required=True
            )
        }
    )
