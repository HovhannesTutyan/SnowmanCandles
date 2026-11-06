import re

from rest_framework import serializers

from languages.conf import CODES

from .services import KINDS, MAX_PER_LINE, Line

MAX_LINES = 50
PHONE = re.compile(r"^\+?[\d\s()\-]{7,20}$")


class LineSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=list(KINDS))
    slug = serializers.SlugField(max_length=220)
    scent = serializers.CharField(max_length=60, required=False, allow_blank=True, default="")
    quantity = serializers.IntegerField(min_value=1, max_value=MAX_PER_LINE)


class LinesField(serializers.ListField):
    child = LineSerializer()

    def to_internal_value(self, data):
        return [Line(**item) for item in super().to_internal_value(data)]


class QuoteSerializer(serializers.Serializer):
    items = LinesField(max_length=MAX_LINES)


class OrderSerializer(serializers.Serializer):
    items = LinesField(min_length=1, max_length=MAX_LINES)
    full_name = serializers.CharField(max_length=120, trim_whitespace=True)
    phone = serializers.CharField(max_length=40, trim_whitespace=True)
    email = serializers.EmailField(required=False, allow_blank=True, default="")
    city = serializers.CharField(max_length=80, trim_whitespace=True)
    address = serializers.CharField(max_length=255, trim_whitespace=True)
    notes = serializers.CharField(max_length=1000, required=False, allow_blank=True, default="")
    language = serializers.ChoiceField(choices=list(CODES), required=False, default="hy")
    # Hidden field that people never fill in; bots often do.
    website = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_phone(self, value):
        if not PHONE.match(value):
            raise serializers.ValidationError("invalid_phone")
        return value

    def validate_website(self, value):
        if value:
            raise serializers.ValidationError("spam")
        return value
