import pickle

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer

TRAITS = ["OPN", "CON", "EXT", "AGR", "NEU"]


class Predictor:
    def __init__(self):
        self.models = {}
        self.load_models()

    def load_models(self):
        for trait in TRAITS:
            with open(f"ml/training/{trait}_model.pkl", "rb") as f:
                x = pickle.load(f)
                self.models[trait] = x

    def predict_status(self, X):
        predictions = []
        for trait in TRAITS:
            model = self.models[trait]

            trait_scores = model.predict_status(X, regression=True).reshape(1, -1)
            trait_categories = model.predict_status(X, regression=False)
            trait_categories_probs = model.predict_proba(X)

            temp = {
                "trait": trait,
                "pred_s": trait_scores.flatten()[0],
                "pred_c": str(trait_categories[0]),
                "pred_prob_c": trait_categories_probs[:, 1][0],
            }
            predictions.append(temp)

        return predictions

    def predict_personality(self, statuses):
        predictions = {}
        for status in statuses:
            predictions[status.value] = self.predict_status([status.value])

        return predictions

    def accuracy(self, x_test, y_test):
        print("Accuracy")
        for trait, model_trait in self.models.items():
            print("Trait", model_trait.score(x_test, y_test))


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

    def predict_status(self, X, regression=True):
        X = self.tfidf.transform(X)
        if regression:
            return self.rfr.predict(X)
        else:
            return self.rfc.predict(X)

    def predict_proba(self, X, regression=False):
        X = self.tfidf.transform(X)
        if regression:
            raise ValueError("Cannot predict probabilites of a regression!")
        else:
            return self.rfc.predict_proba(X)

    def train(self):
        for trait in traits:
            self._train_trait(trait, regression=True)
            self._train_trait(trait, regression=False)
            with open(f"ml/training/{trait}_model.pkl", "wb") as f:
                pickle.dump(self, f)

    def _fit(self, trait, X, y, regression=True):
        print(
            f"---- Fitting trait {trait} using {'regression' if regression else 'classifier'} model..."
        )
        X = self.tfidf.fit_transform(X)
        if regression:
            self.rfr = self.rfr.fit(X, y)
        else:
            self.rfc = self.rfc.fit(X, y)

    def _train_trait(self, trait, regression=False):
        print(
            f"---- Preparing data for {trait} using {'regression' if regression else 'classifier'} model..."
        )

        X = self.dataframe["STATUS"]

        y_column = trait_score_dict[trait] if regression else trait_cat_dict[trait]
        y = self.dataframe[y_column]

        self._fit(trait, X, y, regression)

    def _read_csv(self):
        print("-- Reading myPersonality CSV...")
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