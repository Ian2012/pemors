import logging

from django.views.generic import TemplateView

from pemors.titles.recommender import Recommender
from pemors.users.models import User

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "pages/home.html"
    movie_recommender = Recommender()

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            logger.info(f"Recommending movies for user {self.request.user.email}")
            context_data["recommended_movies"] = self.movie_recommender.recommend(
                User.objects.prefetch_related(
                    "ratings", "ratings__title", "profile"
                ).get(id=self.request.user.id),
                use_genre_preferences=True,
            )
        return context_data


home_view = HomeView.as_view()


class AboutView(TemplateView):
    template_name = "pages/about.html"


about_view = AboutView.as_view()
