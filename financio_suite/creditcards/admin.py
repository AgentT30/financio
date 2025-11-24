from django.contrib import admin
from .models import CreditCard, CreditCardBalance


@admin.register(CreditCard)
class CreditCardAdmin(admin.ModelAdmin):
    """Admin interface for CreditCard model"""
    
    list_display = [
        'name',
        'card_type',
        'institution',
        'user',
        'get_masked_number',
        'get_balance',
        'get_available_credit',
        'color_preview',
        'status',
        'expiry_date',
        'created_at'
    ]
    list_filter = ['card_type', 'status', 'institution', 'created_at']
    search_fields = ['name', 'user__username', 'user__email', 'institution', 'card_number_last4']
    readonly_fields = ['card_number_last4', 'created_at', 'updated_at', 'get_current_balance', 'available_credit', 'amount_owed']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'card_type', 'status')
        }),
        ('Institution Details', {
            'fields': ('institution',)
        }),
        ('Card Identifiers', {
            'fields': ('card_number', 'card_number_last4', 'cvv'),
            'description': 'Card number and CVV are encrypted. Last 4 digits auto-extracted on save.'
        }),
        ('Credit Limit & Billing', {
            'fields': ('credit_limit', 'billing_day', 'due_day', 'expiry_date')
        }),
        ('Financial Information', {
            'fields': ('opening_balance', 'currency', 'opened_on', 'get_current_balance', 'available_credit', 'amount_owed')
        }),
        ('Additional Information', {
            'fields': ('notes', 'picture', 'color'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_masked_number(self, obj):
        """Display masked card number"""
        return obj.get_masked_card_number()
    get_masked_number.short_description = 'Card Number'
    
    def get_balance(self, obj):
        """Display current balance"""
        balance = obj.get_current_balance()
        if balance < 0:
            return f"-₹{abs(balance):,.2f} (Owed)"
        elif balance > 0:
            return f"+₹{balance:,.2f} (Overpayment)"
        else:
            return "₹0.00"
    get_balance.short_description = 'Current Balance'
    
    def get_available_credit(self, obj):
        """Display available credit"""
        return f"₹{obj.available_credit():,.2f}"
    get_available_credit.short_description = 'Available Credit'
    
    def color_preview(self, obj):
        """Display color preview"""
        if obj.color:
            return f'<span style="display:inline-block;width:20px;height:20px;background-color:{obj.color};border:1px solid #ccc;border-radius:3px;"></span> {obj.color}'
        return '-'
    color_preview.short_description = 'Color'
    color_preview.allow_tags = True
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('user').prefetch_related('balance')


@admin.register(CreditCardBalance)
class CreditCardBalanceAdmin(admin.ModelAdmin):
    """Admin interface for CreditCardBalance model"""
    
    list_display = ['account', 'balance_amount', 'last_posting_id', 'updated_at']
    readonly_fields = ['account', 'balance_amount', 'last_posting_id', 'updated_at']
    search_fields = ['account__name', 'account__user__username']
    
    def has_add_permission(self, request):
        """Prevent manual addition"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent manual deletion"""
        return False
