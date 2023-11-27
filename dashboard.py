import folium
import streamlit as st
import pandas as pd
import geopandas as gpd
import seaborn as sns
from streamlit_folium import folium_static
import matplotlib.pyplot as plt

# Judul landing page
st.set_page_config(page_title="Infografis Pelanggan", layout="wide")
st.title("Infografis Pelanggan")

customer_geolocation_df = pd.read_csv('main_data.csv')

st.subheader("Persebaran Data Pelanggan")

with st.sidebar:
    quartile = st.selectbox(
        label = "Filter berdasarkan kategori jumlah pelanggan",
        options = ('Semua Data', 'Terendah', 'Menengah', 'Tertinggi')
    )

geometry = gpd.points_from_xy(customer_geolocation_df.geolocation_lng, customer_geolocation_df.geolocation_lat, crs="EPSG:4326")
gdf = gpd.GeoDataFrame(data=customer_geolocation_df, geometry=geometry)

# Mendapatkan kuartil untuk mengklasifikasikan banyaknya pelanggan
quantiles = gdf['customer_total_by_state'].quantile([1/3, 2/3])

if quartile == 'Terendah':
    gdf = gdf[(gdf['customer_total_by_state'] <= quantiles.loc[1/3])]
elif quartile == 'Menengah':
    gdf = gdf[(gdf['customer_total_by_state'] > quantiles.loc[1/3]) & (gdf['customer_total_by_state'] < quantiles.loc[2/3])]
elif quartile == 'Tertinggi':
    gdf = gdf[(gdf['customer_total_by_state'] >= quantiles.loc[2/3])]
else:
    gdf = gdf

# Mendapatkan rata-rata seluruh koordinat untuk visualisasi
lat = gdf['geolocation_lat'].mean()
long = gdf['geolocation_lng'].mean()

# Mendefinisikan peta dengan perbesaran sesuai dengan koordinat yang telah dirata-rata
map = folium.Map(location=[lat, long], tiles="CartoDB Positron", zoom_start=4)

geo_df_list = [[point.xy[1][0], point.xy[0][0]] for point in gdf.geometry]

# Menginput data vektor ke dalam peta
for i, row in gdf.iterrows():
    coordinates = [row['geometry'].xy[1][0], row['geometry'].xy[0][0]]

    if row['customer_total_by_state'] <= quantiles.loc[1/3]:
        color = "red"
    elif row['customer_total_by_state'] > quantiles.loc[1/3] and row['customer_total_by_state'] < quantiles.loc[2/3]:
        color = "orange"
    else:
        color = "green"

    map.add_child(
        folium.Marker(
            location=coordinates,
            popup=(
                "<strong>"
                + "State : "
                + row['geolocation_state']
                + "</strong>"
                + "<br>"
                + "Total Customer : " 
                + str(row['customer_total_by_state'])
            ),
            icon=folium.Icon(color=color)
        )
    )

# Menambahkan data vektor ke folium
folium_static(map, width=1412, height=800)

st.subheader("Jumlah Pelanggan di Negara Bagian")

fig, ax = plt.subplots(figsize=(20, 10))

sns.barplot(x='customer_total_by_state', 
            y='geolocation_state', 
            data=gdf.sort_values('customer_total_by_state', ascending=False), 
            palette='magma', 
            orient='h',
            ax=ax)

ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=10)
ax.tick_params(axis='y', labelsize=15)
st.pyplot(fig)

st.caption('Copyright (c) Hanif Arafah Mustofa 2023')