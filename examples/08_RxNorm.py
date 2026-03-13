"""
RxNorm - Drug Naming Standardization and Normalization
Category: Drug-centric | Type: DB | Subcategory: Drug Ontology/Terminology
Link: https://www.nlm.nih.gov/research/umls/rxnorm/
Paper: https://academic.oup.com/jamia/article-abstract/18/4/441/734170

RxNorm provides normalized names for clinical drugs. Maintained by the U.S.
National Library of Medicine.

API docs: https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html
No API key required.
"""

import urllib.request
import urllib.parse
import json


BASE_URL = "https://rxnav.nlm.nih.gov/REST"


def find_rxcui(drug_name: str) -> dict:
    """Find the RxNorm concept unique identifier (RxCUI) for a drug name."""
    params = urllib.parse.urlencode({"name": drug_name})
    url = f"{BASE_URL}/rxcui.json?{params}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_drug_info(rxcui: str) -> dict:
    """Get detailed information for an RxCUI."""
    url = f"{BASE_URL}/rxcui/{rxcui}/allinfo.json"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_drug_interactions(rxcui: str) -> dict:
    """Retrieve drug interaction data for an RxCUI."""
    url = f"https://rxnav.nlm.nih.gov/REST/interaction/interaction.json?rxcui={rxcui}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_related_drugs(rxcui: str, relation_type: str = "tradeName") -> dict:
    """Get related drugs (e.g., trade names) for an RxCUI."""
    url = f"{BASE_URL}/rxcui/{rxcui}/related.json?tty={relation_type}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def normalize_drug_name(drug_name: str) -> str:
    """Return the normalized RxNorm name for a drug string."""
    params = urllib.parse.urlencode({"name": drug_name, "search": 1})
    url = f"{BASE_URL}/approximateTerm.json?{params}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())
    candidates = data.get("approximateGroup", {}).get("candidate", [])
    if candidates:
        return candidates[0].get("name", drug_name)
    return drug_name


if __name__ == "__main__":
    print("=== RxNorm: Find RxCUI for 'aspirin' ===")
    result = find_rxcui("aspirin")
    rxcui_id = result.get("idGroup", {}).get("rxnormId", [None])[0]
    print(f"RxCUI: {rxcui_id}")

    if rxcui_id:
        print(f"\n=== Drug Info for RxCUI {rxcui_id} ===")
        info = get_drug_info(rxcui_id)
        props = info.get("rxcuiStatusHistory", {}).get("attributes", {})
        print(f"  Name: {props.get('name')}")
        print(f"  TTY: {props.get('tty')}")

        print(f"\n=== Drug Interactions for RxCUI {rxcui_id} ===")
        interactions = get_drug_interactions(rxcui_id)
        pairs = interactions.get("interactionTypeGroup", [])
        if pairs:
            for group in pairs[:2]:
                for itype in group.get("interactionType", [])[:2]:
                    for pair in itype.get("interactionPair", [])[:2]:
                        desc = pair.get("description", "")
                        print(f"  {desc[:120]}")
        else:
            print("  No interaction data found.")

    print("\n=== Normalize 'tylenol' ===")
    normalized = normalize_drug_name("tylenol")
    print(f"  Normalized: {normalized}")
