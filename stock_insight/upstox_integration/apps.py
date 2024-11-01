from django.apps import AppConfig

class UpstoxIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'upstox_integration'

    def ready(self):
        import upstox_integration.signals
