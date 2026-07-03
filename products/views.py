# products/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F, Count
from django.core.paginator import Paginator
from .models import Product, Category
from .forms import ProductForm, CategoryForm
from accounts.models import UserActivityLog
from accounts.decorators import admin_required

@login_required
def product_list(request):
    products = Product.objects.select_related('category', 'supplier').all()
    
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(model__icontains=search_query) |
            Q(sku__icontains=search_query)
        )
    
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    status = request.GET.get('status')
    if status:
        products = products.filter(status=status)
    
    stock_filter = request.GET.get('stock')
    if stock_filter == 'low':
        products = products.filter(quantity__lte=F('min_stock_level'))
    elif stock_filter == 'out':
        products = products.filter(quantity=0)
    elif stock_filter == 'in':
        products = products.filter(quantity__gt=0)
    
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    total_products = Product.objects.count()
    out_of_stock_count = Product.objects.filter(quantity=0).count()
    low_stock_count = Product.objects.filter(quantity__lte=F('min_stock_level')).count()
    in_stock_count = total_products - out_of_stock_count
    
    context = {
        'products': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_status': status,
        'selected_stock': stock_filter,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'in_stock_count': in_stock_count,
    }
    
    return render(request, 'products/product_list.html', context)

@login_required
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:5]
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products
    })

@login_required
@admin_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            UserActivityLog.objects.create(
                user=request.user,
                action='product_created',
                details=f'Created product: {product.name}'
            )
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('products:product_detail', slug=product.slug)
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ProductForm()
    
    return render(request, 'products/product_form.html', {
        'form': form,
        'title': 'Add New Product'
    })

@login_required
@admin_required
def product_update(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            UserActivityLog.objects.create(
                user=request.user,
                action='product_updated',
                details=f'Updated product: {product.name}'
            )
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('products:product_detail', slug=product.slug)
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/product_form.html', {
        'form': form,
        'product': product,
        'title': 'Update Product'
    })

@login_required
@admin_required
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        name = product.name
        product.delete()
        UserActivityLog.objects.create(
            user=request.user,
            action='product_deleted',
            details=f'Deleted product: {name}'
        )
        messages.success(request, f'Product "{name}" deleted successfully!')
        return redirect('products:product_list')
    
    return render(request, 'products/product_confirm_delete.html', {'product': product})

@login_required
def category_list(request):
    categories = Category.objects.annotate(
        product_count=Count('products')
    ).all().order_by('name')
    paginator = Paginator(categories, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'products/category_list.html', {'categories': page_obj})

@login_required
@admin_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('products:category_list')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = CategoryForm()
    
    return render(request, 'products/category_form.html', {'form': form, 'title': 'Add Category'})

@login_required
@admin_required
def category_update(request, slug):
    category = get_object_or_404(Category, slug=slug)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('products:category_list')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'products/category_form.html', {
        'form': form,
        'category': category,
        'title': 'Update Category'
    })

@login_required
@admin_required
def category_delete(request, slug):
    category = get_object_or_404(Category, slug=slug)
    
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted successfully!')
        return redirect('products:category_list')
    
    return render(request, 'products/category_confirm_delete.html', {'category': category})