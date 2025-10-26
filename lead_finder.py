#!/usr/bin/env python3
"""
Domain Lead Finder
------------------
This CLI tool finds potential leads for domain sales given a base domain name.
It discovers all active domains with the *exact same SLD* (e.g. apex.in, apex.world for apex.com)
using DuckDuckGo and RapidDNS open sources.

Filters strictly to only direct SLD matches (e.g. "apex" for apex.com).

Outputs results as JSON or CSV, with fields for domain, full URL, category, copyright, status,
lead type, and more.

---------------------------------------
DEPENDENCIES:
    pip install termcolor requests tldextract beautifulsoup4 ddgs

USAGE EXAMPLES:
    python lead_finder.py -d apex.com --debug --output results.json
    python lead_finder.py -l domains.txt --output results.csv

OUTPUT FORMAT:
    JSON (by default) or CSV.
    Each entry includes:
        - domain: the discovered domain (e.g. apex.in)
        - url: full http URL
        - category: classified from website keywords
        - copyright year: extracted
        - status: active/inactive
        - company_name: (N/A)
        - lead_type: 'High', 'Medium', 'Low' - based on TLD relevance

---------------------------------------
SCRIPT BY: Darkstar
---------------------------------------
"""

import argparse
import re
import requests
import socket
import json
import csv
import sys
from urllib.parse import urlparse
from tldextract import extract
from bs4 import BeautifulSoup
from termcolor import colored

def log(message, level="INFO"):
    """Prints a colored log message to the console."""
    colors = {
        "START": "cyan",
        "PROCESS": "blue",
        "INFO": "green",
        "DEBUG": "yellow",
        "WARN": "magenta",
        "ERROR": "red",
        "DONE": "green",
    }
    print(colored(f"[{level}] {message}", colors.get(level, "white")))

def normalize_sld(domain):
    """Extracts the SLD (main name) from a full domain like apex.com -> 'apex'."""
    ext = extract(domain)
    return ext.domain.lower()

def probe_domain_activity(domain):
    """Checks if the domain resolves and if HTTP responds for basic domain activity."""
    try:
        socket.gethostbyname(domain)
        try:
            resp = requests.head(f"http://{domain}", timeout=5)
            return True, resp.status_code
        except:
            return True, "No HTTP"
    except socket.gaierror:
        return False, "No DNS"

def google_tld_search(sld, tld, debug=False):
    """
    Attempts to search for matching SLD.TLD domains using Google.
    Will fail gracefully (warn) as CLI requests are often blocked.
    """
    import urllib.parse
    headers = {"User-Agent": "Mozilla/5.0"}
    query = f'"{sld}" site:.{tld}'
    search_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
    domains = set()
    try:
        res = requests.get(search_url, headers=headers, timeout=20)
        if debug:
            log(f"GOOGLE HTML: {res.text[:500]}", "DEBUG")
        # Google blocks most CLI scraping
        if (
            "enablejs" in res.text
            or "Please click" in res.text
            or "detected unusual traffic" in res.text
        ):
            log("Google blocked our automated query. Use DuckDuckGo and RapidDNS results.", "WARN")
            return []
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a", href=True):
            h = a["href"]
            if h.startswith("/url?q="):
                url = h.split("/url?q=")[1].split("&")[0]
                extd = extract(url)
                normd = extd.domain.lower()
                normd_clean = re.sub(
                    r"(group|tech|solutions|ltd|llc|inc|company|corp|enterprises|industries|systems|technologies|international|global|services)$",
                    "",
                    normd,
                )
                # SLD must match exactly
                if (
                    normd_clean == sld
                    and extd.suffix
                    and f"{normd}.{extd.suffix}" != f"{sld}.com"
                ):
                    domains.add(f"{normd}.{extd.suffix}")
    except Exception as e:
        log(f"Google TLD search (.{tld}) failed: {e}", "WARN")
    return list(domains)

def duckduckgo_tld_search(sld, tld, debug=False):
    """
    Searches DuckDuckGo for domains with given SLD.TLD.
    This is the main source for CLI usage (via ddgs .text()).
    """
    try:
        from ddgs import DDGS
    except ImportError:
        log("DuckDuckGo search requires: pip install ddgs", "WARN")
        return []
    domains = set()
    query = f'"{sld}" site:.{tld}'
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=20):
                url = r.get("href") or r.get("url")
                if url:
                    extd = extract(url)
                    normd = extd.domain.lower()
                    normd_clean = re.sub(
                        r"(group|tech|solutions|ltd|llc|inc|company|corp|enterprises|industries|systems|technologies|international|global|services)$",
                        "",
                        normd,
                    )
                    # SLD must match exactly
                    if (
                        normd_clean == sld
                        and extd.suffix
                        and f"{normd}.{extd.suffix}" != f"{sld}.com"
                    ):
                        domains.add(f"{normd}.{extd.suffix}")
        if debug:
            log(f"DuckDuckGo .{tld}: {list(domains)}", "DEBUG")
    except Exception as e:
        log(f"DuckDuckGo TLD search (.{tld}) failed: {e}", "WARN")
    return list(domains)

def rapid_dns_lookup(sld, debug=False):
    """
    Uses RapidDNS to get all domains for a given SLD across all TLDs.
    """
    url = f"https://rapiddns.io/same/{sld}?full=1"
    domains = set()
    try:
        res = requests.get(url, timeout=20)
        table = BeautifulSoup(res.text, "html.parser")
        for tag in table.find_all("a", href=True):
            dom = tag.text.strip()
            extd = extract(dom)
            normd = extd.domain.lower()
            # SLD must match exactly
            if normd == sld and f"{normd}.{extd.suffix}" != f"{sld}.com":
                domains.add(f"{normd}.{extd.suffix}")
        if debug:
            log(f"RapidDNS found: {list(domains)}", "DEBUG")
    except Exception as e:
        log(f"RapidDNS lookup failed: {e}", "WARN")
    return list(domains)

def get_category_and_copyright(domain):
    """
    Attempts to extract business category and copyright year from content.
    """
    category, year = "Unknown", "N/A"
    try:
        url = f"http://{domain}"
        html = requests.get(url, timeout=5).text.lower()
        for cat in [
            "software", "finance", "wholesale", "agency", "consultancy",
            "technology", "marketing"
        ]:
            if cat in html:
                category = cat.capitalize()
                break
        match = re.search(r"©\s*(\d{4})", html)
        if match:
            year = match.group(1)
    except Exception:
        pass
    return category, year

def classify_lead(domain):
    """Classifies lead type by TLD."""
    suffix = extract(domain).suffix
    high = ["one", "world", "group", "online", "global"]
    medium = ["in", "net", "co", "ai", "biz"]
    if any(suffix.endswith(t) for t in high):
        return "High"
    elif any(suffix.endswith(t) for t in medium):
        return "Medium"
    else:
        return "Low"

def process_domain(domain, debug=False):
    """
    Main workflow:
        - Extract SLD.
        - Discover candidate domains via DuckDuckGo, Google (warn), RapidDNS.
        - Filter strictly to candidates with matching SLD only.
        - Probe activity; extract enrichment data; write output.
    """
    sld = normalize_sld(domain)
    log(f"Starting lead search for SLD: '{sld}'", "START")

    tlds = ["co", "in", "net", "group", "online", "world", "ai", "biz", "org", "app"]
    google_results = []
    duck_results = []
    for tld in tlds:
        g_results = google_tld_search(sld, tld, debug=debug)
        if debug:
            log(f"Google .{tld}: {g_results}", "DEBUG")
        google_results.extend(g_results)
        d_results = duckduckgo_tld_search(sld, tld, debug=debug)
        if debug:
            log(f"DuckDuckGo .{tld}: {d_results}", "DEBUG")
        duck_results.extend(d_results)
    rapid_dns = rapid_dns_lookup(sld, debug=debug)
    combined_domains = list(set(google_results + duck_results + rapid_dns))
    if debug:
        log(f"Total unique domains found: {len(combined_domains)}", "DEBUG")

    leads = []
    for d in combined_domains:
        # Filter for exact match only: SLD must match the original input SLD
        extd = extract(d)
        if extd.domain.lower() != sld:
            continue
        if d == domain:
            continue
        active, status_detail = probe_domain_activity(d)
        if not active:
            if debug:
                log(f"Skipping inactive {d} ({status_detail})", "DEBUG")
            continue
        log(f"Probing {d} -- active [{status_detail}]", "INFO")
        category, year = get_category_and_copyright(d)
        leads.append(
            {
                "domain": d,
                "url": f"http://{d}",
                "category": category,
                "copyright year": year,
                "status": "active",
                "company_name": "N/A",
                "lead_type": classify_lead(d),
            }
        )
        if debug:
            log(f"Discovered: {d} ({category}, {year})", "DEBUG")
    return {domain: leads}

def main():
    """
    CLI entry point. Handles args, orchestrates domain analysis, writes results.
    """
    parser = argparse.ArgumentParser(description="Domain Lead Finder -- Finds all active domains with same SLD")
    parser.add_argument("-d", help="Single domain input (e.g. apex.com)")
    parser.add_argument("-l", "-f", dest="file", help="File of domains, one per line")
    parser.add_argument("--output", help="Output file (JSON or CSV)")
    parser.add_argument("--debug", action="store_true", help="Enable verbose mode (show logs)")
    args = parser.parse_args()

    if not args.d and not args.file:
        parser.print_help()
        sys.exit(1)

    domains = []
    if args.d:
        domains.append(args.d)
    if args.file:
        with open(args.file) as f:
            domains.extend([line.strip() for line in f if line.strip()])

    all_data = {}
    for i, domain in enumerate(domains, start=1):
        log(f"Processing domain {i}/{len(domains)}: {domain}", "PROCESS")
        all_data.update(process_domain(domain, args.debug))

    if args.output:
        if args.output.endswith(".json"):
            json.dump(all_data, open(args.output, "w"), indent=2)
        elif args.output.endswith(".csv"):
            with open(args.output, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "source_domain",
                        "domain",
                        "url",
                        "category",
                        "copyright",
                        "status",
                        "lead_type",
                    ]
                )
                for source, leads in all_data.items():
                    for l in leads:
                        writer.writerow(
                            [
                                source,
                                l["domain"],
                                l["url"],
                                l["category"],
                                l["copyright year"],
                                l["status"],
                                l["lead_type"],
                            ]
                        )
        log(f"Results saved to {args.output}", "DONE")
    else:
        print(json.dumps(all_data, indent=2))

if __name__ == "__main__":
    main()
