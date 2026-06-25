
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
        st.warning("Upload all 3 files")
        st.stop()

    inc = pd.read_excel(inc_file)
    near = pd.read_excel(near_file)
    risk = pd.read_excel(risk_file)

    for df in [inc, near, risk]:
        df.columns = df.columns.str.strip()

    inc["Date"] = pd.to_datetime(inc["Date of Incident (Local Plant Time)"], errors="coerce")
    near["Date"] = pd.to_datetime(near["Date of Near Miss (Local Plant Time)"], errors="coerce")
    risk["Date"] = pd.to_datetime(risk["Date Risk Identified (Local Plant Time)"], errors="coerce")

    return inc, near, risk


# =========================================
# SEVERITY (EXACT)
# =========================================
def severity_chart(df):

    mapping = {
        'Property Damage': 25,
        'Record Only - No Treatment': 50,
        'First Aid': 75,
        'Other Recordable Case': 250,
        'Restricted or Transferred Work': 250,
        'Days Away From Work': 350,
        'Recordable - Fatality': 600
    }

    df["Points"] = df["Injury Classification"].map(mapping).fillna(0)
    df["Week"] = df["Date"].dt.isocalendar().week

    weekly = df.groupby("Week")["Points"].sum().reset_index()

    fig = go.Figure()

    fig.add_hrect(y0=0, y1=400, fillcolor="lightgreen", opacity=0.4)
    fig.add_hrect(y0=400, y1=800, fillcolor="khaki", opacity=0.4)
    fig.add_hrect(y0=800, y1=1250, fillcolor="lightcoral", opacity=0.4)

    fig.add_trace(go.Scatter(x=weekly["Week"], y=weekly["Points"], mode="lines+markers"))

    fig.update_layout(title="Severity Trend")

    return fig


# =========================================
# MAIN
# =========================================
def main():

    st.title("📊 EHSQ EXECUTIVE DASHBOARD")

    # Uploads
    inc_file = st.sidebar.file_uploader("Incidents", type=["xlsx"])
    near_file = st.sidebar.file_uploader("Near Miss", type=["xlsx"])
    risk_file = st.sidebar.file_uploader("Risk Notifications", type=["xlsx"])

    inc, near, risk = load_data(inc_file, near_file, risk_file)

    # =========================================
    # 🔥 EXECUTIVE KPIs (TOP ROW)
    # =========================================
    st.subheader("Executive KPIs")

    total_inc = len(inc)
    severe = inc["Injury Classification"].astype(str).str.contains("Days Away|Fatality").sum()
    recordable = inc["Injury Classification"].astype(str).str.contains("Recordable|Days Away").sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Incidents", total_inc)
    c2.metric("Severe Incidents", severe)
    c3.metric("Recordables", recordable)

    # =========================================
    # 🔥 INCIDENT TREND
    # =========================================
    st.subheader("Incident Trend")

    trend = inc.groupby(inc["Date"].dt.to_period("M")).size().reset_index(name="Count")
    trend["Date"] = trend["Date"].dt.to_timestamp()

    st.plotly_chart(px.line(trend, x="Date", y="Count"))

    # =========================================
    # 🔥 INJURY CLASSIFICATION
    # =========================================
    st.subheader("Injury Classification")

    class_df = inc["Injury Classification"].value_counts().reset_index()
    class_df.columns = ["Type", "Count"]

    st.plotly_chart(px.bar(class_df, x="Type", y="Count"))

    # =========================================
    # 🔥 HAZARD TYPE
    # =========================================
    st.subheader("Hazard Type")

    haz_df = inc["Hazard Type"].value_counts().reset_index()
    haz_df.columns = ["Hazard", "Count"]

    st.plotly_chart(px.bar(haz_df, x="Hazard", y="Count"))

    # =========================================
    # 🔥 DEPARTMENT BREAKDOWN
    # =========================================
    st.subheader("Department Breakdown")

    dept_df = inc["Department"].value_counts().reset_index()
    dept_df.columns = ["Dept", "Count"]

    st.plotly_chart(px.bar(dept_df, x="Dept", y="Count"))

    # =========================================
    # 🔥 SEVERITY GRAPH
    # =========================================
    st.plotly_chart(severity_chart(inc), use_container_width=True)

    # =========================================
    # 🔥 RISK TRACKER
    # =========================================
    st.subheader("Risk Mitigation Tracker")

    status = risk["Status"].astype(str).str.lower()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Completed", status.str.contains("completed").sum())
    c2.metric("In Progress", status.str.contains("review").sum())
    c3.metric("Resolved", status.str.contains("completed on time").sum())
    c4.metric("Needs Info", status.str.contains("draft|overdue").sum())

    # =========================================
    # 🔥 INCIDENT TYPE
    # =========================================
    st.subheader("Incident Type")

    type_df = inc["Type"].value_counts().reset_index()
    type_df.columns = ["Type", "Count"]

    st.plotly_chart(px.bar(type_df, x="Type", y="Count"))

    # =========================================
    # 🔥 NEAR MISS + OBSERVATIONS
    # =========================================
    st.subheader("Observations")

    c1, c2 = st.columns(2)
    c1.metric("Near Miss Count", len(near))
    c2.metric("Risk Notifications", len(risk))


# RUN
if __name__ == "__main__":
    main()
