from rest_framework import serializers

from .models import Candle, Collection

BASE_ITEM_FIELDS = [
    "id",
    "title",
    "slug",
    "description",
    "image",
    "price",
    "stock",
    "tint",
    "is_available",
    "is_featured",
    "created_at",
    "updated_at",
]


# Extra fields on the detail endpoints, used by the product page.
PRODUCT_PAGE_FIELDS = [
    "scents",
    "burn_time",
    "size",
    "details",
    "story_title",
    "story_text",
    "flame",
    "gallery",
    "showcase_views",
]


class GalleryImageSerializer(serializers.Serializer):
    image = serializers.ImageField(read_only=True)
    label = serializers.CharField(read_only=True)


class ShowcaseViewSerializer(serializers.Serializer):
    """One view of the animated product showcase."""

    image = serializers.ImageField(read_only=True)
    label = serializers.CharField(read_only=True)
    short_label = serializers.SerializerMethodField()
    caption = serializers.CharField(read_only=True)
    color = serializers.CharField(read_only=True)
    tint = serializers.CharField(read_only=True)
    group = serializers.CharField(read_only=True)

    def get_short_label(self, view):
        return view.short_label or view.label


class ProductPageFieldsMixin(serializers.Serializer):
    scents = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    # {"x": %, "y": %} of the wick on the main image, or null when there's no lit view.
    flame = serializers.ReadOnlyField()
    gallery = GalleryImageSerializer(many=True, read_only=True)
    # Empty: the product page shows the regular gallery only.
    showcase_views = ShowcaseViewSerializer(many=True, read_only=True)


class CandleSerializer(serializers.ModelSerializer):
    """Image is returned as an absolute URL (request is in the serializer context);
    price is returned as a 2-decimal string (DRF's DecimalField default)."""

    is_available = serializers.BooleanField(read_only=True)
    product_type_label = serializers.CharField(
        source="get_product_type_display", read_only=True
    )

    class Meta:
        model = Candle
        fields = BASE_ITEM_FIELDS + ["product_type", "product_type_label"]


class CandleDetailSerializer(ProductPageFieldsMixin, CandleSerializer):
    class Meta(CandleSerializer.Meta):
        fields = CandleSerializer.Meta.fields + PRODUCT_PAGE_FIELDS


class CandleSummarySerializer(serializers.ModelSerializer):
    """Compact candle representation nested inside a collection."""

    product_type_label = serializers.CharField(
        source="get_product_type_display", read_only=True
    )
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Candle
        fields = ["title", "slug", "image", "price", "tint", "product_type_label", "is_available"]


class CollectionListSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)
    candle_count = serializers.IntegerField(read_only=True)
    # Same keys as candles so the frontend can render both with one card.
    product_type = serializers.SerializerMethodField()
    product_type_label = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = BASE_ITEM_FIELDS + ["product_type", "product_type_label", "candle_count"]

    def get_product_type(self, obj):
        return "collection"

    def get_product_type_label(self, obj):
        return "Collection"


class CollectionDetailSerializer(ProductPageFieldsMixin, CollectionListSerializer):
    candles = CandleSummarySerializer(many=True, read_only=True)

    class Meta(CollectionListSerializer.Meta):
        fields = CollectionListSerializer.Meta.fields + ["candles", *PRODUCT_PAGE_FIELDS]
