from django.apps import AppConfig


class TitlesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pemors.titles"

    def ready(self):
        import pemors.titles.signals  # noqa: F401
