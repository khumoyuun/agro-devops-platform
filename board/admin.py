from django.contrib import admin
from .models import Product, Order, PriceHistory

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "quantity", "unit", "price", "updated_at")
    search_fields = ("name",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "customer_name", "customer_email", "quantity", "created_at")
    search_fields = ("customer_name", "customer_email")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # 100% Render logda chiqadi (stdout)
        print(
            f"NEW ORDER: product={obj.product.name} customer={obj.customer_name} "
            f"email={obj.customer_email} qty={obj.quantity}"
        )

@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ("product", "old_price", "new_price", "changed_at")
