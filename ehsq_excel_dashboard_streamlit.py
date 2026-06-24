
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="EHSQ Dashboard", layout="wide")

# =========================
# LOAD INCIDENT DATA
# =========================
@st.cache_data
def load_incidents(uploaded):
    try:
        file = uploaded if uploaded else "IncidentReports_All_MTH_2026-06-18.xlsx"
        df = pd.read_excel(file, engine="openpyxl")

        df.columns = [str(c).strip() for c in df.columns]
        df = df.replace({pd.NA: None})

        return df

    except Exception as e:
        st.error(f"Error loading incidents: {e}")
        return pd.DataFrame()


# =========================
# LOAD METRICS DATA
# =========================
@st.cache_data
def load_metrics(uploaded):
    try:
        file = uploaded if uploaded else "EHSQ Metrics.xlsx"

        tcir = pd.read_excel(file, sheet_name="TCIR and DART", skiprows=2, engine="openpyxl")
        fsi = pd.read_excel(file, sheet_name="FSI Reports", skiprows=3, engine="openpyxl")
        capas = pd.read_excel(file, sheet_name="CAPAs", skiprows=3, engine="openpyxl")

        for df in [tcir, fsi, capas]:
            df.columns = [str(c).strip() for c in df.columns]
            df.replace({pd.NA: None}, inplace=True)

        return tcir, fsi, capas

    except Exception as e:
        st.warning(f"Metrics load failed: {e}")
        return None, None, None


# =========================
# MAIN
# =========================
def main():

    st.title("📊 EHSQ Performance Dashboard")

    # Sidebar
    st.sidebar.header("Uploads")
    inc_file = st.sidebar.file_uploader("Incident File", type=["xlsx"])
    met_file = st.sidebar.file_uploader("Metrics File", type=["xlsx"])

    df = load_incidents(inc_file)
    tcir, fsi, capas = load_metrics(met_file)

    if df.empty:
        st.warning("No incident data loaded.")
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

    # FILTER
    if "Department" in df.columns:
        departments = df["Department"].dropna().unique()
        selected = st.sidebar.multiselect("Department", departments, default=departments)
        df = df[df["Department"].isin(selected)]

    tab1, tab2 = st.tabs(["🚨 Incident Dashboard", "📈 Metrics Dashboard"])

    # ==================================================
    # INCIDENT TAB
    # ==================================================
    with tab1:

        st.subheader("🚦 KPIs")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Incidents", len(df))
        c2.metric("Severe Incidents", int(df["High Risk"].sum()))
        c3.metric("Recordables", int(df["Recordable"].sum()))

        # Trend
        st.subheader("📈 Incident Trend")
        trend_df = df.dropna(subset=["Date"]).copy()
        trend_df["Month"] = trend_df["Date"].dt.to_period("M").dt.to_timestamp()
        trend = trend_df.groupby("Month").size().reset_index(name="Count")

        if not trend.empty:
            fig = px.line(trend, x="Month", y="Count", markers=True, text="Count")
            fig.update_traces(textposition="top center")
            st.plotly_chart(fig, use_container_width=True)

        # =========================
        # SEVERITY GRAPH (MATCH IMAGE)
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

        fig.add_hrect(y0=0, y1=400, fillcolor="green", opacity=0.25)
        fig.add_hrect(y0=400, y1=800, fillcolor="khaki", opacity=0.35)
        fig.add_hrect(y0=800, y1=1300, fillcolor="lightcoral", opacity=0.35)

        fig.add_trace(go.Scatter(
            x=weekly["Week"],
            y=weekly["Points"],
            mode="lines+markers",
            line=dict(color="black", width=4),
            marker=dict(color="black", size=8),
            name="Weekly Severity Total"
        ))

        fig.add_annotation(
            x=25, y=600,
            text="25 pt: Property Damage<br>50 pt: Record Only<br>75 pt: First Aid<br>150 pt: Spill/Explosion<br>250 pt: Recordable<br>350 pt: Days Away<br>600 pt: Fatality",
            showarrow=False,
            bgcolor="white",
            bordercolor="gray"
        )

        fig.update_layout(
            xaxis=dict(range=[1, 24], dtick=1),
            yaxis=dict(range=[0, 1250], dtick=200)
        )

        st.plotly_chart(fig, use_container_width=True)

    # ==================================================
    # METRICS TAB (FULL CHARTS)
    # ==================================================
    with tab2:

        # =========================
        # TCIR / DART
        # =========================
        if tcir is not None:

            st.subheader("📊 TCIR & DART Trends")

            cols = [str(c).lower() for c in tcir.columns]

            month = next((tcir.columns[i] for i, c in enumerate(cols) if "month" in c), None)
            tcir_col = next((tcir.columns[i] for i, c in enumerate(cols) if "tcir" in c and "actual" in c), None)
            dart_col = next((tcir.columns[i] for i, c in enumerate(cols) if "dart" in c and "actual" in c), None)

            if month and tcir_col:
                fig = px.line(tcir, x=month, y=tcir_col, markers=True, text=tcir_col)
                fig.update_traces(textposition="top center")
                st.plotly_chart(fig, use_container_width=True)

            if month and dart_col:
                fig = px.line(tcir, x=month, y=dart_col, markers=True, text=dart_col)
                fig.update_traces(textposition="top center")
                st.plotly_chart(fig, use_container_width=True)

        # =========================
        # CAPA CHARTS
        # =========================
        if capas is not None:

            st.subheader("🛠️ CAPA Performance")

            status_col = next((c for c in capas.columns if "status" in c.lower()), None)
            if status_col:
                data = capas[status_col].value_counts().reset_index()
                data.columns = ["Status", "Count"]
                fig = px.bar(data, x="Status", y="Count", text="Count", color="Status")
                fig.update_traces(textposition="outside")
                st.plotly_chart(fig, use_container_width=True)

            dept_col = next((c for c in capas.columns if "department" in c.lower()), None)
            if dept_col:
                data = capas[dept_col].value_counts().reset_index()
                data.columns = ["Department", "Count"]
                fig = px.bar(data, x="Department", y="Count", text="Count")
                fig.update_traces(textposition="outside")
                st.plotly_chart(fig, use_container_width=True)

        # =========================
        # FSI CHARTS
        # =========================
        if fsi is not None:

            st.subheader("📋 FSI Reports")

            type_col = next((c for c in fsi.columns if "type" in c.lower() or "category" in c.lower()), None)
            if type_col:
                data = fsi[type_col].value_counts().reset_index()
                data.columns = ["Category", "Count"]
                fig = px.bar(data, x="Category", y="Count", text="Count")
                fig.update_traces(textposition="outside")
                st.plotly_chart(fig, use_container_width=True)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()
