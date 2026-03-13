"""
IUPHAR/BPS Guide to Pharmacology - Expert-Curated Pharmacological Data
Category: Drug-centric | Type: DB | Subcategory: Drug Knowledgebase
Link: https://www.guidetopharmacology.org/
Paper: https://pubmed.ncbi.nlm.nih.gov/41160876/

Expert-curated, open access database providing pharmacological data on drug
targets and the substances that act on them.

API docs: https://www.guidetopharmacology.org/webServices.jsp
No API key required.
"""

import urllib.request
import urllib.parse
import json


BASE_URL = "https://www.guidetopharmacology.org/services"


def get_all_targets(limit: int = 5) -> list:
    """Retrieve a list of pharmacological targets."""
    url = f"{BASE_URL}/targets"
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())
    return data[:limit]


def get_target_detail(target_id: int) -> dict:
    """Get detailed information about a specific target."""
    url = f"{BASE_URL}/targets/{target_id}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_ligands_for_target(target_id: int, limit: int = 5) -> list:
    """Get ligands (drugs/compounds) that interact with a target."""
    url = f"{BASE_URL}/targets/{target_id}/interactions"
    with urllib.request.urlopen(url, timeout=15) as resp:
        data = json.loads(resp.read())
    return data[:limit]


def search_ligands(name: str) -> list:
    """Search for ligands by name."""
    params = urllib.parse.urlencode({"name": name})
    url = f"{BASE_URL}/ligands?{params}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_ligand_detail(ligand_id: int) -> dict:
    """Get detailed information about a specific ligand."""
    url = f"{BASE_URL}/ligands/{ligand_id}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


if __name__ == "__main__":
    print("=== IUPHAR: First 5 targets ===")
    targets = get_all_targets(5)
    for t in targets:
        print(f"  ID={t.get('targetId')}: {t.get('name')} | Family: {t.get('familyIds')}")

    if targets:
        tid = targets[0]["targetId"]
        print(f"\n=== Target detail: ID={tid} ===")
        detail = get_target_detail(tid)
        print(f"  Name: {detail.get('name')}")
        print(f"  Type: {detail.get('type')}")
        print(f"  Genes: {detail.get('geneIds')}")

        print(f"\n=== Ligands for target {tid} (first 5) ===")
        interactions = get_ligands_for_target(tid, 5)
        for inter in interactions:
            print(f"  Ligand: {inter.get('ligandId')} | "
                  f"Action: {inter.get('action')} | "
                  f"Affinity: {inter.get('affinityRange')}")

    print("\n=== Search ligands: 'morphine' ===")
    ligands = search_ligands("morphine")
    for lig in ligands[:3]:
        print(f"  ID={lig.get('ligandId')}: {lig.get('name')} | Type: {lig.get('type')}")
