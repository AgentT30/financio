from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'datetime_ist', 'transaction_type', 'amount', 'category', 'account_info', 'is_deleted']
    list_filter = ['transaction_type', 'method_type', 'deleted_at', 'datetime_ist']
    search_fields = ['purpose', 'user__username', 'category__name']
    readonly_fields = ['user', 'datetime_ist', 'transaction_type', 'amount', 'account_content_type', 
                      'account_object_id', 'method_type', 'purpose', 'category', 'journal_entry', 
                      'created_at', 'updated_at', 'deleted_at']
    date_hierarchy = 'datetime_ist'
    
    def account_info(self, obj):
        return f"{obj.account}" if obj.account else f"CT#{obj.account_content_type_id}/ID#{obj.account_object_id}"
    account_info.short_description = 'Account'
    
    def is_deleted(self, obj):
        return obj.deleted_at is not None
    is_deleted.boolean = True
    is_deleted.short_description = 'Deleted'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
