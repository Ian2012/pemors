from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from pemors.users.models import User


class Title(models.Model):
    id = models.CharField(max_length=16, primary_key=True, unique=True)
    type = models.CharField(max_length=32)
    primary_title = models.CharField(max_length=512)
    original_title = models.CharField(max_length=512)
    start_year = models.IntegerField(null=True)
    runtime = models.IntegerField(null=True)

    def __str__(self) -> str:
        return self.primary_title


class Genre(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __repr__(self):
        return self.name


class TitleGenre(models.Model):
    title = models.ForeignKey(to=Title, related_name="genres", on_delete=models.CASCADE)
    genre = models.ForeignKey(to=Genre, related_name="titles", on_delete=models.CASCADE)

    class Meta:
        unique_together = ["title", "genre"]


class Rating(models.Model):
    title = models.OneToOneField(
        to=Title, related_name="rating", on_delete=models.CASCADE, unique=True
    )
    average_rating = models.FloatField()
    num_votes = models.IntegerField()

    class Meta:
        ordering = ["-average_rating"]


class Aka(models.Model):
    title = models.ForeignKey(to=Title, related_name="akas", on_delete=models.CASCADE)
    value = models.CharField(max_length=2048)
    region = models.CharField(max_length=15)
    language = models.CharField(max_length=15)
    is_original_title = models.BooleanField()
    attributes = models.CharField(max_length=256)
    types = models.CharField(max_length=256)


class Person(models.Model):
    id = models.CharField(max_length=16, primary_key=True, unique=True)
    primary_name = models.CharField(max_length=256)
    birth_year = models.IntegerField(null=True)
    death_year = models.IntegerField(null=True)
    profession = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.primary_name} ({self.profession})"


class KnownFor(models.Model):
    title = models.ForeignKey(to=Title, on_delete=models.CASCADE)
    person = models.ForeignKey(
        to=Person, related_name="known_for", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ["title", "person"]


class Crew(models.Model):
    title = models.ForeignKey(to=Title, related_name="crew", on_delete=models.CASCADE)
    person = models.ForeignKey(
        to=Person, related_name="cast_of", on_delete=models.CASCADE
    )
    category = models.CharField(max_length=2048)
    job = models.CharField(max_length=2048)
    characters = models.CharField(max_length=2048)


class UserRating(models.Model):
    user = models.ForeignKey(
        to=User, related_name="ratings", on_delete=models.CASCADE, null=True
    )
    title = models.ForeignKey(
        to=Title, related_name="ratings", on_delete=models.CASCADE
    )
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)])

    class Meta:
        unique_together = ["user", "title"]
