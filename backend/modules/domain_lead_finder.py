#!/usr/bin/env python3
"""
Domain Lead Finder (Module & CLI)

Finds potential lead domains sharing the same SLD using DuckDuckGo and RapidDNS.
Filters strictly for exact SLD matches (no false positives).
Enrichment: returns domain, URL, category, copyright, status, company_name, lead_type.

Dependencies:
    pip install termcolor requests tldextract beautifulsoup4 ddgs

Usage as CLI:
    python domain_lead_finder.py -d apex.com --debug --output results.json
    python domain_lead_finder.py -l domains.txt --output results.csv

As a module:
    from domain_lead_finder import find_leads_for_domains
    leads_dict = find_leads_for_domains(['apex.com', 'ishaatech.ai'], debug=False)
"""

import re
import requests
import socket
import json
import csv
import sys
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
    """Extracts the SLD (main label) from a full domain like apex.com -> 'apex'."""
    ext = extract(domain)
    return ext.domain.lower()


def probe_domain_activity(domain):
    """
    Checks if the domain resolves and if HTTP responds for basic activity.
    Returns tuple (bool active, status string).
    """
    try:
        socket.gethostbyname(domain)
        try:
            resp = requests.head(f"http://{domain}", timeout=5)
            return True, resp.status_code
        except Exception as e:
            return True, f"No HTTP ({e})"
    except socket.gaierror as err:
        return False, f"No DNS ({err})"
    except Exception as e:
        return False, f"Probe Error ({e})"


def google_tld_search(sld, tld, debug=False):
    """
    Attempts automated Google search for SLD.TLD matches (CLI scraping often blocked).
    Returns list of candidate domains (may often empty).
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
        if (
            "enablejs" in res.text
            or "Please click" in res.text
            or "detected unusual traffic" in res.text
        ):
            log("Google blocked automated query. Use DuckDuckGo and RapidDNS.", "WARN")
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
    Uses DuckDuckGo for SLD.TLD matches; primary engine for CLI usage.
    Returns a list of domains discovered.
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
    Returns a list of all candidate domains.
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
            if normd == sld and f"{normd}.{extd.suffix}" != f"{sld}.com":
                domains.add(f"{normd}.{extd.suffix}")
        if debug:
            log(f"RapidDNS found: {list(domains)}", "DEBUG")
    except Exception as e:
        log(f"RapidDNS lookup failed: {e}", "WARN")
    return list(domains)


def get_category_and_copyright(domain):
    """
    Extracts simple category and copyright year from website's public HTML.
    Returns (category, copyright year).
    """
    category, year = "Unknown", "N/A"
    try:
        url = f"http://{domain}"
        html = requests.get(url, timeout=5).text.lower()
        for cat in [
            "software",
            "finance",
            "wholesale",
            "agency",
            "consultancy",
            "technology",
            "marketing",
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
    """Classifies lead type by TLD: returns 'High', 'Medium', or 'Low'."""
    suffix = extract(domain).suffix
    high = ["one", "world", "group", "online", "global"]
    medium = ["in", "net", "co", "ai", "biz"]
    if any(suffix.endswith(t) for t in high):
        return "High"
    elif any(suffix.endswith(t) for t in medium):
        return "Medium"
    else:
        return "Low"


def find_leads_for_domains(domains, debug=False):
    """
    Main API function. Finds all leads for a list of domains.

    Args:
        domains (list[str]): Domains to search.
        debug (bool): Enable debug logging.

    Returns:
        dict: Dictionary mapping each source domain to its list of lead dicts.
        Also returns errors as a dict if any failures.
    """
    all_data = {}
    errors = {}
    for i, domain in enumerate(domains, start=1):
        try:
            log(f"Processing domain {i}/{len(domains)}: {domain}", "PROCESS")
            all_data.update(_process_domain(domain, debug))
        except Exception as exc:
            log(f"Fatal error with {domain}: {exc}", "ERROR")
            errors[domain] = str(exc)
    return {"data": all_data, "errors": errors} if errors else all_data


def _process_domain(domain, debug=False):
    """
    Internal workflow for a single domain. Used by both CLI and API.
    Returns dict: { domain: [leads...] }
    """
    sld = normalize_sld(domain)
    log(f"Starting lead search for SLD: '{sld}'", "START")

    tlds = ["co", "in", "net", "group", "online", "world", "ai", "biz", "org", "app"]
    google_results, duck_results = [], []
    for tld in tlds:
        try:
            google_results.extend(google_tld_search(sld, tld, debug=debug))
        except Exception as e:
            log(f"Google search for tld .{tld} failed: {e}", "WARN")
        try:
            duck_results.extend(duckduckgo_tld_search(sld, tld, debug=debug))
        except Exception as e:
            log(f"DuckDuckGo search for tld .{tld} failed: {e}", "WARN")
    try:
        rapid_dns = rapid_dns_lookup(sld, debug=debug)
    except Exception as e:
        log(f"RapidDNS failed: {e}", "WARN")
        rapid_dns = []
    combined_domains = list(set(google_results + duck_results + rapid_dns))
    if debug:
        log(f"Total unique domains found: {len(combined_domains)}", "DEBUG")

    leads = []
    for d in combined_domains:
        try:
            extd = extract(d)
            if extd.domain.lower() != sld or d == domain:
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
        except Exception as e:
            log(f"Failed processing {d}: {e}", "WARN")
    return {domain: leads}


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Domain Lead Finder -- Finds all active domains with same SLD"
    )
    parser.add_argument("-d", help="Single domain input (e.g. apex.com)")
    parser.add_argument("-l", "-f", dest="file", help="File of domains, one per line")
    parser.add_argument("--output", help="Output file (JSON or CSV)")
    parser.add_argument(
        "--debug", action="store_true", help="Enable verbose mode (show logs)"
    )
    args = parser.parse_args()

    if not args.d and not args.file:
        parser.print_help()
        sys.exit(1)

    domains = []
    if args.d:
        domains.append(args.d)
    if args.file:
        try:
            with open(args.file) as f:
                domains.extend([line.strip() for line in f if line.strip()])
        except Exception as e:
            log(f"Error reading domain list: {e}", "ERROR")
            sys.exit(2)

    try:
        results = find_leads_for_domains(domains, debug=args.debug)
        out_data = (
            results["data"]
            if isinstance(results, dict) and "data" in results
            else results
        )
        # Write output file, handling errors.
        if args.output:
            try:
                if args.output.endswith(".json"):
                    with open(args.output, "w") as fh:
                        json.dump(results, fh, indent=2)
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
                        for source, leads in out_data.items():
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
            except Exception as e:
                log(f"Failed to write output file: {e}", "ERROR")
                sys.exit(4)
        else:
            print(json.dumps(results, indent=2))
    except KeyboardInterrupt:
        log("Aborted by user.", "ERROR")
        sys.exit(130)
    except Exception as exc:
        log(f"Fatal (main): {exc}", "ERROR")
        sys.exit(5)
