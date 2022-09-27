from os import path

import pandas as pd
import surprise
from django.conf import settings
from django.db.models import Count
from surprise import Dataset, Reader

from pemors.titles.models import Title, UserRating


class Recommender:
    dataframe = None
    dataset = None

    def recommend(self, user, k=20):
        algo, titles_available = self._load_data(user)
        predictions = [algo.predict(user.id, iid) for iid in titles_available]
        recommendations = self.get_recommendation(predictions)
        for i, recommendation in enumerate(recommendations[0:k]):
            title = Title.objects.get(id=recommendation["title"])
            recommendations[i]["title"] = title

        # TODO Sort by user genre preferences
        return recommendations[0:k]

    def _load_data(self, user):
        if self.dataframe is None:
            users = (
                UserRating.objects.values("user")
                .annotate(total=Count("user"))
                .filter(total__gte=100)
                .values("user")
            )
            self.dataframe = pd.DataFrame(
                list(UserRating.objects.filter(user__in=users).values())
            )
        if self.dataset is None:
            self.dataset = Dataset.load_from_df(
                self.dataframe[["user_id", "title_id", "rating"]],
                Reader(rating_scale=(1, 10)),
            )

        rated_titles = user.ratings.values_list("title_id", flat=True)
        titles_available = self.dataframe["title_id"].unique()
        titles_available = [
            title for title in titles_available if title not in rated_titles
        ]

        trainset = self.dataset.build_full_trainset()
        algo = settings.RECOMMENDER_ALGORITHM

        file_name = path.expanduser(f"dump_file{user.id}")
        if path.exists(file_name):
            _, algo = surprise.dump.load(file_name)
        else:
            algo.fit(trainset)
            surprise.dump.dump(file_name, algo=algo)

        return algo, titles_available

    def get_recommendation(self, predictions):
        recommendations = []
        for uid, iid, true_r, est, _ in predictions:
            recommendations.append(
                {"title": iid, "rating": est},
            )

        recommendations.sort(key=lambda x: x["rating"], reverse=True)
        return recommendations
