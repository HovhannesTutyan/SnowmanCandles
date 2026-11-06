from django.urls import path

from .views import CartQuoteView, OrderCreateView

urlpatterns = [
    path("cart/", CartQuoteView.as_view(), name="cart-quote"),
    path("orders/", OrderCreateView.as_view(), name="order-create"),
]
