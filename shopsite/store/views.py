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

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .forms import ProductForm

@staff_member_required
def product_create(request):
    """
    Страница для админ-персонала: добавить товар без захода в /admin.
    Доступно только is_staff пользователям.
    """
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Товар «{product.name}» добавлен.")
            return redirect("store:product_list")
    else:
        form = ProductForm()
    return render(request, "store/product_form.html", {"form": form})

def about(request):
    return render(request, "store/about.html")
