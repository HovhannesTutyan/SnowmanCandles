from django.db.models import Count
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Candle, Collection
from shop.serializers import CandleSerializer, CollectionListSerializer

from .models import HeroSlide, HomePageContent
from .serializers import HeroSlideSerializer, HomePageContentSerializer

FEATURED_LIMIT = 8


class SiteContentView(APIView):
    """Site-wide texts and images used on every page (header, footer, ticker, ...)."""

    def get(self, request):
        content = HomePageContent.load()
        return Response(HomePageContentSerializer(content, context={"request": request}).data)


class HomeView(APIView):
    """Slides and featured products for the homepage, in one (unpaginated) request.
    Site-wide texts come from SiteContentView."""

    def get(self, request):
        slides = HeroSlide.objects.filter(is_active=True).select_related("candle", "collection")
        featured_order = ["featured_order", "-created_at"]
        candles = Candle.objects.filter(is_featured=True, stock__gt=0).order_by(
            *featured_order
        )[:FEATURED_LIMIT]
        collections = (
            Collection.objects.filter(is_featured=True, stock__gt=0)
            .annotate(candle_count=Count("candles"))
            .order_by(*featured_order)[:FEATURED_LIMIT]
        )

        context = {"request": request}
        return Response(
            {
                "slides": HeroSlideSerializer(slides, many=True, context=context).data,
                "featured_candles": CandleSerializer(candles, many=True, context=context).data,
                "featured_collections": CollectionListSerializer(
                    collections, many=True, context=context
                ).data,
            }
        )
