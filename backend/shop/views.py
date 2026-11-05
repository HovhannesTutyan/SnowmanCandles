from decimal import Decimal, InvalidOperation

from django.db.models import Case, Count, IntegerField, Value, When
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from .models import Candle, Collection, ProductType
from .serializers import (
    CandleDetailSerializer,
    CandleSerializer,
    CollectionDetailSerializer,
    CollectionListSerializer,
)

RELATED_LIMIT = 4
FEATURED_FIRST = ["-is_featured", "featured_order", "-created_at"]
TRUE_VALUES = {"true", "1", "yes"}


def related_items(item, request):
    """Up to RELATED_LIMIT other in-stock products for "You might also love".

    A candle gets other candles first (same type first); a collection gets other
    collections first. The other kind fills any remaining places.
    """
    candles = Candle.objects.filter(stock__gt=0)
    collections = Collection.objects.filter(stock__gt=0).annotate(candle_count=Count("candles"))

    if isinstance(item, Candle):
        candles = candles.exclude(pk=item.pk).annotate(
            other_type=Case(
                When(product_type=item.product_type, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        groups = [
            (candles.order_by("other_type", *FEATURED_FIRST), CandleSerializer),
            (collections.order_by(*FEATURED_FIRST), CollectionListSerializer),
        ]
    else:
        groups = [
            (collections.exclude(pk=item.pk).order_by(*FEATURED_FIRST), CollectionListSerializer),
            (candles.order_by(*FEATURED_FIRST), CandleSerializer),
        ]

    context = {"request": request}
    results = []
    for queryset, serializer_class in groups:
        remaining = RELATED_LIMIT - len(results)
        if remaining <= 0:
            break
        results += serializer_class(queryset[:remaining], many=True, context=context).data
    return results

FALSE_VALUES = {"false", "0", "no"}


class BaseItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only list/detail endpoints looked up by slug.

    Query params (list):
      ?available=true|false   only items with stock > 0 (or == 0)
      ?featured=true|false    only items (not) marked as homepage featured
      ?min_price= / ?max_price=
      ?ordering=price | -price | created_at | -created_at
    """

    lookup_field = "slug"
    filter_backends = [OrderingFilter]
    ordering_fields = ["price", "created_at"]
    ordering = ["-created_at"]

    def retrieve(self, request, *args, **kwargs):
        """Detail for the product page, with related products included."""
        instance = self.get_object()
        data = self.get_serializer(instance).data
        data["related"] = related_items(instance, request)
        return Response(data)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if self.action != "list":
            return queryset

        params = self.request.query_params

        available = self._parse_bool(params, "available")
        if available is True:
            queryset = queryset.filter(stock__gt=0)
        elif available is False:
            queryset = queryset.filter(stock=0)

        featured = self._parse_bool(params, "featured")
        if featured is not None:
            queryset = queryset.filter(is_featured=featured)

        min_price = self._parse_price(params, "min_price")
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)

        max_price = self._parse_price(params, "max_price")
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)

        return queryset

    @staticmethod
    def _parse_bool(params, name):
        raw = params.get(name)
        if raw is None:
            return None
        value = raw.strip().lower()
        if value in TRUE_VALUES:
            return True
        if value in FALSE_VALUES:
            return False
        raise ValidationError({name: "Use 'true' or 'false'."})

    @staticmethod
    def _parse_price(params, name):
        raw = params.get(name)
        if raw in (None, ""):
            return None
        try:
            value = Decimal(raw)
        except InvalidOperation:
            raise ValidationError({name: "Must be a number."})
        if not value.is_finite() or value < 0:
            raise ValidationError({name: "Must be a non-negative number."})
        return value


class CandleViewSet(BaseItemViewSet):
    """Also supports ?type=candle|set on the list endpoint."""

    def get_queryset(self):
        queryset = Candle.objects.all()
        if self.action == "retrieve":
            queryset = queryset.prefetch_related("scents", "gallery", "showcase_views")
        return queryset

    def get_serializer_class(self):
        return CandleDetailSerializer if self.action == "retrieve" else CandleSerializer

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        product_type = self.request.query_params.get("type")
        if self.action == "list" and product_type:
            if product_type not in ProductType.values:
                raise ValidationError(
                    {"type": f"Use one of: {', '.join(ProductType.values)}."}
                )
            queryset = queryset.filter(product_type=product_type)
        return queryset


class CollectionViewSet(BaseItemViewSet):
    def get_queryset(self):
        queryset = Collection.objects.annotate(candle_count=Count("candles"))
        if self.action == "retrieve":
            queryset = queryset.prefetch_related("candles", "scents", "gallery", "showcase_views")
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CollectionDetailSerializer
        return CollectionListSerializer
