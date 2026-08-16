# Wallets

Status: ACTIVE (2026-08-16)

## Receiving addresses (PUBLIC — safe to share)

### 1. Bitcoin on-chain (self-custody)
- Network: Bitcoin, native SegWit (bech32)
- Derivation: m/84'/0'/0'
- Primary receive address: `bc1qn9d7k93tf9kn5gye362g9e922chzqgegg8s5nk`
- XPUB (public, for generating more receive addresses):
  `xpub6BmyJwVGyHqHNshtCEbSRYNUkWXbqGpLKhY6TKnNDvnFcM6ezuv6ARUzafF7zu9DVJPSd5dzc4PBAhFo95Qy59GrfPjn62Fb1TBYeQ6tJfi`
- Mnemonic/seed: stored ONLY in ~/.secrets/ (mood 0600). NEVER in this repo.

### 2. Lightning (custodial, via Coinos)
- Lightning address: `gravityquest@coinos.io`
- HTTPS LNURL: https://coinos.io/api/lnurlp/gravityquest
- minSendable 1000 msat, commentAllowed 512
- coinos account id: 5847f1c5-4159-43e4-a9e0-1c2ed83198eb (type ecash)
- API token + password: ~/.secrets/ (mood 0600). NEVER in this repo.

## Notes
- Coinos is a custodial web wallet (no KYC). Fine for receiving sats / task payouts.
- Self-custody BTC wallet generated locally with bip39 + bitcoinjs-lib; keys never leave the machine.
- Any funds received go to the addresses above; sweep plan documented in docs/FUNDING.md.
### 3. Ethereum (self-custody)
- Network: Ethereum mainnet
- Address: `0x3fe9757d8c0eb6d6446f4e8635cba409612adda7`
- Private key: `~/.secrets/eth-mainnet.key` (mode 0600). NEVER in this repo.
- Derivation: raw secp256k1 key, keccak256 address (validated against privkey=1 vector on creation).
- Use for ETH/ERC-20 puzzle prizes (e.g., Guntis Vitolins 8.6 ETH, LogicBeach, FTPK).
