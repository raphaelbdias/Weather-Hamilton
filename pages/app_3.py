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
import streamlit.components.v1 as components

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
###########################################################
# Section 3#
###########################################################
st.title("Facilities in Hamilton")

# asset_data = df_3.to_dict(orient='records')

# # Display raw data
# st.subheader("Asset Data")
# st.write(asset_data)

# Summary Statistics
st.subheader("Summary Statistics")
st.write(asset_data.describe())

# Visualizations
st.subheader("Data Visualizations")

# Create a horizontal bar chart using plotly
fig = px.bar(
    asset_data["Asset Type"].value_counts().reset_index(),
    x="count",
    y="Asset Type",
    orientation="h",
    labels={"index": "Asset Type", "Asset Type": "Count"},
    title="Asset Types Count",
)

# Display the plot
st.plotly_chart(fig)

# Create a Folium map centered around Hamilton, Ontario

# m = folium.Map(location=hamilton_coords, zoom_start=10, tiles="Cartodb Positron")

# folium.GeoJson(
#     api_url,
#     style_function=lambda feature: {
#         "fillColor": "#ffff00",
#         "color": "black",
#         "weight": 1,
#         "dashArray": "5, 5",
#         "fillOpacity": 0.1,
#     },
# ).add_to(m)

# # Add markers to the map
# for index, row in asset_data.iterrows():
#     folium.CircleMarker(
#         location=[row["Latitude"], row["Longitude"]], radius=1.6, opacity=0.3
#     ).add_to(m)

# # Display the map
# st.subheader("Asset Locations in Hamilton")
# folium_static(m)
# asset_data[['lat', 'lon']] = asset_data[["Latitude","Longitude"]]

# st.map(asset_data, color='Asset Type',)

components.iframe("https://miro.com/app/embed/uXjVNimtC2M=/?pres=1&frameId=3458764581757088982&embedId=509266931541", scrolling=False, height=200, width=200)
