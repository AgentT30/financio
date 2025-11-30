from django.urls import path
from . import views

app_name = 'fds'

urlpatterns = [
    path('', views.fd_list, name='fd_list'),
    path('create/', views.fd_create, name='fd_create'),
    path('<int:pk>/', views.fd_detail, name='fd_detail'),
    path('<int:pk>/edit/', views.fd_edit, name='fd_edit'),
    path('<int:pk>/delete/', views.fd_delete, name='fd_delete'),
    path('<int:pk>/mark-matured/', views.fd_mark_matured, name='fd_mark_matured'),
]
