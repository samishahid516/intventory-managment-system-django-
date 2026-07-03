# inventory_system/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Redirect Django's default /accounts/login/ to our actual login page
    path('accounts/login/', RedirectView.as_view(url='/login/', permanent=False)),

    # Accounts app first - so /admin/users/, /admin/reports/, /admin/settings/ etc.
    # are caught by custom views BEFORE Django's built-in admin
    path('', include('accounts.urls')),
    
    # Django Admin (catch-all for remaining /admin/ URLs)
    path('admin/', admin.site.urls),
    
    # Other apps
    path('products/', include('products.urls')),
    path('sales/', include('sales.urls')),
    path('suppliers/', include('suppliers.urls')),
    path('tasks/', include('tasks.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)