from django.utils import translation
from django.utils.cache import patch_vary_headers

from .conf import CODES, SOURCE


class ApiLanguageMiddleware:
    """Answers API requests in the language asked for with ?lang=hy|en|ru.

    Translated model fields then read the Armenian or Russian text, falling back to
    English where a translation is empty. Everything else (the admin) stays in English.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        lang = request.GET.get("lang", "")
        if lang not in CODES:
            lang = SOURCE
        with translation.override(lang):
            response = self.get_response(request)
        response.headers["Content-Language"] = lang
        patch_vary_headers(response, ["Accept-Language"])
        return response
