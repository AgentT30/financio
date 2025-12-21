import secrets
import string
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.views import LoginView as DjangoLoginView, PasswordChangeView as DjangoPasswordChangeView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from .forms import SignupForm, RecoveryPasswordResetForm
from .models import UserRecovery
from ledger.services import LedgerService


class LoginView(DjangoLoginView):
    """Custom login view with styled template."""
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Redirect to dashboard after successful login."""
        return reverse_lazy('dashboard')
    
    def form_invalid(self, form):
        """Add error message on invalid login."""
        messages.error(self.request, 'Invalid username/email or password.')
        return super().form_invalid(form)


class SignupView(FormView):
    """User registration view."""
    template_name = 'auth/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect authenticated users to dashboard."""
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Save the user, log them in, and generate recovery token."""
        user = form.save()
        
        # Generate recovery token
        alphabet = string.ascii_letters + string.digits
        recovery_token = ''.join(secrets.choice(alphabet) for i in range(16))
        
        # Store hashed token in database
        UserRecovery.objects.create(
            user=user,
            token_hash=make_password(recovery_token)
        )
        
        # Store plain token in session to show it once
        self.request.session['recovery_token'] = recovery_token
        
        login(self.request, user)
        messages.success(self.request, 'Account created successfully!')
        return redirect('signup_success')


class SignupSuccessView(TemplateView):
    """View to show the recovery token after signup."""
    template_name = 'auth/signup_success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get token from session
        context['recovery_token'] = self.request.session.get('recovery_token')
        return context
    
    def form_invalid(self, form):
        """Add error messages for form validation errors."""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)


class PasswordResetRequestView(FormView):
    """View for resetting password using a recovery token."""
    template_name = 'auth/password_reset.html'
    form_class = RecoveryPasswordResetForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        """Update the user password."""
        form.save()
        messages.success(self.request, 'Password reset successfully! You can now log in with your new password.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Add error messages for form validation errors."""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        # Also add non-field errors
        for error in form.non_field_errors():
            messages.error(self.request, error)
        return super().form_invalid(form)




class LogoutView(View):
    """Simple logout view."""
    
    def get(self, request):
        """Log out the user and redirect to login."""
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('login')
    
    def post(self, request):
        """Handle POST logout (more secure)."""
        return self.get(request)


class SettingsView(View):
    """View for user settings and preferences."""
    template_name = 'auth/settings.html'
    
    def get(self, request):
        """Render the settings template."""
        return render(request, self.template_name)


class PasswordChangeView(DjangoPasswordChangeView):
    """View for changing user password."""
    template_name = 'auth/password_change.html'
    success_url = reverse_lazy('settings')
    
    def form_valid(self, form):
        """Add success message on successful password change."""
        messages.success(self.request, 'Your password was successfully updated!')
        return super().form_valid(form)


class AccountDeleteView(View):
    """View for deleting user account."""
    
    def post(self, request):
        """Delete the user account and log out."""
        confirmation_text = request.POST.get('confirmation_text')
        expected_text = "Yes I want to delete my account"
        
        if confirmation_text != expected_text:
            messages.error(request, 'Account deletion failed. Confirmation phrase did not match.')
            return redirect('settings')
            
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been permanently deleted.')
        return redirect('login')


class RecalculateBalancesView(View):
    """View to trigger balance recalculation for the current user."""
    
    def post(self, request):
        """Run the recalculation service and redirect back to settings."""
        if not request.user.is_authenticated:
            return redirect('login')
            
        cleanup_orphans = request.POST.get('cleanup_orphans') == 'on'
        
        try:
            results = LedgerService.recalculate_user_balances(
                user=request.user,
                cleanup_orphans=cleanup_orphans
            )
            
            total_fixed = results['banks_fixed'] + results['cards_fixed']
            if total_fixed > 0:
                messages.success(request, f'Successfully recalculated balances. Fixed {total_fixed} accounts.')
                for detail in results['details']:
                    messages.info(request, detail)
            else:
                messages.success(request, 'Balances are already correct. No changes were needed.')
                
            if results['orphans_deleted'] > 0:
                messages.info(request, f'Deleted {results["orphans_deleted"]} orphaned journal entries.')
                
        except Exception as e:
            messages.error(request, f'An error occurred during recalculation: {str(e)}')
            
        return redirect('settings')
