# accounts/decorators.py
from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            if request.user.role not in allowed_roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def admin_required(view_func):
    return role_required(['admin'])(view_func)

def manager_required(view_func):
    return role_required(['admin', 'sale_manager'])(view_func)

def worker_required(view_func):
    return role_required(['admin', 'sale_manager', 'worker'])(view_func)

def supplier_required(view_func):
    return role_required(['admin', 'supplier'])(view_func)