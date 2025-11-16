from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from accounts.models import Account, AccountBalance
from categories.models import Category


@login_required
def dashboard(request):
    """Dashboard view with account summary and stats."""
    # Get user's accounts with balances
    accounts = Account.objects.filter(user=request.user).select_related('balance').order_by('-created_at')
    
    # Calculate stats
    total_balance = AccountBalance.objects.filter(
        account__user=request.user
    ).aggregate(
        total=Sum('balance_amount')
    )['total'] or 0
    
    stats = {
        'net_worth': total_balance,
        'total_accounts': accounts.count(),
        'total_categories': Category.objects.filter(user=request.user).count(),
    }
    
    context = {
        'accounts': accounts[:5],  # Show first 5 accounts
        'stats': stats,
    }
    
    return render(request, 'dashboard/dashboard.html', context)
