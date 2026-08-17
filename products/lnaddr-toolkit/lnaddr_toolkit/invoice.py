"""Invoice creation via LNURL-pay callback.

Given a resolved LNURLPayMetadata and an amount, request a BOLT11 invoice
from the callback endpoint.
"""

import requests
from dataclasses import dataclass
from typing import Optional

from .exceptions import InvoiceError
from .resolver import LNURLPayMetadata


@dataclass
class InvoiceResponse:
    """Response from LNURL-pay callback."""
    pr: str  # BOLT11 invoice
    routes: Optional[list] = None  # Optional route hints
    success_action: Optional[dict] = None  # Optional success action (URL, message, etc.)

    @property
    def invoice(self) -> str:
        """Alias for pr (BOLT11 invoice)."""
        return self.pr


def create_invoice_for_amount(
    metadata: LNURLPayMetadata,
    amount_msat: int,
    comment: Optional[str] = None,
    nostr: Optional[str] = None,
    timeout: int = 15,
    session: Optional[requests.Session] = None
) -> InvoiceResponse:
    """
    Request a BOLT11 invoice from an LNURL-pay callback.

    Args:
        metadata: LNURLPayMetadata from resolve_lightning_address()
        amount_msat: Amount in millisatoshis (must be within min/max sendable)
        comment: Optional comment (must be <= comment_allowed chars)
        nostr: Optional Nostr event for Nostr-enabled LNURL-pay
        timeout: Request timeout in seconds
        session: Optional requests.Session for connection pooling

    Returns:
        InvoiceResponse with BOLT11 invoice and optional routes/success_action

    Raises:
        InvoiceError: If amount is out of bounds, comment too long, or request fails
    """
    # Validate amount bounds
    if amount_msat < metadata.min_sendable:
        raise InvoiceError(
            f"Amount {amount_msat} msat below minimum {metadata.min_sendable} msat "
            f"({metadata.min_sats} sats)"
        )
    if amount_msat > metadata.max_sendable:
        raise InvoiceError(
            f"Amount {amount_msat} msat exceeds maximum {metadata.max_sendable} msat "
            f"({metadata.max_sats} sats)"
        )

    # Validate comment length
    if comment and len(comment) > metadata.comment_allowed:
        raise InvoiceError(
            f"Comment length {len(comment)} exceeds allowed {metadata.comment_allowed} characters"
        )

    # Build callback request params
    params: dict[str, str | int] = {"amount": amount_msat}
    if comment:
        params["comment"] = comment
    if nostr and metadata.allows_nostr:
        params["nostr"] = nostr

    try:
        if session:
            response = session.get(metadata.callback, params=params, timeout=timeout)
        else:
            response = requests.get(metadata.callback, params=params, timeout=timeout)

        response.raise_for_status()
        data = response.json()

        # Check for LNURL error response
        if data.get("status") == "ERROR":
            raise InvoiceError(f"LNURL error: {data.get('reason', 'Unknown error')}")

        # Validate required field
        if "pr" not in data:
            raise InvoiceError("Missing 'pr' (BOLT11 invoice) in callback response")

        return InvoiceResponse(
            pr=data["pr"],
            routes=data.get("routes"),
            success_action=data.get("successAction"),
        )

    except requests.exceptions.Timeout:
        raise InvoiceError(f"Request timeout creating invoice at {metadata.callback}")
    except requests.exceptions.ConnectionError as e:
        raise InvoiceError(f"Connection error creating invoice: {e}")
    except requests.exceptions.HTTPError as e:
        raise InvoiceError(f"HTTP error creating invoice: {e.response.status_code} {e.response.reason}")
    except ValueError as e:
        raise InvoiceError(f"Invalid JSON response from callback: {e}")
    except KeyError as e:
        raise InvoiceError(f"Malformed callback response: missing {e}")


def create_invoice_for_sats(
    metadata: LNURLPayMetadata,
    amount_sats: int,
    comment: Optional[str] = None,
    nostr: Optional[str] = None,
    timeout: int = 15,
    session: Optional[requests.Session] = None
) -> InvoiceResponse:
    """
    Convenience wrapper: create invoice for amount in satoshis (converts to msat).

    Args:
        metadata: LNURLPayMetadata from resolve_lightning_address()
        amount_sats: Amount in satoshis
        comment: Optional comment
        nostr: Optional Nostr event
        timeout: Request timeout in seconds
        session: Optional requests.Session

    Returns:
        InvoiceResponse
    """
    return create_invoice_for_amount(
        metadata, amount_sats * 1000, comment, nostr, timeout, session
    )