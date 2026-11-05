from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CarePage
from .serializers import CarePageSerializer


class CarePageView(APIView):
    """Everything on the "Candle care & tips" page, in one request."""

    def get(self, request):
        CarePage.load()  # make sure the page exists
        page = (
            CarePage.objects.select_related("fragrance_product")
            .prefetch_related("tips", "rituals", "fragrance_tips", "faqs")
            .get(pk=1)
        )
        # The featured candle's label is only shown while it can be bought.
        if page.fragrance_product and not page.fragrance_product.is_available:
            page.fragrance_product = None
        return Response(CarePageSerializer(page, context={"request": request}).data)
