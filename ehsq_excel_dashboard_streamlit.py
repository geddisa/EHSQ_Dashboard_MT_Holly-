import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="EHSQ Dashboard", layout="wide")

# =========================
# STYLE (Power BI look)
# =========================
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
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
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

    # ✅ read WITHOUT assuming headers
    tcir = pd.read_excel(file, sheet_name="TCIR and DART", engine="openpyxl")
    fsi = pd.read_excel(file, sheet_name="FSI Reports", engine="openpyxl")
    capas = pd.read_excel(file, sheet_name="CAPAs", engine="openpyxl")

    return tcir, fsi, capas


# =========================
# CLEAN FUNCTION (IMPORTANT)
# =========================
def clean_table(df):
    df = df.copy()
    df = df.dropna(how="all")

    # find first row with real headers
    df.columns = [str(c).strip() for c in df.columns]
    df = df.reset_index(drop=True)

    return df


# =========================
# MAIN
# =========================
def main():

    st.title("📊 EHSQ Performance Dashboard")

    inc_file = st.sidebar.file_uploader("Incident File", type=["xlsx"])
    met_file = st.sidebar.file_uploader("Metrics File", type=["xlsx"])

    df = load_incidents(inc_file)
    tcir_raw, fsi_raw, capas_raw = load_metrics(met_file)

    tab1, tab2 = st.tabs(["🚨 Incident Dashboard", "📈 Metrics Dashboard"])

    # ======================================================
    # INCIDENT TAB
    # ======================================================
    with tab1:

        # KPI
        st.markdown('<div class="card">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)

        c1.metric("Total Incidents", len(df))
        c2.metric("Severe",
                  df.get("Risk Level","").astype(str).str.lower().isin(["high","major"]).sum())
        c3.metric("Recordables",
                  df.get("Injury Classification","").isin([
                      "Days Away From Work",
                      "Restricted or Transferred Work",
                      "Other Recordable Case"
                  ]).sum())
        st.markdown('</div>', unsafe_allow_html=True)

        # TREND
        st.markdown('<div class="card">', unsafe_allow_html=True)

        trend = df.dropna(subset=["Date"]).copy()
        trend["Month"] = trend["Date"].dt.to_period("M").dt.to_timestamp()
        trend = trend.groupby("Month").size().reset_index(name="Count")

        fig = px.line(trend, x="Month", y="Count", markers=True)
        st.subheader("Incidents Over Time")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ✅ SEVERITY GRAPH (EXACT LOGIC)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Incident Severity Graph")

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

        df["Points"] = (
            df["Injury Classification"].map(severity_mapping)
            .fillna(df["Type"].map(severity_mapping))
            .fillna(0)
        )

        df["Week"] = df["Date"].dt.isocalendar().week
        weekly = df.groupby("Week")["Points"].sum()
        weekly = weekly.reindex(range(1,25), fill_value=0).reset_index()
        weekly.columns = ["Week","Points"]

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

        fig.update_layout(
            xaxis=dict(dtick=1, range=[1,30]),
            yaxis=dict(range=[0,1250], dtick=200)
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ======================================================
    # METRICS TAB
    # ======================================================
    with tab2:

        st.header("📈 Metrics Dashboard")

        # CLEAN TABLES
        tcir = clean_table(tcir_raw)
        fsi = clean_table(fsi_raw)
        capas = clean_table(capas_raw)

        # ================= TCIR =================
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("TCIR")

        try:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=tcir.iloc[:,0], y=tcir.iloc[:,1], mode="lines+markers", name="Actual"))
            fig.add_trace(go.Scatter(x=tcir.iloc[:,0], y=tcir.iloc[:,2], mode="lines", name="Target"))
            fig.add_trace(go.Scatter(x=tcir.iloc[:,0], y=tcir.iloc[:,5], mode="lines", name="Industry"))
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.warning("TCIR chart format issue")

        st.markdown('</div>', unsafe_allow_html=True)

        # ================= FSI =================
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("FSI Reports")

        cols = fsi.columns
        month = cols[0]
        on_time = next((c for c in cols if "On Time" in c and "%" not in c), None)
        overdue = next((c for c in cols if "Over" in c), None)
        percent = next((c for c in cols if "%" in c), None)

        if on_time and overdue:
            fig = px.bar(fsi, x=month, y=[on_time, overdue], barmode="group")
            st.plotly_chart(fig, use_container_width=True)

        if percent:
            fig = px.line(fsi, x=month, y=percent, markers=True)
            fig.add_hline(y=1)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ================= CAPA =================
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("CAPAs")

        cols = capas.columns
        month = cols[0]
        on_time = next((c for c in cols if "On Time" in c and "%" not in c), None)
        overdue = next((c for c in cols if "Over" in c), None)
        percent = next((c for c in cols if "%" in c), None)

        if on_time and overdue:
            fig = px.bar(capas, x=month, y=[on_time, overdue], barmode="group")
            st.plotly_chart(fig, use_container_width=True)

        if percent:
            fig = px.line(capas, x=month, y=percent, markers=True)
            fig.add_hline(y=0.8)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)


# RUN
if __name__ == "__main__":
    main()
