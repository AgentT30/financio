"""
Custom template filters for Indian number formatting.
"""
from django import template
from decimal import Decimal

register = template.Library()


@register.filter(name='indian_format')
def indian_format(value, decimals=2):
    """
    Format a number using Indian numbering system (X,XX,XXX).

    Args:
        value: Number to format
        decimals: Number of decimal places (default 2, use 0 for no decimals)

    Examples:
        1000 -> 1,000.00
        10000 -> 10,000.00
        100000 -> 1,00,000.00
        100000|indian_format:0 -> 1,00,000
    """
    if value is None:
        return ''

    try:
        # Convert decimals to int
        decimals = int(decimals) if decimals is not None else 2

        # Convert to string and handle decimals
        if isinstance(value, (int, float, Decimal)):
            # Round to specified decimal places
            if decimals == 0:
                value = round(float(value))
                str_value = str(int(value))
                dec_part = None
            else:
                value = round(float(value), decimals)
                str_value = str(value)
                if '.' in str_value:
                    int_part, dec_part = str_value.split('.')
                    # Pad or truncate to specified decimal places
                    dec_part = dec_part[:decimals].ljust(decimals, '0')
                else:
                    int_part = str_value
                    dec_part = '0' * decimals
                str_value = int_part
        else:
            str_value = str(value)
            dec_part = None

        int_part = str_value

        # Remove any existing commas
        int_part = int_part.replace(',', '')

        # Handle negative numbers
        is_negative = int_part.startswith('-')
        if is_negative:
            int_part = int_part[1:]

        # Format using Indian numbering system
        if len(int_part) <= 3:
            formatted = int_part
        else:
            # Last 3 digits
            last_three = int_part[-3:]
            remaining = int_part[:-3]

            # Add commas every 2 digits from right to left
            groups = []
            while remaining:
                if len(remaining) <= 2:
                    groups.append(remaining)
                    break
                else:
                    groups.append(remaining[-2:])
                    remaining = remaining[:-2]

            # Reverse and join
            groups.reverse()
            formatted = ','.join(groups) + ',' + last_three

        # Add negative sign back if needed
        if is_negative:
            formatted = '-' + formatted

        # Add decimal part if specified
        if dec_part is not None and decimals > 0:
            return f"{formatted}.{dec_part}"
        else:
            return formatted

    except (ValueError, TypeError):
        return value
