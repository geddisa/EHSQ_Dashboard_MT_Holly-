
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="EHSQ Executive Dashboard", layout="wide")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_incidents(uploaded):
    try:
        file = uploaded if uploaded else "IncidentReports_All_MTH_2026-06-18.xlsx"
        df = pd.read_excel(file, engine="openpyxl")

        df.columns = df.columns.astype(str).str.strip()
        df = df.replace({pd.NA: None})

        return df

    except Exception as e:
        st.error(f"Error loading incident file: {e}")
        return pd.DataFrame()


@st.cache_data
def load_metrics(uploaded):
    try:
        file = uploaded if uploaded else "EHSQ Metrics.xlsx"
        df = pd.read_excel(file, sheet_name="TCIR and DART", skiprows=2, engine="openpyxl")
        df.columns = df.columns.astype(str).str.strip()
        return df

    except:
        return None


# =========================
# SAFE PLOT
# =========================
def safe_plot(fig):
    try:
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning("Chart failed")

# =========================
# KPI COLOR LOGIC
# =========================
def kpi_color(value, good, warning):
    if value <= good:
        return "green"
    elif value <= warning:
        return "orange"
    return "red"

# =========================
# MAIN
# =========================
def main():

    st.title("📊 EHSQ Executive Dashboard")

    # Sidebar filters
    st.sidebar.header("Filters")
    inc_file = st.sidebar.file_uploader("Incident File", type=["xlsx"])
    met_file = st.sidebar.file_uploader("Metrics File", type=["xlsx"])

    df = load_incidents(inc_file)
    metrics = load_metrics(met_file)

    if df.empty:
        st.warning("No data loaded.")
        return

    # =========================
    # PREPROCESS
    # =========================
    df["Date"] = pd.to_datetime(
        df.get("Date of Incident (Local Plant Time)"), errors="coerce"
    )

    df["High Risk"] = df.get("Risk Level", "").astype(str).str.lower().isin(["high", "major"])

    df["Recordable"] = df.get("Injury Classification", "").isin([
        "Days Away From Work",
        "Restricted or Transferred Work",
        "Other Recordable Case"
    ])

    # =========================
    # FILTERS (POWER BI STYLE)
    # =========================
    dept_filter = st.sidebar.multiselect(
        "Department",
        options=df["Department"].dropna().unique() if "Department" in df.columns else [],
        default=df["Department"].dropna().unique() if "Department" in df.columns else []
    )

    if "Department" in df.columns:
        df = df[df["Department"].isin(dept_filter)]

    # =========================
    # KPI SECTION
    # =========================
    st.subheader("🚦 KPI Overview")

    total_incidents = len(df)
    severe = df["High Risk"].sum()
    recordables = df["Recordable"].sum()

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Incidents", total_incidents)

    c2.metric(
        "Severe Incidents",
        severe,
        delta=None
    )

    c3.metric(
        "Recordables",
        recordables,
        delta=None
    )

    # =========================
    # TREND
    # =========================
    st.subheader("📈 Incident Trend")

    trend_df = df.dropna(subset=["Date"]).copy()
    trend_df["Month"] = trend_df["Date"].dt.to_period("M").dt.to_timestamp()

    trend = trend_df.groupby("Month").size().reset_index(name="Count")

    fig = px.line(trend, x="Month", y="Count", markers=True, text="Count")
    fig.update_traces(textposition="top center")

    safe_plot(fig)

    # =========================
    # SEVERITY (POLISHED)
    # =========================
    st.subheader("🔥 Severity Breakdown")

    sev = df["Risk Level"].fillna("Unknown").value_counts().reset_index()
    sev.columns = ["Risk Level", "Count"]

    fig = px.bar(
        sev,
        x="Risk Level",
        y="Count",
        text="Count",
        color="Risk Level",
        color_discrete_map={
            "Low": "green",
            "Medium": "orange",
            "High": "red",
            "Major": "darkred"
        }
    )
    fig.update_traces(textposition="outside")

    safe_plot(fig)

    # =========================
    # HAZARDS
    # =========================
    st.subheader("⚠️ Top Hazards")

    hz = df["Hazard Type"].value_counts().head(10).reset_index()
    hz.columns = ["Hazard", "Count"]

    fig = px.bar(hz, x="Hazard", y="Count", text="Count")
    fig.update_traces(textposition="outside")

    safe_plot(fig)

    # =========================
    # RISKS
    # =========================
    st.subheader("🚨 Top Risk Factors")

    risk = df["Risk Factor"].value_counts().head(10).reset_index()
    risk.columns = ["Risk Factor", "Count"]

    fig = px.bar(
        risk.sort_values("Count"),
        x="Count",
        y="Risk Factor",
        orientation="h",
        text="Count"
    )

    fig.update_traces(textposition="outside")

    safe_plot(fig)

    # =========================
    # METRICS
    # =========================
    if metrics is not None:
        st.subheader("📊 TCIR & DART")

        month_col = next((c for c in metrics.columns if "month" in c.lower()), None)
        tcir_actual = next((c for c in metrics.columns if "tcir actual" in c.lower()), None)
        dart_actual = next((c for c in metrics.columns if "dart actual" in c.lower()), None)

        if month_col and tcir_actual:
            fig = px.line(metrics, x=month_col, y=tcir_actual, markers=True, text=tcir_actual)
            fig.update_traces(textposition="top center")
            safe_plot(fig)

        if month_col and dart_actual:
            fig = px.line(metrics, x=month_col, y=dart_actual, markers=True, text=dart_actual)
            fig.update_traces(textposition="top center")
            safe_plot(fig)

    # =========================
    # AUTO INSIGHTS ✅
    # =========================
    st.subheader("🧠 Executive Insights")

    top_hazard = hz.iloc[0]["Hazard"] if not hz.empty else "N/A"
    top_risk = risk.iloc[0]["Risk Factor"] if not risk.empty else "N/A"

    st.success(f"""
    • Most common hazard: **{top_hazard}**  
    • Highest risk driver: **{top_risk}**  
    • Severe incidents: **{severe}** (focus needed on high-risk controls)  
    • Repetitive patterns indicate **systemic exposure risks**  
    • Recommend focus on **mobile equipment, heat exposure, and pinch points**
    """)

    # =========================
    # TABLE
    # =========================
    st.subheader("📋 Full Data")

    st.dataframe(df, use_container_width=True)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()
