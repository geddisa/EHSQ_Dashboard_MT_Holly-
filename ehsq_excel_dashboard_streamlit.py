import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
        # Load sheets. If your Excel file has a title row, add skiprows=1 here.
        return {
            "Incidents": clean_columns(pd.read_excel(incident_path, sheet_name="Sheet1")),
            "FSI": clean_columns(pd.read_excel(metrics_path, sheet_name="FSI Reports", skiprows=1)),
            "CAPAs": clean_columns(pd.read_excel(metrics_path, sheet_name="CAPAs", skiprows=1)),
            "TCIR": clean_columns(pd.read_excel(metrics_path, sheet_name="TCIR and DART", skiprows=1)),
            "Lead_Obs": clean_columns(pd.read_excel(audit_path, sheet_name="Safe Obs - Leadership")),
            "GS_Obs": clean_columns(pd.read_excel(audit_path, sheet_name="Safe Obs - GS and EHS")),
            "HSEQ_Obs": clean_columns(pd.read_excel(audit_path, sheet_name="Safe Obs GS EHS"))
        }
    except Exception as e:
        st.error(f"Error loading files: {e}")
        return None

data = load_all_data()

if data:
    df = data["Incidents"]
    
    # --- FIX: USE THE EXACT DATE COLUMN NAME ---
    # Based on your script, it is 'Date of Incident (UTC)'
    # If this fails, check your columns list by uncommenting the line below:
    # st.write(df.columns.tolist())
    
    date_col = 'Date of Incident (UTC)' 
    df['Date'] = pd.to_datetime(df[date_col], errors='coerce')
    
    # We only drop rows that are strictly NaT, but keep rows with valid data
    df = df.dropna(subset=['Date'])
    df['Week'] = df['Date'].dt.isocalendar().week

    tabs = st.tabs(["Overview", "Compliance", "Housekeeping", "Safe Observations", "Risk Mitigation"])

    with tabs[0]: 
        st.subheader("Incident Severity Tracking")
        
        # Severity Calculation
        severity_mapping = {
            'Property Damage': 25, 'Record Only - No Treatment': 50, 'First Aid': 75,
            'Molten Metal Spill > 25 lbs': 150, 'Molten Metal Explosion (Force 2 or 3)': 150,
            'Other Recordable Case': 250, 'Restricted or Transferred Work': 250,
            'Days Away From Work': 350, 'Recordable - Fatality': 600 
        }
        df['Points'] = df['Injury Classification'].map(severity_mapping).fillna(0)
        weekly_scores = df.groupby('Week')['Points'].sum().sort_index()

        fig = go.Figure()
        fig.add_hrect(y0=0, y1=400, fillcolor="lightgreen", opacity=0.3, line_width=0, annotation_text="Low Risk")
        fig.add_hrect(y0=400, y1=800, fillcolor="khaki", opacity=0.3, line_width=0, annotation_text="Medium Risk")
        fig.add_hrect(y0=800, y1=1250, fillcolor="lightcoral", opacity=0.3, line_width=0, annotation_text="High Risk")
        fig.add_trace(go.Scatter(x=weekly_scores.index, y=weekly_scores.values, mode='lines+markers', name='Severity Total', line=dict(color='black', width=3)))
        fig.update_layout(title="Incident Severity Graph", template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        type_counts = df.groupby('Type').size().reset_index(name='Count')
        col1.plotly_chart(px.bar(type_counts, x='Type', y='Count', title="Incidents by Type", text_auto='.0f'), use_container_width=True)
        
        dept_counts = df.groupby(['Department', 'Type']).size().reset_index(name='Count')
        st.plotly_chart(px.bar(dept_counts, x='Department', y='Count', color='Type', title="Incidents by Department & Type", barmode='group', text_auto='.0f'), use_container_width=True)

    with tabs[1]: 
        st.subheader("Compliance & Reporting Trends")
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.line(data["FSI"].dropna(subset=[data["FSI"].columns[4]]), x=data["FSI"].columns[0], y=data["FSI"].columns[4], title="FSI % On Time").add_hline(y=1.0, line_dash="dash", line_color="red"), use_container_width=True)
        c2.plotly_chart(px.line(data["CAPAs"].dropna(subset=[data["CAPAs"].columns[4]]), x=data["CAPAs"].columns[0], y=data["CAPAs"].columns[4], title="CAPA % On Time").add_hline(y=0.8, line_dash="dash", line_color="red"), use_container_width=True)

    with tabs[2]: 
        st.subheader("Housekeeping Status by Department")
        st.plotly_chart(px.bar(df.groupby(['Department', 'Status']).size().reset_index(name='Count'), x='Department', y='Count', color='Status', barmode='group', title="Status Tracking", text_auto='.0f'), use_container_width=True)

    with tabs[3]: 
        st.subheader("Safe Observations Tracking")
        c1, c2, c3 = st.columns(3)
        c1.metric("Leadership Obs", len(data["Lead_Obs"]))
        c2.metric("GS Obs", len(data["GS_Obs"]))
        hseq_df = data["HSEQ_Obs"]
        c3.metric("HSEQ Obs (Excl. Maddi)", len(hseq_df[hseq_df['Auditor_Name'] != 'Maddi']))

    with tabs[4]: 
        st.subheader("Risk Mitigation Progress")
        total_risk = len(df)
        completed = len(df[df['Status'].isin(['Completed On Time', 'Completed Late'])])
        in_progress = len(df[df['Status'].isin(['In Draft', 'In Review'])])
        st.write("### Edit Incident Status")
        df_edit = st.data_editor(df, column_config={"Status": st.column_config.SelectboxColumn("Status", options=['Completed On Time', 'Completed Late', 'In Draft', 'In Review', 'Need Info'], required=True)}, hide_index=True, use_container_width=True)
