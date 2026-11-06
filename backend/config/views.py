import re
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse, StreamingHttpResponse
from django.utils._os import safe_join
from django.views.decorators.cache import never_cache
from django.views.static import serve


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


_RANGE = re.compile(r"^bytes=(\d*)-(\d*)$")
_CHUNK = 64 * 1024


def serve_media(request, path, document_root):
    """Uploaded files, with support for byte ranges ("Range: bytes=0-1").

    Django's own serve() always sends the whole file. Safari and iPhones ask for videos in
    pieces and won't play them without a "206 Partial Content" answer.
    """
    response = serve(request, path, document_root=document_root)
    response["Accept-Ranges"] = "bytes"
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
    return partial
