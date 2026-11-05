from rest_framework import serializers

from shop.models import Candle

from .models import DecoratePage, GalleryImage


class PictureProductSerializer(serializers.ModelSerializer):
    """Just enough to link to a candle's product page."""

    class Meta:
        model = Candle
        fields = ["title", "slug", "product_type"]


class GalleryImageSerializer(serializers.ModelSerializer):
    products = PictureProductSerializer(many=True, read_only=True)

    class Meta:
        model = GalleryImage
        fields = ["id", "image", "caption", "alt", "products"]


class DecoratePageSerializer(serializers.ModelSerializer):
    """Page texts; hero/closing pictures are absolute URLs, or null for the design's picture."""

    class Meta:
        model = DecoratePage
        exclude = ["id", "updated_at"]
