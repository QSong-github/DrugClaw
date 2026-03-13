"""
BindingDB - Drug-Target Binding Affinity Data
Category: Drug-centric | Type: DB | Subcategory: Drug-Target Interaction (DTI)
Link: https://www.bindingdb.org/
Paper: https://academic.oup.com/nar/article/53/D1/D1633/7906836

BindingDB is a public database of measured binding affinities, focusing on
protein drug-target and small molecule interactions.

Access method: REST API + bulk downloads.
API docs: https://www.bindingdb.org/bind/webservicesPDF.jsp
"""

import urllib.request
import urllib.parse
import json
import os


BASE_URL = "https://www.bindingdb.org/axis2/services/BDBService"


def get_ligands_by_uniprot(uniprot_id: str, cutoff: int = 10000) -> str:
    """Get all ligands that bind to a protein (by UniProt ID)."""
    params = urllib.parse.urlencode({
        "uniprot": uniprot_id,
        "cutoff": cutoff,
        "response": "json",
    })
    url = f"{BASE_URL}/getLigandsByUniprots?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8")


def get_ligands_by_name(drug_name: str) -> str:
    """Search BindingDB for ligands by compound name."""
    params = urllib.parse.urlencode({
        "ligand": drug_name,
        "response": "json",
    })
    url = f"{BASE_URL}/getLigandsByName?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8")


def download_bindingdb_subset():
    """
    Download a small curated subset of BindingDB (FDA-approved drugs only).
    Full database: https://www.bindingdb.org/bind/downloads.jsp
    """
    os.makedirs("BindingDB", exist_ok=True)
    # Smaller subset: ChEMBL-mapped entries
    url = "https://www.bindingdb.org/bind/BindingDB_ChEMBL.tsv.zip"
    fname = "BindingDB/BindingDB_ChEMBL.tsv.zip"
    print(f"Downloading BindingDB ChEMBL subset ...")
    try:
        urllib.request.urlretrieve(url, fname)
        print(f"Saved to {fname}")
        import zipfile
        with zipfile.ZipFile(fname, "r") as zf:
            zf.extractall("BindingDB")
        print("Extracted.")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False


if __name__ == "__main__":
    print("=== BindingDB: Ligands for EGFR (P00533) ===")
    try:
        data = get_ligands_by_uniprot("P00533", cutoff=1000)
        result = json.loads(data)
        affinities = result.get("affinities", [])
        print(f"  Found {len(affinities)} binding entries")
        for entry in affinities[:3]:
            print(f"  Ligand: {entry.get('ligand')} | IC50: {entry.get('ic50')} | Ki: {entry.get('ki')}")
    except Exception as e:
        print(f"  API error: {e}")

    print("\n=== BindingDB: Ligands by name 'imatinib' ===")
    try:
        data = get_ligands_by_name("imatinib")
        result = json.loads(data)
        entries = result.get("affinities", [])
        print(f"  Found {len(entries)} entries")
        for e in entries[:3]:
            print(f"  {e.get('ligand')} | Target: {e.get('uniprot')} | Kd: {e.get('kd')}")
    except Exception as e:
        print(f"  API error: {e}")
        print("  Visit https://www.bindingdb.org/ for full access.")
