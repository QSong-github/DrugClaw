"""
DILI - Drug-Induced Liver Injury Dataset from ChEMBL
Category: Drug-centric | Type: Dataset | Subcategory: Drug Toxicity
Link: https://doi.org/10.1021/acs.chemrestox.0c00296
Paper: https://doi.org/10.1021/acs.chemrestox.0c00296

Reviews systematic curation of drug safety data (boxed warnings and withdrawn
drugs) from the ChEMBL bioactivity database and methods to model these safety
outcomes for toxicology research.

Access method:
  1. Access DILI data via ChEMBL REST API (assay-based)
  2. Download supplemental data from the paper
  3. Use ChEMBL's curated safety data endpoint
"""

import urllib.request
import urllib.parse
import json
import os
import csv

OUTPUT_DIR = "DILI_ChEMBL"
CHEMBL_BASE = "https://www.ebi.ac.uk/chembl/api/data"


def get_dili_compounds_from_chembl(limit: int = 20) -> dict:
    """
    Retrieve DILI-related compounds from ChEMBL using the drug warning endpoint.
    ChEMBL contains drug safety warnings including DILI-related hepatotoxicity data.
    """
    params = urllib.parse.urlencode({
        "warning_type": "LIVER TOXICITY",
        "format": "json",
        "limit": limit,
    })
    url = f"{CHEMBL_BASE}/drug_warning.json?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def get_hepatotoxicity_assays(limit: int = 10) -> dict:
    """Get hepatotoxicity-related bioassays from ChEMBL."""
    params = urllib.parse.urlencode({
        "assay_type": "T",
        "description__icontains": "hepatotoxicity",
        "limit": limit,
        "format": "json",
    })
    url = f"{CHEMBL_BASE}/assay.json?{params}"
    print(f"GET {url}")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read())


def download_supplement_data():
    """
    Download supplemental DILI data from the paper (ACS Chem. Research Toxicology).
    The paper DOI: 10.1021/acs.chemrestox.0c00296
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # ACS supplemental data download URL
    supp_url = "https://pubs.acs.org/doi/suppl/10.1021/acs.chemrestox.0c00296/suppl_file/tx0c00296_si_001.xlsx"
    fname = os.path.join(OUTPUT_DIR, "DILI_supplement.xlsx")
    print(f"Downloading DILI supplement data ...")
    try:
        req = urllib.request.Request(supp_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(fname, "wb") as f:
                f.write(resp.read())
        print(f"Saved to {fname}")
        return fname
    except Exception as e:
        print(f"Failed: {e}")
        return None


if __name__ == "__main__":
    print("=== DILI: Drug safety warnings from ChEMBL ===")
    try:
        result = get_dili_compounds_from_chembl(limit=10)
        warnings = result.get("drug_warnings", [])
        print(f"Found {len(warnings)} liver toxicity warnings (showing first 5):")
        for w in warnings[:5]:
            mol = w.get("molecule_chembl_id", "")
            wtype = w.get("warning_type", "")
            wclass = w.get("warning_class", "")
            year = w.get("warning_year", "")
            print(f"  {mol} | Type: {wtype} | Class: {wclass} | Year: {year}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n=== DILI: Hepatotoxicity assays in ChEMBL ===")
    try:
        result = get_hepatotoxicity_assays(limit=5)
        assays = result.get("assays", [])
        for a in assays:
            print(f"  {a.get('assay_chembl_id')}: {a.get('description', '')[:80]}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n=== DILI: Downloading paper supplement ===")
    fpath = download_supplement_data()
    if not fpath:
        print("For detailed DILI curation data, access the paper at:")
        print("  https://doi.org/10.1021/acs.chemrestox.0c00296")
        print("Or use DILIrank (48_DILIrank.py) for FDA DILI classification.")
