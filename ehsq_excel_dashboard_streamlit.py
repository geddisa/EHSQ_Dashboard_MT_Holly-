import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="EHSQ KPI Dashboard", layout="wide")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data(uploaded):
    try:
        if uploaded:
            df = pd.read_excel(uploaded, engine="openpyxl")
        else:
            df = pd.read_excel("IncidentReports_All_MTH_2026-06-18.xlsx", engine="openpyxl")

        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()


# =========================
# MAIN APP
# =========================
def main():

    st.title("📊 EHSQ Performance Dashboard")

    uploaded = st.sidebar.file_uploader("Upload Incident File", type=["xlsx"])
    df = load_data(uploaded)

    if df.empty:
        st.warning("No data loaded")
        return

    # =========================
    # PREPROCESSING
    # =========================
    if "Date of Incident (Local Plant Time)" in df.columns:
        df["Date"] = pd.to_datetime(df["Date of Incident (Local Plant Time)"], errors="coerce")

    if "Injury Classification" in df.columns:
        df["Recordable"] = df["Injury Classification"].isin([
            "Days Away From Work",
            "Restricted or Transferred Work",
            "Other Recordable Case"
        ])
    else:
        df["Recordable"] = False

    if "Risk Level" in df.columns:
        df["High Risk"] = df["Risk Level"].astype(str).str.lower().isin(["high", "major"])
    else:
        df["High Risk"] = False

    # =========================
    # KPI CARDS (TOP ROW)
    # =========================
    st.subheader("Key Performance Indicators")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Incidents", len(df))
    col2.metric("Severe Incidents", int(df["High Risk"].sum()))
    col3.metric("Recordables", int(df["Recordable"].sum()))

    # =========================
    # INCIDENT TREND
    # =========================
    st.subheader("Incidents Over Time")

    if "Date" in df.columns:
        trend = df.dropna(subset=["Date"]).groupby(df["Date"].dt.to_period("M")).size()
        trend = trend.reset_index(name="Count")

        fig = px.line(trend, x="Date", y="Count", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # BREAKDOWNS
    # =========================
    col1, col2 = st.columns(2)

    # Injury Classification
    if "Injury Classification" in df.columns:
        with col1:
            fig = px.histogram(df, x="Injury Classification", title="Injury Classification")
            st.plotly_chart(fig, use_container_width=True)

    # Hazard Type
    if "Hazard Type" in df.columns:
        with col2:
            fig = px.histogram(df, x="Hazard Type", title="Hazard Type")
            st.plotly_chart(fig, use_container_width=True)

    # =========================
    # INCIDENT TYPE + DEPARTMENT
    # =========================
    col3, col4 = st.columns(2)

    if "Type" in df.columns:
        with col3:
            fig = px.histogram(df, x="Type", title="Incident Type")
            st.plotly_chart(fig, use_container_width=True)

    if "Department" in df.columns:
        with col4:
            fig = px.histogram(df, x="Department", title="Department Breakdown")
            st.plotly_chart(fig, use_container_width=True)

    # =========================
    # TOP RISKS / HAZARDS
    # =========================
    st.subheader("Top Risks & Hazards")

    if "Risk Factor" in df.columns:
        risk_counts = df["Risk Factor"].value_counts().head(10).reset_index()
        risk_counts.columns = ["Risk Factor", "Count"]

        fig = px.bar(risk_counts.sort_values("Count"),
                     x="Count", y="Risk Factor",
                     orientation="h",
                     title="Top Risk Factors")

        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # KPI INSIGHT AREA
    # =========================
    st.subheader("AI Insights")

    st.info("""
    • Most incidents are driven by **Line of Fire, Mobile Equipment, and Heat Exposure**
    • Repeated injuries involve **hands, fingers, and lower body**
    • Heat stress and ergonomic injuries show recurring patterns
    • Environmental risks include **air, chemical, and spill-related incidents**
    • DART-related injuries indicate impacts to work capability
    """)

    # =========================
    # FULL TABLE
    # =========================
    st.subheader("Full Incident Data")

    st.dataframe(df, use_container_width=True)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()
