
from django.apps import AppConfig


class NeonConfig(AppConfig):

    name = 'django_neon'
    verbose_name = 'django_neon'

    def ready(self):
        # explizit imports:
        from .processing import pygmentssupport  # noqa
