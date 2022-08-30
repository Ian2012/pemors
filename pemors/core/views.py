import pandas as pd
from django.db.models import Case, When
from django.views.generic import TemplateView

from pemors.titles.models import Rating, Title, UserRating


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["recommended_movies"] = recommend_movies(self.request.user)
        return context_data


def get_default_titles():
    return [rating.title for rating in Rating.objects.all()[:10]]


def recommend_movies(user):
    if not user.is_authenticated:
        return get_default_titles()

    movie_rating = pd.DataFrame(list(UserRating.objects.all().values()))
    if movie_rating.empty:
        return get_default_titles()

    print(movie_rating.head())
    userRatings = movie_rating.pivot_table(
        index=["user_id"], columns=["title_id"], values="rating"
    )
    userRatings = userRatings.fillna(0, axis=1)
    corrMatrix = userRatings.corr(method="pearson")

    user = pd.DataFrame(list(UserRating.objects.filter(user=user).values())).drop(
        ["user_id", "id"], axis=1
    )
    user_filtered = [tuple(x) for x in user.values]
    movie_id_watched = [each[0] for each in user_filtered]

    similar_movies = pd.DataFrame()
    for movie, rating in user_filtered:
        similar_movies = similar_movies.append(
            get_similar(movie, rating, corrMatrix), ignore_index=True
        )

    movies_id = list(similar_movies.sum().sort_values(ascending=False).index)
    movies_id_recommend = [each for each in movies_id if each not in movie_id_watched]
    preserved = Case(
        *[When(pk=pk, then=pos) for pos, pk in enumerate(movies_id_recommend)]
    )
    movie_list = list(
        Title.objects.filter(id__in=movies_id_recommend).order_by(preserved)[:10]
    )

    return movie_list


def get_similar(movie_name, rating, corrMatrix):
    similar_ratings = corrMatrix[movie_name] * (rating - 2.5)
    similar_ratings = similar_ratings.sort_values(ascending=False)
    return similar_ratings


home_view = HomeView.as_view()


class AboutView(TemplateView):
    template_name = "pages/about.html"


about_view = AboutView.as_view()
