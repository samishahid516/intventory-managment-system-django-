# sales/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import SaleOrder, OrderItem
from .forms import SaleOrderForm
from accounts.decorators import manager_required
from accounts.models import UserActivityLog

@login_required
def sale_list(request):
    orders = SaleOrder.objects.all().order_by('-order_date')
    return render(request, 'sales/sale_list.html', {'orders': orders})

@login_required
@manager_required
def sale_create(request):
    if request.method == 'POST':
        form = SaleOrderForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.created_by = request.user
            sale.save()
            UserActivityLog.objects.create(
                user=request.user,
                action='sale_created',
                details=f'Created sale order {sale.order_number}'
            )
            messages.success(request, f'Sale order {sale.order_number} created successfully.')
            return redirect('sales:sale_list')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = SaleOrderForm()
    
    return render(request, 'sales/sale_form.html', {'form': form})

@login_required
@manager_required
def manager_orders(request):
    status_filter = request.GET.get('status', 'all')
    date_filter = request.GET.get('date', 'all')
    
    orders = SaleOrder.objects.select_related('created_by').all()
    
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    if date_filter == 'today':
        orders = orders.filter(order_date__date=timezone.now().date())
    elif date_filter == 'week':
        week_ago = timezone.now() - timedelta(days=7)
        orders = orders.filter(order_date__gte=week_ago)
    elif date_filter == 'month':
        month_ago = timezone.now() - timedelta(days=30)
        orders = orders.filter(order_date__gte=month_ago)
    
    orders = orders.order_by('-order_date')
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'status_choices': SaleOrder.STATUS_CHOICES,
        'total_orders': orders.count(),
        'total_revenue': orders.aggregate(total=Sum('total_amount'))['total'] or 0,
        'pending_count': orders.filter(status='pending').count(),
        'delivered_count': orders.filter(status='delivered').count(),
        'cancelled_count': orders.filter(status='cancelled').count(),
    }
    
    return render(request, 'sales/manager_orders.html', context)

@login_required
@manager_required
def manager_order_detail(request, order_id):
    order = get_object_or_404(SaleOrder, id=order_id)
    items = order.order_items.all()
    
    return render(request, 'sales/manager_order_detail.html', {
        'order': order,
        'items': items
    })

@login_required
@manager_required
def manager_update_order(request, order_id):
    order = get_object_or_404(SaleOrder, id=order_id)
    
    if request.method == 'POST':
        order.customer_name = request.POST.get('customer_name', order.customer_name)
        order.customer_email = request.POST.get('customer_email', order.customer_email)
        order.customer_phone = request.POST.get('customer_phone', order.customer_phone)
        order.customer_address = request.POST.get('customer_address', order.customer_address)
        order.notes = request.POST.get('notes', order.notes)
        
        status = request.POST.get('status')
        if status in dict(SaleOrder.STATUS_CHOICES):
            order.status = status
        
        payment_status = request.POST.get('payment_status')
        if payment_status in dict(SaleOrder.PAYMENT_STATUS_CHOICES):
            order.payment_status = payment_status
        
        order.save()
        
        UserActivityLog.objects.create(
            user=request.user,
            action='order_updated',
            details=f'Updated order #{order.order_number}'
        )
        
        messages.success(request, f'Order #{order.order_number} updated successfully.')
        return redirect('sales:manager_orders')
    
    return render(request, 'sales/manager_update_order.html', {'order': order})