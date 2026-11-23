"""Puts a page's head tags and text into the built React index.html."""

import json
import re

from django.conf import settings
from django.http import Http404, HttpResponse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from .pages import Page, build_page

_cache = {"mtime": None, "html": ""}

HTML_LANG = re.compile(r'<html lang="[^"]*"')
TITLE = re.compile(r"\s*<title>.*?</title>", re.DOTALL)
DESCRIPTION = re.compile(r'\s*<meta name="description"[^>]*>')
ROOT = '<div id="root"></div>'


def index_html() -> str:
    """The built index.html, read again only when the file changes (a new build)."""
    path = settings.FRONTEND_DIST / "index.html"
    if not path.is_file():
        raise Http404("The frontend hasn't been built yet (run `npm run build` in frontend/).")
    mtime = path.stat().st_mtime
    if _cache["mtime"] != mtime:
        _cache.update(mtime=mtime, html=path.read_text(encoding="utf-8"))
    return _cache["html"]


def json_ld(page: Page) -> str:
    if not page.json_ld:
        return ""
    data = {"@context": "https://schema.org", "@graph": page.json_ld}
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # Nothing inside may close the <script> tag early.
    text = text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return mark_safe(text)  # noqa: S308 - escaped above


def render_html(page: Page, template: str) -> str:
    head = render_to_string("seo/head.html", {"page": page, "json_ld": json_ld(page)})
    body = render_to_string("seo/page.html", {"page": page}).strip()

    html = HTML_LANG.sub(f'<html lang="{page.html_lang}"', template, count=1)
    html = TITLE.sub("", html, count=1)
    html = DESCRIPTION.sub("", html, count=1)
    html = html.replace("</head>", head.rstrip() + "\n  </head>", 1)
    return html.replace(ROOT, f'<div id="root">{body}</div>', 1)


def render_page(request) -> HttpResponse:
    template = index_html()
    page = build_page(request, request.path)
    response = HttpResponse(
        render_html(page, template), content_type="text/html; charset=utf-8", status=page.status
    )
    response["Content-Language"] = page.lang
    return response
