#!/usr/bin/env python
from flask import Flask, render_template, flash, request
import logging, io, base64, os, datetime
from datetime import timedelta
import os
import json
import time
import folium
import requests
import numpy as np
import pandas as pd
from folium.plugins import MarkerCluster

# global variables
velib_op = None

app = Flask(__name__)

def LoadData():

    # set the endpoint API URL
    url = "https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel&lang=fr&rows=-1"

    # make the call
    resp = requests.get(url)

    #grab the results returned in json format
    data = resp.json()

    # Track request_time for comparison with record_timestamp
    request_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


    col = ['nbfreeedock',
        'station_state',
        'creditcard',
        'overflowactivation',
        'station_code',
        'nbedock',
        'nbebike',
        'nbbike',
        'station_name',
        'nbbikeoverflow',
        'geo',
        'kioskstate',
        'request_time',
        'record_timestamp',
        'recordid']

    # Initialize the dataframe 
    df = pd.DataFrame(columns=col)

    nb_stations = data['nhits']
    print("[INFO] Numbers of stations :", nb_stations)

    # loop over the stations
    for i in range(nb_stations):

        # Add all the values from the fields key and 3 other relevants informations
        df.loc[len(df)] = list(data['records'][i]['fields'].values()) + [request_time, data['records'][i]['record_timestamp'], data['records'][i]['recordid']]
        

    # Not very optimize, maybe there is a better index and a better way to do it
    df.set_index('recordid', inplace=True)

    # converting datatypes 
    df = df.infer_objects()
    df['record_timestamp'] = pd.to_datetime(df['record_timestamp'], infer_datetime_format=True)
    df['request_time'] = pd.to_datetime(df['request_time'], format="%Y-%m-%d %H:%M:%S")

    # Available bikes
    velib_op = df[df['station_state']=='Operative']
    # Extract lat and long
    velib_op['lat'] = velib_op['geo'].apply(lambda x: float(x[0]))
    velib_op['long'] = velib_op['geo'].apply(lambda x: float(x[1]))

    velib_op['available_velib'] = velib_op.apply(lambda x: x['nbbike'] + x['nbebike'], axis=1)
    
    print("[INFO] Done.")

    return velib_op

def BuildMap(velib_op):
    m = folium.Map(
        location=[48.85, 2.35],
        tiles='Cartodb Positron',
        zoom_start=11
    )

    marker_cluster = MarkerCluster(
        name='1000 clustered icons',
        overlay=True,
        control=False,
        icon_create_function=None
    )

    for k, v in velib_op.iterrows():
        location = v.geo[0], v.geo[1]
        marker = folium.Marker(location=location)
        popup = 'Station:{}<br>Number of Velibs:{}<br>Number of free Docks:{}'.format(v.station_name, v.available_velib, v.nbfreeedock)
        folium.Popup(popup).add_to(marker)
        marker_cluster.add_child(marker)

    marker_cluster.add_to(m)

    m.save("C:/Users/maxen/OneDrive - DXC Production/Industrialized AI Open Badge Boot Camp/3 Build AI Data Pipelines/real-time-velib/real-time-velib-analysis/web-application/templates/map.html")

    return

@app.before_first_request
def startup():
    global velib_op

    # prepare velib data
    velib_op = LoadData()



@app.route("/")
def index():
    BuildMap(velib_op)

    return render_template('index.html')



if __name__=='__main__':

    app.run(debug=True)
