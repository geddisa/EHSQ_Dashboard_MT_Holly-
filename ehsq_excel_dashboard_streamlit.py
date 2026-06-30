import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")
st.title("EHSQ Performance Dashboard")

FILE_PATH = "EHSQ Metrics.xlsx"
INCIDENT_PATH = "IncidentReports_All_MTH_2026-06-25.xlsx"

@st.cache_data
def load_all_data():
    return {
        "Incidents": pd.read_excel(INCIDENT_PATH),
        "TCIR": pd.read_excel(FILE_PATH, sheet_name="TCIR and DART", header=1),
        "Housekeeping": pd.read_excel(FILE_PATH, sheet_name="Housekeeping", skiprows=2),
        "CAPAs": pd.read_excel(FILE_PATH, sheet_name="CAPAs", skiprows=2),
        "Observations": pd.read_excel(FILE_PATH, sheet_name="Safe Observations", header=0),
        "Environmental": pd.read_excel(FILE_PATH, sheet_name="Environmental Compliance Issues", header=0),
        "Other": pd.read_excel(FILE_PATH, sheet_name="Other Reports", skiprows=2),
        "FSI": pd.read_excel(FILE_PATH, sheet_name="FSI Reports", skiprows=2),
        "Severity": pd.read_excel(FILE_PATH, sheet_name="Overall Severity Ratings", skiprows=8)
    }

data = load_all_data()
df = data["Incidents"]

# Prepare Date/Week
df['Date of Incident (UTC)'] = pd.to_datetime(df['Date of Incident (UTC)'])
df['Year'] = df['Date of Incident (UTC)'].dt.year
df['Week'] = df['Date of Incident (UTC)'].dt.isocalendar().week
df_2026 = df[df['Year'] == 2026].copy()

# Risk Mitigation Mapping
def map_risk(status):
    if status in ['Completed On Time', 'Completed Late']: return 'Completed'
    if status in ['In Draft', 'In Review']: return 'In Progress'
    if status == 'Resolved in Place': return 'Resolved in Place'
    return 'Need More Information'

df['Cat'] = df['Status'].apply(map_risk)
counts = df['Cat'].value_counts()

# Helper for Safe Observations
def get_safe_obs(df, col):
    return df[col].sum() if col in df.columns else 0

tabs = st.tabs(["Dashboard Overview", "Risk Mitigation", "Core Metrics", "Data Explorer"])

with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Incidents (2026)", len(df_2026))
    c2.metric("Avg Housekeeping", f"{data['Housekeeping']['Average Plant Score'].mean():.2%}")
    c3.metric("CAPA On-Time", f"{data['CAPAs']['% On Time'].mean():.2%}")
    c4.metric("Completed Risks", int(counts.get("Completed", 0)))
    st.divider()
    
    r1, r2, r3 = st.columns(3)
    with r1:
        st.subheader("Incident Count by Type")
        st.bar_chart(df_2026['Type'].value_counts())
    with r2:
        st.subheader("Safety Metrics")
        st.write(f"**Near Misses:** {len(df_2026[df_2026['Type'] == 'Near Miss'])}")
        st.write(f"**Visa Notifications:** {len(df_2026[df_2026['Type'] == 'Visa Notification'])}")
        obs = data['Observations']
        st.write(f"**Safe Observations:**")
        st.write(f"- Leadership: {get_safe_obs(obs, 'Leadership')}")
        st.write(f"- 6S: {get_safe_obs(obs, '6S')}")
        st.write(f"- HSEQ (excl. Madai): {get_safe_obs(obs, 'HSEQ') - get_safe_obs(obs, 'Madai')}")
    with r3:
        st.subheader("Status on Risk Mitigation")
        st.write(f"**Total Identified:** {len(df)}")
        st.write(f"**Completed:** {int(counts.get('Completed', 0))}")
        st.write(f"**In Progress:** {int(counts.get('In Progress', 0))}")
        st.write(f"**Need More Info:** {int(counts.get('Need More Information', 0))}")
    
    st.divider()
    st.subheader("Incident Severity Trend (2026)")
    # Logic: map based on specific columns
    sev_map = {'Property Damage': 25, 'First Aid': 75, 'Days Away From Work': 350, 'Recordable - Fatality': 600}
    df_2026['Points'] = df_2026['Injury Classification'].map(sev_map).fillna(0)
    w_scores = df_2026.groupby('Week')['Points'].sum().reindex(range(1, df_2026['Week'].max() + 1), fill_value=0)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(w_scores.index, w_scores.values, marker='o', color='black')
    ax.axhline(400, color='red', linestyle='--')
    for i, v in zip(w_scores.index, w_scores.values):
        ax.text(i, v + 5, str(int(v)), ha='center', fontsize=8)
    st.pyplot(fig)

with tabs[1]:
    st.subheader("Risk Mitigation Tracker")
    edited_df = st.data_editor(df[['Incident', 'Status', 'Department', 'Description']], use_container_width=True)
    if st.button("Save Changes"):
        try:
            with pd.ExcelWriter(INCIDENT_PATH, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                edited_df.to_excel(writer, sheet_name='Incidents', index=False)
            st.success("Saved!")
        except Exception as e: st.error(f"Save Failed: {e}")

with tabs[2]:
    col_a, col_b = st.columns(2)
    with col_a: st.plotly_chart(px.line(data["TCIR"], x='Month', y=['TCIR Actual', 'DART Actual']), use_container_width=True)
    with col_b: st.plotly_chart(px.bar(data["CAPAs"], x=data["CAPAs"].columns[0], y='% On Time'), use_container_width=True)

with tabs[3]:
    sel = st.selectbox("Select Sheet", list(data.keys()))
    st.dataframe(data[sel], use_container_width=True)
