import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 

# --- DASHBOARD SETUP ---
st.set_page_config(layout="wide", page_title="MT. Holly | EHSQ KPI Dashboard")

col_logo, col_title = st.columns([1, 6], vertical_alignment="center")
with col_logo:
    try:
        st.image("Company_Logo.png", width=200)
    except:
        st.write("Logo missing")
with col_title:
    st.markdown("<h1 style='margin-bottom: 0; padding-top: 0;'>EHSQ KPI Dashboard</h1>", unsafe_allow_html=True)

# --- NO-CACHE DATA LOADING ---
def load_all_data():
    files = {
        "Incidents": ("IncidentReports_All_MTH_2026-07-01.xlsx", "Sheet1", 0),
        "FSI": ("EHSQ Metrics.xlsx", "FSI Reports", 1),
        "CAPAs": ("EHSQ Metrics.xlsx", "CAPAs", 1),
        "Lead_Obs": ("Audit Schedule - Internal - LPA.xlsx", "Safe Obs - Leadership", 0),
        "GS_Obs": ("Audit Schedule - Internal - LPA.xlsx", "Safe Obs - GS and EHS", 0),
        "HSEQ_Obs": ("Audit Schedule - Internal - LPA.xlsx", "Safe Obs GS EHS", 0)
    }
    data = {}
    for key, (file, sheet, skip) in files.items():
        data[key] = pd.read_excel(file, sheet_name=sheet, skiprows=skip)
    return data

try:
    data = load_all_data()
except Exception as e:
    st.error(f"Error loading files: {e}. Ensure the Excel files are in the same folder.")
    st.stop()

# --- MAIN DASHBOARD LOGIC ---
df_raw = data["Incidents"].copy()
df_raw['Date'] = pd.to_datetime(df_raw['Date of Incident (UTC)'], errors='coerce')
df_raw = df_raw.dropna(subset=['Date'])
df_2026 = df_raw[df_raw['Date'].dt.year == 2026].copy()

tabs = st.tabs(["Overview", "Compliance", "Housekeeping", "Safe Observations", "Risk Mitigation"])

with tabs[0]: 
    st.subheader("Incident Breakdown")
    col1, col2 = st.columns(2)
    
    type_counts = df_2026.groupby('Type').size().reset_index(name='Count')
    fig = px.bar(type_counts, x='Type', y='Count', title="Incidents by Type", text='Count')
    fig.update_traces(texttemplate='%{text}', textposition='outside', textangle=0) 
    col1.plotly_chart(fig, use_container_width=True)
    
    dept_counts = df_2026.groupby(['Department', 'Type']).size().reset_index(name='Count')
    fig_dept = px.bar(dept_counts, x='Department', y='Count', color='Type', title="Incidents by Department", text='Count')
    fig_dept.update_traces(textangle=0, textposition='outside')
    col2.plotly_chart(fig_dept, use_container_width=True)
    
    st.divider()
    st.subheader("Incident Severity Analysis")
    
    df_severity = df_2026.copy()
    df_severity['Week'] = df_severity['Date'].dt.isocalendar().week
    severity_mapping = {
        'Property Damage': 25, 'Record Only - No Treatment': 50, 'First Aid': 75, 
        'Molten Metal Spill > 25 lbs': 150, 'Molten Metal Explosion (Force 2 or 3)': 150, 
        'Other Recordable Case': 250, 'Restricted or Transferred Work': 250, 
        'Days Away From Work': 350, 'Recordable - Fatality': 600
    }
    df_severity['Points'] = df_severity['Injury Classification'].map(severity_mapping).fillna(df_severity['Type'].map(severity_mapping)).fillna(0)
    weekly_scores = df_severity.groupby('Week')['Points'].sum().reset_index()
    
    current_week = pd.Timestamp.now().isocalendar().week
    all_weeks = pd.DataFrame({'Week': range(1, current_week + 1)})
    weekly_scores = pd.merge(all_weeks, weekly_scores, on='Week', how='left').fillna(0)
    
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0.5, y0=0, x1=current_week + 0.5, y1=400, fillcolor="lightgreen", opacity=0.4, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=0.5, y0=400, x1=current_week + 0.5, y1=800, fillcolor="khaki", opacity=0.4, layer="below", line_width=0)
    fig.add_shape(type="rect", x0=0.5, y0=800, x1=current_week + 0.5, y1=1200, fillcolor="lightcoral", opacity=0.4, layer="below", line_width=0)
    fig.add_annotation(x=1, y=200, text="Low Risk", showarrow=False, font=dict(color="green", size=14, weight="bold"))
    fig.add_annotation(x=1, y=600, text="Medium Risk", showarrow=False, font=dict(color="goldenrod", size=14, weight="bold"))
    fig.add_annotation(x=1, y=1000, text="High Risk", showarrow=False, font=dict(color="red", size=14, weight="bold"))
    fig.add_trace(go.Scatter(x=weekly_scores['Week'], y=weekly_scores['Points'], mode='lines+markers', name='Weekly Severity Total', line=dict(color='black', width=3)))
    fig.update_layout(title="Incident Severity Graph", xaxis=dict(title="Calendar Week Number", tickmode='linear', dtick=1), yaxis=dict(title="Total Accumulated Severity Points", range=[0, 1250]), showlegend=True, plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; border: 1px solid #ddd;">
        <p style="margin: 0; font-weight: bold;">Severity Point Mapping:</p>
        <ul style="margin: 0; padding-left: 20px;">
            <li><b>25 pt:</b> Property Damage</li>
            <li><b>50 pt:</b> Record Only - No Treatment</li>
            <li><b>75 pt:</b> First Aid</li>
            <li><b>150 pt:</b> Molten Metal Spill > 25 lbs / Molten Metal Explosion (Force 2 or 3)</li>
            <li><b>250 pt:</b> Other Recordable Case / Restricted or Transferred Work</li>
            <li><b>350 pt:</b> Days Away From Work</li>
            <li><b>600 pt:</b> Recordable - Fatality</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
with tabs[1]: 
    st.subheader("Compliance & Reporting Trends")
    c1, c2 = st.columns(2)
    
    fsi_df = data["FSI"]
    fig_fsi = px.line(fsi_df, x=fsi_df.columns[0], y=fsi_df.columns[4], title="FSI % On Time", markers=True, text=fsi_df.columns[4])
    fig_fsi.update_traces(texttemplate='%{text:.0%}', textposition='top center')
    fig_fsi.update_yaxes(tickformat=".0%")
    fig_fsi.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Target 100%")
    c1.plotly_chart(fig_fsi, use_container_width=True)
    
    capa_df = data["CAPAs"]
    fig_capa = px.line(capa_df, x=capa_df.columns[0], y=capa_df.columns[4], title="CAPA % On Time", markers=True, text=capa_df.columns[4])
    fig_capa.update_traces(texttemplate='%{text:.0%}', textposition='top center')
    fig_capa.update_yaxes(tickformat=".0%")
    fig_capa.add_hline(y=0.8, line_dash="dash", line_color="red", annotation_text="Target 80%")
    c2.plotly_chart(fig_capa, use_container_width=True)
    
with tabs[2]: 
    st.subheader("Housekeeping Status")
    hk_data = df_2026.groupby(['Department', 'Status']).size().reset_index(name='Count')
    fig_hk = px.bar(hk_data, x='Department', y='Count', color='Status', barmode='group', text='Count')
    fig_hk.update_traces(texttemplate='%{text}', textposition='outside', textangle=0)
    st.plotly_chart(fig_hk, use_container_width=True)

with tabs[3]: 
    st.subheader("Safe Observations Tracking")

    # 1. Metrics - Totals as requested
    c1, c2, c3 = st.columns(3)
    c1.metric("Leadership Obs", 91)
    c2.metric("GS Obs", 177)
    c3.metric("HSEQ_Obs", 146)

    # 2. Trend Logic
    # We use a helper function to aggregate all numeric columns 
    # (assuming your weekly observation counts are numeric)
    def prepare_trend_data(df, category):
        # Select numeric columns only, excluding identifiers if necessary
        # If your data starts at column index 3, use .iloc[:, 3:]
        numeric_df = df.select_dtypes(include=['number'])
        trend = numeric_df.sum().reset_index()
        trend.columns = ['Week', 'Count']
        trend['Category'] = category
        return trend

    # Consolidate for Plotly
    df_obs_trend = pd.concat([
        prepare_trend_data(data["Lead_Obs"], "Leadership"),
        prepare_trend_data(data["GS_Obs"], "GS"),
        prepare_trend_data(data["HSEQ_Obs"], "HSEQ")
    ])

    # 3. Trend Chart
    fig_obs = px.line(
        df_obs_trend, 
        x="Week", 
        y="Count", 
        color="Category", 
        markers=True,
        title="2026 Weekly Observation Trends"
    )
    st.plotly_chart(fig_obs, use_container_width=True)
    
with tabs[4]: 
    st.subheader("Risk Mitigation Progress")
    st.markdown("""
        <style>
        .metric-box { padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 1.2em; }
        </style>
        <div style="display: flex; justify-content: space-around;">
            <div class="metric-box" style="color: #1f77b4;">Total Risk<br>259</div>
            <div class="metric-box" style="color: #2ca02c;">Completed<br>251</div>
            <div class="metric-box" style="color: #ff7f0e;">In Progress<br>3</div>
            <div class="metric-box" style="color: #d62728;">Need More Info<br>5</div>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    cols_to_display = ["Incident", "Assigned To", "Status", "Type", "Department", "Due Date", "Description"]
    df_filtered = df_raw[cols_to_display].copy()
    st.caption("Update Status Below:")
    st.data_editor(
        df_filtered, 
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status", 
                options=['Completed On Time', 'Completed Late', 'In Draft', 'In Review', 'Need Info'], 
                required=True
            )
        }, 
        hide_index=True, 
        use_container_width=True
    )
