from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from accounts.models import BankAccount
from creditcards.models import CreditCard
from fds.models import FixedDeposit
from investments.models import Investment
from categories.models import Category
from transactions.models import Transaction


@login_required
def dashboard(request):
    """
    Dashboard view displaying financial overview and recent activity.

    Displays:
    - Net Worth (sum of bank account balances only, excludes credit card debt)
    - Total Accounts breakdown ("X Banks • Y Cards")
    - Month-to-date Income and Expense
    - Recent transactions (last 10 across all account types)

    Note: Uses get_current_balance() method for graceful handling of missing
    balance records (falls back to opening_balance).

    Args:
        request: HttpRequest object

    Returns:
        Rendered dashboard template with context containing:
        - accounts: First 5 active bank accounts
        - stats: Dictionary with net_worth, total_banks, total_cards, etc.
        - recent_transactions: Last 10 transactions across all accounts
    """
    # Get user's bank accounts with balances
    accounts = BankAccount.objects.filter(
        user=request.user,
        status='active'
    ).select_related('balance').order_by('-created_at')

    # Calculate Net Worth (Bank balances only - excludes credit card debt)
    # Per user specification: Net Worth = Bank balances + Investments (no debt subtraction)
    # Use get_current_balance() to handle cases where balance record doesn't exist
    net_worth = sum(
        account.get_current_balance()
        for account in BankAccount.objects.filter(user=request.user, status='active')
    )

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

    # Count banks, credit cards, FDs, and Investments separately
    total_banks = BankAccount.objects.filter(user=request.user, status='active').count()
    total_cards = CreditCard.objects.filter(user=request.user, status='active').count()
    total_fds = FixedDeposit.objects.filter(user=request.user, status='active').count()
    total_investments = Investment.objects.filter(user=request.user, status='active').count()

    # Calculate total FD value (sum of maturity amounts for active FDs)
    total_fd_value = FixedDeposit.objects.filter(
        user=request.user, 
        status='active'
    ).aggregate(total=Sum('maturity_amount'))['total'] or 0

    # Calculate total Investment value
    # Since current_value is a property, we have to sum it in Python
    # Or we can annotate it if we move calculation to DB (but it depends on transactions)
    # For now, iterating is fine as number of investments is likely small
    active_investments = Investment.objects.filter(user=request.user, status='active')
    total_investment_value = sum(inv.current_value for inv in active_investments)

    # Add FD and Investment value to net worth
    net_worth += total_fd_value + total_investment_value

    stats = {
        'net_worth': net_worth,  # Bank + FD + Investments
        'total_banks': total_banks,
        'total_cards': total_cards,
        'total_fds': total_fds,
        'total_investments': total_investments,
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
