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

###########################################################
# Section 2#
###########################################################
# Load the data
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
data = pd.read_excel("Municipality Hamilton_Analysis.xlsx", sheet_name="RCP 8.5")


st.title("""A notable increase in annual precipitation and significant temperature rises, affecting seasons differently and altering the frequency of extreme weather events.
                      """)
st.markdown(
    """<div style='color: #008080; font-size: 16px; font-weight: bold;'>
        Comparison of historical average (1976-2005) to the projected mean for 
        2021-2050 With GHG emissions continuing to increase at current rates (RCP 8.5).
    </div>""",
    unsafe_allow_html=True,
)

# Create three columns
col1, col2 = st.columns([1, 2])

# Visualize the data using Streamlit's line chart in the first column
with col1:
    # Create a selector for different metrics (columns) within the selected variable
    selected_metric = st.selectbox(
        "Select Metric",
        [
            "2021-2050 (Low)",
            "2021-2050 (Mean)",
            "2021-2050 (High)",
            "2051-2080 (Low)",
            "2051-2080 (Mean)",
            "2051-2080 (High)",
        ],
    )
    container = st.container(border=True)
    # Filter data for Precipitation
    precipitation_data = data.loc[
        (data["Variable"] == "Precipitation (mm)") & (data["Period"] != "annual")
    ]

    # Filter data for Mean Temperature
    temperature_data = data.loc[
        (data["Variable"] == "Mean Temperature (°C)") & (data["Period"] != "annual")
    ]

    # Display the combined chart
    container.subheader(f"Seasonal Precipitation")
    container.line_chart(
        {
            "Precipitation": precipitation_data.set_index("Period")[selected_metric],
        }, use_container_width=True, x=None
    )
    # Display the combined chart
    container.subheader(f"Mean Temperature")
    container.bar_chart(
        {
            "Mean Temperature": temperature_data.set_index("Period")[selected_metric],
        }, use_container_width=True
    )
    # Apply style to the line chart
    # st.line_chart.pyplot().set_theme(style="whitegrid")r


# Display the blurb for extreme weather in the third column
with col2:
    filtered_data = data.loc[
        (data["Variable"] == "Mean Temperature (°C)") & (data["Period"] != "annual")
    ]
    st.markdown(
            """<div style='color: #008080; 
                font-size: 16px; 
                font-weight: bold;
                background-color: #262730;
                padding: 15px;
                border: 2px solid #262730;
                border-radius: 10px;
                margin-top: 20px;'>
        Precipitation Changes: 
        <ul>Overall, there is a notable 6.40% increase in annual precipitation (54mm). 
        Winter, Spring, and Fall are expected to be significantly affected, with increases of 10.70%, 10.60%, and 4.04%, respectively. 
        Summer, however, will experience a more modest impact at 0.92%.
    </div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
            """<div style='color: #008080; 
                font-size: 16px; 
                font-weight: bold;
                background-color: #262730;
                padding: 15px;
                border: 2px solid #262730;
                border-radius: 10px;
                margin-top: 20px;'>
        Mean Temperature Rise: 
        <ul>The annual mean temperature is projected to rise by 25.30%, corresponding to a 2.1°C increase. 
        Winter, Spring, and Fall will be most affected, with increases of 58.97%, 26.87%, and 21.78%, respectively. 
        Summer will see the least impact at 10.41%.
    </div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
            """<div style='color: #008080; 
                font-size: 16px; 
                font-weight: bold;
                background-color: #262730;
                padding: 15px;
                border: 2px solid #262730;
                border-radius: 10px;
                margin-top: 20px;'>
        Extreme Weather Events: 
        <ul>Tropical nights, characterized by temperatures above 20°C, will surge from 7 to 19.
        Very hot days (above 30°C) are expected to more than double, increasing from 16 to 37.
        Fortunately, the occurrence of very cold days (below -30°C) is anticipated to cease due to rising temperatures.
    </div>""",
        unsafe_allow_html=True,
    )


    # Apply custom styles
    custom_styles = """
    <style>
        .facility-info {
            background-color: #262730;
            padding: 15px;
            border: 2px solid #262730;
            border-radius: 10px;
            margin-top: 20px;
            color: #ffffff;
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

    annual_values = pd.DataFrame(
        {
            "Variable": [
                "Tropical Nights",
                "Very hot days (+30°C)",
                "Very cold days (-30°C)",
            ],
            "1976-2005 Mean": [7, 16, 0],
            "2021-2050 (Low)": [8, 18, 0],
            "2021-2050 (Mean)": [19, 37, 0],
            "2021-2050 (High)": [33, 57, 0],
            "2051-2080 (Low)": [22, 38, 0],
            "2051-2080 (Mean)": [40, 63, 0],
            "2051-2080 (High)": [61, 88, 0],
        }
    )

    # Display the styled container using markdown
    st.markdown(custom_styles, unsafe_allow_html=True)

    st.subheader("Extreme Weather")
    st.markdown(f"""
        <div class="facility-info">
            <h1>Extreme weather events values:</h1>
            <p><strong>Tropical Nights:</strong> {annual_values[selected_metric][0]}</p>
            <p><strong>Very hot days (+30°C):</strong> {annual_values[selected_metric][1]}</p>
            <p><strong>Very cold days (-30°C):</strong> {annual_values[selected_metric][2]}</p>
        </div>
    """,
        unsafe_allow_html=True
    )