"""Lightning Address validation utilities.

A Lightning Address has the format: user@domain
Where:
- user: alphanumeric, dots, hyphens, underscores (similar to email local-part)
- domain: valid hostname (RFC 1123)
"""

import re
from typing import Tuple

from .exceptions import ValidationError


# RFC 5322-inspired local-part regex (simplified for LN addresses)
# LN addresses typically allow: alphanumeric, dot, hyphen, underscore
LOCAL_PART_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$')

# Hostname pattern (RFC 1123)
HOSTNAME_PATTERN = re.compile(
    r'^(?=.{1,253}$)(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
)

# Full Lightning Address pattern
LN_ADDRESS_PATTERN = re.compile(
    r'^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}@'
    r'(?=.{1,253}$)(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
)


def validate_lightning_address(address: str) -> bool:
    """
    Validate a Lightning Address format.

    Args:
        address: Lightning Address string (e.g., "user@domain.com")

    Returns:
        True if valid, False otherwise

    Raises:
        ValidationError: If address is invalid (with details)
    """
    if not address or not isinstance(address, str):
        raise ValidationError("Lightning address must be a non-empty string")

    address = address.strip().lower()

    if not LN_ADDRESS_PATTERN.match(address):
        raise ValidationError(
            f"Invalid Lightning Address format: '{address}'. "
            f"Expected format: user@domain (e.g., alice@wallet.example.com)"
        )

    local_part, domain = address.split('@', 1)

    # Additional local-part validation
    if not LOCAL_PART_PATTERN.match(local_part):
        raise ValidationError(
            f"Invalid local part: '{local_part}'. "
            f"Must be 1-64 chars: alphanumeric, dot, hyphen, underscore"
        )

    # Additional domain validation
    if not HOSTNAME_PATTERN.match(domain):
        raise ValidationError(f"Invalid domain: '{domain}'")

    # Check for consecutive dots in local part
    if '..' in local_part:
        raise ValidationError(f"Local part cannot contain consecutive dots: '{local_part}'")

    # Check for leading/trailing dots in local part
    if local_part.startswith('.') or local_part.endswith('.'):
        raise ValidationError(f"Local part cannot start or end with dot: '{local_part}'")

    return True


def parse_lightning_address(address: str) -> Tuple[str, str]:
    """
    Parse a Lightning Address into (local_part, domain).

    Args:
        address: Validated Lightning Address string

    Returns:
        Tuple of (local_part, domain)

    Raises:
        ValidationError: If address is invalid
    """
    validate_lightning_address(address)
    local_part, domain = address.strip().lower().split('@', 1)
    return local_part, domain


def is_valid_lightning_address(address: str) -> bool:
    """
    Check if a Lightning Address is valid (no exception raised).

    Args:
        address: Lightning Address string

    Returns:
        True if valid, False otherwise
    """
    try:
        validate_lightning_address(address)
        return True
    except ValidationError:
        return False