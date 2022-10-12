import logging

from pemors.users.ml.predict import TRAITS, Predictor
from pemors.utils.twiteer import get_user_tweets

predictor = Predictor()
logger = logging.getLogger(__name__)


def predict_personality_for_user(user):
    if not user.statuses.all():
        logger.info(f"Fetching tweets of user {user.email}")
        get_user_tweets(user)

    logger.info(f"Predicting personality for user {user.email}")
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
