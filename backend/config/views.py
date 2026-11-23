import re
from pathlib import Path

from django.http import HttpResponse, StreamingHttpResponse
from django.utils._os import safe_join
from django.views.decorators.cache import never_cache
from django.views.static import serve

from seo.render import render_page


@never_cache
def spa_index(request, path=""):
    """The built React app's index.html, for every page URL (/candles/…, /decorate, …).

    Each page gets its own title, description, language links, link-preview tags,
    structured data and text (see seo/), so search engines and link previews see the real
    page. React Router then takes over in the browser. Files under /assets/ are served by
    WhiteNoise before this view is reached.
    """
    return render_page(request)


_RANGE = re.compile(r"^bytes=(\d*)-(\d*)$")
_CHUNK = 64 * 1024
# Browsers keep uploaded photos and videos for 30 days. A new upload always gets a new file
# name (Django adds a suffix when the name is taken), so changes still show straight away.
MEDIA_CACHE_CONTROL = "public, max-age=2592000"


def serve_media(request, path, document_root):
    """Uploaded files, with support for byte ranges ("Range: bytes=0-1").

    Django's own serve() always sends the whole file. Safari and iPhones ask for videos in
    pieces and won't play them without a "206 Partial Content" answer.
    """
    response = serve(request, path, document_root=document_root)
    response["Accept-Ranges"] = "bytes"
    if response.status_code in (200, 304):
        response["Cache-Control"] = MEDIA_CACHE_CONTROL
    match = _RANGE.match(request.headers.get("Range", "").strip())
    if response.status_code != 200 or not match:
        return response

    response.close()  # we answer with part of the file instead
    file_path = Path(safe_join(document_root, path))
    size = file_path.stat().st_size
    first, last = match.groups()
    if first == "":  # "bytes=-500": the last 500 bytes
        if not last:
            return response
        start, end = max(0, size - int(last)), size - 1
    else:
        start, end = int(first), min(int(last) if last else size - 1, size - 1)
    if start > end or start >= size:
        return HttpResponse(status=416, headers={"Content-Range": f"bytes */{size}"})

    def chunks():
        with file_path.open("rb") as f:
            f.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                data = f.read(min(_CHUNK, remaining))
                if not data:
                    break
                remaining -= len(data)
                yield data

    partial = StreamingHttpResponse(chunks(), status=206, content_type=response["Content-Type"])
    partial["Content-Length"] = str(end - start + 1)
    partial["Content-Range"] = f"bytes {start}-{end}/{size}"
    partial["Accept-Ranges"] = "bytes"
    partial["Cache-Control"] = MEDIA_CACHE_CONTROL
    return partial
