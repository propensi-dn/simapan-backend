from django.apps import AppConfig


class MembersConfig(AppConfig):
    name = 'members'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        import members.signals
