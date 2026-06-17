"""
Runs spy.py logic for multiple competitor brands and produces a combined dataset
plus a rollup (per brand: ad count, longest run, top CTAs).

Usage:
  python3 extract.py --brands "Brand A" "Brand B" "Brand C" --out-dir ./run/ [--max-ads 120]
"""

import argparse, json, os, sys, time
from datetime import date

# Reuse spy logic
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "spy", "scripts"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib"))

import spy as spy_module
import scaleads_keys as keys

try:
    import requests  # noqa: F401
except ImportError:
    print(json.dumps({"error": "requests not installed — run: pip3 install requests"}))
    sys.exit(1)


def run_brand(token: str, brand: str, max_ads: int, country: str, today: date) -> dict:
    actor_input = {
        "searchTerms": [brand],
        "country": country,
        "activeStatus": "ACTIVE",
        "adType": "ALL",
        "maxResults": max_ads,
    }
    try:
        raw = spy_module.run_actor(token, spy_module.ACTOR_OPTIONS[0], actor_input)
    except Exception as e:
        print(f"[extract] {brand}: failed — {e}", flush=True)
        return {"brand": brand, "error": str(e), "ads": []}

    normalized = [spy_module.normalize(r, today) for r in raw]
    normalized = [a for a in normalized if "{{" not in (a.get("hook") or "")]
    filtered, dropped = spy_module.filter_brand(normalized, brand)
    filtered.sort(key=lambda a: a["days_running"], reverse=True)
    print(f"[extract] {brand}: {len(filtered)} ads (dropped {dropped} off-brand)", flush=True)
    return {"brand": brand, "ads": filtered, "filtered_count": dropped}


def build_rollup(brand_results: list) -> list:
    rollup = []
    for r in brand_results:
        ads = r.get("ads", [])
        if not ads:
            rollup.append({"name": r["brand"], "active_ads": 0, "longest_run": 0,
                           "top_ctas": [], "signature_angle": "", "error": r.get("error", "")})
            continue

        longest = ads[0]["days_running"] if ads else 0
        from collections import Counter
        cta_counts = Counter(a.get("cta", "") for a in ads if a.get("cta"))
        top_ctas = [cta for cta, _ in cta_counts.most_common(3) if cta]

        rollup.append({
            "name": r["brand"],
            "active_ads": len(ads),
            "longest_run": longest,
            "top_ctas": top_ctas,
            "signature_angle": "",  # filled in by Claude during analysis
        })
    return rollup


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--brands", nargs="+", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--max-ads", type=int, default=120)
    p.add_argument("--country", default="US")
    args = p.parse_args()

    creds = keys.load()
    token = creds.get("APIFY_TOKEN")
    if not token:
        print(json.dumps({"error": "APIFY_TOKEN not set — run /setup first"}))
        sys.exit(1)

    os.makedirs(args.out_dir, exist_ok=True)
    today = date.today()

    brand_results = []
    for brand in args.brands:
        result = run_brand(token, brand, args.max_ads, args.country, today)
        brand_results.append(result)
        # Small delay to avoid rate limits
        time.sleep(2)

    rollup = build_rollup(brand_results)

    all_ads_path = os.path.join(args.out_dir, "competitors_ads.json")
    with open(all_ads_path, "w") as f:
        json.dump(brand_results, f, indent=2)

    rollup_path = os.path.join(args.out_dir, "competitors_rollup.json")
    with open(rollup_path, "w") as f:
        json.dump(rollup, f, indent=2)

    print(json.dumps({
        "ok": True,
        "brands": len(brand_results),
        "total_ads": sum(len(r.get("ads", [])) for r in brand_results),
        "all_ads": all_ads_path,
        "rollup": rollup_path,
    }))


if __name__ == "__main__":
    main()
