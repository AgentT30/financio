from django.urls import path
from . import views

app_name = 'transfers'

urlpatterns = [
    path('', views.transfer_list, name='transfer_list'),
    path('create/', views.transfer_create, name='transfer_create'),
    path('<int:pk>/delete/', views.transfer_delete, name='transfer_delete'),
]
