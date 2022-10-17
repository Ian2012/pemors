from django.urls import include, path
from rest_framework.routers import DefaultRouter

from pemors.titles.api.views import UserRatingViewSet, recommendation_view, train_view

router = DefaultRouter()
router.register(r"user_rating", UserRatingViewSet, basename="user_rating")
urlpatterns = [
    path("", include(router.urls)),
    path("train", train_view, name="train"),
    path("recommend", recommendation_view, name="recommend"),
]
app_name = "titles_api"
