# tasks/admin.py
from django.contrib import admin
from .models import Task, Issue

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task_type', 'priority', 'status', 'assigned_to', 'due_date', 'is_overdue']
    list_filter = ['status', 'priority', 'task_type']
    search_fields = ['title', 'description', 'assigned_to__username']

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['product', 'issue_type', 'severity', 'status', 'reported_by', 'created_at']
    list_filter = ['status', 'severity', 'issue_type']
    search_fields = ['product__name', 'description']