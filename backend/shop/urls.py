from rest_framework.routers import DefaultRouter

from .views import CandleViewSet, CollectionViewSet

router = DefaultRouter()
router.register("candles", CandleViewSet, basename="candle")
router.register("collections", CollectionViewSet, basename="collection")

urlpatterns = router.urls
