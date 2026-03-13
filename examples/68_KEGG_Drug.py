"""
KEGG Drug - Approved Drugs and Their Molecular Mechanisms
Category: Drug-centric | Type: DB | Subcategory: Drug-Drug Interaction (DDI)
Link: https://www.genome.jp/kegg/
Paper: https://academic.oup.com/nar/article/38/suppl_1/D355/3112250

KEGG Drug is a curated database of approved drugs with chemical structures,
drug targets, metabolic pathways, and drug-drug interactions, integrated with
KEGG pathway and disease maps.

API docs: https://www.kegg.jp/kegg/docs/keggapi.html
No API key required (free for academic use).
"""

import urllib.request
import urllib.parse
import os

KEGG_BASE = "https://rest.kegg.jp"


def search_kegg_drug(query: str) -> list:
    """Search KEGG Drug by name or keyword."""
    url = f"{KEGG_BASE}/find/drug/{urllib.parse.quote(query)}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        text = resp.read().decode("utf-8")
    results = []
    for line in text.strip().split("\n"):
        if "\t" in line:
            drug_id, name = line.split("\t", 1)
            results.append({"id": drug_id.strip(), "name": name.strip()})
    return results


def get_drug_entry(drug_id: str) -> str:
    """Get the full KEGG Drug entry for a drug ID (e.g., D00109)."""
    url = f"{KEGG_BASE}/get/{drug_id}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return resp.read().decode("utf-8")


def get_drug_targets(drug_id: str) -> list:
    """Get target genes/proteins for a KEGG Drug entry."""
    entry = get_drug_entry(drug_id)
    targets = []
    in_target_section = False
    for line in entry.split("\n"):
        if line.startswith("TARGET"):
            in_target_section = True
        elif in_target_section:
            if line.startswith(" "):
                targets.append(line.strip())
            else:
                in_target_section = False
    return targets


def get_drug_interactions(drug_id: str) -> str:
    """Get drug interaction section from KEGG Drug entry."""
    entry = get_drug_entry(drug_id)
    ddi_section = []
    in_ddi = False
    for line in entry.split("\n"):
        if line.startswith("INTERACTION"):
            in_ddi = True
        elif in_ddi:
            if line.startswith(" "):
                ddi_section.append(line.strip())
            else:
                in_ddi = False
    return "\n".join(ddi_section)


def get_kegg_pathway(pathway_id: str) -> str:
    """Get a KEGG pathway entry."""
    url = f"{KEGG_BASE}/get/{pathway_id}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return resp.read().decode("utf-8")


def list_drug_network(drug_id: str) -> list:
    """Get all KEGG interactions (network) for a drug."""
    url = f"{KEGG_BASE}/get/{drug_id}/network"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            text = resp.read().decode("utf-8")
        return text.strip().split("\n")
    except Exception as e:
        return [f"Error: {e}"]


if __name__ == "__main__":
    print("=== KEGG Drug: Search 'aspirin' ===")
    results = search_kegg_drug("aspirin")
    for r in results[:5]:
        print(f"  {r['id']}: {r['name']}")

    if results:
        drug_id = results[0]["id"]
        print(f"\n=== KEGG Drug: Entry for {drug_id} ===")
        entry = get_drug_entry(drug_id)
        # Print first 20 lines
        for line in entry.split("\n")[:20]:
            print(f"  {line}")

        print(f"\n=== Targets for {drug_id} ===")
        targets = get_drug_targets(drug_id)
        for t in targets[:5]:
            print(f"  {t}")

        print(f"\n=== Drug Interactions for {drug_id} ===")
        ddi = get_drug_interactions(drug_id)
        if ddi:
            print(ddi[:300])
        else:
            print("  No interaction data in entry.")

    print("\n=== KEGG Drug: Search 'imatinib' (Gleevec) ===")
    results = search_kegg_drug("imatinib")
    for r in results[:3]:
        print(f"  {r['id']}: {r['name']}")

    print("\n=== KEGG Drug: Search 'metformin' ===")
    results = search_kegg_drug("metformin")
    for r in results[:3]:
        print(f"  {r['id']}: {r['name']}")
