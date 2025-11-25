from django.contrib import admin
from .models import BankAccount, BankAccountBalance


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    """Admin interface for BankAccount model"""

    list_display = [
        'name',
        'account_type',
        'institution',
        'user',
        'get_masked_number',
        'get_balance',
        'color_preview',
        'status',
        'created_at'
    ]
    list_filter = ['account_type', 'status', 'institution', 'created_at']
    search_fields = ['name', 'user__username', 'user__email', 'institution', 'customer_id']
    readonly_fields = ['account_number_last4', 'created_at', 'updated_at', 'get_current_balance']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'account_type', 'status')
        }),
        ('Institution Details', {
            'fields': ('institution', 'branch_name', 'ifsc_code', 'customer_id')
        }),
        ('Account Identifiers', {
            'fields': ('account_number', 'account_number_last4'),
            'description': 'Account number is encrypted. Last 4 digits auto-extracted on save.'
        }),
        ('Financial Information', {
            'fields': ('opening_balance', 'currency', 'opened_on', 'get_current_balance')
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
        """Display masked account number"""
        return obj.get_masked_account_number()
    get_masked_number.short_description = 'Account Number'

    def get_balance(self, obj):
        """Display current balance"""
        return f"{obj.get_current_balance():,.2f} {obj.currency}"
    get_balance.short_description = 'Current Balance'

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


@admin.register(BankAccountBalance)
class BankAccountBalanceAdmin(admin.ModelAdmin):
    """Admin interface for BankAccountBalance model"""

    list_display = ['account', 'balance_amount', 'last_posting_id', 'updated_at']
    readonly_fields = ['account', 'balance_amount', 'last_posting_id', 'updated_at']
    search_fields = ['account__name', 'account__user__username']

    def has_add_permission(self, request):
        """Prevent manual addition"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent manual deletion"""
        return False

