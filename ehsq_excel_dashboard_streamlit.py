
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="EHSQ Executive Dashboard", layout="wide")

# =========================================
# 🎯 STYLING
# =========================================
st.markdown("""
<style>
body {background-color: #f4f6f9;}

.card {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 15px;
}

.kpi-green {color: green; font-weight: bold;}
.kpi-yellow {color: orange; font-weight: bold;}
.kpi-red {color: red; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# =========================================
# LOAD DATA
# =========================================
@st.cache_data
def load_incidents(file):
    file = file if file else "IncidentReports_All_MTH_2026-06-18.xlsx"
    df = pd.read_excel(file, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]
    df["Date"] = pd.to_datetime(df.get("Date of Incident (Local Plant Time)"), errors="coerce")
    return df


@st.cache_data
def load_metrics(file):
    file = file if file else "EHSQ Metrics.xlsx"
    tcir = pd.read_excel(file, sheet_name="TCIR and DART", engine="openpyxl")
    fsi = pd.read_excel(file, sheet_name="FSI Reports", engine="openpyxl")
    capas = pd.read_excel(file, sheet_name="CAPAs", engine="openpyxl")
    return tcir, fsi, capas


# =========================================
# KPI COLOR LOGIC
# =========================================
def kpi_color(value, target):
    if value >= target:
        return "kpi-green"
    elif value >= target * 0.8:
        return "kpi-yellow"
    else:
        return "kpi-red"


# =========================================
# MAIN
# =========================================
def main():

    st.title("📊 EHSQ Executive Dashboard")

    inc_file = st.sidebar.file_uploader("Incident File", type=["xlsx"])
    met_file = st.sidebar.file_uploader("Metrics File", type=["xlsx"])

    df = load_incidents(inc_file)
    tcir, fsi, capas = load_metrics(met_file)

    tab1, tab2, tab3 = st.tabs([
        "🚨 Incident Overview",
        "📈 Performance Metrics",
        "⚠️ Risk Mitigation"
    ])

    # ======================================================
    # 🚨 INCIDENT TAB
    # ======================================================
    with tab1:

        st.subheader("Executive KPIs")

        total = len(df)
        severe = df.get("Risk Level","").astype(str).str.contains("high|major", case=False).sum()
        recordable = df.get("Injury Classification","").isin([
            "Days Away From Work",
            "Restricted or Transferred Work",
            "Other Recordable Case"
        ]).sum()

        c1, c2, c3 = st.columns(3)

        c1.markdown(f"<div class='card'><h3>Total Incidents</h3><h1>{total}</h1></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>Severe</h3><h1 class='{kpi_color(severe,5)}'>{severe}</h1></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Recordables</h3><h1 class='{kpi_color(recordable,3)}'>{recordable}</h1></div>", unsafe_allow_html=True)

        # ================= TREND
        st.subheader("Incident Trend")

        trend = df.dropna(subset=["Date"]).copy()
        trend["Month"] = trend["Date"].dt.to_period("M").dt.to_timestamp()
        trend = trend.groupby("Month").size().reset_index(name="Count")

        fig = px.line(trend, x="Month", y="Count", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # ================= SEVERITY (highlight)
        st.subheader("🔥 Severity (Executive Focus)")

        severity_mapping = {
            'Property Damage': 25,
            'Record Only - No Treatment': 50,
            'First Aid': 75,
            'Other Recordable Case': 250,
            'Restricted or Transferred Work': 250,
            'Days Away From Work': 350,
            'Recordable - Fatality': 600
        }

        df["Points"] = df["Injury Classification"].map(severity_mapping).fillna(0)
        df["Week"] = df["Date"].dt.isocalendar().week

        weekly = df.groupby("Week")["Points"].sum().reindex(range(1,25), fill_value=0).reset_index()
        weekly.columns = ["Week", "Points"]

        fig = go.Figure()
        fig.add_hrect(y0=0, y1=400, fillcolor="lightgreen", opacity=0.4)
        fig.add_hrect(y0=400, y1=800, fillcolor="khaki", opacity=0.4)
        fig.add_hrect(y0=800, y1=1250, fillcolor="lightcoral", opacity=0.4)

        fig.add_trace(go.Scatter(
            x=weekly["Week"],
            y=weekly["Points"],
            mode="lines+markers",
            line=dict(color="black", width=3)
        ))

        st.plotly_chart(fig, use_container_width=True)

    # ======================================================
    # 📈 METRICS TAB
    # ======================================================
    with tab2:

        st.subheader("TCIR & DART")

        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=tcir.iloc[:,0], y=tcir.iloc[:,1], name="TCIR Actual"))
            fig.add_trace(go.Scatter(x=tcir.iloc[:,0], y=tcir.iloc[:,2], name="TCIR Target"))
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.warning("TCIR format issue")

        # ================= FSI
        st.subheader("FSI Performance")

        fsi = fsi.dropna(how="all")
        cols = fsi.columns

        month = cols[0]
        on_time = next((c for c in cols if "On Time" in c and "%" not in c), None)
        percent = next((c for c in cols if "%" in c), None)

        if on_time:
            fig = px.bar(fsi, x=month, y=on_time)
            st.plotly_chart(fig, use_container_width=True)

        if percent:
            fig = px.line(fsi, x=month, y=percent)
            fig.add_hline(y=1)
            st.plotly_chart(fig, use_container_width=True)

        # ================= CAPA
        st.subheader("CAPA Performance")

        capas = capas.dropna(how="all")
        cols = capas.columns

        month = cols[0]
        on_time = next((c for c in cols if "On Time" in c and "%" not in c), None)
        percent = next((c for c in cols if "%" in c), None)

        if on_time:
            fig = px.bar(capas, x=month, y=on_time)
            st.plotly_chart(fig, use_container_width=True)

        if percent:
            fig = px.line(capas, x=month, y=percent)
            fig.add_hline(y=0.8)
            st.plotly_chart(fig, use_container_width=True)

    # ======================================================
    # ⚠️ RISK MITIGATION TAB
    # ======================================================
    with tab3:

        st.subheader("Risk Status Overview")

        status = df["Status"].astype(str).str.lower()

        completed = status.str.contains("completed").sum()
        in_progress = status.str.contains("review|progress").sum()
        resolved = status.str.contains("completed on time").sum()
        need_info = status.str.contains("draft|overdue").sum()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("✅ Completed", completed)
        c2.metric("⏳ In Progress", in_progress)
        c3.metric("✔️ Resolved", resolved)
        c4.metric("❗ Needs Info", need_info)

        # ================= BAR
        st.subheader("Risk Distribution")

        status_counts = df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        fig = px.bar(status_counts, x="Status", y="Count", text="Count")
        st.plotly_chart(fig, use_container_width=True)

        # ================= TREND
        st.subheader("Open Risk Trend")

        df_trend = df.dropna(subset=["Date"]).copy()
        open_risks = df_trend[df_trend["Status"].astype(str).str.contains("draft|review", case=False)]

        trend = open_risks.groupby(df_trend["Date"].dt.to_period("M")).size().reset_index(name="Open Risks")
        trend["Date"] = trend["Date"].dt.to_timestamp()

        fig = px.line(trend, x="Date", y="Open Risks", markers=True)
        st.plotly_chart(fig, use_container_width=True)


# RUN
if __name__ == "__main__":
    main()
