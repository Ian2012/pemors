from celery import Celery

app = Celery("pemors")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
