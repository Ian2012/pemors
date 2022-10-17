import logging

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from pemors.titles.api.serializers import TitleSerializer, UserRatingSerializer
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
        cache.set(settings.RECOMMENDER_CACHE_KEY, algo)
        return JsonResponse(status=200, data={"message": "Ready to start."})


train_view = TrainView.as_view()


class RecommendationView(APIView):
    permission_classes = []
    movie_recommender = Recommender()
    PAGE_SIZE = 30

    def get(self, request):
        logger.info(f"Loading recommendations for user {request.user.email}")

        recommendations = self.movie_recommender.recommend(
            user=request.user,
            page=int(request.GET.get("page")) if request.GET.get("page") else 0,
            page_size=self.PAGE_SIZE,
            use_genre_preferences=True,
        )

        movie_data = TitleSerializer(
            [recommendation["title"] for recommendation in recommendations],
            many=True,
        )

        data = {
            "movies": movie_data.data,
            "page_size": self.PAGE_SIZE,
        }
        return JsonResponse(status=200, data=data)


recommendation_view = RecommendationView.as_view()
