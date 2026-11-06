"""Machine translation for the admin's "Translate" button.

Off unless TRANSLATION_PROVIDER and TRANSLATION_API_KEY are set in .env. Two services:

* claude: the Anthropic API (needs `pip install anthropic`). It is told about the shop,
  so it keeps the tone and the "candle" wording.
* google: Google Cloud Translation (v2, API key).

The result is always a draft: the admin puts it in the form, and the editor reviews it
before saving.
"""

import json
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

from .conf import NAMES, SOURCE, provider_name

DEFAULT_CLAUDE_MODEL = "claude-opus-5-5"
TIMEOUT_SECONDS = 120

CLAUDE_INSTRUCTIONS = """\
You translate website texts for Celeb Candles, a small studio that makes hand-cast, \
hand-painted plaster pieces filled with soy wax candles: single candles and candle sets.

Translate each English text into {language}. Write natural, warm shop copy that a native \
speaker would write, not a word-for-word translation. Keep the meaning, the tone and \
roughly the length.

Rules:
- Every product is a candle. Never call a product a jar, keepsake, figurine or ornament.
- Keep line breaks, blank lines and **double-asterisk** bold markers exactly where they are.
- Keep numbers, sizes, prices, emails and links as they are; translate unit words such as \
"hours" or "cm".
- Do not translate the brand name "Celeb Candles".
- Return one translation per input text, in the same order."""


class TranslationError(Exception):
    """A problem worth showing to the editor in the admin."""


def translate(texts: list[str], target: str) -> list[str]:
    """English texts -> the same texts in `target` ("hy" or "ru")."""
    if not texts:
        return []
    name = provider_name()
    if name == "claude":
        result = _translate_with_claude(texts, target)
    elif name == "google":
        result = _translate_with_google(texts, target)
    else:
        raise TranslationError(
            "Automatic translation is off. Set TRANSLATION_PROVIDER and TRANSLATION_API_KEY "
            "in backend/.env and restart the server."
        )
    if len(result) != len(texts):
        raise TranslationError("The translation service returned an incomplete answer. Try again.")
    return result


def _translate_with_claude(texts: list[str], target: str) -> list[str]:
    try:
        import anthropic
    except ImportError as exc:
        raise TranslationError(
            "The Claude translator needs the anthropic package: run "
            "`pip install anthropic` in backend/ and restart the server."
        ) from exc

    client = anthropic.Anthropic(api_key=settings.TRANSLATION_API_KEY, timeout=TIMEOUT_SECONDS)
    schema = {
        "type": "object",
        "properties": {"translations": {"type": "array", "items": {"type": "string"}}},
        "required": ["translations"],
        "additionalProperties": False,
    }
    try:
        response = client.beta.messages.create(
            model=settings.TRANSLATION_MODEL or DEFAULT_CLAUDE_MODEL,
            max_tokens=16000,
            system=CLAUDE_INSTRUCTIONS.format(language=NAMES[target]),
            messages=[
                {"role": "user", "content": json.dumps({"texts": texts}, ensure_ascii=False)}
            ],
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": schema}},
            # If a request is declined, the API retries it on a suitable fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.AuthenticationError as exc:
        raise TranslationError("The Anthropic API key in .env was rejected.") from exc
    except anthropic.RateLimitError as exc:
        raise TranslationError("Too many translation requests. Wait a minute and try again.") from exc
    except anthropic.APIStatusError as exc:
        raise TranslationError(f"The translation service failed ({exc.status_code}).") from exc
    except anthropic.APIConnectionError as exc:
        raise TranslationError("Could not reach the translation service.") from exc

    if response.stop_reason == "refusal":
        raise TranslationError("The translation service declined these texts.")
    if response.stop_reason == "max_tokens":
        raise TranslationError("Too much text at once. Translate fewer fields at a time.")
    text = next((block.text for block in response.content if block.type == "text"), "")
    try:
        return [str(t) for t in json.loads(text)["translations"]]
    except (ValueError, KeyError, TypeError) as exc:
        raise TranslationError("The translation service returned an unreadable answer.") from exc


def _translate_with_google(texts: list[str], target: str) -> list[str]:
    url = "https://translation.googleapis.com/language/translate/v2?" + urllib.parse.urlencode(
        {"key": settings.TRANSLATION_API_KEY}
    )
    body = json.dumps({"q": texts, "source": SOURCE, "target": target, "format": "text"}).encode()
    request = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            data = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code in (400, 401, 403):
            raise TranslationError("The Google API key in .env was rejected.") from exc
        raise TranslationError(f"The translation service failed ({exc.code}).") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise TranslationError("Could not reach the translation service.") from exc
    try:
        return [item["translatedText"] for item in data["data"]["translations"]]
    except (KeyError, TypeError) as exc:
        raise TranslationError("The translation service returned an unreadable answer.") from exc
