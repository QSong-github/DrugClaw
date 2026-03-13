"""
nSIDES - EHR-Derived Drug Side Effects
Category: Drug-centric | Type: DB | Subcategory: Adverse Drug Reaction (ADR)
Link: https://nsides.io/
Paper: https://www.science.org/doi/10.1126/scitranslmed.3003377

nSIDES provides drug side effects and polypharmacy adverse events mined from
electronic health records using statistical disproportionality methods.

API docs: https://nsides.io/ (REST API)
"""

import urllib.request
import urllib.parse
import json


BASE_URL = "https://nsides.io/api/v1"


def get_drug_outcomes(drug_concept_id: int, limit: int = 10) -> dict:
    """Get adverse outcomes associated with a drug by OMOP concept ID."""
    params = urllib.parse.urlencode({
        "drug": drug_concept_id,
        "limit": limit
    })
    url = f"{BASE_URL}/drug/{drug_concept_id}/outcomes?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_outcome_drugs(outcome_concept_id: int, limit: int = 10) -> dict:
    """Get drugs associated with a specific adverse outcome."""
    params = urllib.parse.urlencode({"limit": limit})
    url = f"{BASE_URL}/outcome/{outcome_concept_id}/drugs?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def search_concept(name: str) -> dict:
    """Search OMOP concepts by name."""
    params = urllib.parse.urlencode({"q": name})
    url = f"{BASE_URL}/concepts?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


if __name__ == "__main__":
    # Aspirin OMOP concept ID: 1112807
    ASPIRIN_ID = 1112807
    print(f"=== nSIDES: Adverse outcomes for Aspirin (concept_id={ASPIRIN_ID}) ===")
    try:
        result = get_drug_outcomes(ASPIRIN_ID, limit=5)
        outcomes = result.get("results", result if isinstance(result, list) else [])
        for item in outcomes[:5]:
            print(f"  Outcome: {item.get('outcome_concept_name', item.get('concept_name', item))}")
    except Exception as e:
        print(f"  API error: {e}")
        print("  Visit https://nsides.io/ to explore the data interactively.")

    print("\n=== nSIDES: Search concept 'aspirin' ===")
    try:
        concepts = search_concept("aspirin")
        items = concepts if isinstance(concepts, list) else concepts.get("results", [])
        for item in items[:3]:
            print(f"  concept_id={item.get('concept_id')}: {item.get('concept_name')}")
    except Exception as e:
        print(f"  API error: {e}")
