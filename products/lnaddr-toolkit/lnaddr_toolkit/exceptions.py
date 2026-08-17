"""Custom exceptions for lnaddr-toolkit."""


class LNAddressError(Exception):
    """Base exception for all lnaddr-toolkit errors."""
    pass


class ValidationError(LNAddressError):
    """Raised when a Lightning Address fails validation."""
    pass


class ResolutionError(LNAddressError):
    """Raised when Lightning Address resolution fails."""
    pass


class InvoiceError(LNAddressError):
    """Raised when invoice creation fails."""
    pass