from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()


@register.filter
def get_account(transaction):
    """Get the account name from a transaction's GenericForeignKey."""
    if transaction.account_content_type and transaction.account_object_id:
        try:
            account = transaction.account_content_type.get_object_for_this_type(
                pk=transaction.account_object_id
            )
            return account.name if hasattr(account, 'name') else str(account)
        except Exception:
            return "Unknown"
    return "Unknown"


@register.filter
def get_transfer_from_account(transfer):
    """Get the from_account name from a transfer's GenericForeignKey."""
    if transfer.from_account_content_type and transfer.from_account_object_id:
        try:
            account = transfer.from_account_content_type.get_object_for_this_type(
                pk=transfer.from_account_object_id
            )
            return account.name if hasattr(account, 'name') else str(account)
        except Exception:
            return "Unknown"
    return "Unknown"


@register.filter
def get_transfer_to_account(transfer):
    """Get the to_account name from a transfer's GenericForeignKey."""
    if transfer.to_account_content_type and transfer.to_account_object_id:
        try:
            account = transfer.to_account_content_type.get_object_for_this_type(
                pk=transfer.to_account_object_id
            )
            return account.name if hasattr(account, 'name') else str(account)
        except Exception:
            return "Unknown"
    return "Unknown"


@register.filter
def is_outgoing_transfer(transfer, account):
    """Check if a transfer is outgoing from the given account."""
    try:
        account_content_type = ContentType.objects.get_for_model(account)
        return (transfer.from_account_content_type.id == account_content_type.id and 
                transfer.from_account_object_id == account.id)
    except Exception:
        return False


@register.filter
def ordinal(value):
    """Convert an integer to its ordinal string representation (e.g., 1 -> '1st', 2 -> '2nd')."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value
    
    # Special cases for 11, 12, 13
    if 10 <= value % 100 <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(value % 10, 'th')
    
    return f"{value}{suffix}"
