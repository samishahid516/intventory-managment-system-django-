# products/admin.py
from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ['name']}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'quantity', 'status', 'category', 'created_at']
    list_filter = ['status', 'category', 'is_featured', 'created_at']
    search_fields = ['name', 'sku', 'brand', 'model', 'description']
    readonly_fields = ['slug', 'sku', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ['name']}