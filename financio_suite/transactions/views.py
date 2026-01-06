from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.contrib import messages
from django.utils import timezone
from django.db import transaction as db_transaction
from decimal import Decimal
from itertools import chain
from operator import attrgetter

from .models import Transaction
from .forms import TransactionForm
from categories.models import Category
from accounts.models import BankAccount
from creditcards.models import CreditCard
from transfers.models import Transfer
from django.contrib.contenttypes.models import ContentType
from ledger.services import LedgerService
from activity.utils import log_activity, track_model_changes
from core.utils import get_all_accounts_with_emoji


@login_required
def transaction_list(request):
    """
    Unified list view for transactions and transfers with filtering, search, and pagination.
    Use ?view=transfers to show transfers instead of transactions.
    """
    # Determine active view (transactions or transfers)
    view_type = request.GET.get('view', 'transactions').strip()

    if view_type == 'transfers':
        # Get all non-deleted transfers
        items = Transfer.objects.filter(
            user=request.user,
            deleted_at__isnull=True
        ).select_related(
            'from_account_content_type',
            'to_account_content_type',
            'journal_entry'
        ).order_by('-datetime_ist')

        # Search by memo
        search_query = request.GET.get('search', '').strip()
        if search_query:
            items = items.filter(Q(memo__icontains=search_query))

        # Filter by from_account
        from_account_id = request.GET.get('from_account', '').strip()
        if from_account_id:
            if '|' in from_account_id:
                obj_id, model_name = from_account_id.split('|')
                items = items.filter(from_account_content_type__model=model_name, from_account_object_id=obj_id)
            elif ':' in from_account_id:
                ct_id, obj_id = from_account_id.split(':')
                items = items.filter(from_account_content_type_id=ct_id, from_account_object_id=obj_id)
            else:
                items = items.filter(from_account_object_id=from_account_id)

        # Filter by to_account
        to_account_id = request.GET.get('to_account', '').strip()
        if to_account_id:
            if '|' in to_account_id:
                obj_id, model_name = to_account_id.split('|')
                items = items.filter(to_account_content_type__model=model_name, to_account_object_id=obj_id)
            elif ':' in to_account_id:
                ct_id, obj_id = to_account_id.split(':')
                items = items.filter(to_account_content_type_id=ct_id, to_account_object_id=obj_id)
            else:
                items = items.filter(to_account_object_id=to_account_id)

        # Filter by date range
        date_from = request.GET.get('date_from', '').strip()
        date_to = request.GET.get('date_to', '').strip()

        if date_from:
            try:
                from datetime import datetime
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                items = items.filter(datetime_ist__date__gte=date_from_obj.date())
            except ValueError:
                pass

        if date_to:
            try:
                from datetime import datetime
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                items = items.filter(datetime_ist__date__lte=date_to_obj.date())
            except ValueError:
                pass

        # Get all active accounts (Bank + Credit Cards) for filter dropdowns
        accounts_data = get_all_accounts_with_emoji(request.user)
        accounts = [{'id': val, 'name': name} for obj, name, val in accounts_data]

        # Pagination
        paginator = Paginator(items, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'accounts': accounts,
            'search_query': search_query,
            'selected_from_account': from_account_id,
            'selected_to_account': to_account_id,
            'date_from': date_from,
            'date_to': date_to,
            'view_type': view_type,
            'is_transfer_view': True,
        }
    else:
        # Get all non-deleted transactions for the user
        items = Transaction.objects.filter(
            user=request.user,
            deleted_at__isnull=True
        ).select_related(
            'category',
            'journal_entry',
            'account_content_type'
        ).order_by('-datetime_ist')

        # Search by purpose
        search_query = request.GET.get('search', '').strip()
        if search_query:
            items = items.filter(
                Q(purpose__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        # Filter by transaction type
        transaction_type = request.GET.get('type', '').strip()
        if transaction_type in ['income', 'expense']:
            items = items.filter(transaction_type=transaction_type)

        # Filter by category
        category_id = request.GET.get('category', '').strip()
        if category_id:
            try:
                items = items.filter(category_id=int(category_id))
            except ValueError:
                pass

        # Filter by account (using content_type and object_id)
        account_id = request.GET.get('account', '').strip()
        if account_id:
            try:
                if '|' in account_id:
                    obj_id, model_name = account_id.split('|')
                    items = items.filter(
                        account_content_type__model=model_name,
                        account_object_id=obj_id
                    )
                elif ':' in account_id:
                    ct_id, obj_id = account_id.split(':')
                    items = items.filter(
                        account_content_type_id=ct_id,
                        account_object_id=obj_id
                    )
                else:
                    # Legacy support for BankAccount only
                    bank_account_ct = ContentType.objects.get_for_model(BankAccount)
                    items = items.filter(
                        account_content_type=bank_account_ct,
                        account_object_id=int(account_id)
                    )
            except (ValueError, ContentType.DoesNotExist):
                pass

        # Filter by date range
        date_from = request.GET.get('date_from', '').strip()
        date_to = request.GET.get('date_to', '').strip()

        if date_from:
            try:
                from datetime import datetime
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                items = items.filter(datetime_ist__date__gte=date_from_obj.date())
            except ValueError:
                pass

        if date_to:
            try:
                from datetime import datetime
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                items = items.filter(datetime_ist__date__lte=date_to_obj.date())
            except ValueError:
                pass

        # Pagination (20 per page)
        paginator = Paginator(items, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Get categories and accounts for filter dropdowns
        categories = Category.objects.filter(user=request.user).order_by('name')
        
        # Get all active accounts (Bank + Credit Cards)
        accounts_data = get_all_accounts_with_emoji(request.user)
        accounts = [{'id': val, 'name': name} for obj, name, val in accounts_data]

        context = {
            'page_obj': page_obj,
            'categories': categories,
            'accounts': accounts,
            'search_query': search_query,
            'selected_type': transaction_type,
            'selected_category': category_id,
            'selected_account': account_id,
            'date_from': date_from,
            'date_to': date_to,
            'view_type': view_type,
            'is_transfer_view': False,
        }

    return render(request, 'transactions/transaction_list.html', context)


@login_required
def transaction_create(request):
    """
    Create a new transaction with double-entry ledger integration.
    """
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)

        if form.is_valid():
            try:
                # Create transaction instance (don't save yet)
                transaction = form.save(commit=False)
                transaction.user = request.user

                # Get the account and datetime from cleaned_data
                account = form.cleaned_data.get('account')
                datetime_ist = form.cleaned_data.get('datetime_ist')

                if account:
                    from django.contrib.contenttypes.models import ContentType
                    transaction.account_content_type = ContentType.objects.get_for_model(account)
                    transaction.account_object_id = account.id

                if datetime_ist:
                    transaction.datetime_ist = datetime_ist

                # Create journal entry using LedgerService
                ledger_service = LedgerService()

                memo = f"{transaction.get_transaction_type_display()}: {transaction.purpose[:100]}"

                journal_entry = ledger_service.create_simple_entry(
                    user=request.user,
                    transaction_type=transaction.transaction_type,
                    account=account,
                    amount=transaction.amount,
                    occurred_at=transaction.datetime_ist,
                    memo=memo
                )

                # Link transaction to journal entry
                transaction.journal_entry = journal_entry
                transaction.save(skip_validation=True)

                # Log activity
                log_activity(
                    user=request.user,
                    action='create',
                    obj=transaction,
                    changes={
                        'transaction_type': transaction.transaction_type,
                        'amount': str(transaction.amount),
                        'account': str(account),
                        'category': transaction.category.name if transaction.category else None,
                        'method': transaction.method_type,
                    },
                    request=request
                )

                messages.success(request, f'Transaction created successfully! Balance updated.')
                return redirect('transactions:transaction_list')

            except Exception as e:
                messages.error(request, f'Error creating transaction: {str(e)}')
                # Re-render form with errors
        else:
            # Form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = TransactionForm(user=request.user)

    context = {
        'form': form,
        'page_title': 'Add Transaction',
        'submit_text': 'Create Transaction',
    }

    return render(request, 'transactions/transaction_form.html', context)


@login_required
def transaction_edit(request, pk):
    """
    Edit an existing transaction.
    Note: Editing transactions requires reversing and recreating ledger entries.
    """
    transaction = get_object_or_404(
        Transaction,
        pk=pk,
        user=request.user,
        deleted_at__isnull=True
    )

    # Store old instance for change tracking
    old_transaction = Transaction.objects.get(pk=transaction.pk)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)

        if form.is_valid():
            try:
                with db_transaction.atomic():
                    # Track changes
                    changes = track_model_changes(
                        old_instance=old_transaction,
                        new_instance=form.instance,
                        fields_to_track=[
                            'datetime_ist', 'transaction_type', 'amount',
                            'category', 'method_type', 'purpose'
                        ]
                    )

                    # Update transaction instance
                    updated_transaction = form.save(commit=False)

                    # Get the account from form
                    account = form.cleaned_data.get('account')
                    if account:
                        from django.contrib.contenttypes.models import ContentType
                        updated_transaction.account_content_type = ContentType.objects.get_for_model(account)
                        updated_transaction.account_object_id = account.id

                    # For transaction edits, reverse old entry and create new one
                    ledger_service = LedgerService()

                    # Store the old account for reversal (might be different from new account)
                    old_account = old_transaction.account if old_transaction.account else None

                    # Delete old journal entry and reverse balances
                    if updated_transaction.journal_entry:
                        old_journal = updated_transaction.journal_entry

                        # Find the posting that affected the user's account (not ControlAccount)
                        # Journal has 2 postings: one for user account, one for control account
                        # We need the user account posting to reverse its balance effect
                        old_user_posting = None
                        for posting in old_journal.postings.all():
                            if posting.account:
                                account_type = posting.account.__class__.__name__
                                if account_type in ['BankAccount', 'CreditCard']:
                                    old_user_posting = posting
                                    break

                        # Reverse the old posting's effect on account balance
                        if old_user_posting and old_account:
                            account_type = old_account.__class__.__name__
                            if account_type in ['BankAccount', 'CreditCard']:
                                # Reverse by applying negative of the posting amount
                                # Example: Old posting was +100 (income), reverse with -100
                                # Example: Old posting was -50 (expense), reverse with +50
                                ledger_service._update_account_balance(
                                    account=old_account,
                                    delta=-old_user_posting.amount,
                                    posting_id=old_user_posting.id
                                )

                        # Unlink transaction from journal entry before deleting
                        updated_transaction.journal_entry = None
                        updated_transaction.save()
                        # Delete the old journal entry (cascades to postings)
                        old_journal.delete()

                    # Create new journal entry with updated values
                    new_journal_entry = ledger_service.create_simple_entry(
                        user=request.user,
                        transaction_type=updated_transaction.transaction_type,
                        account=account,
                        amount=updated_transaction.amount,
                        occurred_at=updated_transaction.datetime_ist,
                        memo=f"{updated_transaction.get_transaction_type_display()}: {updated_transaction.purpose[:100]}"
                    )

                    # Link transaction to new journal entry
                    updated_transaction.journal_entry = new_journal_entry
                    updated_transaction.save()

                    # Log activity
                    if changes:
                        log_activity(
                            user=request.user,
                            action='update',
                            obj=updated_transaction,
                            changes=changes,
                            request=request
                        )

                messages.success(request, 'Transaction updated successfully!')
                return redirect('transactions:transaction_list')

            except Exception as e:
                messages.error(request, f'Error updating transaction: {str(e)}')
        else:
            # Form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        # Form will automatically populate account field from instance
        form = TransactionForm(instance=transaction, user=request.user)

    context = {
        'form': form,
        'transaction': transaction,
        'page_title': 'Edit Transaction',
        'submit_text': 'Update Transaction',
    }

    return render(request, 'transactions/transaction_form.html', context)


@login_required
def transaction_delete(request, pk):
    """
    Soft delete a transaction by setting deleted_at timestamp.
    """
    transaction = get_object_or_404(
        Transaction,
        pk=pk,
        user=request.user,
        deleted_at__isnull=True
    )

    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                # Get account before soft delete
                account = transaction.account

                # Reverse the balance change
                if account and transaction.journal_entry:
                    ledger_service = LedgerService()

                    # For income: we debited (added) money, so credit (subtract) it back
                    # For expense: we credited (subtracted) money, so debit (add) it back
                    # Double-entry reversal: negate the original posting's effect
                    if transaction.transaction_type == 'income':
                        delta = -transaction.amount  # Reverse the debit (was +amount)
                    elif transaction.transaction_type == 'expense':
                        delta = transaction.amount   # Reverse the credit (was -amount)
                    else:
                        delta = Decimal('0')

                    # Get the posting ID for this transaction
                    posting = transaction.journal_entry.postings.filter(
                        account_object_id=account.id
                    ).first()

                    if posting:
                        # Update account balance
                        ledger_service._update_account_balance(
                            account,
                            delta,
                            posting.id
                        )

                # Soft delete
                transaction.deleted_at = timezone.now()
                transaction.save(update_fields=['deleted_at'])

                # Log activity
                log_activity(
                    user=request.user,
                    action='delete',
                    obj=transaction,
                    changes={
                        'deleted_at': transaction.deleted_at.isoformat(),
                        'amount': str(transaction.amount),
                        'type': transaction.transaction_type,
                    },
                    request=request
                )

            messages.success(request, 'Transaction deleted successfully! Balance updated.')
            return redirect('transactions:transaction_list')

        except Exception as e:
            messages.error(request, f'Error deleting transaction: {str(e)}')
            return redirect('transactions:transaction_list')

    context = {
        'transaction': transaction,
        'page_title': 'Delete Transaction',
    }

    return render(request, 'transactions/transaction_confirm_delete.html', context)
