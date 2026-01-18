from django.shortcuts import render
from .models import Product, Order
from django.http import JsonResponse
from django.utils.timezone import now

def product_list(request):
    products = Product.objects.order_by("-updated_at")
    return render(request, "board/product_list.html", {"products": products})


def health(request):
    return JsonResponse({"status": "ok"})

def dashboard(request):
    data = {
        "products_count": Product.objects.count(),
        "orders_count": Order.objects.count(),
        "last_product_update": Product.objects.order_by("-updated_at").values_list("updated_at", flat=True).first(),
        "server_time": now(),
    }
    return render(request, "board/dashboard.html", data)