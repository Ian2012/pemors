import logging
import random

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, TemplateView

from pemors.titles.api.serializers import TitleSerializer
from pemors.titles.models import Title, UserRating
from pemors.titles.tasks import recalculate_recommendations_for_user_task

logger = logging.getLogger(__name__)


@method_decorator(cache_page(0), name="dispatch")
class TitleDetailView(LoginRequiredMixin, DetailView):
    model = Title
    slug_field = "id"
    slug_url_kwarg = "id"
    context_object_name = "title"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        _filter = {"user": self.request.user, "title": context_data["title"]}
        context_data["rating"] = UserRating.objects.filter(**_filter).first()
        context_data["title_data"] = TitleSerializer(
            instance=context_data["title"]
        ).data
        return context_data


class ColdStart(LoginRequiredMixin, TemplateView):
    template_name = "titles/coldstart.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        logger.info(f"Generating most rated movie list for user {self.request.user}")

        title_counter = list(
            UserRating.objects.values("title_id")
            .annotate(total=Count("title_id"))
            .filter(total__gte=100)
            .values("title_id", "total")
        )
        title_counter = sorted(title_counter, key=lambda d: d["total"], reverse=True)
        ratings = UserRating.objects.filter(user=self.request.user).values_list(
            "title_id", flat=True
        )
        titles = [
            title["title_id"]
            for title in title_counter
            if title["title_id"] not in ratings
        ]
        titles = random.choices(titles, k=200)
        random_items = Title.objects.filter(id__in=titles).select_related("rating")
        context_data["movies"] = TitleSerializer(random_items, many=True).data
        random.shuffle(context_data["movies"])
        context_data["needed_movies"] = settings.NEEDED_MOVIES
        return context_data

    def dispatch(self, *args, **kwargs):
        if self.request.user.rating_counter >= settings.NEEDED_MOVIES:
            return redirect(reverse("home"))
        return super().dispatch(*args, **kwargs)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        if not self.request.user.is_updated:
            recalculate_recommendations_for_user_task.delay(self.request.user.id)
        else:
            logger.info(f"Skipping recalculation for user {self.request.user.email}")
        return super().get_context_data(**kwargs)


home_view = HomeView.as_view()

title_detail_view = TitleDetailView.as_view()

coldstart_view = ColdStart.as_view()
