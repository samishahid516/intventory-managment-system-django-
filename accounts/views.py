# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Sum, F, ExpressionWrapper, DecimalField, Avg
from django.utils import timezone
from django.utils.timezone import localdate
from datetime import timedelta
from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm
from .models import User, UserActivityLog, SystemSetting
from .decorators import admin_required

# ============================================
# AUTHENTICATION VIEWS
# ============================================

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = UserLoginForm
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        
        UserActivityLog.objects.create(
            user=user,
            action='login',
            details=f'User {user.username} logged in',
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        user.last_login_ip = self.request.META.get('REMOTE_ADDR')
        user.save(update_fields=['last_login_ip'])
        
        return response

    def get_success_url(self):
        return '/'

class CustomLogoutView(LogoutView):
    http_method_names = ['get', 'post', 'options']
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            UserActivityLog.objects.create(
                user=request.user,
                action='logout',
                details=f'User {request.user.username} logged out'
            )
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to the Inventory System.')
            return redirect('accounts:dashboard')
        messages.error(request, 'Please fix the errors below and try again.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

# ============================================
# DASHBOARD VIEW
# ============================================

@login_required
def dashboard(request):
    from products.models import Product
    from sales.models import SaleOrder
    from suppliers.models import Supplier
    
    today = localdate()
    current_month = today.month
    current_year = today.year
    
    total_inventory_value = Product.objects.aggregate(
        total=Sum(ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField(max_digits=14, decimal_places=2)))
    )['total'] or 0

    from sales.models import OrderItem
    cogs = OrderItem.objects.aggregate(
        total=Sum(ExpressionWrapper(F('product__cost_price') * F('quantity'), output_field=DecimalField(max_digits=14, decimal_places=2)))
    )['total'] or 0

    revenue = SaleOrder.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    profit = revenue - cogs

    monthly_sales_amount = SaleOrder.objects.filter(
        order_date__year=current_year,
        order_date__month=current_month,
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    monthly_sales_count = SaleOrder.objects.filter(
        order_date__year=current_year,
        order_date__month=current_month,
    ).count()

    top_selling_products = (
        Product.objects.annotate(sold_qty=Sum('sale_items__quantity'))
        .filter(sold_qty__gt=0)
        .order_by('-sold_qty', 'name')[:5]
    )

    recent_logs = UserActivityLog.objects.select_related('user').order_by('-timestamp')[:10]
    
    context = {
        'user': request.user,
        'today': timezone.now(),
        'total_products': Product.objects.count(),
        'low_stock': Product.objects.filter(quantity__lte=F('min_stock_level')).count(),
        'total_sales': SaleOrder.objects.count(),
        'total_suppliers': Supplier.objects.count(),
        'total_users': User.objects.count(),
        'pending_orders': SaleOrder.objects.filter(status='pending').count(),
        'out_of_stock': Product.objects.filter(quantity=0).count(),
        'recent_orders': SaleOrder.objects.order_by('-order_date')[:5],
        'recent_products': Product.objects.select_related('category', 'supplier').order_by('-created_at')[:5],
        'recent_suppliers': Supplier.objects.filter(is_active=True).order_by('name')[:5],
        'low_stock_products': Product.objects.filter(quantity__lte=F('min_stock_level')).order_by('quantity')[:5],
        'total_inventory_value': total_inventory_value,
        'revenue': revenue,
        'profit': profit,
        'monthly_sales_amount': monthly_sales_amount,
        'monthly_sales_count': monthly_sales_count,
        'top_selling_products': top_selling_products,
        'active_staff_count': User.objects.filter(is_active=True, is_staff=True).count(),
        'role_counts': User.objects.values('role').annotate(count=Count('id')).order_by('role'),
        'today_sales_count': SaleOrder.objects.filter(order_date__date=today).count(),
        'today_sales_amount': SaleOrder.objects.filter(order_date__date=today).aggregate(total=Sum('total_amount'))['total'] or 0,
        'system_activity': recent_logs,
    }

    dashboard_templates = {
        'admin': 'dashboard/admin_dashboard.html',
        'worker': 'dashboard/worker_dashboard.html',
        'sale_manager': 'dashboard/manager_dashboard.html',
        'supplier': 'dashboard/supplier_dashboard.html',
    }
    template_name = dashboard_templates.get(request.user.role, 'dashboard/dashboard.html')

    if request.user.role == 'admin':
        # Use a different variable name to avoid conflict with imported timedelta
        from datetime import timedelta as td
        today_dt = localdate()
        start_of_week = today_dt - td(days=today_dt.weekday())
        start_of_month = today_dt.replace(day=1)
        week_sales_qs = SaleOrder.objects.filter(order_date__gte=start_of_week)
        context.update({
            'total_revenue': revenue,
            'profit_margin': (profit / revenue * 100) if revenue > 0 else 0,
            'low_stock_count': context['low_stock'],
            'out_of_stock_count': context['out_of_stock'],
            'week_sales_count': week_sales_qs.count(),
            'week_sales_amount': week_sales_qs.aggregate(total=Sum('total_amount'))['total'] or 0,
            'month_sales_amount': monthly_sales_amount,
            'month_sales_count': monthly_sales_count,
            'processing_orders': SaleOrder.objects.filter(status='processing').count(),
            'recent_activity': recent_logs,
            'total_suppliers': Supplier.objects.count(),
            'active_suppliers': Supplier.objects.filter(is_active=True).count(),
            'pending_suppliers': Supplier.objects.filter(is_active=False).count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'role_stats': context['role_counts'],
        })

    elif request.user.role == 'sale_manager':
        # Use a different variable name to avoid conflict with imported timedelta
        from datetime import timedelta as td
        today_dt = localdate()
        week_start = today_dt - td(days=today_dt.weekday())
        delivered = SaleOrder.objects.filter(status='delivered')
        weekly_sales = SaleOrder.objects.filter(order_date__gte=week_start)
        context.update({
            'completed_orders': delivered.count(),
            'cancelled_orders': SaleOrder.objects.filter(status='cancelled').count(),
            'weekly_sales_amount': weekly_sales.aggregate(total=Sum('total_amount'))['total'] or 0,
            'weekly_sales_count': weekly_sales.count(),
            'average_order_value': SaleOrder.objects.aggregate(avg=Avg('total_amount'))['avg'] or 0,
            'inventory_low_items': Product.objects.filter(quantity__lte=F('min_stock_level')).order_by('quantity')[:5],
            'pending_customer_orders': SaleOrder.objects.filter(status='pending').order_by('-order_date')[:5],
            'recent_orders': SaleOrder.objects.order_by('-order_date')[:5],
            'staff_performance': User.objects.filter(role='worker').annotate(
                orders_handled=Count('created_sales'),
                total_sales=Sum('created_sales__total_amount')
            ).order_by('-total_sales')[:5],
        })

    elif request.user.role == 'worker':
        from tasks.models import Task, Issue
        assigned_tasks = Task.objects.filter(assigned_to=request.user).order_by('-created_at')[:5]
        context.update({
            'total_tasks': Task.objects.filter(assigned_to=request.user).count(),
            'pending_tasks': Task.objects.filter(assigned_to=request.user, status='pending').count(),
            'in_progress_tasks': Task.objects.filter(assigned_to=request.user, status='in_progress').count(),
            'completed_tasks_count': Task.objects.filter(assigned_to=request.user, status='completed').count(),
            'overdue_tasks': Task.objects.filter(assigned_to=request.user, is_overdue=True).count(),
            'assigned_tasks': assigned_tasks,
            'pending_orders': SaleOrder.objects.filter(status__in=['pending', 'processing']).order_by('-order_date')[:5],
            'low_stock': Product.objects.filter(quantity__lte=F('min_stock_level')).order_by('quantity')[:5],
            'issues': Issue.objects.filter(
                assigned_to=request.user
            ).select_related('product').order_by('-created_at')[:5],
            'inventory_low_items': Product.objects.filter(quantity__lte=F('min_stock_level')).order_by('quantity')[:5],
        })

    elif request.user.role == 'supplier':
        supplier_profile = getattr(request.user, 'supplier_profile', None)
        if supplier_profile:
            products = Product.objects.filter(supplier=supplier_profile)
            orders = SaleOrder.objects.filter(order_items__product__supplier=supplier_profile).distinct()
            context.update({
                'my_products_count': products.count(),
                'total_orders_count': orders.count(),
                'pending_orders_count': orders.filter(status='pending').count(),
                'low_stock_count': products.filter(quantity__lte=F('min_stock_level')).count(),
                'supplier_products': products.order_by('-created_at')[:5],
                'supplier_orders': orders.order_by('-order_date')[:5],
                'recent_activity': recent_logs,
            })
        else:
            context.update({
                'my_products_count': 0,
                'total_orders_count': 0,
                'pending_orders_count': 0,
                'low_stock_count': 0,
                'supplier_products': Product.objects.none(),
                'supplier_orders': SaleOrder.objects.none(),
                'recent_activity': [],
            })

    return render(request, template_name, context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})

# ============================================
# ADMIN SPECIFIC VIEWS
# ============================================

@login_required
@admin_required
def admin_user_management(request):
    users = User.objects.all().order_by('-date_joined')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_user':
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save()
                UserActivityLog.objects.create(
                    user=request.user,
                    action='user_created',
                    details=f'Created user: {user.username} with role: {user.role}'
                )
                messages.success(request, f'User {user.username} created successfully.')
                return redirect('accounts:admin_user_management')
            else:
                messages.error(request, 'Please fix the errors below.')
        
        elif action == 'delete_user':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            if user == request.user:
                messages.error(request, 'You cannot delete your own account.')
            else:
                username = user.username
                user.delete()
                UserActivityLog.objects.create(
                    user=request.user,
                    action='user_deleted',
                    details=f'Deleted user: {username}'
                )
                messages.success(request, f'User {username} deleted successfully.')
            return redirect('accounts:admin_user_management')
        
        elif action == 'toggle_status':
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            if user == request.user:
                messages.error(request, 'You cannot change your own status.')
            else:
                user.is_active = not user.is_active
                user.save()
                status = 'activated' if user.is_active else 'deactivated'
                UserActivityLog.objects.create(
                    user=request.user,
                    action='user_status_toggled',
                    details=f'{user.username} {status}'
                )
                messages.success(request, f'User {user.username} {status}.')
            return redirect('accounts:admin_user_management')
        
        elif action == 'change_role':
            user_id = request.POST.get('user_id')
            new_role = request.POST.get('new_role')
            user = get_object_or_404(User, id=user_id)
            if user == request.user:
                messages.error(request, 'You cannot change your own role.')
            else:
                user.role = new_role
                user.save()
                UserActivityLog.objects.create(
                    user=request.user,
                    action='user_role_changed',
                    details=f'Changed {user.username} role to {new_role}'
                )
                messages.success(request, f'Role changed to {new_role} for {user.username}')
            return redirect('accounts:admin_user_management')
    
    form = UserRegistrationForm()
    return render(request, 'dashboard/admin_user_management.html', {
        'users': users,
        'form': form,
        'role_choices': User.ROLE_CHOICES,
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'staff_users': User.objects.filter(is_staff=True).count(),
        'admin_users': User.objects.filter(role='admin').count(),
    })

@login_required
@admin_required
def admin_user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully.')
            return redirect('accounts:admin_user_management')
    else:
        form = UserUpdateForm(instance=user)
    
    return render(request, 'accounts/admin_user_edit.html', {
        'form': form,
        'user': user
    })

@login_required
@admin_required
def admin_reports(request):
    from products.models import Product
    from sales.models import SaleOrder
    from suppliers.models import Supplier
    
    report_type = request.GET.get('type', 'sales')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    context = {
        'report_type': report_type,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    if report_type == 'sales':
        orders = SaleOrder.objects.all()
        if date_from:
            orders = orders.filter(order_date__gte=date_from)
        if date_to:
            orders = orders.filter(order_date__lte=date_to)
        
        context.update({
            'orders': orders,
            'total_orders': orders.count(),
            'total_revenue': orders.aggregate(total=Sum('total_amount'))['total'] or 0,
            'average_order_value': orders.aggregate(avg=Avg('total_amount'))['avg'] or 0,
            'pending_orders': orders.filter(status='pending').count(),
            'completed_orders': orders.filter(status='delivered').count(),
            'cancelled_orders': orders.filter(status='cancelled').count(),
        })
    
    elif report_type == 'inventory':
        products = Product.objects.all()
        context.update({
            'products': products,
            'total_products': products.count(),
            'total_value': products.aggregate(
                total=Sum(ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField(max_digits=14, decimal_places=2)))
            )['total'] or 0,
            'low_stock': products.filter(quantity__lte=F('min_stock_level')).count(),
            'out_of_stock': products.filter(quantity=0).count(),
        })
    
    elif report_type == 'users':
        users = User.objects.all()
        context.update({
            'users': users,
            'total_users': users.count(),
            'active_users': users.filter(is_active=True).count(),
            'inactive_users': users.filter(is_active=False).count(),
            'role_breakdown': users.values('role').annotate(count=Count('id')),
        })
    
    elif report_type == 'suppliers':
        suppliers = Supplier.objects.all()
        context.update({
            'suppliers': suppliers,
            'total_suppliers': suppliers.count(),
            'active_suppliers': suppliers.filter(is_active=True).count(),
            'pending_suppliers': suppliers.filter(is_active=False).count(),
        })
    
    return render(request, 'accounts/admin_reports.html', context)

@login_required
@admin_required
def admin_settings(request):
    if request.method == 'POST':
        settings_data = {
            'company_name': request.POST.get('company_name'),
            'company_address': request.POST.get('company_address'),
            'company_phone': request.POST.get('company_phone'),
            'company_email': request.POST.get('company_email'),
            'low_stock_threshold': request.POST.get('low_stock_threshold', 5),
            'tax_rate': request.POST.get('tax_rate', 0),
            'currency_symbol': request.POST.get('currency_symbol', 'PKR'),
        }
        
        for key, value in settings_data.items():
            SystemSetting.objects.update_or_create(
                key=key,
                defaults={'value': value or ''}
            )
        
        UserActivityLog.objects.create(
            user=request.user,
            action='settings_updated',
            details='System settings were updated'
        )
        
        messages.success(request, 'Settings updated successfully!')
        return redirect('accounts:admin_settings')
    
    settings = {setting.key: setting.value for setting in SystemSetting.objects.all()}
    
    return render(request, 'accounts/admin_settings.html', {
        'settings': settings,
        'role_choices': User.ROLE_CHOICES,
    })

@login_required
@admin_required
def admin_dashboard(request):
    from products.models import Product
    from sales.models import SaleOrder
    from suppliers.models import Supplier
    
    # Use a different variable name to avoid conflict with imported timedelta
    from datetime import timedelta as td
    today = localdate()
    start_of_week = today - td(days=today.weekday())
    start_of_month = today.replace(day=1)
    
    total_revenue = SaleOrder.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    from sales.models import OrderItem
    cogs = OrderItem.objects.aggregate(
        total=Sum(ExpressionWrapper(F('product__cost_price') * F('quantity'), output_field=DecimalField(max_digits=14, decimal_places=2)))
    )['total'] or 0
    profit = total_revenue - cogs
    
    today_sales = SaleOrder.objects.filter(order_date__date=today)
    week_sales = SaleOrder.objects.filter(order_date__gte=start_of_week)
    month_sales = SaleOrder.objects.filter(order_date__gte=start_of_month)
    
    total_products = Product.objects.count()
    low_stock_items = Product.objects.filter(quantity__lte=F('min_stock_level'))
    out_of_stock = Product.objects.filter(quantity=0)
    
    context = {
        'total_revenue': total_revenue,
        'profit': profit,
        'profit_margin': (profit / total_revenue * 100) if total_revenue > 0 else 0,
        'today_sales_count': today_sales.count(),
        'today_sales_amount': today_sales.aggregate(total=Sum('total_amount'))['total'] or 0,
        'week_sales_count': week_sales.count(),
        'week_sales_amount': week_sales.aggregate(total=Sum('total_amount'))['total'] or 0,
        'month_sales_count': month_sales.count(),
        'month_sales_amount': month_sales.aggregate(total=Sum('total_amount'))['total'] or 0,
        'total_products': total_products,
        'low_stock_count': low_stock_items.count(),
        'out_of_stock_count': out_of_stock.count(),
        'total_inventory_value': Product.objects.aggregate(
            total=Sum(ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField(max_digits=14, decimal_places=2)))
        )['total'] or 0,
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'total_staff': User.objects.filter(is_staff=True).count(),
        'total_suppliers': Supplier.objects.count(),
        'active_suppliers': Supplier.objects.filter(is_active=True).count(),
        'pending_suppliers': Supplier.objects.filter(is_active=False).count(),
        'pending_orders': SaleOrder.objects.filter(status='pending').count(),
        'processing_orders': SaleOrder.objects.filter(status='processing').count(),
        'shipped_orders': SaleOrder.objects.filter(status='shipped').count(),
        'completed_orders': SaleOrder.objects.filter(status='delivered').count(),
        'recent_orders': SaleOrder.objects.select_related('created_by').order_by('-order_date')[:10],
        'recent_products': Product.objects.select_related('category', 'supplier').order_by('-created_at')[:10],
        'recent_activity': UserActivityLog.objects.select_related('user').order_by('-timestamp')[:15],
        'low_stock_products': low_stock_items[:10],
        'role_stats': User.objects.values('role').annotate(count=Count('id')),
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)