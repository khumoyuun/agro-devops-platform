from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST, require_http_methods
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from django.http import HttpResponse
from .models import Product, Order, OrderItem
from .cart import cart_add, cart_remove


# =========================
# PRODUCTS
# =========================
@cache_page(60)
def product_list(request):
    qs = Product.objects.filter(is_active=True).order_by("-id")

    paginator = Paginator(qs, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "board/product_list.html", {"page_obj": page_obj})


@cache_page(60)
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return render(request, "board/product_detail.html", {"product": product})


# =========================
# CART
# =========================
@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    qty = request.POST.get("qty", "1")

    try:
        qty_int = int(qty)
    except ValueError:
        qty_int = 1

    if qty_int < 1:
        qty_int = 1

    cart_add(request.session, product.id, qty_int)
    request.session.modified = True
    return redirect("cart")


@require_POST
def remove_from_cart(request, pk):
    cart_remove(request.session, pk)
    request.session.modified = True
    return redirect("cart")


@require_http_methods(["GET", "POST"])
def cart_view(request):
    cart = request.session.get("cart", {})

    # POST: update/remove
    if request.method == "POST":
        action = request.POST.get("action")
        pid = request.POST.get("product_id")

        if pid:
            pid_str = str(pid)

            if action == "remove":
                cart.pop(pid_str, None)

            elif action == "update":
                qty_raw = request.POST.get("qty", "1")
                try:
                    qty_int = int(qty_raw)
                except ValueError:
                    qty_int = 1

                if qty_int <= 0:
                    cart.pop(pid_str, None)
                else:
                    cart[pid_str] = qty_int

        request.session["cart"] = cart
        request.session.modified = True
        return redirect("cart")

    # GET: productlarni 1 query bilan olish
    product_ids = []
    for k in cart.keys():
        try:
            product_ids.append(int(k))
        except ValueError:
            pass

    products = Product.objects.filter(id__in=product_ids, is_active=True)
    product_map = {p.id: p for p in products}

    cart_items = []
    total = Decimal("0.00")

    for pid_str, qty in cart.items():
        try:
            pid = int(pid_str)
            qty_int = int(qty)
        except ValueError:
            continue

        if qty_int <= 0:
            continue

        product = product_map.get(pid)
        if not product:
            continue

        price = Decimal(str(product.price))
        subtotal = price * qty_int
        total += subtotal

        cart_items.append(
            {"product": product, "qty": qty_int, "subtotal": subtotal}
        )

    context = {
        "cart_items": cart_items,
        "total": total,
        "cart_count": sum(item["qty"] for item in cart_items),
    }
    return render(request, "board/cart.html", context)


# =========================
# CHECKOUT + ORDER
# =========================
@require_http_methods(["GET", "POST"])
def checkout(request):
    cart = request.session.get("cart", {})

    if not cart:
        return redirect("cart")

    # productlarni 1 query bilan olish
    product_ids = []
    for k in cart.keys():
        try:
            product_ids.append(int(k))
        except ValueError:
            pass

    products = Product.objects.filter(id__in=product_ids, is_active=True)
    product_map = {p.id: p for p in products}

    total = Decimal("0.00")
    items = []

    for pid_str, qty in cart.items():
        try:
            pid = int(pid_str)
            qty_int = int(qty)
        except ValueError:
            continue

        if qty_int <= 0:
            continue

        p = product_map.get(pid)
        if not p:
            continue

        price = Decimal(str(p.price))
        subtotal = price * qty_int
        total += subtotal
        items.append((p, qty_int, price, subtotal))

    if not items:
        return redirect("cart")

    if request.method == "POST":
        full_name = (request.POST.get("full_name") or "").strip()
        phone = (request.POST.get("phone") or "").strip()
        address = (request.POST.get("address") or "").strip()

        errors = {}
        if not full_name:
            errors["full_name"] = "Required"
        if not phone:
            errors["phone"] = "Required"
        if not address:
            errors["address"] = "Required"

        if errors:
            return render(request, "board/checkout.html", {
                "items": items,
                "total": total,
                "errors": errors,
                "full_name": full_name,
                "phone": phone,
                "address": address,
            })

        with transaction.atomic():
            order = Order.objects.create(
                full_name=full_name,
                phone=phone,
                address=address,
                total_price=total,
            )

            bulk_items = []
            for p, qty_int, price, subtotal in items:
                oi = OrderItem(order=order, product=p)

    # qty field nomi har xil bo'lishi mumkin
                if hasattr(oi, "quantity"):
                    oi.quantity = qty_int
                elif hasattr(oi, "qty"):
                    oi.qty = qty_int
                elif hasattr(oi, "count"):
                    oi.count = qty_int
                elif hasattr(oi, "amount"):
                    oi.amount = qty_int

    # ✅ unit_price majburiy bo‘lsa shuni to‘ldiramiz
                if hasattr(oi, "unit_price"):
                    oi.unit_price = price

    # boshqa nomlar bo‘lsa ham to‘ldirib ketamiz
                if hasattr(oi, "price"):
                    oi.price = price
                if hasattr(oi, "subtotal"):
                    oi.subtotal = subtotal
                if hasattr(oi, "total_price"):
                    oi.total_price = subtotal
                if hasattr(oi, "total"):
                    oi.total = subtotal

                bulk_items.append(oi)

            OrderItem.objects.bulk_create(bulk_items)

        request.session["cart"] = {}
        request.session.modified = True

        return redirect("order_success", pk=order.id)

    return render(request, "board/checkout.html", {"items": items, "total": total})


# =========================
# ORDER SUCCESS + HEALTH
# =========================
def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = OrderItem.objects.filter(order=order).select_related("product")
    return render(request, "board/order_success.html", {"order": order, "items": items})

def health(request):
    return JsonResponse({"status": "ok"})


def metrics(request):
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)