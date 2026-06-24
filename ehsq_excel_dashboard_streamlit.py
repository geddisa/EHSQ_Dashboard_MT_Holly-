import pandas as pd
import streamlit as st
import plotly.express as px

# =========================
# SETTINGS
# =========================
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

        # Clean columns
        df.columns = df.columns.astype(str).str.strip()

        # Replace problematic values (important for Plotly)
        df = df.replace({pd.NA: None})

        return df

    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        return pd.DataFrame()


# =========================
# SAFE PLOT FUNCTION
# =========================
def safe_plot(fig, title="Chart"):
    try:
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ {title} failed to render: {e}")


# =========================
# MAIN
# =========================
def main():

    st.title("📊 EHSQ Performance Dashboard")

    # Upload
    uploaded = st.sidebar.file_uploader("Upload Incident File", type=["xlsx"])

    df = load_data(uploaded)

    if df.empty:
        st.warning("⚠️ No data loaded.")
        return

    # =========================
    # PREPROCESSING
    # =========================
    if "Date of Incident (Local Plant Time)" in df.columns:
        df["Date"] = pd.to_datetime(
            df["Date of Incident (Local Plant Time)"],
            errors="coerce"
        )

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
    # KPI CARDS
    # =========================
    st.subheader("🚦 Key Performance Indicators")

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Incidents", len(df))
    c2.metric("Severe Incidents", int(df["High Risk"].sum()))
    c3.metric("Recordables", int(df["Recordable"].sum()))

    # =========================
    # INCIDENT TREND (FIXED)
    # =========================
    st.subheader("📈 Incidents Over Time")

    if "Date" in df.columns:
        trend_df = df.dropna(subset=["Date"]).copy()

        # ✅ FIX: Convert Period → Timestamp
        trend_df["Month"] = trend_df["Date"].dt.to_period("M").dt.to_timestamp()

        trend = trend_df.groupby("Month").size().reset_index(name="Count")

        if not trend.empty:
            fig = px.line(trend, x="Month", y="Count", markers=True)
            safe_plot(fig, "Trend Chart")

    # =========================
    # BREAKDOWNS
    # =========================
    st.subheader("📊 Breakdown Analysis")

    col1, col2 = st.columns(2)

    if "Injury Classification" in df.columns:
        with col1:
            fig = px.histogram(df, x="Injury Classification", title="Injury Classification")
            safe_plot(fig, "Injury Classification")

    if "Hazard Type" in df.columns:
        with col2:
            fig = px.histogram(df, x="Hazard Type", title="Hazard Type")
            safe_plot(fig, "Hazard Type")

    col3, col4 = st.columns(2)

    if "Type" in df.columns:
        with col3:
            fig = px.histogram(df, x="Type", title="Incident Type")
            safe_plot(fig, "Incident Type")

    if "Department" in df.columns:
        with col4:
            fig = px.histogram(df, x="Department", title="Department")
            safe_plot(fig, "Department")

    # =========================
    # TOP RISKS
    # =========================
    st.subheader("⚠️ Top Risk Factors")

    if "Risk Factor" in df.columns:
        risk_df = df["Risk Factor"].fillna("Unknown").value_counts().head(10).reset_index()
        risk_df.columns = ["Risk Factor", "Count"]

        fig = px.bar(
            risk_df.sort_values("Count"),
            x="Count",
            y="Risk Factor",
            orientation="h"
        )

        safe_plot(fig, "Top Risk Factors")

    # =========================
    # INSIGHTS PANEL
    # =========================
    st.subheader("🧠 Key Insights")

    st.info("""
    • High frequency of **Line of Fire, Mobile Equipment, and Heat Stress incidents**
    • Most injuries affect **hands, fingers, and lower body**
    • Repeated patterns indicate **systemic hazard exposure**
    • Environmental risks include **air quality, spills, and chemical events**
    • Recordable injuries are affecting operational performance (DART impact)
    """)

    # =========================
    # FULL TABLE
    # =========================
    st.subheader("📋 Full Incident Data")

    st.dataframe(df, use_container_width=True)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()
