import pandas as pd
import os
from datetime import datetime

# File name
file_name = "Incidents_Log.xlsx"

# Define your incident fields here
columns = [
    "Date",
    "Time",
    "Location",
    "Incident Type",
    "Description",
    "Reported By"
]

# Check if file exists
if os.path.exists(file_name):
    df = pd.read_excel(file_name, engine="openpyxl")
else:
    df = pd.DataFrame(columns=columns)

print("=== Incident Entry System ===")
print("Type 'exit' anytime to stop.\n")

while True:
    # Input fields
    location = input("Enter Location: ")
    if location.lower() == "exit":
        break

    incident_type = input("Enter Incident Type: ")
    if incident_type.lower() == "exit":
        break

    description = input("Enter Description: ")
    if description.lower() == "exit":
        break

    reported_by = input("Enter Reported By: ")
    if reported_by.lower() == "exit":
        break

    # Auto date/time
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    # Create new row
    new_row = {
        "Date": date,
        "Time": time,
        "Location": location,
        "Incident Type": incident_type,
        "Description": description,
        "Reported By": reported_by
    }

    # Append to dataframe
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Save file
    df.to_excel(file_name, index=False, engine="openpyxl")

    print("\n✅ Incident saved successfully!\n")

print("\nSystem closed.")
