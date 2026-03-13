"""
DailyMed - Current Drug Prescribing Information
Category: Drug-centric | Type: DB | Subcategory: Drug Labeling/Info
Link: https://dailymed.nlm.nih.gov/dailymed/spl-resources.cfm

DailyMed is the official U.S. provider of FDA label information (package
inserts) for prescription and OTC drugs, offering full-text SPL documents.

API docs: https://dailymed.nlm.nih.gov/dailymed/app-support-web-services.cfm
No API key required.
"""

import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET


BASE_URL = "https://dailymed.nlm.nih.gov/dailymed/services/v2"


def search_drug_labels(drug_name: str, limit: int = 5) -> list:
    """Search drug SPL labels by drug name."""
    params = urllib.parse.urlencode({"drug_name": drug_name, "pagesize": limit})
    url = f"{BASE_URL}/spls.json?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())
    return data.get("data", [])


def get_label_detail(set_id: str) -> dict:
    """Get full label detail by SPL set ID."""
    url = f"{BASE_URL}/spls/{set_id}.json"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_ndc_info(ndc: str) -> dict:
    """Retrieve label information for an NDC code."""
    url = f"{BASE_URL}/ndc/{ndc}.json"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


if __name__ == "__main__":
    print("=== Search DailyMed for 'metformin' ===")
    results = search_drug_labels("metformin", limit=5)
    for item in results:
        print(f"  Title: {item.get('title')} | SetId: {item.get('setid')}")

    if results:
        set_id = results[0]["setid"]
        print(f"\n=== Label detail for set_id={set_id} ===")
        detail = get_label_detail(set_id)
        spl = detail.get("data", {})
        print(f"  Title: {spl.get('title')}")
        print(f"  Published: {spl.get('published_date')}")
