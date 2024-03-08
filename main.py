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


tab1, tab2 = st.tabs(["Overview", "Analysis"])

with tab1:
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
    st.title("Climate Analysis of Hamilton")

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

with tab2:
    # Load the data
    data = pd.read_excel('Municipality Hamilton_Analysis.xlsx', sheet_name='RCP 8.5')

    # Sidebar
    st.title("Climate Forecast Analysis")
    st.markdown("<div style='color: #008080; font-size: 16px; font-weight: bold;'>Comparison of historical average (1976-2005) to the projected mean for 2021-2050 With GHG emissions continuing to increase at current rates (RCP 8.5).</div>", unsafe_allow_html=True)
    
    # Create a selector for different variables
    selected_variable = st.selectbox("Select Variable", ['Precipitation (mm)', 'Mean Temperature (°C)'])

    # Filter the data based on the selected variable and exclude 'annual'
    filtered_data = data.loc[(data['Variable'] == selected_variable) & (data['Period'] != 'annual')]

    # Create a selector for different metrics (columns) within the selected variable
    selected_metric = st.selectbox("Select Metric", ['2021-2050 (Low)', '2021-2050 (Mean)', '2021-2050 (High)', '2051-2080 (Low)', '2051-2080 (Mean)', '2051-2080 (High)'])

    # Update blurbs based on selected variable
    if selected_variable == 'Precipitation (mm)':
        st.markdown("""<div style='color: #008080; font-size: 16px; font-weight: bold;'>
        Precipitation:
        <ul> Overall, there is an increase in annual precipitation by 6.40% (54mm).
        <ul> Winter (10.70%), Spring (10.60%), and Fall (4.04%) will be greatly affected, while Summer (0.92%) will experience a slight impact.
        </div>""", unsafe_allow_html=True)
    elif selected_variable == 'Mean Temperature (°C)':
        st.markdown("""<div style='color: #008080; font-size: 16px; font-weight: bold;'>
        Mean Temperature:
        <ul> The overall change in mean temperature has significantly increased annually by 25.30%. The annual mean temperature is expected to increase by 2.1°C.
        <ul> Winter (58.97%), Spring (26.87%), and Fall (21.78%) are greatly affected, while Summer (10.41%) will experience the least impact.
        </div>""", unsafe_allow_html=True)

    # Display the filtered data
    st.subheader(f"{selected_variable} Data")
    st.write(filtered_data)

    # Visualize the data using Streamlit's line chart
    st.subheader(f"Seasonal {selected_variable} - {selected_metric}")
    st.line_chart(filtered_data.set_index('Period')[selected_metric])

    annual = pd.DataFrame({
    'Variable': ['Tropical Nights', 'Very hot days (+30°C)', 'Very cold days (-30°C)'],
    'Period': ['annual', 'annual', 'annual'],
    '1976-2005 Mean': [7, 16, 0],
    '2021-2050 (Low)': [8, 18, 0],
    '2021-2050 (Mean)': [19, 37, 0],
    '2021-2050 (High)': [33, 57, 0],
    '2051-2080 (Low)': [22, 38, 0],
    '2051-2080 (Mean)': [40, 63, 0],
    '2051-2080 (High)': [61, 88, 0],
})
    
    # Visualize the annual using Plotly Express
    fig = px.bar(annual, x=selected_metric, y='Variable',
                title="Climate Metrics Over Time",
                labels={'value': 'Value', 'variable': 'Metric'})
    
    # Display the plot
    st.subheader(f"Extreme Weather Overview")
    st.plotly_chart(fig)

    st.markdown("""<div style='color: #008080; font-size: 16px; font-weight: bold;'>
    Extreme Weather:
    <ul>- Tropical nights (nights with temperatures above 20°C) increase from 7 to 19.
    <ul>- Very hot days (above 30°C) more than double from 16 to 37.
    <ul>- Very cold days (below -30°C) will not be experienced as temperatures continue to rise.
    </div>""", unsafe_allow_html=True)
# Additional analysis or visualizations can be added based on your requirements