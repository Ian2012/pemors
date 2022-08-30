from rest_framework import viewsets

from pemors.titles.api.serializers import UserRatingSerializer
from pemors.titles.models import UserRating


class UserRatingViewSet(viewsets.ModelViewSet):
    serializer_class = UserRatingSerializer
    queryset = UserRating.objects.all()
