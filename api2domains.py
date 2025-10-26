#!/usr/bin/env python3
"""
extract_domains_api.py

Fetches domain allocation data from the Namekart dashboard API, extracts unique domain names,
and writes them to an output text file (one per line).

Usage:
    python extract_domains_api.py -t <your_bearer_token> [-o output.txt]

Arguments:
    -t, --token    Bearer API access token (REQUIRED).
    -o, --output   Output text filename (default: domains.txt).

Graceful error handling for HTTP/network errors, KeyboardInterrupt (Ctrl+C), and file I/O.
"""

import requests
import json
import argparse
import sys


def fetch_and_extract_domains(token, output_file):
    """
    Fetch domain data from dashboard API using the supplied token.
    Extract both 'domainName' and 'presentDomain.domain' from each object.
    Writes to both domains.json (full API response) and output_file (unique domains).
    """
    url = "https://nk-dashboard-1.grayriver-ffcf7337.westus.azurecontainerapps.io/getmysocialallocations"
    params = {"page": "0", "size": "200", "sort": "{}", "filter": "{}", "search": ""}

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {token}",
        "origin": "https://app.namekart.com",
        "x-auth-provider": "GOOGLE",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    }

    try:
        # API request (timeout=30s for robustness)
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"API response object: {response}")
        print(f"Status code: {response.status_code}")
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Exiting gracefully.")
        sys.exit(0)
    except requests.RequestException as err:
        print(f"HTTP error: {err}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(2)

    if response.ok:
        try:
            # Save full API response
            data = response.json()
            with open("domains.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print("Saved API response as domains.json.")

            # Extract unique domain names from response
            domains = set()
            for entry in data.get("content", []):
                if "domainName" in entry and entry["domainName"]:
                    domains.add(entry["domainName"])
                present_domain = entry.get("presentDomain", {}).get("domain")
                if present_domain:
                    domains.add(present_domain)

            # Output domain list (one per line)
            with open(output_file, "w", encoding="utf-8") as out:
                for domain in sorted(domains):
                    out.write(domain + "\n")
            print(f"Wrote {len(domains)} domains to {output_file}.")

        except Exception as e:
            print(f"Error processing API response: {e}")
            sys.exit(3)
    else:
        print(f"API Response: {response.status_code} - {response.text}")
        sys.exit(4)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Extract domains from dashboard API to a text file"
    )
    parser.add_argument("-t", "--token", required=True, help="Bearer API access token")
    parser.add_argument(
        "-o",
        "--output",
        default="domains.txt",
        help="Output text filename (default: domains.txt)",
    )
    args = parser.parse_args()
    try:
        fetch_and_extract_domains(args.token, args.output)
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Exiting gracefully.")
        sys.exit(0)
