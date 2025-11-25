from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.db.models.deletion import ProtectedError
from decimal import Decimal
from .models import BankAccount, BankAccountBalance
from .forms import BankAccountForm
from creditcards.models import CreditCard, CreditCardBalance
from transactions.models import Transaction
from transfers.models import Transfer


@login_required
def account_list(request):
    """Display all user bank accounts and credit cards."""
    # Query bank accounts
    bank_accounts = BankAccount.objects.filter(
        user=request.user
    ).select_related('balance').order_by('status', '-created_at')
    
    # Query credit cards
    credit_cards = CreditCard.objects.filter(
        user=request.user
    ).select_related('balance').order_by('status', '-created_at')
    
    # Calculate bank account stats
    active_banks = bank_accounts.filter(status='active')
    # Use get_current_balance() to handle cases where balance record doesn't exist
    total_bank_balance = sum(
        account.get_current_balance()
        for account in active_banks
    )
    
    # Calculate credit card stats
    active_cards = credit_cards.filter(status='active')
    total_credit_limit = active_cards.aggregate(
        total=Sum('credit_limit')
    )['total'] or Decimal('0.00')
    
    # Calculate total available credit and amount owed
    total_available_credit = Decimal('0.00')
    total_amount_owed = Decimal('0.00')
    
    for card in active_cards:
        total_available_credit += card.available_credit()
        total_amount_owed += card.amount_owed()
    
    context = {
        # Bank accounts
        'bank_accounts': bank_accounts,
        'active_banks_count': active_banks.count(),
        'archived_banks_count': bank_accounts.filter(status='archived').count(),
        'total_bank_balance': total_bank_balance,
        
        # Credit cards
        'credit_cards': credit_cards,
        'active_cards_count': active_cards.count(),
        'archived_cards_count': credit_cards.filter(status='archived').count(),
        'total_credit_limit': total_credit_limit,
        'total_available_credit': total_available_credit,
        'total_amount_owed': total_amount_owed,
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
            
            messages.success(request, f'Account "{account.name}" created successfully!')
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
        # Store old opening balance to check if it changed
        old_opening_balance = account.opening_balance
        
        form = BankAccountForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            account = form.save()
            
            # If opening balance changed, update the materialized balance
            # (only if no transactions have been recorded yet)
            if old_opening_balance != account.opening_balance:
                try:
                    balance_record = account.balance
                    # Only update if this is still the opening balance (no transactions)
                    if balance_record.last_posting_id is None:
                        balance_record.balance_amount = account.opening_balance
                        balance_record.save()
                except BankAccountBalance.DoesNotExist:
                    # Create balance record if it doesn't exist
                    BankAccountBalance.objects.create(
                        account=account,
                        balance_amount=account.opening_balance
                    )
            
            messages.success(request, f'Account "{account.name}" updated successfully!')
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
    """View bank account details with transaction history."""
    account = get_object_or_404(BankAccount, pk=pk, user=request.user)
    
    # Get ContentType for this account
    account_content_type = ContentType.objects.get_for_model(BankAccount)
    
    # Get transactions for this account (filtered by GenericForeignKey)
    transactions = Transaction.objects.filter(
        user=request.user,
        account_content_type=account_content_type,
        account_object_id=account.id,
        deleted_at__isnull=True
    ).select_related('category').order_by('-datetime_ist')
    
    # Get transfers involving this account (either from or to)
    transfers = Transfer.objects.filter(
        user=request.user,
        deleted_at__isnull=True
    ).filter(
        Q(from_account_content_type=account_content_type, from_account_object_id=account.id) |
        Q(to_account_content_type=account_content_type, to_account_object_id=account.id)
    ).order_by('-datetime_ist')
    
    # Pagination for transactions
    transactions_paginator = Paginator(transactions, 20)
    transactions_page_number = request.GET.get('transactions_page', 1)
    transactions_page = transactions_paginator.get_page(transactions_page_number)
    
    # Pagination for transfers
    transfers_paginator = Paginator(transfers, 20)
    transfers_page_number = request.GET.get('transfers_page', 1)
    transfers_page = transfers_paginator.get_page(transfers_page_number)
    
    context = {
        'account': account,
        'full_account_number': str(account.account_number) if account.account_number else None,
        'transactions': transactions_page,
        'transfers': transfers_page,
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
            messages.error(request, f'Cannot delete "{name}" because it has transactions or transfers.')
            return redirect('account_list')
        
        try:
            # Delete the account (cascade will handle BankAccountBalance)
            account.delete()
            messages.success(request, f'Account "{name}" deleted successfully!')
        except ProtectedError:
            # Catch ProtectedError if can_delete() check missed something
            messages.error(request, f'Cannot delete "{name}" because it has transactions or transfers.')
        
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
        messages.success(request, f'Account "{account.name}" archived.')
    else:
        account.activate()
        messages.success(request, f'Account "{account.name}" activated.')
    
    return redirect('account_list')
