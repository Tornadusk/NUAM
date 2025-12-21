"""
URLs para Microservicios NUAM
"""
from django.urls import path
from .views.testing import (
    testing_dashboard,
    api_testing_status,
    api_run_tests,
    api_test_list,
)
from .views import (
    # Gráficos
    graficos_dashboard,
    api_estadisticas_generales,
    api_calificaciones_por_pais,
    api_calificaciones_por_moneda,
    api_actividad_reciente,
    api_cargas_detalle,
    api_cargas_por_corredora,
    api_auditoria_resumen,
    api_tipos_cambio_resumen,
    api_kpis_operativos,
    api_refrescar_grafico,
    api_exportar_grafico,
    api_exportar_grafico_imagen,
    # Comprobantes
    api_generar_comprobante,
    # Tipos de Cambio
    tipos_cambio_dashboard,
    api_tipos_cambio_por_pais,
    api_tipos_cambio_actuales,
    api_obtener_tipos_cambio,
    api_generar_datos_simulados,
    # Pulsar
    pulsar_dashboard,
    api_pulsar_status,
    api_pulsar_topics,
    api_pulsar_mensajes_recientes,
    api_pulsar_publicar_test,
    # Mercados
    mercados_dashboard,
    api_mercados_resumen,
    api_mercados_historia,
)

app_name = 'microservicio'

urlpatterns = [
    # Vistas de dashboards
    path('graficos/', graficos_dashboard, name='graficos_dashboard'),
    path('tipos-cambio/', tipos_cambio_dashboard, name='tipos_cambio_dashboard'),
    path('mercados/', mercados_dashboard, name='mercados_dashboard'),
    
    # APIs REST para datos de gráficos
    path('api/estadisticas-generales/', api_estadisticas_generales, name='api_estadisticas_generales'),
    path('api/calificaciones-por-pais/', api_calificaciones_por_pais, name='api_calificaciones_por_pais'),
    path('api/calificaciones-por-moneda/', api_calificaciones_por_moneda, name='api_calificaciones_por_moneda'),
    path('api/actividad-reciente/', api_actividad_reciente, name='api_actividad_reciente'),
    
    # APIs REST adicionales para gráficos expandidos
    path('api/cargas-detalle/', api_cargas_detalle, name='api_cargas_detalle'),
    path('api/cargas-por-corredora/', api_cargas_por_corredora, name='api_cargas_por_corredora'),
    path('api/auditoria-resumen/', api_auditoria_resumen, name='api_auditoria_resumen'),
    path('api/tipos-cambio-resumen/', api_tipos_cambio_resumen, name='api_tipos_cambio_resumen'),
    path('api/tipos-cambio-por-pais/', api_tipos_cambio_por_pais, name='api_tipos_cambio_por_pais'),
    path('api/tipos-cambio-por-pais/<str:codigo_pais>/', api_tipos_cambio_por_pais, name='api_tipos_cambio_por_pais_codigo'),
    path('api/tipos-cambio-actuales/', api_tipos_cambio_actuales, name='api_tipos_cambio_actuales'),
    path('api/obtener-tipos-cambio/', api_obtener_tipos_cambio, name='api_obtener_tipos_cambio'),
    path('api/generar-datos-simulados/', api_generar_datos_simulados, name='api_generar_datos_simulados'),
    path('api/kpis-operativos/', api_kpis_operativos, name='api_kpis_operativos'),
    path('api/refrescar-grafico/', api_refrescar_grafico, name='api_refrescar_grafico'),
    
    # Endpoints de exportación
    path('api/exportar/<str:tipo_grafico>/<str:formato>/', api_exportar_grafico, name='api_exportar_grafico'),
    path('api/exportar-grafico-imagen/', api_exportar_grafico_imagen, name='api_exportar_grafico_imagen'),
    
    # Endpoint para generar comprobantes
    path('api/generar-comprobante/', api_generar_comprobante, name='api_generar_comprobante'),
    path('api/generar-comprobante/<int:calificacion_id>/', api_generar_comprobante, name='api_generar_comprobante_id'),
    
    # Microservicio de Pulsar - Visualización
    path('pulsar/', pulsar_dashboard, name='pulsar_dashboard'),
    path('api/pulsar/status/', api_pulsar_status, name='api_pulsar_status'),
    path('api/pulsar/topics/', api_pulsar_topics, name='api_pulsar_topics'),
    path('api/pulsar/mensajes-recientes/', api_pulsar_mensajes_recientes, name='api_pulsar_mensajes_recientes'),
    path('api/pulsar/publicar-test/', api_pulsar_publicar_test, name='api_pulsar_publicar_test'),
    
    # Microservicio de Mercados (Bolsa)
    path('api/mercados/resumen/', api_mercados_resumen, name='api_mercados_resumen'),
    path('api/mercados/historia/', api_mercados_historia, name='api_mercados_historia'),
    
    # Microservicio de Testing - Visualización
    path('testing/', testing_dashboard, name='testing_dashboard'),
    path('api/testing/status/', api_testing_status, name='api_testing_status'),
    path('api/testing/run/', api_run_tests, name='api_run_tests'),
    path('api/testing/list/', api_test_list, name='api_test_list'),
]


