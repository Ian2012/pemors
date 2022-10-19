import logging
from decimal import Decimal

import pandas as pd
import surprise
from django.conf import settings
from django.core.cache import cache
from surprise import Dataset, Reader

from pemors.titles.models import HistoricalRecommender, Title, UserRating
from pemors.users.models import User

logger = logging.getLogger(__name__)

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
RECOMMENDATION_CACHE_FORMAT = "recommendations_{}"
AVAILABLE_TITLES_CACHE_KEY = "available_titles"


class Recommender:
    dataframe = None
    dataset = None

    def recommend(self, user, page=1, page_size=30, use_genre_preferences=True):
        recommendations = cache.get(RECOMMENDATION_CACHE_FORMAT.format(user.id))
        if not recommendations:
            recommendations = self.generate_recommendations(user)
            logger.info(f"Saving recommendations for user {user.email} in cache")
            cache.set(RECOMMENDATION_CACHE_FORMAT.format(user.id), recommendations)

        i, j = page * page_size, (page + 1) * page_size
        recommendations = recommendations[i:j]
        titles_id = (recommendation["title"] for recommendation in recommendations)

        titles = list(
            Title.objects.filter(id__in=titles_id)
            .select_related("rating")
            .prefetch_related("genres__genre")
            .all()
        )

        titles = {title.id: title for title in titles}

        for i, recommendation in enumerate(recommendations):
            recommendations[i]["title"] = titles[recommendation["title"]]

        if use_genre_preferences:
            return self.sort_recommendations_by_genre_preferences(recommendations, user)

        return recommendations

    def load_recommender(self, user=None, force=False, celery_logger=None):
        if celery_logger:
            current_logger = celery_logger
        else:
            current_logger = logger
        current_logger.info("Verify model is trained for user")

        cache_results = cache.get_many(
            [settings.RECOMMENDER_CACHE_KEY, AVAILABLE_TITLES_CACHE_KEY]
        )
        algo = cache_results.get(settings.RECOMMENDER_CACHE_KEY)
        available_titles = cache_results.get(AVAILABLE_TITLES_CACHE_KEY)

        if force or not algo:
            algo, available_titles = self.train(user, logger)
            cache.set(
                settings.RECOMMENDER_CACHE_KEY,
                algo,
            )
            cache.set(AVAILABLE_TITLES_CACHE_KEY, available_titles)
            HistoricalRecommender.objects.create()

        if not available_titles:
            available_titles = self._load_available_titles()

        return algo, available_titles

    def calculate_prediction(self, user):
        algo, available_titles = self.load_recommender(user)
        logger.info(f"Predicting movies for user {user.email}")
        predictions = (algo.predict(user.id, title.id) for title in available_titles)

        return predictions

    def train(self, user=None, celery_logger=None):
        if celery_logger:
            current_logger = celery_logger
        else:
            current_logger = logger
        current_logger.info(
            f"Training recommender {f'for user {user.email}' if user else ''}"
        )
        dataset, available_titles = self._load_data(user)
        current_logger.info(
            f"Building full trainset {f'for user {user.email}' if user else ''}"
        )
        trainset = dataset.build_full_trainset()
        algo = surprise.SVD()
        current_logger.info(f"Fitting SVD {f'for user {user.email}' if user else ''}")
        algo.fit(trainset)

        return algo, available_titles

    def _load_data(self, user=None):
        dataframe = pd.DataFrame(
            list(
                UserRating.objects.filter(
                    user__rating_counter__gte=settings.NEEDED_MOVIES
                ).values()
            )
        )
        dataset = Dataset.load_from_df(
            dataframe[["user_id", "title_id", "rating"]],
            Reader(rating_scale=(1, 10)),
        )

        available_titles = dataframe["title_id"].unique()

        if user:
            available_titles = Title.objects.filter(id__in=available_titles).exclude(
                id__in=user.ratings.values_list("title_id", flat=True)
            )
        else:
            available_titles = Title.objects.filter(id__in=available_titles)
        return dataset, available_titles

    def _load_available_titles(self):
        logger.info("Loading available titles")

        available_titles = cache.get(AVAILABLE_TITLES_CACHE_KEY)
        if available_titles:
            logger.info("Loading available titles from cache")
            return available_titles

        users = User.objects.filter(
            rating_counter__gte=settings.NEEDED_MOVIES
        ).prefetch_related("ratings")
        user_ratings = UserRating.objects.filter(user_id__in=users).values("title_id")

        available_titles = Title.objects.filter(id__in=user_ratings)
        logger.info("Saving available titles in cache")
        cache.set(AVAILABLE_TITLES_CACHE_KEY, available_titles)
        return available_titles

    def generate_recommendations(self, user):
        logger.info(f"Generating recommendations for user {user.email}")
        predictions = self.calculate_prediction(user)
        recommendations = (
            {"title": iid, "rating": Decimal(est)}
            for uid, iid, true_r, est, _ in predictions
        )
        return sorted(recommendations, key=lambda d: d["rating"])

    def sort_recommendations_by_genre_preferences(self, recommendations, user):
        logger.info(f"Sorting recommendations by user genre preferences {user.email}")
        profile = user.profile
        user_profile = [profile.opn, profile.con, profile.ext, profile.agr, profile.neu]
        user_genre_preferences = {}

        for genre, values in USER_GENRE_PREFERENCES.items():
            distance = sum(
                abs(user_trait - Decimal(genre_trait))
                for user_trait, genre_trait in zip(user_profile, values)
            )
            user_genre_preferences[genre] = 10 - distance

        for i, recommendation in enumerate(recommendations):
            recommendations[i]["genres"] = [
                title_genre.genre.name
                for title_genre in recommendations[i]["title"].genres.all()
            ]

            most_valuable_genre_value = 0
            counter = 0
            for genre in recommendation["genres"]:
                if (
                    genre in USER_GENRE_PREFERENCES.keys()
                    and user_genre_preferences[genre] < most_valuable_genre_value
                ):
                    most_valuable_genre_value += user_genre_preferences[genre]
                    counter += 1
            if counter != 0:
                recommendations[i]["predicted_rating"] = (
                    recommendation["rating"] / 2 + most_valuable_genre_value / counter
                )
            else:
                recommendations[i]["predicted_rating"] = recommendation["rating"]

            # TODO Resolver esto
        recommendations.sort(key=lambda x: x["predicted_rating"], reverse=True)
        return recommendations
