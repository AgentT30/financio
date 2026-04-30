from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction as db_transaction
from django.contrib.contenttypes.models import ContentType
from .models import Transfer
from .forms import TransferForm
from accounts.models import BankAccount
from ledger.services import LedgerService
from activity.utils import log_activity, track_model_changes


@login_required
def transfer_list(request):
    """
    List all transfers for the logged-in user with filtering and pagination.
    """
    # Base queryset (exclude soft-deleted)
    transfers = Transfer.objects.filter(
        user=request.user,
        deleted_at__isnull=True
    ).select_related(
        'from_account_content_type',
        'to_account_content_type',
        'journal_entry'
    )

    # Search by memo
    search_query = request.GET.get('search', '').strip()
    if search_query:
        transfers = transfers.filter(
            Q(memo__icontains=search_query)
        )

    # Filter by from_account
    from_account_id = request.GET.get('from_account', '').strip()
    if from_account_id:
        transfers = transfers.filter(from_account_object_id=from_account_id)

    # Filter by to_account
    to_account_id = request.GET.get('to_account', '').strip()
    if to_account_id:
        transfers = transfers.filter(to_account_object_id=to_account_id)

    # Filter by date range
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    if date_from:
        try:
            from datetime import datetime
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            transfers = transfers.filter(datetime_ist__date__gte=date_from_obj.date())
        except ValueError:
            pass

    if date_to:
        try:
            from datetime import datetime
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            transfers = transfers.filter(datetime_ist__date__lte=date_to_obj.date())
        except ValueError:
            pass

    # Pagination (20 per page)
    paginator = Paginator(transfers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get accounts for filter dropdowns
    accounts = BankAccount.objects.filter(user=request.user, status='active').order_by('name')

    context = {
        'page_obj': page_obj,
        'accounts': accounts,
        'search_query': search_query,
        'selected_from_account': from_account_id,
        'selected_to_account': to_account_id,
        'date_from': date_from,
        'date_to': date_to,
    }

    return render(request, 'transfers/transfer_list.html', context)


@login_required
def transfer_create(request):
    """
    Create a new transfer with double-entry ledger integration.
    """
    if request.method == 'POST':
        form = TransferForm(request.POST, user=request.user)

        if form.is_valid():
            try:
                # Get the accounts from form cleaned data
                from_account = form.cleaned_data.get('from_account')
                to_account = form.cleaned_data.get('to_account')

                # Get ContentType for the accounts
                from_account_ct = ContentType.objects.get_for_model(from_account)
                to_account_ct = ContentType.objects.get_for_model(to_account)

                # Create journal entry using LedgerService first
                ledger_service = LedgerService()

                memo = form.cleaned_data.get('memo', '')
                memo_text = f"Transfer: {memo[:100]}" if memo else "Transfer"

                journal_entry, from_balance, to_balance = ledger_service.create_transfer_entry(
                    user=request.user,
                    from_account=from_account,
                    to_account=to_account,
                    amount=form.cleaned_data.get('amount'),
                    occurred_at=form.cleaned_data.get('datetime_ist'),
                    memo=memo_text
                )

                # Now create and save transfer with all fields set
                transfer = Transfer(
                    user=request.user,
                    datetime_ist=form.cleaned_data.get('datetime_ist'),
                    amount=form.cleaned_data.get('amount'),
                    from_account_content_type=from_account_ct,
                    from_account_object_id=from_account.pk,
                    to_account_content_type=to_account_ct,
                    to_account_object_id=to_account.pk,
                    method_type=form.cleaned_data.get('method_type'),
                    memo=memo,
                    journal_entry=journal_entry
                )
                transfer.save(skip_validation=True)

                # Log activity
                log_activity(
                    user=request.user,
                    action='create',
                    obj=transfer,
                    changes={
                        'from_account': str(from_account),
                        'to_account': str(to_account),
                        'amount': str(transfer.amount),
                        'method': transfer.get_method_type_display(),
                        'datetime': transfer.datetime_ist.isoformat(),
                    },
                    request=request
                )

                messages.success(request, f'Transfer of ₹{transfer.amount} created successfully!')
                return redirect('transfers:transfer_list')

            except Exception as e:
                messages.error(request, f'Error creating transfer: {str(e)}')
    else:
        form = TransferForm(user=request.user)

    context = {
        'form': form,
        'page_title': 'New Transfer',
        'submit_text': 'Create Transfer',
    }

    return render(request, 'transfers/transfer_form.html', context)


@login_required
def transfer_edit(request, pk):
    """
    Edit an existing transfer and update the associated ledger entry.
    """
    transfer = get_object_or_404(Transfer, pk=pk, user=request.user, deleted_at__isnull=True)
    old_transfer = Transfer.objects.get(pk=transfer.pk)

    if request.method == 'POST':
        form = TransferForm(request.POST, user=request.user)

        if form.is_valid():
            try:
                with db_transaction.atomic():
                    ledger_service = LedgerService()

                    # Reverse the existing transfer in ledger if a journal entry exists.
                    if transfer.journal_entry:
                        old_from_account = transfer.from_account
                        old_to_account = transfer.to_account
                        old_journal = transfer.journal_entry

                        from_ct = ContentType.objects.get_for_model(old_from_account)
                        to_ct = ContentType.objects.get_for_model(old_to_account)

                        old_from_posting = old_journal.postings.filter(
                            account_content_type=from_ct,
                            account_object_id=old_from_account.id
                        ).first()
                        old_to_posting = old_journal.postings.filter(
                            account_content_type=to_ct,
                            account_object_id=old_to_account.id
                        ).first()

                        if old_from_posting:
                            ledger_service._update_account_balance(
                                old_from_account,
                                -old_from_posting.amount,
                                old_from_posting.id
                            )

                        if old_to_posting:
                            ledger_service._update_account_balance(
                                old_to_account,
                                -old_to_posting.amount,
                                old_to_posting.id
                            )

                        transfer.journal_entry = None
                        transfer.save(update_fields=['journal_entry'])
                        old_journal.delete()

                    from_account = form.cleaned_data.get('from_account')
                    to_account = form.cleaned_data.get('to_account')

                    transfer.datetime_ist = form.cleaned_data.get('datetime_ist')
                    transfer.amount = form.cleaned_data.get('amount')
                    transfer.method_type = form.cleaned_data.get('method_type')
                    transfer.memo = form.cleaned_data.get('memo')
                    transfer.from_account_content_type = ContentType.objects.get_for_model(from_account)
                    transfer.from_account_object_id = from_account.pk
                    transfer.to_account_content_type = ContentType.objects.get_for_model(to_account)
                    transfer.to_account_object_id = to_account.pk
                    transfer.save(skip_validation=True)

                    journal_entry, from_balance, to_balance = ledger_service.create_transfer_entry(
                        user=request.user,
                        occurred_at=transfer.datetime_ist,
                        amount=transfer.amount,
                        from_account=from_account,
                        to_account=to_account,
                        memo=transfer.memo or 'Transfer'
                    )

                    transfer.journal_entry = journal_entry
                    transfer.save(skip_validation=True)

                    changes = track_model_changes(
                        old_instance=old_transfer,
                        new_instance=transfer,
                        fields_to_track=[
                            'datetime_ist', 'amount', 'method_type',
                            'memo', 'from_account_object_id', 'to_account_object_id'
                        ]
                    )

                    if changes:
                        log_activity(
                            user=request.user,
                            action='update',
                            obj=transfer,
                            changes=changes,
                            request=request
                        )

                messages.success(request, 'Transfer updated successfully!')
                return redirect('transfers:transfer_list')

            except Exception as e:
                messages.error(request, f'Error updating transfer: {str(e)}')
    else:
        initial_data = {
            'date': transfer.datetime_ist.date(),
            'amount': transfer.amount,
            'method_type': transfer.method_type,
            'memo': transfer.memo,
            'from_account': f"{transfer.from_account.id}|{transfer.from_account.__class__.__name__.lower()}",
            'to_account': f"{transfer.to_account.id}|{transfer.to_account.__class__.__name__.lower()}"
        }
        form = TransferForm(initial=initial_data, user=request.user)

    context = {
        'form': form,
        'page_title': 'Edit Transfer',
        'submit_text': 'Update Transfer',
    }

    return render(request, 'transfers/transfer_form.html', context)


@login_required
def transfer_delete(request, pk):
    """
    Soft delete a transfer and reverse the balance changes.
    """
    transfer = get_object_or_404(Transfer, pk=pk, user=request.user, deleted_at__isnull=True)

    if request.method == 'POST':
        try:
            with db_transaction.atomic():
                # Get accounts before soft delete
                from_account = transfer.from_account
                to_account = transfer.to_account

                # Reverse the balance changes
                if from_account and to_account and transfer.journal_entry:
                    ledger_service = LedgerService()

                    # Original transfer: from_account decreased, to_account increased
                    # To reverse: from_account increase, to_account decrease

                    # Get the postings for this transfer
                    from_posting = transfer.journal_entry.postings.filter(
                        account_object_id=from_account.id
                    ).first()

                    to_posting = transfer.journal_entry.postings.filter(
                        account_object_id=to_account.id
                    ).first()

                    # Reverse from_account (was credited/decreased, now debit/increase)
                    if from_posting:
                        ledger_service._update_account_balance(
                            from_account,
                            transfer.amount,  # Add back the money
                            from_posting.id
                        )

                    # Reverse to_account (was debited/increased, now credit/decrease)
                    if to_posting:
                        ledger_service._update_account_balance(
                            to_account,
                            -transfer.amount,  # Remove the money
                            to_posting.id
                        )

                # Soft delete
                transfer.soft_delete()

                # Log activity
                log_activity(
                    user=request.user,
                    action='delete',
                    obj=transfer,
                    changes={
                        'deleted_at': transfer.deleted_at.isoformat(),
                        'from_account': str(from_account),
                        'to_account': str(to_account),
                        'amount': str(transfer.amount),
                    },
                    request=request
                )

            messages.success(request, 'Transfer deleted successfully! Balances updated.')
            return redirect('transfers:transfer_list')

        except Exception as e:
            messages.error(request, f'Error deleting transfer: {str(e)}')
            return redirect('transfers:transfer_list')

    context = {
        'transfer': transfer,
    }

    return render(request, 'transfers/transfer_confirm_delete.html', context)

