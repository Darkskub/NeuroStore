# store/views.py
from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import ProductForm, UserRegisterForm
from .models import Category, Product, News, Order, OrderItem, ActiveCart


# ====== РОЛИ ======

def is_client(user):
    # Клиент — залогиненный пользователь, который не staff и не superuser
    return user.is_authenticated and not user.is_staff and not user.is_superuser


def is_manager(user):
    # Менеджер — staff, но не superuser
    return user.is_authenticated and user.is_staff and not user.is_superuser


def is_admin(user):
    # Администратор — superuser
    return user.is_authenticated and user.is_superuser


# ====== ГЛАВНАЯ, НОВОСТИ, КОНТАКТЫ, КАТАЛОГ ======

def home(request):
    last_news = News.objects.filter(is_published=True)[:3]
    return render(request, "store/home.html", {"last_news": last_news})


def news_list(request):
    news = News.objects.filter(is_published=True)
    return render(request, "store/news_list.html", {"news_list": news})


def news_detail(request, slug: str):
    news_item = get_object_or_404(News, slug=slug, is_published=True)
    return render(request, "store/news_detail.html", {"news": news_item})


def contacts(request):
    return render(request, "store/contacts.html")


def category_list(request):
    categories = Category.objects.all()
    return render(request, "store/category_list.html", {"categories": categories})


def category_detail(request, category_slug: str):
    category = get_object_or_404(Category, slug=category_slug)
    products = category.products.all()
    return render(
        request,
        "store/category_detail.html",
        {"category": category, "products": products},
    )


# ====== КОРЗИНА / ОФОРМЛЕНИЕ — КЛИЕНТ ======

@login_required
@user_passes_test(is_client)
def cart_detail(request):
    cart = Cart(request)
    return render(request, "store/cart.html", {"cart": cart})


@login_required
@user_passes_test(is_client)
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


@login_required
@user_passes_test(is_client)
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


@login_required
@user_passes_test(is_client)
@require_POST
def cart_remove(request, product_id: int):
    cart = Cart(request)
    cart.remove(product_id)
    return redirect("store:cart_detail")


@login_required
@user_passes_test(is_client)
def checkout(request):
    cart = Cart(request)

    if request.method == "POST":
        if cart.total_qty() == 0:
            messages.error(request, "Корзина пуста.")
            return redirect("store:cart_detail")

        comment = request.POST.get("comment", "").strip()
        order = Order.objects.create(user=request.user, comment=comment)

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                price=item["price"],
                qty=item["qty"],
            )

        cart.clear()
        return render(
            request,
            "store/checkout.html",
            {"success": True, "order": order},
        )

    return render(
        request,
        "store/checkout.html",
        {"success": False},
    )


# ====== МОИ ЗАКАЗЫ — КЛИЕНТ ======

@login_required
@user_passes_test(is_client)
def my_orders(request):
    orders = request.user.orders.all()
    return render(request, "store/my_orders.html", {"orders": orders})


@login_required
@user_passes_test(is_client)
@require_POST
def my_order_delete(request, order_id: int):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == Order.STATUS_NEW:
        order.delete()
        messages.success(request, "Заказ удалён.")
    else:
        messages.error(request, "Можно удалять только новые заказы.")
    return redirect("store:my_orders")


# ====== ЗАКАЗЫ — МЕНЕДЖЕР ======

@login_required
@user_passes_test(is_manager)
def manager_orders(request):
    orders = (
        Order.objects.select_related("user")
        .prefetch_related("items", "items__product")
        .all()
    )
    return render(request, "store/manager_orders.html", {"orders": orders})


@login_required
@user_passes_test(is_manager)
@require_POST
def manager_set_status(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get("status")
    valid_statuses = {choice[0] for choice in Order.STATUS_CHOICES}
    if new_status in valid_statuses:
        order.status = new_status
        order.save()
        messages.success(request, f"Статус заказа #{order.id} изменён.")
    else:
        messages.error(request, "Некорректный статус.")
    return redirect("store:manager_orders")


# ====== КОРЗИНЫ КЛИЕНТОВ — МЕНЕДЖЕР ======

@login_required
@user_passes_test(is_manager)
def manager_carts(request):
    """
    Список всех корзин клиентов: кто, сколько товаров, на какую сумму.
    """
    carts = (
        ActiveCart.objects.select_related("user")
        .prefetch_related("items", "items__product")
        .all()
        .order_by("user__username")
    )
    return render(request, "store/manager_carts.html", {"carts": carts})


@login_required
@user_passes_test(is_manager)
def manager_cart_detail(request, user_id: int):
    """
    Просмотр и управление корзиной конкретного клиента.
    Менеджер может изменить количества, удалить позиции или очистить корзину.
    """
    cart_user = get_object_or_404(User, id=user_id)
    cart_obj, _ = ActiveCart.objects.get_or_create(user=cart_user)

    if request.method == "POST":
        changed = False

        # Очистка корзины целиком
        if "clear_cart" in request.POST:
            cart_obj.items.all().delete()
            changed = True
        else:
            # Обновление количеств по каждому item
            for item in cart_obj.items.all():
                field_name = f"qty_{item.id}"
                if field_name in request.POST:
                    raw_val = request.POST.get(field_name, "").strip()
                    try:
                        qty = int(raw_val)
                    except ValueError:
                        qty = item.qty

                    if qty <= 0:
                        item.delete()
                        changed = True
                    elif qty != item.qty:
                        item.qty = qty
                        item.save()
                        changed = True

        if changed:
            messages.success(request, "Корзина клиента обновлена.")
        else:
            messages.info(request, "Изменений не обнаружено.")

        return redirect("store:manager_cart_detail", user_id=cart_user.id)

    return render(
        request,
        "store/manager_cart_detail.html",
        {
            "cart_user": cart_user,
            "cart": cart_obj,
        },
    )


# ====== УПРАВЛЕНИЕ ТОВАРАМИ — ПЕРСОНАЛ ======

@staff_member_required
def product_create(request):
    """
    Страница для админ-персонала: добавить товар без захода в /admin.
    Доступно только is_staff пользователям (Менеджер/Админ).
    """
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Товар «{product.name}» добавлен.")
            return redirect("store:category_list")
    else:
        form = ProductForm()
    return render(request, "store/product_form.html", {"form": form})


# ====== РЕГИСТРАЦИЯ КЛИЕНТА ======

def register(request):
    """
    Регистрация нового пользователя со статусом «Клиент».
    """
    if request.user.is_authenticated:
        return redirect("store:home")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            user.is_superuser = False
            user.save()
            messages.success(request, "Регистрация выполнена. Войдите под своим логином.")
            return redirect("login")
    else:
        form = UserRegisterForm()

    return render(request, "store/register.html", {"form": form})
