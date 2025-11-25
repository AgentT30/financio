"""
Management command to recalculate all account balances from ledger postings.

This command rebuilds the materialized balance tables (bank_account_balances,
credit_card_balances) by replaying all postings from the ledger. Useful for:
- Fixing balance inconsistencies
- Recovering from balance record deletions
- Verifying ledger integrity
- Testing balance calculation logic

The command:
1. Calculates correct balance: opening_balance + SUM(postings)
2. Only counts postings from active (non-deleted) transactions/transfers
3. Compares calculated balance with stored balance
4. Updates balance records if differences found
5. Optionally cleans up orphaned journal entries

Usage:
    # Preview changes without applying them
    python manage.py recalculate_balances --dry-run

    # Apply balance corrections
    python manage.py recalculate_balances

    # Also cleanup orphaned journal entries
    python manage.py recalculate_balances --cleanup-orphans
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal

from accounts.models import BankAccount, BankAccountBalance
from creditcards.models import CreditCard, CreditCardBalance
from ledger.models import Posting, JournalEntry
from transactions.models import Transaction
from transfers.models import Transfer


class Command(BaseCommand):
    help = 'Recalculate all account balances from ledger postings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually changing it',
        )
        parser.add_argument(
            '--cleanup-orphans',
            action='store_true',
            help='Also cleanup orphaned journal entries not linked to any transaction/transfer',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        cleanup_orphans = options['cleanup_orphans']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))

        # Cleanup orphaned journal entries first
        if cleanup_orphans:
            self.stdout.write(self.style.SUCCESS('Checking for orphaned journal entries...\n'))

            # Get all journal entry IDs that are linked to transactions or transfers
            linked_journal_ids = set()
            linked_journal_ids.update(
                Transaction.objects.exclude(journal_entry__isnull=True)
                .values_list('journal_entry_id', flat=True)
            )
            linked_journal_ids.update(
                Transfer.objects.exclude(journal_entry__isnull=True)
                .values_list('journal_entry_id', flat=True)
            )

            # Find orphaned journal entries
            orphaned_entries = JournalEntry.objects.exclude(id__in=linked_journal_ids)
            orphan_count = orphaned_entries.count()

            if orphan_count > 0:
                self.stdout.write(
                    self.style.WARNING(f'Found {orphan_count} orphaned journal entries:')
                )
                for entry in orphaned_entries[:10]:  # Show first 10
                    self.stdout.write(f'  - ID {entry.id}: {entry.memo} ({entry.occurred_at.date()})')

                if orphan_count > 10:
                    self.stdout.write(f'  ... and {orphan_count - 10} more')

                if not dry_run:
                    orphaned_entries.delete()
                    self.stdout.write(self.style.SUCCESS(f'✓ Deleted {orphan_count} orphaned journal entries\n'))
                else:
                    self.stdout.write(self.style.WARNING(f'Would delete {orphan_count} orphaned entries\n'))
            else:
                self.stdout.write('✓ No orphaned journal entries found\n')

        self.stdout.write('Recalculating account balances from ledger...\n')

        # Process Bank Accounts
        self.stdout.write(self.style.SUCCESS('Processing Bank Accounts:'))
        bank_content_type = ContentType.objects.get_for_model(BankAccount)

        # Get all active journal entries (linked to active transactions or transfers)
        active_journal_ids = set()
        active_journal_ids.update(
            Transaction.objects.filter(deleted_at__isnull=True)
            .exclude(journal_entry__isnull=True)
            .values_list('journal_entry_id', flat=True)
        )
        active_journal_ids.update(
            Transfer.objects.filter(deleted_at__isnull=True)
            .exclude(journal_entry__isnull=True)
            .values_list('journal_entry_id', flat=True)
        )

        for bank_account in BankAccount.objects.filter(status='active'):
            # Calculate total from postings of ACTIVE journal entries only
            postings = Posting.objects.filter(
                account_content_type=bank_content_type,
                account_object_id=bank_account.id,
                journal_entry_id__in=active_journal_ids
            )

            total_from_postings = sum(
                posting.amount for posting in postings
            ) or Decimal('0.00')

            # Expected balance = opening balance + all postings
            expected_balance = bank_account.opening_balance + total_from_postings

            # Get current balance
            try:
                balance_record = BankAccountBalance.objects.get(account=bank_account)
                current_balance = balance_record.balance_amount
            except BankAccountBalance.DoesNotExist:
                current_balance = bank_account.opening_balance
                balance_record = None

            # Check if correction needed
            if current_balance != expected_balance:
                self.stdout.write(
                    f'  🏦 {bank_account.name}:'
                )
                self.stdout.write(
                    f'     Current: ₹{current_balance:,.2f} → Expected: ₹{expected_balance:,.2f} '
                    f'(Diff: ₹{expected_balance - current_balance:,.2f})'
                )

                if not dry_run:
                    # Get last posting for this account
                    last_posting = postings.order_by('-id').first()

                    if balance_record:
                        balance_record.balance_amount = expected_balance
                        if last_posting:
                            balance_record.last_posting_id = last_posting.id
                        balance_record.save()
                    else:
                        BankAccountBalance.objects.create(
                            account=bank_account,
                            balance_amount=expected_balance,
                            last_posting_id=last_posting.id if last_posting else None
                        )
                    self.stdout.write(self.style.SUCCESS('     ✓ Fixed'))
            else:
                self.stdout.write(
                    f'  🏦 {bank_account.name}: ₹{current_balance:,.2f} ✓'
                )

        # Process Credit Cards
        self.stdout.write(self.style.SUCCESS('\nProcessing Credit Cards:'))
        creditcard_content_type = ContentType.objects.get_for_model(CreditCard)

        for credit_card in CreditCard.objects.filter(status='active'):
            # Calculate total from postings of ACTIVE journal entries only
            postings = Posting.objects.filter(
                account_content_type=creditcard_content_type,
                account_object_id=credit_card.id,
                journal_entry_id__in=active_journal_ids
            )

            total_from_postings = sum(
                posting.amount for posting in postings
            ) or Decimal('0.00')

            # Expected balance = opening balance + all postings
            expected_balance = credit_card.opening_balance + total_from_postings

            # Get current balance
            try:
                balance_record = CreditCardBalance.objects.get(account=credit_card)
                current_balance = balance_record.balance_amount
            except CreditCardBalance.DoesNotExist:
                current_balance = credit_card.opening_balance
                balance_record = None

            # Check if correction needed
            if current_balance != expected_balance:
                card_display = credit_card.name or f"Card ending {credit_card.card_number_last4}"
                self.stdout.write(
                    f'  💳 {card_display}:'
                )
                self.stdout.write(
                    f'     Current: ₹{current_balance:,.2f} → Expected: ₹{expected_balance:,.2f} '
                    f'(Diff: ₹{expected_balance - current_balance:,.2f})'
                )

                if not dry_run:
                    # Get last posting for this account
                    last_posting = postings.order_by('-id').first()

                    if balance_record:
                        balance_record.balance_amount = expected_balance
                        if last_posting:
                            balance_record.last_posting_id = last_posting.id
                        balance_record.save()
                    else:
                        CreditCardBalance.objects.create(
                            account=credit_card,
                            balance_amount=expected_balance,
                            last_posting_id=last_posting.id if last_posting else None
                        )
                    self.stdout.write(self.style.SUCCESS('     ✓ Fixed'))
            else:
                card_display = credit_card.name or f"Card ending {credit_card.card_number_last4}"
                self.stdout.write(
                    f'  💳 {card_display}: ₹{current_balance:,.2f} ✓'
                )

        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠ DRY RUN - No changes were saved'))
            self.stdout.write('Run without --dry-run to apply changes')
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ Balance recalculation complete!'))
