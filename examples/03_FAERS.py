"""
FAERS - FDA Adverse Event Reporting System
Category: Drug-centric | Type: DB | Subcategory: Adverse Drug Reaction (ADR)
Link: https://www.fda.gov/drugs/surveillance/fdas-adverse-event-reporting-system-faers

FAERS collects spontaneous reports of adverse events and medication errors.
Accessible via the openFDA API (no API key required for basic use).

API docs: https://open.fda.gov/apis/drug/event/
"""

import urllib.request
import json


BASE_URL = "https://api.fda.gov/drug/event.json"


def search_adverse_events(drug_name: str, limit: int = 5) -> dict:
    """Search adverse event reports for a given drug name."""
    query = f'patient.drug.medicinalproduct:"{drug_name}"'
    params = f"search={urllib.parse.quote(query)}&limit={limit}"
    url = f"{BASE_URL}?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def count_reactions_for_drug(drug_name: str, top_n: int = 10) -> dict:
    """Count the top adverse reactions reported for a drug."""
    import urllib.parse
    query = f'patient.drug.medicinalproduct:"{drug_name}"'
    params = (
        f"search={urllib.parse.quote(query)}"
        f"&count=patient.reaction.reactionmeddrapt.exact&limit={top_n}"
    )
    url = f"{BASE_URL}?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_faers_metadata() -> dict:
    """Retrieve FAERS dataset metadata (total record count, date range)."""
    import urllib.parse
    url = f"{BASE_URL}?limit=1"
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())
    meta = data.get("meta", {})
    results = data.get("meta", {}).get("results", {})
    return {"total": results.get("total"), "last_updated": meta.get("last_updated")}


if __name__ == "__main__":
    import urllib.parse

    print("=== FAERS Metadata ===")
    meta = get_faers_metadata()
    print(f"Total adverse event reports: {meta['total']:,}")
    print(f"Last updated: {meta['last_updated']}")

    print("\n=== Top Reactions for Aspirin ===")
    result = count_reactions_for_drug("ASPIRIN", top_n=10)
    for item in result.get("results", []):
        print(f"  {item['term']}: {item['count']}")

    print("\n=== Sample Adverse Event Reports for Ibuprofen ===")
    result = search_adverse_events("IBUPROFEN", limit=3)
    for report in result.get("results", []):
        drugs = [d.get("medicinalproduct", "") for d in report.get("patient", {}).get("drug", [])]
        reactions = [r.get("reactionmeddrapt", "") for r in report.get("patient", {}).get("reaction", [])]
        print(f"  Drugs: {drugs} | Reactions: {reactions}")
