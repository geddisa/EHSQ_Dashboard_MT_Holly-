import streamlit as st
import pandas as pd
import plotly.express as px

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
# Create two columns: a smaller one for the logo and a larger one for the title
header_left, header_right = st.columns([1, 4])

with header_left:
    # Adjust width as needed to fit perfectly on your screen
    st.image("century_logo.png", use_container_width=True)

with header_right:
    # Left-aligned to sit cleanly next to the brand logo
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
            "IncidentReports_All_MTH_2026-07-14.xlsx",
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
    barmode="group" # This puts the bars side-by-side
)

# Force the labels to appear on top of each individual bar
fig_dept.update_traces(
    textposition="outside", 
    texttemplate="%{text}"
)

col2.plotly_chart(
    fig_dept,
    use_container_width=True
)

# -----------------------------------------
    # Incident Severity Graph
    # -----------------------------------------
    st.subheader("Incident Severity Trend")

    # Prepare data from the already loaded 'data' dictionary
    df_incidents = data["Incidents"].copy()
    df_incidents['Date of Incident (UTC)'] = pd.to_datetime(df_incidents['Date of Incident (UTC)'])
    df_incidents['Week'] = df_incidents['Date of Incident (UTC)'].dt.isocalendar().week

    severity_mapping = {
        'Property Damage': 25,
        'Record Only - No Treatment': 50,
        'First Aid': 75,
        'Molten Metal Spill > 25 lbs': 150,
        'Molten Metal Explosion (Force 2 or 3)': 150,
        'Other Recordable Case': 250,
        'Restricted or Transferred Work': 250,
        'Days Away From Work': 350,
        'Recordable - Fatality': 600 
    }

    df_incidents['Points'] = df_incidents['Injury Classification'].map(severity_mapping).fillna(
        df_incidents['Type'].map(severity_mapping)
    ).fillna(0) 

    weekly_scores = df_incidents.groupby('Week')['Points'].sum()
    current_week = pd.Timestamp.now().isocalendar().week
    weekly_scores = weekly_scores.reindex(range(1, current_week + 1), fill_value=0)

    # Plotting
    fig, ax = plt.subplots(figsize=(14, 6)) 
    low_zone_upper, med_zone_upper, y_max = 400, 800, 1250
    
    ax.axhspan(0, low_zone_upper, color='lightgreen', alpha=0.4, label='Low Risk Zone (0-400)')
    ax.axhspan(low_zone_upper, med_zone_upper, color='khaki', alpha=0.4, label='Medium Risk Zone (401-800)')
    ax.axhspan(med_zone_upper, y_max, color='lightcoral', alpha=0.4, label='High Risk Zone (800+)')

    ax.plot(weekly_scores.index, weekly_scores.values, color='black', linewidth=2.5, marker='o', markersize=6, label='Weekly Severity Total')

    # Legend Sidebar logic omitted for brevity in snippet; 
    # you can include the legend logic here as defined in your provided script.

    ax.set_title('Incident Severity Graph', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Calendar Week Number')
    ax.set_ylabel('Total Accumulated Severity Points')
    ax.set_ylim(0, y_max)
    ax.set_xticks(range(1, current_week + 1))
    ax.legend(loc='upper left')

    # Display the plot in Streamlit
    st.pyplot(fig)
# =====================================================
# TAB 2 - COMPLIANCE
# =====================================================
with tab2:
    st.subheader("Compliance & Reporting Trends")

    c1, c2 = st.columns(2)

    # -----------------------------------------
    # FSI Trend
    # -----------------------------------------
    # Create a local copy to avoid modifying the original data
    df_fsi = data["FSI"].copy()
    
    # Identify the column name
    fsi_col = df_fsi.columns[4]
    
    # Convert column to numeric to handle any unexpected text/formatting
    df_fsi[fsi_col] = pd.to_numeric(df_fsi[fsi_col], errors='coerce')
    
    # Create a temporary column for the chart (0-100 scale)
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
    # Create a local copy to avoid modifying the original data
    df_capa = data["CAPAs"].copy()
    
    # Identify the column name
    capa_col = df_capa.columns[4]
    
    # Convert column to numeric to handle any unexpected text/formatting
    df_capa[capa_col] = pd.to_numeric(df_capa[capa_col], errors='coerce')
    
    # Create a temporary column for the chart (0-100 scale)
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

    c1, c2, c3 = st.columns(3)

    c1.metric("Leadership Obs", 91)
    c2.metric("GS Obs", 177)
    c3.metric("HSEQ Obs", 146)

    # -----------------------------------------
    # Trend Data Preparation
    # -----------------------------------------
    def prepare_trend_data(df, category):

        week_cols = [
            c for c in df.columns
            if "Week" in str(c)
        ]

        if not week_cols:
            return pd.DataFrame(
                columns=["Week", "Count", "Category"]
            )

        trend = (
            df[week_cols]
            .apply(
                pd.to_numeric,
                errors="coerce"
            )
            .sum()
            .reset_index()
        )

        trend.columns = [
            "Week",
            "Count"
        ]

        trend["Count"] = (
            trend["Count"]
            .fillna(0)
        )

        trend["Category"] = category

        return trend

    leadership_trend = prepare_trend_data(
        data["Lead_Obs"],
        "Leadership"
    )

    gs_trend = prepare_trend_data(
        data["GS_Obs"],
        "GS"
    )

    hseq_trend = prepare_trend_data(
        data["HSEQ_Obs"],
        "HSEQ"
    )

    df_trends = pd.concat(
        [
            leadership_trend,
            gs_trend,
            hseq_trend
        ],
        ignore_index=True
    )

    fig_obs = px.line(
        df_trends,
        x="Week",
        y="Count",
        color="Category",
        markers=True,
        text="Count",
        title="Weekly Observation Trends"
    )

    fig_obs.update_traces(
        mode="lines+markers+text",
        textposition="top center",
        connectgaps=True
    )

    fig_obs.update_layout(
        hovermode="x unified",
        legend_title="Observation Type"
    )

    st.plotly_chart(
        fig_obs,
        use_container_width=True
    )
    
# =====================================================
# TAB 5 - RISK MITIGATION
# =====================================================
with tab5:
    st.subheader("Risk Mitigation")
    
    risk_df = data["Risk_Mitigation"]
    
    # 1. Calculate counts for each status
    # We use .get() with 0 to handle cases where a status might not exist in the data
    status_counts = risk_df['Status'].value_counts()
    
    # Define mapping for colors (using HTML/CSS colors for style)
    # Note: Streamlit's st.metric doesn't have a direct 'color' param, 
    # so we use markdown and CSS for custom coloring.
    
    def display_metric(label, value, color):
        st.markdown(
            f"""
            <div style="background-color: {color}; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;">
                {label}<br><span style="font-size: 24px;">{value}</span>
            </div>
            """, unsafe_allow_html=True
        )

    # 2. Display the counters in a row
    cols = st.columns(6)
    with cols[0]: display_metric("Completed On Time", status_counts.get("Completed On Time", 0), "#28a745") # Green
    with cols[1]: display_metric("In Draft", status_counts.get("In Draft", 0), "#fd7e14") # Orange
    with cols[2]: display_metric("Rejected", status_counts.get("Rejected", 0), "#dc3545") # Red
    with cols[3]: display_metric("In Review", status_counts.get("In Review", 0), "#17a2b8") # Light Blue
    with cols[4]: display_metric("Completed Late", status_counts.get("Completed Late", 0), "#f8d7da") # Light Red (text will be dark if needed)
    with cols[5]: display_metric("Draft Overdue", status_counts.get("Draft Overdue", 0), "#6c757d") # Gray (added for completeness)

    st.markdown("---") # Divider

    # 3. Display the editor
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
