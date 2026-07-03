# tasks/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, F
from django.utils import timezone
from .models import Task, Issue
from .forms import TaskForm, IssueForm
from products.models import Product
from sales.models import SaleOrder
from accounts.models import UserActivityLog
from accounts.decorators import manager_required


@login_required
def worker_dashboard(request):
    # Get assigned tasks
    assigned_tasks = Task.objects.filter(
        assigned_to=request.user,
        status__in=['pending', 'in_progress']
    ).order_by('priority', '-created_at')
    
    # Get completed tasks
    completed_tasks = Task.objects.filter(
        assigned_to=request.user,
        status='completed'
    ).order_by('-completed_at')[:5]
    
    # Get pending orders
    pending_orders_list = SaleOrder.objects.filter(
        status__in=['pending', 'processing']
    ).order_by('-order_date')[:5]
    
    # Get low stock products
    low_stock = Product.objects.filter(
        quantity__lte=F('min_stock_level')
    ).order_by('quantity')[:5]
    
    # Get issues
    issues = Issue.objects.filter(
        reported_by=request.user,
        status__in=['pending', 'in_progress']
    ).order_by('-created_at')[:5]
    
    # Count statistics
    total_tasks = Task.objects.filter(assigned_to=request.user).count()
    pending_tasks = Task.objects.filter(assigned_to=request.user, status='pending').count()
    in_progress_tasks = Task.objects.filter(assigned_to=request.user, status='in_progress').count()
    completed_tasks_count = Task.objects.filter(assigned_to=request.user, status='completed').count()
    overdue_tasks = Task.objects.filter(
        assigned_to=request.user, 
        is_overdue=True, 
        status__in=['pending', 'in_progress']
    ).count()
    
    context = {
        'assigned_tasks': assigned_tasks,
        'completed_tasks': completed_tasks,
        'pending_orders': pending_orders_list,
        'low_stock': low_stock,
        'issues': issues,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks_count': completed_tasks_count,
        'overdue_tasks': overdue_tasks,
        'recent_products': Product.objects.order_by('-updated_at')[:5],
    }
    
    return render(request, 'dashboard/worker_dashboard.html', context)


@login_required
@manager_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            
            UserActivityLog.objects.create(
                user=request.user,
                action='task_created',
                details=f'Created task: {task.title} for {task.assigned_to.username}'
            )
            
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('tasks:task_list')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = TaskForm()
    
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Create Task'})


@login_required
def task_list(request):
    if request.user.role in ['admin', 'sale_manager']:
        tasks = Task.objects.all().order_by('-created_at')
    else:
        tasks = Task.objects.filter(assigned_to=request.user).order_by('-created_at')
    
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        tasks = tasks.filter(status=status_filter)
    
    context = {
        'tasks': tasks,
        'status_filter': status_filter,
        'status_choices': Task.STATUS_CHOICES,
        'total_tasks': tasks.count(),
        'pending_count': tasks.filter(status='pending').count(),
        'in_progress_count': tasks.filter(status='in_progress').count(),
        'completed_count': tasks.filter(status='completed').count(),
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, id=pk)
    
    if request.user.role not in ['admin', 'sale_manager'] and task.assigned_to != request.user:
        messages.error(request, 'You are not authorized to update this task.')
        return redirect('tasks:task_list')
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Task.STATUS_CHOICES):
            task.status = status
            task.save()
            
            UserActivityLog.objects.create(
                user=request.user,
                action='task_updated',
                details=f'Updated task: {task.title} to {status}'
            )
            
            messages.success(request, f'Task status updated to {status}!')
        return redirect('tasks:task_list')
    
    return render(request, 'tasks/task_update.html', {
        'task': task,
        'status_choices': Task.STATUS_CHOICES
    })


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, id=pk)
    return render(request, 'tasks/task_detail.html', {'task': task})


@login_required
def issue_create(request):
    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.reported_by = request.user
            issue.save()
            
            UserActivityLog.objects.create(
                user=request.user,
                action='issue_reported',
                details=f'Reported issue: {issue.issue_type} for {issue.product.name}'
            )
            
            messages.success(request, 'Issue reported successfully!')
            return redirect('tasks:issue_list')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = IssueForm()
    
    return render(request, 'tasks/issue_form.html', {'form': form, 'title': 'Report Issue'})


@login_required
def issue_list(request):
    if request.user.role in ['admin', 'sale_manager']:
        issues = Issue.objects.all().order_by('-created_at')
    else:
        issues = Issue.objects.filter(
            Q(reported_by=request.user) | Q(assigned_to=request.user)
        ).order_by('-created_at')
    
    context = {
        'issues': issues,
        'total_issues': issues.count(),
        'pending_issues': issues.filter(status='pending').count(),
        'resolved_issues': issues.filter(status='resolved').count(),
    }
    return render(request, 'tasks/issue_list.html', context)