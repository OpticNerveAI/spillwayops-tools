#!/usr/bin/env python3
"""
copilot-usage-audit — see where your GitHub Copilot capacity actually goes.

Reads your organization's or enterprise's Copilot seat and usage data and prints
a distribution report: who consumes what, how much of the pooled allowance went
unused, and how many developers would be blocked by an even per-user cap.

  READ-ONLY.  This script issues GET requests only. It never writes to GitHub,
  never touches repositories, never reads prompts or code, and sends your data
  nowhere — the report is printed locally and, optionally, written to a file you
  name. There are no third-party dependencies; everything below is the Python
  standard library, so you can read the whole thing before you run it.

Usage
-----
    export GITHUB_TOKEN=ghp_...
    python3 copilot-usage-audit.py --org my-org
    python3 copilot-usage-audit.py --enterprise my-enterprise --plan enterprise
    python3 copilot-usage-audit.py --demo            # synthetic data, no token

Token scopes (classic PAT): `manage_billing:copilot` for an organization, or
`manage_billing:enterprise` for an enterprise. Fine-grained tokens need the
organization "GitHub Copilot Business" permission (read). Read access is enough;
do not grant write.

MIT licensed. Issues and corrections welcome — including to the assumptions in
ENTITLEMENTS below, which change when GitHub changes them.
"""

import argparse
import json
import os
import random
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

API = "https://api.github.com"
UA = "copilot-usage-audit/1.0 (+https://github.com/OpticNerveAI/spillwayops-tools)"

# Included AI credits per user per month, as published by GitHub for the
# standard (post-promotional) allowance effective 1 September 2026. Override
# with --entitlement if your agreement differs. Verify against:
# https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-organizations-and-enterprises
ENTITLEMENTS = {"business": 1900, "enterprise": 3900}

DORMANT_DAYS = 30


# --------------------------------------------------------------------------
# HTTP — plain urllib so there is nothing to audit but this file
# --------------------------------------------------------------------------

class ApiError(Exception):
    def __init__(self, status, path, message):
        super().__init__(f"{status} on {path}: {message}")
        self.status, self.path, self.message = status, path, message


def get(path, token, params=None):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": UA,
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode()), dict(r.headers)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            msg = json.loads(body).get("message", body[:200])
        except Exception:
            msg = body[:200]
        raise ApiError(e.code, path, msg)
    except urllib.error.URLError as e:
        raise ApiError(0, path, f"network error: {e.reason}")


def get_paged(path, token, params=None, item_key=None, cap=50):
    """Follow Link: rel=next. item_key pulls the list out of an object response."""
    out, page, params = [], 1, dict(params or {})
    params.setdefault("per_page", 100)
    while page <= cap:
        params["page"] = page
        data, headers = get(path, token, params)
        chunk = data.get(item_key, []) if isinstance(data, dict) and item_key else data
        if not isinstance(chunk, list):
            return out
        out.extend(chunk)
        if 'rel="next"' not in headers.get("Link", ""):
            break
        page += 1
    return out


# --------------------------------------------------------------------------
# Collection. Endpoints move; each of these degrades to None with a stated
# reason rather than guessing, and the report says what it could not see.
# --------------------------------------------------------------------------

def fetch_seats(scope, name, token, notes):
    path = f"/{scope}/{name}/copilot/billing/seats"
    try:
        return get_paged(path, token, item_key="seats")
    except ApiError as e:
        notes.append(f"seat detail unavailable ({e.status}: {e.message})")
        return []


def fetch_billing_usage(scope, name, token, notes):
    """Enhanced-billing usage report. Shape varies; we normalise defensively."""
    year, month = datetime.now(timezone.utc).year, datetime.now(timezone.utc).month
    candidates = [
        (f"/{'organizations' if scope == 'orgs' else scope}/{name}/settings/billing/usage",
         {"year": year, "month": month}),
        (f"/{scope}/{name}/settings/billing/usage", {"year": year, "month": month}),
    ]
    for path, params in candidates:
        try:
            data, _ = get(path, token, params)
            items = data.get("usageItems") or data.get("usage_items") or []
            if items:
                return items
        except ApiError as e:
            last = e
            continue
    notes.append("per-user credit consumption unavailable from the billing usage "
                 f"endpoint ({getattr(locals().get('last', None), 'message', 'no data returned')}). "
                 "Falling back to seat activity only — concentration figures will be omitted.")
    return []


def normalise_usage(items):
    """Sum Copilot premium-request / AI-credit quantity per username."""
    per_user, total = {}, 0.0
    for it in items:
        product = str(it.get("product") or it.get("sku") or "").lower()
        if "copilot" not in product and "premium" not in product:
            continue
        who = it.get("username") or it.get("actor") or it.get("user") or "(unattributed)"
        qty = it.get("quantity") or it.get("grossQuantity") or it.get("gross_quantity") or 0
        try:
            qty = float(qty)
        except (TypeError, ValueError):
            continue
        per_user[who] = per_user.get(who, 0.0) + qty
        total += qty
    return per_user, total


def demo_data():
    """Synthetic org with a realistic power-law shape, for seeing the output."""
    rnd = random.Random(11)
    names = [f"dev-{i:03d}" for i in range(1, 121)]
    per_user = {}
    for i, n in enumerate(names):
        if i < 6:                      # heavy adopters
            per_user[n] = rnd.uniform(4200, 9000)
        elif i < 24:                   # steady agent users
            per_user[n] = rnd.uniform(1500, 3800)
        elif i < 84:                   # completions-mostly
            per_user[n] = rnd.uniform(80, 900)
        else:                          # dormant / trivial
            per_user[n] = rnd.uniform(0, 40)
    now = datetime.now(timezone.utc)
    seats = [{"assignee": {"login": n},
              "last_activity_at": (now - timedelta(days=rnd.choice([0, 1, 2, 5, 9, 20, 45, 90])))
              .isoformat().replace("+00:00", "Z")} for n in names]
    return seats, per_user, sum(per_user.values())


# --------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------

def dormant_count(seats):
    cutoff, dormant, unknown = datetime.now(timezone.utc) - timedelta(days=DORMANT_DAYS), 0, 0
    for s in seats:
        ts = s.get("last_activity_at")
        if not ts:
            unknown += 1
            continue
        try:
            when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            unknown += 1
            continue
        if when < cutoff:
            dormant += 1
    return dormant, unknown


def analyse(seats, per_user, total, entitlement):
    seat_count = len(seats) or len(per_user)
    pool = entitlement * seat_count if seat_count else 0
    values = sorted(per_user.values(), reverse=True)
    n = len(values)

    a = {
        "seats": seat_count,
        "entitlement": entitlement,
        "pool": pool,
        "consumed": total,
        "unused": max(pool - total, 0),
        "utilization": (total / pool) if pool else None,
        "users_with_usage": n,
    }
    if n:
        top10 = values[:max(1, n // 10)]
        top20 = values[:max(1, n // 5)]
        a["top10_share"] = sum(top10) / total if total else 0
        a["top20_share"] = sum(top20) / total if total else 0
        a["zero_users"] = sum(1 for v in values if v <= 0)
        # The number that matters: under a strict even per-user cap (pool/seats,
        # i.e. the entitlement), these developers would have been cut off.
        a["over_even_share"] = sum(1 for v in values if v > entitlement)
        a["over_share_excess"] = sum(v - entitlement for v in values if v > entitlement)
        a["median"] = values[n // 2]
        a["max"] = values[0]
    return a


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def bar(frac, width=32):
    filled = int(round(max(0.0, min(1.0, frac)) * width))
    return "█" * filled + "·" * (width - filled)


def fmt(n):
    return f"{n:,.0f}"


def report(a, notes, label):
    L = []
    add = L.append
    add("")
    add("=" * 66)
    add(f" Copilot capacity audit — {label}")
    add(f" {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ·  read-only  ·  nothing left this machine")
    add("=" * 66)

    add("")
    add(f"  Seats                      {fmt(a['seats'])}")
    add(f"  Included allowance         {fmt(a['entitlement'])} credits/user/month")
    add(f"  Monthly pool               {fmt(a['pool'])} credits")

    if a["consumed"] or a.get("users_with_usage"):
        add(f"  Consumed month-to-date     {fmt(a['consumed'])} credits")
        if a["utilization"] is not None:
            add(f"  Pool utilization           {a['utilization']*100:5.1f} %  {bar(a['utilization'])}")
            add(f"  Expiring unused            {fmt(a['unused'])} credits")

    if "top10_share" in a:
        add("")
        add("  Distribution")
        add(f"    Top 10% of users         {a['top10_share']*100:5.1f} % of consumption  {bar(a['top10_share'])}")
        add(f"    Top 20% of users         {a['top20_share']*100:5.1f} % of consumption  {bar(a['top20_share'])}")
        add(f"    Median user              {fmt(a['median'])} credits")
        add(f"    Heaviest user            {fmt(a['max'])} credits")
        add(f"    Users with zero usage    {fmt(a['zero_users'])}")

    dormant = a.get("dormant")
    if dormant is not None:
        add("")
        add(f"  Seats with no activity in {DORMANT_DAYS} days   {fmt(dormant)}"
            + (f"  ({dormant / a['seats'] * 100:.0f}% of seats)" if a["seats"] else ""))
        if a.get("dormant_unknown"):
            add(f"  Seats with no activity timestamp        {fmt(a['dormant_unknown'])}")

    # The finding.
    if "over_even_share" in a and a["pool"]:
        add("")
        add("-" * 66)
        add("  THE SHAPE OF THE PROBLEM")
        add("")
        add(f"    {fmt(a['over_even_share'])} developers consumed more than the included per-user")
        add(f"    allowance ({fmt(a['entitlement'])} credits) — by {fmt(a['over_share_excess'])} credits in total.")
        add("")
        add(f"    Meanwhile {fmt(a['unused'])} credits in the shared pool are on course")
        add("    to expire unused at 00:00 UTC on the 1st.")
        add("")
        if a["over_even_share"] and a["unused"] > 0:
            covered = min(a["unused"], a["over_share_excess"])
            add(f"    The unused pool covers {covered/a['over_share_excess']*100:.0f}% of that excess.")
            add("    A per-user cap set at the allowance would have blocked those")
            add("    developers while this capacity expired in the same month.")
        add("-" * 66)

    if notes:
        add("")
        add("  Notes")
        for nte in notes:
            add(f"    - {nte}")

    add("")
    add("  What this does not tell you: which requests were worth making. Credit")
    add("  counts are not a productivity measure, and this report is deliberately")
    add("  aggregate — treat per-user figures as capacity planning input, not as")
    add("  individual performance data.")
    add("")
    add("  Audit script by Spillway Ops — https://github.com/OpticNerveAI/spillwayops-tools")
    add("")
    return "\n".join(L)


# --------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        description="Read-only audit of GitHub Copilot capacity distribution.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--org", help="organization login")
    g.add_argument("--enterprise", help="enterprise slug")
    g.add_argument("--demo", action="store_true", help="synthetic data; no token needed")
    p.add_argument("--plan", choices=sorted(ENTITLEMENTS), default="business",
                   help="included allowance to assume (default: business)")
    p.add_argument("--entitlement", type=int,
                   help="override credits/user/month explicitly")
    p.add_argument("--json", metavar="FILE", help="also write the raw figures as JSON")
    p.add_argument("--token", help="GitHub token (default: $GITHUB_TOKEN)")
    args = p.parse_args()

    entitlement = args.entitlement or ENTITLEMENTS[args.plan]
    notes = []

    if args.demo:
        seats, per_user, total = demo_data()
        label = "DEMO (synthetic data)"
        notes.append("Demo mode: figures are invented to show the report's shape.")
    else:
        token = args.token or os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("No token. Set GITHUB_TOKEN or pass --token. "
                     "Needs manage_billing:copilot (org) or manage_billing:enterprise.")
        scope = "orgs" if args.org else "enterprises"
        name = args.org or args.enterprise
        label = f"{'organization' if args.org else 'enterprise'} {name}"
        print(f"Reading {label} (read-only)...", file=sys.stderr)
        seats = fetch_seats(scope, name, token, notes)
        per_user, total = normalise_usage(fetch_billing_usage(scope, name, token, notes))
        if not seats and not per_user:
            sys.exit("Could not read seat or usage data. Check the token's scopes and "
                     "that Copilot billing is managed at this level.\n  " +
                     "\n  ".join(notes))

    a = analyse(seats, per_user, total, entitlement)
    if seats:
        d, u = dormant_count(seats)
        a["dormant"], a["dormant_unknown"] = d, u

    print(report(a, notes, label))

    if args.json:
        with open(args.json, "w") as f:
            json.dump({"generated": datetime.now(timezone.utc).isoformat(),
                       "scope": label, **a}, f, indent=2)
        print(f"Wrote {args.json}", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
