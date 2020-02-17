import dash
import json
import datetime
import requests
import pandas as pd
from utils import LoadData, BuildMap
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}], external_stylesheets=external_stylesheets)
app.title = 'Real-Time Velib Monitor'

server = app.server


app.layout = html.Div(
    children=[
        # Interval component for live clock
        dcc.Interval(id="interval", interval=1 * 1000, n_intervals=0),

        html.H1(children='Real-Time Velib'),
            
        dcc.Markdown(children='''### Velib Geo Data Analysis in Paris and suburbs'''),
        
        html.P(
            id="live_clock",
            children=datetime.datetime.now().strftime("%H:%M:%S"),
        ),

        html.Iframe(id='map', title='Interactive Map' , srcDoc=open('web-application/map.html', 'r').read(), width='100%', height='600')
])

# =====Callbacks=====

# Callback to update live clock
@app.callback(Output("live_clock", "children"), [Input("interval", "n_intervals")])
def update_time(n):
    return datetime.datetime.now().strftime("%H:%M:%S")

if __name__ == '__main__':
    app.run_server(debug=True)