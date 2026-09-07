# copilot-billing-report

Reads a GitHub Copilot billing usage CSV and shows how consumption is distributed
across users, how much of the recorded monthly quota is drawn, and which users are
over it.

One HTML file. No install, no runtime, no access token.

## Use

**Hosted:** <https://opticnerveai.github.io/spillwayops-tools/copilot-billing-report/>

**Local:** download `index.html` and open it. It behaves identically offline.

The hosted copy is served by GitHub Pages straight from this repository, so the
page you run is the source in this directory. Running your own copy is the
stronger option if you want to read the file once and know it cannot change
afterwards — the input is billing data, so that is a reasonable thing to want.

Open the page and drop the CSV on it. There is also a
synthetic-data button that renders the report shape without reading a file.

`sample-usage-report.csv` in this directory is a synthetic file in the documented
format — 25 invented users over six days, with an uneven distribution, three users
over quota, three with no usage, a request-metered row, a non-Copilot row, and a
quoted field containing a comma. Drop it on the page to see the report against a
file, or use it as a fixture when changing the parser. It contains no real data.

The file is parsed by JavaScript in the page. Nothing is uploaded, and the page
makes no network requests of any kind — there is no script, font, or stylesheet
loaded from anywhere, so this is verifiable by opening the network tab or by
reading the single file.

## Getting the CSV

An organization owner or billing manager can download it from GitHub without an
access token: **Settings → Billing & licensing → Usage**, then request a usage
report.

Note this is a different export from the Copilot *activity* report, which carries
only `report_time`, `login`, `last_authenticated_at`, `last_activity_at` and
`last_surface_used` — seat activity, with no consumption figures. This tool needs
the billing usage report.

## Expected columns

Columns are matched by header name. Unexpected columns are ignored; missing ones
are reported rather than guessed.

| Column | Used for |
|---|---|
| `username` | **Required.** Per-user attribution |
| `quantity` | **Required.** Billable units for the row |
| `unit_type` | **Required.** Whether the row is denominated in AI Credits or requests |
| `aic_quantity` | Usage converted to AI Credits — preferred over `quantity` when present |
| `total_monthly_quota` | The quota recorded for that user. Without it, quota utilization and unused capacity are omitted |
| `exceeds_quota` | Over-quota flag, as recorded by GitHub |
| `product` | Rows whose product is not Copilot are skipped |
| `model` | The credits-by-model breakdown |
| `net_amount` | Net charge total |
| `date` | The period the report covers |
| `sku`, `organization`, `cost_center_name`, `applied_cost_per_quantity`, `gross_amount`, `discount_amount`, `aic_gross_amount` | Read but not currently summarised |

Schema per GitHub's published billing report format.

## Reading the report

| Figure | What it is |
|---|---|
| Users | Distinct usernames with at least one Copilot row |
| Credits consumed | Sum of AI-credit usage across those users |
| Monthly quota | Sum of the per-user quotas recorded in the file |
| Quota utilization | Credits consumed ÷ monthly quota |
| Unused quota | Monthly quota − credits consumed, over the period the file covers |
| Share drawn by the heaviest 10% / 20% | Portion of total consumption drawn by that fraction of users, heaviest first |
| Median user | Credits drawn by the middle user |
| Heaviest user | Credits drawn by the single largest consumer |
| Users with zero usage | Usernames present in the file with no credit consumption |
| Over quota | Users whose consumption exceeds the quota recorded for them, or whose `exceeds_quota` is true, and the total by which they exceed it |
| Request-metered units | Rows denominated in requests rather than credits, counted separately and never added to a credit total |
| Credits by model | Credit consumption grouped by the `model` column |

Per-user figures are capacity data. Credit consumption varies with which features
someone uses — agent tasks and premium models draw credits, ordinary completions
do not — so the figures describe capacity draw, not output or performance.

## Caveats

- **The file is the authority.** Quota comes from `total_monthly_quota` in the CSV,
  not from a table in this tool. Nothing here needs updating when published
  allowances change.
- **The period is whatever the file covers.** Unused quota is quota minus what was
  drawn in the rows supplied. A partial month reads as low utilization because it is.
- **Request-metered rows are not credits.** They are reported separately rather than
  converted, because the conversion depends on model and is not in the file.
- **Export formats change.** If a required column is absent the tool names it and
  stops rather than inferring. Corrections by pull request are welcome.

## Licence

MIT — see [LICENSE](../LICENSE). Copyright (c) 2026 Optic Nerve AI, LLC.
