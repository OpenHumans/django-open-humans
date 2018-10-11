from django.apps import AppConfig


class OpenHumansConfig(AppConfig):
    name = 'openhumans'

    def ready(self):
        import openhumans.receivers  # noqa
