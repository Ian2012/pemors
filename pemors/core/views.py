from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = "pages/about.html"


about_view = AboutView.as_view()
