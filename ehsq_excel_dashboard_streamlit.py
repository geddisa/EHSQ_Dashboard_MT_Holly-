
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# =========================================
# LOAD DATA
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

    # Dates
    incidents["Date"] = pd.to_datetime(
        incidents.get("Date of Incident (Local Plant Time)"),
        errors="coerce"
    )
    near["Date"] = pd.to_datetime(
        near.get("Date of Near Miss (Local Plant Time)"),
        errors="coerce"
    )
    risk["Date"] = pd.to_datetime(
        risk.get("Date Risk Identified (Local Plant Time)"),
        errors="coerce"
    )

    incidents["Source"] = "Incident"
    near["Source"] = "Near Miss"
    risk["Source"] = "Risk Notification"

    return incidents, near, risk


# =========================================
# INSIGHTS
# =========================================
def generate_insights(df):

    if df.empty:
        return "No data available."

    total = len(df)
    high = df["Risk Level"].astype(str).str.contains("high", case=False).sum()
    overdue = df["Status"].astype(str).str.contains("overdue", case=False).sum()

    high_pct = round((high / total) * 100, 1)
    overdue_pct = round((overdue / total) * 100, 1)

    text = f"""
### 📊 Key Insights

• {high_pct}% HIGH risk  
• {overdue_pct}% overdue  

"""

    if high_pct > 25:
        text += "🔴 High exposure — attention needed\n"
    else:
        text += "🟢 Risk controlled\n"

    if overdue_pct > 20:
        text += "🔴 Action delays present\n"
    else:
        text += "🟢 Actions on track\n"

    return text


# =========================================
# ✅ EXACT SEVERITY GRAPH (YOUR LOGIC)
# =========================================
def severity_graph(df):

    df = df.copy()

    severity_mapping = {
        'Property Damage': 25,
        'Record Only - No Treatment': 50,
        'First Aid': 75,
        'Molten Metal Spill > 25 lbs': 150,
        'Molten Metal Explosion (Force 2 or 3)': 150,
        'Other Recordable Case': 250,
        'Restricted or Transferred Work': 250,
        'Days Away From Work': 350,
        'Recordable - Fatality': 600
    }

    # ✅ SAME fallback logic as your file
    df["Points"] = (
        df["Injury Classification"].map(severity_mapping)
        .fillna(df["Type"].map(severity_mapping))
        .fillna(0)
    )

    df["Week"] = df["Date"].dt.isocalendar().week

    weekly = df.groupby("Week")["Points"].sum()

    current_week = 24  # SAME concept as your script
    weekly = weekly.reindex(range(1, current_week + 1), fill_value=0)

    weekly = weekly.reset_index()
    weekly.columns = ["Week", "Points"]

    # ✅ PLOTLY VERSION (matches your matplotlib zones)
    fig = go.Figure()

    # Zones
    fig.add_hrect(y0=0, y1=400, fillcolor="lightgreen", opacity=0.4)
    fig.add_hrect(y0=400, y1=800, fillcolor="khaki", opacity=0.4)
    fig.add_hrect(y0=800, y1=1250, fillcolor="lightcoral", opacity=0.4)

    # Line
    fig.add_trace(go.Scatter(
        x=weekly["Week"],
        y=weekly["Points"],
        mode="lines+markers",
        line=dict(color="black", width=3),
        marker=dict(size=6)
    ))

    fig.update_layout(
        title="Incident Severity Graph",
        xaxis_title="Week",
        yaxis_title="Severity Points",
        yaxis=dict(range=[0, 1250], dtick=200),
        xaxis=dict(dtick=1)
    )

    return fig


# =========================================
# MAIN
# =========================================
def main():

    st.title("📊 EHSQ EXECUTIVE DASHBOARD")

    # Upload
    st.sidebar.header("📂 Upload Files")
    inc_file = st.sidebar.file_uploader("Incident Reports", type=["xlsx"])
    near_file = st.sidebar.file_uploader("Near Miss", type=["xlsx"])
    risk_file = st.sidebar.file_uploader("Risk Notifications", type=["xlsx"])

    incidents, near, risk = load_data(inc_file, near_file, risk_file)

    combined = pd.concat([risk, near, incidents], ignore_index=True)

    # FILTERS
    st.sidebar.header("🔎 Filters")

    dept = st.sidebar.multiselect("Department", combined["Department"].dropna().unique())
    source = st.sidebar.multiselect("Source", combined["Source"].unique())

    if dept:
        combined = combined[combined["Department"].isin(dept)]

    if source:
        combined = combined[combined["Source"].isin(source)]

    # TABS
    tab1, tab2, tab3 = st.tabs([
        "🚨 Overview",
        "📈 Trends",
        "⚠️ Risk Tracker"
    ])

    # OVERVIEW
    with tab1:

        c1, c2, c3 = st.columns(3)
        c1.metric("Risks", len(combined[combined["Source"] == "Risk Notification"]))
        c2.metric("Near Miss", len(combined[combined["Source"] == "Near Miss"]))
        c3.metric("Incidents", len(combined[combined["Source"] == "Incident"]))

        # Funnel
        funnel = pd.DataFrame({
            "Stage": ["Risk", "Near Miss", "Incident"],
            "Count": [
                len(risk),
                len(near),
                len(incidents)
            ]
        })

        st.plotly_chart(px.funnel(funnel, x="Count", y="Stage"))

        # ✅ SEVERITY GRAPH (EXACT)
        st.plotly_chart(severity_graph(incidents), use_container_width=True)

        st.markdown(generate_insights(combined))

    # TRENDS
    with tab2:

        df_trend = combined.dropna(subset=["Date"]).copy()
        df_trend["Month"] = df_trend["Date"].dt.to_period("M").dt.to_timestamp()

        trend = df_trend.groupby(["Month", "Source"]).size().reset_index(name="Count")

        st.plotly_chart(
            px.line(trend, x="Month", y="Count", color="Source", markers=True),
            use_container_width=True
        )

    # RISK TRACKER
    with tab3:

        status = combined["Status"].astype(str).str.lower()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Completed", status.str.contains("completed").sum())
        c2.metric("In Progress", status.str.contains("review").sum())
        c3.metric("Resolved", status.str.contains("completed on time").sum())
        c4.metric("Needs Info", status.str.contains("draft|overdue").sum())


if __name__ == "__main__":
    main()
