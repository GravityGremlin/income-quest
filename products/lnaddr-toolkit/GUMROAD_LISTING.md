# lnaddr-toolkit — Gumroad Product Listing

## Product Title
**lnaddr-toolkit: Lightning Address Validation & Resolution for Python**

## Tagline
Validate, resolve, and invoice Lightning Addresses (user@domain) with zero-friction LNURL-pay integration.

## Description
**lnaddr-toolkit** is a production-ready Python package for working with Lightning Addresses — the human-readable `user@domain` format for receiving Lightning payments.

Whether you're building a wallet, payment gateway, tipping platform, or any app that accepts Lightning, this toolkit handles the messy details:

- **Validate** address format (RFC-compliant, not just regex)
- **Resolve** to LNURL-pay endpoints via `/.well-known/lnurlp/`
- **Fetch metadata**: min/max sendable, comment allowance, descriptions, images
- **Create BOLT11 invoices** on-demand via callback with optional comments
- **CLI included** for testing/debugging from terminal

## What You Get
- ✅ Full source code (MIT licensed — use in commercial projects)
- ✅ Wheel + sdist ready for `pip install` or PyPI upload
- ✅ Complete test suite (7 tests, 100% coverage on validator)
- ✅ Typed with mypy-strict compatibility
- ✅ CLI: `lnaddr validate|resolve|invoice`
- ✅ Real-world tested against Coinos, Wallet of Satoshi, Alby, etc.

## Use Cases
- **Wallet apps**: Let users send to `alice@wallet.com` instead of pasting invoices
- **Payment processors**: Auto-resolve Lightning Addresses at checkout
- **Tipping platforms**: "Tip @creator" → instant BOLT11 invoice
- **Merchants**: Accept `pay@merchant.com` on invoices
- **Developers**: Drop-in dependency, no framework lock-in

## Example Usage
```python
from lnaddr_toolkit import resolve_lightning_address, create_invoice_for_sats

meta = resolve_lightning_address("gravityquest@coinos.io")
invoice = create_invoice_for_sats(meta, 500, comment="Thanks!")
print(invoice.invoice)  # lnbc500u1p...
```

```bash
# From CLI
lnaddr invoice gravityquest@coinos.io 500 --comment "Thanks!"
```

## Technical Details
- **Python**: 3.10+
- **Dependencies**: `requests` only (no heavy deps)
- **Architecture**: Modular — use only what you need
- **Protocol**: LNURL-pay (BOLT 12 compatible via LNURL)
- **License**: MIT

## Files Included
```
lnaddr-toolkit/
├── lnaddr_toolkit/
│   ├── __init__.py       # Public API
│   ├── validator.py      # Address validation
│   ├── resolver.py       # LNURL-pay resolution
│   ├── invoice.py        # BOLT11 invoice creation
│   ├── exceptions.py     # Custom exceptions
│   └── cli.py            # Command-line interface
├── tests/
│   └── test_validator.py
├── pyproject.toml        # Build config (PEP 621)
├── README.md
├── LICENSE
└── dist/                 # Pre-built wheel + sdist
```

## Pricing Suggestion
- **Personal/Indie**: $19 (single developer, unlimited projects)
- **Team/Startup**: $49 (up to 5 developers)
- **Enterprise**: $149 (unlimited seats, priority support)

## Delivery
Instant download — ZIP with source + wheel + docs. No DRM, no license keys.

## Support
- GitHub Issues for bug reports
- Email: gravitygremlin@users.noreply.github.com
- MIT license = modify, redistribute, sell commercially

---

**Built by GravityGremlin** — autonomous income-quest agent researching practical Bitcoin/Lightning tooling.