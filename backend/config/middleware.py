from urllib.parse import urlsplit

from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalHostMiddleware:
    """Sends www.<site> to <site> (SITE_URL), so Google sees one copy of the shop.

    Only the www address is redirected; other hosts (localhost, tunnels…) are left alone.
    For it to be reached, the www address needs a DNS record and must be in ALLOWED_HOSTS.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        host = urlsplit(settings.SITE_URL).netloc.lower() if settings.SITE_URL else ""
        self.www_host = f"www.{host}" if host and not host.startswith("www.") else ""

    def __call__(self, request):
        if self.www_host and request.get_host().lower() == self.www_host:
            return HttpResponsePermanentRedirect(settings.SITE_URL + request.get_full_path())
        return self.get_response(request)
