import json
import logging

from django.contrib import admin
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

from .conf import NAMES, TARGETS, provider_name
from .providers import TranslationError, translate
from .report import collect_missing, totals

logger = logging.getLogger(__name__)

MAX_TEXTS = 200
MAX_CHARACTERS = 60_000


@require_POST
def translate_view(request):
    """Admin only: {"texts": [...english], "targets": ["hy", "ru"]} -> {"hy": [...], "ru": [...]}."""
    try:
        payload = json.loads(request.body)
        texts = [str(t) for t in payload["texts"]]
        targets = [t for t in payload.get("targets", TARGETS) if t in TARGETS]
    except (ValueError, KeyError, TypeError):
        return JsonResponse({"error": "Bad request."}, status=400)
    if not texts or not targets:
        return JsonResponse({"error": "Nothing to translate."}, status=400)
    if len(texts) > MAX_TEXTS or sum(map(len, texts)) > MAX_CHARACTERS:
        return JsonResponse(
            {"error": "Too much text at once. Translate a few fields at a time."}, status=400
        )

    result = {}
    try:
        for target in targets:
            result[target] = translate(texts, target)
    except TranslationError as exc:
        return JsonResponse({"error": str(exc)}, status=502)
    except Exception:
        logger.exception("Automatic translation failed")
        return JsonResponse({"error": "Automatic translation failed. Try again."}, status=502)
    return JsonResponse(result)


def missing_view(request):
    """Admin only: every text that still needs an Armenian or Russian version."""
    items = collect_missing()
    counts = totals(items)
    context = {
        **admin.site.each_context(request),
        "title": "Missing translations",
        "items": items,
        "summary": [(NAMES[lang], counts[lang]) for lang in TARGETS],
        "provider": provider_name(),
    }
    return TemplateResponse(request, "admin/languages/missing.html", context)
