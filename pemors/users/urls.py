from django.urls import path

from pemors.users.views import user_detail_view, user_personality_view

app_name = "users"
urlpatterns = [
    path("me/", view=user_detail_view, name="detail"),
    path("personality", view=user_personality_view, name="personality"),
]
