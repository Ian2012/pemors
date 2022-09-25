import pandas as pd
from django.conf import settings
from django.db.models import Count
from surprise import Dataset, Reader

from pemors.titles.models import Title, UserRating


class Recommender:
    dataframe = None
    dataset = None

    def recommend(self, user, k=20):
        algo, titles_available = self._load_data(user)
        # This can be cached while there are no new users nor movies

        predictions = [algo.predict(user.id, iid) for iid in titles_available]
        print("RECOMMENDING")
        recommendations = self.get_recommendation(predictions)
        for i, recommendation in enumerate(recommendations[0:k]):
            title = Title.objects.get(id=recommendation["title"])
            recommendations[i]["title"] = title

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
            print("LOADING")
        if self.dataset is None:
            self.dataset = Dataset.load_from_df(
                self.dataframe[["user_id", "title_id", "rating"]],
                Reader(rating_scale=(1, 10)),
            )
            print("LOADING")

        rated_titles = user.ratings.values_list("title_id", flat=True)
        titles_available = self.dataframe["title_id"].unique()
        titles_available = [
            title for title in titles_available if title not in rated_titles
        ]

        trainset = self.dataset.build_full_trainset()
        algo = settings.RECOMMENDER_ALGORITHM

        # TODO Create a model that stores the last time a fit happened, amount of users and ratings. Then,
        #  compare it with a count to verify if has changed.
        if self.has_changed():
            print("FITTING")
            algo.fit(trainset)

        return algo, titles_available

    def has_changed(self):
        return True

    def get_recommendation(self, predictions):
        recommendations = []
        for uid, iid, true_r, est, _ in predictions:
            recommendations.append(
                {"title": iid, "rating": est},
            )

        recommendations.sort(key=lambda x: x["rating"], reverse=True)
        return recommendations
