import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt
import folium
import requests
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import plotly.graph_objects as go



# Sample data (replace this with your actual data)
# Fetch data from the API
# Fetch data from the API
api_url = "https://services.arcgis.com/rYz782eMbySr2srL/arcgis/rest/services/Ward_Boundaries/FeatureServer/7/query?outFields=*&where=1%3D1&f=geojson"
response = requests.get(api_url).json()


# Hamilton's geographical coordinates
hamilton_coords = (43.2557, -79.8711)

df = pd.read_excel('Hamilton_Climate_Summary.xlsx')
df['Year'] = pd.to_datetime(df['Year'], format='%Y')

# Hamilton's geographical coordinates
hamilton_coords = (43.2557, -79.8711)

# Streamlit app
st.title("Climate Analysis and Hamilton Map")

# Provide some key insights about the data with styling
st.markdown("<div style='color: #008080; font-size: 16px; font-weight: bold;'>1. The average maximum temperature in Hamilton is around {}°C.</div>".format(round(df['Max Temp (Historical)'].mean(), 2)), unsafe_allow_html=True)
st.markdown("<div style='color: #008080; font-size: 16px; font-weight: bold;'>2. The number of summer days has increased over the years.</div>", unsafe_allow_html=True)
st.markdown("<div style='color: #008080; font-size: 16px; font-weight: bold;'>3. Heat waves per year have also shown an increasing trend.</div>", unsafe_allow_html=True)


# Create a Folium map centered around Hamilton, Ontario
m = folium.Map(location=hamilton_coords, zoom_start=10, tiles = 'Cartodb dark_matter')
folium.GeoJson(api_url, style_function=lambda feature: {
        "fillColor": "#ffff00",
        "color": "black",
        "weight": 2,
        "dashArray": "5, 5",
        "fillOpacity": 0.1
    },).add_to(m)
folium_static(m)

# Navigation bar
nav_choice = st.sidebar.radio("Navigation", ["Summary Statistics", "Raw Data"])


# Display content based on user's choice
if nav_choice == "Summary Statistics":
    st.subheader("Summary Statistics")
    st.write(df.describe())
else:  # Assume "Raw Data" as the default choice
    st.subheader("Raw Data")
    st.write(df)

# Data analysis and visualization
st.subheader("Data Analysis and Visualization")

# Unique key for multiselect widget
multiselect_key = "select_columns_multiselect"

# Select chart type using a radio button
chart_type = st.radio("Select Chart Type", ["Bar Chart", "Line Chart"], index=0)

# Plotting example: Bar or Line chart for selected columns
selected_columns = st.multiselect("Select columns for plot", df.columns, key=multiselect_key)
if selected_columns:
    # Include "Year" as x-axis labels in the chart
    chart_data = df.set_index("Year")[selected_columns]

    if chart_type == "Bar Chart":
        st.bar_chart(chart_data)
    elif chart_type == "Line Chart":
        st.line_chart(chart_data, use_container_width=True)

# Unique years for dropdown
years = df['Year'].dt.year.unique()
# Select a year using a dropdown
selected_year = st.selectbox("Select Year", years)

# Filter data based on the selected year
filtered_data = df[df['Year'].dt.year == selected_year]

# Calculate percentages for Summer Days and Winter Days
summer_percentage = filtered_data['Summer Days (Ensemble)'].iloc[0] / filtered_data['Summer Days (Ensemble)'].sum() * 100
winter_percentage = filtered_data['Winter Day (Ensemble)'].iloc[0] / filtered_data['Winter Day (Ensemble)'].sum() * 100

# Donut chart for Summer Days and Winter Days
fig = go.Figure()

fig.add_trace(go.Pie(labels=['Summer Days', 'Winter Days'], values=[filtered_data['Summer Days (Ensemble)'].iloc[0],
                                                                 filtered_data['Winter Day (Ensemble)'].iloc[0]],
                     hole=0.7, marker=dict(colors=['#FFE37A', '#8de2ff'])))

fig.update_layout(title_text=f"Summer and Winter Days Distribution for {selected_year}")

st.plotly_chart(fig, use_container_width=True)


# About section
st.sidebar.header("About")
st.sidebar.info("This app analyzes and visualizes climate data of Hamilton.")

