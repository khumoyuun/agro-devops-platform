from django.contrib import admin
from .models import Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "stock", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


def _qty(obj):
    for f in ("quantity", "qty", "count", "amount"):
        if hasattr(obj, f):
            v = getattr(obj, f)
            if v is not None:
                return v
    return "-"


def _unit_price(obj):
    for f in ("unit_price", "price"):
        if hasattr(obj, f):
            v = getattr(obj, f)
            if v is not None:
                return v
    return "-"


def _subtotal(obj):
    for f in ("subtotal", "total", "total_price", "line_total"):
        if hasattr(obj, f):
            v = getattr(obj, f)
            if v is not None:
                return v
    # agar modelda subtotal bo‘lmasa hisoblab beramiz
    try:
        q = _qty(obj)
        p = _unit_price(obj)
        if q != "-" and p != "-":
            return q * p
    except Exception:
        pass
    return "-"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "show_qty", "show_unit_price", "show_subtotal")
    readonly_fields = ("show_qty", "show_unit_price", "show_subtotal")

    def show_qty(self, obj):
        return _qty(obj)
    show_qty.short_description = "Qty"

    def show_unit_price(self, obj):
        return _unit_price(obj)
    show_unit_price.short_description = "Unit price"

    def show_subtotal(self, obj):
        return _subtotal(obj)
    show_subtotal.short_description = "Subtotal"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "created_at")
    readonly_fields = ("full_name", "phone", "address", "created_at")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "show_qty", "show_unit_price", "show_subtotal")
    readonly_fields = ("show_qty", "show_unit_price", "show_subtotal")

    def show_qty(self, obj):
        return _qty(obj)
    show_qty.short_description = "Qty"

    def show_unit_price(self, obj):
        return _unit_price(obj)
    show_unit_price.short_description = "Unit price"

    def show_subtotal(self, obj):
        return _subtotal(obj)
    show_subtotal.short_description = "Subtotal"
