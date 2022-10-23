import logging

from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from surprise import BaselineOnly

from pemors.titles.api.serializers import TitleSerializer, UserRatingSerializer
from pemors.titles.models import Title, UserRating, UserTasks
from pemors.titles.recommender import Recommender

logger = logging.getLogger(__name__)


class UserRatingViewSet(viewsets.ModelViewSet):
    serializer_class = UserRatingSerializer
    queryset = UserRating.objects.all()


class RecommendationView(APIView):
    permission_classes = []
    movie_recommender = Recommender(algo=BaselineOnly)
    PAGE_SIZE = 30

    def get(self, request):
        logger.info(f"Loading recommendations for user {request.user.email}")

        recommendations = self.movie_recommender.recommend(
            user=request.user,
            page=int(request.GET.get("page")) if request.GET.get("page") else 0,
            page_size=self.PAGE_SIZE,
        )

        movie_data = TitleSerializer(
            Title.objects.filter(
                id__in=[recommendation["title"] for recommendation in recommendations]
            ),
            many=True,
        )

        data = {
            "movies": movie_data.data,
            "page_size": self.PAGE_SIZE,
        }
        return JsonResponse(status=200, data=data)


recommendation_view = RecommendationView.as_view()


class ProgressAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = {}
        query = UserTasks.objects.filter(user=request.user)
        if query.exists():
            data["status"] = query[0].task_result.status
        else:
            data["status"] = "Not found"
        return JsonResponse(status=200, data=data)


progress_view = ProgressAPI.as_view()
