from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .serializers import OrderSerializer, QuoteSerializer
from .services import StockError, place_order, quote

CUSTOMER_FIELDS = ["full_name", "phone", "email", "city", "address", "notes"]


class CartQuoteView(APIView):
    """POST the basket lines; get back current titles, images, prices and stock.

    A POST so a long basket fits, but it changes nothing. No session auth, so it works
    the same for signed-in admins (no CSRF token needed).
    """

    authentication_classes = []

    def post(self, request):
        serializer = QuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(quote(serializer.validated_data["items"], request))


class OrderCreateView(APIView):
    """Place an order (no payment). Prices and stock are checked here, not in the browser."""

    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "orders"

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            order = place_order(
                {field: data[field] for field in CUSTOMER_FIELDS}, data["items"], data["language"]
            )
        except StockError as exc:
            return Response(
                {"error": "out_of_stock", "problems": exc.problems}, status=status.HTTP_409_CONFLICT
            )
        return Response(
            {"number": order.number, "total": f"{order.total:.2f}"}, status=status.HTTP_201_CREATED
        )
