"""Basket prices and placing orders. Prices and stock always come from the database,
never from the browser."""

from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction
from django.db.models import F, Q
from django.utils import translation

from languages.conf import CODES, SOURCE, localized
from shop.models import Candle, Collection

from .models import Order, OrderItem

MAX_PER_LINE = 20
KINDS = {"candle": Candle, "collection": Collection}


@dataclass(frozen=True)
class Line:
    kind: str  # "candle" | "collection"
    slug: str
    scent: str  # as shown to the visitor (any language), or ""
    quantity: int


class StockError(Exception):
    """Some lines can't be ordered (sold out, too few left, or no longer sold)."""

    def __init__(self, problems):
        super().__init__("Some items are no longer available in that quantity.")
        self.problems = problems  # [{"index": i, "available": n}]


def _products(lines):
    """{(kind, slug): product} for the lines' products."""
    found = {}
    for kind, model in KINDS.items():
        slugs = {line.slug for line in lines if line.kind == kind}
        if slugs:
            for product in model.objects.filter(slug__in=slugs).prefetch_related("scents"):
                found[(kind, product.slug)] = product
    return found


def _scent(product, name):
    """The product's scent matching `name` in any language, or None."""
    if not name:
        return None
    query = Q()
    for lang in CODES:
        query |= Q(**{localized("name", lang): name})
    return product.scents.filter(query).first()


def quote(lines, request=None):
    """Current details of each basket line, in the active language. Lines whose product is
    gone come back as None, in the same positions as `lines`."""
    products = _products(lines)
    results = []
    subtotal = Decimal("0")
    for line in lines:
        product = products.get((line.kind, line.slug))
        if product is None:
            results.append(None)
            continue
        scent = _scent(product, line.scent)
        image = product.image.url if product.image else None
        if image and request is not None:
            image = request.build_absolute_uri(image)
        quantity = min(line.quantity, MAX_PER_LINE)
        line_total = product.price * quantity
        if product.stock > 0:
            subtotal += product.price * min(quantity, product.stock)
        results.append({
            "kind": line.kind,
            "slug": product.slug,
            "title": product.title,
            "image": image,
            "tint": product.tint,
            "product_type": product.product_type if line.kind == "candle" else "collection",
            "price": f"{product.price:.2f}",
            "scent": scent.name if scent else "",
            "quantity": quantity,
            "stock": product.stock,
            "line_total": f"{line_total:.2f}",
        })
    return {"lines": results, "subtotal": f"{subtotal:.2f}", "total": f"{subtotal:.2f}"}


@transaction.atomic
def place_order(customer, lines, language):
    """Create the order and take its items out of stock, all or nothing."""
    locked = {}
    for kind, model in KINDS.items():
        slugs = {line.slug for line in lines if line.kind == kind}
        if slugs:
            for product in model.objects.select_for_update().filter(slug__in=slugs):
                locked[(kind, product.slug)] = product

    # Several lines can be the same product in different scents.
    wanted = {}
    for line in lines:
        wanted[(line.kind, line.slug)] = wanted.get((line.kind, line.slug), 0) + line.quantity

    problems = []
    for index, line in enumerate(lines):
        product = locked.get((line.kind, line.slug))
        if product is None:
            problems.append({"index": index, "available": 0})
        elif wanted[(line.kind, line.slug)] > product.stock:
            problems.append({"index": index, "available": product.stock})
    if problems:
        raise StockError(problems)

    order = Order.objects.create(language=language, **customer)
    total = Decimal("0")
    with translation.override(SOURCE):  # the admin reads titles and scents in English
        for line in lines:
            product = locked[(line.kind, line.slug)]
            scent = _scent(product, line.scent)
            OrderItem.objects.create(
                order=order,
                candle=product if line.kind == "candle" else None,
                collection=product if line.kind == "collection" else None,
                title=product.title,
                scent=scent.name if scent else line.scent[:60],
                unit_price=product.price,
                quantity=line.quantity,
            )
            total += product.price * line.quantity
    for (kind, slug), quantity in wanted.items():
        KINDS[kind].objects.filter(pk=locked[(kind, slug)].pk).update(stock=F("stock") - quantity)
    order.total = total
    order.save(update_fields=["total"])
    return order
