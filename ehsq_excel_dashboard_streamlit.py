
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="EHSQ Executive Dashboard", layout="wide")

# =========================
# LOAD INCIDENT DATA
# =========================
@st.cache_data
def load_incidents(uploaded):
    try:
        file = uploaded if uploaded else "IncidentReports_All_MTH_2026-06-18.xlsx"
        df = pd.read_excel(file, engine="openpyxl")

        df.columns = df.columns.astype(str).str.strip()
        df = df.replace({pd.NA: None})

        return df

    except Exception as e:
        st.error(f"Error loading incident file: {e}")
        return pd.DataFrame()


# =========================
# LOAD METRICS
# =========================
@st.cache_data
def load_metrics(uploaded):
    try:
        file = uploaded if uploaded else "EHSQ Metrics.xlsx"
        df = pd.read_excel(file, sheet_name="TCIR and DART", skiprows=2, engine="openpyxl")
        df.columns = df.columns.astype(str).str.strip()
        return df
    except:
        return None


# =========================
# SAFE PLOT
# =========================
def safe_plot(fig):
    try:
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning("Chart failed")


# =========================
# MAIN
# =========================
def main():

    st.title("📊 EHSQ Executive Dashboard")

    # Sidebar
    st.sidebar.header("Filters")
    inc_file = st.sidebar.file_uploader("Upload Incident File", type=["xlsx"])
    met_file = st.sidebar.file_uploader("Upload Metrics File", type=["xlsx"])

    df = load_incidents(inc_file)
    metrics = load_metrics(met_file)

    if df.empty:
        st.warning("No data loaded.")
        return

    # =========================
    # PREPROCESS
    # =========================
    df["Date"] = pd.to_datetime(
        df.get("Date of Incident (Local Plant Time)"),
        errors="coerce"
    )

    df["High Risk"] = df.get("Risk Level", "").astype(str).str.lower().isin(["high", "major"])

    df["Recordable"] = df.get("Injury Classification", "").isin([
        "Days Away From Work",
        "Restricted or Transferred Work",
        "Other Recordable Case"
    ])

    # =========================
    # FILTER
    # =========================
    if "Department" in df.columns:
        dept_filter = st.sidebar.multiselect(
            "Department",
            df["Department"].dropna().unique(),
            default=df["Department"].dropna().unique()
        )
        df = df[df["Department"].isin(dept_filter)]

    # =========================
    # KPIs
    # =========================
    st.subheader("🚦 KPI Overview")

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Incidents", len(df))
    c2.metric("Severe Incidents", int(df["High Risk"].sum()))
    c3.metric("Recordables", int(df["Recordable"].sum()))

    # =========================
    # TREND
    # =========================
    st.subheader("📈 Incident Trend")

    trend_df = df.dropna(subset=["Date"]).copy()
    trend_df["Month"] = trend_df["Date"].dt.to_period("M").dt.to_timestamp()

    trend = trend_df.groupby("Month").size().reset_index(name="Count")

    fig = px.line(trend, x="Month", y="Count", markers=True, text="Count")
    fig.update_traces(textposition="top center")

    safe_plot(fig)

    # =========================
    # ✅ EXACT SEVERITY GRAPH
    # =========================
    st.subheader("🔥 Incident Severity Graph")

    severity_mapping = {
        'Property Damage': 25,
        'Record Only-No Treatment': 50,
        'First Aid': 75,
        'Molten Metal Spill': 150,
        'Molten Metal Explosion': 150,
        'Other Recordable Case': 250,
        'Restricted or Transferred Work': 250,
        'Days Away From Work': 350,
        'Recordable - Fatality': 600
    }

    df["Points"] = df["Injury Classification"].map(severity_mapping) \
        .fillna(df["Type"].map(severity_mapping)) \
        .fillna(0)

    df["Week"] = df["Date"].dt.isocalendar().week

    weekly = df.groupby("Week")["Points"].sum().reset_index()

    full_weeks = pd.DataFrame({"Week": range(1, 25)})
    weekly = full_weeks.merge(weekly, on="Week", how="left").fillna(0)

    fig = go.Figure()

    # BACKGROUND ZONES
    fig.add_hrect(y0=0, y1=400, fillcolor="green", opacity=0.25, line_width=0)
    fig.add_hrect(y0=400, y1=800, fillcolor="khaki", opacity=0.35, line_width=0)
    fig.add_hrect(y0=800, y1=1300, fillcolor="lightcoral", opacity=0.35, line_width=0)

    # LINE
    fig.add_trace(go.Scatter(
        x=weekly["Week"],
        y=weekly["Points"],
        mode="lines+markers",
        line=dict(color="black", width=4),
        marker=dict(color="black", size=8),
        name="Weekly Severity Total"
    ))

    # ZONE LEGEND
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
        marker=dict(size=10, color='green'),
        name='Low Risk Zone (0-400)'
    ))

    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
        marker=dict(size=10, color='khaki'),
        name='Medium Risk Zone (401-800)'
    ))

    fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
        marker=dict(size=10, color='lightcoral'),
        name='High Risk Zone (800+)'
    ))

    # RIGHT BOX
    fig.add_annotation(
        x=25,
        y=600,
        text="25 pt: Property Damage<br><br>50 pt: Record Only - No Treatment<br><br>75 pt: First Aid<br><br>150 pt: Molten Metal Spill / Explosion<br><br>250 pt: Recordable / Restricted Work<br><br>350 pt: Days Away From Work<br><br>600 pt: Fatality",
        showarrow=False,
        bordercolor="gray",
        borderwidth=1,
        bgcolor="white",
        align="left"
    )

    fig.update_layout(
        title="Incident Severity Graph",
        xaxis_title="Calendar Week Number",
        yaxis_title="Total Accumulated Severity Points",
        xaxis=dict(range=[1, 24], dtick=1),
        yaxis=dict(range=[0, 1250], dtick=200),
        legend=dict(x=0.01, y=0.98)
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # HAZARDS
    # =========================
    st.subheader("⚠️ Top Hazards")

    hz = df["Hazard Type"].value_counts().head(10).reset_index()
    hz.columns = ["Hazard", "Count"]

    fig = px.bar(hz, x="Hazard", y="Count", text="Count")
    fig.update_traces(textposition="outside")

    safe_plot(fig)

    # =========================
    # METRICS
    # =========================
    if metrics is not None:
        st.subheader("📊 TCIR & DART")

        month_col = next((c for c in metrics.columns if "month" in c.lower()), None)
        tcir = next((c for c in metrics.columns if "tcir actual" in c.lower()), None)
        dart = next((c for c in metrics.columns if "dart actual" in c.lower()), None)

        if month_col and tcir:
            fig = px.line(metrics, x=month_col, y=tcir, markers=True, text=tcir)
            fig.update_traces(textposition="top center")
            safe_plot(fig)

        if month_col and dart:
            fig = px.line(metrics, x=month_col, y=dart, markers=True, text=dart)
            fig.update_traces(textposition="top center")
            safe_plot(fig)

    # =========================
    # INSIGHTS
    # =========================
    st.subheader("🧠 Executive Insights")

    top_hazard = hz.iloc[0]["Hazard"] if not hz.empty else "N/A"

    st.success(f"""
    • Most common hazard: **{top_hazard}**  
    • High exposure to repeat risks  
    • Focus needed on high severity weeks  
    """)

    # =========================
    # TABLE
    # =========================
    st.subheader("📋 Data Table")
    st.dataframe(df, use_container_width=True)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()
