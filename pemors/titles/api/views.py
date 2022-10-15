import logging

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from pemors.titles.api.serializers import UserRatingSerializer
from pemors.titles.models import UserRating
from pemors.titles.recommender import Recommender

logger = logging.getLogger(__name__)


class UserRatingViewSet(viewsets.ModelViewSet):
    serializer_class = UserRatingSerializer
    queryset = UserRating.objects.all()


class TrainView(APIView):
    permission_classes = [IsAuthenticated]
    movie_recommender = Recommender()

    def get(self, request):
        logger.info(f"Training model for user {request.user.email}")
        algo, available_titles = self.movie_recommender._train(request.user)
        cache.set(
            settings.USER_CACHE_KEY.format(request.user.id),
            algo,
            timeout=60 * 60 * 24 * 360,
        )
        return JsonResponse(status=200, data={"message": "Ready to start."})


train_view = TrainView.as_view()
