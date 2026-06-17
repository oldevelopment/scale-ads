import argparse, json, html as htmllib
import subprocess, sys, os


def pct(score, max_score):
    return round((score / max_score) * 100) if max_score else 0


def score_color(pct_val):
    if pct_val >= 85:
        return "#4CAF50"
    if pct_val >= 70:
        return "#4f8cff"
    if pct_val >= 55:
        return "#f5a623"
    return "#e5484d"


def render_ad_score(data):
    total = data.get("total", 0)
    verdict = data.get("verdict", "")
    ad_name = htmllib.escape(data.get("ad_name", "Ad Score"))
    dimensions = data.get("dimensions", [])
    fixes = data.get("fixes", [])
    keep = data.get("keep", [])
    color = score_color(total)

    dim_rows = ""
    for d in dimensions:
        name = htmllib.escape(d.get("name", ""))
        score = d.get("score", 0)
        max_s = d.get("max", 25)
        p = pct(score, max_s)
        c = score_color(p)
        dim_rows += f"""
        <div class="dim-row">
          <div class="dim-label">{name}</div>
          <div class="dim-bar-wrap">
            <div class="dim-bar" style="width:{p}%;background:{c};"></div>
          </div>
          <div class="dim-score" style="color:{c}">{score}/{max_s}</div>
        </div>"""

    fix_items = "".join(f'<li>{htmllib.escape(f)}</li>' for f in fixes)
    keep_items = "".join(f'<li>{htmllib.escape(k)}</li>' for k in keep)

    return f"""
    <div class="header"><span class="brand">SCALE ADS</span><span class="skill-tag">AD SCORE</span></div>
    <h1>{ad_name}</h1>
    <div class="score-section">
      <div class="score-ring-wrap">
        <div class="score-ring" style="--pct:{total};--color:{color};">
          <div class="score-inner">
            <span class="score-num" style="color:{color}">{total}</span>
            <span class="score-label">/ 100</span>
          </div>
        </div>
      </div>
      <div class="verdict-wrap">
        <div class="verdict">{htmllib.escape(verdict)}</div>
      </div>
    </div>
    <div class="section"><h2>Dimension Breakdown</h2>{dim_rows}</div>
    <div class="two-col">
      <div class="section"><h2>✅ Keep</h2><ul>{keep_items}</ul></div>
      <div class="section"><h2>🔧 Fix Before Launch</h2><ul>{fix_items}</ul></div>
    </div>"""


def render_spy(data):
    brand = htmllib.escape(data.get("brand", ""))
    ads = data.get("ads", [])
    total = len(ads)
    filtered = data.get("filtered_count", 0)

    rows = ""
    for ad in ads[:30]:
        days = ad.get("days_running", 0)
        hook = htmllib.escape((ad.get("hook", "") or "")[:120])
        cta = htmllib.escape(ad.get("cta", "") or "")
        offer = htmllib.escape((ad.get("offer", "") or "")[:80])
        dest = htmllib.escape(ad.get("destination", "") or "")
        rows += f"""
        <tr>
          <td class="days">{days}d</td>
          <td class="hook">{hook}</td>
          <td>{cta}</td>
          <td>{offer}</td>
          <td class="dest">{dest[:40]}</td>
        </tr>"""

    return f"""
    <div class="header"><span class="brand">SCALE ADS</span><span class="skill-tag">SPY</span></div>
    <h1>{brand} — Active Ads</h1>
    <div class="meta-row">
      <span class="pill">{total} ads shown</span>
      <span class="pill-gray">{filtered} off-brand filtered</span>
    </div>
    <div class="section">
      <table class="ad-table">
        <thead><tr><th>Days</th><th>Hook</th><th>CTA</th><th>Offer</th><th>Destination</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""


def render_competitors(data):
    competitors = data.get("competitors", [])
    gaps = data.get("gaps", [])

    brand_cards = ""
    for c in competitors:
        name = htmllib.escape(c.get("name", ""))
        ads = c.get("active_ads", 0)
        longest = c.get("longest_run", 0)
        ctas = ", ".join(c.get("top_ctas", []))
        angle = htmllib.escape(c.get("signature_angle", ""))
        brand_cards += f"""
        <div class="brand-card">
          <div class="brand-name">{name}</div>
          <div class="brand-stats">{ads} ads · {longest}d longest run</div>
          <div class="brand-ctas">CTAs: {htmllib.escape(ctas)}</div>
          <div class="brand-angle">{angle}</div>
        </div>"""

    angle_rows = ""
    for item in data.get("angle_map", []):
        angle = htmllib.escape(item.get("angle", ""))
        status = item.get("status", "open")
        dot = "🔴" if status == "crowded" else ("🟡" if status == "contested" else "🟢")
        label = status.upper()
        angle_rows += f'<tr><td>{dot}</td><td>{angle}</td><td class="status-{status}">{label}</td></tr>'

    gap_items = "".join(f'<div class="gap-item"><div class="gap-title">{htmllib.escape(g.get("title",""))}</div><div class="gap-evidence">{htmllib.escape(g.get("evidence",""))}</div></div>' for g in gaps)

    return f"""
    <div class="header"><span class="brand">SCALE ADS</span><span class="skill-tag">COMPETITORS</span></div>
    <h1>Category Intelligence</h1>
    <div class="section"><h2>Head-to-Head</h2><div class="brand-grid">{brand_cards}</div></div>
    <div class="section"><h2>Angle Map</h2>
      <table class="angle-table"><thead><tr><th></th><th>Angle</th><th>Status</th></tr></thead>
      <tbody>{angle_rows}</tbody></table>
    </div>
    <div class="section"><h2>🟢 Open Lanes — Your Opportunity</h2>{gap_items}</div>"""


def render_ad_matter(data):
    account = htmllib.escape(data.get("account_name", "Ad Account"))
    score = data.get("score", 0)
    color = score_color(score)
    findings = data.get("findings", [])
    fix_week = data.get("fix_this_week", [])
    meta_score = data.get("meta_opportunity_score")

    severity_order = {"high": 0, "medium": 1, "low": 2}
    findings_sorted = sorted(findings, key=lambda f: severity_order.get(f.get("severity", "low"), 2))

    finding_items = ""
    for f in findings_sorted:
        sev = f.get("severity", "low")
        pill_class = "pill-high" if sev == "high" else ("pill-med" if sev == "medium" else "pill-low")
        finding_items += f"""
        <div class="finding">
          <span class="pill {pill_class}">{sev.upper()}</span>
          <span class="finding-text">{htmllib.escape(f.get('text',''))}</span>
        </div>"""

    fix_items = "".join(f'<li>{htmllib.escape(x)}</li>' for x in fix_week)
    meta_row = f'<div class="meta-score-row">Meta Opportunity Score: <strong>{meta_score}</strong></div>' if meta_score is not None else ""

    return f"""
    <div class="header"><span class="brand">SCALE ADS</span><span class="skill-tag">AD MATTER</span></div>
    <h1>{account} — Account Audit</h1>
    <div class="score-section">
      <div class="score-ring-wrap">
        <div class="score-ring" style="--pct:{score};--color:{color};">
          <div class="score-inner">
            <span class="score-num" style="color:{color}">{score}</span>
            <span class="score-label">/ 100</span>
          </div>
        </div>
      </div>
    </div>
    {meta_row}
    <div class="section"><h2>Findings</h2>{finding_items}</div>
    <div class="section"><h2>🎯 Fix This Week</h2><ul>{fix_items}</ul></div>"""


CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #12121f; color: #e8e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 40px; max-width: 1100px; margin: 0 auto; line-height: 1.5; }
.header { display: flex; align-items: center; gap: 12px; margin-bottom: 28px; }
.brand { font-size: 13px; font-weight: 700; letter-spacing: 0.15em; color: #4f8cff; text-transform: uppercase; }
.skill-tag { font-size: 11px; font-weight: 600; background: #1e1e35; border: 1px solid #2a2a4a; padding: 3px 10px; border-radius: 20px; color: #8888aa; letter-spacing: 0.1em; text-transform: uppercase; }
h1 { font-size: 28px; font-weight: 700; margin-bottom: 24px; color: #fff; }
h2 { font-size: 16px; font-weight: 600; margin-bottom: 16px; color: #b0b0cc; text-transform: uppercase; letter-spacing: 0.08em; }
.section { background: #1a1a2e; border: 1px solid #2a2a45; border-radius: 12px; padding: 24px; margin-bottom: 20px; }
.score-section { display: flex; align-items: center; gap: 40px; margin-bottom: 28px; }
.score-ring-wrap { flex-shrink: 0; }
.score-ring { width: 160px; height: 160px; border-radius: 50%; background: conic-gradient(var(--color) calc(var(--pct) * 1%), #2a2a3e 0); display: flex; align-items: center; justify-content: center; }
.score-inner { width: 120px; height: 120px; background: #12121f; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.score-num { font-size: 42px; font-weight: 800; line-height: 1; }
.score-label { font-size: 14px; color: #666; margin-top: 2px; }
.verdict { font-size: 20px; font-weight: 600; color: #e8e8f0; }
.verdict-wrap { padding: 20px; background: #1a1a2e; border: 1px solid #2a2a45; border-radius: 10px; }
.dim-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.dim-label { width: 160px; font-size: 14px; color: #b0b0cc; flex-shrink: 0; }
.dim-bar-wrap { flex: 1; background: #2a2a3e; border-radius: 5px; height: 10px; overflow: hidden; }
.dim-bar { height: 100%; border-radius: 5px; transition: width 0.3s; }
.dim-score { width: 50px; font-size: 14px; font-weight: 600; text-align: right; flex-shrink: 0; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
ul { list-style: none; }
ul li { padding: 8px 0; border-bottom: 1px solid #2a2a3e; font-size: 14px; }
ul li:last-child { border-bottom: none; }
ul li::before { content: "→ "; color: #4f8cff; }
.meta-row { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.pill { background: #4f8cff22; color: #4f8cff; border: 1px solid #4f8cff55; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; }
.pill-gray { background: #2a2a3e; color: #8888aa; border: 1px solid #3a3a5e; padding: 4px 12px; border-radius: 20px; font-size: 13px; }
.pill-high { background: #e5484d22; color: #e5484d; border: 1px solid #e5484d55; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; }
.pill-med { background: #f5a62322; color: #f5a623; border: 1px solid #f5a62355; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; }
.pill-low { background: #2a2a3e; color: #8888aa; border: 1px solid #3a3a5e; padding: 3px 10px; border-radius: 20px; font-size: 12px; }
.ad-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.ad-table th { text-align: left; padding: 10px 12px; border-bottom: 1px solid #2a2a45; color: #8888aa; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }
.ad-table td { padding: 10px 12px; border-bottom: 1px solid #1e1e35; vertical-align: top; }
.ad-table tr:hover td { background: #1e1e2e; }
.days { font-weight: 700; color: #4f8cff; white-space: nowrap; }
.hook { max-width: 320px; }
.dest { color: #888; max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.brand-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }
.brand-card { background: #12121f; border: 1px solid #2a2a45; border-radius: 10px; padding: 18px; }
.brand-name { font-size: 16px; font-weight: 700; margin-bottom: 6px; color: #fff; }
.brand-stats { font-size: 13px; color: #4f8cff; margin-bottom: 6px; }
.brand-ctas { font-size: 12px; color: #8888aa; margin-bottom: 6px; }
.brand-angle { font-size: 13px; color: #c0c0d8; font-style: italic; }
.angle-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.angle-table th { text-align: left; padding: 8px 12px; border-bottom: 1px solid #2a2a45; color: #8888aa; font-size: 12px; text-transform: uppercase; }
.angle-table td { padding: 10px 12px; border-bottom: 1px solid #1e1e35; }
.status-crowded { color: #e5484d; font-weight: 700; }
.status-contested { color: #f5a623; font-weight: 700; }
.status-open { color: #4CAF50; font-weight: 700; }
.gap-item { background: #12121f; border: 1px solid #2a2a45; border-radius: 10px; padding: 16px; margin-bottom: 12px; }
.gap-title { font-size: 15px; font-weight: 600; color: #4CAF50; margin-bottom: 6px; }
.gap-evidence { font-size: 13px; color: #b0b0cc; }
.finding { display: flex; align-items: flex-start; gap: 12px; padding: 10px 0; border-bottom: 1px solid #1e1e35; }
.finding:last-child { border-bottom: none; }
.finding-text { font-size: 14px; padding-top: 2px; }
.meta-score-row { background: #1a1a2e; border: 1px solid #2a2a45; border-radius: 8px; padding: 12px 20px; margin-bottom: 20px; font-size: 14px; color: #b0b0cc; }
"""


def render(data):
    kind = data["kind"]
    renderers = {
        "ad-score": render_ad_score,
        "spy": render_spy,
        "competitors": render_competitors,
        "ad-matter": render_ad_matter,
    }
    body = renderers[kind](data)
    title = htmllib.escape(data.get("ad_name", data.get("brand", data.get("account_name", "SCALE Ads"))))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — SCALE Ads</title>
<style>{CSS}</style>
</head>
<body>{body}</body>
</html>"""


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    out_html = render(json.load(open(a.data)))
    with open(a.out, "w") as f:
        f.write(out_html)
    print(f"[dashboard] wrote {a.out} ({len(out_html):,} bytes)")
    try:
        subprocess.run(["open", a.out], check=True)
    except Exception:
        pass
