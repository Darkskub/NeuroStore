# store/views.py
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from .models import Product
from .cart import Cart

def product_list(request):
    products = Product.objects.all()
    return render(request, "store/product_list.html", {"products": products})

def cart_detail(request):
    cart = Cart(request)
    return render(request, "store/cart.html", {"cart": cart})

@require_POST
def cart_add(request, product_id: int):
    cart = Cart(request)
    qty = request.POST.get("qty", "1")
    try:
        qty = int(qty)
    except ValueError:
        qty = 1
    cart.add(product_id, qty)
    return redirect("store:cart_detail")

@require_POST
def cart_set(request, product_id: int):
    cart = Cart(request)
    qty = request.POST.get("qty", "1")
    try:
        qty = int(qty)
    except ValueError:
        qty = 1
    cart.set(product_id, qty)
    return redirect("store:cart_detail")

@require_POST
def cart_remove(request, product_id: int):
    cart = Cart(request)
    cart.remove(product_id)
    return redirect("store:cart_detail")

def checkout(request):
    cart = Cart(request)
    if request.method == "POST":
        cart.clear()
        return render(request, "store/checkout.html", {"success": True})
    return render(request, "store/checkout.html", {"success": False})
