---
name: ad-score
description: Grade any Meta ad 0–100 across 6 dimensions before launch. Trigger on "/ad-score", "score this ad", "grade this ad", "how good is this ad", "rate this creative", or "pre-launch check".
---

# /ad-score — Pre-Launch Ad Grader

## Purpose
Apply a rigorous 6-dimension rubric to any ad (pasted copy, script, image description, or URL) and return a 0–100 score, per-dimension breakdown, specific fixes for weak areas, and a launch/no-launch verdict.

## The 6 Dimensions (100 points total)

| # | Dimension | Max | What it measures |
|---|-----------|-----|-----------------|
| 1 | Hook | 25 | Does the first line/3 seconds stop the scroll? Specificity, tension, pattern interrupt |
| 2 | Copy | 20 | Clarity, one-idea focus, believability, voice-of-customer language |
| 3 | CTA | 15 | Is the next action obvious, single, and low-friction? |
| 4 | Offer | 15 | Value framing, risk reversal, stakes — is the offer compelling? |
| 5 | Emotional Resonance | 15 | Real desire/fear/identity — not just features |
| 6 | Visual Fit | 10 | Does the creative match the message and the platform? |

## Scoring rules — enforce these exactly

**Rule 1 — Handle missing dimensions honestly.**
If you only have copy (no visual), Visual Fit is "not assessable." Redistribute its 10 points proportionally across the remaining 5 dimensions. State clearly: "Visual Fit not assessed — copy-only submission. Points redistributed."

**Rule 2 — Every below-80% dimension gets a specific fix.**
Not "make the hook stronger." An actual rewritten line or specific instruction:
> "Hook scores 14/25. Fix: Replace 'Improve your sleep' with 'I stopped waking up at 3am after one week.'"

**Rule 3 — Calibrate hard. This is non-negotiable.**
- Generic ad (could apply to any brand): **40s–50s**
- Decent ad with one strong dimension: **55–65**
- Good ad, launch-ready with minor fixes: **70–79**
- Strong ad, real competitive edge: **80–84**
- Excellent — few ads get here: **85–94**
- Near-perfect: **95–100** (almost never)

If you catch yourself scoring a mediocre ad above 60, stop and re-read Rule 3.

## Verdict bands

| Score | Verdict |
|-------|---------|
| 85–100 | **Launch it** — strong creative, minimal risk |
| 70–84 | **Launch-ready with fixes** — apply the fixes below before spending |
| 55–69 | **Needs work** — don't launch; revise the flagged dimensions |
| 0–54 | **Rebuild** — fundamental issues; start with a new hook |

## Output format

### Chat output
```
## Ad Score: [AD NAME OR FIRST 6 WORDS]

**Total: [SCORE]/100 — [VERDICT]**

| Dimension | Score | Max |
|-----------|-------|-----|
| Hook | X | 25 |
| Copy | X | 20 |
| CTA | X | 15 |
| Offer | X | 15 |
| Emotional Resonance | X | 15 |
| Visual Fit | X | 10 |

### ✅ What's working
- [specific strength 1]
- [specific strength 2]

### 🔧 Fix before launch
- Hook (X/25): [specific rewritten line]
- [Dimension]: [specific fix]

### Verdict
[One paragraph: launch decision + primary reason]
```

### Dashboard output
After the chat scorecard, write a JSON file to a dated run folder and render the dashboard:

**Run folder:** `scale-ads-runs/ad-score-[slug]-[YYYY-MM-DD]/`

**data.json:**
```json
{
  "kind": "ad-score",
  "ad_name": "[first 6 words of ad or provided name]",
  "total": [score],
  "verdict": "[verdict band text]",
  "dimensions": [
    {"name": "Hook", "score": X, "max": 25},
    {"name": "Copy", "score": X, "max": 20},
    {"name": "CTA", "score": X, "max": 15},
    {"name": "Offer", "score": X, "max": 15},
    {"name": "Emotional Resonance", "score": X, "max": 15},
    {"name": "Visual Fit", "score": X, "max": 10}
  ],
  "fixes": ["specific fix 1", "specific fix 2"],
  "keep": ["strength 1", "strength 2"]
}
```

Then run:
```bash
python3 [plugin-path]/lib/scaleads_dashboard.py --data [run-folder]/data.json --out [run-folder]/dashboard.html
```
