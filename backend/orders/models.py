from decimal import Decimal

from django.db import models, transaction
from django.db.models import F

from languages.conf import CODES, NAMES

LANGUAGE_CHOICES = [(code, NAMES[code]) for code in CODES]


class Order(models.Model):
    """An order placed on the site. No online payment: the shop contacts the customer."""

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONFIRMED = "confirmed", "Confirmed"
        SHIPPED = "shipped", "Out for delivery"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NEW, db_index=True,
        help_text="Cancelling an order puts its items back in stock.",
    )
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=40)
    email = models.EmailField(blank=True)
    city = models.CharField(max_length=80)
    address = models.CharField(max_length=255)
    notes = models.TextField("customer's note", blank=True)
    language = models.CharField(
        max_length=5, choices=LANGUAGE_CHOICES, default="hy",
        help_text="The site language the customer ordered in.",
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    admin_notes = models.TextField(blank=True, help_text="Private notes for the shop; customers never see them.")
    stock_returned = models.BooleanField(default=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.number}"

    @property
    def number(self):
        return f"CC-{self.pk:05d}" if self.pk else "—"

    @transaction.atomic
    def cancel(self):
        """Mark as cancelled and put the items back in stock (once)."""
        if not self.stock_returned:
            for item in self.items.select_related("candle", "collection"):
                product = item.product
                if product is not None:
                    type(product).objects.filter(pk=product.pk).update(stock=F("stock") + item.quantity)
            self.stock_returned = True
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status", "stock_returned", "updated_at"])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    candle = models.ForeignKey(
        "shop.Candle", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    collection = models.ForeignKey(
        "shop.Collection", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    # Copied when ordering, so the order stays readable if the product changes later.
    title = models.CharField(max_length=200)
    scent = models.CharField(max_length=60, blank=True)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.quantity} × {self.title}"

    @property
    def product(self):
        return self.candle or self.collection

    @property
    def line_total(self):
        return self.unit_price * self.quantity
