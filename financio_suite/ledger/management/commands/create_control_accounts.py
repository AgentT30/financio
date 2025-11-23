from django.core.management.base import BaseCommand
from ledger.models import ControlAccount


class Command(BaseCommand):
    help = 'Create the two required control accounts for double-entry bookkeeping'
    
    def handle(self, *args, **options):
        # Create Income Control Account
        income_control, created = ControlAccount.objects.get_or_create(
            account_type='income',
            defaults={
                'name': 'Income Control Account',
                'description': 'Synthetic account for balancing income transactions in double-entry ledger'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created: {income_control.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Already exists: {income_control.name}'))
        
        # Create Expense Control Account
        expense_control, created = ControlAccount.objects.get_or_create(
            account_type='expense',
            defaults={
                'name': 'Expense Control Account',
                'description': 'Synthetic account for balancing expense transactions in double-entry ledger'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created: {expense_control.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'Already exists: {expense_control.name}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Control accounts ready!'))
