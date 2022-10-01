import sys
from decimal import Decimal

import pandas as pd
from django.conf import settings
from django.db.models import Count
from surprise import Dataset, Reader

from pemors.titles.models import Title, UserRating
from pemors.users.models import Profile, User

# from os import path


USER_GENRE_PREFERENCES = {
    "Action": [3.87, 3.45, 3.57, 3.58, 2.72],
    "Crime": [3.83, 3.44, 3.43, 3.47, 2.99],
    "Adventure": [3.91, 3.56, 3.54, 3.68, 2.61],
    "Animation": [4.04, 3.22, 3.26, 3.35, 3.02],
    "Comedy": [3.88, 3.44, 3.58, 3.60, 2.75],
    "Drama": [3.99, 3.43, 3.66, 3.60, 2.86],
    "Documentary": [4.12, 3.45, 3.37, 3.53, 2.85],
    "Fantasy": [4.04, 3.34, 3.27, 3.54, 2.87],
    "Game-Show": [3.58, 3.45, 3.30, 3.68, 2.90],
    "Horror": [3.90, 3.38, 3.52, 3.47, 2.91],
    "Film-Noir": [4.34, 3.35, 3.33, 3.37, 2.97],
    "music": [3.98, 3.32, 3.56, 3.55, 3.02],
    "musical": [3.98, 3.32, 3.56, 3.55, 3.02],
    "mystery": [3.91, 3.53, 3.51, 3.61, 2.76],
    "news": [3.97, 3.58, 3.58, 3.54, 2.74],
    "Reality-TV": [3.76, 3.56, 3.61, 3.58, 2.75],
    "Romance": [3.84, 3.48, 3.62, 3.62, 2.85],
    "Sci-Fi": [3.99, 3.55, 3.33, 3.57, 2.73],
    "Sport": [3.67, 3.58, 3.67, 3.64, 2.52],
    "Talk": [3.81, 3.58, 3.58, 3.68, 2.67],
    "Thriller": [3.85, 3.54, 3.51, 3.59, 2.76],
    "War": [3.82, 3.51, 3.49, 3.50, 2.71],
}


class Recommender:
    dataframe = None
    dataset = None

    def recommend(self, user: User, k=20, use_genre_preferences=True):
        algo, titles_available = self._load_data(user)
        predictions = [algo.predict(user.id, iid) for iid in titles_available]
        recommendations = self.get_recommendation(predictions)[0:k]

        for i, recommendation in enumerate(recommendations):
            title = Title.objects.get(id=recommendation["title"])
            recommendations[i]["title"] = title

        if use_genre_preferences:
            return self.sort_recommendations_by_genre_preferences(recommendations, user)

        return recommendations

    def sort_recommendations_by_genre_preferences(self, recommendations, user):
        user_genre_preferences = self.calculate_user_genre_preferences(user)

        for i, recommendation in enumerate(recommendations):
            recommendations[i]["genres"] = [
                title_genre.genre.name
                for title_genre in recommendations[i]["title"].genres.all()
            ]

            most_valuable_genre_value = sys.maxsize
            for genre in recommendation["genres"]:
                if (
                    genre in USER_GENRE_PREFERENCES.keys()
                    and user_genre_preferences[genre] < most_valuable_genre_value
                ):
                    most_valuable_genre_value = user_genre_preferences[genre]

            recommendations[i]["predicted_rating"] = (
                recommendation["rating"] / 2 + most_valuable_genre_value
            )
        recommendations.sort(key=lambda x: x["predicted_rating"], reverse=True)
        return recommendations

    def calculate_user_genre_preferences(self, user):
        profile = Profile.objects.get(user=user)
        user_profile = [profile.opn, profile.con, profile.ext, profile.agr, profile.neu]
        user_genre_preferences = {}

        for genre, values in USER_GENRE_PREFERENCES.items():
            distance = sum(
                abs(user_trait - Decimal(genre_trait))
                for user_trait, genre_trait in zip(user_profile, values)
            )
            user_genre_preferences[genre] = distance

        sorted_user_genre_preferences = sorted(
            user_genre_preferences.items(), key=lambda x: x[1], reverse=True
        )
        print(sorted_user_genre_preferences)
        return user_genre_preferences

    def _load_data(self, user):
        users = (
            UserRating.objects.values("user")
            .annotate(total=Count("user"))
            .filter(total__gte=10)
            .values("user")
        )
        self.dataframe = pd.DataFrame(
            list(UserRating.objects.filter(user__in=users).values())
        )

        self.dataset = Dataset.load_from_df(
            self.dataframe[["user_id", "title_id", "rating"]],
            Reader(rating_scale=(1, 10)),
        )

        rated_titles = user.ratings.values_list("title_id", flat=True)
        titles_available = self.dataframe["title_id"].unique()
        titles_available = [
            title for title in titles_available if title not in rated_titles
        ]

        if user.profile.recommender is None:
            trainset = self.dataset.build_full_trainset()
            algo = settings.RECOMMENDER_ALGORITHM
            algo.fit(trainset)
            user.profile.recommender = algo
            user.profile.save()
        else:
            algo = user.profile.recommender

        return algo, titles_available

    def get_recommendation(self, predictions):
        recommendations = []
        for uid, iid, true_r, est, _ in predictions:
            recommendations.append(
                {"title": iid, "rating": Decimal(est)},
            )

        recommendations.sort(key=lambda x: x["rating"], reverse=True)
        return recommendations
