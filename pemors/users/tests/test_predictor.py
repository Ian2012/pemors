from django.test import TestCase
from pandas import DataFrame
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer

from pemors.users.ml.predict import Model, Predictor
from pemors.users.models import Profile, User
from pemors.users.utils import predict_personality_for_user


class ModelTestCase(TestCase):
    def setUp(self):
        self.model = Model()

    def test_has_properties(self):
        self.assertIn("rfc", self.model.__dict__)
        self.assertIn("rfr", self.model.__dict__)
        self.assertIn("tfidf", self.model.__dict__)
        self.assertIn("dataframe", self.model.__dict__)

    def test_has_right_class(self):
        self.assertIsInstance(self.model.rfc, RandomForestClassifier)
        self.assertIsInstance(self.model.rfr, RandomForestRegressor)
        self.assertIsInstance(self.model.tfidf, TfidfVectorizer)
        self.assertIsInstance(self.model.dataframe, DataFrame)

    def test_read_csv(self):
        dataframe = self.model._read_csv()
        assert dataframe is not None


class PredictorTestCase(TestCase):
    def setUp(self):
        self.predictor = Predictor()
        self.user = User.objects.create(email="dummy@email.com", username="dummy")
        self.profile = Profile.objects.create(user=self.user)
        self.tweets = ["Hello", "Dummy message", "Dummy dummy dummy"]
        for tweet in self.tweets:
            self.user.statuses.create(value=tweet)

    def test_can_predict_text(self):
        self.assertIsInstance(
            self.predictor.predict_status(["dummy text", "dummy text 222"]), list
        )

    def test_can_predict_personality_for_user(self):
        predict_personality_for_user(self.user)
        self.assertIsNot(self.user.profile.agr, 0)
        self.assertIsNot(self.user.profile.con, 0)
        self.assertIsNot(self.user.profile.opn, 0)
        self.assertIsNot(self.user.profile.ext, 0)
        self.assertIsNot(self.user.profile.neu, 0)
