# suppliers/urls.py
from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_list, name='supplier_list'),
    path('<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('create/', views.supplier_create, name='supplier_create'),
    path('<int:pk>/edit/', views.supplier_update, name='supplier_update'),
    path('<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),

    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/create/', views.purchase_order_create, name='purchase_order_create'),
    path('purchase-orders/<int:pk>/update/', views.purchase_order_update, name='purchase_order_update'),

    # Supplier self-service
    path('my-products/', views.supplier_my_products, name='supplier_my_products'),
    path('my-products/create/', views.supplier_product_create, name='supplier_product_create'),
    path('my-products/<int:pk>/edit/', views.supplier_product_update, name='supplier_product_update'),
    path('my-products/<int:pk>/delete/', views.supplier_product_delete, name='supplier_product_delete'),
    path('my-orders/', views.supplier_my_orders, name='supplier_my_orders'),
    path('my-orders/<int:order_id>/', views.supplier_order_detail, name='supplier_order_detail'),
]
