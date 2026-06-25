import streamlit as st
import pandas as pd
import plotly.express as px
import glob

st.set_page_config(page_title="EHSQ Dashboard", layout="wide")
st.title("Comprehensive EHSQ KPI Dashboard")

# --- Helper to load all CSVs ---
@st.cache_data
def load_data():
    files = glob.glob("*.csv")
    data = {f.replace("EHSQ Metrics.xlsx - ", "").replace(".csv", ""): pd.read_csv(f) for f in files}
    return data

data = load_data()

# --- Tab Navigation ---
tab1, tab2, tab3 = st.tabs(["Safety & Incidents", "Performance Metrics", "Compliance & CAPAs"])

with tab1:
    st.header("Safety Performance")
    # TCIR & DART Trend
    df_tcir = data.get("TCIR and DART")
    if df_tcir is not None:
        fig1 = px.line(df_tcir, x='Month', y=['TCIR Actual', 'DART Actual'], 
                       markers=True, title="TCIR & DART Trends", text_auto='.2f')
        st.plotly_chart(fig1, use_container_width=True)

    # Severity Ratings
    df_sev = data.get("Overall Severity Ratings")
    if df_sev is not None:
        st.subheader("Severity Distribution")
        st.dataframe(df_sev.head(10), use_container_width=True)

with tab2:
    st.header("Observations & Housekeeping")
    # Safe Observations
    df_obs = data.get("Safe Observations")
    if df_obs is not None:
        fig2 = px.bar(df_obs, x='Unnamed: 0', y='% Completed', 
                      title="Safe Observation Completion %", text_auto='.0%')
        st.plotly_chart(fig2, use_container_width=True)

    # Housekeeping
    df_house = data.get("Housekeeping")
    if df_house is not None:
        fig3 = px.line(df_house, x='Unnamed: 0', y='Average Plant Score', 
                       title="Housekeeping Scores", markers=True, text_auto='.2f')
        st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.header("CAPA & Compliance")
    # CAPAs
    df_capa = data.get("CAPAs")
    if df_capa is not None:
        fig4 = px.bar(df_capa, x='Unnamed: 0', y='% On Time', 
                      title="CAPA On-Time Performance", text_auto='.0%')
        st.plotly_chart(fig4, use_container_width=True)

    # Environmental
    df_env = data.get("Environmental Compliance Issues")
    if df_env is not None:
        st.subheader("Environmental Issues")
        st.bar_chart(df_env.set_index('2026 Environmental Compliance Issues')['# of Reported Compliance Issues'])
