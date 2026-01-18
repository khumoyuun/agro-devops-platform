from django.contrib import admin
from .models import Product
from .models import Product, Order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "quantity", "unit", "price", "updated_at")
    search_fields = ("name",)
    list_filter = ("updated_at",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "customer_name", "customer_email", "quantity", "created_at")
    search_fields = ("customer_name", "customer_email")
