# sales/forms.py
from django import forms
from .models import SaleOrder

class SaleOrderForm(forms.ModelForm):
    class Meta:
        model = SaleOrder
        fields = ('customer_name', 'customer_email', 'customer_phone', 'customer_address', 'notes')
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }