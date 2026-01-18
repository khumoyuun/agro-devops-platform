from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "quantity", "unit", "price", "updated_at")
    search_fields = ("name",)
    list_filter = ("updated_at",)
