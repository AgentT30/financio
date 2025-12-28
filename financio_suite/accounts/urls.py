from django.urls import path
from . import views

urlpatterns = [
    path('', views.account_list, name='account_list'),
    path('create/', views.account_create, name='account_create'),
    path('<int:pk>/', views.account_detail, name='account_detail'),
    path('<int:pk>/edit/', views.account_edit, name='account_edit'),
    path('<int:pk>/delete/', views.account_delete, name='account_delete'),
    path('<int:pk>/toggle-status/', views.account_toggle_status, name='account_toggle_status'),
    
    # Debit Cards
    path('debit-cards/', views.debit_card_list, name='debit_card_list'),
    path('debit-cards/create/', views.debit_card_create, name='debit_card_create'),
    path('debit-cards/<int:pk>/edit/', views.debit_card_edit, name='debit_card_edit'),
    path('debit-cards/<int:pk>/delete/', views.debit_card_delete, name='debit_card_delete'),
]
