# tasks/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    TASK_TYPE_CHOICES = [
        ('assembly', 'Bike Assembly'),
        ('servicing', 'Servicing'),
        ('delivery', 'Delivery'),
        ('display', 'Display Setup'),
        ('stock_check', 'Stock Check'),
        ('cleaning', 'Cleaning'),
        ('repair', 'Repair'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default='other')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    is_overdue = models.BooleanField(default=False, db_index=True)
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.username}"
    
    def save(self, *args, **kwargs):
        if self.due_date and self.due_date < timezone.now() and self.status != 'completed':
            self.is_overdue = True
        else:
            self.is_overdue = False
        
        if self.status == 'in_progress' and not self.started_at:
            self.started_at = timezone.now()
        
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']

class Issue(models.Model):
    ISSUE_TYPE_CHOICES = [
        ('damaged', 'Damaged Product'),
        ('missing', 'Missing Item'),
        ('defective', 'Defective'),
        ('stock_error', 'Stock Discrepancy'),
        ('other', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]
    
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='issues')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_issues')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues')
    
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPE_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    description = models.TextField()
    resolution = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.issue_type} - {self.product.name}"
    
    class Meta:
        ordering = ['-created_at']