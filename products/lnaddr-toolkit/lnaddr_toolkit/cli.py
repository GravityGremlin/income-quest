"""Command-line interface for lnaddr-toolkit."""

import sys
from argparse import ArgumentParser, Namespace

from . import (
    validate_lightning_address,
    parse_lightning_address,
    resolve_lightning_address,
    create_invoice_for_sats,
    ValidationError,
    ResolutionError,
    InvoiceError,
)


def cmd_validate(args: Namespace) -> int:
    """Validate a Lightning Address."""
    try:
        validate_lightning_address(args.address)
        local, domain = parse_lightning_address(args.address)
        print(f"✓ Valid: {args.address}")
        print(f"  Local part: {local}")
        print(f"  Domain: {domain}")
        return 0
    except ValidationError as e:
        print(f"✗ Invalid: {e}", file=sys.stderr)
        return 1


def cmd_resolve(args: Namespace) -> int:
    """Resolve a Lightning Address to LNURL-pay metadata."""
    try:
        metadata = resolve_lightning_address(args.address, timeout=args.timeout)
        print(f"✓ Resolved: {args.address}")
        print(f"  Callback: {metadata.callback}")
        print(f"  Min sendable: {metadata.min_sats} sats ({metadata.min_sendable} msat)")
        print(f"  Max sendable: {metadata.max_sats} sats ({metadata.max_sendable} msat)")
        print(f"  Comment allowed: {metadata.comment_allowed} chars")
        print(f"  Tag: {metadata.tag}")
        if metadata.allows_nostr:
            print(f"  Nostr enabled: yes (pubkey: {metadata.nostr_pubkey})")
        desc = metadata.get_text_description()
        if desc:
            print(f"  Description: {desc}")
        img = metadata.get_image_url()
        if img:
            print(f"  Image: {img}")
        return 0
    except (ValidationError, ResolutionError) as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def cmd_invoice(args: Namespace) -> int:
    """Create a BOLT11 invoice for a Lightning Address."""
    try:
        metadata = resolve_lightning_address(args.address, timeout=args.timeout)
        invoice_resp = create_invoice_for_sats(
            metadata, args.amount, comment=args.comment, timeout=args.timeout
        )
        print(f"✓ Invoice created for {args.amount} sats to {args.address}")
        print(f"  BOLT11: {invoice_resp.invoice}")
        if invoice_resp.routes:
            print(f"  Routes: {len(invoice_resp.routes)} route hint(s)")
        if invoice_resp.success_action:
            print(f"  Success action: {invoice_resp.success_action}")
        return 0
    except (ValidationError, ResolutionError, InvoiceError) as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = ArgumentParser(
        prog="lnaddr",
        description="Lightning Address validation & resolution toolkit",
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1.0")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # validate command
    p_validate = subparsers.add_parser("validate", help="Validate Lightning Address format")
    p_validate.add_argument("address", help="Lightning Address (e.g., user@domain.com)")
    p_validate.set_defaults(func=cmd_validate)

    # resolve command
    p_resolve = subparsers.add_parser("resolve", help="Resolve to LNURL-pay metadata")
    p_resolve.add_argument("address", help="Lightning Address (e.g., user@domain.com)")
    p_resolve.add_argument("-t", "--timeout", type=int, default=10, help="Request timeout (seconds)")
    p_resolve.set_defaults(func=cmd_resolve)

    # invoice command
    p_invoice = subparsers.add_parser("invoice", help="Create BOLT11 invoice")
    p_invoice.add_argument("address", help="Lightning Address (e.g., user@domain.com)")
    p_invoice.add_argument("amount", type=int, help="Amount in satoshis")
    p_invoice.add_argument("-c", "--comment", help="Optional comment for payment")
    p_invoice.add_argument("-t", "--timeout", type=int, default=15, help="Request timeout (seconds)")
    p_invoice.set_defaults(func=cmd_invoice)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())