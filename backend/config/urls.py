from urllib.parse import urlsplit

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

from care.views import CarePageView
from decorate.views import DecoratePageView
from ingredients.views import IngredientsPageView
from seo.views import robots_txt, sitemap_xml

from .views import serve_media, spa_index

admin.site.site_header = "HugCrafts Admin"
admin.site.site_title = "HugCrafts Admin"
admin.site.index_title = "Manage candles & collections"

urlpatterns = [
    path("robots.txt", robots_txt, name="robots"),
    path("sitemap.xml", sitemap_xml, name="sitemap"),
    path("admin/languages/", include("languages.urls")),
    path("admin/", admin.site.urls),
    path("api/", include("home.urls")),
    path("api/care/", CarePageView.as_view(), name="care"),
    path("api/ingredients/", IngredientsPageView.as_view(), name="ingredients"),
    path("api/decorate/", DecoratePageView.as_view(), name="decorate"),
    path("api/", include("orders.urls")),
    path("api/", include("shop.urls")),
]

# Uploaded files (with byte ranges, so videos play on iPhones too).
if settings.DEBUG or settings.SERVE_MEDIA:
    # MEDIA_URL can be a full address (see SITE_URL); only its path matters here.
    media_prefix = urlsplit(settings.MEDIA_URL).path.strip("/")
    urlpatterns += [
        re_path(
            rf"^{media_prefix}/(?P<path>.*)$", serve_media, {"document_root": settings.MEDIA_ROOT}
        ),
    ]

# Everything else is a page of the React app (when it has been built).
urlpatterns += [
    re_path(r"^(?!api/|admin/|media/|static/)(?P<path>.*)$", spa_index, name="spa"),
]
