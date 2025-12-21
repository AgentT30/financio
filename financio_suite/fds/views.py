from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Count
from decimal import Decimal
from .models import FixedDeposit
from .forms import FixedDepositForm
from activity.utils import log_activity


@login_required
def fd_list(request):
    """
    List all fixed deposits with stats and maturity badges.

    Features:
    - Shows both active and archived FDs
    - Stats card: Total FDs, total principal, total maturity amount (active only)
    - Maturity status badges (green/orange/gray based on dates)
    - Responsive grid layout

    Args:
        request: HttpRequest object

    Returns:
        Rendered FD list template with context containing:
        - fds: All user's FDs (ordered by maturity_date desc)
        - Stats for active FDs
    """
    # Query all FDs for the user
    fds = FixedDeposit.objects.filter(
        user=request.user
    ).order_by('-maturity_date', '-created_at')

    # Calculate stats for active FDs only
    active_fds = fds.filter(status='active')
    
    total_fds = active_fds.count()
    archived_fds = fds.filter(status='archived').count()
    total_principal = active_fds.aggregate(
        total=Sum('principal_amount')
    )['total'] or Decimal('0.00')
    total_maturity = active_fds.aggregate(
        total=Sum('maturity_amount')
    )['total'] or Decimal('0.00')

    context = {
        'fixed_deposits': fds,
        'total_fds': total_fds,
        'archived_fds': archived_fds,
        'total_principal': total_principal,
        'total_maturity': total_maturity,
    }
    return render(request, 'fds/fd_list.html', context)


@login_required
def fd_create(request):
    """
    Create a new fixed deposit.

    Creates the FixedDeposit record and logs activity.
    No balance table needed (FDs are informational only).

    Args:
        request: HttpRequest object

    Returns:
        GET: Rendered FD form template
        POST: Redirect to fd_list on success, or re-render form with errors
    """
    if request.method == 'POST':
        form = FixedDepositForm(request.POST)
        if form.is_valid():
            fd = form.save(commit=False)
            fd.user = request.user
            fd.save()

            # Log activity
            log_activity(
                user=request.user,
                action='create',
                obj=fd,
                request=request
            )

            messages.success(request, f'Fixed Deposit "{fd.name}" created successfully!')
            return redirect('fd_list')
    else:
        form = FixedDepositForm()

    context = {
        'form': form,
        'title': 'Create Fixed Deposit',
        'button_text': 'Create FD',
    }
    return render(request, 'fds/fd_form.html', context)


@login_required
def fd_detail(request, pk):
    """
    View fixed deposit details.

    Shows all FD information with conditional "Mark as Matured" button
    for active FDs that have passed their maturity date.

    Args:
        request: HttpRequest object
        pk: Primary key of the FD

    Returns:
        Rendered FD detail template
    """
    fd = get_object_or_404(FixedDeposit, pk=pk, user=request.user)

    # Get maturity badge info
    badge_info = fd.get_maturity_badge_info()

    context = {
        'fd': fd,
        'badge_info': badge_info,
        'interest_earned': fd.get_interest_earned(),
        'can_mark_matured': fd.status == 'active' and fd.is_matured(),
    }
    return render(request, 'fds/fd_detail.html', context)


@login_required
def fd_edit(request, pk):
    """
    Edit an existing fixed deposit.

    Prevents editing if FD is archived.

    Args:
        request: HttpRequest object
        pk: Primary key of the FD

    Returns:
        GET: Rendered FD form template with existing data
        POST: Redirect to fd_list on success, or re-render form with errors
    """
    fd = get_object_or_404(FixedDeposit, pk=pk, user=request.user)

    # Prevent editing archived FDs
    if fd.status == 'archived':
        messages.error(request, f'Cannot edit archived FD "{fd.name}".')
        return redirect('fd_detail', pk=pk)

    if request.method == 'POST':
        form = FixedDepositForm(request.POST, instance=fd)
        if form.is_valid():
            fd = form.save()

            # Log activity with field changes
            log_activity(
                user=request.user,
                action='update',
                obj=fd,
                request=request
            )

            messages.success(request, f'Fixed Deposit "{fd.name}" updated successfully!')
            return redirect('fd_detail', pk=pk)
    else:
        form = FixedDepositForm(instance=fd)

    context = {
        'form': form,
        'fd': fd,
        'title': 'Edit Fixed Deposit',
        'button_text': 'Update FD',
    }
    return render(request, 'fds/fd_form.html', context)


@login_required
def fd_delete(request, pk):
    """
    Delete a fixed deposit.

    FDs have no dependencies (no transactions/transfers),
    so they can always be deleted.

    Args:
        request: HttpRequest object
        pk: Primary key of the FD

    Returns:
        GET: Rendered delete confirmation template
        POST: Redirect to fd_list after deletion
    """
    fd = get_object_or_404(FixedDeposit, pk=pk, user=request.user)

    if request.method == 'POST':
        name = fd.name

        # Log activity before deletion
        log_activity(
            user=request.user,
            action='delete',
            obj=fd,
            request=request
        )

        # Delete the FD (no dependencies to worry about)
        fd.delete()

        messages.success(request, f'Fixed Deposit "{name}" deleted successfully!')
        return redirect('fd_list')

    context = {
        'fd': fd,
    }
    return render(request, 'fds/fd_confirm_delete.html', context)


@login_required
def fd_mark_matured(request, pk):
    """
    Mark FD as matured by setting status to 'archived'.

    This action is irreversible. Only works for active FDs.

    Args:
        request: HttpRequest object
        pk: Primary key of the FD

    Returns:
        POST only: Redirect to fd_list with success/error message
    """
    fd = get_object_or_404(FixedDeposit, pk=pk, user=request.user)

    if request.method == 'POST':
        # Verify FD is active
        if fd.status != 'active':
            messages.error(request, f'FD "{fd.name}" is already archived.')
            return redirect('fd_detail', pk=pk)

        # Mark as matured (archive)
        fd.status = 'archived'
        fd.save()

        # Log activity
        log_activity(
            user=request.user,
            action='update',
            obj=fd,
            request=request,
            changes={'status': {'old': 'active', 'new': 'archived'}}
        )

        messages.success(
            request,
            f'Fixed Deposit "{fd.name}" marked as matured and archived.'
        )
        return redirect('fd_list')

    # GET request not allowed for this action
    messages.error(request, 'Invalid request method.')
    return redirect('fd_detail', pk=pk)
