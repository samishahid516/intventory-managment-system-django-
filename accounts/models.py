# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('sale_manager', 'Sales Manager'),
        ('worker', 'Worker'),
        ('supplier', 'Supplier'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='worker', db_index=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        db_table = 'accounts_user'

class UserActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=100, db_index=True)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']
        db_table = 'accounts_user_activity_log'

class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True)
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.key}: {self.value}"
    
    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"
        db_table = 'accounts_system_settings'