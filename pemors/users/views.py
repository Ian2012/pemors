from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView

from pemors.titles.models import UserRating
from pemors.users.forms import QUESTIONS, UserPersonalityForm
from pemors.users.models import Profile

User = get_user_model()


class UserDetailView(LoginRequiredMixin, TemplateView):
    model = User
    template_name = "users/user_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, TemplateView):
    model = UserRating


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail")


user_redirect_view = UserRedirectView.as_view()


def user_personality_view(request):
    if request.method == "POST":
        data = request.POST
        form = UserPersonalityForm(data=data)
        if form.is_valid():
            calculate_user_personality_with_form(form, request.user)
            return redirect("home")
        else:
            return render(request, "users/personality.html", {"form": form})
    else:
        form = UserPersonalityForm()
    return render(request, "users/personality.html", {"form": form})


def calculate_user_personality_with_form(form, user):
    scores = [0 for _ in range(0, 5)]
    for i, questiondata in enumerate(QUESTIONS):
        answer = int(form.cleaned_data[f"question_{i}"])
        scores[int(questiondata["type"]) - 1] += (
            answer if questiondata["math"] == "+" else 5 - (answer - 1)
        )

    profile, _ = Profile.objects.get_or_create(user=user)
    profile.ext = scores[0] / 10
    profile.agr = scores[1] / 10
    profile.con = scores[2] / 10
    profile.neu = scores[3] / 10
    profile.opn = scores[4] / 10
    profile.save()
