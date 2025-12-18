from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),

    path("catalog/", views.product_list, name="product_list"),
    path("catalog/category/<slug:slug>/", views.catalog_category, name="catalog_category"),

    path("categories/", views.category_list, name="category_list"),
    path("categories/<slug:slug>/", views.category_detail, name="category_detail"),

    path("news/", views.news_list, name="news_list"),
    path("news/<slug:slug>/", views.news_detail, name="news_detail"),

    path("about/", views.about, name="about"),

    path("signup/", views.signup, name="signup"),

    # cart / checkout
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/set/<int:product_id>/", views.cart_set, name="cart_set"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("my-orders/", views.my_orders, name="my_orders"),


    # my orders (client only)
    path("my-orders/", views.my_orders, name="my_orders"),
    path("my-orders/<int:order_id>/", views.my_order_detail, name="my_order_detail"),

    # manager
    path("manager/", views.manager_dashboard, name="manager_dashboard"),
    path("manager/orders/", views.manager_orders, name="manager_orders"),
    path("manager/orders/<int:order_id>/status/", views.manager_order_status, name="manager_order_status"),


    # panel (superuser)
    path("panel/", views.panel_dashboard, name="panel_dashboard"),

    path("panel/categories/", views.panel_categories, name="panel_categories"),
    path("panel/categories/create/", views.panel_category_create, name="panel_category_create"),
    path("panel/categories/<int:pk>/edit/", views.panel_category_edit, name="panel_category_edit"),
    path("panel/categories/<int:pk>/delete/", views.panel_category_delete, name="panel_category_delete"),

    path("panel/products/", views.panel_products, name="panel_products"),
    path("panel/products/create/", views.panel_product_create, name="panel_product_create"),
    path("panel/products/<int:pk>/edit/", views.panel_product_edit, name="panel_product_edit"),
    path("panel/products/<int:pk>/delete/", views.panel_product_delete, name="panel_product_delete"),

    path("panel/news/", views.panel_news, name="panel_news"),
    path("panel/news/create/", views.panel_news_create, name="panel_news_create"),
    path("panel/news/<int:pk>/edit/", views.panel_news_edit, name="panel_news_edit"),
    path("panel/news/<int:pk>/delete/", views.panel_news_delete, name="panel_news_delete"),

    path("panel/users/", views.panel_users, name="panel_users"),
    path("panel/users/create-manager/", views.panel_user_create_manager, name="panel_user_create_manager"),
    path("panel/users/<int:pk>/delete/", views.panel_user_delete, name="panel_user_delete"),
]
