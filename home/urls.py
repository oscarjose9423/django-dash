from django.urls import path
from . import views
from home.dash_apps.finished_apps import simpleexample
from home.dash_apps.finished_apps import nutrition
from home.dash_apps.finished_apps import industries

consumer_expenditures = '6u1s7w'
food_and_beverages_industries = '4Z4uKk'
nutrition_survey = 'u911K4'

urlpatterns = [
    path(consumer_expenditures, views.consumer_expenditures, name=consumer_expenditures),
    path(food_and_beverages_industries, views.industries, name=food_and_beverages_industries),
    path(nutrition_survey, views.nutrition, name=nutrition_survey),
    # path('consumer-expenditures/food-and-beverages', views.home, name='home')
    ]

# from django.urls import path
# from . import views
# from home.dash_apps.finished_apps.pages import consumer

# urlpatterns = [
#     path('dashboard', consumer.page, name='home')
# ]