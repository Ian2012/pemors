from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Configure default credentials"

    def handle(self, *args, **options):
        socialapp = SocialApp.objects.create(
            name="Twitter",
            client_id="QvsLgJhFgmnux0SvSkN2U1vId",
            secret="X8B2eBYK8TMxP2WEYUuRZiHumOCa8hwTIZYf9NLiaveMc0bbBi",
            provider="twitter",
        )
        socialapp.sites.add(Site.objects.get(id=settings.SITE_ID))
