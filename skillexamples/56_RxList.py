"""
RxList Drug Descriptions - Detailed Drug Monographs for Clinicians
Category: Drug-centric | Type: DB | Subcategory: Drug Labeling/Info
Link: https://www.rxlist.com/

RxList provides comprehensive, FDA-approved drug monographs including
indications, contraindications, side effects, mechanism of action, and
clinical pharmacology for healthcare professionals.

Note: RxList does not provide a public API.
For structured drug label data, use openFDA (05_openFDA_Human_Drug.py) or
DailyMed (06_DailyMed.py).

This script demonstrates how to fetch a drug page from RxList.
"""

import urllib.request
import urllib.parse
import re
import html as html_module


BASE_URL = "https://www.rxlist.com"


def get_drug_page(drug_name: str) -> str:
    """
    Fetch the RxList drug page for a given drug name.
    RxList URLs follow the pattern: /drug_name-drug.htm
    """
    slug = drug_name.lower().replace(" ", "-")
    url = f"{BASE_URL}/{slug}-drug.htm"
    print(f"GET {url}")
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_drug_description(html_content: str, max_chars: int = 500) -> dict:
    """Extract key information from an RxList drug page."""
    info = {}

    # Title
    title_match = re.search(r"<title>(.*?)</title>", html_content, re.IGNORECASE)
    if title_match:
        info["title"] = html_module.unescape(
            re.sub(r"<[^>]+>", "", title_match.group(1))
        ).strip()

    # Description/overview (first paragraph of content)
    desc_match = re.search(
        r'<div[^>]*class="[^"]*monograph[^"]*"[^>]*>(.*?)</div>',
        html_content, re.IGNORECASE | re.DOTALL
    )
    if desc_match:
        text = html_module.unescape(re.sub(r"<[^>]+>", " ", desc_match.group(1)))
        info["description"] = " ".join(text.split())[:max_chars]

    return info


if __name__ == "__main__":
    drugs_to_look_up = ["aspirin", "metformin", "lisinopril"]

    for drug in drugs_to_look_up:
        print(f"\n=== RxList: {drug} ===")
        try:
            content = get_drug_page(drug)
            info = extract_drug_description(content)
            for k, v in info.items():
                print(f"  {k}: {str(v)[:200]}")
        except Exception as e:
            print(f"  Error: {e}")
            print(f"  Visit {BASE_URL}/{drug}-drug.htm directly.")

    print("\nNote: For systematic drug information access, prefer:")
    print("  openFDA API (no rate limits): python 05_openFDA_Human_Drug.py")
    print("  DailyMed API (official SPL): python 06_DailyMed.py")
