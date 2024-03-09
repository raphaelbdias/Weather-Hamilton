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

st.header('Contents')
# st.page_link("app.py", label='Content')
st.page_link("pages/app_1.py",label='Overview')
st.page_link("pages/app_2.py",label="Hamilton's Climate")
st.page_link("pages/app_3.py",label='Climate Insights')
st.page_link("pages/app_4.py",label="Hamilton's Facilties")