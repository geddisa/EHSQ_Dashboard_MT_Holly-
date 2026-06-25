import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

# =========================================
# LOAD DATA
# =========================================
@st.cache_data
def load_data():
    incidents = pd.read_excel("IncidentReports_All_MTH_2026-06-25.xlsx", engine="openpyxl")
    near = pd.read_excel("NearMisses_All_MTH_2026-06-25.xlsx", engine="openpyxl")
    risk = pd.read_excel("RiskNotifications_All_MTH_2026-06-25.xlsx", engine="openpyxl")

    for df in [incidents, near, risk]:
        df.columns = [str(c).strip() for c in df.columns]

    # Dates
    incidents["Date"] = pd.to_datetime(incidents.get("Date of Incident (Local Plant Time)"), errors="coerce")
    near["Date"] = pd.to_datetime(near.get("Date of Near Miss (Local Plant Time)"), errors="coerce")
    risk["Date"] = pd.to_datetime(risk.get("Date Risk Identified (Local Plant Time)"), errors="coerce")

    # Add Source
    incidents["Source"] = "Incident"
    near["Source"] = "Near Miss"
    risk["Source"] = "Risk Notification"

    return incidents, near, risk


# =========================================
# EXECUTIVE INSIGHTS
# =========================================
def generate_insights(df):

    total = len(df)

    high = df["Risk Level"].astype(str).str.contains("high", case=False).sum()
    overdue = df["Status"].astype(str).str.contains("overdue", case=False).sum()

    if total == 0:
        return "No data available."

    high_pct = round((high / total) * 100, 1)
    overdue_pct = round((overdue / total) * 100, 1)

    insight = f"""
    • {high_pct}% of reported items are HIGH risk  
    • {overdue_pct}% of actions are overdue or delayed  

    """

    if high_pct > 25:
        insight += "🔴 Elevated risk exposure detected — leadership attention required.\n"
    else:
        insight += "🟢 Risk levels are within acceptable range.\n"

    if overdue_pct > 20:
        insight += "🔴 Action completion delays present — follow-up needed.\n"
    else:
        insight += "🟢 Action tracking performing well.\n"

    return insight


# =========================================
# MAIN
# =========================================
def main():

    st.title("📊 EHSQ EXECUTIVE DASHBOARD")

    incidents, near, risk = load_data()

    # =========================================
    # COMBINED DATA
    # =========================================
    combined = pd.concat([
        risk,
        near,
        incidents
    ], ignore_index=True)

    # =========================================
    # 🔥 FILTERS (Power BI Style)
    # =========================================
    st.sidebar.header("🔎 Filters")

    dept = st.sidebar.multiselect(
        "Department",
        options=sorted(combined["Department"].dropna().unique()),
        default=None
    )

    source = st.sidebar.multiselect(
        "Source",
        options=combined["Source"].unique(),
        default=None
    )

    risk_level = st.sidebar.multiselect(
        "Risk Level",
        options=combined["Risk Level"].dropna().unique(),
        default=None
    )

    # Apply filters
    if dept:
        combined = combined[combined["Department"].isin(dept)]

    if source:
        combined = combined[combined["Source"].isin(source)]

    if risk_level:
        combined = combined[combined["Risk Level"].isin(risk_level)]

    # =========================================
    # TABS
    # =========================================
    tab1, tab2, tab3 = st.tabs([
        "🚨 Executive Overview",
        "📈 Trends",
        "⚠️ Risk Mitigation"
    ])

    # =========================================
    # 🚨 EXECUTIVE OVERVIEW
    # =========================================
    with tab1:

        st.subheader("Safety Pipeline")

        risk_count = len(combined[combined["Source"] == "Risk Notification"])
        near_count = len(combined[combined["Source"] == "Near Miss"])
        inc_count = len(combined[combined["Source"] == "Incident"])

        c1, c2, c3 = st.columns(3)
        c1.metric("⚠️ Risks", risk_count)
        c2.metric("⚡ Near Miss", near_count)
        c3.metric("🚨 Incidents", inc_count)

        # Funnel
        funnel = pd.DataFrame({
            "Stage": ["Risk", "Near Miss", "Incident"],
            "Count": [risk_count, near_count, inc_count]
        })

        fig = px.funnel(funnel, x="Count", y="Stage")
        st.plotly_chart(fig, use_container_width=True)

        # ✅ EXECUTIVE INSIGHTS
        st.subheader("📢 Executive Insights")

        st.markdown(generate_insights(combined))

    # =========================================
    # 📈 TRENDS
    # =========================================
    with tab2:

        st.subheader("Trend Over Time")

        df_trend = combined.dropna(subset=["Date"]).copy()
        df_trend["Month"] = df_trend["Date"].dt.to_period("M").dt.to_timestamp()

        trend = df_trend.groupby(["Month", "Source"]).size().reset_index(name="Count")

        fig = px.line(trend, x="Month", y="Count", color="Source", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    # =========================================
    # ⚠️ RISK MITIGATION
    # =========================================
    with tab3:

        st.subheader("Risk Status Breakdown")

        status = combined["Status"].astype(str).str.lower()

        completed = status.str.contains("completed").sum()
        in_progress = status.str.contains("review|progress").sum()
        resolved = status.str.contains("completed on time").sum()
        need_info = status.str.contains("draft|overdue").sum()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("✅ Completed", completed)
        c2.metric("⏳ In Progress", in_progress)
        c3.metric("✔️ Resolved", resolved)
        c4.metric("❗ Needs Info", need_info)

        # Distribution
        st.subheader("Status Distribution")
        dist = combined["Status"].value_counts().reset_index()
        dist.columns = ["Status", "Count"]

        fig = px.bar(dist, x="Status", y="Count", text="Count")
        st.plotly_chart(fig, use_container_width=True)

        # Open trend
        st.subheader("Open Risk Trend")

        open_df = combined[status.str.contains("draft|review")].copy()
        open_df["Month"] = open_df["Date"].dt.to_period("M").dt.to_timestamp()

        trend = open_df.groupby("Month").size().reset_index(name="Open Items")

        fig = px.line(trend, x="Month", y="Open Items", markers=True)
        st.plotly_chart(fig, use_container_width=True)


# RUN
if __name__ == "__main__":
    main()
