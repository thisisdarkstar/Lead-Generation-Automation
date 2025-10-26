#!/usr/bin/env python3
"""
extract_domains_csv.py

Extracts unique domain names from a CSV file with a "domain" column
and writes them (one per line) into an output text file.

Usage:
    python extract_domains_csv.py -f input.csv [-o output.txt]

Arguments:
    -f, --file     Input CSV filename (REQUIRED)
    -o, --output   Output text filename (default: domains.txt)

Features:
    - Robust error handling for file/IO/network issues and KeyboardInterrupt
    - Skips header row automatically (with DictReader)
    - No duplicate domains in output
    - Output file is sorted alphabetically
"""

import csv
import argparse
import sys


def extract_domains(input_file, output_file):
    """
    Reads domain names from the provided CSV file and writes them into the output text file, one per line.
    """
    domains = set()
    try:
        # Open input CSV and extract domains from "domain" column
        with open(input_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                domain = row.get("domain")
                if domain:
                    domains.add(domain)
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Exiting gracefully.")
        sys.exit(0)
    except FileNotFoundError:
        print(f"File not found: {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(2)

    try:
        # Write domains to output file, one per line, sorted
        with open(output_file, "w", encoding="utf-8") as out:
            for domain in sorted(domains):
                out.write(domain + "\n")
        print(f"{len(domains)} domains written to {output_file}!")
    except KeyboardInterrupt:
        print("\nScript interrupted by user during writing. Exiting gracefully.")
        sys.exit(0)
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract domains from a CSV to a domains text file"
    )
    parser.add_argument("-f", "--file", required=True, help="Path to input CSV file")
    parser.add_argument(
        "-o",
        "--output",
        default="domains.txt",
        help="Output text filename (default: domains.txt)",
    )
    args = parser.parse_args()
    try:
        extract_domains(args.file, args.output)
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Exiting gracefully.")
        sys.exit(0)
