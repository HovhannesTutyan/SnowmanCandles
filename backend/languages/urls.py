from django.contrib import admin
from django.urls import path

from . import views

# Mounted under /admin/languages/, before the admin's own URLs. admin_view() lets in
# signed-in staff only (others go to the login page).
urlpatterns = [
    path("translate/", admin.site.admin_view(views.translate_view), name="languages_translate"),
    path("missing/", admin.site.admin_view(views.missing_view), name="languages_missing"),
]
