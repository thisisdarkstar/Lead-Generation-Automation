#!/usr/bin/env python3
"""
domain_lead_finder.py

Minimal Domain Lead Finder — enumerate alternate TLDs for a given SLD, DNS-check, and optional colored output.
Can be used as both CLI tool and importable module.

Dependencies:
    pip install requests beautifulsoup4 tldextract termcolor ddgs python-dotenv

Functions:
    find_leads(domains)
    print_colored_json(data)
    show_api_status()
    (others: probe_dns, google_tld_search, etc.)
"""

import re
import requests
import socket
import sys
import time
import json
import base64
from urllib.parse import quote_plus
from tldextract import extract
from bs4 import BeautifulSoup
from termcolor import colored
import os
from dotenv import load_dotenv
from pathlib import Path

# -- Load API keys from .env only once on import
env_file = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=str(env_file))
CONFIG = {
    "github_token": os.getenv("GITHUB_TOKEN"),
    "virustotal_api_key": os.getenv("VT_API_KEY"),
}


def log(message, level="INFO"):
    """Colored logging for informational output."""
    colors = {
        "START": "cyan",
        "PROCESS": "blue",
        "INFO": "green",
        "WARN": "magenta",
        "ERROR": "red",
        "DONE": "green",
    }
    print(colored(f"[{level}] {message}", colors.get(level, "white")))


def mask_key(key, start=4, end=4):
    """Returns masked version of API key for privacy."""
    return f"{key[:start]}****...{key[-end:]}" if key else "Missing"


def show_api_status():
    """Print availability/masking of configured API keys."""
    print("\nAPI Key Status:\n------------------------------")
    print(f"GitHub         : {mask_key(CONFIG['github_token'])}")
    print(f"VirusTotal     : {mask_key(CONFIG['virustotal_api_key'])}")
    print("------------------------------\n")


def normalize_sld(domain):
    """Extracts SLD and TLD from input domain."""
    ext = extract(domain)
    return ext.domain.lower(), ext.suffix.lower()


def probe_dns(domain):
    """Checks if domain resolves in DNS (True/False)."""
    try:
        socket.setdefaulttimeout(3)
        socket.gethostbyname(domain)
        return True
    except Exception:
        return False


def google_tld_search(sld, tld):
    """Get domains from Google search for SLD.TLD."""
    headers = {"User-Agent": "Mozilla/5.0"}
    query = f'"{sld}" site:.{tld}'
    try:
        res = requests.get(
            f"https://www.google.com/search?q={quote_plus(query)}",
            headers=headers,
            timeout=10,
        )
        soup = BeautifulSoup(res.text, "html.parser")
        result = set()
        for a in soup.find_all("a", href=True):
            h = a["href"]
            if h.startswith("/url?q="):
                url = h.split("/url?q=")[1].split("&")[0]
                extd = extract(url)
                if extd.domain == sld and extd.suffix == tld:
                    result.add(f"{sld}.{tld}")
        return list(result)
    except Exception:
        return []


def bing_tld_search(sld, tld):
    """Get domains from Bing search for SLD.TLD."""
    headers = {"User-Agent": "Mozilla/5.0"}
    query = f'"{sld}" site:.{tld}'
    try:
        res = requests.get(
            f"https://www.bing.com/search?q={quote_plus(query)}",
            headers=headers,
            timeout=10,
        )
        soup = BeautifulSoup(res.text, "html.parser")
        result = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            extd = extract(href)
            if extd.domain == sld and extd.suffix == tld:
                result.add(f"{sld}.{tld}")
        return list(result)
    except Exception:
        return []


def duckduckgo_tld_search(sld, tld):
    """Get domains from DuckDuckGo search for SLD.TLD."""
    try:
        from ddgs import DDGS
    except ImportError:
        return []
    result = set()
    query = f'"{sld}" site:.{tld}'
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=20):
                url = r.get("href") or r.get("url")
                extd = extract(url)
                if extd.domain == sld and extd.suffix == tld:
                    result.add(f"{sld}.{tld}")
    except Exception:
        pass
    return list(result)


def rapid_dns_lookup(sld):
    """Get domains from RapidDNS for SLD.*."""
    url = f"https://rapiddns.io/same/{sld}?full=1"
    result = set()
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        for tag in soup.find_all("a", href=True):
            dom = tag.text.strip()
            extd = extract(dom)
            if extd.domain == sld and extd.suffix:
                result.add(f"{sld}.{extd.suffix}")
    except Exception:
        pass
    return list(result)


def github_code_search(sld):
    """Search GitHub code for SLD.TLD combos."""
    token = CONFIG["github_token"]
    if not token:
        return []
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    query = f'"{sld}." in:file'
    result = set()
    try:
        r = requests.get(
            f"https://api.github.com/search/code?q={quote_plus(query)}",
            headers=headers,
            timeout=10,
        )
        for item in r.json().get("items", []):
            file_url = item.get("url")
            content_res = requests.get(file_url, headers=headers, timeout=10)
            if content_res.status_code == 200:
                data = content_res.json()
                content = base64.b64decode(data.get("content", "")).decode(
                    "utf-8", errors="ignore"
                )
                matches = re.findall(rf"{sld}\.([a-z]{{2,10}})", content, re.IGNORECASE)
                for tld in matches:
                    result.add(f"{sld}.{tld}")
        return list(result)
    except Exception:
        return []


def virustotal_passive_dns(sld):
    """Query VirusTotal for SLD.TLD combos if API key supplied."""
    token = CONFIG["virustotal_api_key"]
    if not token:
        return []
    headers = {"x-apikey": token}
    tlds = [
        "com",
        "net",
        "org",
        "io",
        "co",
        "in",
        "sh",
        "biz",
        "app",
        "me",
        "info",
        "site",
        "group",
        "world",
        "online",
    ]
    result = set()
    for t in tlds:
        dom = f"{sld}.{t}"
        url = f"https://www.virustotal.com/api/v3/domains/{dom}"
        try:
            r = requests.get(url, headers=headers, timeout=6)
            if r.status_code == 200 and "data" in r.json():
                result.add(dom)
        except Exception:
            pass
    return list(result)


def all_tld_domains(sld, exclude=None):
    """Find all possible TLDs for an SLD (excluding input TLD)."""
    tlds = [
        "co",
        "in",
        "net",
        "group",
        "online",
        "world",
        "ai",
        "biz",
        "org",
        "app",
        "io",
        "info",
        "sh",
        "site",
        "store",
        "cloud",
        "me",
    ]
    all_domains = set()
    for tld in tlds:
        if tld == exclude:
            continue
        all_domains.update(google_tld_search(sld, tld))
        all_domains.update(bing_tld_search(sld, tld))
        all_domains.update(duckduckgo_tld_search(sld, tld))
    all_domains.update(rapid_dns_lookup(sld))
    all_domains.update(github_code_search(sld))
    all_domains.update(virustotal_passive_dns(sld))
    return all_domains


def find_leads(domains):
    """
    Main routine: For a list of input domains, returns dictionary:
    { "input.com": [ { "domain": "other.net", "url": "http://other.net" }, ... ] }
    Only outputs DNS-resolving (active) domains.
    """
    result = {}
    for dom in domains:
        sld, orig_tld = normalize_sld(dom)
        log(f"Finding TLDs for '{sld}', excluding .{orig_tld}", "PROCESS")
        found = []
        for d in all_tld_domains(sld, exclude=orig_tld):
            extd = extract(d)
            if extd.domain != sld or d == dom:
                continue
            if probe_dns(d):
                found.append({"domain": d, "url": f"http://{d}"})
                log(f"{d:30} [ACTIVE]", "INFO")
            else:
                log(f"{d:30} [INACTIVE]", "WARN")
        result[dom] = found
    return result


def print_colored_json(data):
    """
    Pretty print colored JSON-like structure to terminal.
    """
    for input_domain, items in data.items():
        print(colored(f"\n{input_domain}:", "cyan", attrs=["bold"]))
        if not items:
            print(colored("  (no active alternate TLDs found)", "red"))
        for d in items:
            print(
                colored("  domain: ", "yellow", attrs=["bold"])
                + colored(d["domain"], "green")
                + colored(" | url: ", "magenta", attrs=["bold"])
                + colored(d["url"], "blue")
            )


# CLI/standalone usage below
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Minimal Domain Lead Finder — alternate TLDs, DNS-check, colored log."
    )
    parser.add_argument("-d", help="Single domain (e.g. apex.com)")
    parser.add_argument("-f", dest="file", help="File of domains, one per line")
    parser.add_argument("--output", help="Results file (JSON)")
    parser.add_argument(
        "--check-apis", action="store_true", help="Print API status and exit"
    )
    args = parser.parse_args()

    if args.check_apis:
        show_api_status()
        sys.exit(0)

    domains = []
    if args.d:
        domains.append(args.d)
    if args.file:
        try:
            with open(args.file) as f:
                domains += [line.strip() for line in f if line.strip()]
        except Exception as e:
            log(f"Error reading domain list: {e}", "ERROR")
            sys.exit(2)
    if not domains:
        parser.print_help()
        sys.exit(1)

    try:
        results = find_leads(domains)
        if args.output:
            with open(args.output, "w") as fh:
                json.dump(results, fh, indent=2)
            log(f"Results saved to {args.output}", "DONE")
        else:
            print_colored_json(results)

    except KeyboardInterrupt:
        log("Aborted by user.", "ERROR")
        sys.exit(130)
    except Exception as exc:
        log(f"Fatal (main): {exc}", "ERROR")
        sys.exit(5)
