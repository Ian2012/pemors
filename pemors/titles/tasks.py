from celery import shared_task
from celery.utils.log import get_task_logger

from pemors.titles.recommender import Recommender

logger = get_task_logger(__name__)


@shared_task
def train_recommender():
    Recommender().train(celery_logger=logger)
