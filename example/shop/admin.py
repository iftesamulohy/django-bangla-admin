from django.contrib import admin

from .models import Category, Order, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_active", "created_at")
    list_filter = ("is_active", "category")
    search_fields = ("name",)
    list_editable = ("price", "stock", "is_active")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("__str__", "product", "quantity", "total", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("customer_name",)
    date_hierarchy = "created_at"
