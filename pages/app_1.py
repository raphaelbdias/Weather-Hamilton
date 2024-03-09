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

# st.page_link("app.py", label='Content')
st.selectbox(
    'How would you like to be contacted?',
(st.page_link("pages/app_1.py",label='Overview'),
st.page_link("pages/app_2.py",label="Hamilton's Climate"),
st.page_link("pages/app_3.py",label='Climate Insights'),
st.page_link("pages/app_4.py",label="Hamilton's Facilties")))

# # Create tabs
# tabs = [
#     "Overview",
#     "Weather Analysis",
#     "Facilities in Hamilton",
#     "Facility Information",
# ]

# # Add some styling to the sidebar
# st.sidebar.markdown(
#     """
#     <style>
#         .sidebar .widget-title {
#             color: #33adff;
#             text-align: center;
#             padding: 15px 0;
#             font-size: 24px;
#             font-weight: bold;
#         }
#         .sidebar .radio-item {
#             padding: 10px;
#             margin: 5px 0;
#             background-color: #f0f0f0;
#             border-radius: 10px;
#             cursor: pointer;
#             transition: background-color 0.3s;
#         }
#         .sidebar .radio-item:hover {
#             background-color: #e0e0e0;
#         }
#         .sidebar .radio-item:checked {
#             background-color: #33adff;
#             color: white;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )
# st.sidebar.title("Navigation")
# selected_tab = st.sidebar.button("", tabs)
# # About section
# st.sidebar.header("About")
# st.sidebar.info("This app analyzes and visualizes climate data of Hamilton.")

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
# Section 1#
###########################################################

    # Streamlit app
st.title("Climate Analysis of Hamilton")

# Provide some key insights about the data with styling
st.markdown(
    "<div style='color: #008080; font-size: 16px; font-weight: bold;'>1. The average maximum temperature in Hamilton is around {}°C.</div>".format(
        round(df["Max Temp (Historical)"].mean(), 2)
    ),
    unsafe_allow_html=True,
)
st.markdown(
    "<div style='color: #008080; font-size: 16px; font-weight: bold;'>2. The number of summer days has increased over the years.</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div style='color: #008080; font-size: 16px; font-weight: bold;'>3. Heat waves per year have also shown an increasing trend.</div>",
    unsafe_allow_html=True,
)

# Create a Folium map centered around Hamilton, Ontario
m = folium.Map(location=hamilton_coords, zoom_start=10, tiles="Cartodb dark_matter")
folium.GeoJson(
    api_url,
    style_function=lambda feature: {
        "fillColor": "#008080",
        "color": "black",
        "weight": 2,
        "dashArray": "5, 5",
        "fillOpacity": 0.4,
    },
).add_to(m)
folium_static(m)

# Navigation bar
# nav_choice = st.sidebar.radio("Navigation", ["Summary Statistics", "Raw Data"])

# Display content based on user's choice
st.subheader("Summary Statistics")
st.write(df.describe())

# Data analysis and visualization
st.subheader("Data Analysis and Visualization")

# Unique key for multiselect widget
multiselect_key = "select_columns_multiselect"

# Select chart type using a radio button
chart_type = st.radio("Select Chart Type", ["Bar Chart", "Line Chart"], index=0)

# Plotting example: Bar or Line chart for selected columns
selected_columns = st.multiselect(
    "Select columns for plot", df.columns, key=multiselect_key
)
if selected_columns:
    # Include "Year" as x-axis labels in the chart
    chart_data = df.set_index("Year")[selected_columns]

    if chart_type == "Bar Chart":
        st.bar_chart(chart_data)
    elif chart_type == "Line Chart":
        st.line_chart(chart_data, use_container_width=True)

# Unique years for dropdown
years = df["Year"].dt.year.unique()
# Select a year using a dropdown
selected_year = st.selectbox("Select Year", years)

# Filter data based on the selected year
filtered_data = df[df["Year"].dt.year == selected_year]

# Calculate percentages for Summer Days and Winter Days
summer_percentage = (
    filtered_data["Summer Days (Ensemble)"].iloc[0]
    / filtered_data["Summer Days (Ensemble)"].sum()
    * 100
)
winter_percentage = (
    filtered_data["Winter Day (Ensemble)"].iloc[0]
    / filtered_data["Winter Day (Ensemble)"].sum()
    * 100
)

# Donut chart for Summer Days and Winter Days
fig = go.Figure()

fig.add_trace(
    go.Pie(
        labels=["Summer Days", "Winter Days"],
        values=[
            filtered_data["Summer Days (Ensemble)"].iloc[0],
            filtered_data["Winter Day (Ensemble)"].iloc[0],
        ],
        hole=0.7,
        marker=dict(colors=["#FFE37A", "#8de2ff"]),
    )
)

fig.update_layout(
    title_text=f"Summer and Winter Days Distribution for {selected_year}"
)

st.plotly_chart(fig, use_container_width=True)
