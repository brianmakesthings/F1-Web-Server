from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('lap_times', views.lap_times, name='lap_times'),
    path('events', views.events, name='events'),
    path('drivers', views.drivers, name='drivers'),
]