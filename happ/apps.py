from django.apps import AppConfig

class HappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'happ'

    def ready(self):
        import happ.signals  # Ensure signals are imported
