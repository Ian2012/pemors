from django.urls import path

from pemors.titles.views import title_detail_view

app_name = "titles"
urlpatterns = [path("<str:id>", view=title_detail_view, name="title")]
