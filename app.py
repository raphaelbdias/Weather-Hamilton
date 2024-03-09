import streamlit as st
import pandas as pd

# import matplotlib.pyplot as plt
from datetime import datetime as dt
import folium
import requests
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import plotly.graph_objects as go
import plotly.express as px
import json


# Create tabs
tabs = [
    "Overview",
    "Weather Analysis",
    "Facilities in Hamilton",
    "Facility Information",
]

# Add some styling to the sidebar
st.sidebar.markdown(
    """
    <style>
        .sidebar .widget-title {
            color: #33adff;
            text-align: center;
            padding: 15px 0;
            font-size: 24px;
            font-weight: bold;
        }
        .sidebar .radio-item {
            padding: 10px;
            margin: 5px 0;
            background-color: #f0f0f0;
            border-radius: 10px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .sidebar .radio-item:hover {
            background-color: #e0e0e0;
        }
        .sidebar .radio-item:checked {
            background-color: #33adff;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.sidebar.title("Navigation")
selected_tab = st.sidebar.radio("", tabs)
# About section
st.sidebar.header("About")
st.sidebar.info("This app analyzes and visualizes climate data of Hamilton.")

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

# Display content based on the selected tab
if selected_tab == "Overview":
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

###########################################################
# Section 2#
###########################################################

elif selected_tab == "Weather Analysis":
    # Load the data
    data = pd.read_excel("Municipality Hamilton_Analysis.xlsx", sheet_name="RCP 8.5")

    # Sidebar
    st.title("Climate Forecast Analysis")
    st.markdown(
        """<div style='color: #008080; font-size: 16px; font-weight: bold;'>
            Comparison of historical average (1976-2005) to the projected mean for 
            2021-2050 With GHG emissions continuing to increase at current rates (RCP 8.5).
        </div>""",
        unsafe_allow_html=True,
    )

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


    # Create three columns
    col1, col2, col3 = st.columns(3)

    # Visualize the data using Streamlit's line chart in the first column
    with col1:
        # Filter data for Precipitation
        precipitation_data = data.loc[
            (data["Variable"] == "Precipitation (mm)") & (data["Period"] != "annual")
        ]

        # Filter data for Mean Temperature
        temperature_data = data.loc[
            (data["Variable"] == "Mean Temperature (°C)") & (data["Period"] != "annual")
        ]

        # Display blurbs based on selected variable
        st.markdown(
            """<div style='color: #008080; font-size: 16px; font-weight: bold;'>
            Precipitation:
            <ul> Overall, there is an increase in annual precipitation by 6.40% (54mm).
            <ul> Winter (10.70%), Spring (10.60%), and Fall (4.04%) will be greatly affected, while Summer (0.92%) will experience a slight impact.
            </div>""",
            unsafe_allow_html=True,
        )

        # Display the combined chart
        st.subheader(f"Seasonal Precipitation and Mean Temperature - {selected_metric}")
        st.line_chart(
            {
                "Precipitation": precipitation_data.set_index("Period")[selected_metric],
                "Mean Temperature": temperature_data.set_index("Period")[selected_metric],
            }
        )


    # Visualize the annual using Plotly Express in the second column
    with col2:
        # Create a DataFrame for the annual bar chart
        annual = pd.DataFrame(
        {
            "Variable": [
                "Tropical Nights",
                "Very hot days (+30°C)",
                "Very cold days (-30°C)",
            ],
            "Period": ["annual", "annual", "annual"],
            "1976-2005 Mean": [7, 16, 0],
            "2021-2050 (Low)": [8, 18, 0],
            "2021-2050 (Mean)": [19, 37, 0],
            "2021-2050 (High)": [33, 57, 0],
            "2051-2080 (Low)": [22, 38, 0],
            "2051-2080 (Mean)": [40, 63, 0],
            "2051-2080 (High)": [61, 88, 0],
        }
    )
        fig = px.bar(
            annual,
            x=selected_metric,
            y="Variable",
            title="Climate Metrics Over Time",
            labels={"value": "Value", "variable": "Metric"},
        )
        st.subheader(f"Extreme Weather Overview")
        st.plotly_chart(fig)

        st.markdown(
            """<div style='color: #008080; font-size: 16px; font-weight: bold;'>
        Extreme Weather:
        <ul>- Tropical nights (nights with temperatures above 20°C) increase from 7 to 19.
        <ul>- Very hot days (above 30°C) more than double from 16 to 37.
        <ul>- Very cold days (below -30°C) will not be experienced as temperatures continue to rise.
        </div>""",
            unsafe_allow_html=True,
        )

    # Display the blurb for extreme weather in the third column
    with col3:
        filtered_data = data.loc[
            (data["Variable"] == "Mean Temperature (°C)") & (data["Period"] != "annual")
        ]
        st.markdown(
                """<div style='color: #008080; font-size: 16px; font-weight: bold;'>
            Mean Temperature:
            <ul> The overall change in mean temperature has significantly increased annually by 25.30%. The annual mean temperature is expected to increase by 2.1°C.
            <ul> Winter (58.97%), Spring (26.87%), and Fall (21.78%) are greatly affected, while Summer (10.41%) will experience the least impact.
            </div>""",
                unsafe_allow_html=True,
            )
        st.subheader(f"Mean Temprature - {selected_metric}")
        st.line_chart(filtered_data.set_index("Period")[selected_metric])

# Additional analysis or visualizations can be added based on your requirements

###########################################################
# Section 3#
###########################################################

elif selected_tab == "Facilities in Hamilton":
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

    m = folium.Map(location=hamilton_coords, zoom_start=10, tiles="Cartodb Positron")

    folium.GeoJson(
        api_url,
        style_function=lambda feature: {
            "fillColor": "#ffff00",
            "color": "black",
            "weight": 1,
            "dashArray": "5, 5",
            "fillOpacity": 0.1,
        },
    ).add_to(m)

    # Add markers to the map
    for index, row in asset_data.iterrows():
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]], radius=1.6, opacity=0.3
        ).add_to(m)

    # Display the map
    st.subheader("Asset Locations in Hamilton")
    folium_static(m)


###########################################################
# Section 4#
###########################################################

elif selected_tab == "Facility Information":
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
            zoom_start=14,
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
