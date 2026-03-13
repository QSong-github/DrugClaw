"""
ChEMBL - Drug Bioactivity and Target Data
Category: Drug-centric | Type: DB | Subcategory: Drug-Target Interaction (DTI)
Link: https://www.ebi.ac.uk/chembl/
Paper: https://doi.org/10.1093/nar/gkad1004

ChEMBL is a manually curated database of bioactive molecules with drug-like
properties, containing binding, functional, and ADMET data.

API docs: https://chembl.gitbook.io/chembl-interface-documentation/web-services/chembl-data-web-services
No API key required.
"""

import urllib.request
import urllib.parse
import json


BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"


def get_molecule(chembl_id: str) -> dict:
    """Retrieve molecule data by ChEMBL ID."""
    url = f"{BASE_URL}/molecule/{chembl_id}.json"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def search_molecules(name: str, limit: int = 5) -> dict:
    """Search molecules by preferred name."""
    params = urllib.parse.urlencode({"pref_name__icontains": name, "limit": limit})
    url = f"{BASE_URL}/molecule.json?{params}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_bioactivities(chembl_id: str, limit: int = 5) -> dict:
    """Get bioactivity data for a molecule."""
    params = urllib.parse.urlencode({"molecule_chembl_id": chembl_id, "limit": limit})
    url = f"{BASE_URL}/activity.json?{params}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_target(chembl_id: str) -> dict:
    """Retrieve target data by ChEMBL target ID."""
    url = f"{BASE_URL}/target/{chembl_id}.json"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def search_targets(gene_name: str, limit: int = 5) -> dict:
    """Search drug targets by gene/protein name."""
    params = urllib.parse.urlencode({"target_synonym__icontains": gene_name, "limit": limit})
    url = f"{BASE_URL}/target.json?{params}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


if __name__ == "__main__":
    print("=== ChEMBL Molecule: Aspirin (CHEMBL25) ===")
    mol = get_molecule("CHEMBL25")
    props = mol.get("molecule_properties", {})
    print(f"  Name: {mol.get('pref_name')}")
    print(f"  MW: {props.get('full_mwt')}")
    print(f"  AlogP: {props.get('alogp')}")
    print(f"  RO5 violations: {props.get('num_ro5_violations')}")

    print("\n=== Search Molecules: 'ibuprofen' ===")
    result = search_molecules("ibuprofen")
    for m in result.get("molecules", [])[:3]:
        print(f"  {m.get('chembl_id')}: {m.get('pref_name')}")

    print("\n=== Bioactivities for CHEMBL25 (top 5) ===")
    activities = get_bioactivities("CHEMBL25")
    for act in activities.get("activities", []):
        print(f"  Target: {act.get('target_chembl_id')} | "
              f"Type: {act.get('standard_type')} | "
              f"Value: {act.get('standard_value')} {act.get('standard_units')}")

    print("\n=== Search Targets: 'EGFR' ===")
    targets = search_targets("EGFR")
    for t in targets.get("targets", [])[:3]:
        print(f"  {t.get('chembl_id')}: {t.get('pref_name')} ({t.get('target_type')})")
