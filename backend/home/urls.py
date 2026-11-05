from django.urls import path

from .views import HomeView, SiteContentView

urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    path("site/", SiteContentView.as_view(), name="site"),
]
