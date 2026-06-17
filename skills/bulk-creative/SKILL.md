---
name: bulk-creative
description: Generate 20 on-brand Meta ad copy variations from a single reference ad, brief, or hook. Trigger on "/bulk-creative", "write 20 ads", "generate ad variations", "remix this ad", "write ad copy for [brand/product]", or "bulk copy".
---

# /bulk-creative — 20 Ad Copy Variations

## Purpose
Take one reference (a winning ad, a hook, or a 60-second brief) and generate 20 distinct ad copy variations, each differing on at least one named dimension. No API keys, no setup required — delivers value immediately.

## Step 1 — Find brand context

Look for brand files in this order:
1. `./brand/brand-dna.md`
2. `./brand/brand-voice.md`
3. `./brand/icp-cards.md`
4. `./clients/[brand-name]/brand/` (for agencies working with multiple clients)

If found, extract:
- Voice style (bold / friendly / expert / playful / etc.)
- Forbidden tones or words (never violate these)
- ICP (ideal customer profile) — their #1 frustration/desire
- Brand personality rules

## Step 2 — If no brand files, collect a 60-second inline brief

**Do not stop and demand files.** If no brand context exists, ask for these five things in one message:
1. Product name and one-line description
2. Target audience + their #1 frustration or desire
3. Voice: bold / friendly / expert / playful (pick one or describe)
4. One reference line — a hook or headline they like (can be from a competitor)
5. Offer or CTA (free trial, shop now, book a call, etc.)

Then proceed immediately. Do not ask for anything else.

## Step 3 — Lock the reference

Identify the "control" — the reference ad, hook, or brief this batch remixes. State it clearly before generating:
> "Remixing from: [reference]"

## Step 4 — Generate 20 variations

Produce exactly 20 numbered variations. Each must:
- Be a complete, ready-to-test ad (primary text + optional headline)
- Differ from others on at least one named dimension
- Be labeled with its dimension(s)

**Distribute across these dimensions:**
- **Hook angle** (~2 each): problem-agitate, curiosity gap, bold claim, social proof/UGC, us-vs-them, founder story, myth-bust, question, transformation, fear/urgency
- **Length**: ~8 short (1–2 sentences), ~8 medium (3–5 sentences), ~4 long (6+ sentences or story format)
- **CTA approach**: urgency, value framing, question, command, risk reversal
- **Emotional register**: aspirational, empathetic, challenging, excited, calm/authoritative

Label each variation:
```
**#7 — [Hook: social proof · Length: short · CTA: urgency]**
"10,000 people switched in 30 days. You're next. Try free →"
```

## Step 5 — Pick the Top 5 to test first

After the 20, add:
> "**Top 5 to test first:**"
List 5 with one-line reasoning for each (why this one, not just "it's strong").

## Step 6 — Save output

If a project folder is active (there's a `./copy/` directory or a brand folder), save to:
```
./copy/[brand]-bulk-copy-[YYYY-MM-DD].md
```
Otherwise offer to save. Don't save without asking if the directory doesn't exist.

## Hard rules — enforce always

- **ALWAYS use voice-of-customer language** over marketing-speak. "Finally stopped waking up at 3am" beats "improves sleep quality."
- **NEVER use "Shop now" or "Limited time offer" as a hook.** These are CTAs, not hooks.
- **NEVER violate brand forbidden-tones** when files are present.
- **Every variation must be distinct on a named dimension.** If two are identical except for one word, merge them and write a genuinely different one.
- **No filler variations** — each of the 20 must be something you'd actually test.
- **No em-dash abuse** — varied punctuation reads as authentic.
