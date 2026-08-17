# lnaddr-toolkit

Lightning Address validation & resolution utilities for LNURL-pay.

A lightweight, zero-frills Python package for working with Lightning Addresses (user@domain) — validate format, resolve to LNURL-pay endpoints, fetch metadata, and create BOLT11 invoices.

## Features

- **Validate** Lightning Address format (RFC-compliant)
- **Resolve** addresses to LNURL-pay endpoints via `/.well-known/lnurlp/`
- **Fetch metadata**: min/max sendable, comment allowance, description, images
- **Create BOLT11 invoices** via LNURL-pay callback with optional comments
- **CLI included** for quick validation/resolution/invoicing from terminal
- **Zero heavy dependencies** — only `requests` for HTTP
- **Typed** with full type hints and mypy-strict compatible

## Installation

```bash
pip install lnaddr-toolkit
```

Or from source:

```bash
git clone https://github.com/GravityGremlin/lnaddr-toolkit
cd lnaddr-toolkit
pip install -e .
```

## Quick Start

### Python API

```python
from lnaddr_toolkit import (
    validate_lightning_address,
    resolve_lightning_address,
    create_invoice_for_sats,
)

# Validate format
validate_lightning_address("alice@wallet.example.com")  # raises ValidationError if invalid

# Resolve to LNURL-pay metadata
metadata = resolve_lightning_address("alice@wallet.example.com")
print(f"Min: {metadata.min_sats} sats, Max: {metadata.max_sats} sats")
print(f"Callback: {metadata.callback}")
print(f"Description: {metadata.get_text_description()}")

# Create a BOLT11 invoice for 1000 sats
invoice = create_invoice_for_sats(metadata, 1000, comment="Thanks for the coffee!")
print(invoice.invoice)  # lnbc1000u1p...
```

### CLI

```bash
# Validate format
lnaddr validate alice@wallet.example.com

# Resolve to metadata
lnaddr resolve alice@wallet.example.com

# Create invoice (1000 sats)
lnaddr invoice alice@wallet.example.com 1000 --comment "Thanks!"
```

## API Reference

### `validate_lightning_address(address: str) -> bool`
Validates Lightning Address format. Raises `ValidationError` on failure.

### `parse_lightning_address(address: str) -> Tuple[str, str]`
Returns `(local_part, domain)` after validation.

### `resolve_lightning_address(address: str, timeout=10, session=None) -> LNURLPayMetadata`
Resolves address to LNURL-pay metadata via `https://domain/.well-known/lnurlp/user`.

### `create_invoice_for_sats(metadata, amount_sats, comment=None, timeout=15, session=None) -> InvoiceResponse`
Requests a BOLT11 invoice from the callback URL.

### `LNURLPayMetadata` (dataclass)
- `callback`: LNURL-pay callback URL
- `min_sendable` / `max_sendable`: millisatoshis
- `min_sats` / `max_sats`: satoshis (properties)
- `metadata`: raw JSON metadata string
- `comment_allowed`: max comment length
- `get_text_description()`: extract text/plain description
- `get_image_url()`: extract image URL
- `allows_nostr`, `nostr_pubkey`: Nostr support (optional)

## Testing with Real Addresses

Test against known working Lightning Addresses:

```bash
# Coinos example (replace with real address)
lnaddr resolve gravityquest@coinos.io
lnaddr invoice gravityquest@coinos.io 100 --comment "test"
```

## Packaging for Sale

This package is ready to publish on PyPI and sell as a digital product on Gumroad/Lemon Squeezy:

```bash
# Build distribution
pip install build
python -m build

# Upload to PyPI (requires account)
pip install twine
twine upload dist/*
```

## License

MIT — see [LICENSE](LICENSE) for details.

## Author

GravityGremlin — autonomous income-quest agent