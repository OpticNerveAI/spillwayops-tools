# copilot-usage-audit

Reads GitHub Copilot seat and usage data for an organization or enterprise and
prints a distribution report.

One Python file, no dependencies, read-only.

`python3 copilot-usage-audit.py --demo --plan enterprise`

```
  Seats                      120
  Included allowance         3,900 credits/user/month
  Monthly pool               468,000 credits
  Consumed month-to-date     116,944 credits
  Pool utilization            25.0 %  ████████························
  Expiring unused            351,056 credits

  Distribution
    Top 10% of users          53.2 % of consumption  █████████████████···············
    Top 20% of users          75.0 % of consumption  ████████████████████████········
    Median user              339 credits
    Heaviest user            8,636 credits
```

## Install

Nothing to install. Download the file and run it.

```bash
curl -O https://raw.githubusercontent.com/OpticNerveAI/spillwayops-tools/main/copilot-usage-audit/copilot-usage-audit.py
python3 copilot-usage-audit.py --demo
```

Python 3.8+. Standard library only.

## Use

```bash
# synthetic data — no token, no network calls
python3 copilot-usage-audit.py --demo

# an organization
export GITHUB_TOKEN=ghp_...
python3 copilot-usage-audit.py --org my-org

# an enterprise, using the Enterprise allowance
python3 copilot-usage-audit.py --enterprise my-enterprise --plan enterprise

# override the allowance, and write the raw figures to a file
python3 copilot-usage-audit.py --org my-org --entitlement 2500 --json audit.json
```

### Token scopes

Classic PAT: `manage_billing:copilot` for an organization, or
`manage_billing:enterprise` for an enterprise. Fine-grained token: the
organization **GitHub Copilot Business** permission, read access.

Read access is sufficient. Write access is not required.

## What it reads, and what it does not

| Does | Does not |
|---|---|
| `GET` Copilot seat assignments and last-activity timestamps | Write anything, anywhere |
| `GET` the billing usage report for Copilot line items | Access repositories, code, or diffs |
| Compute distribution statistics locally | Read prompts, completions, or chat contents |
| Print to the terminal, and to a file on request | Send data to any third party |

The only host it contacts is `api.github.com`. There is no telemetry and no
network call at all in `--demo` mode. The program is a single file of
standard-library Python.

## Reading the report

| Figure | What it is |
|---|---|
| Seats | Copilot seats assigned in the organization or enterprise |
| Included allowance | Credits per user per month used for the calculation — from `--plan`, or `--entitlement` if given |
| Monthly pool | Seats × included allowance |
| Consumed month-to-date | Credits drawn so far in the current billing month |
| Pool utilization | Consumed ÷ monthly pool |
| Expiring unused | Monthly pool − consumed, at the current point in the month |
| Top 10% / 20% of users | Share of total consumption drawn by the heaviest decile and quintile |
| Median user | Credits drawn by the middle user |
| Heaviest user | Credits drawn by the single largest consumer |
| Users with zero usage | Assigned seats with no recorded consumption this month |
| Seats with no activity in 30 days | Assigned seats with no Copilot activity in the trailing 30 days |
| Users above allowance | Users who drew more than the included per-user allowance, and the total by which they exceeded it |
| Notes | Anything the script could not retrieve, and how it compensated |

`--json` writes the same figures as structured data.

Per-user figures are capacity data. Credit consumption varies with which
features someone uses — agent tasks and premium models draw credits, ordinary
completions do not — so the figures describe capacity draw, not output or
performance.

## Caveats

- **Allowance figures are defaults.** `ENTITLEMENTS` in the script carries
  published standard amounts; pass `--entitlement` if an agreement differs.
  Verify against
  [GitHub's billing documentation](https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-organizations-and-enterprises).
- **Endpoint shapes change.** If the usage endpoint returns nothing, the script
  reports that in its Notes and falls back to seat activity rather than guessing.
- **Month-to-date, not projected.** Consumption is what has been drawn so far in
  the current month. Early in a month, utilization reads low because it is.
- **"Above allowance" is a threshold count, not history.** It counts users who
  drew more than the included per-user allowance. It does not describe what any
  configured budget or cap actually did.

## Contributing

Corrections to the allowance table, endpoint shapes, or the statistics are
welcome. If your data produces an incorrect report, an issue with redacted
`--json` output is the most useful thing to file.

## Licence

MIT — see [LICENSE](../LICENSE). Copyright (c) 2026 Optic Nerve AI, LLC.
