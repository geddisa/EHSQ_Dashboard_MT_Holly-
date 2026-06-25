
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

# ===================================
# LOAD DATA
# ===================================
@st.cache_data
def load_data():
    incidents = pd.read_excel("IncidentReports_All_MTH_2026-06-25.xlsx")
    near = pd.read_excel("NearMisses_All_MTH_2026-06-25.xlsx")
    risk = pd.read_excel("RiskNotifications_All_MTH_2026-06-25.xlsx")

    # Clean columns
    for df in [incidents, near, risk]:
        df.columns = [str(c).strip() for c in df.columns]

    # Convert dates
    incidents["Date"] = pd.to_datetime(incidents["Date of Incident (Local Plant Time)"], errors="coerce")
    near["Date"] = pd.to_datetime(near["Date of Near Miss (Local Plant Time)"], errors="coerce")
    risk["Date"] = pd.to_datetime(risk["Date Risk Identified (Local Plant Time)"], errors="coerce")

    return incidents, near, risk


# ===================================
# MAIN
# ===================================
def main():

    st.title("📊 EHSQ Executive Dashboard")

    incidents, near, risk = load_data()

    tab1, tab2, tab3 = st.tabs([
        "🚨 Executive Overview",
        "📈 Performance",
        "⚠️ Risk Mitigation Tracker"
    ])

    # ===================================
    # 🚨 EXECUTIVE OVERVIEW
    # ===================================
    with tab1:

        st.subheader("Enterprise Safety Pipeline")

        total_risk = len(risk)
        total_near = len(near)
        total_inc = len(incidents)

        c1, c2, c3 = st.columns(3)

        c1.metric("⚠️ Risks Identified", total_risk)
        c2.metric("⚡ Near Misses", total_near)
        c3.metric("🚨 Incidents", total_inc)

        st.markdown("### 📉 Exposure Funnel")

        funnel = pd.DataFrame({
            "Stage": ["Risk Notifications", "Near Misses", "Incidents"],
            "Count": [total_risk, total_near, total_inc]
        })

        fig = px.funnel(funnel, x="Count", y="Stage")
        st.plotly_chart(fig, use_container_width=True)

    # ===================================
    # 📈 PERFORMANCE (SMART INSIGHTS)
    # ===================================
    with tab2:

        st.subheader("Trend Comparison")

        def make_trend(df, date_col):
            d = df.dropna(subset=[date_col]).copy()
            d["Month"] = d[date_col].dt.to_period("M").dt.to_timestamp()
            return d.groupby("Month").size().reset_index(name="Count")

        inc_trend = make_trend(incidents, "Date")
        near_trend = make_trend(near, "Date")
        risk_trend = make_trend(risk, "Date")

        fig = px.line()
        fig.add_scatter(x=risk_trend["Month"], y=risk_trend["Count"], name="Risks")
        fig.add_scatter(x=near_trend["Month"], y=near_trend["Count"], name="Near Miss")
        fig.add_scatter(x=inc_trend["Month"], y=inc_trend["Count"], name="Incidents")

        st.plotly_chart(fig, use_container_width=True)

    # ===================================
    # ⚠️ RISK MITIGATION TRACKER (FULLY INTEGRATED)
    # ===================================
    with tab3:

        st.subheader("Unified Risk Mitigation")

        # Combine ALL systems
        risk["Source"] = "Risk"
        near["Source"] = "Near Miss"
        incidents["Source"] = "Incident"

        combined = pd.concat([
            risk[["Status", "Date", "Source"]],
            near[["Status", "Date", "Source"]],
            incidents[["Status", "Date", "Source"]]
        ])

        combined["Status"] = combined["Status"].astype(str).str.lower()

        # ✅ EXECUTIVE BUCKETS
        completed = combined["Status"].str.contains("completed").sum()
        in_progress = combined["Status"].str.contains("review|progress").sum()
        resolved = combined["Status"].str.contains("completed on time").sum()
        need_info = combined["Status"].str.contains("draft|overdue").sum()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("✅ Completed", completed)
        c2.metric("⏳ In Progress", in_progress)
        c3.metric("✔️ Resolved", resolved)
        c4.metric("❗ Needs Info", need_info)

        # ===================================
        # SOURCE BREAKDOWN
        # ===================================
        st.subheader("Source Contribution")

        fig = px.histogram(combined, x="Source", color="Source")
        st.plotly_chart(fig, use_container_width=True)

        # ===================================
        # STATUS DISTRIBUTION
        # ===================================
        st.subheader("Status Distribution")

        status_counts = combined["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        fig = px.bar(status_counts, x="Status", y="Count", text="Count")
        st.plotly_chart(fig, use_container_width=True)

        # ===================================
        # OPEN RISK TREND
        # ===================================
        st.subheader("Open Risk Trend")

        open_items = combined[combined["Status"].str.contains("draft|review")]

        open_items["Month"] = open_items["Date"].dt.to_period("M").dt.to_timestamp()

        trend = open_items.groupby("Month").size().reset_index(name="Open Items")

        fig = px.line(trend, x="Month", y="Open Items", markers=True)
        st.plotly_chart(fig, use_container_width=True)


# RUN
if __name__ == "__main__":
    main()
