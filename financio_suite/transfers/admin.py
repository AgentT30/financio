from django.contrib import admin
from .models import Transfer


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    """Admin interface for Transfer model."""
    
    list_display = [
        'id',
        'user',
        'datetime_ist',
        'amount',
        'from_account_display',
        'to_account_display',
        'method_type',
        'created_at',
        'is_deleted',
    ]
    
    list_filter = [
        'method_type',
        'datetime_ist',
        'created_at',
        'deleted_at',
    ]
    
    search_fields = [
        'memo',
        'user__username',
        'user__email',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'journal_entry',
    ]
    
    date_hierarchy = 'datetime_ist'
    
    fieldsets = (
        ('Transfer Information', {
            'fields': (
                'user',
                'datetime_ist',
                'amount',
                'method_type',
                'memo',
            )
        }),
        ('From Account', {
            'fields': (
                'from_account_content_type',
                'from_account_object_id',
            )
        }),
        ('To Account', {
            'fields': (
                'to_account_content_type',
                'to_account_object_id',
            )
        }),
        ('Ledger', {
            'fields': (
                'journal_entry',
            )
        }),
        ('Metadata', {
            'fields': (
                'deleted_at',
                'created_at',
                'updated_at',
            )
        }),
    )
    
    def from_account_display(self, obj):
        """Display from account name."""
        return str(obj.from_account) if obj.from_account else '-'
    from_account_display.short_description = 'From Account'
    
    def to_account_display(self, obj):
        """Display to account name."""
        return str(obj.to_account) if obj.to_account else '-'
    to_account_display.short_description = 'To Account'
    
    def is_deleted(self, obj):
        """Check if transfer is soft deleted."""
        return obj.is_deleted()
    is_deleted.boolean = True
    is_deleted.short_description = 'Deleted'

