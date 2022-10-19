import datetime
import logging

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.timezone import utc

from pemors.titles.models import HistoricalRecommender, UserRating
from pemors.titles.tasks import train_recommender_for_user_task

logger = logging.getLogger(__name__)


@receiver(post_save, sender=UserRating)
def user_rating_created_counter_signal(sender, instance, created, **kwargs):
    if created:
        instance.user.rating_counter = UserRating.objects.filter(
            user_id=instance.user.id
        ).count()

    instance.user.in_recommender = False
    instance.user.save()
    if should_train(instance.user):
        train_recommender_for_user_task.delay(instance.user.id)
    else:
        logger.info("Skipping training")


@receiver(post_delete, sender=UserRating)
def user_rating_deleted_counter_signal(sender, instance, **kwargs):
    instance.user.rating_counter = UserRating.objects.filter(
        user_id=instance.user.id
    ).count()

    instance.user.in_recommender = False
    instance.user.save()
    if should_train(instance.user):
        train_recommender_for_user_task.delay(instance.user.id)
    else:
        logger.info("Skipping training")


def should_train(user):
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    try:
        history = HistoricalRecommender.objects.latest("created")
        timediff = now - history.created
        return user.rating_counter >= settings.NEEDED_MOVIES and (
            not user.in_recommender or timediff > datetime.timedelta(minutes=5)
        )
    except HistoricalRecommender.DoesNotExist:
        return user.rating_counter >= settings.NEEDED_MOVIES
