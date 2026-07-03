# suppliers/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from .models import Supplier, PurchaseOrder
from .forms import SupplierForm, PurchaseOrderForm, SupplierProductForm
from products.models import Product
from sales.models import SaleOrder
from accounts.models import UserActivityLog
from accounts.decorators import admin_required, manager_required, supplier_required

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('name')
    
    search_query = request.GET.get('search', '')
    if search_query:
        suppliers = suppliers.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(city__icontains=search_query)
        )
    
    paginator = Paginator(suppliers, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'suppliers': page_obj,
        'search_query': search_query,
        'total_suppliers': paginator.count,
        'active_suppliers': Supplier.objects.filter(is_active=True).count(),
    }
    return render(request, 'suppliers/supplier_list.html', context)

@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, id=pk)
    products = Product.objects.filter(supplier=supplier)
    purchase_orders = PurchaseOrder.objects.filter(supplier=supplier).order_by('-order_date')[:20]
    
    context = {
        'supplier': supplier,
        'products': products,
        'purchase_orders': purchase_orders,
        'total_products': products.count(),
        'total_orders': purchase_orders.count(),
        'total_spent': purchase_orders.filter(status='delivered').aggregate(total=Sum('total_amount'))['total'] or 0,
    }
    return render(request, 'suppliers/supplier_detail.html', context)

@login_required
@admin_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            UserActivityLog.objects.create(
                user=request.user,
                action='supplier_created',
                details=f'Created supplier: {supplier.name}'
            )
            messages.success(request, f'Supplier "{supplier.name}" created successfully!')
            return redirect('suppliers:supplier_list')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = SupplierForm()
    
    return render(request, 'suppliers/supplier_form.html', {'form': form, 'title': 'Add Supplier'})

@login_required
@admin_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, id=pk)
    
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            UserActivityLog.objects.create(
                user=request.user,
                action='supplier_updated',
                details=f'Updated supplier: {supplier.name}'
            )
            messages.success(request, f'Supplier "{supplier.name}" updated successfully!')
            return redirect('suppliers:supplier_list')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = SupplierForm(instance=supplier)
    
    return render(request, 'suppliers/supplier_form.html', {
        'form': form,
        'supplier': supplier,
        'title': 'Update Supplier'
    })

@login_required
@admin_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, id=pk)
    
    if request.method == 'POST':
        name = supplier.name
        supplier.delete()
        UserActivityLog.objects.create(
            user=request.user,
            action='supplier_deleted',
            details=f'Deleted supplier: {name}'
        )
        messages.success(request, f'Supplier "{name}" deleted successfully!')
        return redirect('suppliers:supplier_list')
    
    return render(request, 'suppliers/supplier_confirm_delete.html', {'supplier': supplier})

@login_required
@manager_required
def purchase_order_create(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            purchase_order = form.save(commit=False)
            purchase_order.requested_by = request.user
            purchase_order.save()
            
            if purchase_order.status == 'delivered':
                product = purchase_order.product
                product.quantity += purchase_order.quantity
                product.save()
            
            UserActivityLog.objects.create(
                user=request.user,
                action='purchase_order_created',
                details=f'Created purchase order for {purchase_order.product.name} from {purchase_order.supplier.name}'
            )
            
            messages.success(request, f'Purchase order created successfully!')
            return redirect('suppliers:purchase_order_list')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = PurchaseOrderForm()
    
    return render(request, 'suppliers/purchase_order_form.html', {
        'form': form,
        'title': 'Create Purchase Order'
    })

@login_required
def purchase_order_list(request):
    purchase_orders = PurchaseOrder.objects.select_related('supplier', 'product', 'requested_by').all().order_by('-order_date')
    
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        purchase_orders = purchase_orders.filter(status=status_filter)
    
    context = {
        'purchase_orders': purchase_orders,
        'status_filter': status_filter,
        'status_choices': PurchaseOrder.STATUS_CHOICES,
        'total_orders': purchase_orders.count(),
        'pending_count': purchase_orders.filter(status='pending').count(),
        'delivered_count': purchase_orders.filter(status='delivered').count(),
    }
    return render(request, 'suppliers/purchase_order_list.html', context)

@login_required
@manager_required
def purchase_order_update(request, pk):
    purchase_order = get_object_or_404(PurchaseOrder, id=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(PurchaseOrder.STATUS_CHOICES):
            purchase_order.status = status
            if status == 'delivered':
                purchase_order.delivery_date = timezone.now()
                product = purchase_order.product
                product.quantity += purchase_order.quantity
                product.save()
            purchase_order.save()
            
            UserActivityLog.objects.create(
                user=request.user,
                action='purchase_order_updated',
                details=f'Updated purchase order #{purchase_order.id} status to {status}'
            )
            
            messages.success(request, f'Purchase order status updated to {status}!')
        return redirect('suppliers:purchase_order_list')
    
    return render(request, 'suppliers/purchase_order_update.html', {
        'purchase_order': purchase_order,
        'status_choices': PurchaseOrder.STATUS_CHOICES
    })

@login_required
@supplier_required
def supplier_my_products(request):
    supplier_profile = getattr(request.user, 'supplier_profile', None)
    if not supplier_profile:
        messages.error(request, 'No supplier profile found.')
        return redirect('accounts:dashboard')
    products = Product.objects.filter(supplier=supplier_profile).order_by('-created_at')
    return render(request, 'suppliers/supplier_my_products.html', {
        'products': products,
        'supplier': supplier_profile,
    })

@login_required
@supplier_required
def supplier_product_create(request):
    supplier_profile = getattr(request.user, 'supplier_profile', None)
    if not supplier_profile:
        messages.error(request, 'No supplier profile found.')
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = SupplierProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.supplier = supplier_profile
            product.save()
            UserActivityLog.objects.create(
                user=request.user,
                action='product_created',
                details=f'Supplier {request.user.username} created product: {product.name}'
            )
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('suppliers:supplier_my_products')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = SupplierProductForm()
    return render(request, 'suppliers/supplier_product_form.html', {
        'form': form,
        'title': 'Add Product',
    })

@login_required
@supplier_required
def supplier_product_update(request, pk):
    supplier_profile = getattr(request.user, 'supplier_profile', None)
    if not supplier_profile:
        messages.error(request, 'No supplier profile found.')
        return redirect('accounts:dashboard')
    product = get_object_or_404(Product, id=pk, supplier=supplier_profile)
    if request.method == 'POST':
        form = SupplierProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            UserActivityLog.objects.create(
                user=request.user,
                action='product_updated',
                details=f'Supplier {request.user.username} updated product: {product.name}'
            )
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('suppliers:supplier_my_products')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = SupplierProductForm(instance=product)
    return render(request, 'suppliers/supplier_product_form.html', {
        'form': form,
        'product': product,
        'title': 'Update Product',
    })

@login_required
@supplier_required
def supplier_product_delete(request, pk):
    supplier_profile = getattr(request.user, 'supplier_profile', None)
    if not supplier_profile:
        messages.error(request, 'No supplier profile found.')
        return redirect('accounts:dashboard')
    product = get_object_or_404(Product, id=pk, supplier=supplier_profile)
    if request.method == 'POST':
        name = product.name
        product.delete()
        UserActivityLog.objects.create(
            user=request.user,
            action='product_deleted',
            details=f'Supplier {request.user.username} deleted product: {name}'
        )
        messages.success(request, f'Product "{name}" deleted successfully!')
        return redirect('suppliers:supplier_my_products')
    return render(request, 'suppliers/supplier_product_confirm_delete.html', {'product': product})

@login_required
@supplier_required
def supplier_my_orders(request):
    supplier_profile = getattr(request.user, 'supplier_profile', None)
    if not supplier_profile:
        messages.error(request, 'No supplier profile found.')
        return redirect('accounts:dashboard')
    orders = SaleOrder.objects.filter(order_items__product__supplier=supplier_profile).distinct().order_by('-order_date')
    return render(request, 'suppliers/supplier_my_orders.html', {
        'orders': orders,
        'supplier': supplier_profile,
    })

@login_required
@supplier_required
def supplier_order_detail(request, order_id):
    supplier_profile = getattr(request.user, 'supplier_profile', None)
    if not supplier_profile:
        messages.error(request, 'No supplier profile found.')
        return redirect('accounts:dashboard')
    order = get_object_or_404(SaleOrder, id=order_id)
    items = order.order_items.filter(product__supplier=supplier_profile)
    if not items.exists():
        messages.error(request, 'Order not found or does not contain your products.')
        return redirect('suppliers:supplier_my_orders')
    return render(request, 'suppliers/supplier_order_detail.html', {
        'order': order,
        'items': items,
    })