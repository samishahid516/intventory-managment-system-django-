# sales/admin.py
from django.contrib import admin
from .models import SaleOrder, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('subtotal',)

@admin.register(SaleOrder)
class SaleOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'total_amount', 'status', 'payment_status', 'order_date')
    list_filter = ('status', 'payment_status', 'order_date')
    search_fields = ('order_number', 'customer_name', 'customer_email')
    readonly_fields = ('order_number', 'order_date', 'subtotal', 'total_amount')
    inlines = [OrderItemInline]