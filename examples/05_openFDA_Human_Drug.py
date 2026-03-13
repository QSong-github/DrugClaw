"""
openFDA Human Drug - Structured Drug Prescribing Information
Category: Drug-centric | Type: DB | Subcategory: Drug Labeling/Info
Link: https://open.fda.gov/data/downloads/

openFDA provides structured access to FDA drug labeling data (SPL), including
indications, warnings, dosage, adverse reactions, and contraindications.

API docs: https://open.fda.gov/apis/drug/label/
No API key required for up to 1,000 requests/day (240/minute).
"""

import urllib.request
import urllib.parse
import json


BASE_URL = "https://api.fda.gov/drug/label.json"


def get_drug_label(drug_name: str, limit: int = 1) -> dict:
    """Retrieve drug label(s) for a given brand or generic name."""
    query = f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"'
    params = f"search={urllib.parse.quote(query)}&limit={limit}"
    url = f"{BASE_URL}?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def search_by_indication(condition: str, limit: int = 3) -> dict:
    """Search drug labels by indication text."""
    query = f'indications_and_usage:"{condition}"'
    params = f"search={urllib.parse.quote(query)}&limit={limit}"
    url = f"{BASE_URL}?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def count_drugs_by_route(top_n: int = 10) -> dict:
    """Count drug labels grouped by route of administration."""
    params = f"count=openfda.route.exact&limit={top_n}"
    url = f"{BASE_URL}?{params}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


if __name__ == "__main__":
    print("=== Drug Label: Aspirin ===")
    result = get_drug_label("ASPIRIN")
    label = result["results"][0]
    print(f"Brand: {label.get('openfda', {}).get('brand_name', ['N/A'])[0]}")
    indications = label.get("indications_and_usage", ["N/A"])[0]
    print(f"Indications (truncated): {indications[:300]} ...")

    print("\n=== Labels for Hypertension ===")
    result = search_by_indication("hypertension", limit=3)
    for lbl in result.get("results", []):
        brand = lbl.get("openfda", {}).get("brand_name", ["Unknown"])[0]
        print(f"  Brand: {brand}")

    print("\n=== Top Administration Routes ===")
    result = count_drugs_by_route()
    for item in result.get("results", []):
        print(f"  {item['term']}: {item['count']}")
