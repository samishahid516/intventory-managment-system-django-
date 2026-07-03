# products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    path('<slug:slug>/update/', views.product_update, name='product_update'),
    path('<slug:slug>/delete/', views.product_delete, name='product_delete'),
    
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<slug:slug>/update/', views.category_update, name='category_update'),
    path('categories/<slug:slug>/delete/', views.category_delete, name='category_delete'),
]