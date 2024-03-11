import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

def load_data_and_process():
    # Fetch ward boundaries via API and create GeoDataFrame
    api_url = "https://services.arcgis.com/rYz782eMbySr2srL/arcgis/rest/services/Ward_Boundaries/FeatureServer/7/query?outFields=*&where=1%3D1&f=geojson"
    response = requests.get(api_url).json() 

    # Extract features from the GeoJSON response
    features = response['features']

    # Create GeoDataFrame for wards
    gdf = gpd.GeoDataFrame.from_features(features)

    # Load asset locations from the uploaded Excel file
    assets_df = pd.read_excel('data_20240308_combined_v2.xlsx')

    gdf_assets = gpd.GeoDataFrame(
        assets_df,
        geometry=gpd.points_from_xy(assets_df['Longitude'], assets_df['Latitude'])
    )

    # It's important to ensure that the assets GeoDataFrame is using the same Coordinate Reference System (CRS) as the wards GeoDataFrame
    gdf_assets.crs = gdf.crs

    # Perform spatial join to find out which ward each asset belongs to
    joined = gpd.sjoin(gdf_assets, gdf, how="left", op="within")

    # Filter the DataFrame to only show the asset name and ward number
    final_output = joined[['Asset Name', 'Asset Type','WARD', 'Latitude', 'Longitude']]

    return final_output

def get_unique_asset_type(final_output):
    # Extract unique wards
    unique_wards = final_output['Asset Type'].unique()
    print(unique_wards)
    return unique_wards
