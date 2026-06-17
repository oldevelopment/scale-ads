---
name: spy
description: Pull every active Meta ad a competitor is running, ranked by run-time (longest-running = proven winners). Trigger on "/spy", "spy on [brand]", "what ads is [brand] running", "show me [brand]'s ads", or "competitor ads for [brand]".
---

# /spy — Competitor Ad Intelligence

## The core thesis
In the Meta Ad Library, longevity is the only visible shadow of spend. Brands kill losing ads fast. An ad running 100+ days is paying for itself. Sort by run-time and the proven winners float to the top.

**Honest caveat — always include in your output:** The Ad Library shows live creative, not spend or results. Longevity is a strong proxy, not proof. A long-running ad could also be organic evergreen content.

## Step 1 — Extract the brand name
From the user's message, extract the brand to spy on. If ambiguous, ask: "Which brand — the full company name or their Facebook page name?"

## Step 2 — Find the plugin path
Determine where this plugin is installed (check the path of this SKILL.md file or use the known install location). The spy.py script is at: `[plugin-path]/skills/spy/scripts/spy.py`

## Step 3 — Run the scraper
```bash
python3 [plugin-path]/skills/spy/scripts/spy.py \
  --brand "[BRAND_NAME]" \
  --out-dir "scale-ads-runs/spy-[brand-slug]-$(date +%Y-%m-%d)/" \
  --max-ads 200 \
  --country US
```

If the user specifies a country, pass it with `--country`. Default is US.

Read the JSON result from stdout. If `error` is present, report it and stop.

## Step 4 — Interpret and present the results

### Table view (top 15 by days running)
Present this table from `spy_ads.json`:

| Days | CTA | Hook (first 100 chars) | Offer | Destination |
|------|-----|------------------------|-------|-------------|

Only include ads with a non-empty hook. Skip ads where hook contains `{{` (dynamic catalog tokens — not human-written).

### Analysis layer — this is the value
After the table, add:

**Hook patterns across long-runners (60+ days):**
Identify 2–4 recurring patterns. Quote real hooks.

**CTA + offer combo they lean on:**
What's their dominant CTA? What offer appears most? What does this reveal about what converts for them?

**Their "control" ad:**
The 1–3 longest-running ads. Why is it sticky? What specifically is working — the hook type, the offer, the emotional angle?

**What's missing (open angles):**
What angles are they NOT running? This is intelligence for `/competitors-extractor`.

## Step 5 — Dashboard
Write the spy_ads.json output (already written by the script) and render the dashboard:
```bash
python3 [plugin-path]/lib/scaleads_dashboard.py \
  --data scale-ads-runs/spy-[slug]-[date]/spy_ads.json \
  --out scale-ads-runs/spy-[slug]-[date]/dashboard.html
```

## Filtering — mention this in output
The script automatically filters out off-brand advertisers (keyword searches are fuzzy). Always state:
> "Showing [N] [Brand] ads. Filtered out [X] off-brand results."

If the user wants all results including off-brand, re-run with `--all-advertisers` flag.

## If the scraper fails
Common causes:
1. Wrong actor ID — try `--actor curious_coder/facebook-ad-library-scraper`
2. Apify token not set — run `/setup`
3. Brand name doesn't match page name — try the exact Facebook page name

## Run folder naming
```
scale-ads-runs/spy-[brand-slug]-[YYYY-MM-DD]/
```
Example: `scale-ads-runs/spy-ridge-wallet-2024-01-15/`
