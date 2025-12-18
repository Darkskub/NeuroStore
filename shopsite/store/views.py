# store/views.py
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Prefetch, Q
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.utils.text import slugify
from django.views.decorators.http import require_GET, require_POST

from .cart import Cart
from .forms import (
    CategoryForm,
    ManagerCreateForm,
    NewsForm,
    ProductForm,
)
from .models import Category, News, Order, OrderItem, Product


# ---------------------------
# Helpers / roles
# ---------------------------

def _is_manager(user: User) -> bool:
    return user.is_authenticated and user.is_staff and (not user.is_superuser)


def _is_admin(user: User) -> bool:
    return user.is_authenticated and user.is_superuser


def _is_client(user: User) -> bool:
    # Клиент = обычный пользователь (не staff и не superuser)
    return user.is_authenticated and (not user.is_staff) and (not user.is_superuser)


def _deny_cart_for_guests(request: HttpRequest) -> HttpResponse | None:
    """
    Гостям запрещаем корзину/оформление/мои заказы.
    Возвращаем redirect, если гость. Иначе None.
    """
    if not request.user.is_authenticated:
        messages.warning(request, "Для доступа к корзине нужно войти в аккаунт.")
        return redirect("login")
    return None


def _deny_cart_for_not_clients(request: HttpRequest) -> HttpResponse | None:
    """
    Корзина/заказы доступны только клиентам (не staff, не superuser).
    """
    if not _is_client(request.user):
        return render(
            request,
            "store/forbidden.html",
            {"message": "Эта страница доступна только клиентам."},
            status=403,
        )
    return None


# ---------------------------
# Public pages
# ---------------------------

@require_GET
def home(request: HttpRequest) -> HttpResponse:
    news = News.objects.all().order_by("-created_at")[:3]
    return render(request, "store/home.html", {"news": news})


@require_GET
def news_list(request: HttpRequest) -> HttpResponse:
    news = News.objects.all().order_by("-created_at")
    return render(request, "store/news_list.html", {"news": news})


@require_GET
def news_detail(request: HttpRequest, slug: str) -> HttpResponse:
    item = get_object_or_404(News, slug=slug)
    return render(request, "store/news_detail.html", {"item": item})


@require_GET
def about(request: HttpRequest) -> HttpResponse:
    return render(request, "store/about.html")


def contacts(request: HttpRequest) -> HttpResponse:
    """
    Совместимость: если в urls.py есть /contacts/ и в base.html ссылка на contacts.
    """
    try:
        return render(request, "store/contacts.html")
    except TemplateDoesNotExist:
        # если вдруг contacts.html нет — покажем about.html
        return about(request)


# ---------------------------
# Catalog
# ---------------------------

@require_GET
def product_list(request: HttpRequest) -> HttpResponse:
    categories = Category.objects.all().order_by("name")
    products = Product.objects.all().order_by("-id")
    return render(
        request,
        "store/product_list.html",
        {"categories": categories, "products": products},
    )


@require_GET
def catalog_category(request: HttpRequest, slug: str) -> HttpResponse:
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category).order_by("-created_at")
    categories = Category.objects.all().order_by("name")
    return render(
        request,
        "store/catalog_category.html",
        {
            "category": category,
            "products": products,
            "categories": categories,
        },
    )


@require_GET
def category_list(request: HttpRequest) -> HttpResponse:
    categories = Category.objects.all().order_by("name")
    return render(request, "store/category_list.html", {"categories": categories})


@require_GET
def category_detail(request: HttpRequest, category_slug: str) -> HttpResponse:
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category).order_by("-created_at")
    return render(
        request,
        "store/category_detail.html",
        {"category": category, "products": products},
    )


# ---------------------------
# Auth / signup
# ---------------------------

def signup(request: HttpRequest) -> HttpResponse:
    """
    Регистрация через стандартный UserCreationForm.
    Шаблон: templates/registration/signup.html
    """
    if request.user.is_authenticated:
        return redirect("store:home")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("store:home")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


# ---------------------------
# Cart (clients only)
# ---------------------------

@require_GET
def cart_detail(request: HttpRequest) -> HttpResponse:
    denied = _deny_cart_for_guests(request)
    if denied:
        return denied
    denied2 = _deny_cart_for_not_clients(request)
    if denied2:
        return denied2

    cart = Cart(request)
    return render(
        request,
        "store/cart.html",
        {
            "cart_items": cart.items,
            "cart_total_qty": cart.total_quantity,
            "cart_total_price": cart.total_price,
        },
    )


def cart_view(request: HttpRequest) -> HttpResponse:
    """
    Алиас на cart_detail, чтобы твой текущий urls.py с views.cart_view не падал.
    """
    return cart_detail(request)


@require_POST
def cart_add(request: HttpRequest, product_id: int) -> HttpResponse:
    denied = _deny_cart_for_guests(request)
    if denied:
        return denied
    denied2 = _deny_cart_for_not_clients(request)
    if denied2:
        return denied2

    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product, qty=1)
    messages.success(request, f"Добавлено в корзину: {product.name}")
    return redirect(request.META.get("HTTP_REFERER", reverse("store:cart_detail")))


@require_POST
def cart_set(request: HttpRequest, product_id: int) -> HttpResponse:
    denied = _deny_cart_for_guests(request)
    if denied:
        return denied
    denied2 = _deny_cart_for_not_clients(request)
    if denied2:
        return denied2

    qty = int(request.POST.get("qty", "1"))
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.set(product, qty=max(qty, 0))
    return redirect("store:cart_detail")


@require_POST
def cart_remove(request: HttpRequest, product_id: int) -> HttpResponse:
    denied = _deny_cart_for_guests(request)
    if denied:
        return denied
    denied2 = _deny_cart_for_not_clients(request)
    if denied2:
        return denied2

    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("store:cart_detail")


# ---------------------------
# Checkout + Orders (clients)
# ---------------------------

def checkout(request: HttpRequest) -> HttpResponse:
    denied = _deny_cart_for_guests(request)
    if denied:
        return denied
    denied2 = _deny_cart_for_not_clients(request)
    if denied2:
        return denied2

    cart = Cart(request)

    if request.method == "POST":
        if cart.total_quantity == 0:
            return render(
                request,
                "store/checkout.html",
                {
                    "success": False,
                    "cart_total_qty": 0,
                    "cart_total_price": Decimal("0"),
                    "error": "Корзина пуста.",
                },
            )

        comment = (request.POST.get("comment") or "").strip()

        # Создаём заказ
        order = Order.objects.create(
            user=request.user,
            status=Order.STATUS_NEW,
            comment=comment,
        )

        # Создаём позиции заказа
        items = []
        for it in cart.items:
            items.append(
                OrderItem(
                    order=order,
                    product=it.product,
                    price=it.price,
                    quantity=it.qty,
                )
            )
        OrderItem.objects.bulk_create(items)

        cart.clear()

        return render(
            request,
            "store/checkout.html",
            {
                "success": True,
                "order": order,
                "cart_total_qty": 0,
                "cart_total_price": Decimal("0"),
            },
        )

    return render(
        request,
        "store/checkout.html",
        {
            "success": False,
            "cart_total_qty": cart.total_quantity,
            "cart_total_price": cart.total_price,
        },
    )


@login_required
def my_orders(request: HttpRequest) -> HttpResponse:
    denied2 = _deny_cart_for_not_clients(request)
    if denied2:
        return denied2

    orders = (
        Order.objects.filter(user=request.user)
        .order_by("-created_at")
        .prefetch_related("items", "items__product")
    )
    return render(request, "store/my_orders.html", {"orders": orders})


@login_required
def my_order_detail(request: HttpRequest, order_id: int) -> HttpResponse:
    denied2 = _deny_cart_for_not_clients(request)
    if denied2:
        return denied2

    order = get_object_or_404(
        Order.objects.prefetch_related("items", "items__product"),
        id=order_id,
        user=request.user,
    )
    return render(request, "store/my_order_detail.html", {"order": order})


# ---------------------------
# Manager: view client orders + change status
# ---------------------------

@login_required
@user_passes_test(_is_manager)
def manager_dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, "store/manager/dashboard.html")


@login_required
@user_passes_test(_is_manager)
def manager_orders(request: HttpRequest) -> HttpResponse:
    orders = (
        Order.objects.all()
        .order_by("-created_at")
        .select_related("user")
        .prefetch_related("items", "items__product")
    )
    return render(request, "store/manager/orders_list.html", {"orders": orders})


@login_required
@user_passes_test(_is_manager)
def manager_set_status(request: HttpRequest, order_id: int) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        new_status = request.POST.get("status", "").strip()
        valid_statuses = {c[0] for c in Order.STATUS_CHOICES}
        if new_status in valid_statuses:
            order.status = new_status
            order.save(update_fields=["status"])
            messages.success(request, f"Статус заказа #{order.id} обновлён.")
        else:
            messages.error(request, "Некорректный статус.")
    return redirect("store:manager_orders")


@login_required
@user_passes_test(_is_manager)
def manager_carts(request: HttpRequest) -> HttpResponse:
    # Заглушка/страница: если у тебя реализована таблица активных корзин — сюда можно подключить.
    return render(request, "store/manager/carts_list.html")


@login_required
@user_passes_test(_is_manager)
def manager_cart_detail(request: HttpRequest, user_id: int) -> HttpResponse:
    # Заглушка/страница: если у тебя реализована таблица активных корзин — сюда можно подключить.
    user = get_object_or_404(User, id=user_id)
    return render(request, "store/manager/cart_detail.html", {"client_user": user})


# ---------------------------
# Manager: add product
# ---------------------------

@login_required
@user_passes_test(_is_manager)
def product_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Товар создан: {product.name}")
            return redirect("store:product_list")
    else:
        form = ProductForm()

    return render(request, "store/product_form.html", {"form": form})


# ---------------------------
# Admin panel (superuser)
# ---------------------------

@login_required
@user_passes_test(_is_admin)
def panel_dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, "store/panel/dashboard.html")


@login_required
@user_passes_test(_is_admin)
def panel_products(request: HttpRequest) -> HttpResponse:
    products = Product.objects.all().order_by("-created_at")
    return render(request, "store/panel/products_list.html", {"products": products})


@login_required
@user_passes_test(_is_admin)
def panel_product_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Товар создан: {product.name}")
            return redirect("store:panel_products")
    else:
        form = ProductForm()
    return render(request, "store/panel/product_form.html", {"form": form})


@login_required
@user_passes_test(_is_admin)
def panel_product_edit(request: HttpRequest, product_id: int) -> HttpResponse:
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Товар обновлён.")
            return redirect("store:panel_products")
    else:
        form = ProductForm(instance=product)
    return render(request, "store/panel/product_form.html", {"form": form, "product": product})


@login_required
@user_passes_test(_is_admin)
def panel_product_delete(request: HttpRequest, product_id: int) -> HttpResponse:
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Товар удалён.")
        return redirect("store:panel_products")
    return render(request, "store/panel/product_delete.html", {"product": product})


@login_required
@user_passes_test(_is_admin)
def panel_categories(request: HttpRequest) -> HttpResponse:
    categories = Category.objects.all().order_by("name")
    return render(request, "store/panel/categories_list.html", {"categories": categories})


@login_required
@user_passes_test(_is_admin)
def panel_category_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Категория создана: {cat.name}")
            return redirect("store:panel_categories")
    else:
        form = CategoryForm()
    return render(request, "store/panel/category_form.html", {"form": form})


@login_required
@user_passes_test(_is_admin)
def panel_category_edit(request: HttpRequest, cat_id: int) -> HttpResponse:
    cat = get_object_or_404(Category, id=cat_id)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, "Категория обновлена.")
            return redirect("store:panel_categories")
    else:
        form = CategoryForm(instance=cat)
    return render(request, "store/panel/category_form.html", {"form": form, "category": cat})


@login_required
@user_passes_test(_is_admin)
def panel_category_delete(request: HttpRequest, cat_id: int) -> HttpResponse:
    cat = get_object_or_404(Category, id=cat_id)
    if request.method == "POST":
        cat.delete()
        messages.success(request, "Категория удалена.")
        return redirect("store:panel_categories")
    return render(request, "store/panel/category_delete.html", {"category": cat})


@login_required
@user_passes_test(_is_admin)
def panel_news(request: HttpRequest) -> HttpResponse:
    news = News.objects.all().order_by("-created_at")
    return render(request, "store/panel/news_list.html", {"news": news})


@login_required
@user_passes_test(_is_admin)
def panel_news_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = NewsForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, f"Новость создана: {item.title}")
            return redirect("store:panel_news")
    else:
        form = NewsForm()
    return render(request, "store/panel/news_form.html", {"form": form})


@login_required
@user_passes_test(_is_admin)
def panel_news_edit(request: HttpRequest, news_id: int) -> HttpResponse:
    item = get_object_or_404(News, id=news_id)
    if request.method == "POST":
        form = NewsForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Новость обновлена.")
            return redirect("store:panel_news")
    else:
        form = NewsForm(instance=item)
    return render(request, "store/panel/news_form.html", {"form": form, "item": item})


@login_required
@user_passes_test(_is_admin)
def panel_news_delete(request: HttpRequest, news_id: int) -> HttpResponse:
    item = get_object_or_404(News, id=news_id)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Новость удалена.")
        return redirect("store:panel_news")
    return render(request, "store/panel/news_delete.html", {"item": item})


@login_required
@user_passes_test(_is_admin)
def panel_users(request: HttpRequest) -> HttpResponse:
    users = User.objects.all().order_by("username")
    return render(request, "store/panel/users_list.html", {"users": users})


@login_required
@user_passes_test(_is_admin)
def panel_user_create_manager(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ManagerCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = False
            user.set_password(form.cleaned_data["password1"])
            user.save()
            messages.success(request, f"Менеджер создан: {user.username}")
            return redirect("store:panel_users")
    else:
        form = ManagerCreateForm()
    return render(request, "store/panel/user_create_manager.html", {"form": form})


# ---------------------------
# Register (alias page if you need)
# ---------------------------

def register(request: HttpRequest) -> HttpResponse:
    # если используешь отдельный шаблон store/register.html
    if request.user.is_authenticated:
        return redirect("store:home")
    return redirect("store:signup")

@user_passes_test(_is_admin)
def panel_products(request):
    # Product НЕ имеет created_at, поэтому сортируем по id (новые сверху)
    products = Product.objects.select_related("category").order_by("-id")
    return render(request, "store/panel/products_list.html", {"products": products})
