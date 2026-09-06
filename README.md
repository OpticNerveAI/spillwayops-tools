# spillwayops-tools

Standalone tools for reading AI coding capacity data — what an organisation is
allocated, what it has consumed, and how that consumption is distributed.

Each tool is self-contained and runs on its own.

## Tools

| Tool | What it does |
|---|---|
| [`copilot-usage-audit`](copilot-usage-audit/) | Reads GitHub Copilot seat and usage data for an organisation or enterprise and prints a distribution report: consumption per user, share of the shared monthly pool consumed, and the number of users above the included per-user allowance. One Python file, no dependencies, read-only. |

Further tools, including for vendors other than GitHub, will be added here. Each
gets its own directory and its own README.

## How these tools behave

- **Read-only.** Tools issue `GET` requests only. They do not write to your systems.
- **No telemetry.** Nothing is sent anywhere. The only host a tool contacts is the
  vendor API it reads, named in that tool's README.
- **Standard library only** where possible, so a tool can be read in full before
  it is run.
- **Demo mode.** Every tool runs against synthetic data with no token and no
  network call, so the output shape can be inspected before any access is granted.
- **Vendor figures are documented and overridable.** Where a tool relies on a
  published vendor number, its README links to the vendor's documentation and the
  tool accepts an override. These numbers change; corrections by pull request are
  welcome.

## Contributing

Issues and pull requests welcome, particularly corrections to vendor allowance
figures and API endpoint shapes. If a tool produces an incorrect report against
your data, an issue with redacted JSON output is the most useful thing to file.

## Licence

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Optic Nerve AI, LLC.
