import pandas as pd
import matplotlib.pyplot as plt
import pprint
import requests

# Sample data (replace this with your actual data)


# df = pd.read_excel('Hamilton_Climate_Summary.xlsx')
# data = df.to_dict('records')
api_url = "https://services.arcgis.com/rYz782eMbySr2srL/arcgis/rest/services/Ward_Boundaries/FeatureServer/7/query?where=1%3D1&outFields=*&outSR=4326&f=json"
response = requests.get(api_url)
ward_data = response.json()

data = pd.DataFrame(ward_data)

pprint.pprint(data)