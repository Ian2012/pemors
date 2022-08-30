from django.core.management.base import BaseCommand

from pemors.users.ml.predict import Model


class Command(BaseCommand):
    help = "Train the models"

    def handle(self, *args, **options):
        Model().train()
