from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('signup/success/', views.SignupSuccessView.as_view(), name='signup_success'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('settings/password-change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('settings/account-delete/', views.AccountDeleteView.as_view(), name='account_delete'),
    path('settings/recalculate-balances/', views.RecalculateBalancesView.as_view(), name='recalculate_balances'),
]
