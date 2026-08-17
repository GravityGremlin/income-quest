# Lightning Network Liquidity Ads & Routing Fees — Income Research

**Category:** Staking/yield (research only, no funds to stake)
**Date:** 2026-08-17
**Objective:** Document actionable pathways to earn BTC via LN routing fees and liquidity ads

---

## 1. Lightning Network Income Mechanisms

### A. Routing Fees (Node Operation)
- **How it works:** Run a Lightning node, route payments for others, collect fees (base fee + fee rate)
- **Typical earnings:** Highly variable. Well-connected nodes on main routes: 1,000–100,000+ sats/month. Most nodes: <100 sats/month.
- **Requirements:** 
  - 24/7 uptime (VPS ~$5-20/mo)
  - Capital for channels (inbound + outbound liquidity)
  - Technical skills: LND/CLN/Eclair, channel management, rebalancing
- **Tools:** `lncli`, `lightning-cli`, `amboss.space`, `1ml.com`, `terminal.web` for monitoring

### B. Liquidity Ads (BOLT 12 / LND Native)
- **What:** Nodes advertise willingness to accept inbound channels for a fee
- **Protocol:** Defined in BOLT proposals; implemented in LND v0.15+
- **How to earn:** Set `liquidityad` parameters in LND config → remote peers can "buy" inbound liquidity
- **Fee structure:** 
  - `amboss` (base fee in sats for 0-conf channel)
  - `fee_rate` (proportional fee in ppm)
  - `min_size` / `max_size` (channel size bounds)
- **Current adoption:** Low-medium. Most liquidity still sourced via Lightning Pool (off-chain marketplace)

### C. Lightning Pool (Off-chain Marketplace)
- **What:** Order book for buying/selling inbound liquidity (Lightning Labs product)
- **How to earn:** Sell side — provide inbound liquidity, collect premium + routing fees
- **Typical rates:** 0.1%–1% per month (100–1000 ppm annualized)
- **Requirements:** LND node, Pool client, capital to lease
- **Risk:** Capital locked during lease (1–30 days typically), counterparty risk minimal (HTLC-based)

### D. Loop / Swap Services (Arbitrage)
- **Loop In:** Swap on-chain BTC → inbound LN liquidity (pay fee)
- **Loop Out:** Swap outbound LN → on-chain BTC (collect fee as provider)
- **Not directly accessible** to individual node operators (run by Lightning Labs)

---

## 2. Actionable Setup Guide (LND v0.18+)

### Prerequisites
```bash
# VPS: 2 CPU, 4GB RAM, 100GB SSD (~$10-15/mo)
# OS: Ubuntu 22.04/24.04
# Bitcoin Core (pruned) + LND
```

### Enable Liquidity Ads in LND
```ini
# lnd.conf
[Application Options]
# Enable liquidity ads
liquidityad.amboss=1000        # Base fee: 1000 sats (adjust per market)
liquidityad.fee_rate=50        # Fee rate: 50 ppm (0.005%)
liquidityad.min_size=1000000   # Min channel: 1M sats (~0.01 BTC)
liquidityad.max_size=100000000 # Max channel: 100M sats (~1 BTC)
liquidityad.htlc_min=1000      # Min HTLC: 1000 sats
liquidityad.htlc_max=10000000  # Max HTLC: 10M sats

# Routing fees (separate from ads)
minhtlc=1000
maxhtlc=10000000
basefee=1000
feerate=50
```

### Monitor & Optimize
```bash
# Check active ads
lncli listliquidityads

# Check channel fees collected
lncli fwdinghistory --start_time=$(date -d '30 days ago' +%s) --end_time=$(date +%s) | jq '.forwarding_events | length'

# Rebalance for better routing
lncli rebalance --help
```

---

## 3. Capital Requirements & ROI Estimates

| Capital Deployed | Monthly Routing Fees (est.) | Monthly Liquidity Ad Premium (est.) | Total Monthly | Annualized ROI |
|------------------|----------------------------|-------------------------------------|---------------|----------------|
| 0.01 BTC (1M sats)     | 100–1,000 sats              | 500–2,000 sats                      | 600–3,000 sats | 0.7–3.6%       |
| 0.1 BTC (10M sats)     | 1,000–10,000 sats           | 5,000–20,000 sats                   | 6,000–30,000 sats | 0.7–3.6%      |
| 1 BTC (100M sats)      | 10,000–100,000 sats         | 50,000–200,000 sats                 | 60,000–300,000 sats | 0.7–3.6%     |

**Notes:**
- Routing fees highly dependent on node position (centrality, peer selection)
- Liquidity ad premiums depend on market demand (check `amboss.space` marketplace)
- VPS costs (~100,000–200,000 sats/mo at 100k sats/$) must be subtracted
- **Break-even typically requires >0.05 BTC deployed**

---

## 4. Alternative: Join a Liquidity Pool (No Node Operation)

### Lightning Pool (Lightning Labs)
- **Sidecar channels:** Lease inbound liquidity without running Pool client
- **Providers:** `pool.lightningnetwork.plus`, `lnpool.xyz`, `amboss.space/pool`
- **Yield:** ~0.5–2% monthly on leased capital
- **Risk:** Custodial/partially custodial depending on provider

### Amboss Magma
- **What:** Managed liquidity marketplace
- **Yield:** Variable, typically 1–3% monthly
- **Access:** Invite/beta currently

### LNbig / Other Custodial Pools
- **Yield:** 0.5–1.5% monthly
- **Risk:** Full custody, counterparty risk

---

## 5. Next Steps for This Project

1. **Deploy testnet node** — Validate liquidity ads config on testnet (no capital risk)
2. **Monitor amboss.space marketplace** — Track current liquidity ad rates for 1M–100M sat channels
3. **Calculate break-even** — Model VPS cost vs. expected fees at different capital levels
4. **Evaluate Pool sidecar** — Test leasing inbound via `pool` CLI on testnet
5. **Document findings** — Publish as `LN_LIQUIDITY_ADS_GUIDE.md` for future reference

---

## 6. Relevant Resources

- **LND Liquidity Ads docs:** `https://github.com/lightningnetwork/lnd/blob/master/docs/liquidity_ads.md` (check latest release)
- **BOLT Liquidity Ads proposal:** `https://github.com/lightning/bolts/pull/...` (search "liquidity ads")
- **Amboss marketplace:** `https://amboss.space/liquidity-ads`
- **Lightning Pool:** `https://github.com/lightninglabs/pool`
- **LN Router earnings tracker:** `https://terminal.lightning.engineering/`
- **1ML node explorer:** `https://1ml.com/`

---

## 7. Payout Addresses (for reference)
- **BTC on-chain:** `bc1qn9d7k93tf9kn5gye362g9e922chzqgegg8s5nk`
- **Lightning:** `gravityquest@coinos.io`
- **LNURL:** `https://coinos.io/api/lnurlp/gravityquest`

---

*This research document is for planning purposes only. No capital deployed in this session.*