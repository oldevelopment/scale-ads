---
name: setup
description: Set up and verify credentials for the scale-ads plugin. Collects the Apify API token, saves it securely, and verifies it with a live API call. Trigger on "/setup", "setup scale-ads", "configure scale-ads", "save my apify token", or "add credentials".
---

# /setup — Credential Setup & Verification

## Purpose
Collect the Apify Personal API token, store it securely in `~/.scale-ads/credentials.env` (chmod 600), and verify it with a live API call before confirming success.

## Three hard rules you must never break

1. **Never echo the token back in chat.** After saving, only show a masked version (first 4 chars + "…" + last 4 chars).
2. **Always verify with a live API call.** A silently-wrong key is worse than a missing one.
3. **Only collect what's needed.** This plugin needs exactly one key: the Apify Personal API token. The `/ad-matter` skill uses the official Meta Ads MCP which handles its own auth — never ask for a Meta token here.

## Step-by-step flow

### Step 1 — Check current status
Run:
```bash
python3 ~/.claude/plugins/scale-ads/scripts/verify_keys.py
```
(Adjust the path to wherever the plugin is installed.)

Parse the JSON result:
- If `APIFY_TOKEN` is present and `ok: true` → tell the user their token is already set and verified (show masked value). Offer to replace it if they want.
- If missing or `ok: false` → proceed to Step 2.

### Step 2 — Request the token
Ask the user:
> "Please paste your Apify Personal API token. You can find it at: **Console → Settings → Integrations → Personal API tokens**. Do not share your account ID — it starts with 'apify_api_' or is a long alphanumeric string starting with your username."

Wait for their response.

### Step 3 — Save the token
Run this Python snippet (adapt the path as needed):
```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/plugins/scale-ads/lib"))
import scaleads_keys as keys
keys.save({"APIFY_TOKEN": "<TOKEN_FROM_USER>"})
```

### Step 4 — Verify live
Run verify_keys.py again and check the result.

- **Success** (`ok: true`): Reply with:
  > "✅ All set! APIFY_TOKEN saved and verified (apif…XXXX). You're ready to run /spy and /competitors-extractor."
- **Failure** (`ok: false`): Show the error detail. Common issues:
  - "Pasted the account ID instead of the Personal API token" — the Personal API token is found under Settings → Integrations, not the main dashboard
  - HTTP 401 → token is wrong or expired
  - HTTP 429 → rate limited, try again in a minute

### Step 5 — Remind about /ad-matter
After successful setup, add:
> "Note: `/ad-matter` connects through the official Meta Ads MCP at mcp.facebook.com/ads — no token needed here. Make sure that MCP is connected in your Claude Code settings."

## What NOT to do
- Do not create the credentials file manually with hardcoded content
- Do not store the token in the plugin folder or any git-tracked location
- Do not proceed if verify fails — make the user fix the token first
