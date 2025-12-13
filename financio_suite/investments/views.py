from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F
from django.db import transaction
from django.db.models.deletion import ProtectedError
from .models import Investment, InvestmentTransaction, Broker
from .forms import InvestmentForm, InvestmentTransactionForm, BrokerForm, InvestmentCreationForm
from activity.utils import log_activity

# -----------------------------------------------------------------------------
# Broker Views
# -----------------------------------------------------------------------------

@login_required
def broker_list(request):
    """List all brokers for the user."""
    active_brokers = Broker.objects.filter(user=request.user, status='active').order_by('name')
    archived_brokers = Broker.objects.filter(user=request.user, status='archived').order_by('name')
    
    context = {
        'active_brokers': active_brokers,
        'archived_brokers': archived_brokers,
    }
    return render(request, 'investments/broker_list.html', context)

@login_required
def broker_archive(request, pk):
    """Archive a broker."""
    broker = get_object_or_404(Broker, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Check if broker has any active investments
        active_investments_count = Investment.objects.filter(broker=broker, status='active').count()
        
        if active_investments_count > 0:
            messages.error(
                request,
                f"Cannot archive broker '{broker.name}' because it has {active_investments_count} active investment(s). Please archive all investments first."
            )
            return redirect('investments:broker_list')
        
        broker.status = 'archived'
        broker.save()
        log_activity(request.user, 'archived', broker, request=request)
        messages.success(request, f"Broker '{broker.name}' archived successfully.")
        return redirect('investments:broker_list')
        
    return render(request, 'investments/broker_confirm_archive.html', {'broker': broker})

@login_required
def broker_unarchive(request, pk):
    """Unarchive a broker."""
    broker = get_object_or_404(Broker, pk=pk, user=request.user, status='archived')
    
    if request.method == 'POST':
        broker.status = 'active'
        broker.save()
        log_activity(request.user, 'unarchived', broker, request=request)
        messages.success(request, f"Broker '{broker.name}' unarchived successfully.")
        return redirect('investments:broker_list')
        
    return render(request, 'investments/broker_confirm_unarchive.html', {'broker': broker})


@login_required
def broker_create(request):
    """Create a new broker."""
    if request.method == 'POST':
        form = BrokerForm(request.POST)
        if form.is_valid():
            broker = form.save(commit=False)
            broker.user = request.user
            broker.save()
            
            log_activity(request.user, 'created', broker, request=request)
            messages.success(request, f"Broker '{broker.name}' created successfully.")
            return redirect('investments:broker_list')
    else:
        form = BrokerForm()
    
    return render(request, 'investments/broker_form.html', {'form': form, 'title': 'Add Broker'})

@login_required
def broker_edit(request, pk):
    """Edit an existing broker."""
    broker = get_object_or_404(Broker, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BrokerForm(request.POST, instance=broker)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'updated', broker, request=request)
            messages.success(request, "Broker updated successfully.")
            return redirect('investments:broker_list')
    else:
        form = BrokerForm(instance=broker)
    
    return render(request, 'investments/broker_form.html', {'form': form, 'title': 'Edit Broker', 'broker': broker})

@login_required
def broker_delete(request, pk):
    """Delete a broker."""
    broker = get_object_or_404(Broker, pk=pk, user=request.user)
    
    if request.method == 'POST':
        try:
            name = broker.name
            log_activity(request.user, 'deleted', broker, request=request)
            broker.delete()
            messages.success(request, f"Broker '{name}' deleted successfully.")
        except ProtectedError:
            # Get the count of linked investments
            linked_count = Investment.objects.filter(broker=broker).count()
            messages.error(
                request,
                f"Cannot delete broker '{broker.name}' because it has {linked_count} linked investment(s). Please delete or move these investments first."
            )
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            
        return redirect('investments:broker_list')
        
    return render(request, 'investments/broker_confirm_delete.html', {'broker': broker})


# -----------------------------------------------------------------------------
# Investment Views
# -----------------------------------------------------------------------------

@login_required
def investment_list(request):
    """
    List all investments, grouped by broker or flat list.
    Shows summary stats: Total Invested, Current Value, P&L.
    """
    # Check if user wants to see archived investments
    show_archived = request.GET.get('show_archived', 'false').lower() == 'true'
    
    # Check if user wants to filter by broker
    broker_filter = request.GET.get('broker', '')
    
    # Filter investments based on status
    if show_archived:
        investments = Investment.objects.filter(
            user=request.user, 
            status='archived'
        ).select_related('broker').order_by('broker__name', 'name')
    else:
        investments = Investment.objects.filter(
            user=request.user, 
            status='active'
        ).select_related('broker').order_by('broker__name', 'name')
    
    # Apply broker filter if specified
    if broker_filter:
        investments = investments.filter(broker_id=broker_filter)
    
    # Calculate summary stats
    total_invested = sum(inv.total_invested for inv in investments)
    total_current_value = sum(inv.current_value for inv in investments)
    total_pnl = total_current_value - total_invested
    
    # Group by broker for display
    investments_by_broker = {}
    for inv in investments:
        broker_name = inv.broker.name
        if broker_name not in investments_by_broker:
            investments_by_broker[broker_name] = []
        investments_by_broker[broker_name].append(inv)
        
    # Check if user has any brokers
    has_brokers = Broker.objects.filter(user=request.user).exists()
    
    # Get all brokers for filter dropdown (only active brokers unless showing archived investments)
    if show_archived:
        all_brokers = Broker.objects.filter(user=request.user).order_by('name')
    else:
        all_brokers = Broker.objects.filter(user=request.user, status='active').order_by('name')

    context = {
        'investments_by_broker': investments_by_broker,
        'total_invested': total_invested,
        'total_current_value': total_current_value,
        'total_pnl': total_pnl,
        'has_brokers': has_brokers,
        'show_archived': show_archived,
        'all_brokers': all_brokers,
        'selected_broker': broker_filter,
    }
    return render(request, 'investments/investment_list.html', context)

@login_required
def investment_create(request):
    """Create a new investment asset with initial transaction."""
    # Check if user has any brokers
    if not Broker.objects.filter(user=request.user).exists():
        messages.warning(request, "Please add a broker before creating an investment.")
        return redirect('investments:broker_create')

    if request.method == 'POST':
        form = InvestmentCreationForm(request.user, request.POST)
        if form.is_valid():
            investment = form.save()
            
            log_activity(request.user, 'created', investment, request=request)
            messages.success(request, f"Investment '{investment.name}' updated/created successfully.")
            return redirect('investments:investment_detail', pk=investment.pk)
    else:
        initial_data = {}
        if 'name' in request.GET:
            initial_data['name'] = request.GET.get('name')
        if 'symbol' in request.GET:
            initial_data['symbol'] = request.GET.get('symbol')
        if 'broker' in request.GET:
            initial_data['broker'] = request.GET.get('broker')
            
        form = InvestmentCreationForm(request.user, initial=initial_data)
    
    return render(request, 'investments/investment_form.html', {'form': form, 'title': 'Add Investment / Transaction'})

@login_required
def investment_detail(request, pk):
    """Show investment details and transaction history."""
    investment = get_object_or_404(Investment, pk=pk, user=request.user)
    transactions = investment.transactions.all().order_by('-date', '-created_at')
    
    context = {
        'investment': investment,
        'transactions': transactions,
    }
    return render(request, 'investments/investment_detail.html', context)

@login_required
def investment_edit(request, pk):
    """Edit an existing investment."""
    investment = get_object_or_404(Investment, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = InvestmentForm(request.user, request.POST, instance=investment)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'updated', investment, request=request)
            messages.success(request, "Investment updated successfully.")
            return redirect('investments:investment_detail', pk=investment.pk)
    else:
        form = InvestmentForm(request.user, instance=investment)
    
    return render(request, 'investments/investment_form.html', {'form': form, 'title': 'Edit Investment', 'investment': investment})

@login_required
def investment_delete(request, pk):
    """Delete an investment."""
    investment = get_object_or_404(Investment, pk=pk, user=request.user)
    
    if request.method == 'POST':
        name = investment.name
        log_activity(request.user, 'deleted', investment, request=request)
        investment.delete()
        messages.success(request, f"Investment '{name}' deleted successfully.")
        return redirect('investments:investment_list')
        
    return render(request, 'investments/investment_confirm_delete.html', {'investment': investment})


# -----------------------------------------------------------------------------
# Transaction Views
# -----------------------------------------------------------------------------

@login_required
def transaction_create(request, investment_id):
    """
    Redirect to the unified Investment/Transaction creation form (Smart Form).
    Pre-fills the investment name and broker.
    """
    investment = get_object_or_404(Investment, pk=investment_id, user=request.user)
    return redirect(f"{reverse('investments:investment_create')}?name={investment.name}&symbol={investment.symbol or ''}&broker={investment.broker.id}")

@login_required
def transaction_edit(request, pk):
    """Edit a transaction."""
    txn = get_object_or_404(InvestmentTransaction, pk=pk, investment__user=request.user)
    investment = txn.investment
    
    if request.method == 'POST':
        form = InvestmentTransactionForm(request.POST, instance=txn)
        if form.is_valid():
            try:
                form.save()
                log_activity(request.user, 'updated', txn, request=request)
                messages.success(request, "Transaction updated successfully.")
                return redirect('investments:investment_detail', pk=investment.pk)
            except Exception as e:
                messages.error(request, f"Error updating transaction: {str(e)}")
    else:
        form = InvestmentTransactionForm(instance=txn)
    
    return render(request, 'investments/investment_form.html', {
        'form': form, 
        'title': f'Edit Transaction - {investment.name}',
        'investment': investment
    })

@login_required
def transaction_delete(request, pk):
    """Delete a transaction."""
    txn = get_object_or_404(InvestmentTransaction, pk=pk, investment__user=request.user)
    investment = txn.investment
    
    if request.method == 'POST':
        log_activity(request.user, 'deleted', txn, request=request)
        txn.delete()
        
        # Check if any transactions remain
        if investment.transactions.count() == 0:
            investment_name = investment.name
            investment.delete()
            messages.success(request, f"Transaction deleted. Investment '{investment_name}' was also deleted as it had no remaining transactions.")
            return redirect('investments:investment_list')
            
        messages.success(request, "Transaction deleted successfully.")
        return redirect('investments:investment_detail', pk=investment.pk)
        
    return render(request, 'investments/transaction_confirm_delete.html', {'transaction': txn})
