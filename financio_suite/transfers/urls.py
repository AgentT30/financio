from django.urls import path
from . import views

app_name = 'transfers'

urlpatterns = [
    path('', views.transfer_list, name='transfer_list'),
    path('export/csv/', views.transfer_export_csv, name='transfer_export_csv'),
    path('create/', views.transfer_create, name='transfer_create'),
    path('<int:pk>/edit/', views.transfer_edit, name='transfer_edit'),
    path('<int:pk>/delete/', views.transfer_delete, name='transfer_delete'),
]
