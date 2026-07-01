import streamlit as st
import pandas as pd
import plotly.express as px

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
        # Loading directly from disk without caching
        data[key] = pd.read_excel(file, sheet_name=sheet, skiprows=skip)
    return data

# Load data without st.cache_data
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
    df_severity = df_raw.copy()
    df_severity['Week'] = df_severity['Date'].dt.isocalendar().week
    severity_mapping = {'Property Damage': 25, 'Record Only - No Treatment': 50, 'First Aid': 75, 'Molten Metal Spill > 25 lbs': 150, 'Molten Metal Explosion (Force 2 or 3)': 150, 'Other Recordable Case': 250, 'Restricted or Transferred Work': 250, 'Days Away From Work': 350, 'Recordable - Fatality': 600}
    df_severity['Points'] = df_severity['Injury Classification'].map(severity_mapping).fillna(df_severity['Type'].map(severity_mapping)).fillna(0)
    weekly_scores = df_severity.groupby('Week')['Points'].sum().reset_index()
    current_week = pd.to_datetime('2026-06-09').isocalendar().week
    all_weeks = pd.DataFrame({'Week': range(1, current_week + 1)})
    weekly_scores = pd.merge(all_weeks, weekly_scores, on='Week', how='left').fillna(0)
    fig_severity = px.line(weekly_scores, x='Week', y='Points', title="Weekly Incident Severity Score", markers=True)
    st.plotly_chart(fig_severity, use_container_width=True)

with tabs[1]: 
    st.subheader("Compliance & Reporting Trends")
    c1, c2 = st.columns(2)
    
    # --- FSI Chart ---
    fsi_df = data["FSI"]
    fig_fsi = px.line(
        fsi_df, 
        x=fsi_df.columns[0], 
        y=fsi_df.columns[4], 
        title="FSI % On Time", 
        markers=True,
        text=fsi_df.columns[4]
    )
    fig_fsi.update_traces(texttemplate='%{text:.0%}', textposition='top center')
    # Update Y-axis to show whole number percentages
    fig_fsi.update_yaxes(tickformat=".0%")
    fig_fsi.add_hline(y=1.0, line_dash="dash", line_color="red", annotation_text="Target 100%")
    c1.plotly_chart(fig_fsi, use_container_width=True)
    
    # --- CAPA Chart ---
    capa_df = data["CAPAs"]
    fig_capa = px.line(
        capa_df, 
        x=capa_df.columns[0], 
        y=capa_df.columns[4], 
        title="CAPA % On Time", 
        markers=True,
        text=capa_df.columns[4]
    )
    fig_capa.update_traces(texttemplate='%{text:.0%}', textposition='top center')
    # Update Y-axis to show whole number percentages
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
    c1, c2, c3 = st.columns(3)
    c1.metric("Leadership Obs", len(data["Lead_Obs"]))
    c2.metric("GS Obs", len(data["GS_Obs"]))
    c3.metric("HSEQ_Obs", len(data["HSEQ_Obs"]))
        
with tabs[4]: 
    st.subheader("Risk Mitigation Progress")
    
    # 1. Calculate Metrics
    total_risk = len(df_raw)
    completed = len(df_raw[df_raw['Status'].isin(['Completed On Time', 'Completed Late'])])
    in_progress = len(df_raw[df_raw['Status'].isin(['In Draft', 'In Review'])])
    need_info = max(0, total_risk - (completed + in_progress))
    
    # 2. Display Metric Columns
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Risk", total_risk)
    m2.metric("Completed", completed)
    m3.metric("In Progress", in_progress)
    m4.metric("Need More Info", need_info)
    
    st.divider()
    
    # 3. Donut Chart Visualization
    c1, c2 = st.columns([1, 2])
    
    # Prepare data for the pie/donut chart
    chart_data = pd.DataFrame({
        'Category': ['Completed', 'In Progress', 'Need More Info'],
        'Value': [completed, in_progress, need_info]
    })
    
    fig_donut = px.pie(
        chart_data, 
        values='Value', 
        names='Category', 
        hole=0.5,
        title="Risk Mitigation Distribution",
        color='Category',
        color_discrete_map={'Completed': '#2ca02c', 'In Progress': '#1f77b4', 'Need More Info': '#d62728'}
    )
    fig_donut.update_traces(textinfo='percent+value')
    c1.plotly_chart(fig_donut, use_container_width=True)
    
    # 4. Interactive Editor
    with c2:
        st.caption("Update Status Below:")
        st.data_editor(
            df_raw, 
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
