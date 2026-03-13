"""
STITCH - Search Tool for Interactions of Chemicals
Category: Drug-centric | Type: KG | Subcategory: Drug-Target Interaction (DTI)
Link: http://stitch.embl.de/
Paper: https://academic.oup.com/nar/article/44/D1/D380/2503089

STITCH integrates chemical-protein interaction data from experiments, databases,
and text mining, covering direct (binding) and indirect (functional) interactions.

Access method: Download bulk files or use the REST API.
API docs: http://stitch.embl.de/api/
"""

import urllib.request
import urllib.parse
import json
import os

API_BASE = "http://stitch.embl.de/api"
DOWNLOAD_BASE = "https://stringdb-downloads.org/download"


def get_interaction_partners(chemical_id: str, species: int = 9606,
                              required_score: int = 400, limit: int = 10) -> list:
    """
    Get protein interaction partners for a chemical.
    species: 9606 = Homo sapiens
    chemical_id: CIDm or CIDs identifier (e.g., CIDm00004091 for aspirin)
    """
    params = urllib.parse.urlencode({
        "identifiers": chemical_id,
        "species": species,
        "required_score": required_score,
        "limit": limit,
        "format": "json",
    })
    url = f"{API_BASE}/json/interactors?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def resolve_chemical(chemical_name: str, species: int = 9606) -> list:
    """Resolve a chemical name to STITCH identifiers."""
    params = urllib.parse.urlencode({
        "identifier": chemical_name,
        "species": species,
        "format": "json",
    })
    url = f"{API_BASE}/json/resolve?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def download_stitch_chemical_links():
    """
    Download STITCH chemical-protein interaction scores for human.
    File: 9606.actions.v5.0.tsv.gz (~several GB for full file)
    Use the filtered version with score >= 700.
    """
    os.makedirs("STITCH", exist_ok=True)
    # Use protein.links.detailed for chemical-protein interactions
    url = "https://stringdb-downloads.org/download/protein-chemical.links.v5.0/9606.protein_chemical.links.v5.0.tsv.gz"
    fname = "STITCH/9606.protein_chemical.links.v5.0.tsv.gz"
    print(f"Downloading STITCH chemical-protein links for human (~200MB) ...")
    try:
        urllib.request.urlretrieve(url, fname)
        print(f"Saved to {fname}")
        return fname
    except Exception as e:
        print(f"Failed: {e}")
        return None


if __name__ == "__main__":
    print("=== STITCH: Resolve 'aspirin' ===")
    try:
        results = resolve_chemical("aspirin")
        print(f"Results: {results[:3]}")
        if results:
            cid = results[0].get("stringId", results[0].get("id", ""))
            print(f"STITCH ID: {cid}")
            print(f"\n=== STITCH: Interaction partners of aspirin ===")
            partners = get_interaction_partners(cid)
            for p in partners[:5]:
                print(f"  Protein: {p.get('stringId_B')} | Score: {p.get('score')}")
    except Exception as e:
        print(f"API error: {e}")
        print("Trying with direct CID (aspirin = CIDm00001983) ...")
        try:
            partners = get_interaction_partners("CIDm00001983")
            for p in partners[:5]:
                print(f"  Protein: {p.get('stringId_B')} | Score: {p.get('score')}")
        except Exception as e2:
            print(f"  Also failed: {e2}")
            print("  Visit http://stitch.embl.de/ to query STITCH interactively.")
