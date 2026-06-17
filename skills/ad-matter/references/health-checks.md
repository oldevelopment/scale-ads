# Ad Matter — Account Health Scoring Rubric

**Start at 100. Subtract per finding. Cap each category's damage at 30.**
High severity: −8 pts · Medium: −4 pts · Low: −2 pts

---

## Category 1: Creative Fatigue (cap: 30)

### Per-ad check — Fatigue curve
**High (−8):** Last-7d CTR fell >25% below the 30d baseline CTR AND frequency > 2.5.
**Medium (−4):** Last-7d CTR fell 15–25% below the 30d baseline CTR AND frequency > 2.0.
**Low (−2):** Frequency > 2.5 alone (without CTR data to confirm fatigue).

### Account-level check — Thin creative pool
**Medium (−4):** Fewer than 5 ads with meaningful delivery (100+ impressions in the last 30 days). Small pools fatigue faster.

---

## Category 2: Frequency & Saturation (cap: 30)

### Ad-level
**High (−8):** Frequency > 6
**Medium (−4):** Frequency 4–6

### Ad set level
**High (−8):** Ad set frequency > 6
**Medium (−4):** Ad set frequency 3–4

### Account level
**High (−8):** Account average frequency > 4
**Medium (−4):** Account average frequency 3–4

---

## Category 3: Efficiency Gaps (cap: 30)

### Low CTR
**High (−8):** Ad CTR < 50% of account median AND impressions > 1,000
**Medium (−4):** Ad CTR < 70% of account median AND impressions > 1,000

### High cost-per-result
**High (−8):** Cost-per-result > 2× the account blend (weighted average across all ads)
**Medium (−4):** Cost-per-result 1.5–2× the account blend

---

## Category 4: Wasted Spend (cap: 30)

**High (−8):** Spend > MAX($50, 3% of total account spend) with zero results
**Medium (−4):** Spend > MAX($20, 1% of total account spend) with zero results
**Low (−2):** Any spend > $10 with zero results (flag but don't penalize heavily)

---

## Category 5: Audience Overlap Heuristic (cap: 30)

*Note: This is a heuristic, not a verified overlap calculation. Label it as such in the output.*

**Medium (−4):** 3 or more ad sets simultaneously running with frequency > 3.0 — likely overlapping audiences cannibalizing each other.
**Low (−2):** 2 ad sets with frequency > 3.0 — possible overlap.

---

## Category 6: Spend Concentration (cap: 30)

**Low (−2):** >70% of account spend concentrated in a single campaign. Concentration risk — single point of failure.

---

## How to apply the rubric

1. **Detect result type first.** Pull account insights and read the conversion indicator (e.g., `fb_pixel_lead`, `omni_purchase`, `link_click`). Never mention or flag purchase metrics on a lead-gen account.

2. **Score each category independently.** Sum the findings per category, cap at 30, subtract from 100.

3. **Minimum data thresholds.** Only apply efficiency flags (CTR, CPR) to ads with ≥1,000 impressions and ≥7 days of data. Don't penalize brand-new ads.

4. **Attribution window.** Assume 7-day click / 1-day view unless the account shows otherwise.

5. **Fold in Meta's own signals last.** After applying this rubric:
   - Pull `ads_get_opportunity_score` — causally-backed recommendations sorted by expected points of lift
   - Pull `ads_insights_anomaly_signal` — anomalies Meta has detected
   - If this rubric finds nothing but Meta's opportunity score is < 100, lead with Meta's score: "No rubric defects found. Meta's opportunity score is [X]/100, suggesting [Meta's top recommendation]."

---

## Verdict bands

| Score | Verdict |
|-------|---------|
| 90–100 | Healthy — minor optimizations only |
| 75–89 | Good — fix the flagged items this week |
| 60–74 | Needs attention — these issues are costing money |
| 0–59 | Critical — significant waste or fatigue; act today |

---

## Data fields to pull (Meta MCP)

**Account level (30d + 7d):**
- `spend`, `impressions`, `clicks`, `ctr`, `frequency`, `results`, `cost_per_result`

**Campaign level (30d):**
- `spend`, `results`, `cost_per_result`, `impressions`

**Ad set level (30d + 7d):**
- `spend`, `impressions`, `frequency`, `results`

**Ad level (30d + 7d):**
- `spend`, `impressions`, `clicks`, `ctr`, `frequency`, `results`, `cost_per_result`

**Fields NOT to request (Meta MCP does not support):**
- `quality_ranking`
- `engagement_rate_ranking`
- `conversion_rate_ranking`

Use Meta's native diagnostics tools instead:
- `ads_get_opportunity_score`
- `ads_insights_anomaly_signal`
