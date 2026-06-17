---
name: ad-matter
description: Full health audit of your live Meta ad account — scores it 0–100 using a 6-category rubric, surfaces wasted spend and fatigue, and delivers a severity-ranked fix list. Requires the official Meta Ads MCP. Trigger on "/ad-matter", "audit my meta account", "check my ad account health", "what's wrong with my Meta ads", "meta account audit", or "ad account review".
---

# /ad-matter — Live Meta Account Audit

## Requirements
- The **Commerce365 MCP** must be connected. Install Commerce365 on your Shopify store at [apps.shopify.com/commerce365](https://apps.shopify.com/commerce365), then connect the Claude MCP from within the Commerce365 dashboard.
- No Meta API token needed — auth is handled through the Commerce365 MCP connection.
- If MCP tools are unavailable, inform the user and stop gracefully.

## Step 1 — Find the account

Ask the user: "Which Meta ad account should I audit? (Account name or ID)"

Use `ads_list_ad_accounts` or `ads_get_ad_accounts` to find it. If there's only one, proceed automatically.

## Step 2 — Detect result type (critical)

Pull account-level insights and read the `indicator` field on the `results` metric (or look at the conversion events being optimized for).

Common types:
- `omni_purchase` / `purchase` → ecommerce
- `fb_pixel_lead` / `lead` → lead generation
- `link_click` → traffic
- `landing_page_view` → top-funnel

**Never mention purchases, ROAS, or revenue for a lead-gen account. Never mention leads for an ecommerce account.** The rubric adapts to the detected result type.

## Step 3 — Read the rubric

Read the full rubric from the reference file at:
`[plugin-path]/skills/ad-matter/references/health-checks.md`

This is the single source of truth for scoring thresholds.

## Step 4 — Pull data

Pull these in parallel (use the Meta MCP):

**30-day window:**
- Account insights: `spend`, `impressions`, `clicks`, `ctr`, `frequency`, `results`, `cost_per_result`
- Campaign breakdown: `spend`, `results`, `cost_per_result`, `impressions`
- Ad set breakdown: `spend`, `impressions`, `frequency`, `results`
- Ad breakdown: `spend`, `impressions`, `clicks`, `ctr`, `frequency`, `results`, `cost_per_result`

**7-day window (for fatigue detection):**
- Ad-level: `ctr`, `frequency`

**DO NOT request:** `quality_ranking`, `engagement_rate_ranking`, `conversion_rate_ranking` — Meta MCP rejects these.

## Step 5 — Apply the rubric

Score each category independently per health-checks.md:
1. Creative Fatigue (cap: −30)
2. Frequency & Saturation (cap: −30)
3. Efficiency Gaps (cap: −30)
4. Wasted Spend (cap: −30)
5. Audience Overlap Heuristic (cap: −30)
6. Spend Concentration (cap: −30)

Sum deductions, subtract from 100. Minimum score: 0.

## Step 6 — Pull Meta's own diagnostics

After scoring:
```
ads_get_opportunity_score(account_id)
ads_insights_anomaly_signal(account_id)
```

If the rubric finds nothing but Meta's opportunity score is < 100:
> "No rubric defects found. Meta's opportunity score is [X]/100, with [N] recommendations. Top suggestion: [Meta's #1 recommendation by lift]."

Always attribute Meta's findings: "Meta reports…" not "I found…"

## Step 7 — Chat output

```
## [Account Name] — Account Audit
**Health Score: [SCORE]/100 — [VERDICT]**

### Findings
[Severity-grouped list]

**HIGH** (−X pts)
- [Finding with specific numbers: "Ad 'Summer Sale' — CTR 0.3% vs account median 1.1% (70% below). Spend: $847 last 30d."]

**MEDIUM** (−X pts)
- [Finding]

**LOW** (−X pts)
- [Finding]

### 🎯 Fix This Week (highest impact)
1. [Specific action tied to a dollar amount where possible]
2.
3.

### Meta Diagnostics
[Opportunity score + top recommendation, attributed to Meta]
```

**Rules for findings:**
- Every finding must include specific numbers from the account
- Every HIGH finding must include the dollar amount at risk or being wasted
- Use the result type you detected — never mention the wrong conversion type

## Step 8 — Dashboard

Write the data file and render:

**data.json:**
```json
{
  "kind": "ad-matter",
  "account_name": "[Account Name]",
  "score": [0-100],
  "meta_opportunity_score": [0-100 or null],
  "findings": [
    {"severity": "high", "text": "Ad 'Summer Sale' — CTR 0.3% vs median 1.1% (−$847 risk)"},
    {"severity": "medium", "text": "..."},
    {"severity": "low", "text": "..."}
  ],
  "fix_this_week": [
    "Pause 'Summer Sale' — 70% below CTR median, $847 spent with poor results",
    "..."
  ]
}
```

```bash
python3 [plugin-path]/lib/scaleads_dashboard.py \
  --data scale-ads-runs/ad-matter-[account-slug]-[date]/data.json \
  --out scale-ads-runs/ad-matter-[account-slug]-[date]/dashboard.html
```

## Run folder naming
```
scale-ads-runs/ad-matter-[account-slug]-[YYYY-MM-DD]/
```

## If Meta MCP is unavailable
Inform the user:
> "The Commerce365 MCP isn't connected. To set it up: install Commerce365 on your Shopify store at apps.shopify.com/commerce365, then open the Commerce365 dashboard and follow the Claude MCP connection steps. The other 5 skills work without it."
