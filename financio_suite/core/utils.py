"""
Utility functions for the core app.
"""
from django.contrib.contenttypes.models import ContentType


def get_all_accounts_with_emoji(user):
    """
    Returns a combined list of all accounts (banks + credit cards) with emoji prefixes.
    
    Args:
        user: User object to filter accounts by
        
    Returns:
        List of tuples: [(account_object, display_string, compound_value), ...]
        - account_object: The actual account instance (BankAccount or CreditCard)
        - display_string: Formatted string with emoji for display
        - compound_value: "id|model_name" for form value (e.g., "1|bankaccount")
        
    Format: "[Emoji] Account Name (Institution/Type)"
    Examples:
        - "🏦 HDFC Savings (HDFC Bank)"
        - "💳 HDFC Regalia (Credit Card)"
    """
    from accounts.models import BankAccount
    from creditcards.models import CreditCard
    
    accounts_list = []
    
    # Get all active bank accounts
    bank_accounts = BankAccount.objects.filter(
        user=user,
        status='active'  # Use status instead of deleted_at
    ).select_related('user')
    
    for account in bank_accounts:
        # Format: "🏦 Account Name (Institution)"
        display_name = f"🏦 {account.name} ({account.institution})"
        compound_value = f"{account.id}|bankaccount"
        accounts_list.append((account, display_name, compound_value))
    
    # Get all active credit cards
    credit_cards = CreditCard.objects.filter(
        user=user,
        status='active'  # Use status instead of deleted_at
    ).select_related('user')
    
    for card in credit_cards:
        # Format: "💳 Card Name (Credit Card)"
        display_name = f"💳 {card.name} (Credit Card)"
        compound_value = f"{card.id}|creditcard"
        accounts_list.append((card, display_name, compound_value))
    
    # Sort alphabetically by display name
    accounts_list.sort(key=lambda x: x[1])
    
    return accounts_list


def get_account_from_compound_value(compound_value, user):
    """
    Extracts and returns the actual account object from a compound value.
    
    Args:
        compound_value: String in format "id|model_name" (e.g., "1|bankaccount" or "5|creditcard")
        user: User object for security validation
        
    Returns:
        The actual account object (BankAccount or CreditCard instance)
        
    Raises:
        ValueError: If compound_value format is invalid or account not found
    """
    from accounts.models import BankAccount
    from creditcards.models import CreditCard
    
    if not compound_value or '|' not in compound_value:
        raise ValueError("Invalid account value format. Expected 'id|model_name'")
    
    try:
        account_id, model_name = compound_value.split('|', 1)
        account_id = int(account_id)
    except (ValueError, AttributeError):
        raise ValueError("Invalid account value format. Expected 'id|model_name'")
    
    # Determine which model to query based on model_name
    model_name_lower = model_name.lower()
    
    if model_name_lower == 'bankaccount':
        try:
            account = BankAccount.objects.get(
                id=account_id,
                user=user,
                status='active'  # Use status instead of deleted_at
            )
            return account
        except BankAccount.DoesNotExist:
            raise ValueError(f"Bank account with ID {account_id} not found or not accessible")
    
    elif model_name_lower == 'creditcard':
        try:
            account = CreditCard.objects.get(
                id=account_id,
                user=user,
                status='active'  # Use status instead of deleted_at
            )
            return account
        except CreditCard.DoesNotExist:
            raise ValueError(f"Credit card with ID {account_id} not found or not accessible")
    
    else:
        raise ValueError(f"Unknown account type: {model_name}")


def get_account_choices_for_form(user):
    """
    Returns choices list formatted for Django form Select widget.
    
    Args:
        user: User object to filter accounts by
        
    Returns:
        List of tuples: [(compound_value, display_string), ...]
        Suitable for use in forms.ChoiceField or forms.Select widget
    """
    accounts = get_all_accounts_with_emoji(user)
    # Return as (value, label) tuples for form choices
    return [(compound_value, display_name) for _, display_name, compound_value in accounts]
