
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="EHSQ Dashboard", layout="wide")

# =========================================
# STYLING (POWER BI LOOK)
# =========================================
st.markdown("""
<style>
body {background-color: #f4f6f9;}

.block-container {
    padding-top: 2rem;
}

.card {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 15px;
}
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
    df = df.replace({pd.NA: None})
    df["Date"] = pd.to_datetime(df.get("Date of Incident (Local Plant Time)"), errors="coerce")
    return df


@st.cache_data
def load_metrics(file):
    file = file if file else "EHSQ Metrics.xlsx"

    tcir = pd.read_excel(file, sheet_name="TCIR and DART", skiprows=2, engine="openpyxl")
    fsi = pd.read_excel(file, sheet_name="FSI Reports", skiprows=3, engine="openpyxl")
    capas = pd.read_excel(file, sheet_name="CAPAs", skiprows=3, engine="openpyxl")

    for d in [tcir, fsi, capas]:
        d.columns = [str(c).strip() for c in d.columns]
        d.replace({pd.NA: None}, inplace=True)

    return tcir, fsi, capas


# =========================================
# MAIN
# =========================================
def main():

    st.title("📊 EHSQ Performance Dashboard")

    inc_file = st.sidebar.file_uploader("Upload Incident File", type=["xlsx"])
    met_file = st.sidebar.file_uploader("Upload Metrics File", type=["xlsx"])

    df = load_incidents(inc_file)
    tcir, fsi, capas = load_metrics(met_file)

    tab1, tab2 = st.tabs(["🚨 Incident Dashboard", "📈 Metrics Dashboard"])

    # ==========================================================
    # INCIDENT DASHBOARD
    # ==========================================================
    with tab1:

        # ================= KPI CARDS =================
        st.markdown('<div class="card">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)

        c1.metric("Total Incidents", len(df))
        c2.metric("Severe Incidents",
                  df.get("Risk Level","").astype(str).str.lower().isin(["high","major"]).sum())
        c3.metric("Recordables",
                  df.get("Injury Classification","").isin([
                      "Days Away From Work",
                      "Restricted or Transferred Work",
                      "Other Recordable Case"
                  ]).sum())
        st.markdown('</div>', unsafe_allow_html=True)

        # ================= TREND =================
        st.markdown('<div class="card">', unsafe_allow_html=True)

        trend = df.dropna(subset=["Date"]).copy()
        trend["Month"] = trend["Date"].dt.to_period("M").dt.to_timestamp()
        trend = trend.groupby("Month").size().reset_index(name="Count")

        fig = px.line(trend, x="Month", y="Count", markers=True, text="Count")
        fig.update_traces(textposition="top center")

        st.subheader("Incidents Over Time")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # ================= TWO COLUMN SECTION =================
        col1, col2 = st.columns(2)

        # Injury
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            ic = df["Injury Classification"].value_counts().reset_index()
            ic.columns = ["Type","Count"]

            fig = px.bar(ic, x="Type", y="Count", text="Count")
            fig.update_traces(textposition="outside")

            st.subheader("Injury Classification")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # Hazard
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            hz = df["Hazard Type"].value_counts().head(15).reset_index()
            hz.columns = ["Hazard","Count"]

            fig = px.bar(hz, x="Hazard", y="Count", text="Count")
            fig.update_traces(textposition="outside")

            st.subheader("Hazard Type")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # ================= TYPE + DEPT =================
        col3, col4 = st.columns(2)

        with col3:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            t = df["Type"].value_counts().reset_index()
            t.columns = ["Type","Count"]

            fig = px.bar(t, x="Type", y="Count", text="Count")
            fig.update_traces(textposition="outside")

            st.subheader("Incident Type")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

        with col4:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            d = df["Department"].value_counts().reset_index()
            d.columns = ["Dept","Count"]

            fig = px.bar(d, x="Dept", y="Count", text="Count")
            fig.update_traces(textposition="outside")

            st.subheader("Department")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # ================= SEVERITY (FULL WIDTH FEATURE TILE) =================
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

        current_week = 24
        weekly = weekly.reindex(range(1, current_week + 1), fill_value=0)

        weekly = weekly.reset_index()
        weekly.columns = ["Week","Points"]

        fig = go.Figure()

        fig.add_hrect(y0=0, y1=400, fillcolor="lightgreen", opacity=0.4)
        fig.add_hrect(y0=400, y1=800, fillcolor="khaki", opacity=0.4)
        fig.add_hrect(y0=800, y1=1250, fillcolor="lightcoral", opacity=0.4)

        fig.add_trace(go.Scatter(
            x=weekly["Week"],
            y=weekly["Points"],
            mode="lines+markers",
            line=dict(color="black", width=3),
            marker=dict(size=8, color="black")
        ))

        fig.update_layout(
            xaxis=dict(dtick=1, range=[1, current_week+6]),
            yaxis=dict(dtick=200, range=[0,1250])
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================
    # METRICS DASHBOARD
    # ==========================================================
  
with tab2:

    st.header("📈 EHSQ Metrics Dashboard")

    # ======================================================
    # ✅ TCIR & DART (ACTUAL vs TARGET vs INDUSTRY)
    # ======================================================
    st.subheader("📊 TCIR & DART Performance")

    tcir_df = tcir.copy()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=tcir_df["Month"],
        y=tcir_df["TCIR Actual"],
        mode='lines+markers',
        name="TCIR Actual",
        line=dict(color="blue", width=3)
    ))

    fig.add_trace(go.Scatter(
        x=tcir_df["Month"],
        y=tcir_df["TCIR Target"],
        mode='lines',
        name="TCIR Target",
        line=dict(color="green", dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=tcir_df["Month"],
        y=tcir_df["TCIR Industry Average"],
        mode='lines',
        name="Industry Avg",
        line=dict(color="red", dash="dot")
    ))

    st.plotly_chart(fig, use_container_width=True)

    # ================= DART =================
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=tcir_df["Month"],
        y=tcir_df["DART Actual"],
        mode='lines+markers',
        name="DART Actual",
        line=dict(color="blue", width=3)
    ))

    fig.add_trace(go.Scatter(
        x=tcir_df["Month"],
        y=tcir_df["DART Target"],
        mode='lines',
        name="DART Target",
        line=dict(color="green", dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=tcir_df["Month"],
        y=tcir_df["DART Industry Average"],
        mode='lines',
        name="Industry Avg",
        line=dict(color="red", dash="dot")
    ))

    st.plotly_chart(fig, use_container_width=True)

    # ======================================================
    # ✅ FSI REPORTS (KEY KPI CHART)
    # ======================================================
    st.subheader("📋 FSI Reports Performance")

    fsi_chart = fsi[["FSI Reports", "On Time", "Over Due"]].dropna()

    fig = px.bar(
        fsi_chart,
        x="FSI Reports",
        y=["On Time", "Over Due"],
        barmode="group",
        title="FSI On Time vs Overdue"
    )

    st.plotly_chart(fig, use_container_width=True)

    # % ON TIME LINE
    if "% On Time" in fsi.columns:
        fig = px.line(
            fsi,
            x="FSI Reports",
            y="% On Time",
            markers=True,
            title="FSI % On Time vs Target"
        )

        fig.add_hline(y=1, line_dash="dash", line_color="green")  # target = 100%
        st.plotly_chart(fig, use_container_width=True)

    # ======================================================
    # ✅ CAPAs (MOST IMPORTANT BUSINESS KPI)
    # ======================================================
    st.subheader("🛠️ CAPA Performance")

    capa_chart = capas[["CAPAs", "On Time", "Over Due"]].dropna()

    fig = px.bar(
        capa_chart,
        x="CAPAs",
        y=["On Time", "Over Due"],
        barmode="group",
        title="CAPAs On Time vs Overdue"
    )

    st.plotly_chart(fig, use_container_width=True)

    # CAPA % LINE
    if "% On Time" in capas.columns:
        fig = px.line(
            capas,
            x="CAPAs",
            y="% On Time",
            markers=True,
            title="CAPA % On Time vs Target"
        )

        fig.add_hline(y=0.8, line_dash="dash", line_color="red")  # 80% target
        st.plotly_chart(fig, use_container_width=True)

    # ======================================================
    # ✅ HOUSEKEEPING
    # ======================================================
    st.subheader("🧹 Housekeeping")

    hk = metrics_housekeeping = load_metrics(met_file)[0] if False else None
    
# ------------------------------------------------------
    # SAFE OBSERVATIONS
    # ------------------------------------------------------
    st.subheader("✅ Safe Observations")

    safe_cols = [c for c in fsi.columns]  # fallback safe

    # real dataset fix
    safe = load_metrics(met_file)[1] if False else None



# RUN
if __name__ == "__main__":
    main()
