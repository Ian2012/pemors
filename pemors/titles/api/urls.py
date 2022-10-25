from django.urls import include, path
from rest_framework.routers import DefaultRouter

from pemors.titles.api.views import (
    UserRatingViewSet,
    progress_view,
    recommendation_view,
    title_view,
)

router = DefaultRouter()
router.register(r"user_rating", UserRatingViewSet, basename="user_rating")
urlpatterns = [
    path("", include(router.urls)),
    path("recommend", recommendation_view, name="recommend"),
    path("progress", progress_view, name="progress"),
    path("<str:pk>", title_view, name="title_detail"),
]
app_name = "titles_api"
