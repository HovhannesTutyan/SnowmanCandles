from rest_framework import serializers

from .models import CONTENT_IMAGE_FIELDS, HeroSlide, HomePageContent


def absolute_url(serializer, image):
    if not image:
        return None
    request = serializer.context.get("request")
    return request.build_absolute_uri(image.url) if request else image.url


class HeroSlideSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()

    class Meta:
        model = HeroSlide
        fields = ["id", "title", "subtitle", "image", "button_text", "link"]

    def get_image(self, obj):
        return absolute_url(self, obj.display_image)

    def get_link(self, obj):
        if obj.candle:
            item, link_type, label = obj.candle, "candle", obj.candle.get_product_type_display()
        elif obj.collection:
            item, link_type, label = obj.collection, "collection", "Collection"
        else:
            return None
        return {
            "type": link_type,
            "slug": item.slug,
            "price": f"{item.price:.2f}",
            "product_type_label": label,
        }


class HomePageContentSerializer(serializers.ModelSerializer):
    ticker_messages = serializers.ListField(source="ticker_list", read_only=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = HomePageContent
        # Images are returned together under "images".
        exclude = ["id", "updated_at", *CONTENT_IMAGE_FIELDS]

    def get_images(self, obj):
        """Absolute URLs, or null where the frontend should use the design's image."""
        return {
            "made_before": absolute_url(self, obj.made_before_image),
            "made_after": absolute_url(self, obj.made_after_image),
            "video": absolute_url(self, obj.video_image),
            "single_tile": absolute_url(self, obj.single_tile_image),
            "sets_tile": absolute_url(self, obj.sets_tile_image),
            "custom_1": absolute_url(self, obj.custom_image_1),
            "custom_2": absolute_url(self, obj.custom_image_2),
        }
