
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="EHSQ Dashboard", layout="wide")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_incidents(uploaded):
    file = uploaded if uploaded else "IncidentReports_All_MTH_2026-06-18.xlsx"
    df = pd.read_excel(file, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]
    df = df.replace({pd.NA: None})
    return df


@st.cache_data
def load_metrics(uploaded):
    file = uploaded if uploaded else "EHSQ Metrics.xlsx"

    tcir = pd.read_excel(file, sheet_name="TCIR and DART", skiprows=2, engine="openpyxl")
    fsi = pd.read_excel(file, sheet_name="FSI Reports", skiprows=3, engine="openpyxl")
    capas = pd.read_excel(file, sheet_name="CAPAs", skiprows=3, engine="openpyxl")

    for d in [tcir, fsi, capas]:
        d.columns = [str(c).strip() for c in d.columns]
        d.replace({pd.NA: None}, inplace=True)

    return tcir, fsi, capas


# =========================
# MAIN
# =========================
def main():

    st.title("📊 EHSQ FULL ANALYTICS DASHBOARD")

    inc_file = st.sidebar.file_uploader("Incident File", type=["xlsx"])
    met_file = st.sidebar.file_uploader("Metrics File", type=["xlsx"])

    df = load_incidents(inc_file)
    tcir, fsi, capas = load_metrics(met_file)

    df["Date"] = pd.to_datetime(df.get("Date of Incident (Local Plant Time)"), errors="coerce")

    tab1, tab2 = st.tabs(["🚨 Incident", "📈 Metrics"])

    # ======================================================
    # INCIDENT TAB
    # ======================================================
    with tab1:

        st.subheader("KPIs")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total", len(df))
        c2.metric("Severe", df.get("Risk Level", "").astype(str).str.lower().isin(["high","major"]).sum())
        c3.metric("Recordable", df.get("Injury Classification","").isin([
            "Days Away From Work","Restricted or Transferred Work","Other Recordable Case"
        ]).sum())

        # Trend
        trend = df.dropna(subset=["Date"]).copy()
        trend["Month"] = trend["Date"].dt.to_period("M").dt.to_timestamp()
        trend = trend.groupby("Month").size().reset_index(name="Count")

        fig = px.line(trend, x="Month", y="Count", markers=True, text="Count")
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True)

        # =========================================
        # SEVERITY (EXACT LOOK)
        # =========================================
       
st.subheader("🔥 Incident Severity Graph")

import plotly.graph_objects as go

# =========================
# EXACT SAME MAPPING
# =========================
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

# =========================
# EXACT SAME POINT LOGIC
# =========================
df["Points"] = (
    df["Injury Classification"].map(severity_mapping)
    .fillna(df["Type"].map(severity_mapping))
    .fillna(0)
)

# =========================
# WEEK CALCULATION (MATCH YOUR CODE)
# =========================
df["Week"] = df["Date"].dt.isocalendar().week

weekly_scores = df.groupby("Week")["Points"].sum()

# EXACT same week cap logic
current_week = 24
weekly_scores = weekly_scores.reindex(range(1, current_week + 1), fill_value=0)

# Convert to dataframe
weekly = weekly_scores.reset_index()
weekly.columns = ["Week", "Points"]

# =========================
# BUILD GRAPH (STRUCTURE MATCH)
# =========================
fig = go.Figure()

# ZONES (same thresholds)
fig.add_hrect(y0=0, y1=400, fillcolor='lightgreen', opacity=0.4, line_width=0)
fig.add_hrect(y0=400, y1=800, fillcolor='khaki', opacity=0.4, line_width=0)
fig.add_hrect(y0=800, y1=1250, fillcolor='lightcoral', opacity=0.4, line_width=0)

# LINE (same style)
fig.add_trace(go.Scatter(
    x=weekly["Week"],
    y=weekly["Points"],
    mode="lines+markers",
    line=dict(color="black", width=3),
    marker=dict(color="black", size=8),
    name="Weekly Severity Total"
))

# =========================
# LEGEND MATCH
# =========================
fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers",
    marker=dict(size=10, color="lightgreen"),
    name="Low Risk Zone (0-400)"
))
fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers",
    marker=dict(size=10, color="khaki"),
    name="Medium Risk Zone (401-800)"
))
fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers",
    marker=dict(size=10, color="lightcoral"),
    name="High Risk Zone (800+)"
))

# =========================
# EXACT TEXT BOX (RIGHT SIDE)
# =========================
fig.add_annotation(
    x=current_week + 3,
    y=600,
    xref="x",
    yref="y",
    showarrow=False,
    align="left",
    bordercolor="#cccccc",
    borderwidth=1,
    bgcolor="white",
    text=(
        "25 pt: Property Damage<br><br>"
        "50 pt: Record Only - No Treatment<br><br>"
        "75 pt: First Aid<br><br>"
        "150 pt: Molten Metal Spill > 25 lbs /<br>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Molten Metal Explosion (Force 2 or 3)<br><br>"
        "250 pt: Other Recordable Case /<br>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Restricted or Transferred Work<br><br>"
        "350 pt: Days Away From Work<br><br>"
        "600 pt: Recordable - Fatality"
    )
)

# =========================
# AXES + LIMITS (MATCH IMAGE)
# =========================
fig.update_layout(
    title="Incident Severity Graph",
    xaxis=dict(
        title="Calendar Week Number",
        dtick=1,
        range=[1, current_week + 6]
    ),
    yaxis=dict(
        title="Total Accumulated Severity Points",
        range=[0, 1250],
        dtick=200
    ),
    plot_bgcolor="white",
    legend=dict(
        x=0.01,
        y=0.98,
        bgcolor="rgba(255,255,255,1)",
        bordercolor="#cccccc",
        borderwidth=1
    )
)

st.plotly_chart(fig, use_container_width=True)

    # ======================================================
    # METRICS TAB (ALL CHARTS)
    # ======================================================
    with tab2:

        # =========================
        # TCIR / DART
        # =========================
        st.subheader("TCIR & DART")

        cols = [str(c).lower() for c in tcir.columns]

        month = next((tcir.columns[i] for i,c in enumerate(cols) if "month" in c), None)
        tcir_col = next((tcir.columns[i] for i,c in enumerate(cols) if "tcir" in c and "actual" in c), None)
        dart_col = next((tcir.columns[i] for i,c in enumerate(cols) if "dart" in c and "actual" in c), None)

        if month and tcir_col:
            fig = px.line(tcir, x=month, y=tcir_col, markers=True, text=tcir_col)
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig, use_container_width=True)

        if month and dart_col:
            fig = px.line(tcir, x=month, y=dart_col, markers=True, text=dart_col)
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig, use_container_width=True)

        # =========================
        # CAPA FULL DASHBOARD
        # =========================
        st.subheader("🛠️ CAPA ANALYTICS")

        for key in ["Status","Department","Assigned","Type"]:
            col = next((c for c in capas.columns if key.lower() in c.lower()), None)

            if col:
                data = capas[col].fillna("Unknown").value_counts().reset_index()
                data.columns = [key,"Count"]

                fig = px.bar(data, x=key, y="Count", text="Count")
                fig.update_traces(textposition="outside")
                st.plotly_chart(fig, use_container_width=True)

        # CAPA Trend
        date_col = next((c for c in capas.columns if "date" in c.lower()), None)
        if date_col:
            capas["Date"] = pd.to_datetime(capas[date_col], errors="coerce")
            trend = capas.dropna(subset=["Date"])
            trend["Month"] = trend["Date"].dt.to_period("M").dt.to_timestamp()
            trend = trend.groupby("Month").size().reset_index(name="Count")

            fig = px.line(trend, x="Month", y="Count", markers=True, text="Count")
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig, use_container_width=True)

        # =========================
        # FSI FULL DASHBOARD
        # =========================
        st.subheader("📋 FSI ANALYTICS")

        for key in ["Type","Category","Department","Assigned"]:
            col = next((c for c in fsi.columns if key.lower() in c.lower()), None)

            if col:
                data = fsi[col].fillna("Unknown").value_counts().reset_index()
                data.columns = [key,"Count"]

                fig = px.bar(data, x=key, y="Count", text="Count")
                fig.update_traces(textposition="outside")
                st.plotly_chart(fig, use_container_width=True)

        # FSI Trend
        date_col = next((c for c in fsi.columns if "date" in c.lower()), None)
        if date_col:
            fsi["Date"] = pd.to_datetime(fsi[date_col], errors="coerce")
            trend = fsi.dropna(subset=["Date"])
            trend["Month"] = trend["Date"].dt.to_period("M").dt.to_timestamp()
            trend = trend.groupby("Month").size().reset_index(name="Count")

            fig = px.line(trend, x="Month", y="Count", markers=True, text="Count")
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
