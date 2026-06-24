# EHSQ Excel Dashboard (Streamlit)

This version reads **your actual Excel workbooks directly**:

- `IncidentReports_All_MTH_2026-06-18.xlsx`
- `EHSQ Metrics.xlsx`

## Run
```bash
pip install -r requirements.txt
streamlit run ehsq_excel_dashboard_streamlit.py
```

## What it includes
- **Incident Dashboard** from the incident report workbook
- **Report KPIs** from FSI, Other Reports, CAPAs, Housekeeping, Environmental Compliance, and Safe Observations
- **TCIR & DART** trends using the metrics workbook
- **Severity & Year over Year** charts from the metrics workbook
- **Data Explorer** tab so you can inspect the parsed data

## Notes / assumptions
- Recordable cases are derived from `Injury Classification` values:
  - `Days Away From Work`
  - `Restricted or Transferred Work`
  - `Other Recordable Case`
- DART cases are derived from:
  - `Days Away From Work`
  - `Restricted or Transferred Work`
- “High/Major Risk Incidents” are based on the `Risk Level` field being `High` or `Major`.
- If you upload workbooks in the sidebar, the app will use those instead of the default files in the folder.
