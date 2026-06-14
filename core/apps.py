from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        import sys

        if 'runserver' in sys.argv:
            try:
                from django.contrib.sessions.models import Session
                Session.objects.all().delete()
            except Exception:
                pass