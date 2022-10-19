from django.contrib import admin
from django.contrib.admin import TabularInline

from .models import (
    Aka,
    Crew,
    Genre,
    HistoricalRecommender,
    KnownFor,
    Person,
    Rating,
    Title,
    TitleGenre,
    UserRating,
    UserTasks,
)


class TitleGenreInline(TabularInline):
    model = TitleGenre


class KnownForInline(TabularInline):
    model = KnownFor

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        queryset = formset.form.base_fields["person"].queryset
        queryset = queryset.select_related("known_for")
        formset.form.base_fields["person"].queryset = queryset
        return formset


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_filter = ["type"]
    list_display = ["id", "type", "primary_title", "start_year", "runtime"]
    inlines = [TitleGenreInline]


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "num_votes", "average_rating"]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_filter = ["name"]
    list_display = ["id", "name"]


@admin.register(Aka)
class AkaAdmin(admin.ModelAdmin):
    list_filter = ["region", "language", "is_original_title"]
    list_display = ["region", "language", "is_original_title", "value", "title"]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["birth_year", "death_year", "primary_name", "profession"]
    inlines = [KnownForInline]
    # list_select_related = ['known_for']


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ["title", "person", "category", "job", "characters"]


@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ["rating", "user", "title"]


@admin.register(HistoricalRecommender)
class HistoricalRecommenderAdmin(admin.ModelAdmin):
    list_display = ["id", "created"]


@admin.register(UserTasks)
class UserTasksAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "task_result"]
