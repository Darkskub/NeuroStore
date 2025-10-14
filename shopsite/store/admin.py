from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")
