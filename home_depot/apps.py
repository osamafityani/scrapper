from django.apps import AppConfig


class HomeDepotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home_depot'

    def ready(self):
        import home_depot.signals
