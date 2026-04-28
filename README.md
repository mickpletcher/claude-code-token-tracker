# Claude Code Token Tracker

Local dashboard for tracking Claude Code token usage and estimated costs in real time.

## Overview

This tool reads Claude Code session data directly from `~/.claude/projects/` and displays token counts and cost estimates in a browser-based dashboard. A lightweight Python server parses the JSONL session files and serves them to a single-page HTML frontend. No cloud services, no accounts, no data leaves the machine.

## What This Does

- Reads Claude Code session JSONL files from `~/.claude/projects/` automatically
- Aggregates input, output, cache write, and cache read token counts per session
- Calculates estimated cost using Claude Sonnet 4 pricing
- Displays running totals across all sessions with a per-category cost breakdown
- Auto-refreshes every 30 seconds while the server is running
- Exports session data to CSV

## Repository Structure

```
claude-code-token-tracker/
|-- README.md
|-- cc_token_server.py        # Python HTTP server that reads JSONL files and serves the API
|-- claude-code-token-tracker.html  # Single-page dashboard, fetches from localhost:7823
```

## Prerequisites

- Python 3.7 or later (stdlib only, no pip installs required)
- Claude Code installed and at least one session run so `~/.claude/projects/` exists
- A modern browser

## Setup

1. Clone the repository:

```bash
git clone https://github.com/mickpletcher/claude-code-token-tracker.git
cd claude-code-token-tracker
```

2. Start the server:

```bash
python cc_token_server.py
```

3. Open the dashboard:

```
http://localhost:7823
```

The server reads `~/.claude/projects/**/*.jsonl` on every request. No restart needed as new sessions appear.

## Usage

```
python cc_token_server.py
```

The server runs on port `7823`. Keep it running in a terminal or background process while working in Claude Code. The dashboard will show a red "server offline" status if the server is not running.

To start the server automatically on login, add a startup entry pointing to the script. On Windows, create a `.bat` file and place it in the Startup folder:

```bat
start /min python "C:\path\to\cc_token_server.py"
```

## Cost Rates

Rates are based on Claude Sonnet 4 pricing at time of publishing. Update the `RATES` object in `claude-code-token-tracker.html` if pricing changes.

| Token Type | Rate |
|---|---|
| Input | $3.00 per million tokens |
| Output | $15.00 per million tokens |
| Cache Write | $3.75 per million tokens |
| Cache Read | $0.30 per million tokens |

## Common Errors

| Problem | Likely Cause | Fix |
|---|---|---|
| "server offline" status in dashboard | `cc_token_server.py` is not running | Run `python cc_token_server.py` in a terminal |
| No sessions appear | Claude Code has not been run yet | Run at least one Claude Code session first |
| Sessions show 0 tokens | JSONL format differs from expected | Open a JSONL file in `~/.claude/projects/` and verify the `usage` field is present in assistant message entries |
| Port conflict | Another process is using port 7823 | Change `PORT = 7823` in `cc_token_server.py` and update the `API` variable in the HTML to match |

## Blog

Technical posts about automation and developer tooling at [mickitblog.blogspot.com](https://mickitblog.blogspot.com).

## License

This project is licensed under the MIT License. See `LICENSE` for the full text.
