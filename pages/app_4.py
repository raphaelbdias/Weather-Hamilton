###########################################################
# Section 4#
###########################################################
import streamlit as st
import pandas as pd
import seaborn as sns
# import matplotlib.pyplot as plt
from datetime import datetime as dt
import folium
import requests
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import plotly.graph_objects as go
import plotly.express as px
import json

api_url = "https://services.arcgis.com/rYz782eMbySr2srL/arcgis/rest/services/Ward_Boundaries/FeatureServer/7/query?outFields=*&where=1%3D1&f=geojson"
response = requests.get(api_url).json()

# Hamilton's geographical coordinates
hamilton_coords = (43.2557, -79.8711)

df = pd.read_excel("Hamilton_Climate_Summary.xlsx")
df["Year"] = pd.to_datetime(df["Year"], format="%Y")

asset_data = pd.read_excel("data_20240308_combined_v2.xlsx", sheet_name="raw")
asset_data["Maintenance Types"] = asset_data["Maintenance Types"].apply(
    lambda x: x.split(", ")
)
asset_data["Weather Condition"] = asset_data["Weather Condition"].apply(
    lambda x: x.split(", ")
)

# Convert 'Asset Date Built' to datetime format
asset_data["Asset Date Built"] = pd.to_datetime(asset_data["Asset Date Built"])

# Calculate the current age
current_date = dt.now()
asset_data["Asset Age"] = current_date - asset_data["Asset Date Built"]

# Extract the age in years, days, etc.
asset_data["Asset Age Years"] = asset_data["Asset Age"].dt.days // 365
asset_data["Asset Date Built"] = asset_data["Asset Date Built"].apply(lambda x: str(x))

st.title("Facility Information")
# Custom CSS styles
custom_styles = """
<style>
    .facility-info {
        background-color: #262730;
        padding: 15px;
        border: 2px solid #262730;
        border-radius: 10px;
        margin-top: 20px;
        color:#ffffff;
    }

    .facility-info strong {
        display: block;
        margin-bottom: 8px;
        font-weight: bold;
    }

    .facility-info h1 {
        display: block;
        margin-bottom: 8px;
        font-weight: bold;
    }

    .facility-info i.fas.fa-arrow-up {
    color: green;
    }

    .facility-info i.fas.fa-arrow-down {
    color: #9b111e;
    }

    .facility-info i.fas.fa-minus {
    color: grey;
}
</style>
"""

# Display custom styles
st.markdown(custom_styles, unsafe_allow_html=True)

# Create a dropdown to select the facility
selected_facility = st.selectbox("Select Facility", asset_data["Asset Name"])

# Filter the data for the selected facility
selected_facility_data = asset_data[asset_data["Asset Name"] == selected_facility]

# Display the information for the selected facility
if not selected_facility_data.empty:
    st.write(
        f"<h2 style='color: #008080; font-weight: bold;'>{selected_facility.title()}</h2>",
        unsafe_allow_html=True,
    )
    m = folium.Map(
        location=(
            selected_facility_data["Latitude"],
            selected_facility_data["Longitude"],
        ),
        zoom_start=16,
    )
    folium.CircleMarker(
        location=(
            selected_facility_data["Latitude"],
            selected_facility_data["Longitude"],
        ),
        radius=20,
        color="#008080",
        fill=True,
        fill_color="#008080",
        fill_opacity=0.6,
        popup=selected_facility_data["Full_Address"].iloc[0],
    ).add_to(m)

    # Display the map
    folium_static(m)

    # Calculate change from last year
    fci_change = (
        selected_facility_data["Current FCI"].iloc[0]
        - selected_facility_data["2023 FCI Rating"].iloc[0]
    )
    change_class = "change-positive" if fci_change < 0 else "change-negative"

    # Display basic information
    st.markdown(
        f"""
                <div class='facility-info'> FCI 2024
                    <h1>{round(selected_facility_data['2023 FCI Rating'].iloc[0]*100,2)}%</h1>
                    <strong>Change from Last Year:<i style='color: {'green' if fci_change < 0 else 'red'};'> {fci_change:.2f}%</i></strong>
                    <strong>Address: {selected_facility_data['Asset Address'].iloc[0]}</strong> 
                    <strong>Size: {selected_facility_data['Asset Size'].iloc[0]} {selected_facility_data['Asset Measure Unit'].iloc[0]}</strong>
                    <strong>{int(selected_facility_data['Asset Age Years'].iloc[0])} years old</strong>
                </div>""",
        unsafe_allow_html=True,
    )

else:
    st.warning("Please select a facility from the dropdown.")
