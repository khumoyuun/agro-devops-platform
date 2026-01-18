from django.shortcuts import render
from .models import Product
from django.http import JsonResponse


def product_list(request):
    products = Product.objects.order_by("-updated_at")
    return render(request, "board/product_list.html", {"products": products})


def health(request):
    return JsonResponse({"status": "ok"})
