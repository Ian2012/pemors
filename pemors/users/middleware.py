import logging

from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

from pemors.users.models import Profile
from pemors.users.utils import predict_personality_for_user

logger = logging.getLogger(__name__)


class CheckUserProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        if request.path.__contains__(settings.ADMIN_URL):
            return self.get_response(request)

        if not Profile.objects.filter(user=request.user).exists():
            if SocialAccount.objects.filter(user=request.user).exists():
                Profile.objects.create(user=request.user)
                predict_personality_for_user(request.user)
            else:
                if not request.path == reverse("users:personality"):
                    logger.debug(
                        f"User personality of {request.user.email} not calculated. Redirect"
                    )
                    return redirect("users:personality")

        if request.user.rating_counter < settings.NEEDED_MOVIES:
            excluded_paths = [
                reverse("account_logout"),
                reverse("titles:coldstart"),
                reverse("users:personality"),
                reverse("titles_api:user_rating-list"),
                reverse("titles_api:progress"),
            ]
            if request.path not in excluded_paths and "__debug__" not in request.path:
                logger.debug(f"User {request.user.email} in coldstart")
                return redirect("titles:coldstart")

        return self.get_response(request)
