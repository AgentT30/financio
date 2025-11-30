from django.contrib import admin
from .models import Investment, InvestmentTransaction, Broker

class InvestmentTransactionInline(admin.TabularInline):
    model = InvestmentTransaction
    extra = 0
    readonly_fields = ('total_amount',)

@admin.register(Broker)
class BrokerAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'broker_user_id', 'demat_account_number_last4')
    search_fields = ('name', 'user__username', 'broker_user_id')

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'broker', 'investment_type', 'total_quantity', 'current_price', 'current_value', 'status')
    list_filter = ('investment_type', 'status', 'user', 'broker')
    search_fields = ('name', 'symbol', 'broker__name')
    inlines = [InvestmentTransactionInline]
    readonly_fields = ('total_quantity', 'average_buy_price', 'total_invested', 'current_value', 'unrealized_pnl')

@admin.register(InvestmentTransaction)
class InvestmentTransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'transaction_type', 'investment', 'quantity', 'price_per_unit', 'total_amount')
    list_filter = ('transaction_type', 'date', 'investment__user')
    search_fields = ('investment__name', 'investment__symbol')
    date_hierarchy = 'date'
