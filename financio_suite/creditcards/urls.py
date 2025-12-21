from django.urls import path
from . import views

urlpatterns = [
    path('', views.creditcard_list, name='creditcard_list'),
    path('create/', views.creditcard_create, name='creditcard_create'),
    path('<int:pk>/', views.creditcard_detail, name='creditcard_detail'),
    path('<int:pk>/edit/', views.creditcard_edit, name='creditcard_edit'),
    path('<int:pk>/delete/', views.creditcard_delete, name='creditcard_delete'),
    path('<int:pk>/toggle-status/', views.creditcard_toggle_status, name='creditcard_toggle_status'),
]
