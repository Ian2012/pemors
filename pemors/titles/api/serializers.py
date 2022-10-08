from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from pemors.titles.models import Title, UserRating


class UserRatingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = UserRating
        fields = "__all__"

    def create(self, validated_data):
        user_rating, created = UserRating.objects.update_or_create(
            user=validated_data["user"],
            title=validated_data["title"],
            defaults={"rating": validated_data["rating"]},
        )
        return user_rating

    def get_unique_together_validators(self):
        return []


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = "__all__"
