# store/urls.py
from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    # Public
    path("", views.home, name="home"),
    path("news/", views.news_list, name="news_list"),
    path("news/<slug:slug>/", views.news_detail, name="news_detail"),
    path("about/", views.about, name="about"),
    path("contacts/", views.contacts, name="contacts"),

    # Catalog
    path("catalog/", views.product_list, name="product_list"),
    path("catalog/category/<slug:slug>/", views.catalog_category, name="catalog_category"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/<slug:category_slug>/", views.category_detail, name="category_detail"),

    # Auth
    path("signup/", views.signup, name="signup"),
    path("register/", views.register, name="register"),

    # Cart / checkout (clients)
    path("cart/", views.cart_view, name="cart"),                 # твой текущий вариант
    path("cart/", views.cart_detail, name="cart_detail"),        # совместимость: если где-то reverse('cart_detail')
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/set/<int:product_id>/", views.cart_set, name="cart_set"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("my-orders/<int:order_id>/", views.my_order_detail, name="my_order_detail"),

    # Manager
    path("manager/", views.manager_dashboard, name="manager_dashboard"),
    path("manager/orders/", views.manager_orders, name="manager_orders"),
    path("manager/orders/<int:order_id>/set-status/", views.manager_set_status, name="manager_set_status"),
    path("manager/carts/", views.manager_carts, name="manager_carts"),
    path("manager/carts/<int:user_id>/", views.manager_cart_detail, name="manager_cart_detail"),
    path("manage/products/new/", views.product_create, name="product_create"),

    # Admin panel (superuser)
    path("panel/", views.panel_dashboard, name="panel_dashboard"),
    path("panel/products/", views.panel_products, name="panel_products"),
    path("panel/products/new/", views.panel_product_create, name="panel_product_create"),
    path("panel/products/<int:product_id>/edit/", views.panel_product_edit, name="panel_product_edit"),
    path("panel/products/<int:product_id>/delete/", views.panel_product_delete, name="panel_product_delete"),

    path("panel/categories/", views.panel_categories, name="panel_categories"),
    path("panel/categories/new/", views.panel_category_create, name="panel_category_create"),
    path("panel/categories/<int:cat_id>/edit/", views.panel_category_edit, name="panel_category_edit"),
    path("panel/categories/<int:cat_id>/delete/", views.panel_category_delete, name="panel_category_delete"),

    path("panel/news/", views.panel_news, name="panel_news"),
    path("panel/news/new/", views.panel_news_create, name="panel_news_create"),
    path("panel/news/<int:news_id>/edit/", views.panel_news_edit, name="panel_news_edit"),
    path("panel/news/<int:news_id>/delete/", views.panel_news_delete, name="panel_news_delete"),

    path("panel/users/", views.panel_users, name="panel_users"),
    path("panel/users/create-manager/", views.panel_user_create_manager, name="panel_user_create_manager"),
    path("panel/users/create-manager/", views.panel_user_create_manager, name="panel_create_manager"),  # алиас
]
