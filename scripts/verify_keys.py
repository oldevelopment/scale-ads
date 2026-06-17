import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

try:
    import requests
except ImportError:
    print(json.dumps({"error": "requests library not installed — run: pip3 install requests", "results": []}))
    sys.exit(1)

import scaleads_keys as keys


def verify_apify(token):
    try:
        r = requests.get(
            "https://api.apify.com/v2/users/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        if r.status_code == 200:
            return True, f"valid (account: {r.json()['data']['username']})"
        return False, f"rejected (HTTP {r.status_code}) — did you paste the account ID instead of the Personal API token?"
    except requests.exceptions.Timeout:
        return False, "timed out after 15s — check your internet connection"
    except Exception as e:
        return False, f"error: {e}"


creds = keys.load()
results = []

if "APIFY_TOKEN" in creds:
    ok, detail = verify_apify(creds["APIFY_TOKEN"])
    results.append({"key": "APIFY_TOKEN", "ok": ok, "detail": detail})
else:
    results.append({"key": "APIFY_TOKEN", "ok": False, "detail": "not set"})

print(json.dumps({"results": results}, indent=2))
