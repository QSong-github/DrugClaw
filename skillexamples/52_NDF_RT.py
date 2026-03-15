"""
NDF-RT - National Drug File Reference Terminology
Category: Drug-centric | Type: KG | Subcategory: Drug Ontology/Terminology
Link: https://evsexplore.semantics.cancer.gov/evsexplore/welcome?terminology=ndfrt

NDF-RT is an ontology of drug mechanisms of action, physiological effects, and
chemical structures extending the VA National Drug File drug terminology.

Access method: NCI EVS REST API
API docs: https://api-evsrest.nci.nih.gov/api/v1
No API key required.
"""

import urllib.request
import urllib.parse
import json


EVS_BASE = "https://api-evsrest.nci.nih.gov/api/v1"
TERMINOLOGY = "ndfrt"


def search_ndfrt(term: str, limit: int = 5) -> dict:
    """Search NDF-RT concepts by name."""
    params = urllib.parse.urlencode({
        "terminology": TERMINOLOGY,
        "term": term,
        "pageSize": limit,
    })
    url = f"{EVS_BASE}/concept/search?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_concept(code: str) -> dict:
    """Get detailed concept information by NDF-RT code."""
    url = f"{EVS_BASE}/concept/{TERMINOLOGY}/{code}?include=full"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_concept_children(code: str) -> dict:
    """Get child concepts for a given NDF-RT code."""
    url = f"{EVS_BASE}/concept/{TERMINOLOGY}/{code}/children"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_all_roots() -> dict:
    """Get the top-level root concepts in NDF-RT."""
    url = f"{EVS_BASE}/concept/{TERMINOLOGY}/roots"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


if __name__ == "__main__":
    print("=== NDF-RT: Search 'aspirin' ===")
    result = search_ndfrt("aspirin", limit=5)
    concepts = result.get("concepts", [])
    for c in concepts[:3]:
        print(f"  Code: {c.get('code')} | Name: {c.get('name')}")

    if concepts:
        code = concepts[0]["code"]
        print(f"\n=== NDF-RT: Concept detail for {code} ===")
        detail = get_concept(code)
        print(f"  Name: {detail.get('name')}")
        props = detail.get("properties", [])
        for p in props[:5]:
            print(f"  {p.get('type')}: {p.get('value', '')[:80]}")

    print("\n=== NDF-RT: Root concepts ===")
    try:
        roots = get_all_roots()
        root_list = roots if isinstance(roots, list) else roots.get("concepts", [])
        for r in root_list[:5]:
            print(f"  Code: {r.get('code')} | Name: {r.get('name')}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n=== NDF-RT: Search 'pharmacological effect' ===")
    result = search_ndfrt("pharmacological effect", limit=3)
    for c in result.get("concepts", [])[:3]:
        print(f"  Code: {c.get('code')} | Name: {c.get('name')}")
