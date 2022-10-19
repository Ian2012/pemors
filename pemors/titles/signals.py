import logging

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from pemors.titles.models import UserRating
from pemors.titles.tasks import train_recommender_for_user_task

logger = logging.getLogger(__name__)


def common_user_rating_signal(instance):
    instance.user.rating_counter = UserRating.objects.filter(
        user_id=instance.user.id
    ).count()

    instance.user.save()
    if instance.user.in_recommender:  # User is new
        logger.info("Skipping training")
    elif should_train(instance.user):
        train_recommender_for_user_task.delay(instance.user.id)
    else:
        logger.info("Skipping training")


@receiver(post_save, sender=UserRating)
def user_rating_created_counter_signal(sender, instance, created, **kwargs):
    if created:
        common_user_rating_signal(instance)


@receiver(post_delete, sender=UserRating)
def user_rating_deleted_counter_signal(sender, instance, **kwargs):
    common_user_rating_signal(instance)


def should_train(user):
    return user.rating_counter >= settings.NEEDED_MOVIES
