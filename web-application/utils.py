import os
import json
import time
import folium
import requests
import numpy as np
import pandas as pd
from folium.plugins import MarkerCluster

def LoadData():
    """Load velib data from opendata API
    
    Returns:
        DataFrame: Clean Dataset with [lat, long, Available velib, Nom de la station,
                                Nombre de bornes disponible] columns
    """

    # set the endpoint API URL
    url = "https://opendata.paris.fr/explore/dataset/velib-disponibilite-en-temps-reel/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true&csv_separator=%3B"
        
    df = pd.read_csv(url, delimiter=";" )

    # Track request_time for comparison with record_timestamp
    request_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    df["Request_time"] = request_time

    df['Request_time'] = pd.to_datetime(df['Request_time'], format="%Y-%m-%d %H:%M:%S")

    # Available bikes
    velib_op = df[df['Etat des stations']=='Operative']
    
    # Extract latitude and longitude from geo
    velib_op['lat'] = velib_op['geo'].apply(lambda x: float(x.split(',')[0]))
    velib_op['long'] = velib_op['geo'].apply(lambda x: float(x.split(',')[1]))

    # Number of available velib
    velib_op['Available velib'] = velib_op.apply(lambda x: x['Nombre de vélo mécanique'] + x['Nombre vélo électrique'], axis=1)

    print("[INFO] Done.")

    return velib_op


def BuildMap(velib_op):
    """
    Create and save a folium map with operational velib in Paris and suburbs 
    
    Args:
        velib_op (DataFrame): Clean Dataset with [lat, long, Available velib, Nom de la station,
                                Nombre de bornes disponible] columns
    """
  
    m = folium.Map(
        location=[48.85, 2.35],
        tiles='Cartodb Positron',
        zoom_start=11
        )

    marker_cluster = MarkerCluster(
        name='Velib clustered',
        overlay=True,
        control=False,
        icon_create_function=None
    )

    for k, v in velib_op.iterrows():
        location = v.lat, v.long
        marker = folium.Marker(location=location)
        popup = 'Station:{}<br>Number of Velibs:{}<br>Number of available docks:{}'.format(v['Nom de la station'], v['Available velib'], v['Nombre de bornes disponibles'])
        folium.Popup(popup).add_to(marker)
        marker_cluster.add_child(marker)

    marker_cluster.add_to(m)

    m.save("C:/Users/maxen/OneDrive - DXC Production/Industrialized AI Open Badge Boot Camp/3 Build AI Data Pipelines/real-time-velib/real-time-velib-analysis/web-application/templates/map.html")

    return