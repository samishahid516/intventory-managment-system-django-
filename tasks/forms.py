# tasks/forms.py
from django import forms
from .models import Task, Issue
from accounts.models import User

class TaskForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(role='worker', is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'task_type', 'priority', 'assigned_to', 'due_date', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'task_type': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['product', 'issue_type', 'severity', 'description']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'issue_type': forms.Select(attrs={'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }