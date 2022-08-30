from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from pemors.titles.models import Title, UserRating


class TitleDetailView(LoginRequiredMixin, DetailView):
    model = Title
    slug_field = "id"
    slug_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        _filter = {"user": self.request.user, "title": context_data["title"]}
        context_data["rating"] = UserRating.objects.filter(**_filter).first()
        return context_data


title_detail_view = TitleDetailView.as_view()
