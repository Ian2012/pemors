import logging

from pemors.users.ml.predict import Predictor
from pemors.utils.twiteer import get_user_tweets

predictor = Predictor()
logger = logging.getLogger(__name__)


def predict_personality_for_user(user):
    if not user.statuses.all():
        logger.info(f"Fetching tweets of user {user.email}")
        get_user_tweets(user)

    logger.info(f"Predicting personality for user {user.email}")
    prediction = predictor.predict_status(
        x=[status.value for status in user.statuses.all()]
    )
    total = {}
    for trait in prediction:
        total[trait["trait"]] = trait["pred_s"]
    logger.info(f"Personality for user {user.email}: {total}")
    user.profile.agr = total["AGR"]
    user.profile.con = total["CON"]
    user.profile.ext = total["EXT"]
    user.profile.neu = total["NEU"]
    user.profile.opn = total["OPN"]
    user.profile.save()
