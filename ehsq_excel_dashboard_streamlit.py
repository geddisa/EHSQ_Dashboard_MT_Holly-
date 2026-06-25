
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# =========================================
# LOAD DATA (NO UPLOADS)
# =========================================
def load_data():

    inc = pd.read_excel("IncidentReports_All_MTH_2026-06-25.xlsx")
    metrics = pd.read_excel("EHSQ Metrics.xlsx", sheet_name=None)

    inc.columns = inc.columns.str.strip()

    inc["Date"] = pd.to_datetime(
        inc["Date of Incident (Local Plant Time)"], errors="coerce"
    )

    return inc, metrics


# =========================================
# SEVERITY CHART
# =========================================
def severity_chart(df):

    mapping = {
        'Property Damage': 25,
        'Record Only-No Treatment': 50,
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

    fig.add_hrect(y0=0, y1=400, fillcolor="lightgreen", opacity=0.3)
    fig.add_hrect(y0=400, y1=800, fillcolor="khaki", opacity=0.3)
    fig.add_hrect(y0=800, y1=1500, fillcolor="lightcoral", opacity=0.3)

    fig.add_trace(
        go.Scatter(
            x=weekly["Week"],
            y=weekly["Points"],
            mode="lines+markers",
            name="Severity"
        )
    )

    fig.update_layout(title="Severity Trend")

    return fig


# =========================================
# TCIR / DART CHART
# =========================================
def tcir_chart(metrics):

    df = metrics["TCIR and DART"].copy()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["Month"], y=df["TCIR Actual"],
        name="TCIR Actual"
    ))

    fig.add_trace(go.Scatter(
        x=df["Month"], y=df["TCIR Target"],
        name="TCIR Target",
        line=dict(dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=df["Month"], y=df["DART Actual"],
        name="DART Actual"
    ))

    fig.add_trace(go.Scatter(
        x=df["Month"], y=df["DART Target"],
        name="DART Target",
        line=dict(dash="dash")
    ))

    fig.update_layout(title="TCIR & DART Trend")

    return fig


# =========================================
# MAIN APP
# =========================================
def main():

    st.title("📊 EHSQ EXECUTIVE DASHBOARD")

    # ✅ AUTO LOAD FILES
    inc, metrics = load_data()

    # =========================================
    # KPI SECTION
    # =========================================
    st.subheader("Executive KPIs")

    total_inc = len(inc)

    severe = inc["Injury Classification"].astype(str).str.contains(
        "Days Away|Fatality", case=False
    ).sum()

    recordable = inc["Injury Classification"].astype(str).str.contains(
        "Recordable|Days Away", case=False
    ).sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Incidents", total_inc)
    c2.metric("Severe Incidents", severe)
    c3.metric("Recordables", recordable)

    # =========================================
    # INCIDENT TREND
    # =========================================
    st.subheader("Incident Trend")

    trend = inc.groupby(
        inc["Date"].dt.to_period("M")
    ).size().reset_index(name="Count")

    trend["Date"] = trend["Date"].dt.to_timestamp()

    st.plotly_chart(
        px.line(trend, x="Date", y="Count"),
        use_container_width=True
    )

    # =========================================
    # INJURY CLASSIFICATION
    # =========================================
    st.subheader("Injury Classification")

    class_df = inc["Injury Classification"].value_counts().reset_index()
    class_df.columns = ["Type", "Count"]

    st.plotly_chart(
        px.bar(class_df, x="Type", y="Count"),
        use_container_width=True
    )

    # =========================================
    # HAZARD TYPE
    # =========================================
    st.subheader("Hazard Type")

    haz_df = inc["Hazard Type"].value_counts().reset_index()
    haz_df.columns = ["Hazard", "Count"]

    st.plotly_chart(
        px.bar(haz_df, x="Hazard", y="Count"),
        use_container_width=True
    )

    # =========================================
    # DEPARTMENT BREAKDOWN
    # =========================================
    st.subheader("Department Breakdown")

    dept_df = inc["Department"].value_counts().reset_index()
    dept_df.columns = ["Dept", "Count"]

    st.plotly_chart(
        px.bar(dept_df, x="Dept", y="Count"),
        use_container_width=True
    )

    # =========================================
    # SEVERITY
    # =========================================
    st.plotly_chart(
        severity_chart(inc),
        use_container_width=True
    )

    # =========================================
    # TCIR / DART
    # =========================================
    st.subheader("TCIR & DART Performance")

    st.plotly_chart(
        tcir_chart(metrics),
        use_container_width=True
    )

    # =========================================
    # CAPA PERFORMANCE
    # =========================================
    st.subheader("CAPA Performance")

    capa = metrics["CAPAs"]

    if "% On Time" in capa.columns:
        st.plotly_chart(
            px.line(capa, x="CAPAs", y="% On Time"),
            use_container_width=True
        )

    # =========================================
    # FSI PERFORMANCE
    # =========================================
    st.subheader("FSI Reports Performance")

    fsi = metrics["FSI Reports"]

    if "% On Time" in fsi.columns:
        st.plotly_chart(
            px.line(fsi, x="FSI Reports", y="% On Time"),
            use_container_width=True
        )


# RUN APP
if __name__ == "__main__":
    main()
