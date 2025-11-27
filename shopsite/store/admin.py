from django.contrib import admin
from .models import Product, Category, News, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price")
    list_filter = ("category",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "is_published")
    list_filter = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "body")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "status", "total_price")
    list_filter = ("status", "created_at")
    search_fields = ("user__username",)
    inlines = [OrderItemInline]
