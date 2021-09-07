from django_plotly_dash import DjangoDash

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

external_stylesheets = [
    'https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css',
    '/style.css'
]

external_scripts = [
    'https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js'
]


app = DjangoDash('Nutrition', external_stylesheets=external_stylesheets)