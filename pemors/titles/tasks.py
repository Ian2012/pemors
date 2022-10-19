from celery import shared_task
from celery.utils.log import get_task_logger
from django_celery_results.models import TaskResult

from pemors.titles.models import UserTasks
from pemors.titles.utils import train_for_user

logger = get_task_logger(__name__)


@shared_task(bind=True)
def train_recommender_for_user_task(self, user_id):
    UserTasks.objects.create(
        user_id=user_id, task_result=TaskResult.objects.get(task_id=self.request.id)
    )
    train_for_user(user_id, logger)
    return user_id
