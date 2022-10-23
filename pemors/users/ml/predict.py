import logging
import pickle
from os.path import exists

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer

TRAITS = ["OPN", "CON", "EXT", "AGR", "NEU"]

logger = logging.getLogger(__name__)


class Predictor:
    def load_model(self, trait):
        with open(f"ml/training/{trait}_model.pkl", "rb") as file:
            return pickle.load(file)

    def predict_status(self, x):
        predictions = []
        for trait in TRAITS:
            model = self.load_model(trait)

            trait_scores = model.predict_status(x, regression=True).reshape(1, -1)
            trait_categories = model.predict_status(x, regression=False)
            trait_categories_probs = model.predict_proba(x)

            temp = {
                "trait": trait,
                "pred_s": trait_scores.flatten()[0],
                "pred_c": str(trait_categories[0]),
                "pred_prob_c": trait_categories_probs[:, 1][0],
            }
            predictions.append(temp)

        return predictions

    def accuracy(self, x_test, y_test):
        logger.debug("Accuracy")
        for trait in TRAITS:
            model = self.load_model(trait)
            logging.debug("Trait", model.score(x_test, y_test))


trait_cat_dict = {
    "O": "cOPN",
    "C": "cCON",
    "E": "cEXT",
    "A": "cAGR",
    "N": "cNEU",
    "OPN": "cOPN",
    "CON": "cCON",
    "EXT": "cEXT",
    "AGR": "cAGR",
    "NEU": "cNEU",
    "Openness": "cOPN",
    "Conscientiousness": "cCON",
    "Extraversion": "cEXT",
    "Agreeableness": "cAGR",
    "Neuroticism": "cNEU",
}
trait_score_dict = {
    "O": "sOPN",
    "C": "sCON",
    "E": "sEXT",
    "A": "sAGR",
    "N": "sNEU",
    "OPN": "sOPN",
    "CON": "sCON",
    "EXT": "sEXT",
    "AGR": "sAGR",
    "NEU": "sNEU",
    "Openness": "sOPN",
    "Conscientiousness": "sCON",
    "Extraversion": "sEXT",
    "Agreeableness": "sAGR",
    "Neuroticism": "sNEU",
}
traits = ["OPN", "CON", "EXT", "AGR", "NEU"]


class Model:
    def __init__(self):
        self.rfr = RandomForestRegressor(
            bootstrap=True,
            max_features="sqrt",
            min_samples_leaf=1,
            min_samples_split=2,
            n_estimators=200,
        )
        self.rfc = RandomForestClassifier(max_features="sqrt", n_estimators=110)
        self.tfidf = TfidfVectorizer(stop_words="english", strip_accents="ascii")
        self.dataframe = self._read_csv()

    def predict_status(self, x, regression=True):
        x = self.tfidf.transform(x)
        if regression:
            return self.rfr.predict(x)
        else:
            return self.rfc.predict(x)

    def predict_proba(self, x, regression=False):
        x = self.tfidf.transform(x)
        if regression:
            raise ValueError("Cannot predict probabilites of a regression!")
        else:
            return self.rfc.predict_proba(x)

    def train(self):
        for trait in traits:
            path_to_file = f"ml/training/{trait}_model.pkl"

            if exists(path_to_file):
                logger.info(
                    f"Trait already trained. Skipping {trait}",
                )
                continue

            self._train_trait(trait, regression=True)
            self._train_trait(trait, regression=False)
            with open(path_to_file, "wb") as file:
                pickle.dump(self, file)

    def _fit(self, trait, x, y, regression=True):
        logging.info(
            f"Fitting trait {trait} using {'regression' if regression else 'classifier'} model"
        )
        x = self.tfidf.fit_transform(x)
        if regression:
            self.rfr = self.rfr.fit(x, y)
        else:
            self.rfc = self.rfc.fit(x, y)

    def _train_trait(self, trait, regression=False):
        logging.info(
            f"Preparing data for {trait} using {'regression' if regression else 'classifier'} model"
        )
        x = self.dataframe["STATUS"]
        y_column = trait_score_dict[trait] if regression else trait_cat_dict[trait]
        y = self.dataframe[y_column]

        self._fit(trait, x, y, regression)

    def _read_csv(self):
        logging.info("Reading myPersonality CSV")
        df = pd.read_csv(
            "ml/data/myPersonality/mypersonality_final.csv", encoding="ISO-8859-1"
        )
        trait_columns = ["cOPN", "cCON", "cEXT", "cAGR", "cNEU"]
        d = {"y": True, "n": False}

        for trait in trait_columns:
            df[trait] = df[trait].map(d)

        return df


if __name__ == "__main__":
    Model().train()
