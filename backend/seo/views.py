"""robots.txt and sitemap.xml for search engines."""

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import translation
from django.views.decorators.cache import cache_control

from care.models import CarePage
from decorate.models import DecoratePage
from home.models import HomePageContent
from ingredients.models import IngredientsPage
from shop.models import Candle, Collection

from .pages import DEFAULT_LANG, LANGS, localize, site_origin

# Search engines may read these at most once an hour from a cache.
CACHE = {"public": True, "max_age": 60 * 60}


@cache_control(**CACHE)
def robots_txt(request):
    """Everything may be crawled except the admin. The API stays open: Google runs the
    React app and needs it. The basket and checkout say "noindex" themselves."""
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "",
        f"Sitemap: {site_origin(request)}/sitemap.xml",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


def _entries(origin):
    """One entry per page and language: (url, lastmod, alternates, images)."""
    content = HomePageContent.load()

    def updated(*objects):
        dates = [obj.updated_at for obj in objects if obj and getattr(obj, "updated_at", None)]
        return max(dates).date().isoformat() if dates else ""

    pages = [
        ("/", updated(content), []),
        ("/candle-care", updated(CarePage.load()), []),
        ("/ingredients", updated(IngredientsPage.load()), []),
        ("/decorate", updated(DecoratePage.load()), []),
    ]
    for model, kind in [(Candle, "candles"), (Collection, "collections")]:
        for item in model.objects.prefetch_related("gallery").order_by("pk"):
            images = [item.image] + [g.image for g in item.gallery.all()]
            pages.append((f"/{kind}/{item.slug}", updated(item), [i for i in images if i]))

    for path, lastmod, images in pages:
        alternates = [(lang, origin + localize(path, lang)) for lang in LANGS]
        alternates.append(("x-default", origin + localize(path, DEFAULT_LANG)))
        image_urls = [
            image.url if image.url.startswith(("http://", "https://")) else origin + image.url
            for image in images
        ]
        for lang in LANGS:
            yield {
                "loc": origin + localize(path, lang),
                "lastmod": lastmod,
                "alternates": alternates,
                "images": image_urls,
            }


@cache_control(**CACHE)
def sitemap_xml(request):
    with translation.override(DEFAULT_LANG):
        entries = list(_entries(site_origin(request)))
    xml = render_to_string("seo/sitemap.xml", {"entries": entries})
    return HttpResponse(xml, content_type="application/xml; charset=utf-8")
