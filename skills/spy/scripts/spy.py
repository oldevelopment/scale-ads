"""
Pulls active Meta ads for a competitor brand via Apify's Facebook Ad Library scrapers.
Sorts by days_running (longevity = spend proxy).

Usage:
  python3 spy.py --brand "Ridge Wallet" --out-dir ./run/ [--max-ads 200] [--country US] [--all-advertisers]
"""

import argparse, json, os, sys, time
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "lib"))

try:
    import requests
except ImportError:
    print(json.dumps({"error": "requests not installed — run: pip3 install requests"}))
    sys.exit(1)

import scaleads_keys as keys

# Top Apify actors for Facebook Ad Library (by usage). We try the first, fall back to others.
ACTOR_OPTIONS = [
    "apify/facebook-ads-scraper",
    "curious_coder/facebook-ad-library-scraper",
    "nwua9Gu5YrADL7ZDj",  # Clockwork Facebook Ad Library
]


def run_actor(token: str, actor_id: str, actor_input: dict, timeout: int = 300) -> list:
    resp = requests.post(
        f"https://api.apify.com/v2/acts/{actor_id}/runs",
        params={"token": token},
        json=actor_input,
        timeout=30,
    )
    resp.raise_for_status()
    run = resp.json()["data"]
    run_id = run["id"]

    deadline = time.time() + timeout
    while run["status"] in ("READY", "RUNNING"):
        if time.time() > deadline:
            raise TimeoutError(f"Actor run {run_id} did not finish within {timeout}s")
        time.sleep(5)
        run = requests.get(
            f"https://api.apify.com/v2/actor-runs/{run_id}",
            params={"token": token},
            timeout=30,
        ).json()["data"]

    if run["status"] != "SUCCEEDED":
        raise RuntimeError(f"Actor run failed with status: {run['status']}")

    items = requests.get(
        f"https://api.apify.com/v2/datasets/{run['defaultDatasetId']}/items",
        params={"token": token, "clean": "true"},
        timeout=60,
    ).json()
    return items if isinstance(items, list) else []


def normalize(raw: dict, today: date) -> dict:
    """Flatten an Apify ad record into our standard shape."""
    # Different actors use different field names
    started_raw = (
        raw.get("startDate")
        or raw.get("ad_creation_time")
        or raw.get("start_date")
        or raw.get("createdAt", "")
    )
    try:
        started = date.fromisoformat(str(started_raw)[:10])
        days = (today - started).days
    except Exception:
        started = None
        days = 0

    text = (
        raw.get("snapshot", {}).get("body", {}).get("text", "")
        or raw.get("ad_creative_bodies", [""])[0]
        or raw.get("body", "")
        or raw.get("text", "")
        or ""
    )
    hook = text[:140].replace("\n", " ").strip()

    return {
        "advertiser": raw.get("page_name") or raw.get("pageName") or raw.get("advertiser", ""),
        "hook": hook,
        "cta": raw.get("cta_type") or raw.get("snapshot", {}).get("cta_text") or raw.get("cta", ""),
        "offer": (
            raw.get("snapshot", {}).get("link_description", "")
            or raw.get("link_description", "")
            or raw.get("offer", "")
        )[:120],
        "destination": (
            raw.get("snapshot", {}).get("link_url", "")
            or raw.get("link_url", "")
            or raw.get("destination", "")
        ),
        "started": str(started) if started else "",
        "days_running": days,
        "is_active": raw.get("is_active", True),
    }


def filter_brand(ads: list, brand_token: str) -> tuple[list, int]:
    """Keep only ads whose advertiser name contains the brand token."""
    token = brand_token.lower()
    kept = [a for a in ads if token in (a.get("advertiser") or "").lower()]
    dropped = len(ads) - len(kept)
    return kept, dropped


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--brand", required=True, help="Brand name to spy on")
    p.add_argument("--out-dir", required=True, help="Directory to write outputs")
    p.add_argument("--max-ads", type=int, default=200)
    p.add_argument("--country", default="US")
    p.add_argument("--all-advertisers", action="store_true", help="Skip brand filter")
    p.add_argument("--actor", default=None, help="Override actor ID")
    args = p.parse_args()

    creds = keys.load()
    token = creds.get("APIFY_TOKEN")
    if not token:
        print(json.dumps({"error": "APIFY_TOKEN not set — run /setup first"}))
        sys.exit(1)

    os.makedirs(args.out_dir, exist_ok=True)
    today = date.today()

    actor_input = {
        "searchTerms": [args.brand],
        "country": args.country,
        "activeStatus": "ACTIVE",
        "adType": "ALL",
        "maxResults": args.max_ads,
    }

    actor_id = args.actor or ACTOR_OPTIONS[0]
    print(f"[spy] Running actor {actor_id} for '{args.brand}'…", flush=True)

    try:
        raw_ads = run_actor(token, actor_id, actor_input)
    except Exception as e:
        print(json.dumps({"error": str(e), "hint": "Try a different actor with --actor flag"}))
        sys.exit(1)

    print(f"[spy] Got {len(raw_ads)} raw results", flush=True)

    normalized = [normalize(r, today) for r in raw_ads]

    # Filter out dynamic catalog ads (template tokens signal auto-generated, not human-written)
    normalized = [a for a in normalized if "{{" not in (a.get("hook") or "")]

    if args.all_advertisers:
        filtered = normalized
        dropped_count = 0
    else:
        filtered, dropped_count = filter_brand(normalized, args.brand)

    # Sort by days running descending
    filtered.sort(key=lambda a: a["days_running"], reverse=True)

    print(f"[spy] Kept {len(filtered)} brand ads, dropped {dropped_count} off-brand", flush=True)

    result = {
        "kind": "spy",
        "brand": args.brand,
        "ads": filtered,
        "total": len(filtered),
        "filtered_count": dropped_count,
        "scraped_at": str(today),
    }

    json_path = os.path.join(args.out_dir, "spy_ads.json")
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2)

    # CSV
    import csv
    csv_path = os.path.join(args.out_dir, "spy_ads.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["days_running", "advertiser", "hook", "cta", "offer", "destination", "started"])
        w.writeheader()
        for ad in filtered:
            w.writerow({k: ad.get(k, "") for k in w.fieldnames})

    print(json.dumps({"ok": True, "ads": len(filtered), "filtered": dropped_count,
                      "json": json_path, "csv": csv_path}))


if __name__ == "__main__":
    main()
