from rest_framework import serializers

from languages.conf import localized_field_names

from shop.serializers import CandleSerializer

from .models import FAQ, CarePage, CareRitual, CareTip, FragranceTip


class CareTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareTip
        fields = ["title", "text"]


class CareRitualSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareRitual
        fields = ["title", "text"]


class FragranceTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = FragranceTip
        fields = ["lead", "text"]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ["question", "answer"]


class CarePageSerializer(serializers.ModelSerializer):
    """Images are absolute URLs, or null where the frontend shows the design's scene."""

    tips = CareTipSerializer(many=True, read_only=True)
    rituals = CareRitualSerializer(many=True, read_only=True)
    fragrance_tips = FragranceTipSerializer(many=True, read_only=True)
    faqs = FAQSerializer(many=True, read_only=True)
    fragrance_product = CandleSerializer(read_only=True)

    class Meta:
        model = CarePage
        # Translated fields once, in the requested language.
        exclude = ["id", "updated_at", *localized_field_names(CarePage)]
