from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    # Главная
    path("", views.home, name="home"),

    # Новости
    path("news/", views.news_list, name="news_list"),
    path("news/<slug:slug>/", views.news_detail, name="news_detail"),

    # Контакты
    path("contacts/", views.contacts, name="contacts"),

    # Каталог
    path("catalog/", views.category_list, name="category_list"),
    path("catalog/<slug:category_slug>/", views.category_detail, name="category_detail"),

    # Корзина / заказ (клиент)
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("cart/set/<int:product_id>/", views.cart_set, name="cart_set"),
    path("checkout/", views.checkout, name="checkout"),

    # Мои заказы (клиент)
    path("my-orders/", views.my_orders, name="my_orders"),
    path("my-orders/delete/<int:order_id>/", views.my_order_delete, name="my_order_delete"),

    # Заказы (менеджер)
    path("manager/orders/", views.manager_orders, name="manager_orders"),
    path(
        "manager/orders/<int:order_id>/set-status/",
        views.manager_set_status,
        name="manager_set_status",
    ),

    # Корзины клиентов (менеджер)
    path("manager/carts/", views.manager_carts, name="manager_carts"),
    path(
        "manager/carts/<int:user_id>/",
        views.manager_cart_detail,
        name="manager_cart_detail",
    ),

    # Управление товарами (персонал)
    path("manage/products/new/", views.product_create, name="product_create"),

    # Регистрация клиента
    path("register/", views.register, name="register"),
]
