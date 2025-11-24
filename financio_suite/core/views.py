from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from accounts.models import BankAccount, BankAccountBalance
from categories.models import Category
from transactions.models import Transaction


@login_required
def dashboard(request):
    """Dashboard view with account summary and stats."""
    # Get user's bank accounts with balances
    accounts = BankAccount.objects.filter(user=request.user).select_related('balance').order_by('-created_at')
    
    # Calculate stats
    total_balance = BankAccountBalance.objects.filter(
        account__user=request.user
    ).aggregate(
        total=Sum('balance_amount')
    )['total'] or 0
    
    # Get first day of current month for MTD calculations
    now = timezone.now()
    first_day_of_month = datetime(now.year, now.month, 1, tzinfo=now.tzinfo)
    
    # Calculate month-to-date income and expense
    monthly_income = Transaction.objects.filter(
        user=request.user,
        transaction_type='income',
        datetime_ist__gte=first_day_of_month,
        deleted_at__isnull=True
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_expense = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        datetime_ist__gte=first_day_of_month,
        deleted_at__isnull=True
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get recent transactions (last 10)
    recent_transactions = Transaction.objects.filter(
        user=request.user,
        deleted_at__isnull=True
    ).select_related('category').prefetch_related('account_content_type').order_by('-datetime_ist')[:10]
    
    stats = {
        'net_worth': total_balance,
        'total_accounts': accounts.count(),
        'total_categories': Category.objects.filter(user=request.user).count(),
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
    }
    
    context = {
        'accounts': accounts[:5],  # Show first 5 accounts
        'stats': stats,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'dashboard/dashboard.html', context)
