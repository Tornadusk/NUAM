from django.urls import path
from . import views

app_name = 'calificaciones'

urlpatterns = [
    path('mantenedor/', views.mantenedor_calificaciones, name='mantenedor'),
]

