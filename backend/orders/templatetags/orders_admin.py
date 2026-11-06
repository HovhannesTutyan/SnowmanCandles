from django import template
from django.urls import reverse

from ..models import Order

register = template.Library()


@register.inclusion_tag("admin/orders/panel.html")
def orders_panel():
    """The "Orders" box on the admin home page."""
    new = Order.objects.filter(status=Order.Status.NEW).count()
    in_progress = Order.objects.filter(
        status__in=[Order.Status.CONFIRMED, Order.Status.SHIPPED]
    ).count()
    url = reverse("admin:orders_order_changelist")
    return {
        "new": new,
        "in_progress": in_progress,
        "new_url": f"{url}?status__exact={Order.Status.NEW}",
        "all_url": url,
    }
