# usage-report tests

Synthetic CSV files in each vendor's export formats, and a page that drops
them on the usage report and checks what it shows.

## Run

The page reads the fixtures over HTTP, so serve the repository first. From the
repository root:

```sh
python3 -m http.server 8000
```

Then open [http://localhost:8000/usage-report/test/](http://localhost:8000/usage-report/test/).
Each case shows PASS or FAIL, and a failing case lists every expected line it
did not find, beside the line the page showed instead. Opened straight from
disk, the page says it needs HTTP and runs nothing. Once merged, the hosted copy
runs at [https://opticnerveai.github.io/spillwayops-tools/usage-report/test/](https://opticnerveai.github.io/spillwayops-tools/usage-report/test/).

From a terminal, with the server above running and Chrome installed:

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
  --virtual-time-budget=60000 --dump-dom http://localhost:8000/usage-report/test/ \
  | grep -o '<title>[^<]*'
```

This prints `<title>PASS 28/28 usage-report tests` when every case passes, or
`FAIL` and the count that passed.

## How it works

`index.html` holds the cases. For each one it loads the usage report,
`../index.html`, in a frame, puts the fixture files into the report's own file
input, and takes the steps a reader would: confirm the column mapper, choose a
column, type a unit or an allowance, remove a file. It then checks the redacted
summary, the stat tiles and any message against figures worked out by hand from
the fixture, and checks that the report page loaded nothing over the network.
There is nothing to install and no build step.

## Fixtures

Every fixture is synthetic: members are `dev-NNN` or `dev-NNN@example.com`, and
no row comes from a real account. The source column says how far each file's
format is established:

- **Documented**: the vendor's documentation lists the columns.
- **Staff-stated**: the vendor's staff describe the file on the vendor's forum.
- **Third-party**: open-source parsers of the real export read these columns.
- **Hypothetical**: no source gives the columns, and the file tests a behavior.

### GitHub Copilot

| File | What it models | Source | Expected |
|---|---|---|---|
| `copilot/ai-usage-report.csv` | The AI usage report, from Billing & Licensing → Usage → AI usage → Get usage report | Documented: the fields in GitHub's [Billing reports reference](https://docs.github.com/en/billing/reference/billing-reports). The column order and the `unit_type` value `AI Credits` are assumed | Recognized as the GitHub AI usage report: 4 members, 5,200 AI credits, $21.00 net. No allowance until one is typed; at 1,000, one member is over by 3,000 and one is below 20 %, leaving 1,000 |
| `copilot/billing-usage-preview.csv` | The billing usage CSV of GitHub's usage-based billing preview, in transition: a requests row converted to credits, a requests row without a conversion, and an Actions row | Documented: the columns, their order and the `unit_type` rule in GitHub's [Copilot billing preview report format](https://github.com/github/copilot-billing-preview/blob/main/docs/report-format.md) | Recognized as the billing usage CSV: 3 members, 3,650 AI credits, $25.00; 40 request-metered units counted apart; the Actions row set aside. The allowance comes from rows in credits only: one member over by 1,600, one below 20 % leaving 1,750, one with no allowance |
| `copilot/billing-usage-premium-requests.csv` | A file with request rows only, from before AI credits: the billing usage CSV without its two `aic_` columns | Hypothetical: no source lists this header | Read in premium requests: 380 requests, $2.00. Against the 300-request quota, one member is over by 50 and two are below 20 %, leaving 570 |
| `copilot/billing-usage-spreadsheet-resave.csv` | The billing usage CSV after a spreadsheet re-save: a byte-order mark, CRLF line ends, title-case headers and a quoted `1,200` | Robustness case | Recognized: 3,200 AI credits, $32.00, one member over by 100 |
| `copilot/activity-report.csv` | The Copilot activity report | Documented: the fields in GitHub's [Metrics data properties for GitHub Copilot](https://docs.github.com/en/copilot/reference/metrics-data) | Named as the activity report; nothing is drawn |
| `../../copilot-billing-report/sample-usage-report.csv` | The Copilot billing report's own sample | That tool's README | Recognized: 25 members, 27,027 AI credits, $270.59, 18 request-metered units |

### Claude

| File | What it models | Source | Expected |
|---|---|---|---|
| `claude/spend-report.csv` | The spend report, from Settings → Analytics → Export spend report | Column names read from a real export, per the [claude-spend-report](../../claude-spend-report/) README; the `account_uuid` and `model_family` spellings are that tool's assumption | Recognized: 3 members, $86.00. The organization service usage row is set aside carrying $14.40, and the row with no model carrying $0.80 |
| `claude/spend-report-alternate-headers.csv` | The spend report under alias headers, with a byte-order mark, CRLF line ends and a `$` sign | Robustness case for the alias list | Recognized: 2 members, $52.50 |
| `claude/code-contribution-export.csv` | The Claude Code analytics "Export all users" contribution CSV | Hypothetical: [Track team usage with analytics](https://code.claude.com/docs/en/analytics) describes the export but not its columns | Named as the Claude Code analytics export; opened in the mapper anyway, its lines add up to 340 |
| `../../claude-spend-report/sample-spend-report.csv` | The Claude spend report's own sample | That tool's README | Recognized: 48 members, $3,413.88 |

### Cursor

| File | What it models | Source | Expected |
|---|---|---|---|
| `cursor/usage-events.csv` | The Usage page's Export CSV, one row per request | Staff-stated: the User and Cost columns, the word Included in Cost for usage the plan covers, and a numeric user ID for a member who has left ([166548](https://forum.cursor.com/t/166548), [167153](https://forum.cursor.com/t/167153), [167128](https://forum.cursor.com/t/167128), [169020](https://forum.cursor.com/t/169020)). Third-party: the full header row, in [jnst/cursor-usage](https://github.com/jnst/cursor-usage/blob/main/src/core/parse.ts), and quoted rows with Cost `Included` and `-`, in [junhoyeo/tokscale](https://github.com/junhoyeo/tokscale/blob/main/crates/tokscale-core/src/sessions/cursor.rs). A Cursor forum user reports `Free` on the Usage page ([167153](https://forum.cursor.com/t/167153)) | The mapper pre-selects User, Cost, Date and Model. In USD: 5 members, $22.55, with 2 Included, 1 `-` and 1 Free cell counted as zero. Mapped to Total Tokens instead: 1,870,460 |
| `cursor/usage-events-part-2.csv` | A second export of the same page, repeating one row of the first | As above | Combined with the first, the repeated row is counted and reported: $23.11. Removing the first file leaves $0.56 |
| `cursor/analytics-raw-data-2025.csv` | The Analytics page's raw-data download | Hypothetical beyond its origin: headers read from users' 2025 screenshots | Opens the mapper rather than being named as the Claude file; Agent Requests add up to 40 |
| `cursor/ai-code-commits.csv`, `cursor/ai-code-changes.csv` | The AI Code Tracking API's CSVs | Documented: the header lines in Cursor's [AI Code Tracking API](https://cursor.com/docs/account/teams/ai-code-tracking-api) | Named as Cursor AI Code Tracking exports; nothing is drawn |
| `cursor/admin-api-daily-usage.csv` | `/teams/daily-usage-data` rows written out as CSV | Documented field names, in Cursor's [Admin API](https://cursor.com/docs/account/teams/admin-api). The API returns JSON, so this file is a reader's conversion | Opens the mapper despite its lines columns; with `day` as the date, `usageBasedReqs` add up to 6 over 2026-09-01 to 2026-09-02 |
| `cursor/admin-api-spend.csv` | `/teams/spend` rows written out as CSV | Documented field names, with the fractional cents the Admin API describes | The mapper pre-selects `email` and `spendCents`: 19,750.62 cents |

### Codex

| File | What it models | Source | Expected |
|---|---|---|---|
| `codex/workspace-analytics-users.csv` | The ChatGPT Enterprise and Edu workspace analytics Users export | Documented: the columns in OpenAI's [Workspace analytics for ChatGPT Enterprise and Edu](https://help.openai.com/en/articles/10875114). The column order and the text of the serialized maps and groups are assumed | The mapper pre-selects `email`, `messages`, `period_start` and `seat_type`: 837 messages across 3 seat types |
| `codex/business-member-usage.csv` | The ChatGPT Business member usage table, were it exported | Hypothetical: the columns are the table's labels in the [ChatGPT Business release notes](https://help.openai.com/en/articles/11391654-chatgpt-business-release-notes), and no export of the table is documented | The mapper pre-selects Email, Credits spent and Seat type: 5,700 credits |

### Any vendor

| File | What it tests | Expected |
|---|---|---|
| `../sample-usage.csv` | The usage report's own sample | All seven mapper fields pre-selected: 20,908 credits, 2 members at or over the allowance, 19 below 20 % |
| `generic/amount-not-a-number.csv` | An amount cell reading `n/a` | The report stops and names the cell |
| `generic/blank-amount.csv` | A blank amount cell | Read as zero and counted |
| `cursor/usage-events.csv` with `codex/business-member-usage.csv` | Two files whose header rows differ | Not combined; the first differing column is named |
| No file | The synthetic data button | 60 members, labeled as synthetic |

## Adding a case

Put the fixture in its vendor's directory, keeping it synthetic, and work out
its figures by hand. Add a case to `CASES` in `index.html` with the lines the
summary must contain, and add a row above that says where the format comes
from.
