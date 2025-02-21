from django.apps import AppConfig


class EvenementsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'evenements'
    def ready(self):
        import evenements.signals  # Import des signaux au démarrage de l'application