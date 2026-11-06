from django import forms
from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html

from .models import Order, OrderItem

STATUS_COLOURS = {
    Order.Status.NEW: "#b4451a",
    Order.Status.CONFIRMED: "#1f6fb2",
    Order.Status.SHIPPED: "#7a5bb5",
    Order.Status.DELIVERED: "#2e7d32",
    Order.Status.CANCELLED: "#757575",
}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    fields = ["title", "scent", "unit_price", "quantity", "line_total_display"]
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Line total")
    def line_total_display(self, obj):
        return f"{obj.line_total:.2f}"


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"

    def clean_status(self):
        status = self.cleaned_data["status"]
        if self.instance.pk and self.instance.status == Order.Status.CANCELLED and status != Order.Status.CANCELLED:
            raise forms.ValidationError(
                "A cancelled order can't be reopened (its items went back into stock). "
                "Ask the customer to order again."
            )
        return status


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderForm
    list_display = ["number_display", "created_at", "full_name", "phone", "city", "item_count", "total", "status_badge"]
    list_display_links = ["number_display", "full_name"]
    list_filter = ["status", "created_at", "language"]
    search_fields = ["id", "full_name", "phone", "email", "city", "address"]
    date_hierarchy = "created_at"
    readonly_fields = ["number_display", "total", "language", "created_at", "updated_at"]
    fieldsets = [
        (None, {"fields": [("number_display", "created_at"), "status", "admin_notes"]}),
        ("Customer", {"fields": ["full_name", "phone", "email", ("city", "address"), "notes", "language"]}),
        ("Total", {
            "fields": ["total"],
            "description": "Delivery is free. No payment was taken on the site.",
        }),
        ("Info", {"fields": ["updated_at"], "classes": ["collapse"]}),
    ]
    inlines = [OrderItemInline]
    actions = ["mark_confirmed", "mark_shipped", "mark_delivered", "mark_cancelled"]
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_items=Count("items"))

    def has_add_permission(self, request):
        return False  # orders come from the site

    @admin.display(description="Order", ordering="id")
    def number_display(self, obj):
        return obj.number

    @admin.display(description="Items", ordering="_items")
    def item_count(self, obj):
        return obj._items

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        return format_html(
            '<span style="display:inline-block;padding:2px 10px;border-radius:999px;'
            'background:{};color:#fff;font-weight:600;font-size:11px;">{}</span>',
            STATUS_COLOURS.get(obj.status, "#757575"),
            obj.get_status_display(),
        )

    def save_model(self, request, obj, form, change):
        cancelling = change and "status" in form.changed_data and obj.status == Order.Status.CANCELLED
        if cancelling:
            obj.status = form.initial["status"]  # cancel() sets it and restocks
            super().save_model(request, obj, form, change)
            obj.cancel()
            messages.info(request, f"{obj.number} cancelled; its items are back in stock.")
        else:
            super().save_model(request, obj, form, change)

    def _set_status(self, request, queryset, status, label):
        done = skipped = 0
        for order in queryset:
            if order.status == Order.Status.CANCELLED:
                skipped += 1
                continue
            order.status = status
            order.save(update_fields=["status", "updated_at"])
            done += 1
        self.message_user(request, f"{done} order(s) marked as {label}.")
        if skipped:
            self.message_user(request, f"{skipped} cancelled order(s) left unchanged.", messages.WARNING)

    @admin.action(description="Mark as confirmed")
    def mark_confirmed(self, request, queryset):
        self._set_status(request, queryset, Order.Status.CONFIRMED, "confirmed")

    @admin.action(description="Mark as out for delivery")
    def mark_shipped(self, request, queryset):
        self._set_status(request, queryset, Order.Status.SHIPPED, "out for delivery")

    @admin.action(description="Mark as delivered")
    def mark_delivered(self, request, queryset):
        self._set_status(request, queryset, Order.Status.DELIVERED, "delivered")

    @admin.action(description="Cancel (puts items back in stock)")
    def mark_cancelled(self, request, queryset):
        count = 0
        for order in queryset.exclude(status=Order.Status.CANCELLED):
            order.cancel()
            count += 1
        self.message_user(request, f"{count} order(s) cancelled; their items are back in stock.")
