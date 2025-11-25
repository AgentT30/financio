from decimal import Decimal
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from .models import JournalEntry, Posting, ControlAccount
from accounts.models import BankAccountBalance
from creditcards.models import CreditCardBalance


class LedgerService:
    """
    Service class for creating journal entries and updating account balances.
    Handles all ledger operations atomically.
    """
    
    @staticmethod
    @transaction.atomic
    def create_simple_entry(user, transaction_type, account, amount, occurred_at, memo, category=None):
        """
        Create a simple journal entry with 2 postings (user transaction).
        
        Args:
            user: User instance
            transaction_type: String ('income' or 'expense')
            account: Account instance (BankAccount, etc.)
            amount: Decimal amount (positive)
            occurred_at: DateTime when transaction occurred (IST)
            memo: String description
            category: Category instance (optional)
        
        Returns:
            JournalEntry: Created journal entry instance
        
        Raises:
            ValidationError: If amount <= 0 or other validation fails
        """
        if amount <= 0:
            raise ValidationError("Amount must be greater than zero")
        
        # Create journal entry
        journal_entry = JournalEntry.objects.create(
            user=user,
            occurred_at=occurred_at,
            memo=memo
        )
        
        # Get content type for user account
        account_content_type = ContentType.objects.get_for_model(account)
        
        # Get control account content type
        control_account_ct = ContentType.objects.get_for_model(ControlAccount)
        
        category_name = category.name if category else "Uncategorized"
        
        if transaction_type == 'income':
            # Income Transaction:
            # Debit: User Account (increase balance)
            # Credit: Income Control Account
            
            # Get Income Control Account
            income_control = ControlAccount.objects.get(account_type='income')
            
            # Posting 1: Debit User Account
            user_posting = Posting.objects.create(
                journal_entry=journal_entry,
                account_content_type=account_content_type,
                account_object_id=account.pk,
                amount=Decimal(str(amount)),
                posting_type='debit',
                currency='INR',
                memo=f"Income: {category_name}"
            )
            
            # Posting 2: Credit Income Control
            Posting.objects.create(
                journal_entry=journal_entry,
                account_content_type=control_account_ct,
                account_object_id=income_control.pk,
                amount=-Decimal(str(amount)),
                posting_type='credit',
                currency='INR',
                memo=f"Income: {category_name}"
            )
            
            # Update account balance (increase)
            new_balance = LedgerService._update_account_balance(
                account, 
                Decimal(str(amount)), 
                user_posting.id
            )
            
        else:  # expense
            # Expense Transaction:
            # Debit: Expense Control Account
            # Credit: User Account (decrease balance)
            
            # Get Expense Control Account
            expense_control = ControlAccount.objects.get(account_type='expense')
            
            # Posting 1: Debit Expense Control
            Posting.objects.create(
                journal_entry=journal_entry,
                account_content_type=control_account_ct,
                account_object_id=expense_control.pk,
                amount=Decimal(str(amount)),
                posting_type='debit',
                currency='INR',
                memo=f"Expense: {category_name}"
            )
            
            # Posting 2: Credit User Account
            user_posting = Posting.objects.create(
                journal_entry=journal_entry,
                account_content_type=account_content_type,
                account_object_id=account.pk,
                amount=-Decimal(str(amount)),
                posting_type='credit',
                currency='INR',
                memo=f"Expense: {category_name}"
            )
            
            # Update account balance (decrease)
            new_balance = LedgerService._update_account_balance(
                account, 
                -Decimal(str(amount)), 
                user_posting.id
            )
        
        # Validate that postings sum to zero
        journal_entry.validate_balanced()
        
        return journal_entry
    
    @staticmethod
    @transaction.atomic
    def create_transfer_entry(user, occurred_at, amount, from_account, to_account, memo):
        """
        Create a transfer journal entry (2 postings).
        
        Args:
            user: User instance
            occurred_at: DateTime when transfer occurred (IST)
            amount: Decimal amount to transfer (positive)
            from_account: Source account instance
            to_account: Destination account instance
            memo: String description
        
        Returns:
            tuple: (JournalEntry, from_balance, to_balance)
        """
        if amount <= 0:
            raise ValidationError("Transfer amount must be greater than zero")
        
        # Check if transferring to the same account (same type AND same ID)
        from_ct = ContentType.objects.get_for_model(from_account)
        to_ct = ContentType.objects.get_for_model(to_account)
        if from_ct.id == to_ct.id and from_account.pk == to_account.pk:
            raise ValidationError("Cannot transfer to the same account")
        
        # Create journal entry
        journal_entry = JournalEntry.objects.create(
            user=user,
            occurred_at=occurred_at,
            memo=f"Transfer: {memo}"
        )
        
        # Get content types
        from_ct = ContentType.objects.get_for_model(from_account)
        to_ct = ContentType.objects.get_for_model(to_account)
        
        # Posting 1: Credit FROM account (decrease balance)
        from_posting = Posting.objects.create(
            journal_entry=journal_entry,
            account_content_type=from_ct,
            account_object_id=from_account.pk,
            amount=-Decimal(str(amount)),
            posting_type='credit',
            currency='INR',
            memo=f"Transfer to {to_account.name}"
        )
        
        # Posting 2: Debit TO account (increase balance)
        to_posting = Posting.objects.create(
            journal_entry=journal_entry,
            account_content_type=to_ct,
            account_object_id=to_account.pk,
            amount=Decimal(str(amount)),
            posting_type='debit',
            currency='INR',
            memo=f"Transfer from {from_account.name}"
        )
        
        # Update balances
        from_balance = LedgerService._update_account_balance(
            from_account, 
            -Decimal(str(amount)), 
            from_posting.id
        )
        to_balance = LedgerService._update_account_balance(
            to_account, 
            Decimal(str(amount)), 
            to_posting.id
        )
        
        # Validate
        journal_entry.validate_balanced()
        
        return journal_entry, from_balance, to_balance
    
    @staticmethod
    def _create_postings_for_simple_entry(journal_entry, transaction_type, account, amount):
        """
        Helper method to create postings for a simple entry.
        Used when updating existing transactions.
        
        Args:
            journal_entry: JournalEntry instance
            transaction_type: String ('income' or 'expense')
            account: Account instance
            amount: Decimal amount (positive)
        """
        # Get content types
        account_content_type = ContentType.objects.get_for_model(account)
        control_account_ct = ContentType.objects.get_for_model(ControlAccount)
        
        if transaction_type == 'income':
            income_control = ControlAccount.objects.get(account_type='income')
            
            # Posting 1: Debit User Account
            Posting.objects.create(
                journal_entry=journal_entry,
                account_content_type=account_content_type,
                account_object_id=account.pk,
                amount=Decimal(str(amount)),
                posting_type='debit',
                currency='INR',
                memo=journal_entry.memo
            )
            
            # Posting 2: Credit Income Control
            Posting.objects.create(
                journal_entry=journal_entry,
                account_content_type=control_account_ct,
                account_object_id=income_control.pk,
                amount=-Decimal(str(amount)),
                posting_type='credit',
                currency='INR',
                memo=journal_entry.memo
            )
        else:  # expense
            expense_control = ControlAccount.objects.get(account_type='expense')
            
            # Posting 1: Debit Expense Control
            Posting.objects.create(
                journal_entry=journal_entry,
                account_content_type=control_account_ct,
                account_object_id=expense_control.pk,
                amount=Decimal(str(amount)),
                posting_type='debit',
                currency='INR',
                memo=journal_entry.memo
            )
            
            # Posting 2: Credit User Account
            Posting.objects.create(
                journal_entry=journal_entry,
                account_content_type=account_content_type,
                account_object_id=account.pk,
                amount=-Decimal(str(amount)),
                posting_type='credit',
                currency='INR',
                memo=journal_entry.memo
            )
    
    @staticmethod
    def _update_account_balance(account, delta, posting_id):
        """
        Update account balance atomically.
        Supports both BankAccount and CreditCard account types.
        
        Args:
            account: Account instance (BankAccount or CreditCard)
            delta: Decimal amount to add/subtract
            posting_id: ID of posting that caused this update
        
        Returns:
            Decimal: New balance amount
        """
        account_type = account.__class__.__name__
        
        if account_type == 'BankAccount':
            balance, created = BankAccountBalance.objects.select_for_update().get_or_create(
                account=account,
                defaults={'balance_amount': account.opening_balance}
            )
            
            balance.balance_amount += delta
            balance.last_posting_id = posting_id
            balance.save(update_fields=['balance_amount', 'last_posting_id', 'updated_at'])
            
            return balance.balance_amount
            
        elif account_type == 'CreditCard':
            balance, created = CreditCardBalance.objects.select_for_update().get_or_create(
                account=account,
                defaults={'balance_amount': account.opening_balance}
            )
            
            balance.balance_amount += delta
            balance.last_posting_id = posting_id
            balance.save(update_fields=['balance_amount', 'last_posting_id', 'updated_at'])
            
            return balance.balance_amount
            
        else:
            raise NotImplementedError(
                f"Balance updates not implemented for {account_type}"
            )
