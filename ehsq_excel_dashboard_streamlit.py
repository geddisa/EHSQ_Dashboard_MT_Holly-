import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="EHSQ Performance Dashboard")

@st.cache_data
def load_all_data():
    # Attempt to load data with header=1 (skips one top row if there's a title)
    try:
        # If your Excel has NO title row, change header=1 back to header=0
        incidents = pd.read_excel("IncidentReports_All_MTH_2026-06-25.xlsx", sheet_name="Sheet1", header=0)
        return {"Incidents": incidents}
    except Exception as e:
        st.error(f"File Load Error: {e}")
        return None

data = load_all_data()

if data:
    df = data["Incidents"]
    
    # DEBUG: This will show you exactly what column names your file actually has
    st.write("Columns found in your file:", df.columns.tolist())
    
    # --- IMPORTANT ---
    # Look at the list that prints on your screen. 
    # Use that EXACT name below.
    date_col = 'Date of Incident (UTC)' 
    
    # Attempt conversion
    df['Date'] = pd.to_datetime(df[date_col], errors='coerce')
    
    # Check if we have valid dates
    if df['Date'].isna().all():
        st.error(f"Critical Error: Could not find dates in column '{date_col}'. Please verify the column name in the list above.")
    else:
        # Proceed with filtering
        df = df[df['Date'].dt.year == 2026].dropna(subset=['Date'])
        df['Week'] = df['Date'].dt.isocalendar().week
        st.success("Data loaded successfully!")
        
        # Display the rest of your dashboard here...
