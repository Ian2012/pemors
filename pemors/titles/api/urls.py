from rest_framework.routers import DefaultRouter

from pemors.titles.api.views import UserRatingViewSet

router = DefaultRouter()
router.register(r"user_rating", UserRatingViewSet, basename="user_rating")
urlpatterns = router.urls
app_name = "titles_api"
