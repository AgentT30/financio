from django.urls import path
from . import views

app_name = 'investments'

urlpatterns = [
    # Dashboard/Overview
    path('', views.investment_list, name='investment_list'),
    
    # Broker Management
    path('brokers/', views.broker_list, name='broker_list'),
    path('brokers/add/', views.broker_create, name='broker_create'),
    path('brokers/<int:pk>/edit/', views.broker_edit, name='broker_edit'),
    path('brokers/<int:pk>/archive/', views.broker_archive, name='broker_archive'),
    path('brokers/<int:pk>/delete/', views.broker_delete, name='broker_delete'),
    
    # Investment Management
    path('add/', views.investment_create, name='investment_create'),
    path('<int:pk>/', views.investment_detail, name='investment_detail'),
    path('<int:pk>/edit/', views.investment_edit, name='investment_edit'),
    path('<int:pk>/delete/', views.investment_delete, name='investment_delete'),
    
    # Transaction Management
    path('<int:investment_id>/transaction/add/', views.transaction_create, name='transaction_create'),
    path('transaction/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('transaction/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
]
