from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('lap_times', views.lap_times, name='lap_times'),
    path('tyre_usage', views.tyre_usage, name='tyre_usage'),
    path('compounds_lineplot', views.compounds_lineplot, name='compounds_lineplot'),
    path('compounds_boxplot', views.compounds_boxplot, name='compounds_boxplot'),

    # API endopoints
    path('events', views.events, name='events'),
    path('drivers', views.drivers, name='drivers'),
]