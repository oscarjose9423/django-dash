import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash

#%%SERVER

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

external_stylesheets = [
    'https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css',
    '/style.css'
]

external_scripts = [
    'https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js'
]

app = DjangoDash('Nutrition_app', external_stylesheets=external_stylesheets)

#%%LOAD DATABASES



app.layout = html.Div(
    className = "row card",
    id = 'graph-1',
    children = [

            html.Div([
                html.H1('NUTRITION'),
                # dcc.Graph(
                #     id='slider-graph', 
                #     animate=True, 
                #     style={"backgroundColor": "#1a2d46", 'color': '#ffffff'}),
                # dcc.Slider(
                #     id='slider-updatemode',
                #     marks={i: '{}'.format(i) for i in range(20)},
                #     max=20,
                #     value=2,
                #     step=1,
                #     updatemode='drag',
                # ),
                ])
    ]
)

