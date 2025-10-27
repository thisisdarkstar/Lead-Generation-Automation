# Lead Generation Automation

A small collection of Python scripts to extract domains and build simple lead lists from CSVs or the Namekart dashboard API, and to enrich discovered domains into lead records.

This README documents environment setup (Windows PowerShell and Linux), exact usage for each shipped script, inputs/outputs, and troubleshooting tips.

## Table of contents

- About
- Quick setup (Windows PowerShell)
- Quick setup (Linux / macOS)
- Scripts and exact usage
  - `csv2domains.py`
  - `api2domains.py`
  - `domain_lead_finder.py`
- Files included
- Contract (inputs / outputs / exit codes)
- Edge cases / notes
- Troubleshooting
- Contributing

## About

Small utilities to:

- extract unique domains from CSVs (`csv2domains.py`),
- fetch allocated domains from the Namekart dashboard API and write both the raw response and a domain list (`api2domains.py`), and
- discover related SLD domains and probe them for activity and basic enrichment data (`domain_lead_finder.py`).

These scripts are intentionally simple and command-line oriented so you can compose them in pipelines or use them interactively.

## Quick setup (Windows PowerShell)

1) Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Upgrade pip and install dependencies from `requirements.txt`:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Optional: `domain_lead_finder.py` lists additional runtime packages it can use; ensure those are installed if you intend to run that script directly:

```powershell
pip install termcolor requests tldextract beautifulsoup4 ddgs
```

## Quick setup (Linux / macOS)

1) Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Upgrade pip and install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Optional packages for `domain_lead_finder.py`:

```bash
pip install termcolor requests tldextract beautifulsoup4 ddgs
```

Notes:
- These instructions assume Python 3.8+. If your system's default Python is `python` rather than `python3` adjust the commands accordingly.
- Use a virtual environment to avoid polluting system packages.

## Scripts and exact usage

Below are exact usages and behavior notes taken directly from the shipped scripts.

### csv2domains.py

- What it does: Reads a CSV file using csv.DictReader and extracts values from the `domain` column. It deduplicates and sorts domains, then writes them one-per-line to the output file.
- Flags:
  - `-f, --file` (required): input CSV path
  - `-o, --output`: output text filename (defaults to `domains.txt`)

Example (PowerShell / Bash):

```powershell
python csv2domains.py -f my_export.csv -o domains.txt
```

Behavior notes:
- If the `domain` column is missing rows with no `domain` value are skipped.
- On file-not-found or IO errors the script exits with a non-zero exit code.

### api2domains.py

- What it does: Calls the Namekart dashboard endpoint and:
  - Saves the full JSON response to `domains.json`.
  - Extracts unique domain names from `domainName` and `presentDomain.domain` fields and writes them (sorted) to the provided output file (default `domains.txt`).
- Flags:
  - `-t, --token` (required): Bearer API access token
  - `-o, --output`: output text filename (default: `domains.txt`)

Examples:

PowerShell (pass token variable):

```powershell
$token = 'eyJhbGciOi...'
python api2domains.py -t $token -o domains_from_api.txt
```

Linux / macOS (export then pass):

```bash
export NAMEKART_TOKEN='eyJhbGciOi...'
python api2domains.py -t "$NAMEKART_TOKEN" -o domains_from_api.txt
```

Behavior notes:
- The script writes a `domains.json` file containing the raw API response.
- HTTP errors and unexpected responses exit with non-zero exit codes and print the response code/text.
- The script uses a 30s request timeout to be robust against hanging requests.

### domain_lead_finder.py

- What it does: Given a single domain (`-d`) or a file of domains (`-l` / `-f`) it:
  - Extracts the SLD (second-level domain) and searches across a set of TLDs for exact SLD matches using several sources (DuckDuckGo via `ddgs`, RapidDNS scraping, and a Google attempt which may be blocked).
  - Probes discovered domains for DNS and HTTP activity.
  - Attempts simple enrichment (category detection and copyright year) by scraping page content.
  - Classifies leads by TLD into `High` / `Medium` / `Low` relevance.
  - Outputs a JSON structure by default, or CSV if the `--output` filename ends with `.csv`.

- Flags:
  - `-d`: single domain (e.g. `apex.com`)
  - `-l, -f, --file`: file of domains (one per line)
  - `--output`: output filename (JSON or CSV)
  - `--debug`: verbose logging

Examples:

Single domain to JSON (PowerShell / Bash):

```powershell
python domain_lead_finder.py -d apex.com --debug --output results_apex.json
```

Process domains from file to CSV:

```bash
python domain_lead_finder.py -l domains.txt --output results.csv
```

Dependencies:
- The script recommends: `termcolor`, `requests`, `tldextract`, `beautifulsoup4`, and `ddgs` (DuckDuckGo scraping helper). Install them via pip as shown in the Quick setup.

Behavior & caveats:
- Google scraping often fails due to bot detection; the script warns and falls back to DuckDuckGo / RapidDNS.
- DuckDuckGo usage requires the `ddgs` package; if not installed the script will skip that source and log a warning.
- Network/RPC/DNS failures for individual domains are handled per-domain and do not abort the full run.

## Files included

- `csv2domains.py` — extract domains from a CSV (reads `domain` column).
- `api2domains.py` — fetch Namekart dashboard allocations, write `domains.json` (raw) and an output domain list.
- `domain_lead_finder.py` — discover related SLD domains and probe them for leads; outputs JSON or CSV.
- `domains.txt` — example placeholder (not required).
- `leads.json` — example or previously generated leads output.
- `requirements.txt` — dependencies. Use `pip install -r requirements.txt`.
- `myclaim_export_2025-10-26 (2).csv` / `sample.csv.file` — example CSV inputs you may use to test `csv2domains.py`.

## Contract (inputs / outputs / exit codes)

- Inputs: CSV files with a `domain` column (`csv2domains.py`), Namekart bearer token (`api2domains.py`), or domain(s) supplied to `domain_lead_finder.py`.
- Outputs: text file with domains (one per line), `domains.json` (raw API response), and lead files (JSON or CSV) from `domain_lead_finder.py`.
- Exit codes: non-zero for fatal errors (file-not-found, HTTP auth failure, unhandled exceptions). Per-row or per-domain issues are typically logged and skipped.

## Edge cases / notes

1. Duplicate domains are removed when generating domain lists.
2. If the CSV has no `domain` column the `csv2domains.py` will simply not find any values — verify the column header in your CSV.
3. API-auth failures will show the server response text and exit with a non-zero code; ensure tokens are valid and not expired.
4. Scraping-based discovery can be incomplete and may be rate-limited or blocked. Respect remote site terms and rate limits.

## Troubleshooting

- If a script raises `ModuleNotFoundError`, make sure your virtual environment is active and run `pip install -r requirements.txt`.
- If `api2domains.py` reports 401/403, verify the token you provided and try a short test with a known-good token.
- If `domain_lead_finder.py` finds few or no results, try enabling `--debug` to see the search sources and any warnings about blocked searches.

Collect logs for long runs:

```powershell
python domain_lead_finder.py -l domains.txt --output leads.json > run.log 2>&1
```

## Contributing

Enhancements that help users:
- Add unit tests for CSV parsing and domain-normalization helpers.
- Add a `--column` flag to `csv2domains.py` to support CSVs where the domain is under a different header.
- Add configurable retries and backoff for API calls.

To contribute: open an issue, create a branch, implement changes, and open a pull request.

## License

If you intend to share this repository, add a `LICENSE` file describing permitted usage. For private use, document that here.

---

If you'd like, I can also:

- add `--help` descriptions to the scripts (small edits),
- generate a minimal `requirements.txt` entry for any missing runtime packages, or
- add a quick test verifying that `csv2domains.py` correctly extracts domains from a tiny sample CSV.

Tell me which you'd like next.
