from django.contrib import admin
from .models import FixedDeposit


@admin.register(FixedDeposit)
class FixedDepositAdmin(admin.ModelAdmin):
    """Admin interface for Fixed Deposit model"""
    
    list_display = [
        'name',
        'institution',
        'principal_amount',
        'interest_rate',
        'maturity_amount',
        'maturity_date',
        'status',
        'user',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'compounding_frequency',
        'institution',
        'maturity_date',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'institution',
        'fd_number',
        'user__username',
        'user__email'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'institution', 'fd_number')
        }),
        ('Financial Details', {
            'fields': (
                'principal_amount',
                'interest_rate',
                'maturity_amount',
                'compounding_frequency'
            )
        }),
        ('FD Terms', {
            'fields': (
                'tenure_months',
                'opened_on',
                'maturity_date',
                'auto_renewal'
            )
        }),
        ('Status & Customization', {
            'fields': ('status', 'color', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-maturity_date', '-created_at']
    
    date_hierarchy = 'maturity_date'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user')
