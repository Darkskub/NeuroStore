from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Product, Category, News, Order
from .cart import Cart
from .forms import ProductForm, CategoryForm, NewsForm, ManagerCreateForm
from .permissions import staff_or_superuser_required, superuser_required


def _is_client(user) -> bool:
    return bool(user and user.is_authenticated and (not user.is_staff) and (not user.is_superuser))


def _deny_cart_for_guests(request):
    messages.error(request, "Корзина доступна только авторизованным клиентам. Войдите или зарегистрируйтесь.")
    return redirect(f"{reverse('login')}?next={request.path}")


# ---------------------------
# ПУБЛИЧНЫЕ СТРАНИЦЫ
# ---------------------------

def home(request):
    news = News.objects.filter(is_published=True).order_by("-created_at")[:3]
    return render(request, "store/home.html", {"news": news})


def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.filter(parent__isnull=True).order_by("name")
    return render(request, "store/product_list.html", {"products": products, "categories": categories})


def catalog_category(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, "store/catalog_category.html", {"category": category, "products": products})


def category_list(request):
    categories = Category.objects.filter(parent__isnull=True).order_by("name")
    return render(request, "store/category_list.html", {"categories": categories})


def category_detail(request, slug: str):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category).order_by("name")
    return render(request, "store/category_detail.html", {"category": category, "products": products})


def news_list(request):
    news = News.objects.filter(is_published=True).order_by("-created_at")
    return render(request, "store/news_list.html", {"news": news})


def news_detail(request, slug: str):
    obj = get_object_or_404(News, slug=slug, is_published=True)
    return render(request, "store/news_detail.html", {"news": obj})


def about(request):
    return render(request, "store/about.html")


# ---------------------------
# РЕГИСТРАЦИЯ
# ---------------------------

def signup(request):
    if request.user.is_authenticated:
        return redirect("store:home")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Аккаунт создан. Добро пожаловать!")
            return redirect("store:home")
    else:
        form = UserCreationForm()

    return render(request, "registration/signup.html", {"form": form})


# ---------------------------
# МОИ ЗАКАЗЫ (ТОЛЬКО КЛИЕНТ)
# ---------------------------

def my_orders(request):
    if not _is_client(request.user):
        return _deny_cart_for_guests(request)

    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "store/my_orders.html", {"orders": orders})


def my_order_detail(request, order_id: int):
    if not _is_client(request.user):
        return _deny_cart_for_guests(request)

    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.select_related("product").all()
    return render(request, "store/my_order_detail.html", {"order": order, "items": items})


# ---------------------------
# КОРЗИНА / ОФОРМЛЕНИЕ (ТОЛЬКО КЛИЕНТЫ)
# ---------------------------

def cart_detail(request):
    if not _is_client(request.user):
        return _deny_cart_for_guests(request)
    cart = Cart(request)
    return render(request, "store/cart.html", {"cart": cart})


@require_POST
def cart_add(request, product_id: int):
    if not _is_client(request.user):
        return _deny_cart_for_guests(request)

    cart = Cart(request)
    qty = request.POST.get("qty", "1")
    try:
        qty = int(qty)
    except ValueError:
        qty = 1
    cart.add(product_id, qty)
    messages.success(request, "Товар добавлен в корзину.")
    return redirect("store:cart_detail")


@require_POST
def cart_set(request, product_id: int):
    if not _is_client(request.user):
        return _deny_cart_for_guests(request)

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
    if not _is_client(request.user):
        return _deny_cart_for_guests(request)

    cart = Cart(request)
    cart.remove(product_id)
    return redirect("store:cart_detail")


def checkout(request):
    if not _is_client(request.user):
        return _deny_cart_for_guests(request)

    cart = Cart(request)

    # если корзина пуста — просто показать страницу
    if request.method == "GET":
        return render(request, "store/checkout.html", {"success": False})

    # POST — оформить заказ
    if cart.total_qty() == 0:
        messages.error(request, "Корзина пуста.")
        return redirect("store:product_list")

    comment = (request.POST.get("comment") or "").strip()

    # Создаём заказ из корзины
    order = cart.create_order(comment=comment)
    cart.clear()

    messages.success(request, "Заказ оформлен. Корзина очищена.")
    return render(request, "store/checkout.html", {"success": True, "order": order})


# ---------------------------
# МЕНЕДЖЕРСКИЕ СТРАНИЦЫ (менеджер ИЛИ админ)
# ---------------------------

@staff_or_superuser_required
def manager_dashboard(request):
    return render(request, "store/manager/dashboard.html")


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

@login_required
def my_orders(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )
    return render(request, "store/my_orders.html", {"orders": orders})

def is_manager(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_manager)
def manager_orders(request):
    orders = (
        Order.objects
        .select_related("user")
        .prefetch_related("items__product")
        .order_by("-created_at")
    )
    return render(
        request,
        "store/manager/orders_list.html",
        {"orders": orders}
    )

@login_required
@user_passes_test(is_manager)
def manager_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        status = request.POST.get("status")
        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            order.save()

    return redirect("store:manager_orders")
