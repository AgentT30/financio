from django.contrib import admin
from .models import ControlAccount, JournalEntry, Posting


@admin.register(ControlAccount)
class ControlAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_type', 'description']
    readonly_fields = ['name', 'account_type', 'description']

    def has_add_permission(self, request):
        # Only 2 control accounts should exist
        return ControlAccount.objects.count() < 2

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'occurred_at', 'memo_short', 'created_at']
    list_filter = ['user', 'occurred_at', 'created_at']
    search_fields = ['memo', 'user__username']
    readonly_fields = ['user', 'occurred_at', 'memo', 'created_at']
    date_hierarchy = 'occurred_at'

    def memo_short(self, obj):
        return obj.memo[:50] + '...' if len(obj.memo) > 50 else obj.memo
    memo_short.short_description = 'Memo'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Posting)
class PostingAdmin(admin.ModelAdmin):
    list_display = ['id', 'journal_entry', 'posting_type', 'amount', 'account_info', 'created_at']
    list_filter = ['posting_type', 'currency', 'created_at']
    search_fields = ['memo', 'journal_entry__memo']
    readonly_fields = ['journal_entry', 'account_content_type', 'account_object_id', 'amount', 'posting_type', 'currency', 'memo', 'created_at']
    date_hierarchy = 'created_at'

    def account_info(self, obj):
        return f"{obj.account_content_type.model} #{obj.account_object_id}"
    account_info.short_description = 'Account'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
