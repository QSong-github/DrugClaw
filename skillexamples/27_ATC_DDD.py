"""
ATC/DDD - WHO Anatomical Therapeutic Chemical Classification
Category: Drug-centric | Type: DB | Subcategory: Drug Ontology/Terminology
Link: https://atcddd.fhi.no/atc_ddd_index/

The WHO ATC Classification System classifies drugs at five hierarchical levels
based on organ/system and chemical, pharmacological, therapeutic properties.

Access method: Download the ATC index from WHO/WHOCC or use the online API.
Data available at: https://atcddd.fhi.no/atc_ddd_index/
"""

import urllib.request
import urllib.parse
import os
import json


# WHOCC does not provide a formal REST API, but the index is queryable
WHOCC_BASE = "https://atcddd.fhi.no"
# Alternative: RxNav ATC API from NLM
RXNAV_ATC_URL = "https://rxnav.nlm.nih.gov/REST/rxclass/classMembers.json"


def get_atc_class_drugs(atc_code: str) -> dict:
    """Get drugs belonging to a specific ATC code via RxNav."""
    params = urllib.parse.urlencode({
        "classId": atc_code,
        "relaSource": "ATC",
    })
    url = f"https://rxnav.nlm.nih.gov/REST/rxclass/classMembers.json?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def search_atc_by_drug(drug_name: str) -> dict:
    """Find ATC classification for a drug via RxNav."""
    # First get RxCUI
    params = urllib.parse.urlencode({"name": drug_name})
    rxcui_url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?{params}"
    with urllib.request.urlopen(rxcui_url, timeout=15) as resp:
        rxcui_data = json.loads(resp.read())
    rxcui = rxcui_data.get("idGroup", {}).get("rxnormId", [None])[0]
    if not rxcui:
        return {"error": f"No RxCUI found for '{drug_name}'"}

    # Then get ATC class
    class_url = f"https://rxnav.nlm.nih.gov/REST/rxclass/class/byDrugName.json?drugName={urllib.parse.quote(drug_name)}&relaSource=ATC"
    print(f"GET {class_url}")
    with urllib.request.urlopen(class_url, timeout=15) as resp:
        return json.loads(resp.read())


def get_atc_hierarchy():
    """
    Retrieve ATC hierarchy via RxClass.
    Top-level ATC classes (first level A-Z).
    """
    url = "https://rxnav.nlm.nih.gov/REST/rxclass/allClasses.json?classTypes=ATC1-4"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())
    classes = data.get("rxclassMinConceptList", {}).get("rxclassMinConcept", [])
    return classes


if __name__ == "__main__":
    print("=== ATC/DDD: Find ATC code for 'aspirin' ===")
    try:
        result = search_atc_by_drug("aspirin")
        class_list = result.get("rxclassDrugInfoList", {}).get("rxclassDrugInfo", [])
        for cls in class_list[:5]:
            atc = cls.get("rxclassMinConceptItem", {})
            print(f"  ATC: {atc.get('classId')} - {atc.get('className')}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n=== ATC/DDD: Drugs in class N02BA (Salicylic acid and derivatives) ===")
    try:
        result = get_atc_class_drugs("N02BA")
        members = result.get("drugMemberGroup", {}).get("drugMember", [])
        for m in members[:5]:
            concept = m.get("minConcept", {})
            print(f"  {concept.get('name')} (RxCUI: {concept.get('rxcui')})")
    except Exception as e:
        print(f"  Error: {e}")
        print("  Visit https://atcddd.fhi.no/atc_ddd_index/ for the full ATC index.")
