from django.apps import AppConfig

class LittlelemonapidrfConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'LittleLemonAPIDRF'

    def ready(self):
        import LittleLemonAPIDRF.signals
