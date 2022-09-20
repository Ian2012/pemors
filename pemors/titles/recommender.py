from collections import defaultdict

import pandas as pd
from django.db.models import Count
from surprise import Dataset, KNNWithZScore, Reader, accuracy
from surprise.model_selection import train_test_split

from pemors.titles.models import UserRating


class MovieRecommender:
    prediction = None

    # def __init__(self):
    # self.predictions = None
    # self.load_data()

    def load_data(self):
        print("Loading data")
        users = (
            UserRating.objects.values("user")
            .annotate(total=Count("user"))
            .filter(total__gte=10)
            .values("user")
        )
        user_ratings = UserRating.objects.filter(user__in=users).values()
        dataframe = pd.DataFrame(list(user_ratings))
        data = Dataset.load_from_df(
            dataframe[["user_id", "title_id", "rating"]], Reader(rating_scale=(1, 10))
        )

        self.train(data)

    def train(self, data):
        print("Training")
        bsl_options = {"method": "als", "n_epochs": 5, "reg_u": 12, "reg_i": 5}
        sim_options = {"name": "pearson_baseline"}
        trainset, testset = train_test_split(data, test_size=0.25)
        algo = KNNWithZScore(bsl_options=bsl_options, sim_options=sim_options)
        predictions = algo.fit(trainset).test(testset)
        accuracy.rmse(predictions)

        self.predictions = predictions

    def recommend(self, user, n=10):

        top_n = defaultdict(list)
        for uid, iid, true_r, est, _ in filter(
            lambda x: x[0] == user.id, self.predictions
        ):
            top_n[uid].append((iid, est))

        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]

        print(top_n[user.id])
        return top_n[user.id]


# KNNWithZScore
# KNNWithMeans: Es lento de entrenar, da predicciones sobre nuevos datos
