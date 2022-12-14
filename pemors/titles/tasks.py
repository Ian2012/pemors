from celery import shared_task
from celery.utils.log import get_task_logger
from django_celery_results.models import TaskResult

from pemors.titles.models import UserTasks
from pemors.titles.utils import train_for_user

logger = get_task_logger(__name__)


@shared_task(bind=True, name="Train recommender")
def train_recommender_for_user_task(self, user_id):
    UserTasks.objects.create(
        user_id=user_id, task_result=TaskResult.objects.get(task_id=self.request.id)
    )
    train_for_user(user_id, logger, train_recommender=True)
    return user_id


@shared_task(name="Recalculate recommendations")
def recalculate_recommendations_for_user_task(user_id):
    train_for_user(user_id, logger, train_recommender=False)
    return user_id
