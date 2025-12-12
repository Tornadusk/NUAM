from django.urls import path
from . import views
from .views import exportar_datos_view

app_name = 'calificaciones'

urlpatterns = [
    path('mantenedor/', views.mantenedor_calificaciones, name='mantenedor'),
    path('exportar/<str:formato>/', exportar_datos_view, name='exportar_datos'),
]

