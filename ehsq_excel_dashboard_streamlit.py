import streamlit as st
import pandas as pd

# Load the Excel file once
FILE_PATH = "EHSQ Metrics.xlsx"

@st.cache_data
def load_all_data():
    # Use specific header/skiprows settings based on your file structure
    data = {
        "TCIR": pd.read_excel(FILE_PATH, sheet_name="TCIR and DART", header=1),
        "Housekeeping": pd.read_excel(FILE_PATH, sheet_name="Housekeeping", skiprows=2),
        "CAPAs": pd.read_excel(FILE_PATH, sheet_name="CAPAs", skiprows=2),
        "Observations": pd.read_excel(FILE_PATH, sheet_name="Safe Observations", header=0),
        "Environmental": pd.read_excel(FILE_PATH, sheet_name="Environmental Compliance Issues", header=0),
        "Other": pd.read_excel(FILE_PATH, sheet_name="Other Reports", skiprows=2),
        "FSI": pd.read_excel(FILE_PATH, sheet_name="FSI Reports", skiprows=2),
        "Severity": pd.read_excel(FILE_PATH, sheet_name="Overall Severity Ratings", skiprows=8)
    }
    return data
