# suppliers/admin.py
from django.contrib import admin
from .models import Supplier, PurchaseOrder

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'phone', 'city', 'is_active', 'created_at']
    list_filter = ['is_active', 'city', 'country']
    search_fields = ['name', 'email', 'phone', 'city']
    ordering = ['name']

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'product', 'quantity', 'total_amount', 'status', 'order_date']
    list_filter = ['status', 'order_date', 'supplier']
    search_fields = ['supplier__name', 'product__name', 'notes']
    readonly_fields = ['total_amount', 'order_date']