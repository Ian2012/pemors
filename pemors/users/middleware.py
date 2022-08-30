from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
from django.urls import reverse

from pemors.users.models import Profile
from pemors.users.utils import predict_personality_for_user


def check_userprofile_middleware(get_response):
    def middleware(request: WSGIRequest):
        if not request.user.is_authenticated:
            return get_response(request)

        if request.path.__contains__(settings.ADMIN_URL):
            return get_response(request)

        if not Profile.objects.filter(user=request.user).exists():
            if SocialAccount.objects.filter(user=request.user).exists():
                Profile.objects.create(user=request.user)
                predict_personality_for_user(request.user)
            else:
                if not request.path == reverse("users:personality"):
                    return redirect("users:personality")
        return get_response(request)

    return middleware
