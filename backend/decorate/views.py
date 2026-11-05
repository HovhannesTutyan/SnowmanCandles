from django.db.models import Prefetch
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Candle

from .models import DecoratePage, GalleryImage, Room
from .serializers import DecoratePageSerializer, GalleryImageSerializer


class DecoratePageView(APIView):
    """Everything on the "Decorate with candles" page, in one request.

    Each room points at its picture by position in `gallery` (`gallery_index`), so the
    frontend can open that picture in the full-screen viewer. Rooms whose picture is
    missing or hidden get `null`.
    """

    def get(self, request):
        context = {"request": request}
        page = DecoratePage.load()
        gallery = list(
            GalleryImage.objects.filter(is_published=True).prefetch_related(
                Prefetch("products", queryset=Candle.objects.order_by("title"))
            )
        )
        positions = {picture.pk: index for index, picture in enumerate(gallery)}
        rooms = Room.objects.filter(page=page)

        data = DecoratePageSerializer(page, context=context).data
        data["rooms"] = [
            {
                "title": room.title,
                "text": room.text,
                "gallery_index": positions.get(room.picture_id),
            }
            for room in rooms
        ]
        data["gallery"] = GalleryImageSerializer(gallery, many=True, context=context).data
        return Response(data)
