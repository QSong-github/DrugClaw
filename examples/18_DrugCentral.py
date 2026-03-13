"""
DrugCentral - Comprehensive Drug Pharmacology
Category: Drug-centric | Type: DB | Subcategory: Drug Knowledgebase
Link: https://drugcentral.org/
Paper: https://academic.oup.com/nar/article/45/D1/D932/2333938

DrugCentral integrates structure, bioactivity, regulatory, pharmacological,
and disease data for drugs approved for human or veterinary use.

API docs: https://drugcentral.org/api
No API key required.
"""

import urllib.request
import urllib.parse
import json


BASE_URL = "https://drugcentral.org/api/v1"


def search_drug(name: str) -> dict:
    """Search DrugCentral by drug name."""
    params = urllib.parse.urlencode({"name": name})
    url = f"{BASE_URL}/drugs?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_drug_targets(drug_id: int) -> dict:
    """Get drug targets by DrugCentral drug ID."""
    url = f"{BASE_URL}/drugs/{drug_id}/targets"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_drug_indications(drug_id: int) -> dict:
    """Get disease indications for a drug."""
    url = f"{BASE_URL}/drugs/{drug_id}/indications"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def download_full_database():
    """Download the full DrugCentral dump (PostgreSQL SQL file)."""
    import os
    dump_url = "https://unmtid-shinyapps.net/download/drugcentral.dump.11012023.sql.gz"
    fname = "drugcentral.dump.sql.gz"
    if os.path.exists(fname):
        print(f"Already exists: {fname}")
        return
    print(f"Downloading DrugCentral database dump (~500 MB) ...")
    urllib.request.urlretrieve(dump_url, fname)
    print(f"Saved to {fname}")


if __name__ == "__main__":
    print("=== DrugCentral: Search 'aspirin' ===")
    try:
        result = search_drug("aspirin")
        drugs = result if isinstance(result, list) else result.get("data", [])
        for drug in drugs[:3]:
            drug_id = drug.get("id") or drug.get("drug_id")
            print(f"  ID={drug_id}: {drug.get('name')} | INN: {drug.get('inn')}")

        if drugs:
            drug_id = drugs[0].get("id") or drugs[0].get("drug_id")
            if drug_id:
                print(f"\n=== Targets for drug ID={drug_id} ===")
                targets = get_drug_targets(drug_id)
                t_list = targets if isinstance(targets, list) else targets.get("data", [])
                for t in t_list[:5]:
                    print(f"  {t.get('gene_symbol') or t.get('name')}: {t.get('action_type')}")
    except Exception as e:
        print(f"API error: {e}")
        print("Visit https://drugcentral.org/ for interactive access.")
