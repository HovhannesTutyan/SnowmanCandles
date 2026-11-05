from django.conf import settings
from django.http import FileResponse, Http404
from django.views.decorators.cache import never_cache


@never_cache
def spa_index(request, path=""):
    """The built React app's index.html, for every page URL (/candles/…, /decorate, …).

    React Router picks the page in the browser. Files under /assets/ are served by
    WhiteNoise before this view is reached.
    """
    index = settings.FRONTEND_DIST / "index.html"
    if not index.is_file():
        raise Http404("The frontend hasn't been built yet (run `npm run build` in frontend/).")
    return FileResponse(index.open("rb"), content_type="text/html; charset=utf-8")
