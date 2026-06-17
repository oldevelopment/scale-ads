---
name: competitors-extractor
description: Map an entire ad category head-to-head — pull active ads for 3–5 competitor brands, classify every hook angle, and surface the open lanes nobody is running. Trigger on "/competitors-extractor", "map the category", "compare competitors' ads", "what angles is the category running", or "competitive ad analysis for [brand/category]".
---

# /competitors-extractor — Category Intelligence Map

## Purpose
Run the spy engine on 3–5 competitor brands simultaneously, classify every hook angle, and deliver three outputs: a head-to-head table, a visual angle map (🔴 crowded / 🟡 contested / 🟢 open), and the highest-opportunity gaps no competitor is running.

## Step 1 — Identify the competitors

If the user provides a brand (not a list), ask:
> "Who are the 3–5 main competitors in this category? Or should I include [Brand A], [Brand B], [Brand C]? (I'll pull active ads for each.)"

If the user provides a list, proceed. If they provide a niche/category, make your best guess at 3–5 well-known brands and confirm before running.

## Step 2 — Run the extractor

```bash
python3 [plugin-path]/skills/competitors-extractor/scripts/extract.py \
  --brands "Brand A" "Brand B" "Brand C" \
  --out-dir "scale-ads-runs/competitors-[slug]-$(date +%Y-%m-%d)/" \
  --max-ads 120 \
  --country US
```

Read stdout JSON. If individual brands fail, continue with the ones that succeeded and note the failures.

## Step 3 — Three-part analysis output

### A. Head-to-head table

| Competitor | Active Ads | Longest Run | Top CTAs | Signature Angle |
|------------|-----------|-------------|----------|----------------|
| Brand A | N | X days | CTA1, CTA2 | [angle] |

Fill in "Signature Angle" from reading their actual long-running hooks — not from the rollup data alone.

### B. Angle map

Classify each brand's longest-running hooks (top 10 per brand) into these buckets:

| Angle | Brands Using It | Status |
|-------|----------------|--------|
| Problem-agitate | Brand A, Brand C | 🔴 crowded (2+ brands, high volume) |
| Social proof / UGC | Brand B | 🟡 contested (1–2 brands, moderate) |
| Founder story | — | 🟢 open (nobody running it) |
| Feature claims | Brand A, B, C | 🔴 crowded |
| Curiosity gap | — | 🟢 open |
| Transformation | Brand B | 🟡 contested |
| Fear / urgency | — | 🟢 open |
| Us-vs-them | Brand A | 🟡 contested |
| Price / value | Brand A, C | 🔴 crowded |
| Identity / status | — | 🟢 open |

**Status rules:**
- 🔴 Crowded: 2+ brands running this angle at high volume
- 🟡 Contested: 1–2 brands, moderate usage
- 🟢 Open: Nobody running it, or only low-volume attempts

### C. The gaps — the payoff

Name the **2–3 highest-opportunity open lanes** with:
1. The angle name
2. Why it's an opportunity for this category (what desire/pain it addresses)
3. Real competitor hooks quoted as evidence for EVERY classification — never say "nobody runs X" without checking

Example gap write-up:
> **Open: UGC / Social Proof** — Neither Brand A nor Brand B runs a single user-story ad. Brand A leans hard on feature claims ("precision-cut RFID blocking"), Brand C uses price. The social proof lane is wide open. First-person transformation hooks ("I returned my [competitor] after one week") are completely uncontested in this category.

## Step 4 — Re-render dashboard after analysis

After completing the analysis, write the dashboard data file and render:

**data.json:**
```json
{
  "kind": "competitors",
  "competitors": [
    {
      "name": "Brand A",
      "active_ads": N,
      "longest_run": X,
      "top_ctas": ["CTA1"],
      "signature_angle": "Feature claims + price urgency"
    }
  ],
  "angle_map": [
    {"angle": "Problem-agitate", "status": "crowded"},
    {"angle": "Social proof / UGC", "status": "open"}
  ],
  "gaps": [
    {
      "title": "Open: UGC / Social Proof",
      "evidence": "Brand A runs feature claims. Brand B runs price. Nobody runs a user story."
    }
  ]
}
```

```bash
python3 [plugin-path]/lib/scaleads_dashboard.py \
  --data scale-ads-runs/competitors-[slug]-[date]/data.json \
  --out scale-ads-runs/competitors-[slug]-[date]/dashboard.html
```

## Rules
- Quote real hooks for every classification — evidence, not assertion
- If a brand's data failed, note it plainly: "Brand C failed — included in angle map only for brands with data"
- The gaps section must name the specific angle, not generic advice like "try more creative formats"
- Minimum 3 angle buckets marked 🟢 open for the output to be useful — if everything is crowded, dig deeper

## Run folder naming
```
scale-ads-runs/competitors-[category-slug]-[YYYY-MM-DD]/
```
