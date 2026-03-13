"""
CPIC - Clinical Pharmacogenomics Implementation Consortium
Category: Drug-centric | Type: DB | Subcategory: Drug Knowledgebase
Link: https://cpicpgx.org/

CPIC provides peer-reviewed, regularly updated pharmacogenomics prescribing
guidelines to help clinicians interpret genetic test results and optimize therapy.

API docs: https://cpicpgx.org/cpic-data/
No API key required.
"""

import urllib.request
import urllib.parse
import json
import os

BASE_URL = "https://api.cpicpgx.org/v1"


def get_all_guidelines() -> list:
    """Retrieve all CPIC pharmacogenomics guidelines."""
    url = f"{BASE_URL}/guideline"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_guideline_by_drug(drug_name: str) -> list:
    """Get CPIC guidelines for a specific drug."""
    url = f"{BASE_URL}/guideline"
    with urllib.request.urlopen(url, timeout=15) as resp:
        all_guidelines = json.loads(resp.read())
    matching = [g for g in all_guidelines
                if drug_name.lower() in str(g.get("name", "")).lower()
                or drug_name.lower() in str(g.get("drugs", "")).lower()]
    return matching


def get_gene_drug_pairs() -> list:
    """Get all gene-drug pairs with CPIC guidelines."""
    url = f"{BASE_URL}/pair?select=genesymbol,drugname,cpiclevel,pgkbcalevel,pgxtesting,citations"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_drug_recommendations(drug_name: str) -> list:
    """Get dosing recommendations for a drug."""
    params = urllib.parse.urlencode({"drugname": f"eq.{drug_name}"})
    url = f"{BASE_URL}/recommendation?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def download_cpic_data():
    """Download CPIC gene-drug pairs and allele definitions."""
    os.makedirs("CPIC", exist_ok=True)
    # Gene-drug pairs CSV
    url = "https://raw.githubusercontent.com/cpicpgx/cpic-data/master/gene-drug-pairs.csv"
    fname = "CPIC/gene_drug_pairs.csv"
    print("Downloading CPIC gene-drug pairs ...")
    try:
        urllib.request.urlretrieve(url, fname)
        print(f"Saved to {fname}")
        return fname
    except Exception as e:
        print(f"Failed: {e}")
        return None


if __name__ == "__main__":
    print("=== CPIC: All guidelines (first 5) ===")
    try:
        guidelines = get_all_guidelines()
        print(f"Total guidelines: {len(guidelines)}")
        for g in guidelines[:5]:
            print(f"  {g.get('name')} | Status: {g.get('status')} | "
                  f"Version: {g.get('version')}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n=== CPIC: Gene-drug pairs (first 10) ===")
    try:
        pairs = get_gene_drug_pairs()
        print(f"Total gene-drug pairs: {len(pairs)}")
        for p in pairs[:10]:
            print(f"  Gene: {p.get('genesymbol')} | Drug: {p.get('drugname')} | "
                  f"CPIC Level: {p.get('cpiclevel')}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n=== CPIC: Guidelines for 'clopidogrel' ===")
    try:
        matching = get_guideline_by_drug("clopidogrel")
        for g in matching[:3]:
            print(f"  {g.get('name')} | URL: {g.get('url', '')}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n=== CPIC: Download gene-drug pairs ===")
    fpath = download_cpic_data()
    if fpath:
        import csv
        with open(fpath, newline="", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            print(f"Columns: {reader.fieldnames}")
            for i, row in enumerate(reader):
                if i >= 3:
                    break
                print(f"  {row}")
