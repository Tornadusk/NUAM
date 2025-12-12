"""
URLs para Microservicios NUAM
"""
from django.urls import path
from . import views

app_name = 'microservicio'

urlpatterns = [
    # Vista de gráficos
    path('graficos/', views.graficos_dashboard, name='graficos_dashboard'),
    
    # APIs REST para datos de gráficos
    path('api/estadisticas-generales/', views.api_estadisticas_generales, name='api_estadisticas_generales'),
    path('api/calificaciones-por-pais/', views.api_calificaciones_por_pais, name='api_calificaciones_por_pais'),
    path('api/calificaciones-por-moneda/', views.api_calificaciones_por_moneda, name='api_calificaciones_por_moneda'),
    path('api/actividad-reciente/', views.api_actividad_reciente, name='api_actividad_reciente'),
    
    # APIs REST adicionales para gráficos expandidos
    path('api/cargas-detalle/', views.api_cargas_detalle, name='api_cargas_detalle'),
    path('api/cargas-por-corredora/', views.api_cargas_por_corredora, name='api_cargas_por_corredora'),
    path('api/auditoria-resumen/', views.api_auditoria_resumen, name='api_auditoria_resumen'),
    path('api/tipos-cambio-resumen/', views.api_tipos_cambio_resumen, name='api_tipos_cambio_resumen'),
    path('api/kpis-operativos/', views.api_kpis_operativos, name='api_kpis_operativos'),
    path('api/refrescar-grafico/', views.api_refrescar_grafico, name='api_refrescar_grafico'),
    
    # Endpoints de exportación
    path('api/exportar/<str:tipo_grafico>/<str:formato>/', views.api_exportar_grafico, name='api_exportar_grafico'),
    
    # Endpoint para generar comprobantes
    path('api/generar-comprobante/', views.api_generar_comprobante, name='api_generar_comprobante'),
    path('api/generar-comprobante/<int:calificacion_id>/', views.api_generar_comprobante, name='api_generar_comprobante_id'),
]


