import logging

import surprise
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from pemors.titles.api.serializers import TitleSerializer, UserRatingSerializer
from pemors.titles.models import Title, UserRating, UserTasks
from pemors.titles.recommender import RECOMMENDATION_CACHE_FORMAT, Recommender

logger = logging.getLogger(__name__)


class UserRatingViewSet(viewsets.ModelViewSet):
    serializer_class = UserRatingSerializer
    queryset = UserRating.objects.all()


class RecommendationView(APIView):
    permission_classes = []
    movie_recommender = Recommender(algo=surprise.SVD)
    PAGE_SIZE = 30

    def get(self, request):
        page = request.GET.get("page")
        page = int(page) if page else 0
        i = page * self.PAGE_SIZE
        j = (page + 1) * self.PAGE_SIZE
        data = {
            "movies": cache.get(RECOMMENDATION_CACHE_FORMAT.format(request.user.id))[
                i:j
            ],
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


class TitleAPIView(RetrieveAPIView):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


title_view = TitleAPIView.as_view()
