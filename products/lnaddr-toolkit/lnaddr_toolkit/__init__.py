"""
lnaddr-toolkit: Lightning Address validation & resolution utilities.

A lightweight, zero-dependency Python package for:
- Validating Lightning Address format (user@domain)
- Resolving Lightning Addresses to LNURL-pay endpoints
- Fetching pay metadata (min/max sendable, comment allowance, etc.)
- Generating BOLT11 invoices for a given amount
"""

from .validator import validate_lightning_address, parse_lightning_address
from .resolver import resolve_lightning_address, fetch_lnurl_pay_metadata
from .invoice import create_invoice_for_amount
from .exceptions import LNAddressError, ValidationError, ResolutionError, InvoiceError

__version__ = "0.1.0"
__author__ = "GravityGremlin"
__license__ = "MIT"

__all__ = [
    "validate_lightning_address",
    "parse_lightning_address",
    "resolve_lightning_address",
    "fetch_lnurl_pay_metadata",
    "create_invoice_for_amount",
    "LNAddressError",
    "ValidationError",
    "ResolutionError",
    "InvoiceError",
]