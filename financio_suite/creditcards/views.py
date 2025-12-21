from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.db.models.deletion import ProtectedError
from .models import CreditCard, CreditCardBalance
from .forms import CreditCardForm
from transactions.models import Transaction
from transfers.models import Transfer


@login_required
def creditcard_list(request):
    """Display all user credit cards."""
    creditcards = CreditCard.objects.filter(
        user=request.user
    ).select_related('balance').order_by('status', '-created_at')

    # Calculate totals
    active_cards = creditcards.filter(status='active')

    # Total amount owed (sum of negative balances)
    total_owed = 0
    total_credit_limit = 0
    total_available_credit = 0

    for card in active_cards:
        total_owed += card.amount_owed()
        total_credit_limit += card.credit_limit
        total_available_credit += card.available_credit()

    context = {
        'creditcards': creditcards,
        'active_count': active_cards.count(),
        'archived_count': creditcards.filter(status='archived').count(),
        'total_owed': total_owed,
        'total_credit_limit': total_credit_limit,
        'total_available_credit': total_available_credit,
    }
    return render(request, 'creditcards/creditcard_list.html', context)


@login_required
def creditcard_create(request):
    """Create a new credit card."""
    if request.method == 'POST':
        form = CreditCardForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            creditcard = form.save(commit=False)
            creditcard.user = request.user
            creditcard.save()

            # Create initial balance record
            CreditCardBalance.objects.create(
                account=creditcard,
                balance_amount=creditcard.opening_balance
            )

            messages.success(request, f'Credit Card "{creditcard.name}" created successfully!')
            return redirect('creditcard_list')
    else:
        form = CreditCardForm(user=request.user)

    context = {
        'form': form,
        'title': 'Add Credit Card',
        'button_text': 'Add Credit Card',
    }
    return render(request, 'creditcards/creditcard_form.html', context)


@login_required
def creditcard_edit(request, pk):
    """Edit an existing credit card."""
    creditcard = get_object_or_404(CreditCard, pk=pk, user=request.user)

    if request.method == 'POST':
        # Store old opening balance to check if it changed
        old_opening_balance = creditcard.opening_balance

        form = CreditCardForm(request.POST, request.FILES, instance=creditcard, user=request.user)
        if form.is_valid():
            creditcard = form.save()

            # If opening balance changed, update the materialized balance
            # (only if no transactions have been recorded yet)
            if old_opening_balance != creditcard.opening_balance:
                try:
                    balance_record = creditcard.balance
                    # Only update if this is still the opening balance (no transactions)
                    if balance_record.last_posting_id is None:
                        balance_record.balance_amount = creditcard.opening_balance
                        balance_record.save()
                except CreditCardBalance.DoesNotExist:
                    # Create balance record if it doesn't exist
                    CreditCardBalance.objects.create(
                        account=creditcard,
                        balance_amount=creditcard.opening_balance
                    )

            messages.success(request, f'Credit Card "{creditcard.name}" updated successfully!')
            return redirect('creditcard_list')
    else:
        form = CreditCardForm(instance=creditcard, user=request.user)

    context = {
        'form': form,
        'creditcard': creditcard,
        'title': 'Edit Credit Card',
        'button_text': 'Update Credit Card',
    }
    return render(request, 'creditcards/creditcard_form.html', context)


@login_required
def creditcard_detail(request, pk):
    """View credit card details with transaction history."""
    creditcard = get_object_or_404(CreditCard, pk=pk, user=request.user)

    # Get ContentType for this credit card
    account_content_type = ContentType.objects.get_for_model(CreditCard)

    # Get transactions for this card (filtered by GenericForeignKey)
    transactions = Transaction.objects.filter(
        user=request.user,
        account_content_type=account_content_type,
        account_object_id=creditcard.id,
        deleted_at__isnull=True
    ).select_related('category').order_by('-datetime_ist')

    # Get transfers involving this card (either from or to)
    transfers = Transfer.objects.filter(
        user=request.user,
        deleted_at__isnull=True
    ).filter(
        Q(from_account_content_type=account_content_type, from_account_object_id=creditcard.id) |
        Q(to_account_content_type=account_content_type, to_account_object_id=creditcard.id)
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
        'creditcard': creditcard,
        'full_card_number': str(creditcard.card_number) if creditcard.card_number else None,
        'full_cvv': str(creditcard.cvv) if creditcard.cvv else None,
        'transactions': transactions_page,
        'transfers': transfers_page,
    }
    return render(request, 'creditcards/creditcard_detail.html', context)


@login_required
def creditcard_delete(request, pk):
    """Delete a credit card."""
    creditcard = get_object_or_404(CreditCard, pk=pk, user=request.user)

    if request.method == 'POST':
        name = creditcard.name

        # Check if card can be deleted
        if not creditcard.can_delete():
            messages.error(request, f'Cannot delete "{name}" because it has transactions or transfers.')
            return redirect('creditcard_list')

        try:
            # Delete the card (cascade will handle CreditCardBalance)
            creditcard.delete()
            messages.success(request, f'Credit Card "{name}" deleted successfully!')
        except ProtectedError:
            # Catch ProtectedError if can_delete() check missed something
            messages.error(request, f'Cannot delete "{name}" because it has transactions or transfers.')

        return redirect('creditcard_list')

    context = {
        'creditcard': creditcard,
    }
    return render(request, 'creditcards/creditcard_confirm_delete.html', context)


@login_required
def creditcard_toggle_status(request, pk):
    """Toggle credit card status between active and archived."""
    creditcard = get_object_or_404(CreditCard, pk=pk, user=request.user)

    if creditcard.status == 'active':
        creditcard.archive()
        messages.success(request, f'Credit Card "{creditcard.name}" archived.')
    else:
        creditcard.activate()
        messages.success(request, f'Credit Card "{creditcard.name}" activated.')

    return redirect('creditcard_list')
