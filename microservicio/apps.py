from django.apps import AppConfig


class MicroservicioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'microservicio'
    verbose_name = 'Microservicios NUAM'

    def ready(self):
        """
        Importa las señales cuando Django carga la app
        """
        import microservicio.signals  # noqa


