from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
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

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})


class Status(models.Model):
    value = models.TextField()
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="statuses")


class Profile(models.Model):
    user = models.ForeignKey(
        to="User", on_delete=models.CASCADE, related_name="profile"
    )
    agr = models.FloatField(default=0)
    con = models.FloatField(default=0)
    ext = models.FloatField(default=0)
    neu = models.FloatField(default=0)
    opn = models.FloatField(default=0)
