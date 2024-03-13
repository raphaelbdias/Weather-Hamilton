import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

gdf_wards = None

def load_data_and_process():
    global gdf_wards
    # Fetch ward boundaries via API and create GeoDataFrame
    api_url = "https://services.arcgis.com/rYz782eMbySr2srL/arcgis/rest/services/Ward_Boundaries/FeatureServer/7/query?outFields=*&where=1%3D1&f=geojson"
    response = requests.get(api_url).json()

    # Extract features from the GeoJSON response and assign to gdf_wards
    gdf_wards = gpd.GeoDataFrame.from_features(response['features'])

    # Load asset locations from the uploaded Excel file
    assets_df = pd.read_excel('data_20240308_combined_v2.xlsx')

    gdf_assets = gpd.GeoDataFrame(
        assets_df,
        geometry=gpd.points_from_xy(assets_df['Longitude'], assets_df['Latitude'])
    )

    # Ensure that the assets GeoDataFrame uses the same Coordinate Reference System (CRS) as the wards GeoDataFrame
    gdf_assets.crs = gdf_wards.crs

    # Perform spatial join to find out which ward each asset belongs to
    joined = gpd.sjoin(gdf_assets, gdf_wards, how="left", predicate="within")  # Updated to 'predicate' based on deprecation warning

    # Filter the DataFrame to only show the asset name and ward number
    final_output = joined[['Asset Name', 'Asset Type', 'WARD', 'Latitude', 'Longitude']]

    return final_output

def get_unique_asset_type(final_output):
    # Extract unique asset types
    unique_asset_types = final_output['Asset Type'].unique()
    print(unique_asset_types)
    return unique_asset_types

def calculate_ward_centroids():
    global gdf_wards

    if gdf_wards is None:
        print("gdf_wards is not populated. Please call load_data_and_process first.")
        return None

    # Calculate the centroids for each ward
    centroids = gdf_wards.geometry.centroid
    centroids_gdf = gpd.GeoDataFrame(geometry=centroids)
    centroids_gdf['WARD'] = gdf_wards['WARD']
    centroids_gdf['Centroid Latitude'] = centroids_gdf.geometry.y
    centroids_gdf['Centroid Longitude'] = centroids_gdf.geometry.x
    return centroids_gdf

