import logging
import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.views.generic import DetailView, TemplateView

from pemors.titles.api.serializers import TitleSerializer
from pemors.titles.models import Title, UserRating

logger = logging.getLogger(__name__)


class TitleDetailView(LoginRequiredMixin, DetailView):
    model = Title
    slug_field = "id"
    slug_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        _filter = {"user": self.request.user, "title": context_data["title"]}
        context_data["rating"] = UserRating.objects.filter(**_filter).first()
        return context_data


class ColdStart(LoginRequiredMixin, TemplateView):
    template_name = "titles/coldstart.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        logger.info(f"Generating most rated movie list for user {self.request.user}")

        title_counter = (
            UserRating.objects.values("title_id")
            .annotate(total=Count("title_id"))
            .filter(total__gte=500)
            .values("title_id", "total")
        )
        title_counter = sorted(title_counter, key=lambda d: d["total"], reverse=True)
        titles = [title["title_id"] for title in title_counter]
        titles = random.choices(titles, k=10)
        random_items = Title.objects.filter(id__in=titles)

        context_data["movies"] = TitleSerializer(random_items, many=True).data

        return context_data


title_detail_view = TitleDetailView.as_view()

coldstart_view = ColdStart.as_view()
