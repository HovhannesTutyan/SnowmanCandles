"""Shared test helpers (not a test module itself)."""

import io
import shutil
import tempfile
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

from .models import Candle, Collection

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


def make_image(name="test.png"):
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), color="orange").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


def make_candle(title="Vanilla Dream", price="12.50", stock=10, **kwargs):
    return Candle.objects.create(
        title=title,
        description="A lovely candle.",
        image=make_image(),
        price=Decimal(price),
        stock=stock,
        **kwargs,
    )


def make_collection(title="Autumn Set", price="39.99", stock=5, **kwargs):
    return Collection.objects.create(
        title=title,
        description="A lovely collection.",
        image=make_image(),
        price=Decimal(price),
        stock=stock,
        **kwargs,
    )


class MediaTestMixin:
    """Store uploaded test images in a temp dir instead of the real MEDIA_ROOT."""

    @classmethod
    def setUpClass(cls):
        # Enabled before super() so setUpTestData() uploads go to the temp dir too.
        cls._media_override = override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
        cls._media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._media_override.disable()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
