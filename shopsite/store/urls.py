# store/urls.py
from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("checkout/", views.checkout, name="checkout"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("cart/set/<int:product_id>/", views.cart_set, name="cart_set"),
    path("manage/products/new/", views.product_create, name="product_create"),
    path("about/", views.about, name="about"),
]
