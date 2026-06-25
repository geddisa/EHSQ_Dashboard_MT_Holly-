
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

# =========================================
# LOAD DATA (UPLOAD VERSION ✅ FIXED)
# =========================================
def load_data(inc_file, near_file, risk_file):

    if inc_file is None or near_file is None or risk_file is None:
        st.warning("📂 Please upload ALL three files to continue.")
        st.stop()

    incidents = pd.read_excel(inc_file, engine="openpyxl")
    near = pd.read_excel(near_file, engine="openpyxl")
    risk = pd.read_excel(risk_file, engine="openpyxl")

    for df in [incidents, near, risk]:
        df.columns = [str(c).strip() for c in df.columns]

    # ✅ SAFE DATE HANDLING
    incidents["Date"] = pd.to_datetime(
        incidents.get("Date of Incident (Local Plant Time)"), errors="coerce"
    )
    near["Date"] = pd.to_datetime(
        near.get("Date of Near Miss (Local Plant Time)"), errors="coerce"
    )
    risk["Date"] = pd.to_datetime(
        risk.get("Date Risk Identified (Local Plant Time)"), errors="coerce"
    )

    # ✅ ADD SOURCE
    incidents["Source"] = "Incident"
    near["Source"] = "Near Miss"
    risk["Source"] = "Risk Notification"

    return incidents, near, risk


# =========================================
# EXECUTIVE INSIGHTS ENGINE ✅
# =========================================
def generate_insights(df):

    if df.empty:
        return "No data available."

    total = len(df)

    high = df["Risk Level"].astype(str).str.contains("high", case=False).sum()
    overdue = df["Status"].astype(str).str.contains("overdue", case=False).sum()

    high_pct = round((high / total) * 100, 1)
    overdue_pct = round((overdue / total) * 100, 1)

    insight = f"""
### 📊 Key Insights

• **{high_pct}%** of records are HIGH risk  
• **{overdue_pct}%** of actions are overdue  

"""

    if high_pct > 25:
        insight += "🔴 High risk exposure detected — leadership action recommended.\n"
    else:
        insight += "🟢 Risk levels are controlled.\n"

    if overdue_pct > 20:
        insight += "🔴 Delays in action completion — follow-up required.\n"
    else:
        insight += "🟢 Action closure performance is strong.\n"

    return insight


# =========================================
# MAIN APP
# =========================================
def main():

    st.title("📊 EHSQ EXECUTIVE DASHBOARD")

    # =========================================
    # 📂 FILE UPLOAD (THIS FIXES YOUR ERROR)
    # =========================================
    st.sidebar.header("📂 Upload Data")

    inc_file = st.sidebar.file_uploader("Incident Reports", type=["xlsx"])
    near_file = st.sidebar.file_uploader("Near Miss Reports", type=["xlsx"])
    risk_file = st.sidebar.file_uploader("Risk Notifications", type=["xlsx"])

    incidents, near, risk = load_data(inc_file, near_file, risk_file)

    # =========================================
    # COMBINE ALL DATA
    # =========================================
    combined = pd.concat([risk, near, incidents], ignore_index=True)

    # =========================================
    # 🔎 FILTERS (EXECUTIVE SLICERS)
    # =========================================
    st.sidebar.header("🔎 Filters")

    dept = st.sidebar.multiselect(
        "Department",
        options=sorted(combined["Department"].dropna().unique())
    )

    source = st.sidebar.multiselect(
        "Source",
        options=combined["Source"].unique()
    )

    risk_level = st.sidebar.multiselect(
        "Risk Level",
        options=combined["Risk Level"].dropna().unique()
    )

    # APPLY FILTERS
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

        st.subheader("Safety Pipeline Overview")

        risk_count = len(combined[combined["Source"] == "Risk Notification"])
        near_count = len(combined[combined["Source"] == "Near Miss"])
        inc_count = len(combined[combined["Source"] == "Incident"])

        c1, c2, c3 = st.columns(3)
        c1.metric("⚠️ Risks", risk_count)
        c2.metric("⚡ Near Misses", near_count)
        c3.metric("🚨 Incidents", inc_count)

        # FUNNEL
        funnel = pd.DataFrame({
            "Stage": ["Risk Notifications", "Near Misses", "Incidents"],
            "Count": [risk_count, near_count, inc_count]
        })

        fig = px.funnel(funnel, x="Count", y="Stage")
        st.plotly_chart(fig, use_container_width=True)

        # ✅ EXECUTIVE INSIGHTS
        st.markdown(generate_insights(combined))

    # =========================================
    # 📈 TRENDS
    # =========================================
    with tab2:

        st.subheader("Trend Analysis")

        df_trend = combined.dropna(subset=["Date"]).copy()

        if not df_trend.empty:
            df_trend["Month"] = df_trend["Date"].dt.to_period("M").dt.to_timestamp()

            trend = df_trend.groupby(["Month", "Source"]).size().reset_index(name="Count")

            fig = px.line(trend, x="Month", y="Count", color="Source", markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No valid date data available for trend.")

    # =========================================
    # ⚠️ RISK MITIGATION
    # =========================================
    with tab3:

        st.subheader("Risk Mitigation Tracker")

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

        # STATUS DISTRIBUTION
        st.subheader("Status Distribution")

        dist = combined["Status"].value_counts().reset_index()
        dist.columns = ["Status", "Count"]

        fig = px.bar(dist, x="Status", y="Count", text="Count")
        st.plotly_chart(fig, use_container_width=True)

        # OPEN TREND
        st.subheader("Open Risk Trend")

        open_df = combined[status.str.contains("draft|review")].copy()

        if not open_df.empty:
            open_df["Month"] = open_df["Date"].dt.to_period("M").dt.to_timestamp()

            trend = open_df.groupby("Month").size().reset_index(name="Open Items")

            fig = px.line(trend, x="Month", y="Open Items", markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No open risks found.")

# =========================================
# RUN APP ✅
# =========================================
if __name__ == "__main__":
    main()
