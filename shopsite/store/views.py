from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Product, Category, News
from .cart import Cart
from .forms import ProductForm, CategoryForm, NewsForm, ManagerCreateForm
from .permissions import staff_or_superuser_required, superuser_required


# ---------------------------
# ПУБЛИЧНЫЕ СТРАНИЦЫ
# ---------------------------

def home(request):
    products = Product.objects.all()[:9]
    news = News.objects.filter(is_published=True).order_by("-created_at")[:3]
    return render(request, "store/home.html", {"products": products, "news": news})


def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.filter(parent__isnull=True).order_by("name")
    return render(request, "store/product_list.html", {"products": products, "categories": categories})


def catalog_category(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, "store/catalog_category.html", {"category": category, "products": products})


def news_list(request):
    news = News.objects.filter(is_published=True).order_by("-created_at")
    return render(request, "store/news_list.html", {"news": news})


def about(request):
    return render(request, "store/about.html")


# ---------------------------
# КОРЗИНА / ОФОРМЛЕНИЕ
# ---------------------------

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
        # тут позже можно создавать Order/OrderItem в БД
        cart.clear()
        return render(request, "store/checkout.html", {"success": True})
    return render(request, "store/checkout.html", {"success": False})


# ---------------------------
# МЕНЕДЖЕРСКИЕ СТРАНИЦЫ (доступ: менеджер ИЛИ админ)
# ---------------------------

@staff_or_superuser_required
def manager_dashboard(request):
    return render(request, "store/manager/dashboard.html")


# пример: здесь позже подключишь реальные модели Order/ActiveCart
@staff_or_superuser_required
def manager_stub_orders(request):
    return render(request, "store/manager/orders_stub.html")


# ---------------------------
# ПАНЕЛЬ АДМИНИСТРАТОРА ВНУТРИ САЙТА (только superuser)
# ---------------------------

@superuser_required
def panel_dashboard(request):
    return render(request, "store/panel/dashboard.html")


# ----- Категории -----

@superuser_required
def panel_categories(request):
    cats = Category.objects.select_related("parent").order_by("name")
    return render(request, "store/panel/categories_list.html", {"cats": cats})


@superuser_required
def panel_category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Категория добавлена.")
            return redirect("store:panel_categories")
    else:
        form = CategoryForm()
    return render(request, "store/panel/category_form.html", {"form": form, "mode": "create"})


@superuser_required
def panel_category_edit(request, pk: int):
    obj = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Категория обновлена.")
            return redirect("store:panel_categories")
    else:
        form = CategoryForm(instance=obj)
    return render(request, "store/panel/category_form.html", {"form": form, "mode": "edit", "obj": obj})


@superuser_required
@require_POST
def panel_category_delete(request, pk: int):
    obj = get_object_or_404(Category, pk=pk)
    try:
        obj.delete()
        messages.success(request, "Категория удалена.")
    except Exception:
        messages.error(request, "Нельзя удалить категорию (возможно, в ней есть товары).")
    return redirect("store:panel_categories")


# ----- Товары -----

@superuser_required
def panel_products(request):
    products = Product.objects.select_related("category").order_by("name")
    return render(request, "store/panel/products_list.html", {"products": products})


@superuser_required
def panel_product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Товар добавлен.")
            return redirect("store:panel_products")
    else:
        form = ProductForm()
    return render(request, "store/panel/product_form.html", {"form": form, "mode": "create"})


@superuser_required
def panel_product_edit(request, pk: int):
    obj = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Товар обновлён.")
            return redirect("store:panel_products")
    else:
        form = ProductForm(instance=obj)
    return render(request, "store/panel/product_form.html", {"form": form, "mode": "edit", "obj": obj})


@superuser_required
@require_POST
def panel_product_delete(request, pk: int):
    obj = get_object_or_404(Product, pk=pk)
    obj.delete()
    messages.success(request, "Товар удалён.")
    return redirect("store:panel_products")


# ----- Новости -----

@superuser_required
def panel_news(request):
    news = News.objects.order_by("-created_at")
    return render(request, "store/panel/news_list.html", {"news": news})


@superuser_required
def panel_news_create(request):
    if request.method == "POST":
        form = NewsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Новость добавлена.")
            return redirect("store:panel_news")
    else:
        form = NewsForm()
    return render(request, "store/panel/news_form.html", {"form": form, "mode": "create"})


@superuser_required
def panel_news_edit(request, pk: int):
    obj = get_object_or_404(News, pk=pk)
    if request.method == "POST":
        form = NewsForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Новость обновлена.")
            return redirect("store:panel_news")
    else:
        form = NewsForm(instance=obj)
    return render(request, "store/panel/news_form.html", {"form": form, "mode": "edit", "obj": obj})


@superuser_required
@require_POST
def panel_news_delete(request, pk: int):
    obj = get_object_or_404(News, pk=pk)
    obj.delete()
    messages.success(request, "Новость удалена.")
    return redirect("store:panel_news")


# ----- Пользователи -----

@superuser_required
def panel_users(request):
    users = User.objects.order_by("username")
    return render(request, "store/panel/users_list.html", {"users": users})


@superuser_required
def panel_user_create_manager(request):
    if request.method == "POST":
        form = ManagerCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Менеджер создан.")
            return redirect("store:panel_users")
    else:
        form = ManagerCreateForm()
    return render(request, "store/panel/user_manager_form.html", {"form": form})


@superuser_required
@require_POST
def panel_user_delete(request, pk: int):
    u = get_object_or_404(User, pk=pk)
    if u.is_superuser:
        messages.error(request, "Нельзя удалить администратора.")
        return redirect("store:panel_users")
    u.delete()
    messages.success(request, "Пользователь удалён.")
    return redirect("store:panel_users")
