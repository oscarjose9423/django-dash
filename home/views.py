from home import apps
from django.shortcuts import render
from plotly.offline import plot
import plotly.graph_objects as go
# Create your views here.
# from dash_apps.finished_apps.simpleexample import app 

def consumer_expenditures(request):
    return render(request, 'home/consumer_expenditures.html')

def nutrition(request):
    return render(request, 'home/nutrition.html')

def industries(request):
    return render(request, 'home/industries.html')