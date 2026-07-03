# sales/urls.py
from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sale_list, name='sale_list'),
    path('create/', views.sale_create, name='sale_create'),
    path('manager/orders/', views.manager_orders, name='manager_orders'),
    path('manager/order/<int:order_id>/', views.manager_order_detail, name='manager_order_detail'),
    path('manager/order/<int:order_id>/update/', views.manager_update_order, name='manager_update_order'),
]