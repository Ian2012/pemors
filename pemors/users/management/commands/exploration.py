import time

import pandas as pd
from django.core.management.base import BaseCommand
from django.db.models import Count
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from surprise import (  # KNNBasic,; KNNWithZScore,; SlopeOne,
    NMF,
    SVD,
    BaselineOnly,
    CoClustering,
    Dataset,
    KNNBaseline,
    KNNWithMeans,
    NormalPredictor,
    Reader,
    SVDpp,
    accuracy,
)
from surprise.model_selection import cross_validate, train_test_split

from pemors.titles.models import Title, UserRating
from pemors.users.admin import User


class Command(BaseCommand):
    help = "Configure default credentials"
    titles = []
    indices = []
    cosine_sim = []
    tfidf_matrix = None

    def handle(self, *args, **options):
        self.collaborative_filtering()

    def load_cosine_sim(self, tfidf_matrix):
        self.cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    def content_based_recommender(self):
        print("Loading movies")
        smd = pd.DataFrame(Title.objects.all().values()[0:20000])
        print("Altering IDs")
        smd["id"].apply(lambda x: int(x[2:]))
        print("Generating descriptions")
        smd["description"] = smd["type"] + smd["primary_title"] + str(smd["start_year"])
        print("Init tfidvectorizer")
        tf = TfidfVectorizer(
            analyzer="word", ngram_range=(1, 2), min_df=0, stop_words="english"
        )
        print("Fit transform")
        tfidf_matrix = tf.fit_transform(smd["description"])
        print("Cosine sim")

        start_time = time.time()
        self.cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        print("--- %s seconds ---" % (time.time() - start_time))
        self.titles = smd["primary_title"]
        self.indices = pd.Series(smd.index, index=smd["primary_title"])

        x = input("Movie title:")
        while x != "":
            print(self.get_recommendations(x))
            x = input("Movie title:")

    def get_recommendations(self, title):
        idx = self.indices[title]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:31]
        movie_indices = [i[0] for i in sim_scores]
        return self.titles.iloc[movie_indices]

    def collaborative_filtering(self):
        users = (
            UserRating.objects.values("user")
            .annotate(total=Count("user"))
            .filter(total__gte=10)
            .values("user")
        )
        user_ratings = UserRating.objects.filter(user__in=users).values()

        dataframe = pd.DataFrame(list(user_ratings))
        print("Filtered ratings:", dataframe.shape)
        # dataframe['title_id'] = dataframe['title_id'].apply(lambda x: int(x[2:]))
        # print(dataframe.head())

        print("Init dataset")
        data = Dataset.load_from_df(
            dataframe[["user_id", "title_id", "rating"]], Reader(rating_scale=(1, 10))
        )

        # self.benchmark(data)
        self.train(data)

    def benchmark(self, data):
        benchmark = []
        # Iterate over all algorithms
        for algorithm in [
            SVD(),
            SVDpp(),
            NMF(),
            NormalPredictor(),
            KNNBaseline(),
            KNNWithMeans(),
            BaselineOnly(),
            CoClustering(),
        ]:
            # Perform cross validation
            print("Cross validating", algorithm)
            results = cross_validate(
                algorithm, data, measures=["RMSE"], cv=3, verbose=True
            )

            # Get results & append algorithm name
            tmp = pd.DataFrame.from_dict(results).mean(axis=0)
            tmp = tmp.append(
                pd.Series(
                    [str(algorithm).split(" ")[0].split(".")[-1]], index=["Algorithm"]
                )
            )
            benchmark.append(tmp)

        print(pd.DataFrame(benchmark).set_index("Algorithm").sort_values("test_rmse"))

    def train(self, data):
        # bsl_options = {"method": "als", "n_epochs": 5, "reg_u": 12, "reg_i": 5}
        # sim_options = {"name": "pearson_baseline"}
        trainset, testset = train_test_split(data, test_size=0.25)
        algo = SVD()
        predictions = algo.fit(trainset).test(testset)

        accuracy.rmse(predictions)

        # self.inspect(trainset, predictions)
        count = 0
        for user, recommendations in self.get_top_n(predictions).items():
            if count > 5:
                break
            count += 1
            user = User.objects.get(id=user)
            print(user.id, recommendations, "\n")
            print(
                "User ratings:",
                [
                    (rating.title.id, rating.title.primary_title)
                    for rating in user.ratings.all()
                ],
            )
            print("\n")

    def get_top_n(self, predictions, n=10):
        """Return the top-N recommendation for each user from a set of predictions.

        Args:
            predictions(list of Prediction objects): The list of predictions, as
                returned by the test method of an algorithm.
            n(int): The number of recommendation to output for each user. Default
                is 10.

        Returns:
        A dict where keys are user (raw) ids and values are lists of tuples:
            [(raw item id, rating estimation), ...] of size n.
        """

        from collections import defaultdict

        # First map the predictions to each user.
        top_n = defaultdict(list)
        for uid, iid, true_r, est, _ in predictions:
            top_n[uid].append((iid, true_r, est))

        # Then sort the predictions for each user and retrieve the k highest ones.
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]

        return top_n
