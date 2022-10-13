from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField, Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for Personality Aware Movie Recommendation System.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    rating_counter = models.IntegerField(default=0)

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def is_syntethic_user(self):
        return self.username.startswith(settings.SYNTETHIC_USER_PATTERN)

    class Meta:
        indexes = [
            models.Index(
                fields=["rating_counter"], condition=Q(rating_counter__gte=10)
            ),
            models.Index(fields=["username"]),
        ]


class Status(models.Model):
    value = models.TextField()
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="statuses")


class Profile(models.Model):
    user = models.OneToOneField(
        to="User",
        on_delete=models.CASCADE,
        related_name="profile",
        related_query_name="profile",
    )
    agr = models.DecimalField(default=0, decimal_places=3, max_digits=4)
    con = models.DecimalField(default=0, decimal_places=3, max_digits=4)
    ext = models.DecimalField(default=0, decimal_places=3, max_digits=4)
    neu = models.DecimalField(default=0, decimal_places=3, max_digits=4)
    opn = models.DecimalField(default=0, decimal_places=3, max_digits=4)
