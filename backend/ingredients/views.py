from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Chapter, IngredientsPage
from .serializers import ChapterSerializer, IngredientsPageSerializer


class IngredientsPageView(APIView):
    """Everything on the "What's inside our candles" page, in one request."""

    def get(self, request):
        context = {"request": request}
        chapters = Chapter.objects.filter(is_published=True).prefetch_related(
            "points", "questions", "cards", "swatches"
        )
        data = IngredientsPageSerializer(IngredientsPage.load(), context=context).data
        data["chapters"] = ChapterSerializer(chapters, many=True, context=context).data
        return Response(data)
