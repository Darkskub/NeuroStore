from django.contrib import admin
from .models import Product, Category, News

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "is_published")
    list_filter = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "body")

# Если Order/OrderItem появятся позже — просто добавишь их регистрацию.
