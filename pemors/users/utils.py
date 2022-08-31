from pemors.users.ml.predict import TRAITS, Predictor
from pemors.utils.twiteer import get_user_tweets

predictor = Predictor()


def predict_personality_for_user(user):
    if not user.statuses.all():
        get_user_tweets(user)

    predictions = predictor.predict_personality(statuses=user.statuses.all())
    total = {trait: 0 for trait in TRAITS}
    n = len(predictions)
    for key, traits in predictions.items():
        for trait in traits:
            total[trait["trait"]] += trait["pred_s"]
    total = {trait: value / n for trait, value in total.items()}
    user.profile.agr = total["AGR"]
    user.profile.con = total["CON"]
    user.profile.ext = total["EXT"]
    user.profile.neu = total["NEU"]
    user.profile.opn = total["OPN"]
    user.profile.save()
