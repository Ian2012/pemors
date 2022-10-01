from django.urls import path

from pemors.titles.views import coldstart_view, title_detail_view

app_name = "titles"
urlpatterns = [
    path("coldstart", view=coldstart_view, name="coldstart"),
    path("<str:id>", view=title_detail_view, name="title"),
]
