from rest_framework import serializers

from .models import (
    Chapter,
    ChapterCard,
    ChapterPoint,
    ChapterQuestion,
    ChapterSwatch,
    IngredientsPage,
)


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChapterPoint
        fields = ["lead", "text"]


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChapterQuestion
        fields = ["question", "answer"]


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChapterCard
        fields = ["icon", "title", "text"]


class SwatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChapterSwatch
        fields = ["name", "color", "note"]


class ChapterSerializer(serializers.ModelSerializer):
    paragraphs = serializers.ListField(child=serializers.CharField(), read_only=True)
    points = PointSerializer(many=True, read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    cards = CardSerializer(many=True, read_only=True)
    swatches = SwatchSerializer(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = [
            "anchor", "nav_label", "title", "intro", "paragraphs",
            "illustration", "banner_image", "banner_color", "banner_text",
            "cards_title", "points", "questions", "cards", "swatches",
        ]


class IngredientsPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientsPage
        exclude = ["id", "updated_at"]
