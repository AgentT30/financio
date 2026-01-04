from datetime import date, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class FixedDeposit(models.Model):
    """
    Fixed Deposit model for tracking FD investments.
    
    FDs are informational records only - they do NOT integrate with 
    the transaction/ledger system. Users manually enter all details 
    including maturity amount.
    
    Key behaviors:
    - Standalone model (does NOT inherit from BaseAccount)
    - No transaction/transfer integration
    - Manual interest entry (maturity_amount field)
    - Status workflow: active → archived (via Mark as Matured)
    - Dashboard includes active FD maturity amounts in net worth
    """

    COMPOUNDING_FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]

    # Ownership
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='fixed_deposits',
        help_text="Owner of the FD"
    )

    # Basic Information
    name = models.CharField(
        max_length=100,
        help_text="FD display name/nickname"
    )
    institution = models.CharField(
        max_length=100,
        help_text="Bank name"
    )
    fd_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="FD account/certificate number"
    )

    # Financial Details
    principal_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Deposited amount"
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Annual interest rate (%)"
    )
    maturity_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        help_text="Final amount including interest (user-entered)"
    )

    # FD Terms
    compounding_frequency = models.CharField(
        max_length=20,
        choices=COMPOUNDING_FREQUENCY_CHOICES,
        default='quarterly',
        help_text="Interest compounding frequency"
    )
    tenure_days = models.IntegerField(
        help_text="Duration in days"
    )
    auto_renewal = models.BooleanField(
        default=False,
        help_text="Auto-renew on maturity"
    )

    # Important Dates
    opened_on = models.DateField(
        help_text="FD start date"
    )
    maturity_date = models.DateField(
        help_text="When FD matures"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True,
        help_text="FD status"
    )

    # Additional Information
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Optional notes"
    )
    color = models.CharField(
        max_length=7,
        null=True,
        blank=True,
        help_text="Color code for visual customization (hex format)"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Record creation time"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update time"
    )

    class Meta:
        db_table = 'fixed_deposits'
        verbose_name = 'Fixed Deposit'
        verbose_name_plural = 'Fixed Deposits'
        ordering = ['-maturity_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status'], name='idx_fd_user_status'),
            models.Index(fields=['maturity_date'], name='idx_fd_maturity_date'),
            models.Index(fields=['status'], name='idx_fd_status'),
        ]

    def __str__(self):
        return f"{self.name} ({self.institution})"

    def clean(self):
        """Validate FD data"""
        errors = {}

        # Validate principal amount
        if self.principal_amount is not None and self.principal_amount <= 0:
            errors['principal_amount'] = 'Principal amount must be greater than zero.'

        # Validate interest rate
        if self.interest_rate is not None:
            if self.interest_rate < 0 or self.interest_rate > 100:
                errors['interest_rate'] = 'Interest rate must be between 0 and 100%.'

        # Validate maturity amount
        if self.maturity_amount is not None and self.principal_amount is not None:
            if self.maturity_amount < self.principal_amount:
                errors['maturity_amount'] = 'Maturity amount cannot be less than principal amount.'

        # Validate tenure days
        if self.tenure_days is not None and self.tenure_days <= 0:
            errors['tenure_days'] = 'Tenure must be at least 1 day.'

        # Validate dates
        if self.opened_on and self.maturity_date:
            if self.maturity_date <= self.opened_on:
                errors['maturity_date'] = 'Maturity date must be after the opening date.'

        # Validate color format (if provided)
        if self.color:
            import re
            if not re.match(r'^#[0-9A-Fa-f]{6}$', self.color):
                errors['color'] = 'Color must be in hex format (e.g., #FF5733).'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Override save to run validation"""
        # Run validation
        self.full_clean()
        super().save(*args, **kwargs)

    def can_delete(self):
        """
        Check if the FD can be deleted.
        
        FDs have no dependencies (no transactions/transfers linked),
        so they can always be deleted.
        
        Returns:
            bool: Always True for FDs
        """
        return True

    def days_to_maturity(self):
        """
        Calculate days remaining until maturity.
        
        Returns:
            int: Positive number for future maturity, negative for past maturity
        """
        today = date.today()
        delta = self.maturity_date - today
        return delta.days

    def is_matured(self):
        """
        Check if the FD has matured.
        
        Returns:
            bool: True if maturity date has passed
        """
        return date.today() >= self.maturity_date

    def get_maturity_badge_info(self):
        """
        Get badge information for display in list view.
        
        Returns:
            dict: Contains 'text', 'color', and 'type' for badge display
        """
        if self.status == 'archived':
            # Archived FD: Show matured date
            return {
                'text': f"Matured on {self.maturity_date.strftime('%d/%m/%Y')}",
                'color': 'gray',
                'type': 'archived'
            }
        elif self.is_matured():
            # Active FD that has matured: Show days past maturity
            days_past = abs(self.days_to_maturity())
            days_text = 'day' if days_past == 1 else 'days'
            return {
                'text': f"Matured {days_past} {days_text} ago",
                'color': 'orange',
                'type': 'matured'
            }
        else:
            # Active FD with future maturity: Show days until maturity
            days_remaining = self.days_to_maturity()
            days_text = 'day' if days_remaining == 1 else 'days'
            return {
                'text': f"Matures in {days_remaining} {days_text}",
                'color': 'green',
                'type': 'active'
            }

    def get_tenure_display(self):
        """
        Get a friendly display of tenure in years, months, and days.
        
        Returns:
            str: Friendly format like "1 year 2 months", "45 days", etc.
        """
        days = self.tenure_days
        if days is None or days <= 0:
            return "0 days"
        
        years = days // 365
        remaining_days = days % 365
        months = remaining_days // 30
        final_days = remaining_days % 30
        
        parts = []
        
        if years > 0:
            parts.append(f"{years} year" if years == 1 else f"{years} years")
        
        if months > 0:
            parts.append(f"{months} month" if months == 1 else f"{months} months")
        
        if final_days > 0:
            parts.append(f"{final_days} day" if final_days == 1 else f"{final_days} days")
        
        # If no parts (shouldn't happen with days > 0), return days
        if not parts:
            return f"{days} days"
        
        return " ".join(parts)

    def get_interest_earned(self):
        """
        Calculate interest earned (simple calculation).
        
        Returns:
            Decimal: Interest amount (maturity_amount - principal_amount)
        """
        return self.maturity_amount - self.principal_amount
