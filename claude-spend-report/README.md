# claude-spend-report

Reads the spend report CSV exported from a Claude Team or Enterprise organization
and shows how usage-credit spend is distributed across members, by product and by
model, and which members are at or over a per-member limit you type in.

One HTML file. No install, no runtime, no access token.

## Use

**Hosted:** [https://opticnerveai.github.io/spillwayops-tools/claude-spend-report/index.html](https://opticnerveai.github.io/spillwayops-tools/claude-spend-report/index.html)

**Local:** download `index.html` and open it. It behaves identically offline.

The hosted copy is served by GitHub Pages straight from this repository, so the
page you run is the source in this directory. Running your own copy is the
stronger option if you want to read the file once and know it cannot change
afterwards. The input is spend data attributed to named people, so that is a
reasonable thing to want.

Open the page and drop the CSV on it. There is also a synthetic-data button that
renders the report shape without reading a file.

`sample-spend-report.csv` in this directory is a synthetic file in the documented
format: 48 invented members over an uneven distribution, four products and four
models, several members at or over a plausible per-member limit, an organization
service usage row, and a quoted product field containing commas. Drop it on the
page to see the report against a file, or use it as a fixture when changing the
parser. It contains no real data.

The file is parsed by JavaScript in the page. Nothing is uploaded, and the page
makes no network requests of any kind. There is no script, font, or stylesheet
loaded from anywhere, so this is verifiable by opening the network tab or by
reading the single file.

## Getting the CSV

An Owner or Primary Owner exports it from claude.ai without an access token:
**Settings → Analytics → "How much is Claude costing?" → Export spend report**,
choosing month to date, last month, the last 90 days, or a custom range of up to
90 days. The most recent data is from the previous day. The export is available
once usage credits are turned on for the organization. On Enterprise plans,
Admins can open Analytics but cannot see spend, so they cannot export this file.

Note this is a different export from the Claude Code *analytics* export under
Analytics → Claude Code, which carries members' email addresses and lines of
code accepted, with no spend figures. If that file is dropped on the page, the
page names it and stops. This tool needs the spend report.

## Expected columns

Columns are matched by header name, case-insensitively. Unexpected columns are
ignored; missing ones are reported rather than guessed. The Help Center describes
every field below; the header spellings marked confirmed were read from a real
export, and the two marked documented are the spellings the tool looks for
first, with the aliases it also accepts.

| Column | Status | Used for |
|---|---|---|
| `user_email` | confirmed | **Required.** Per-member attribution. Aliases: `email`, `user`, `member_email` |
| `total_net_spend_usd` | confirmed | **Required.** Spend after discounts and credits, the figure every distribution uses |
| `total_gross_spend_usd` | confirmed | Spend before discounts; the difference is reported as discounts and credits |
| `product` | confirmed | Spend by product (Chat, Claude Code, Cowork, Office Agents) |
| `model` | confirmed | Spend by model. Rows with an empty model are skipped and their spend reported |
| `total_requests` | confirmed | Request totals |
| `total_prompt_tokens`, `total_completion_tokens` | confirmed | Token totals per member. Aliases: `input_tokens`, `output_tokens` |
| account UUID | documented | Read as `account_uuid` (aliases `account_id`, `uuid`); not currently summarized |
| model family | documented | Read as `model_family` (alias `family`); not currently summarized |

Each row of the export is one member's use of one model on one product, summed
over the period chosen at export. Rows whose member is `(org service usage)` are
summed separately as organization service usage and never attributed to a person.

## Reading the report

| Figure | What it is |
|---|---|
| Members with spend | Distinct member emails with at least one row |
| Net spend | Sum of net spend across those members |
| Gross spend, Discounts and credits | Sum of gross spend, and gross minus net |
| Requests, Prompt tokens, Completion tokens | Sums of those columns where present |
| Organization service usage | Net spend on rows not attributed to a member |
| Share drawn by the heaviest 10% / 20% | Portion of net spend drawn by that fraction of members, heaviest first |
| Median member | Net spend of the middle member |
| Heaviest member | Net spend of the single largest spender |
| Seats with no spend | Your typed seat count minus members with spend. Shown only when a seat count is typed, and labeled as based on it |
| At or over the limit | Members whose net spend is at or above the per-member monthly limit you typed, and the total by which they exceed it. Members at 80% or more of the limit are counted beside them. Shown only when a limit is typed |
| Spend by member | The 25 heaviest members, with all members in the table below |
| Net spend by product, by model | Net spend grouped by the `product` and `model` columns |

Per-member figures are capacity data. Spend varies with which products and
models someone uses and how they work, so the figures describe capacity draw,
not output or performance.

## Caveats

- **The file carries usage-credit spend only on Team and seat-based Enterprise
  plans.** Usage inside the included seat allowance is not metered in dollars and
  is not in the export, so on those plans this report reads who is buying past
  their allowance and how much. On usage-based Enterprise plans the export covers
  all usage. An organization with usage credits turned off has no spend report to
  export.
- **The limit and the seat count are yours.** Neither is in the file. The report
  compares every member with the one limit you type; it cannot see the limit each
  member actually has, which may differ by seat tier, group, or individual override.
- **The period is whatever the export covers.** There is no date column. A
  month-to-date export read on the 10th reads as low spend because it is.
- **Net is after discounts and credits.** Gross is before. Analytics, the export,
  and the invoice should closely match, per the vendor, but this page is not the
  invoice.
- **Export formats change.** If a required column is absent the tool names it and
  stops rather than inferring. Corrections by pull request are welcome, especially
  the exact header spellings of the account UUID and model family columns.

## License

MIT — see [LICENSE](../LICENSE). Copyright (c) 2026 Optic Nerve AI, LLC · [www.spillwayops.com](https://www.spillwayops.com)
