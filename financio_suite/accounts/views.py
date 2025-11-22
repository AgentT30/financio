from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import BankAccount, BankAccountBalance
from .forms import BankAccountForm


@login_required
def account_list(request):
    """Display all user bank accounts."""
    accounts = BankAccount.objects.filter(
        user=request.user
    ).select_related('balance').order_by('status', '-created_at')
    
    # Calculate totals
    active_accounts = accounts.filter(status='active')
    total_balance = active_accounts.aggregate(
        total=Sum('balance__balance_amount')
    )['total'] or 0
    
    context = {
        'accounts': accounts,
        'active_count': active_accounts.count(),
        'archived_count': accounts.filter(status='archived').count(),
        'total_balance': total_balance,
    }
    return render(request, 'accounts/account_list.html', context)


@login_required
def account_create(request):
    """Create a new bank account."""
    if request.method == 'POST':
        form = BankAccountForm(request.POST, request.FILES)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            
            # Create initial balance record
            BankAccountBalance.objects.create(
                account=account,
                balance_amount=account.opening_balance
            )
            
            messages.success(request, f'Account "{account.name.title()}" created successfully!')
            return redirect('account_list')
    else:
        form = BankAccountForm()
    
    context = {
        'form': form,
        'title': 'Create Account',
        'button_text': 'Create Account',
    }
    return render(request, 'accounts/account_form.html', context)


@login_required
def account_edit(request, pk):
    """Edit an existing bank account."""
    account = get_object_or_404(BankAccount, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BankAccountForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, f'Account "{account.name.title()}" updated successfully!')
            return redirect('account_list')
    else:
        form = BankAccountForm(instance=account)
    
    context = {
        'form': form,
        'account': account,
        'title': 'Edit Account',
        'button_text': 'Update Account',
    }
    return render(request, 'accounts/account_form.html', context)


@login_required
def account_detail(request, pk):
    """View bank account details."""
    account = get_object_or_404(BankAccount, pk=pk, user=request.user)
    
    # TODO: Get recent transactions when Transaction model is ready
    # transactions = account.transactions.all()[:10]
    
    context = {
        'account': account,
        'full_account_number': str(account.account_number) if account.account_number else None,
        # 'transactions': transactions,
    }
    return render(request, 'accounts/account_detail.html', context)


@login_required
def account_delete(request, pk):
    """Delete a bank account."""
    account = get_object_or_404(BankAccount, pk=pk, user=request.user)
    
    if request.method == 'POST':
        name = account.name
        
        # Check if account can be deleted
        if not account.can_delete():
            messages.error(request, f'Cannot delete "{name.title()}" because it has transactions.')
            return redirect('account_list')
        
        # Delete the account (cascade will handle BankAccountBalance)
        account.delete()
        messages.success(request, f'Account "{name.title()}" deleted successfully!')
        return redirect('account_list')
    
    context = {
        'account': account,
    }
    return render(request, 'accounts/account_confirm_delete.html', context)


@login_required
def account_toggle_status(request, pk):
    """Toggle bank account status between active and archived."""
    account = get_object_or_404(BankAccount, pk=pk, user=request.user)
    
    if account.status == 'active':
        account.archive()
        messages.success(request, f'Account "{account.name.title()}" archived.')
    else:
        account.activate()
        messages.success(request, f'Account "{account.name.title()}" activated.')
    
    return redirect('account_list')
