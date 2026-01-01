from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from transactions.models import Transaction

class ReportService:
    """
    Service for generating financial reports and analytics data.
    """

    @staticmethod
    def get_monthly_cashflow(user, months_count=6):
        """
        Calculates monthly income and expense totals for the last N months.
        Uses only standard library to avoid dependency issues.
        
        Returns:
            dict: {
                'labels': ['Month Year', ...],
                'income': [total, ...],
                'expense': [total, ...]
            }
        """
        now = timezone.now()
        
        labels = []
        income_data = []
        expense_data = []
        
        # Current month and year
        curr_month = now.month
        curr_year = now.year
        
        # Iterate backwards for the specified number of months
        for i in range(months_count - 1, -1, -1):
            # Calculate month and year for i months ago
            target_month = curr_month - i
            target_year = curr_year
            
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            
            month_start = datetime(target_year, target_month, 1)
            
            # Calculate end of month
            if target_month == 12:
                next_month_start = datetime(target_year + 1, 1, 1)
            else:
                next_month_start = datetime(target_year, target_month + 1, 1)
            
            month_end = next_month_start - timedelta(seconds=1)
            
            # Month label (e.g., "Oct 2025")
            labels.append(month_start.strftime('%b %Y'))
            
            # Aggregate income
            income = Transaction.objects.filter(
                user=user,
                transaction_type='income',
                datetime_ist__range=(month_start, month_end),
                deleted_at__isnull=True
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Aggregate expense
            expense = Transaction.objects.filter(
                user=user,
                transaction_type='expense',
                datetime_ist__range=(month_start, month_end),
                deleted_at__isnull=True
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            income_data.append(float(income))
            expense_data.append(float(expense))
            
        return {
            'labels': labels,
            'income': income_data,
            'expense': expense_data
        }

    @staticmethod
    def get_expense_breakdown(user):
        """
        Calculates expense totals per category for the current month.
        
        Returns:
            dict: {
                'labels': ['Category Name', ...],
                'data': [total, ...],
                'colors': ['#hex', ...]
            }
        """
        now = timezone.now()
        month_start = datetime(now.year, now.month, 1)
        
        # Aggregate expenses by category
        expenses = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            datetime_ist__gte=month_start,
            deleted_at__isnull=True
        ).values('category__name', 'category__color').annotate(total=Sum('amount')).order_by('-total')
        
        labels = []
        data = []
        colors = []
        
        # Default colors if category color is missing
        default_colors = [
            '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', 
            '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
        ]
        
        for i, exp in enumerate(expenses):
            labels.append(exp['category__name'].title() if exp['category__name'] else 'Uncategorized')
            data.append(float(exp['total']))
            colors.append(exp['category__color'] or default_colors[i % len(default_colors)])
            
        return {
            'labels': labels,
            'data': data,
            'colors': colors
        }

    @staticmethod
    def get_net_worth_trend(user, months_count=6):
        """
        Calculates net worth trend for the last N months.
        Net Worth = Bank Balances + FD Maturity Amounts + Investment Values.
        """
        from accounts.models import BankAccount
        from fds.models import FixedDeposit
        from investments.models import Investment, InvestmentTransaction
        from ledger.models import Posting
        from django.db.models.functions import Coalesce
        from decimal import Decimal

        now = timezone.now()
        labels = []
        data = []

        # Current month and year
        curr_month = now.month
        curr_year = now.year

        for i in range(months_count - 1, -1, -1):
            # Calculate target month/year
            target_month = curr_month - i
            target_year = curr_year
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            
            # End of target month
            if target_month == 12:
                next_month_start = datetime(target_year + 1, 1, 1)
            else:
                next_month_start = datetime(target_year, target_month + 1, 1)
            month_end = next_month_start - timedelta(seconds=1)
            
            labels.append(month_end.strftime('%b %Y'))

            # 1. Bank Balances
            # Sum of opening balances + all postings up to month_end
            opening_balances = BankAccount.objects.filter(
                user=user, 
                created_at__lte=month_end
            ).aggregate(total=Sum('opening_balance'))['total'] or Decimal('0')
            
            postings_sum = Posting.objects.filter(
                journal_entry__user=user,
                journal_entry__occurred_at__lte=month_end,
                account_content_type__model='bankaccount'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            bank_total = opening_balances + postings_sum

            # 2. FD Values (Maturity Amount of active FDs at that time)
            fd_total = FixedDeposit.objects.filter(
                user=user,
                opened_on__lte=month_end.date(),
            ).filter(
                Q(status='active') | Q(maturity_date__gt=month_end.date())
            ).aggregate(total=Sum('maturity_amount'))['total'] or Decimal('0')

            # 3. Investment Values
            # If it's the current month, use current market value. 
            # Otherwise, use cost basis (invested amount) as historical price is unknown.
            if i == 0:
                # Current month: Use current_price * quantity
                investments = Investment.objects.filter(user=user, status='active')
                inv_total = sum(inv.current_value for inv in investments)
            else:
                # Past months: Use sum of transactions up to that date
                inv_total = InvestmentTransaction.objects.filter(
                    investment__user=user,
                    date__lte=month_end.date()
                ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

            data.append(float(bank_total + fd_total + inv_total))

        return {
            'labels': labels,
            'data': data
        }
