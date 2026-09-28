# usage-report

Reads a per-member usage CSV from any AI coding vendor and shows how usage is
distributed across members: how much the heaviest fifth draws, who is at or over
an allowance, whose allowance went unused, and how many seats recorded no usage.
GitHub's Copilot usage reports and the Claude spend report are recognized by
their header rows. Any other per-member CSV, including Cursor and Codex exports,
goes through a column mapper that you confirm.

One HTML file. No install, no runtime, no access token.

## Use

**Hosted:** [https://opticnerveai.github.io/spillwayops-tools/usage-report/index.html](https://opticnerveai.github.io/spillwayops-tools/usage-report/index.html)

**Local:** download `index.html` and open it. It behaves identically offline.

The hosted copy is served by GitHub Pages straight from this repository, so the
page you run is the source in this directory. Running your own copy is the
stronger option if you want to read the file once and know it cannot change
afterwards. The input is usage data attributed to named people, so that is a
reasonable thing to want.

Open the page and drop one or more CSV files on it, or choose them with the file
picker. There is also a synthetic-data button that renders the report shape
without reading a file, and the report it draws is labeled as synthetic.

`sample-usage.csv` in this directory is a synthetic file with generic headers
(`Member`, `Seat type`, `Period`, `Product`, `Model`, `Credits used`,
`Included allowance`): 32 invented members over an uneven distribution, three
Premium seats with a larger allowance, two members over their allowance, most of
the rest well under it, three with no usage, and a quoted product field
containing a comma. It matches no verified export, so dropping it opens the
column mapper with every choice pre-selected from the header names for you to
confirm. It contains no real data.

The files are parsed by JavaScript in the page. Nothing is uploaded, and the
page makes no network requests of any kind. There is no script, font, or
stylesheet loaded from anywhere, so this is verifiable by opening the network
tab or by reading the single file. Files over 20 MB are refused by name.

## Getting each vendor's export

The tool's guidance panel says the same things with the same sources. Each
statement traces to the vendor page linked beside it.

### GitHub Copilot

An enterprise owner, organization owner or billing manager opens
**Billing & Licensing → Usage → AI usage** in GitHub, selects **Get usage
report**, and receives the AI usage report by email, as a link that expires
after 24 hours, with no token
([Viewing your usage of metered products and licenses](https://docs.github.com/en/billing/how-tos/products/view-productlicense-use)).
The report breaks AI credits down per user, date and model over at most 31 days,
with the tokens behind each model's credits, and has no per-user quota column
([Billing reports reference](https://docs.github.com/en/billing/reference/billing-reports)),
so type an allowance to see who is at or over it. Since June 2026, consumption
is metered in AI credits pooled at the billing entity, at one credit per cent,
and the pool resets on the first of each month with unused credits forfeited
([Usage-based billing for organizations and enterprises](https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-organizations-and-enterprises)).

The billing usage CSV of GitHub's usage-based billing preview carries each
user's monthly quota and the usage converted to AI credits
([Copilot billing preview report format](https://github.com/github/copilot-billing-preview/blob/main/docs/report-format.md));
it is recognized too, and there the allowance figures come from the file. The
[Copilot billing report](../copilot-billing-report/) in this repository reads
that file with the same preset. Neither is the Copilot activity report, which
lists each user's last activity and last surface used with no consumption
figures ([Metrics data properties for GitHub Copilot](https://docs.github.com/en/copilot/reference/metrics-data));
the tool names that file and stops. The usage dashboard and the metrics API are
a different view of the same activity, updated within two full days and
dependent on IDE telemetry ([Copilot metrics and the usage dashboard](https://docs.github.com/copilot/concepts/copilot-metrics)).

### Claude Code

An Owner or Primary Owner exports the spend report from claude.ai under
**Settings → Analytics → "How much is Claude costing?" → Export spend report**,
choosing month to date, last month, the last 90 days, or a custom range. The
export lists each member's use of each model with requests, prompt and completion
tokens, and net and gross spend, summed over the window; spend data refreshes
daily with a one-day delay, and on Enterprise plans Admins can open Analytics but
cannot view spend ([View usage analytics for Team and Enterprise plans](https://support.claude.com/en/articles/12883420-view-usage-analytics-for-team-and-enterprise-plans)).
On Team and seat-based Enterprise plans the report covers usage-credit spend
only, which appears once usage credits are turned on, because usage inside the
seat allowance is not metered in dollars ([Manage costs effectively](https://code.claude.com/docs/en/costs),
[Manage usage credits for Team and seat-based Enterprise plans](https://support.claude.com/en/articles/12005970-manage-usage-credits-for-team-and-seat-based-enterprise-plans)).
The file has no date column and no per-member limit. The Claude Code analytics
export under Analytics → Claude Code carries member emails and lines of code
with no spend; the tool names that file and stops. The
[Claude spend report](../claude-spend-report/) in this repository reads the same
file with the same preset.

### Cursor

On Teams, an Admin opens the dashboard's Usage page and selects **Export CSV**
above the events table. The file lists requests, with the member in a `User`
column and the charge in a `Cost` column: a dollar figure for on-demand usage, and
the word `Included` for usage the plan covers, where nothing is charged. Summing
the Cost column gives the spend for the range. A member who has left the team, or
whose record does not resolve, appears by a numeric user ID instead of an email.
These statements come from Cursor staff on Cursor's forum
([New Spending/Usage tabs no longer shows $ spent](https://forum.cursor.com/t/166548),
[Usage Page $$ to Token Amount? WHAT?](https://forum.cursor.com/t/167153),
[Question About Numeric User IDs in Exported Usage Details](https://forum.cursor.com/t/167128),
[Remaining budget and spending unclear on Dashboard](https://forum.cursor.com/t/169020));
no Cursor documentation page lists the columns of this file. The tool reads a
Cost cell of `Included`, `Free` or `-` as zero and counts those cells by name in
the report, so the Cost total is on-demand spend.

The dashboard's analytics page also offers a CSV download per chart, with the
daily usage chart covering the preceding 365 days, filtered to at most ten users
and 90 continuous days at a time, with data collected only from clients on
version 1.5 or higher ([Analytics](https://cursor.com/docs/account/teams/analytics)).
The page does not list the columns of these downloads. Members have no access to
the admin dashboard ([Members, Roles, and Seat Types](https://cursor.com/docs/account/teams/members)).
On Team and Enterprise plans ([Dashboard](https://cursor.com/docs/account/teams/dashboard)),
the Admin API returns per-user on-demand spend in cents, total spend including
included usage, daily per-user usage over at most 30 days, and per-request usage
events; it needs an API key and this page never calls it
([Admin API](https://cursor.com/docs/account/teams/admin-api)). Ten users per
filter means a team of forty is at least four files exported from the same chart;
drop them together and the tool combines them when the header rows are identical.
Included usage and on-demand spend are separate figures in Cursor's dashboard
([Team Pricing](https://cursor.com/docs/account/teams/pricing)); label the unit
with whichever the file you exported shows. The AI Code Tracking API's
`commits.csv` and `changes.csv` count lines of code with no usage amounts
([AI Code Tracking API](https://cursor.com/docs/account/teams/ai-code-tracking-api));
the tool names them and stops. No Cursor export has been verified against this
tool, so the mapper opens.

### Codex

On ChatGPT Business, workspace analytics shows usage by member, including seat
type, credits spent and messages sent, over seven days, one month, six months,
twelve months, or a custom window ([ChatGPT Business Release Notes](https://help.openai.com/en/articles/11391654-chatgpt-business-release-notes)),
and Owners download usage reports under Billing ([Flexible pricing for the Enterprise, Edu, and Business plans](https://help.openai.com/en/articles/11487671-flexible-pricing-for-the-enterprise-edu-and-business-plans)).
On Enterprise, the Admin Console breaks credit spend down by user, product and
model, with a Cost API ([New usage analytics and updated spend controls for enterprises](https://openai.com/index/chatgpt-enterprise-spend-controls/)).
On Enterprise and Edu, workspace analytics exports CSV reports covering up to
twelve months, refreshed every one to 24 hours; the Users export is a per-member
report whose documented columns include `email`, `seat_type`, `messages` and
`period_start`, and none of its documented columns carries credits or dollars
([Workspace analytics for ChatGPT Enterprise and Edu](https://help.openai.com/en/articles/10875114)).
No cited page lists the columns of the Business member table or of the Billing
usage reports, or says that the member table can be exported. Usage inside a seat's five-hour and weekly windows is not metered in dollars;
only usage past them draws credits, at a rate card in credits per million tokens
([ChatGPT Rate Card](https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing)).
What a credit costs in dollars depends on the plan or agreement
([Pricing](https://learn.chatgpt.com/docs/pricing)), and no cited page prices a
Business credit, so the tool never supplies a dollar rate for Codex credits. No
Codex export has been verified against this tool, so the mapper opens, with the
Users export's `email`, `messages`, `period_start` and `seat_type` columns
pre-selected for you to confirm.

## Verified presets

A preset is a header set that has been verified against a real export or the
vendor's documented column list. A file whose headers match a preset is mapped
without asking, and the report names the export it recognized. Three presets
exist: the two files the vendor tools in this repository already read, and
GitHub's AI usage report, by the columns GitHub documents for it:

| Preset | Recognized by | Read as |
|---|---|---|
| GitHub AI usage report | `username`, `quantity`, `unit_type` and `model`, with at least one of `input`, `output`, `cache_read` and `cache_write` | Read as the billing usage CSV below. The file has no quota column, so a typed allowance is the only allowance. |
| GitHub Copilot billing usage CSV | `username`, `quantity` and `unit_type`, with at least one of `aic_quantity`, `total_monthly_quota` and `exceeds_quota` | Member from `username`; amount in AI credits from `aic_quantity`, or from `quantity` on rows whose `unit_type` is not requests, as GitHub's billing preview documents the field; allowance from `total_monthly_quota` on rows in AI credits; `model` and `date`; dollars from the file's own `net_amount` column. Rows whose `product` is not Copilot are set aside, and request-metered rows are counted separately and never added to credits. A file with no credit rows at all, from before AI credits, is read in premium requests instead: `quantity` is the amount and `total_monthly_quota` the allowance, both in requests. |
| Claude spend report | A member column (`user_email`, `email`, `user`, `member_email`, `member` or `user email`) and a net spend column (`total_net_spend_usd`, `net_spend_usd`, `total_net_spend` or `net_spend`), with `product` or `model` | Member from the member column; amount in dollars from the net spend column; `product` and `model`. Organization service usage rows and rows with no model are set aside and reported. |

The billing usage CSV and Claude alias lists are copied from the two vendor
tools; the AI usage report's columns are those in GitHub's
[Billing reports reference](https://docs.github.com/en/billing/reference/billing-reports).
Headers are matched case-insensitively after trimming.

**No other vendor is recognized.** A preset for Cursor or Codex is added only
after a real export, or the vendor's documented column list, has confirmed the
header row. Until then those files go through the mapper, and the redacted
summary described below is how a verified header set reaches this repository.

Three known exports from the same vendors carry no usage amounts and are named
rather than reported as a missing column: the Claude Code analytics export
(member emails and lines of code), the Copilot activity report (seat
activity), and Cursor's AI Code Tracking CSVs (`commits.csv` and `changes.csv`,
recognized by the columns Cursor's API reference lists). For each, the tool
names the file it needs and where it comes from. A file with lines-of-code
columns is named as the Claude Code analytics export only when no column could
be an amount (spend, cost, credits, amount, quantity, usage, or request counts
other than pull requests), so a Cursor analytics or daily usage export, which
carries both, goes to the mapper. If the detection is wrong for your file, a
button opens the mapper anyway.

## The mapping model

Any file that matches no preset opens the mapper. Every choice is a column of
the file, chosen from a list of its headers.

| Field | Required | Used for |
|---|---|---|
| Member | Yes | Rows are summed by this column. Its values never appear in the redacted summary. |
| Amount | Yes | The figure every distribution uses, in the unit you label. Every cell is parsed before anything is drawn. |
| Date | No | The period the report covers, shown as the earliest and latest value. |
| Allowance | No | A per-member allowance or limit recorded in the file; the largest value per member is used. |
| Product | No | A breakdown of the total by this column. |
| Model | No | A breakdown of the total by this column. |
| Seat type | No | A breakdown by seat type, and a column in the member table. |

A header that matches a generic name, or a field the vendor pages describe for
Cursor and Codex exports (member, seat type, credits spent, spend in cents,
on-demand spend, included usage), is pre-selected and marked as such. Headers are
compared after splitting camelCase and treating underscores, hyphens, dots and
parentheses as spaces, so `spendCents`, `spend_cents` and `Spend (cents)` match
alike. Cursor's included usage is usage, so it is offered as an amount, never as
an allowance. Pre-selection is a convenience and never a
recognition: the report is drawn only when you choose to draw it. The first five
rows of the chosen columns are shown before you do.

Validation stops the report and names the problem:

- A missing member or amount choice is named, and nothing is drawn.
- Every cell of the amount column is parsed. A cell that is not a number stops
  the report with the column, the count of failing cells, and an example. A blank
  cell is read as zero and the count of blank cells is shown in the report. A
  cell reading `Included`, `Free` or `-` is also read as zero, and the report
  counts each by name: Cursor's usage export writes `Included` in its Cost column
  where the plan covers the usage and nothing is charged. Accepted forms are plain numbers, a leading or trailing dollar, euro or pound
  sign, thousands separators in the `1,234` pattern, and parentheses for a
  negative.
- The same column chosen for two fields is refused.
- A file over 20 MB is refused by name, with the limit stated.

Several files can be supplied at once, and more can be added later. They are
combined only when every header row is identical; otherwise the report names
the first differing header and the file it came from, and nothing is drawn until
one of the files is removed. A row that is an exact duplicate of a row in an
earlier file is counted, the count is shown beside the file list, and the rows
are not removed, so remove a file if the count is not what you expect. A mapping
you confirmed is kept for files with the same header row.

## Inputs

| Input | What it does |
|---|---|
| Vendor | Chooses which page of the site the report refers to at the end. A recognized export sets it; you can change it. |
| Per-member allowance or limit | The value every member is compared with, in the amount column's unit. A typed value overrides an allowance column. |
| Unused when below this share of the allowance | The threshold, in percent, below which a member's allowance counts as unused. The default is 20. |
| Seats in the organization | When it is larger than the members in the file, the difference is shown as seats with no usage recorded, labeled as inferred from the seat count. |
| Unit of the amount column | The label every figure carries. A recognized export fills it in (AI credits for Copilot, or premium requests for a Copilot file with no credit rows, and USD for Claude). `USD` or `dollars` formats every figure as dollars. |
| Dollars per unit | Optional. Blank unless a recognized export carries a value with a cited source, and none does at present: the Copilot file carries its own `net_amount` column in dollars, the Claude file is already in dollars, and no cited page prices a Codex credit. A rate you type is shown beside every converted figure as the rate you typed. |

None of these values leaves the page.

## Reading the report

| Figure | What it is |
|---|---|
| Members in the file | Distinct values of the member column with at least one row |
| Total | Sum of the amount column across those members, in the labeled unit |
| Total in dollars | Shown only when the amount is convertible: from the file's own dollar column on a Copilot export, or at the rate you typed, with the source named beside it |
| Share drawn by the heaviest fifth | Portion of the total drawn by the heaviest fifth of members, the fifth being the member count times 0.2 rounded up to a whole member. The member table is ranked, so the figure can be checked by hand |
| Median member, Heaviest member | The middle member's amount and the largest |
| Members with a zero amount | Members present in the file whose amount sums to zero |
| Seats with no usage recorded | Your typed seat count minus the members in the file. Shown only when the seat count is larger, and labeled as inferred |
| Request-metered units | Copilot only: rows denominated in requests, counted separately and never added to credits |
| At or over the allowance | Members whose amount is at or above their allowance, and the total drawn past it |
| Below the unused share | Members whose amount is below the typed share of their allowance, and the allowance they left unused |
| Members by amount | The 25 heaviest members as bars, marked in text when at or over the allowance or below the unused share |
| By product, By model, By seat type | The total grouped by that column, shown only when the column is mapped |
| All members as a table | Every member with rank, amount, dollars when convertible, share of the total, allowance and status |
| What this shows | The finding in the file's own numbers, and one text link to the site's page for the chosen vendor, or to the site's home when none is chosen |

When no allowance is known from a column or a typed value, the allowance tiles
are absent and the report says that typing an allowance will show them.

Per-member figures are capacity data. Usage varies with which products and
models someone uses and how they work, so the figures describe capacity draw,
not output or performance.

## The redacted summary

The report ends with a text summary in which every member identifier is
replaced by an ordinal label. It carries the header row, the mapping, the unit,
the counts, the totals, the allowance figures when present, the ten heaviest
members by ordinal label, and the distribution in ten equal buckets. Product,
model and seat type names are reported as counts of distinct values, not by
name. A button copies it; the text is also shown in a box so it can be selected
by hand.

To file a format issue, paste the summary into an issue on this repository. It
is enough to reproduce the shape of the file without any of its names, and for
a Cursor or Codex export it is exactly what a verified preset needs: the header
row as the vendor wrote it. Please say which vendor, plan and dashboard the
export came from.

## Caveats

- **Units stay the file's units.** Amounts are summed as they are and labeled
  with the unit you type. No conversion happens unless you type a rate, and the
  tool never supplies a rate that no cited source states.
- **Overlap without a date column cannot be seen.** Two exports that cover
  overlapping periods are combined as they are; only rows that are exact
  duplicates are counted and reported. If the exports are per-chart or per-filter
  downloads, export the same chart for disjoint filters.
- **The seat count and the allowance are yours.** Neither is in most exports. A
  typed allowance is compared with every member; the tool cannot see the limit
  each member actually has. Seats with no usage are inferred from the seat count
  and labeled as such.
- **A mapping the reader confirmed is only as right as the reader.** The preview
  shows the first rows of each chosen column for that reason, and the amount
  column is parsed in full before anything is drawn.
- **Blank amount cells, and cells reading Included, Free or a dash, read as
  zero.** Each count is shown. Any other cell that is not a number stops the
  report.
- **Export formats change.** The presets match header sets read from real
  files or from the vendor's documented column list; if a vendor renames a column, the file falls through to the mapper
  rather than being read wrongly. Corrections by pull request are welcome.

## Tests

[`test/`](test/) holds synthetic CSV files in each vendor's export formats,
from GitHub Copilot, Claude, Cursor and Codex, and a page that drops each one on
this report and checks what it shows against figures worked out by hand. Its
[README](test/README.md) says where each file's format comes from and how far it
is established, and how to run the page in a browser or from a terminal. Run it
after any change to this file.

## The copy on the site

The SpillwayOps site embeds this report in the first screen of its pages. The
site carries a copy of this file's script block, verbatim, in its theme
(`landing/src/themes/reimagined/assets/js/usage-report.js` in the marketing
repository), with the commit it was copied from in its header. This file is
the source. When this tool changes, that copy is regenerated by copying the
script block again; the site keeps its own markup with the same element ids
and classes, its own styles, and its own analytics wrapper. Nothing on the
site is edited into this file.

## License

MIT, see [LICENSE](../LICENSE). Copyright (c) 2026 Optic Nerve AI, LLC. [www.spillwayops.com](https://www.spillwayops.com)
