from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

from .forms import SignupForm, PasswordResetRequestForm


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
        """Save the user and log them in."""
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Account created successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Add error messages for form validation errors."""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)


class PasswordResetRequestView(FormView):
    """View for requesting password reset."""
    template_name = 'auth/password_reset.html'
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        """Send password reset email."""
        email = form.cleaned_data['email']
        user = User.objects.get(email=email)
        
        # Generate token and uid
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Build reset URL (we'll implement the confirm view later)
        reset_url = self.request.build_absolute_uri(
            reverse_lazy('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )
        
        # Send email (in production, use proper email backend)
        # For now, we'll just print to console
        subject = 'Password Reset - Financio'
        message = f'''
Hi {user.username},

You requested a password reset. Click the link below to reset your password:

{reset_url}

If you didn't request this, please ignore this email.

Thanks,
Financio Team
'''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            # In development, just print to console
            print(f"\n{'='*80}")
            print(f"PASSWORD RESET EMAIL")
            print(f"{'='*80}")
            print(f"To: {email}")
            print(f"Subject: {subject}")
            print(f"\n{message}")
            print(f"{'='*80}\n")
        
        messages.success(self.request, 'Password reset instructions sent to your email.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Add error messages for form validation errors."""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)


class PasswordResetDoneView(View):
    """View shown after password reset request."""
    template_name = 'auth/password_reset_done.html'
    
    def get(self, request):
        """Render the password reset done template."""
        return render(request, self.template_name)


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
